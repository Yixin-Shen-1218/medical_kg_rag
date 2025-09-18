import torch
import torchvision.transforms as transforms
from PIL import Image
from transformers import CLIPProcessor, CLIPModel, CLIPTokenizer
import numpy as np

class ImageProcessor:
    def __init__(self):
        """Initialize CLIP model for image and text feature extraction"""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-base-patch32")
        
    def extract_features(self, image_path):
        """Extract feature vector from an image using CLIP"""
        try:
            image = Image.open(image_path).convert("RGB")
            inputs = self.processor(images=image, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)
            
            # Normalize feature vector
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            return image_features.cpu().numpy().flatten().tolist()
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            return None
    
    def extract_text_features(self, text):
        """Extract feature vector from text using CLIP"""
        try:
            inputs = self.tokenizer(text, return_tensors="pt", padding=True).to(self.device)
            
            with torch.no_grad():
                text_features = self.model.get_text_features(**inputs)
            
            # Normalize feature vector
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            return text_features.cpu().numpy().flatten().tolist()
        except Exception as e:
            print(f"Error processing text {text}: {e}")
            return None
    
    def calculate_similarity(self, text, image_features):
        """Calculate similarity between text and image features"""
        text_features = self.extract_text_features(text)
        if text_features is None or image_features is None:
            return 0.0
        
        # Calculate cosine similarity
        similarity = np.dot(text_features, image_features) / (
            np.linalg.norm(text_features) * np.linalg.norm(image_features)
        )
        return similarity
    
    def calculate_image_similarity(self, image_features1, image_features2):
        """Calculate similarity between two image feature vectors"""
        if image_features1 is None or image_features2 is None:
            return 0.0
        
        # Calculate cosine similarity
        similarity = np.dot(image_features1, image_features2) / (
            np.linalg.norm(image_features1) * np.linalg.norm(image_features2)
        )
        return similarity