# similarity.py
# Compute cosine similarity between documents using Sentence-BERT
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text: str) -> np.ndarray:
    """Get sentence embedding for text."""
    return model.encode(text)

def compute_similarity(text1: str, text2: str) -> float:
    """Compute cosine similarity between two texts."""
    emb1 = get_embedding(text1)
    emb2 = get_embedding(text2)
    return cosine_similarity([emb1], [emb2])[0][0]

def check_similarity_threshold(docs: list, threshold: float = 0.80) -> bool:
    """
    Check if any pair of documents has similarity >= threshold.
    docs: list of (uuid, text) tuples
    """
    for i in range(len(docs)):
        for j in range(i+1, len(docs)):
            sim = compute_similarity(docs[i][1], docs[j][1])
            if sim >= threshold:
                return True
    return False

def compute_similarity_matrix(docs: list) -> np.ndarray:
    """
    Compute similarity matrix for all docs.
    docs: list of (uuid, text) tuples
    Returns: n x n matrix
    """
    texts = [doc[1] for doc in docs]
    embeddings = [get_embedding(text) for text in texts]
    return cosine_similarity(embeddings)