import io
from fastapi.testclient import TestClient


def test_upload_valid_pdf(client: TestClient, auth_headers, sample_exam_pdf_bytes):
    files = {"file": ("exam.pdf", io.BytesIO(sample_exam_pdf_bytes), "application/pdf")}
    data = {"title": "CS Midterm Exam", "sync_process": "true"}

    response = client.post("/api/v1/documents", files=files, data=data, headers=auth_headers)
    assert response.status_code == 202
    res_data = response.json()
    assert "document_id" in res_data
    assert res_data["title"] == "CS Midterm Exam"


def test_upload_valid_image(client: TestClient, auth_headers, sample_image_bytes):
    files = {"file": ("question.png", io.BytesIO(sample_image_bytes), "image/png")}
    data = {"title": "Chemistry Question", "sync_process": "true"}

    response = client.post("/api/v1/documents", files=files, data=data, headers=auth_headers)
    assert response.status_code == 202
    res_data = response.json()
    assert "document_id" in res_data


def test_upload_invalid_file_type(client: TestClient, auth_headers):
    files = {"file": ("script.sh", io.BytesIO(b"#!/bin/bash\necho hello"), "text/x-shellscript")}
    response = client.post("/api/v1/documents", files=files, headers=auth_headers)
    assert response.status_code == 415
    res_data = response.json()
    assert res_data["error"]["code"] == "UNSUPPORTED_FILE_TYPE"


def test_upload_unauthorized(client: TestClient, sample_exam_pdf_bytes):
    files = {"file": ("exam.pdf", io.BytesIO(sample_exam_pdf_bytes), "application/pdf")}
    response = client.post("/api/v1/documents", files=files)
    assert response.status_code == 401


def test_get_document_status_and_details(client: TestClient, auth_headers, sample_exam_pdf_bytes):
    # Upload first
    files = {"file": ("exam.pdf", io.BytesIO(sample_exam_pdf_bytes), "application/pdf")}
    upload_res = client.post("/api/v1/documents", files=files, data={"sync_process": "true"}, headers=auth_headers)
    doc_id = upload_res.json()["document_id"]

    # Status check
    status_res = client.get(f"/api/v1/documents/{doc_id}/status", headers=auth_headers)
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["document_id"] == doc_id
    assert status_data["status"] in ("COMPLETED", "COMPLETED_WITH_WARNINGS")

    # Detail check
    detail_res = client.get(f"/api/v1/documents/{doc_id}", headers=auth_headers)
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert len(detail_data["pages"]) >= 1


def test_unauthorized_document_access(client: TestClient, auth_headers, other_auth_headers, sample_exam_pdf_bytes):
    # User 1 uploads document
    files = {"file": ("exam.pdf", io.BytesIO(sample_exam_pdf_bytes), "application/pdf")}
    upload_res = client.post("/api/v1/documents", files=files, data={"sync_process": "true"}, headers=auth_headers)
    doc_id = upload_res.json()["document_id"]

    # User 2 attempts to fetch user 1's document
    response = client.get(f"/api/v1/documents/{doc_id}", headers=other_auth_headers)
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "PERMISSION_DENIED"
