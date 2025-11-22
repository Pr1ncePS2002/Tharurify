"""Vector store abstraction layer.
Supports local FAISS and optional Qdrant if QDRANT_URL env is set.
"""
import os
from typing import List
from langchain.docstore.document import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

try:
    from qdrant_client import QdrantClient
    from langchain_community.vectorstores import Qdrant
except ImportError:  # qdrant optional
    QdrantClient = None
    Qdrant = None

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")  # e.g. http://localhost:6333
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

_embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)


def build_store(documents: List[Document], collection_name: str = "default"):
    if QDRANT_URL and QdrantClient is not None:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        return Qdrant.from_documents(documents, _embeddings, location=QDRANT_URL, collection_name=collection_name, api_key=QDRANT_API_KEY)
    return FAISS.from_documents(documents, _embeddings)


def similarity_search(store, query: str, k: int = 3):
    return store.similarity_search(query, k=k)
