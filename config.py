import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask settings
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 8000))
    
    # LLM settings
    HF_MODEL = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
    HF_TOKEN = os.getenv("HF_TOKEN", "")
    
    # Alternative models
    MODELS = {
        "mistral": "mistralai/Mistral-7B-Instruct-v0.2",
        "llama": "meta-llama/Llama-2-7b-chat-hf",
        "zephyr": "HuggingFaceH4/zephyr-7b-beta",
        "tinyllama": "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # для слабых ПК
    }
    
    # RAG settings
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "vectorstore_index")
    KNOWLEDGE_BASE_PATH = os.getenv("KNOWLEDGE_BASE_PATH", "knowledge_base")
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", 5))
    
    # API KEYS для внешних сервисов
    NCBI_API_KEY = os.getenv("NCBI_API_KEY", "")  # PubMed
    NCBI_EMAIL = os.getenv("NCBI_EMAIL", "your.email@example.com")
    DRUGBANK_API_KEY = os.getenv("DRUGBANK_API_KEY", "")  # DrugBank (опционально)
    
    # Scraping settings
    REQUEST_TIMEOUT = 30
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # секунд
    
    # Output settings
    OUTPUT_DIR = "outputs"
    SUPPORTED_FORMATS = ["docx", "json", "markdown"]
    
    # Performance
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", 3))
