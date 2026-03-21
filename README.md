# Phase 3 — Final Project Submission

> **Course:** Software Design & Architecture (SDA) &nbsp;|&nbsp; **Status:** ✅ Final Submission Ready

---

## 📌 Overview

This repository contains the **Phase 3** submission of the SDA/Software Engineering project.  
Phase 3 represents full system integration — combining all modules from Phase 1 and Phase 2 into a single, cohesive, and evaluation-ready application.

The system is built to process **CSV-based datasets** and produce structured, validated outputs through a clean, modular codebase.

---

## ✨ What's New in Phase 3

| Feature | Status |
|---|---|
| Full module integration (Phase 1 + 2) | ✅ Complete |
| Dynamic CSV input handling (TA datasets) | ✅ Complete |
| Improved error handling & input validation | ✅ Complete |
| Optimized data processing pipeline | ✅ Complete |
| Edge case testing (missing values, malformed rows) | ✅ Complete |
| Clean, modular code structure | ✅ Complete |

---

## 📁 Project Structure

```
project-root/
│
├── src/                  # Core source code & logic modules
├── data/                 # Sample and test CSV datasets
├── output/               # Program-generated results
├── tests/                # Unit and integration test cases
├── main.py               # Entry point
├── requirements.txt      # Python dependencies
└── README.md             # You are here
```

---

## ⚙️ Setup & Running

### 1. Clone the Repository

```bash
git clone <repository-link>
cd project-root
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Program

```bash
python main.py
```

> **Note:** To use a custom CSV file, place it in the `data/` directory and update the input path in `main.py` accordingly — no other code changes required.

---

## 📊 Evaluation Notes (TA — Please Read)

- The system is designed to **accept any valid CSV file** without requiring code modifications.
- Simply provide the CSV file path at runtime or drop it into the `data/` folder.
- All output is written to the `output/` directory for easy review.
- Do **not** manually alter file paths during evaluation unless explicitly needed.

---

## 🧪 Testing

- Core functionalities tested against multiple sample datasets.
- Edge cases handled:
  - Missing or null values
  - Malformed CSV rows
  - Unexpected column orders
  - Empty datasets
- Output validated against expected results for all test cases.

---

## 👨‍💻 Authors

| Field | Detail |
|---|---|
| **Name** | Muhammad Nouman Malik |
| **Roll No.** | 24L-0759 |
|---|---|
| **Name** | Abdullah Nawaz |
| **Roll No.** | 24L-0626 |
| **Course** | Software Design & Architecture |
| **Phase** | 3 — Final |

---

## 📝 Version History

| Phase | Description |
|---|---|
| Phase 1 | Initial module development & basic CSV parsing |
| Phase 2 | Module expansion & intermediate integration |
| **Phase 3** | **Full integration, testing & final submission** |

---

## 📄 License

This project is submitted for academic evaluation only. Redistribution or reuse outside of course requirements requires explicit permission from the authors.