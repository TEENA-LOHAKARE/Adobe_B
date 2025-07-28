import os
import json
import datetime
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')


def extract_sections(pdf_path):
    doc = fitz.open(pdf_path)
    sections = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        if len(text.strip()) > 100:
            sections.append({
                "page_number": page_num,
                "text": text.strip()
            })
    return sections


def rank_sections(sections, query_embedding):
    for sec in sections:
        sec_embedding = model.encode(sec["text"], convert_to_tensor=True)
        sec["score"] = util.cos_sim(sec_embedding, query_embedding).item()

        # Penalize generic sections
        if "conclusion" in sec["text"].lower()[:100]:
            sec["score"] *= 0.5

    sections.sort(key=lambda x: x["score"], reverse=True)
    return sections


def extract_section_title(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        return lines[0] if len(lines[0]) <= 100 else lines[0][:100]
    return text[:60] + "..."


def build_custom_query(doc_title, base_query):
    doc_title = doc_title.lower()
    if "cuisine" in doc_title:
        return base_query + " Focus on food, cooking classes, restaurants, and wine experiences."
    elif "things to do" in doc_title:
        return base_query + " Focus on activities, entertainment, and sightseeing for students."
    elif "tips and tricks" in doc_title:
        return base_query + " Focus on practical travel tips, packing hacks, local advice."
    elif "restaurants" in doc_title:
        return base_query + " Focus on accommodations and dining recommendations."
    elif "history" in doc_title:
        return base_query + " Focus on cultural landmarks and historical experiences."
    elif "culture" in doc_title:
        return base_query + " Focus on cultural events, local traditions, and heritage."
    else:
        return base_query + f" Focus on important aspects from the document titled '{doc_title}'."


def run_pipeline(base_dir):
    for collection_name in sorted(os.listdir(base_dir)):
        collection_path = os.path.join(base_dir, collection_name)
        if not os.path.isdir(collection_path):
            continue

        input_json_path = os.path.join(collection_path, "input.json")
        if not os.path.exists(input_json_path):
            continue

        with open(input_json_path, "r", encoding="utf-8") as f:
            input_data = json.load(f)

        persona = input_data.get("persona", {}).get("role", "")
        job = input_data.get("job_to_be_done", {}).get("task", "")
        base_query = f"{persona} - {job}. Plan a well-balanced, exciting and enjoyable experience for 10 college friends over 4 days."

        pdf_files = []
        for doc in input_data.get("documents", []):
            fname = doc.get("filename")
            if fname:
                full_path = os.path.join(collection_path, "pdfs", fname)
                if os.path.exists(full_path):
                    pdf_files.append((full_path, doc["title"]))

        if not pdf_files:
            continue

        extracted_sections = []
        sub_analysis = []
        importance_rank = 1

        for file_path, doc_title in pdf_files:
            document_name = os.path.basename(file_path)
            custom_query = build_custom_query(doc_title, base_query)
            query_embedding = model.encode(custom_query, convert_to_tensor=True)

            sections = extract_sections(file_path)
            ranked = rank_sections(sections, query_embedding)

            if ranked:
                top_section = ranked[0]
                extracted_sections.append({
                    "document": document_name,
                    "section_title": extract_section_title(top_section["text"]),
                    "importance_rank": importance_rank,
                    "page_number": top_section["page_number"]
                })
                for r in ranked[:3]:
                    sub_analysis.append({
                        "document": document_name,
                        "refined_text": r["text"][:1000].strip(),
                        "page_number": r["page_number"]
                    })
                importance_rank += 1

        output_data = {
            "metadata": {
                "input_documents": [os.path.basename(f[0]) for f in pdf_files],
                "persona": persona,
                "job_to_be_done": job,
                "processing_timestamp": datetime.datetime.now().isoformat()
            },
            "extracted_sections": extracted_sections,
            "subsection_analysis": sub_analysis
        }

        output_path = os.path.join(collection_path, "output.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=4)
print(" All collections processed successfully!")            


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf_dir", required=True, help="Path to folder containing collections (e.g., Challenge_1b)")
    args = parser.parse_args()

    run_pipeline(args.pdf_dir)
