import io
from fastapi.testclient import TestClient
from app.db.models.document import Document
from app.processing.pipeline import DocumentProcessor
from app.processing.ocr.mock_ocr import MockOCRProvider


def test_e2e_spanning_questions_pipeline(client: TestClient, auth_headers, sample_spanning_pdf_bytes):
    # Upload spanning question PDF
    files = {"file": ("spanning.pdf", io.BytesIO(sample_spanning_pdf_bytes), "application/pdf")}
    upload_res = client.post("/api/v1/documents", files=files, data={"sync_process": "true"}, headers=auth_headers)
    doc_id = upload_res.json()["document_id"]

    # Check extracted questions
    q_res = client.get(f"/api/v1/documents/{doc_id}/questions", headers=auth_headers)
    assert q_res.status_code == 200
    items = q_res.json()["items"]
    assert len(items) >= 2

    # Verify first question spans pages [1, 2]
    first_q = items[0]
    assert first_q["question_number"] == "1"
    assert first_q["source_pages"] == [1, 2]
    assert first_q["options_count"] == 4


def test_e2e_image_processing_with_mock_ocr(db_session, test_user, sample_image_bytes):
    # Directly test DocumentProcessor with Mock OCR provider
    from app.services.storage_service import storage_service
    import io

    # Save image
    stream = io.BytesIO(sample_image_bytes)
    rel_path, sha_hash, total_bytes = storage_service.save_file(
        file_obj=stream,
        original_filename="question.png",
        content_type="image/png",
    )

    doc = Document(
        user_id=test_user.id,
        title="Image Exam Question",
        original_filename="question.png",
        stored_path=rel_path,
        mime_type="image/png",
        file_size=total_bytes,
        file_hash=sha_hash,
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)

    processor = DocumentProcessor(db=db_session, ocr_provider_name="mock")
    processed_doc = processor.process_document(doc.id)

    assert processed_doc.status.value in ("COMPLETED", "COMPLETED_WITH_WARNINGS")
    assert len(processed_doc.questions) >= 1
    assert processed_doc.questions[0].question_number == "1"
    assert len(processed_doc.questions[0].options) == 4


def test_e2e_idempotent_reprocessing(db_session, test_user, sample_exam_pdf_bytes):
    from app.services.storage_service import storage_service
    import io

    stream = io.BytesIO(sample_exam_pdf_bytes)
    rel_path, sha_hash, total_bytes = storage_service.save_file(
        file_obj=stream,
        original_filename="exam.pdf",
        content_type="application/pdf",
    )

    doc = Document(
        user_id=test_user.id,
        title="Exam Reprocessing Test",
        original_filename="exam.pdf",
        stored_path=rel_path,
        mime_type="application/pdf",
        file_size=total_bytes,
        file_hash=sha_hash,
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)

    processor = DocumentProcessor(db=db_session, ocr_provider_name="mock")
    # First execution
    proc1 = processor.process_document(doc.id)
    count1 = len(proc1.questions)

    # Second execution on same document ID (idempotency check)
    proc2 = processor.process_document(doc.id)
    count2 = len(proc2.questions)

    assert count1 == count2
    assert count2 >= 3
