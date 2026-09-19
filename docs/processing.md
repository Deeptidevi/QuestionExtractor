# Document Processing & Question Extraction Mechanics

## 1. Multi-Stage Pipeline Workflow

```
[Upload PDF/Image]
        │
        ▼
[File Signature & Size Validation]
        │
        ▼
[Storage Abstraction & File Hashing (SHA-256)]
        │
        ▼
[Page Extraction & Geometry Calculation]
        │
        ▼
[Digital Text Density Evaluation] ──────────► [Is Text Poor / Scanned Image?]
        │                                                    │ YES
        │ NO                                                 ▼
        │                                         [Tesseract OCR Provider]
        │                                         [Orientation Normalization]
        │                                                    │
        └────────────────────┬───────────────────────────────┘
                             │
                             ▼
               [Text & OCR Artifact Cleanup]
                             │
                             ▼
               [Question Header & Layout Segmentation]
               - Multi-style Regex (1., Q1, Question 1:)
               - Cross-page boundary tracking
                             │
                             ▼
               [Option & Choice Extraction]
               - Single & multi-line options (A-D, (a)-(d))
               - Inline horizontal options
                             │
                             ▼
               [Figure & Table Asset Association]
                             │
                             ▼
               [Answer Key Extraction & Option Verification]
                             │
                             ▼
               [Multi-Signal Confidence Scoring (0.0 - 1.0)]
                             │
                             ▼
               [Review Warnings & Flag Generation]
                             │
                             ▼
               [Atomic Database Commit]
```

---

## 2. Multi-Page Spanning Questions

In real examination papers, a question may begin near the bottom of Page $N$ and its descriptive choices or continuation may extend onto Page $N+1$.

### How the Algorithm Resolves Spanning Questions:
1. **Active Question State**: The `RuleBasedExtractor` tracks `current_number`, `current_lines`, and `current_pages`.
2. **Continuation Detection**: If a new page starts without matching a new question start pattern (e.g. `2.` or `Q2`), the lines are appended to the active question, and the page number is added to `source_pages`:
   ```python
   source_pages = [1, 2]
   ```
3. **Traceability**: The resulting `Question` record maintains all pages it spans across, and generates a `QUESTION_CONTINUES_NEXT_PAGE` informational flag for reviewers.

---

## 3. Answer Key Matching & Ambiguity Guards

1. **Detection**: `AnswerKeyDetector` scans document blocks for `Answer Key`, `Marking Scheme`, or columnar grids (`1 - B`, `Q1: B`, `1. A  2. B`).
2. **Ambiguity Validation**: `AnswerMatcher` compares candidate answers to the choices detected in the question:
   - If an answer refers to option `E`, but the question only extracted choices `A`, `B`, `C`, `D`, the system detects an inconsistency.
   - **Safety Rule**: It marks the answer as `null`, sets `match_status = AMBIGUOUS`, assigns low confidence, and flags `ANSWER_MATCH_UNCERTAIN`.

---

## 4. Multi-Signal Confidence Formula

The overall question confidence score $C_Q \in [0.0, 1.0]$ is computed as:

$$C_Q = w_1 S_{\text{numbering}} + w_2 S_{\text{options}} + w_3 S_{\text{text\_quality}} + w_4 S_{\text{boundaries}} + w_5 S_{\text{continuity}}$$

Where:
- $w_1 = 0.25$ (Numbering clarity)
- $w_2 = 0.25$ (Option integrity: 4 options = 1.0, 3 = 0.75, 2 = 0.50, <2 = 0.10)
- $w_3 = 0.20$ (OCR clarity & text density)
- $w_4 = 0.15$ (Boundary punctuation & structure)
- $w_5 = 0.15$ (Page continuity)

### Thresholds:
- $C_Q \ge 0.85$: `HIGH_CONFIDENCE` (`status = SUCCESS`, `review_required = false`)
- $0.60 \le C_Q < 0.85$: `MEDIUM_CONFIDENCE` (`status = PARTIAL`)
- $C_Q < 0.60$: `LOW_CONFIDENCE` (`status = REVIEW_REQUIRED`, `review_required = true`)
