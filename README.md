
# PDF Document Intelligence Pipeline

This project extracts and ranks the most relevant sections from a set of PDF documents based on a given **persona** and **job-to-be-done**, producing a structured `output.json` for downstream use.

---

## Project Structure

```


├── Adobe_B/
│   ├── Collection 1/
│   │   ├── input.json
│   │   ├── output.json          ← Generated output
│   │   └── pdfs/
│   │       ├── South of France - Cuisine.pdf
│   │       └── ...
│   └── ...
│
├── main.py                      ← Main script
└── README.md                    ← You're here
```

---

##  What It Does

- Reads `input.json` containing:
  - List of PDF files
  - Persona description (e.g., "Travel Planner")
  - Job-to-be-done (e.g., "Plan a trip of 4 days for a group of 10 college friends")
- Extracts all text sections from each PDF
- Scores them using semantic similarity (SentenceTransformer)
- Returns top-ranked section from each document + additional top 3 refined subsections
- Outputs a clean and structured `output.json`

---

## ⚙️ Installation

```bash
# Clone the repo or copy the code
git clone https://github.com/TEENA-LOHAKARE/Adobe_B
cd Adobe_B

#  Docker Setup & Usage
docker build -t doc-intel .


## How to Run

```bash
docker run --rm -v $(pwd):/app doc-intel python main.py --pdf_dir /app
```


---

##  Expected input: `input.json`

```json
{
  "persona": {
    "role": "Travel Planner"
  },
  "job_to_be_done": {
    "task": "Plan a trip of 4 days for a group of 10 college friends."
  },
  "documents": [
    {
      "filename": "South of France - Cuisine.pdf",
      "title": "Cuisine"
    },
    {
      "filename": "South of France - Things to Do.pdf",
      "title": "Things to Do"
    }
    // ...
  ]
}
```


---

##  Output: `output.json`

The pipeline generates an `output.json` with:

- Metadata (persona, job, file list)
- Top extracted section per document
- Top 3 refined subsection texts (for deeper insight)

Example:

```json
{
  "metadata": {
    "input_documents": [...],
    "persona": "Travel Planner",
    "job_to_be_done": "Plan a trip of 4 days for a group of 10 college friends.",
    "processing_timestamp": "2025-07-28T15:14:23.312559"
  },
  "extracted_sections": [
    {
      "document": "South of France - Cuisine.pdf",
      "section_title": "Culinary Experiences",
      "importance_rank": 1,
      "page_number": 6
    }
  ],
  "subsection_analysis": [
    {
      "document": "South of France - Cuisine.pdf",
      "refined_text": "In addition to dining at top restaurants, there are several culinary experiences you should consider...",
      "page_number": 6
    }
  ]
}
```

---

##  Features

- Domain-agnostic: Works for any PDF content
- Persona-driven relevance scoring
- Context-aware custom query generation for each document
- PDF parsing with layout preservation (via PyMuPDF)


