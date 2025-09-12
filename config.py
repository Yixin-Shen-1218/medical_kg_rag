# config.py
import os

# === Neo4j connection settings ===
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

# === LLM / OpenAI settings ===
USE_OPENAI = os.getenv("USE_OPENAI", "true").lower() in ("1","true","yes")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# === Prompt delimiters ===
TUPLE_DELIM = "<|>"
RECORD_DELIM = "##"
COMPLETION_DELIM = "<|COMPLETE|>"
