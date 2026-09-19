"""
Live demonstration script for Document Processing & Question Extraction Service.
This script boots an in-process FastAPI test client against the full application,
registers a user, uploads a multi-page exam document, runs the extraction pipeline,
and prints the structured output.
"""

import json
import time
import sys

# Ensure UTF-8 output encoding on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

def run_demo():
    print("=" * 80)
    print("[*] DOCUMENT PROCESSING & QUESTION EXTRACTION SERVICE - LIVE DEMO")
    print("=" * 80)
    
    # Initialize database tables
    Base.metadata.create_all(bind=engine)
    
    client = TestClient(app)

    # 1. Check Health
    print("\n[1] Checking Service Health...")
    health_resp = client.get("/api/v1/health")
    print(f"Status: {health_resp.status_code}")
    print(f"Health Response: {json.dumps(health_resp.json(), indent=2)}")

    # 2. Register & Login
    print("\n[2] Registering & Authenticating Demo User...")
    email = f"demo_student_{int(time.time())}@example.com"
    password = "SecurePassword123!"
    reg_resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Demo Student", "role": "admin"}
    )
    print(f"Registration: {reg_resp.status_code}")
    
    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password}
    )
    tokens = login_resp.json()
    access_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    print(f"Authenticated successfully! Token type: {tokens.get('token_type')}")

    # 3. Upload Sample Exam PDF with synchronous processing
    sample_pdf_path = "samples/documents/computer_science_midterm_exam.pdf"
    print(f"\n[3] Uploading Sample Exam PDF: '{sample_pdf_path}'...")
    with open(sample_pdf_path, "rb") as f:
        file_bytes = f.read()

    upload_resp = client.post(
        "/api/v1/documents",
        files={"file": ("computer_science_midterm_exam.pdf", file_bytes, "application/pdf")},
        data={"sync_process": "True"},
        headers=headers
    )
    doc_data = upload_resp.json()
    doc_id = doc_data["document_id"]
    print(f"Upload & Processing Succeeded!")
    print(f"Document ID: {doc_id}")
    print(f"Original File: {doc_data.get('original_filename')}")
    print(f"Status: {doc_data.get('status')}")

    # 4. Fetch Document Status & Details
    print(f"\n[4] Querying Document Details via API...")
    doc_details = client.get(f"/api/v1/documents/{doc_id}", headers=headers).json()
    print(f"Document Title: {doc_details.get('title')}")
    print(f"Document Final Status: {doc_details.get('status')}")
    print(f"Total Pages Processed: {doc_details.get('total_pages')}")
    print(f"SHA-256 Hash: {doc_details.get('file_hash')}")

    # 5. Fetch Extracted Questions
    print(f"\n[5] Fetching Extracted Questions & Options...")
    questions_resp = client.get(f"/api/v1/documents/{doc_id}/questions", headers=headers)
    questions_data = questions_resp.json()
    items = questions_data.get("items", [])
    total_q = questions_data.get("meta", {}).get("total", len(items))
    print(f"Total Questions Extracted: {total_q}")
    
    for idx, q_summary in enumerate(items, 1):
        # Fetch complete question detail
        q_resp = client.get(f"/api/v1/questions/{q_summary['id']}", headers=headers)
        q = q_resp.json()
        
        conf = q.get('extraction_confidence', 0.0)
        status_val = q.get('extraction_status', 'UNKNOWN')
        rev_req = q.get('review_required', False)
        
        print("\n" + "-" * 70)
        print(f"QUESTION #{q.get('question_number')} (Sequence: {q.get('sequence_order')})")
        print(f"Type: {q.get('question_type')} | Confidence Score: {conf:.2f} | Status: {status_val} | Review Required: {rev_req}")
        print(f"Source Pages: {q.get('source_pages')}")
        print(f"Stem:\n  {q.get('question_text')}")
        
        options = q.get("options", [])
        if options:
            print("Options:")
            for opt in options:
                print(f"  [{opt.get('label')}] {opt.get('option_text')}")
        
        assets = q.get("assets", [])
        if assets:
            print("Assets:")
            for asset in assets:
                print(f"  [Asset: {asset.get('asset_type')}] {asset.get('caption')}")
                
        matched_ans = q.get("answer")
        if matched_ans:
            print(f"Matched Answer: Option [{matched_ans.get('answer_value')}] (Confidence: {matched_ans.get('confidence', 1.0):.2f}, Match Status: {matched_ans.get('match_status')})")

    # 6. Fetch Answer Keys
    print("\n" + "=" * 80)
    print("[6] Fetching Extracted & Matched Answer Keys...")
    answers_resp = client.get(f"/api/v1/documents/{doc_id}/answers", headers=headers)
    answers_data = answers_resp.json()
    ans_list = answers_data.get("answers", [])
    print(f"Total Answers Matched: {len(ans_list)} (Matched: {answers_data.get('matched_answers_count')}, Unmatched: {answers_data.get('unmatched_answers_count')})")
    for ans in ans_list:
        print(f"  * Question #{ans.get('question_number')}: Correct Value = '{ans.get('answer_value')}' (Confidence: {ans.get('confidence'):.2f}, Match Status: {ans.get('match_status')})")

    # 7. Fetch Review Queue
    print("\n" + "=" * 80)
    print("[7] Fetching Human Review Queue Items...")
    review_resp = client.get("/api/v1/review/queue", headers=headers)
    review_data = review_resp.json()
    review_items = review_data.get("items", [])
    print(f"Total Review Items in Queue: {len(review_items)}")
    for item in review_items:
        print(f"  * Review Item {item.get('id')} | Issue: {item.get('issue_type')} | Severity: {item.get('severity')} | Status: {item.get('status')}")
        print(f"    Message: {item.get('issue_description')}")

    print("\n" + "=" * 80)
    print("[SUCCESS] DEMO EXECUTION COMPLETED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    run_demo()
