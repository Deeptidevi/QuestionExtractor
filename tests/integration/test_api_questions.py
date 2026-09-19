import io
from fastapi.testclient import TestClient


def test_get_extracted_questions_and_single_question(client: TestClient, auth_headers, sample_exam_pdf_bytes):
    # Upload and synchronously process document
    files = {"file": ("exam.pdf", io.BytesIO(sample_exam_pdf_bytes), "application/pdf")}
    upload_res = client.post("/api/v1/documents", files=files, data={"sync_process": "true"}, headers=auth_headers)
    doc_id = upload_res.json()["document_id"]

    # List questions
    q_res = client.get(f"/api/v1/documents/{doc_id}/questions", headers=auth_headers)
    assert q_res.status_code == 200
    q_data = q_res.json()
    assert len(q_data["items"]) >= 3
    assert q_data["pagination"]["total_items"] >= 3

    # Check question fields
    first_q = q_data["items"][0]
    assert first_q["question_number"] is not None
    assert first_q["options_count"] >= 2
    assert first_q["source_pages"] == [1]

    # Get single question detail
    q_id = first_q["id"]
    detail_res = client.get(f"/api/v1/questions/{q_id}", headers=auth_headers)
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["id"] == q_id
    assert len(detail_data["options"]) >= 2
    assert detail_data["options"][0]["label"] == "A"
