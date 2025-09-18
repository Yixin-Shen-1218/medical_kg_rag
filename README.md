# Multimodal RAG Graph with VQA for Medical Imaging

A comprehensive multimodal retrieval-augmented generation (RAG) system that connects medical text reports with corresponding X-ray images in a knowledge graph, enabling visual question answering (VQA) capabilities.

### Features

1. Multimodal Knowledge Graph: Stores medical reports, extracted entities, and image features in Neo4j

2. CLIP-based Image Processing: Extracts and compares image feature vectors using OpenAI's CLIP model

3. Visual Question Answering: Answers medical questions based on both image content and associated text

4. Entity Extraction: Uses LLMs to extract medical entities and relationships from radiology reports

5. Similarity Search: Finds similar images and related medical concepts using cosine similarity

### Project Structure

```text
Project/
├── config.py              # Configuration settings
├── extractor.py           # Entity extraction functions
├── image_processor.py     # Image feature extraction
├── main.py               # Main processing pipeline
├── neo4j_client.py       # Neo4j database operations
├── prepare_data.py       # Data preparation utilities
├── prepare_image_mapping.py # Image-document mapping
├── prompt_iuxray.py      # LLM prompt templates
├── vqa_test.py          # Visual question answering
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

Installation
1. Clone the repository

```bash
git clone <repository-url>
cd medical_kg_rag
```

2. Install Python dependencies

```bash
pip install -r requirements.txt
```

3. Download spaCy model

```bash
python -m spacy download en_core_web_sm
```

4. Set up Neo4j database
  - Install Neo4j Desktop or Server
  - Update connection settings in config.py
  - Default settings: bolt://localhost:7687 with username neo4j


5. Set up OpenAI API (optional for enhanced entity extraction)
   - Get an API key from OpenAI
   - Add it to your environment variables or update config.py

### Data Preparation

1. Download the IU X-Ray dataset
   1. Request access from https://drive.google.com/file/d/1c0BXEuDy8Cmm2jfN0YYGkQxFZd2ZIoLg/view
   2. Place the data in an iu_xray/ directory with structure:

```text
iu_xray/
├── images/
└── annotation.json
```

2. Prepare the data

```bash
python prepare_data.py
```

3. Create image-document mapping

```bash
python prepare_image_mapping.py
```

### Usage

1. #### Build the Knowledge Graph

  Process medical reports and images to build the multimodal graph:

```bash
# Use default setting（report_10.txt）
python main.py

# Use report_50.txt
python main.py --text-file report_50.txt --image-dir ./images_50/

# Use report_50.txt and clear the database
python main.py --text-file report_50.txt --image-dir ./images_50/ --clear-db
```

This will:

- Extract entities from medical reports
- Process X-ray images to extract feature vectors
- Store everything in Neo4j with relationships

2. #### Run Visual Question Answering

  Answer medical questions about X-ray images:

##### Single question mode:

```bash
python vqa_test.py --image path/to/xray.jpg --question "What abnormalities are visible?"

python vqa_test.py --image images_test/CXR95_IM-2445/0.png --question "What abnormalities are visible?"
```

##### Interactive mode:

```bash
python vqa_test.py --interactive
```



#### Example Questions

"What abnormalities are visible in this X-ray?"

"Is there any evidence of pneumonia in this image?"

"Describe the lung fields in this X-ray."

"Are there any foreign objects visible?"

"What is the cardiomediastinal silhouette like?"



### Configuration

Configure Neo4j and OpenAI:

```
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="password"
export OPENAI_API_KEY="your_key"
export USE_OPENAI=true   # or false to fallback to spaCy
```





