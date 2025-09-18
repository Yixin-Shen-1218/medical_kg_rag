import os
import json
from tqdm import tqdm
from extractor import call_llm_entity_extraction, parse_entity_extraction_output, spacy_fallback_extract, USE_OPENAI
from neo4j_client import Neo4jClient
from image_processor import ImageProcessor

TEXT_FILE = os.path.join(os.path.dirname(__file__), "report_10.txt")

def load_texts(path):
    """Load all reports from the input file"""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    parts = [p.strip() for p in content.split("\n\n") if p.strip()]
    if len(parts) < 2:
        parts = [p.strip() for p in content.splitlines() if p.strip()]
    return parts

def create_image_mapping(annotation_file, target_image_dir):
    """Create mapping between documents and associated images (2 images per document)"""
    # Load annotation data
    with open(annotation_file, 'r') as f:
        data = json.load(f)
    
    # Extract image paths for each document
    mapping = {}
    for i, item in enumerate(data['train']):
        doc_id = f"doc_{i+1}"
        # Each document has 2 associated images
        image_paths = [os.path.join(target_image_dir, img_path) 
                      for img_path in item['image_path']]
        mapping[doc_id] = image_paths
    
    return mapping

def main():
    docs = load_texts(TEXT_FILE)
    image_mapping = create_image_mapping("./iu_xray/annotation.json", "./images_10/")
    client = Neo4jClient()
    image_processor = ImageProcessor()
    
    # Uncomment for testing to start from an empty database
    client.clear_all()
    print("The database is cleaned.")
    
    for idx, doc in enumerate(tqdm(docs, desc="Processing documents")):
        doc_id = f"doc_{idx+1}"
        print(f"\n--- Processing {doc_id} ---")
        
        # Process text entity extraction
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
        
        # Process associated images
        if doc_id in image_mapping:
            image_paths = image_mapping[doc_id]
            for img_path in image_paths:
                # Extract image features
                features = image_processor.extract_features(img_path)
                if features:
                    # Create image node
                    client.create_image_node(img_path, features, doc_id)
                    
                    # Link entities to images based on similarity
                    for entity in parsed["entities"]:
                        similarity = image_processor.calculate_similarity(
                            entity["name"], features
                        )
                        if similarity > 0.3:  # Set similarity threshold
                            client.link_entity_to_image(
                                entity["name"], 
                                entity.get("type", "UNKNOWN"), 
                                img_path, 
                                similarity
                            )

    client.close()
    print("All documents processed.")

if __name__ == "__main__":
    main()