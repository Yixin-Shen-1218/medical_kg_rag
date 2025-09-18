import os
import json
import argparse
from neo4j_client import Neo4jClient
from image_processor import ImageProcessor
from extractor import call_llm_entity_extraction, parse_entity_extraction_output
from config import USE_OPENAI
import openai

class VQATester:
    def __init__(self):
        self.client = Neo4jClient()
        self.image_processor = ImageProcessor()
    
    def answer_question(self, image_path, question_text):
        """Answer a question based on an image and text query"""
        print(f"Processing image: {image_path}")
        print(f"Question: {question_text}")
        
        # Extract features from the input image
        query_features = self.image_processor.extract_features(image_path)
        if query_features is None:
            return "Error: Could not process the input image."
        
        # Find similar images in the database
        similar_images = self.client.find_similar_images(query_features, top_k=3)
        
        if not similar_images:
            return "No similar images found in the database."
        
        print(f"Found {len(similar_images)} similar images:")
        for img_path, similarity in similar_images:
            print(f"  - {img_path} (similarity: {similarity:.3f})")
        
        # Get the most similar image
        most_similar_image = similar_images[0][0]
        
        # Get document associated with the image
        document = self.client.get_document_by_image(most_similar_image)
        if document is None:
            return "No document associated with the similar image."
        
        # Get entities associated with the image
        entities = self.client.get_entities_by_image(most_similar_image)
        
        # Prepare context for the LLM
        context = self._prepare_context(document, entities, question_text)
        
        # Generate answer using LLM
        answer = self._generate_answer(context, question_text)
        
        return answer
    
    def _prepare_context(self, document, entities, question_text):
        """Prepare context information for the LLM"""
        context = {
            "document": {
                "doc_id": document["doc_id"],
                "text": document["text"][:1000] + "..." if len(document["text"]) > 1000 else document["text"]
            },
            "entities": entities,
            "question": question_text
        }
        
        # Add related entities for each entity
        for entity in context["entities"]:
            related_entities = self.client.get_related_entities(entity["name"], entity["type"])
            entity["related_entities"] = related_entities
        
        return context
    
    def _generate_answer(self, context, question_text):
        """Generate answer using LLM based on context"""
        if not USE_OPENAI:
            return "OpenAI API is not enabled. Please enable it in config.py to use VQA functionality."
        
        # Prepare prompt for the LLM
        prompt = self._create_prompt(context, question_text)

        print("prompt: ", prompt)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful medical assistant that answers questions based on the provided context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def _create_prompt(self, context, question_text):
        """Create prompt for the LLM"""
        # Format document information
        doc_info = f"Document ID: {context['document']['doc_id']}\n"
        doc_info += f"Document Text: {context['document']['text']}\n\n"
        
        # Format entity information
        entity_info = "Entities found in similar images:\n"
        for i, entity in enumerate(context["entities"], 1):
            entity_info += f"{i}. {entity['name']} ({entity['type']}) - {entity['description']}\n"
            entity_info += f"   Similarity to image: {entity.get('similarity', 'N/A'):.3f}\n"
            
            # Add related entities
            if entity.get("related_entities"):
                entity_info += "   Related entities:\n"
                for rel_entity in entity["related_entities"][:3]:  # Limit to top 3
                    entity_info += f"     - {rel_entity['name']} ({rel_entity['type']}) - {rel_entity.get('relation_desc', 'No description')}\n"
            
            entity_info += "\n"
        
        prompt = f"""
Based on the following medical context, please answer the question: "{question_text}"

CONTEXT INFORMATION:
{doc_info}
{entity_info}

QUESTION: {question_text}

Please provide a comprehensive answer based on the context. If the context doesn't contain enough information to answer the question, please state that clearly.

ANSWER:
"""
        return prompt
    
    def close(self):
        """Close connections"""
        self.client.close()

def main():
    parser = argparse.ArgumentParser(description="VQA Test for Multimodal RAG Graph")
    parser.add_argument("--image", required=True, help="Path to the input image")
    parser.add_argument("--question", required=True, help="Question to ask about the image")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    vqa_tester = VQATester()
    
    if args.interactive:
        print("Running in interactive mode. Type 'quit' to exit.")
        while True:
            image_path = input("Enter image path: ").strip()
            if image_path.lower() == 'quit':
                break
                
            question = input("Enter your question: ").strip()
            if question.lower() == 'quit':
                break
                
            answer = vqa_tester.answer_question(image_path, question)
            print("\nANSWER:")
            print(answer)
            print("\n" + "="*50 + "\n")
    else:
        answer = vqa_tester.answer_question(args.image, args.question)
        print("\nANSWER:")
        print(answer)
    
    vqa_tester.close()

if __name__ == "__main__":
    main()