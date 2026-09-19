import io
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF


class SampleGenerator:
    """
    Programmatically creates realistic PDF and Image fixtures for testing:
    - Standard exam papers with multiple questions and MCQs
    - Multi-page questions spanning across page boundaries
    - Separate Answer Key documents
    - Images containing rendered exam questions
    - Low-quality / uncertain documents
    """

    @classmethod
    def create_standard_exam_pdf(cls) -> bytes:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "MID-TERM EXAMINATION: COMPUTER SCIENCE", ln=True, align="C")
        pdf.ln(5)

        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 8, "1. What is the time complexity of binary search on a sorted array of N elements?\nA. O(1)\nB. O(log N)\nC. O(N)\nD. O(N^2)")
        pdf.ln(4)

        pdf.multi_cell(0, 8, "2. Which of the following data structures operates on a Last-In, First-Out (LIFO) basis?\nA. Queue\nB. Stack\nC. Linked List\nD. Binary Heap")
        pdf.ln(4)

        pdf.multi_cell(0, 8, "3. State whether the following is True or False: Python lists are mutable.\n(A) True\n(B) False")
        pdf.ln(4)

        pdf.multi_cell(0, 8, "4. In SQL, which keyword is used to sort the result set in ascending or descending order?\nA. GROUP BY\nB. ORDER BY\nC. SORT BY\nD. ARRANGE BY")
        pdf.ln(6)

        # Answer key section at the bottom
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Answer Key", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6, "1 - B\n2 - B\n3 - A\n4 - B")

        return pdf.output()

    @classmethod
    def create_spanning_question_pdf(cls) -> bytes:
        """
        Creates a 2-page PDF where Question 1 starts on Page 1 and finishes its explanation & choices on Page 2.
        """
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "ADVANCED ALGORITHMS: PART 1", ln=True, align="C")
        pdf.ln(5)

        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 8, "1. Consider a distributed consensus network operating under the Raft consensus protocol. When a network partition splits 5 nodes into a cluster of 3 and a cluster of 2, explain how the leader election proceeds and which partition commits new transactions.")
        
        # Add Page 2 where the choices for Question 1 continue
        pdf.add_page()
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 8, "Continuation of Question 1 Choices:\nA. The minority cluster of 2 elects a leader and continues writing.\nB. The majority cluster of 3 maintains quorum and commits transactions.\nC. Both partitions halt immediately.\nD. Neither partition can achieve consensus.")
        pdf.ln(6)

        pdf.multi_cell(0, 8, "2. Which sorting algorithm has an average time complexity of O(N log N) and is typically implemented in-place?\nA. Merge Sort\nB. Quick Sort\nC. Radix Sort\nD. Counting Sort")

        return pdf.output()

    @classmethod
    def create_answer_key_pdf(cls) -> bytes:
        """
        Creates a standalone Answer Key document to be linked via document relationships.
        """
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "OFFICIAL ANSWER KEY & SOLUTIONS", ln=True, align="C")
        pdf.ln(5)

        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 8, "Q1: B - Majority partition holds quorum.\nQ2: B - Quick Sort is in-place and average O(N log N).\nQ3: A - Python lists are mutable.\nQ4: B - ORDER BY clause.")

        return pdf.output()

    @classmethod
    def create_low_confidence_pdf(cls) -> bytes:
        """
        Creates a PDF with missing question numbers and single option to trigger confidence warnings.
        """
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 8, "What is the boiling point of water at sea level under standard atmospheric pressure?\nA. 100 degrees Celsius")

        return pdf.output()

    @classmethod
    def create_question_image(cls) -> bytes:
        """
        Renders a question into a PNG image.
        """
        img = Image.new("RGB", (800, 400), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)

        text = (
            "1. What is the chemical formula for water?\n"
            "A. H2O\n"
            "B. CO2\n"
            "C. NaCl\n"
            "D. CH4\n\n"
            "Answer Key\n"
            "1 - A"
        )
        draw.text((30, 30), text, fill=(0, 0, 0))

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()
