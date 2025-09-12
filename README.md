# medical_kg_rag

## Knowledge Graph from Radiology Reports (Python + Neo4j)

This project builds subgraphs from 50 reports in `report_50.txt`.  
Each line/paragraph is parsed into entities & relationships, then stored in Neo4j.

---

### Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt

2. Configure Neo4j and OpenAI (if used):
   ```bash
   export NEO4J_URI="bolt://localhost:7687"
   export NEO4J_USER="neo4j"
   export NEO4J_PASSWORD="password"
   export OPENAI_API_KEY="your_key"
   export USE_OPENAI=true   # or false to fallback to spaCy

3. Run ingestion:
   ```bash
   python ingest.py
