import os
import sys
from pathlib import Path

# Ensure root directory is on Python path
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from tests.fixtures.sample_generator import SampleGenerator


def main():
    out_dir = Path("./samples/documents").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Standard Exam PDF
    pdf1 = SampleGenerator.create_standard_exam_pdf()
    p1_path = out_dir / "computer_science_midterm_exam.pdf"
    with open(p1_path, "wb") as f:
        f.write(pdf1)
    print(f"Generated: {p1_path}")

    # 2. Spanning Question PDF
    pdf2 = SampleGenerator.create_spanning_question_pdf()
    p2_path = out_dir / "advanced_algorithms_spanning_question.pdf"
    with open(p2_path, "wb") as f:
        f.write(pdf2)
    print(f"Generated: {p2_path}")

    # 3. Answer Key PDF
    pdf3 = SampleGenerator.create_answer_key_pdf()
    p3_path = out_dir / "computer_science_answer_key.pdf"
    with open(p3_path, "wb") as f:
        f.write(pdf3)
    print(f"Generated: {p3_path}")

    # 4. Question Image
    img = SampleGenerator.create_question_image()
    img_path = out_dir / "scanned_chemistry_question.png"
    with open(img_path, "wb") as f:
        f.write(img)
    print(f"Generated: {img_path}")

    # 5. Low Confidence Sample
    pdf_low = SampleGenerator.create_low_confidence_pdf()
    low_path = out_dir / "low_confidence_sample.pdf"
    with open(low_path, "wb") as f:
        f.write(pdf_low)
    print(f"Generated: {low_path}")


if __name__ == "__main__":
    main()
