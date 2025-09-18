# prepare_image_mapping.py
import json
import os

def create_image_mapping(text_file, annotation_file, target_image_dir, output_file):
    """Create mapping between documents and associated images (2 images per document)"""
    # Load documents
    with open(text_file, "r", encoding="utf-8") as f:
        content = f.read().strip()
    docs = [p.strip() for p in content.split("\n\n") if p.strip()]
    if len(docs) < 2:
        docs = [p.strip() for p in content.splitlines() if p.strip()]
    
    # Load annotation data
    with open(annotation_file, 'r') as f:
        data = json.load(f)
    
    # Extract image paths for each document
    mapping = {}
    for i, doc in enumerate(docs):
        doc_id = f"doc_{i+1}"
        if i < len(data['train']):
            # Each document has 2 associated images
            image_paths = [os.path.join(target_image_dir, img_path) 
                          for img_path in data['train'][i]['image_path']]
            mapping[doc_id] = image_paths
        else:
            mapping[doc_id] = []
    
    # Save mapping
    with open(output_file, "w") as f:
        json.dump(mapping, f, indent=2)
    
    print(f"Image mapping saved to {output_file}")
    print(f"Created mapping for {len(mapping)} documents")
    for doc_id, images in mapping.items():
        print(f"{doc_id}: {len(images)} images")

if __name__ == "__main__":
    create_image_mapping(
        "report_10.txt", 
        "./iu_xray/annotation.json",
        "./images_10/", 
        "image_mapping_10.json"
    )