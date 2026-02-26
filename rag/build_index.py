#!/usr/bin/env python3
"""
Скрипт для создания векторного индекса
Запускается один раз для подготовки базы знаний
"""

from document_loader import DocumentLoader
from vector_store import VectorStore
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # 1. Загрузка документов
    loader = DocumentLoader(docs_path="../knowledge_base")
    documents = loader.load_documents()
    documents = loader.add_metadata(documents)
    
    logger.info(f"Всего чанков для индексации: {len(documents)}")
    
    # 2. Создание векторного хранилища
    vectorstore = VectorStore(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
        # Для русского+английского: "intfloat/multilingual-e5-large"
    )
    
    vectorstore.create_vectorstore(documents)
    
    # 3. Сохранение
    vectorstore.save("../vectorstore_index")
    
    # 4. Тестовый поиск
    logger.info("\n=== ТЕСТОВЫЙ ПОИСК ===")
    test_queries = [
        "Требования для препаратов с высокой вариабельностью",
        "Как рассчитать размер выборки для 2x2 crossover",
        "RSABE критерии"
    ]
    
    for query in test_queries:
        logger.info(f"\nЗапрос: {query}")
        results = vectorstore.search(query, k=2)
        for doc, score in results:
            logger.info(f"  - {doc.page_content[:100]}...")
    
    logger.info("\n✅ Индексация завершена!")

if __name__ == "__main__":
    main()