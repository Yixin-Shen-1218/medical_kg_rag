import os
import json
import argparse
from tqdm import tqdm
from extractor import call_llm_entity_extraction, parse_entity_extraction_output, spacy_fallback_extract, USE_OPENAI
from neo4j_client import Neo4jClient
from image_processor import ImageProcessor

# 默认配置
DEFAULT_TEXT_FILE = "report_10.txt"
DEFAULT_ANNOTATION_FILE = "./iu_xray/annotation.json"
DEFAULT_IMAGE_DIR = "./images_10/"

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

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Process medical reports and images into a knowledge graph")
    parser.add_argument("--text-file", type=str, default=DEFAULT_TEXT_FILE,
                        help=f"Path to the text file containing reports (default: {DEFAULT_TEXT_FILE})")
    parser.add_argument("--annotation-file", type=str, default=DEFAULT_ANNOTATION_FILE,
                        help=f"Path to the annotation JSON file (default: {DEFAULT_ANNOTATION_FILE})")
    parser.add_argument("--image-dir", type=str, default=DEFAULT_IMAGE_DIR,
                        help=f"Directory containing images (default: {DEFAULT_IMAGE_DIR})")
    parser.add_argument("--clear-db", action="store_true",
                        help="Clear the database before processing")
    return parser.parse_args()

def main():
    # 解析命令行参数
    args = parse_arguments()
    
    # 使用参数或默认值
    text_file = args.text_file
    annotation_file = args.annotation_file
    image_dir = args.image_dir
    
    docs = load_texts(text_file)
    image_mapping = create_image_mapping(annotation_file, image_dir)
    client = Neo4jClient()
    image_processor = ImageProcessor()
    
    # 根据参数决定是否清空数据库
    if args.clear_db:
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