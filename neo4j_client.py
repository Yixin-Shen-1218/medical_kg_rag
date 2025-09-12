# neo4j_client.py
from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

class Neo4jClient:
    def __init__(self, uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_document_subgraph(self, doc_id: str, doc_text: str, entities: list, relationships: list):
        """Create a Document node, associated Entity nodes, and their relationships"""
        with self.driver.session() as session:
            # Create Document node
            session.run(
                "MERGE (d:Document {doc_id:$doc_id}) "
                "SET d.text=$text",
                doc_id=doc_id, text=doc_text
            )
            # Create Entity nodes and link them to the Document
            for ent in entities:
                session.run(
                    "MERGE (e:Entity {name:$name, type:$type}) "
                    "SET e.description=$desc",
                    name=ent["name"], type=ent.get("type","UNKNOWN"), desc=ent.get("description","")
                )
                session.run(
                    "MATCH (d:Document {doc_id:$doc_id}), (e:Entity {name:$name, type:$type}) "
                    "MERGE (d)-[:MENTIONS]->(e)",
                    doc_id=doc_id, name=ent["name"], type=ent.get("type","UNKNOWN")
                )
            # Create relationships between Entities
            for rel in relationships:
                session.run(
                    "MATCH (s:Entity {name:$sname}), (t:Entity {name:$tname}) "
                    "MERGE (s)-[r:RELATED_TO {desc:$desc, strength:$strength}]->(t)",
                    sname=rel["source"], tname=rel["target"],
                    desc=rel.get("description",""), strength=rel.get("strength","")
                )

    def clear_all(self):
        """Delete all nodes and relationships in the database (for testing)"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
