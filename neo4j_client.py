from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

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

    def create_image_node(self, image_path: str, feature_vector: list, doc_id: str):
        """Create an Image node and link it to the Document"""
        with self.driver.session() as session:
            # Create Image node
            session.run(
                "MERGE (i:Image {path:$path}) "
                "SET i.feature_vector = $feature_vector, i.doc_id = $doc_id",
                path=image_path, feature_vector=feature_vector, doc_id=doc_id
            )
            # Link to document
            session.run(
                "MATCH (d:Document {doc_id:$doc_id}), (i:Image {path:$path}) "
                "MERGE (d)-[:HAS_IMAGE]->(i)",
                doc_id=doc_id, path=image_path
            )
    
    def link_entity_to_image(self, entity_name: str, entity_type: str, image_path: str, similarity: float):
        """Link Entity to Image based on similarity"""
        with self.driver.session() as session:
            session.run(
                "MATCH (e:Entity {name:$name, type:$type}), (i:Image {path:$path}) "
                "MERGE (e)-[r:APPEARS_IN]->(i) "
                "SET r.similarity = $similarity",
                name=entity_name, type=entity_type, path=image_path, similarity=similarity
            )

    def clear_all(self):
        """Delete all nodes and relationships in the database (for testing)"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
    
    def find_similar_images(self, feature_vector, top_k=5):
        """Find images with similar feature vectors using cosine similarity"""
        with self.driver.session() as session:
            # Get all images with their feature vectors
            result = session.run(
                "MATCH (i:Image) RETURN i.path AS path, i.feature_vector AS feature_vector"
            )
            
            images = []
            similarities = []
            
            for record in result:
                path = record["path"]
                db_vector = record["feature_vector"]
                
                if db_vector is not None:
                    # Calculate cosine similarity
                    similarity = cosine_similarity([feature_vector], [db_vector])[0][0]
                    images.append(path)
                    similarities.append(similarity)
            
            # Sort by similarity and return top K
            sorted_indices = np.argsort(similarities)[::-1][:top_k]
            return [(images[i], similarities[i]) for i in sorted_indices]
    
    def get_document_by_image(self, image_path):
        """Get document associated with an image"""
        with self.driver.session() as session:
            result = session.run(
                "MATCH (d:Document)-[:HAS_IMAGE]->(i:Image {path:$path}) "
                "RETURN d.doc_id AS doc_id, d.text AS text",
                path=image_path
            )
            return result.single()
    
    def get_entities_by_image(self, image_path):
        """Get entities associated with an image"""
        with self.driver.session() as session:
            result = session.run(
                "MATCH (e:Entity)-[r:APPEARS_IN]->(i:Image {path:$path}) "
                "RETURN e.name AS name, e.type AS type, e.description AS description, r.similarity AS similarity "
                "ORDER BY r.similarity DESC",
                path=image_path
            )
            return [dict(record) for record in result]
    
    def get_related_entities(self, entity_name, entity_type):
        """Get entities related to a specific entity"""
        with self.driver.session() as session:
            result = session.run(
                "MATCH (e1:Entity {name:$name, type:$type})-[r:RELATED_TO]->(e2:Entity) "
                "RETURN e2.name AS name, e2.type AS type, e2.description AS description, r.strength AS strength, r.desc AS relation_desc "
                "ORDER BY r.strength DESC",
                name=entity_name, type=entity_type
            )
            return [dict(record) for record in result]
    
    def search_entities_by_text(self, search_text):
        """Search entities by text similarity in name or description"""
        with self.driver.session() as session:
            result = session.run(
                "MATCH (e:Entity) "
                "WHERE e.name CONTAINS $search_text OR e.description CONTAINS $search_text "
                "RETURN e.name AS name, e.type AS type, e.description AS description",
                search_text=search_text.lower()
            )
            return [dict(record) for record in result]