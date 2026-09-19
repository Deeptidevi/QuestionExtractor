import io
from fastapi.testclient import TestClient


def test_create_list_and_delete_document_relationships(
    client: TestClient,
    auth_headers,
    sample_exam_pdf_bytes,
    sample_answer_key_pdf_bytes,
):
    # 1. Upload Question Paper
    files1 = {"file": ("exam.pdf", io.BytesIO(sample_exam_pdf_bytes), "application/pdf")}
    res1 = client.post("/api/v1/documents", files=files1, headers=auth_headers)
    doc_id1 = res1.json()["document_id"]

    # 2. Upload Answer Key Document
    files2 = {"file": ("answers.pdf", io.BytesIO(sample_answer_key_pdf_bytes), "application/pdf")}
    res2 = client.post("/api/v1/documents", files=files2, headers=auth_headers)
    doc_id2 = res2.json()["document_id"]

    # 3. Create Relationship: Question Paper -> Answer Key
    link_payload = {
        "target_document_id": doc_id2,
        "relationship_type": "ANSWER_KEY",
    }
    link_res = client.post(f"/api/v1/documents/{doc_id1}/relationships", json=link_payload, headers=auth_headers)
    assert link_res.status_code == 201
    link_data = link_res.json()
    assert link_data["source_document_id"] == doc_id1
    assert link_data["target_document_id"] == doc_id2

    # 4. List Relationships
    list_res = client.get(f"/api/v1/documents/{doc_id1}/relationships", headers=auth_headers)
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total_relationships"] == 1
    assert list_data["relationships"][0]["target_document_id"] == doc_id2

    # 5. Delete Relationship
    del_res = client.delete(f"/api/v1/documents/{doc_id1}/relationships/{doc_id2}", headers=auth_headers)
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # 6. Verify list is empty
    list_res_after = client.get(f"/api/v1/documents/{doc_id1}/relationships", headers=auth_headers)
    assert list_res_after.json()["total_relationships"] == 0
