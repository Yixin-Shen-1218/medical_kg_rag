# ingest.py
import os
from tqdm import tqdm
from extractor import call_llm_entity_extraction, parse_entity_extraction_output, spacy_fallback_extract, USE_OPENAI
from neo4j_client import Neo4jClient

TEXT_FILE = os.path.join(os.path.dirname(__file__), "report_50.txt")

def load_texts(path):
    """Load all reports from the input file"""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    parts = [p.strip() for p in content.split("\n\n") if p.strip()]
    if len(parts) < 2:
        parts = [p.strip() for p in content.splitlines() if p.strip()]
    return parts

def main():
    docs = load_texts(TEXT_FILE)
    client = Neo4jClient()
    # Uncomment for testing to start from an empty database
    client.clear_all()
    print("The database is cleaned.")
    

    for idx, doc in enumerate(tqdm(docs, desc="Processing documents")):
        doc_id = f"doc_{idx+1}"
        print(f"\n--- Processing {doc_id} ---")
        try:
            if USE_OPENAI:
                raw = call_llm_entity_extraction(doc)
                parsed = parse_entity_extraction_output(raw)
            else:
                parsed = spacy_fallback_extract(doc)
        except Exception as e:
            print("Extraction failed:", e)
            parsed = spacy_fallback_extract(doc)

        client.create_document_subgraph(doc_id, doc, parsed["entities"], parsed["relationships"])

    client.close()
    print("All documents processed.")

if __name__ == "__main__":
    main()
