from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
import pickle
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Инициализация векторного хранилища
        
        Модели embeddings (от быстрых к точным):
        - all-MiniLM-L6-v2: 384 dim, быстрая, хорошее качество
        - all-mpnet-base-v2: 768 dim, медленнее, лучше качество
        - multilingual-e5-large: 1024 dim, поддержка русского + английского
        """
        logger.info(f"Инициализация embeddings модели: {model_name}")
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},  # или 'cuda' если есть GPU
            encode_kwargs={'normalize_embeddings': True}
        )
        
        self.vectorstore = None
        self.index_path = "vectorstore_index"
    
    def create_vectorstore(self, documents: list):
        """
        Создание векторного хранилища из документов
        """
        logger.info("Создание векторного хранилища...")
        
        self.vectorstore = FAISS.from_documents(
            documents=documents,
            embedding=self.embeddings
        )
        
        logger.info(f"Векторное хранилище создано с {len(documents)} документами")
    
    def save(self, path: str = None):
        """
        Сохранение векторного хранилища на диск
        """
        if path is None:
            path = self.index_path
        
        logger.info(f"Сохранение векторного хранилища в {path}...")
        self.vectorstore.save_local(path)
        logger.info("Сохранение завершено")
    
    def load(self, path: str = None):
        """
        Загрузка векторного хранилища с диска
        """
        if path is None:
            path = self.index_path
        
        if not os.path.exists(path):
            logger.error(f"Векторное хранилище не найдено: {path}")
            return False
        
        logger.info(f"Загрузка векторного хранилища из {path}...")
        self.vectorstore = FAISS.load_local(
            path,
            embeddings=self.embeddings,
            allow_dangerous_deserialization=True  # FAISS требует это
        )
        logger.info("Загрузка завершена")
        return True
    
    def search(self, query: str, k: int = 3, filter_dict: dict = None):
        """
        Поиск похожих документов
        
        Args:
            query: поисковый запрос
            k: количество результатов
            filter_dict: фильтр по метаданным, например {'type': 'regulation_russia'}
        
        Returns:
            List of (Document, score) tuples
        """
        if self.vectorstore is None:
            logger.error("Векторное хранилище не загружено")
            return []
        
        logger.info(f"Поиск по запросу: '{query}' (top-{k})")
        
        # Поиск с оценкой релевантности
        results = self.vectorstore.similarity_search_with_score(
            query,
            k=k,
            # filter=filter_dict  # FAISS не поддерживает фильтрацию напрямую
        )
        
        for i, (doc, score) in enumerate(results):
            logger.info(f"  {i+1}. Score: {score:.4f} | Source: {doc.metadata.get('source', 'N/A')}")
        
        return results
        