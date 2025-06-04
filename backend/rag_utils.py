import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict

# Use a free, local embedding model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # You can change to any supported model
MODEL = SentenceTransformer(EMBEDDING_MODEL)

# Load knowledge base
with open(os.path.join(os.path.dirname(__file__), "knowledge_base.json"), "r", encoding="utf-8") as f:
    KB = json.load(f)

# In-memory cache for embeddings
EMBEDDINGS = {}

def get_embedding(text: str) -> List[float]:
    """Get embedding for a text using SentenceTransformers (local, free)."""
    return MODEL.encode([text])[0].tolist()

def ensure_kb_embeddings():
    """Compute and cache embeddings for all KB entries."""
    for entry in KB:
        if entry["id"] not in EMBEDDINGS:
            EMBEDDINGS[entry["id"]] = get_embedding(entry["content"])

def cosine_similarity(a: List[float], b: List[float]) -> float:
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def retrieve_relevant_kb(query: str, top_k: int = 2) -> List[Dict]:
    ensure_kb_embeddings()
    query_emb = get_embedding(query)
    scored = [
        (cosine_similarity(query_emb, EMBEDDINGS[entry["id"]]), entry)
        for entry in KB
    ]
    scored.sort(reverse=True, key=lambda x: x[0])
    return [entry for _, entry in scored[:top_k]]
