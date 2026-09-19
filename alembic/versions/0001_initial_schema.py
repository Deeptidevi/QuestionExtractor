"""Initial database schema migration

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-09-19 21:50:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    # 2. documents
    op.create_table(
        "documents",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("stored_path", sa.String(length=512), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("file_hash", sa.String(length=64), nullable=False),
        sa.Column("total_pages", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("is_scanned", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("overall_confidence", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_documents_id"), "documents", ["id"], unique=False)
    op.create_index(op.f("ix_documents_user_id"), "documents", ["user_id"], unique=False)
    op.create_index(op.f("ix_documents_file_hash"), "documents", ["file_hash"], unique=False)
    op.create_index(op.f("ix_documents_status"), "documents", ["status"], unique=False)

    # 3. document_pages
    op.create_table(
        "document_pages",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("cleaned_text", sa.Text(), nullable=True),
        sa.Column("width", sa.Float(), nullable=True),
        sa.Column("height", sa.Float(), nullable=True),
        sa.Column("rotation", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("char_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("word_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("ocr_applied", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("ocr_confidence", sa.Float(), nullable=True),
        sa.Column("extracted_blocks", sa.JSON(), nullable=False),
        sa.Column("extracted_tables", sa.JSON(), nullable=False),
        sa.Column("extracted_images", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_document_pages_id"), "document_pages", ["id"], unique=False)
    op.create_index(op.f("ix_document_pages_document_id"), "document_pages", ["document_id"], unique=False)
    op.create_index(op.f("ix_document_pages_page_number"), "document_pages", ["page_number"], unique=False)

    # 4. document_relationships
    op.create_table(
        "document_relationships",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("source_document_id", sa.String(length=36), nullable=False),
        sa.Column("target_document_id", sa.String(length=36), nullable=False),
        sa.Column("relationship_type", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["source_document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_document_id", "target_document_id", "relationship_type", name="uq_doc_relationship"),
    )

    # 5. processing_jobs
    op.create_table(
        "processing_jobs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("celery_task_id", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("current_stage", sa.String(length=100), nullable=True),
        sa.Column("progress_percent", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default=sa.text("3")),
        sa.Column("error_summary", sa.Text(), nullable=True),
        sa.Column("job_metadata", sa.JSON(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_processing_jobs_id"), "processing_jobs", ["id"], unique=False)
    op.create_index(op.f("ix_processing_jobs_document_id"), "processing_jobs", ["document_id"], unique=False)

    # 6. questions
    op.create_table(
        "questions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("question_number", sa.String(length=50), nullable=True),
        sa.Column("sequence_order", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(length=50), nullable=False),
        sa.Column("source_pages", sa.JSON(), nullable=False),
        sa.Column("source_regions", sa.JSON(), nullable=False),
        sa.Column("extraction_confidence", sa.Float(), nullable=False),
        sa.Column("extraction_status", sa.String(length=50), nullable=False),
        sa.Column("review_required", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_questions_id"), "questions", ["id"], unique=False)
    op.create_index(op.f("ix_questions_document_id"), "questions", ["document_id"], unique=False)
    op.create_index(op.f("ix_questions_question_number"), "questions", ["question_number"], unique=False)

    # 7. question_options
    op.create_table(
        "question_options",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("question_id", sa.String(length=36), nullable=False),
        sa.Column("label", sa.String(length=20), nullable=False),
        sa.Column("option_text", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("is_correct", sa.Boolean(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False, server_default=sa.text("1.0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_question_options_id"), "question_options", ["id"], unique=False)
    op.create_index(op.f("ix_question_options_question_id"), "question_options", ["question_id"], unique=False)

    # 8. question_assets
    op.create_table(
        "question_assets",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("question_id", sa.String(length=36), nullable=False),
        sa.Column("asset_type", sa.String(length=50), nullable=False),
        sa.Column("storage_path", sa.String(length=512), nullable=False),
        sa.Column("source_page", sa.Integer(), nullable=False),
        sa.Column("bbox", sa.JSON(), nullable=False),
        sa.Column("caption", sa.String(length=500), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False, server_default=sa.text("1.0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 9. answers
    op.create_table(
        "answers",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("question_id", sa.String(length=36), nullable=True),
        sa.Column("question_number", sa.String(length=50), nullable=True),
        sa.Column("answer_value", sa.String(length=255), nullable=True),
        sa.Column("raw_answer_text", sa.Text(), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False, server_default=sa.text("1.0")),
        sa.Column("source_page", sa.Integer(), nullable=True),
        sa.Column("match_status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 10. review_items
    op.create_table(
        "review_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("question_id", sa.String(length=36), nullable=True),
        sa.Column("warning_type", sa.String(length=100), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("source_page", sa.Integer(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("is_resolved", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 11. processing_errors
    op.create_table(
        "processing_errors",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("document_id", sa.String(length=36), nullable=False),
        sa.Column("job_id", sa.String(length=36), nullable=True),
        sa.Column("stage", sa.String(length=100), nullable=False),
        sa.Column("error_code", sa.String(length=100), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=False),
        sa.Column("traceback_details", sa.Text(), nullable=True),
        sa.Column("error_metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["processing_jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("processing_errors")
    op.drop_table("review_items")
    op.drop_table("answers")
    op.drop_table("question_assets")
    op.drop_table("question_options")
    op.drop_table("questions")
    op.drop_table("processing_jobs")
    op.drop_table("document_relationships")
    op.drop_table("document_pages")
    op.drop_table("documents")
    op.drop_table("users")
