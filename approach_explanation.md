## Approach Explanation

### Goal
To build a generic, persona-driven document intelligence system that selects and prioritizes the most relevant content from a collection of PDFs, tailored to a specific persona and task.

### Core Steps

1. **PDF Parsing**  
   Each PDF is parsed using PyMuPDF, which provides access to text and page numbers. Pages with meaningful content are extracted.

2. **Embedding the Persona + Task**  
   The "persona" and "job to be done" are combined into a single query string and embedded using a compact, efficient SentenceTransformer model (`MiniLM-L6-v2`). This ensures fast processing and low resource usage.

3. **Section Ranking**  
   Every section or page is embedded and ranked via cosine similarity against the persona+task vector. Sections are sorted by this similarity score to prioritize relevance.

4. **Output Formatting**  
   The top-ranked sections (one per document) are included in `extracted_sections`. For each selected document, the top 3 relevant chunks are included in `subsection_analysis`, capturing fine-grained content.

### Design Decisions
- **Model Size & Speed**: We use a <500MB model to meet size and speed constraints.
- **Domain Agnostic**: Because we use embeddings rather than keyword search, this system generalizes across travel, finance, academia, etc.
- **No Internet Access**: All models and libraries run entirely offline once installed.

### Output
- `metadata`: Describes persona, task, and document list.
- `extracted_sections`: Prioritized sections by relevance.
- `subsection_analysis`: Granular high-relevance content.

This system meets all challenge constraints: ≤1GB model size, ≤60s runtime, CPU-only execution, and generic applicability.

docker build -t doc-intel .