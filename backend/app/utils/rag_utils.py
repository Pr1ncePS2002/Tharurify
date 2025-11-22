import os
import logging
import unicodedata
import nltk
import requests
import zipfile
import io
from dotenv import load_dotenv
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
load_dotenv()
nltk.download('punkt', quiet=True)

FAISS_INDEX_PATH = "/tmp/faiss_index"
FAISS_INDEX_URL = os.getenv("FAISS_INDEX_URL") # Will be read from .env

def download_and_unzip_faiss_index(url: str, dest_path: str):
    """Downloads and unzips the FAISS index from a URL."""
    if not url:
        logger.warning("FAISS_INDEX_URL is not set. Skipping download.")
        return False
    
    logger.info(f"Downloading FAISS index from {url}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        os.makedirs(dest_path, exist_ok=True)
        
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall(dest_path)
        logger.info(f"Successfully downloaded and extracted index to {dest_path}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download FAISS index: {e}", exc_info=True)
        return False
    except zipfile.BadZipFile:
        logger.error("Downloaded file is not a valid zip archive.", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred during index download/extraction: {e}", exc_info=True)
        return False

# --- Util: Clean Unicode ---
def clean_text_for_embedding(text: str) -> str:
    """Normalizes and cleans text to ensure it's UTF-8 compatible for embedding."""
    normalized_text = unicodedata.normalize('NFKC', text)
    cleaned_chars = [char for char in normalized_text if char.encode('utf-8', 'ignore')]
    return "".join(cleaned_chars)

# --- Main Function ---
def load_and_embed_docs() -> FAISS:
    """
    Loads the FAISS vector store.
    It first checks for a local index. If not found, it attempts to download
    and unzip it from a URL specified by the FAISS_INDEX_URL environment variable.
    If downloading fails or is not configured, it returns a dummy retriever.
    """
    logger.info("Attempting to load FAISS vector store.")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY environment variable is not set.")
        raise ValueError("GOOGLE_API_KEY is not set.")

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)

    # 1. Check for an existing local index
    if os.path.exists(FAISS_INDEX_PATH) and os.listdir(FAISS_INDEX_PATH):
        try:
            logger.info(f"Loading existing FAISS vectorstore from {FAISS_INDEX_PATH}")
            vectorstore = FAISS.load_local(
                FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True
            )
            logger.info("Successfully loaded existing FAISS index.")
            return vectorstore.as_retriever(search_kwargs={"k": 3})
        except Exception as e:
            logger.error(f"Failed to load local FAISS index: {e}. Will attempt to download.", exc_info=True)

    # 2. If local index fails or doesn't exist, download from URL
    if download_and_unzip_faiss_index(FAISS_INDEX_URL, FAISS_INDEX_PATH):
        try:
            logger.info(f"Loading newly downloaded FAISS vectorstore from {FAISS_INDEX_PATH}")
            vectorstore = FAISS.load_local(
                FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True
            )
            logger.info("Successfully loaded downloaded FAISS index.")
            return vectorstore.as_retriever(search_kwargs={"k": 3})
        except Exception as e:
            logger.error(f"Failed to load the downloaded FAISS index: {e}", exc_info=True)

    # 3. Fallback: If all else fails, create a dummy retriever
    logger.warning("Could not load or download a FAISS index. Creating a dummy retriever.")
    dummy_doc = Document(page_content="Error: Knowledge base is currently unavailable. Please check the server logs.")
    vectorstore = FAISS.from_documents([dummy_doc], embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": 1})
