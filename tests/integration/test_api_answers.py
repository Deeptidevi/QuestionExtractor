import io
from fastapi.testclient import TestClient


def test_get_document_answers(client: TestClient, auth_headers, sample_exam_pdf_bytes):
    # Upload and process
    files = {"file": ("exam.pdf", io.BytesIO(sample_exam_pdf_bytes), "application/pdf")}
    upload_res = client.post("/api/v1/documents", files=files, data={"sync_process": "true"}, headers=auth_headers)
    doc_id = upload_res.json()["document_id"]

    # Retrieve answers
    ans_res = client.get(f"/api/v1/documents/{doc_id}/answers", headers=auth_headers)
    assert ans_res.status_code == 200
    ans_data = ans_res.json()
    assert ans_data["document_id"] == doc_id
    assert ans_data["total_answers"] >= 3
    assert len(ans_data["answers"]) >= 3
    assert ans_data["matched_answers_count"] >= 1
