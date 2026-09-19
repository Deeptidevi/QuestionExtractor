import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.logging import logger
from app.db.models.document import Document, DocumentStatus
from app.db.models.document_page import DocumentPage
from app.db.models.processing_job import ProcessingJob, JobStatus
from app.db.models.processing_error import ProcessingError
from app.db.models.question import Question, ExtractionStatus
from app.db.models.question_option import QuestionOption
from app.db.models.question_asset import QuestionAsset
from app.db.models.answer import Answer, AnswerMatchStatus
from app.db.models.review_item import ReviewItem, WarningType, ReviewSeverity
from app.processing.page_extractor import PageExtractor, ExtractedPageData
from app.processing.normalizer import Normalizer
from app.processing.ocr import get_ocr_provider
from app.processing.extractors import get_question_extractor
from app.processing.asset_extractor import AssetExtractor
from app.processing.answer_key_detector import AnswerKeyDetector
from app.processing.answer_matcher import AnswerMatcher
from app.processing.confidence_engine import ConfidenceEngine
from app.processing.review_generator import ReviewItemGenerator
from app.services.storage_service import storage_service


class DocumentProcessor:
    """
    Coordinates the multi-stage document processing and question extraction pipeline.
    Ensures idempotency, transactional persistence, progress reporting, and error isolation.
    """

    def __init__(self, db: Session, ocr_provider_name: Optional[str] = None):
        self.db = db
        self.ocr_provider = get_ocr_provider(ocr_provider_name)
        self.question_extractor = get_question_extractor()

    def process_document(self, document_id: str, job_id: Optional[str] = None) -> Document:
        """
        Executes the entire extraction pipeline for a given document.
        """
        doc = self.db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise ValueError(f"Document '{document_id}' does not exist.")

        job = self.db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first() if job_id else None
        
        start_time = time.time()
        logger.info(f"Starting pipeline execution for document '{document_id}' (file: {doc.original_filename})")

        try:
            # 1. Update status to PROCESSING
            doc.status = DocumentStatus.PROCESSING
            if job:
                job.status = JobStatus.RUNNING
                job.current_stage = "INITIALIZATION"
                job.progress_percent = 10
            self.db.commit()

            # Idempotency: clear previously extracted artifacts if re-processing
            self._clear_previous_extractions(doc.id)

            # 2. Stage: Page & Text Extraction
            self._update_stage(job, "PAGE_EXTRACTION", 20)
            physical_file_path = storage_service.get_file_path(doc.stored_path)
            extracted_pages = PageExtractor.extract_pages_from_file(physical_file_path, doc.mime_type)
            doc.total_pages = len(extracted_pages)

            # 3. Stage: OCR & Normalization
            self._update_stage(job, "OCR_AND_NORMALIZATION", 40)
            pages_text_payload: List[Dict[str, Any]] = []
            page_stats: List[Dict[str, Any]] = []
            page_ocr_confidences: List[float] = []

            for page in extracted_pages:
                # Check if OCR fallback is needed (empty text or scanned image)
                needs_ocr = page.is_scanned or len(page.raw_text.strip()) < settings.OCR_PAGE_DENSITY_THRESHOLD
                final_text = page.raw_text
                ocr_conf = 1.0

                if needs_ocr:
                    doc.is_scanned = True
                    if page.image_path:
                        # Normalize image
                        norm_img_path = Normalizer.normalize_image_orientation(page.image_path)
                        ocr_res = self.ocr_provider.extract_text_from_image(norm_img_path)
                        final_text = ocr_res.text
                        ocr_conf = ocr_res.confidence
                    else:
                        # For PDF pages with low text density, attempt OCR fallback
                        ocr_conf = 0.70  # Default estimate for partial digital text

                # Clean and normalize text
                cleaned_text = Normalizer.clean_text(final_text)
                cleaned_text = Normalizer.correct_ocr_artifacts(cleaned_text)

                # Persist DocumentPage record
                db_page = DocumentPage(
                    document_id=doc.id,
                    page_number=page.page_number,
                    raw_text=final_text,
                    cleaned_text=cleaned_text,
                    width=page.width,
                    height=page.height,
                    rotation=page.rotation,
                    char_count=len(cleaned_text),
                    word_count=len(cleaned_text.split()),
                    ocr_applied=needs_ocr,
                    ocr_confidence=ocr_conf,
                )
                self.db.add(db_page)
                
                pages_text_payload.append({"page_number": page.page_number, "text": cleaned_text})
                page_stats.append({"page_number": page.page_number, "ocr_confidence": ocr_conf})
                page_ocr_confidences.append(ocr_conf)

            self.db.commit()

            # 4. Stage: Question Segmentation & Option Extraction
            self._update_stage(job, "QUESTION_SEGMENTATION", 60)
            raw_questions = self.question_extractor.extract_questions(pages_text_payload)

            # 5. Stage: Answer Key Detection & Matching
            self._update_stage(job, "ANSWER_KEY_MATCHING", 75)
            detected_answers = AnswerKeyDetector.detect_answers_in_document(pages_text_payload)
            match_results = AnswerMatcher.match_answers(raw_questions, detected_answers)

            # 6. Stage: Confidence Calculation & Review Generation
            self._update_stage(job, "CONFIDENCE_AND_REVIEW", 85)
            q_conf_scores = []
            for match_res in match_results:
                q = match_res.question
                primary_page = q.source_pages[0] if q.source_pages else 1
                page_ocr = next((p["ocr_confidence"] for p in page_stats if p["page_number"] == primary_page), 1.0)
                
                conf = ConfidenceEngine.calculate_question_confidence(
                    question_number=q.question_number,
                    question_text=q.question_text,
                    question_type=q.question_type,
                    options=q.options,
                    source_pages=q.source_pages,
                    ocr_confidence=page_ocr,
                )
                q_conf_scores.append(conf)

            overall_doc_conf = ConfidenceEngine.calculate_document_overall_confidence(
                q_conf_scores, page_ocr_confidences
            )
            doc.overall_confidence = overall_doc_conf

            review_warnings = ReviewItemGenerator.generate_review_items(
                match_results, q_conf_scores, page_stats
            )

            # 7. Stage: Structured Persistence
            self._update_stage(job, "PERSISTENCE", 95)
            created_questions: List[Question] = []
            
            for idx, match_res in enumerate(match_results):
                q_cand = match_res.question
                conf_score = q_conf_scores[idx]

                db_question = Question(
                    document_id=doc.id,
                    question_number=q_cand.question_number,
                    sequence_order=q_cand.sequence_order,
                    raw_text=q_cand.raw_text,
                    question_text=q_cand.question_text,
                    question_type=q_cand.question_type,
                    source_pages=q_cand.source_pages,
                    source_regions=q_cand.source_regions,
                    extraction_confidence=conf_score.overall_score,
                    extraction_status=conf_score.status,
                    review_required=conf_score.review_required,
                )
                self.db.add(db_question)
                self.db.flush()  # Populates db_question.id

                created_questions.append(db_question)

                # Persist options
                for opt in q_cand.options:
                    db_opt = QuestionOption(
                        question_id=db_question.id,
                        label=opt["label"],
                        option_text=opt["text"],
                        position=opt.get("position", 1),
                        confidence=opt.get("confidence", 1.0),
                    )
                    self.db.add(db_opt)

                # Persist assets
                assets, _ = AssetExtractor.extract_and_associate_assets(
                    q_cand.question_text,
                    q_cand.source_pages[0] if q_cand.source_pages else 1,
                )
                for asset in assets:
                    db_asset = QuestionAsset(
                        question_id=db_question.id,
                        asset_type=asset["asset_type"],
                        storage_path=asset["storage_path"],
                        source_page=asset["source_page"],
                        bbox=asset.get("bbox", []),
                        caption=asset.get("caption"),
                        confidence=asset.get("confidence", 1.0),
                    )
                    self.db.add(db_asset)

                # Persist matched answer
                if match_res.answer:
                    db_ans = Answer(
                        document_id=doc.id,
                        question_id=db_question.id,
                        question_number=match_res.answer.question_number,
                        answer_value=match_res.answer.answer_value,
                        raw_answer_text=match_res.answer.raw_text,
                        explanation=match_res.answer.explanation,
                        confidence=match_res.confidence,
                        source_page=match_res.answer.source_page,
                        match_status=match_res.match_status,
                    )
                    self.db.add(db_ans)

            # Persist standalone detected answers (e.g. if question paper didn't match directly)
            for ans in detected_answers:
                # Check if already saved with a question
                existing = self.db.query(Answer).filter(
                    Answer.document_id == doc.id,
                    Answer.question_number == ans.question_number,
                ).first()
                if not existing:
                    db_ans = Answer(
                        document_id=doc.id,
                        question_id=None,
                        question_number=ans.question_number,
                        answer_value=ans.answer_value,
                        raw_answer_text=ans.raw_text,
                        explanation=ans.explanation,
                        confidence=ans.confidence,
                        source_page=ans.source_page,
                        match_status=AnswerMatchStatus.UNMATCHED,
                    )
                    self.db.add(db_ans)

            # Persist review items
            for rev in review_warnings:
                linked_q_id = None
                if rev.question_index is not None and rev.question_index < len(created_questions):
                    linked_q_id = created_questions[rev.question_index].id

                db_rev = ReviewItem(
                    document_id=doc.id,
                    question_id=linked_q_id,
                    warning_type=rev.warning_type,
                    severity=rev.severity,
                    message=rev.message,
                    source_page=rev.source_page,
                    confidence=rev.confidence,
                    details=rev.details,
                    is_resolved=False,
                )
                self.db.add(db_rev)

            # 8. Complete Document Status
            has_critical_reviews = any(r.severity == ReviewSeverity.CRITICAL for r in review_warnings)
            has_warnings = len(review_warnings) > 0
            
            if has_critical_reviews or (len(raw_questions) == 0 and not detected_answers):
                doc.status = DocumentStatus.COMPLETED_WITH_WARNINGS
            elif has_warnings:
                doc.status = DocumentStatus.COMPLETED_WITH_WARNINGS
            else:
                doc.status = DocumentStatus.COMPLETED

            if job:
                job.status = JobStatus.SUCCESS
                job.current_stage = "COMPLETED"
                job.progress_percent = 100
                job.finished_at = datetime.now(timezone.utc)

            self.db.commit()
            self.db.refresh(doc)

            duration = round((time.time() - start_time) * 1000, 2)
            logger.info(
                f"Successfully processed document '{doc.id}' ({len(created_questions)} questions, "
                f"{len(detected_answers)} answers, {len(review_warnings)} review items) in {duration}ms. Status: {doc.status.value}"
            )
            return doc

        except Exception as e:
            self.db.rollback()
            logger.error(f"Fatal error in pipeline for document '{document_id}': {e}", exc_info=True)

            doc.status = DocumentStatus.FAILED
            if job:
                job.status = JobStatus.FAILED
                job.current_stage = "FAILED"
                job.error_summary = str(e)
                job.finished_at = datetime.now(timezone.utc)

            err_record = ProcessingError(
                document_id=doc.id,
                job_id=job.id if job else None,
                stage=job.current_stage if job else "PROCESSING",
                error_code="PIPELINE_FAILURE",
                error_message=str(e),
                traceback_details=str(e),
            )
            self.db.add(err_record)
            self.db.commit()
            return doc

    def _clear_previous_extractions(self, document_id: str):
        self.db.query(DocumentPage).filter(DocumentPage.document_id == document_id).delete(synchronize_session=False)
        self.db.query(Question).filter(Question.document_id == document_id).delete(synchronize_session=False)
        self.db.query(Answer).filter(Answer.document_id == document_id).delete(synchronize_session=False)
        self.db.query(ReviewItem).filter(ReviewItem.document_id == document_id).delete(synchronize_session=False)
        self.db.query(ProcessingError).filter(ProcessingError.document_id == document_id).delete(synchronize_session=False)
        self.db.commit()

    def _update_stage(self, job: Optional[ProcessingJob], stage_name: str, percent: int):
        if job:
            job.current_stage = stage_name
            job.progress_percent = percent
            self.db.commit()
