"""
Image similarity matching module using CLIP embeddings
Compares user's uploaded image with product images to find best matches
"""

from sentence_transformers import SentenceTransformer, util
from PIL import Image
import requests
from io import BytesIO
from typing import List, Dict, Union
import torch
import streamlit as st


@st.cache_resource
def load_clip_model():
    """Load and cache the CLIP model"""
    print("Loading CLIP model...")
    model = SentenceTransformer('clip-ViT-B-32')
    print("CLIP model loaded successfully")
    return model


def get_image_embedding(image_source: Union[str, bytes], model: SentenceTransformer):
    """
    Get CLIP embedding for an image
    
    Args:
        image_source: Either a URL (str) or image bytes
        model: Loaded CLIP model
    
    Returns:
        Image embedding tensor or None if error
    """
    try:
        if isinstance(image_source, str):  # URL
            response = requests.get(image_source, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
        else:  # bytes
            img = Image.open(BytesIO(image_source))
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if too large (for performance)
        max_size = 512
        if max(img.size) > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Get embedding
        embedding = model.encode(img, convert_to_tensor=True)
        return embedding
    
    except Exception as e:
        print(f"Error getting embedding for image: {e}")
        return None


def find_best_matches(
    original_image: Union[str, bytes],
    products: List[Dict],
    top_k: int = 5,
    min_similarity: float = 0.2
) -> List[Dict]:
    """
    Find products most visually similar to the original image
    
    Args:
        original_image: User's uploaded image (URL or bytes)
        products: List of product dictionaries with 'thumbnail' field
        top_k: Number of top matches to return
        min_similarity: Minimum similarity score (0-1) to include
    
    Returns:
        List of products with similarity scores, sorted by best match
    """
    
    # Load model
    model = load_clip_model()
    
    # Get embedding for original image
    print("Getting embedding for original image...")
    original_embedding = get_image_embedding(original_image, model)
    if original_embedding is None:
        print("Failed to get embedding for original image")
        return []
    
    # Get embeddings for all product images
    print(f"Processing {len(products)} product images...")
    product_embeddings = []
    valid_products = []
    
    for idx, product in enumerate(products):
        thumbnail = product.get('thumbnail')
        if not thumbnail:
            continue
        
        emb = get_image_embedding(thumbnail, model)
        if emb is not None:
            product_embeddings.append(emb)
            valid_products.append(product)
            
            # Progress feedback for large batches
            if (idx + 1) % 5 == 0:
                print(f"Processed {idx + 1}/{len(products)} images...")
    
    if not product_embeddings:
        print("No valid product embeddings found")
        return []
    
    print(f"Successfully processed {len(product_embeddings)} product images")
    
    # Calculate cosine similarity
    product_embeddings_tensor = torch.stack(product_embeddings)
    similarities = util.cos_sim(original_embedding, product_embeddings_tensor)[0]
    
    # Filter by minimum similarity
    valid_indices = (similarities >= min_similarity).nonzero(as_tuple=True)[0]
    if len(valid_indices) == 0:
        print(f"No products found with similarity >= {min_similarity}")
        return []
    
    # Get top K matches from valid ones
    filtered_similarities = similarities[valid_indices]
    filtered_products = [valid_products[i] for i in valid_indices]
    
    k = min(top_k, len(filtered_similarities))
    top_results = torch.topk(filtered_similarities, k=k)
    
    # Build results
    matches = []
    for score, idx in zip(top_results.values, top_results.indices):
        product = filtered_products[idx.item()].copy()
        similarity_score = float(score)
        product['similarity_score'] = similarity_score
        product['match_percentage'] = int(similarity_score * 100)
        matches.append(product)
    
    print(f"Found {len(matches)} matches above threshold")
    return matches


def compare_two_images(image1: Union[str, bytes], image2: Union[str, bytes]) -> float:
    """
    Compare two images and return similarity score
    
    Args:
        image1: First image (URL or bytes)
        image2: Second image (URL or bytes)
    
    Returns:
        Similarity score between 0 and 1
    """
    model = load_clip_model()
    
    emb1 = get_image_embedding(image1, model)
    emb2 = get_image_embedding(image2, model)
    
    if emb1 is None or emb2 is None:
        return 0.0
    
    similarity = util.cos_sim(emb1, emb2)[0][0]
    return float(similarity)
