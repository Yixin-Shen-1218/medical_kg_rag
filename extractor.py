# extractor.py
import os
import re
import importlib.util
from typing import List, Dict
from config import TUPLE_DELIM, RECORD_DELIM, COMPLETION_DELIM, USE_OPENAI, OPENAI_API_KEY

# === Load prompt file ===
PROMPT_MODULE_PATH = os.path.join(os.path.dirname(__file__), "prompt_iuxray.py")
spec = importlib.util.spec_from_file_location("prompt_iuxray", PROMPT_MODULE_PATH)
prompt_mm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prompt_mm)
PROMPTS = getattr(prompt_mm, "PROMPTS", {})

# OpenAI
if USE_OPENAI:
    import openai
    openai.api_key = OPENAI_API_KEY

def parse_entity_extraction_output(raw: str) -> Dict:
    """Parse the raw LLM output into structured entities and relationships"""
    records = [r.strip() for r in raw.split(RECORD_DELIM) if r.strip()]
    entities, relationships = [], []
    for rec in records:
        parts = [p.strip().strip('"') for p in rec.strip().strip("() ").split(TUPLE_DELIM)]
        if not parts: 
            continue
        tag = parts[0].lower()
        if tag == "entity" and len(parts) >= 4:
            entities.append({
                "name": parts[1],
                "type": parts[2],
                "description": parts[3]
            })
        elif tag == "relationship" and len(parts) >= 5:
            relationships.append({
                "source": parts[1],
                "target": parts[2],
                "description": parts[3],
                "strength": parts[4]
            })
    return {"entities": entities, "relationships": relationships}

def call_llm_entity_extraction(text: str, entity_types: List[str]=None, model="gpt-4o-mini"):
    """Call LLM for entity extraction using the provided prompt"""
    template = PROMPTS.get("entity_extraction")
    if not template:
        raise RuntimeError("entity_extraction prompt not found in prompt_iuxray.py")

    entity_types = entity_types or PROMPTS.get("DEFAULT_ENTITY_TYPES", [])
    prompt = template.format(
        entity_types=",".join(entity_types),
        input_text=text,
        tuple_delimiter=TUPLE_DELIM,
        record_delimiter=RECORD_DELIM,
        completion_delimiter=COMPLETION_DELIM
    )

    resp = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a structured information extractor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    raw = resp["choices"][0]["message"]["content"]
    raw = raw.split(COMPLETION_DELIM)[0]
    return raw

def spacy_fallback_extract(text: str):
    """Fallback extractor using spaCy NER (no relationships)"""
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
    except Exception:
        import subprocess
        subprocess.run(["python","-m","spacy","download","en_core_web_sm"], check=True)
        nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    ents = []
    for e in doc.ents:
        ents.append({
            "name": e.text.upper(),
            "type": e.label_.lower(),
            "description": f"spaCy label={e.label_}"
        })
    return {"entities": ents, "relationships": []}
