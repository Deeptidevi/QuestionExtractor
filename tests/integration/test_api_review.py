import io
from fastapi.testclient import TestClient


def test_get_review_items_and_resolve(client: TestClient, auth_headers, sample_low_confidence_pdf_bytes):
    # Upload low-confidence document
    files = {"file": ("low_conf.pdf", io.BytesIO(sample_low_confidence_pdf_bytes), "application/pdf")}
    upload_res = client.post("/api/v1/documents", files=files, data={"sync_process": "true"}, headers=auth_headers)
    doc_id = upload_res.json()["document_id"]

    # Check review items
    rev_res = client.get(f"/api/v1/documents/{doc_id}/review-items", headers=auth_headers)
    assert rev_res.status_code == 200
    rev_data = rev_res.json()
    assert rev_data["document_id"] == doc_id
    assert rev_data["total_review_items"] >= 1
    assert len(rev_data["items"]) >= 1

    # Resolve first review item
    item_id = rev_data["items"][0]["id"]
    resolve_payload = {
        "is_resolved": True,
        "resolution_note": "Manually verified by instructor.",
    }
    resolve_res = client.post(f"/api/v1/review-items/{item_id}/resolve", json=resolve_payload, headers=auth_headers)
    assert resolve_res.status_code == 200
    assert resolve_res.json()["is_resolved"] is True
