from langchain.docstore.document import Document
from app.vector.store import build_store, similarity_search


def test_vector_store_faiss_basic():
    docs = [Document(page_content="Python is great."), Document(page_content="Java is robust."), Document(page_content="Rust is fast.")]
    store = build_store(docs, collection_name="test_collection")
    results = similarity_search(store, "fast language", k=2)
    assert len(results) >= 1
