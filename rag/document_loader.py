import os
from typing import List
from langchain.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentLoader:
    def __init__(self, docs_path: str = "knowledge_base"):
        self.docs_path = docs_path
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,        # Размер одного куска текста
            chunk_overlap=200,      # Перекрытие между кусками
            separators=["\n\n", "\n", ".", " "]
        )
    
    def load_documents(self) -> List:
        """
        Загрузка всех документов из папки
        """
        logger.info(f"Загрузка документов из {self.docs_path}...")
        
        # Загрузка всех .txt файлов
        loader = DirectoryLoader(
            self.docs_path,
            glob="**/*.txt",
            loader_cls=TextLoader,
            loader_kwargs={'encoding': 'utf-8'}
        )
        
        documents = loader.load()
        logger.info(f"Загружено {len(documents)} документов")
        
        # Разбиение на чанки
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Создано {len(chunks)} чанков")
        
        return chunks
    
    def add_metadata(self, chunks: List) -> List:
        """
        Добавление метаданных к чанкам (для фильтрации)
        """
        for chunk in chunks:
            # Определяем тип документа по имени файла
            source = chunk.metadata.get('source', '')
            
            if 'decision_85' in source:
                chunk.metadata['type'] = 'regulation_russia'
                chunk.metadata['authority'] = 'EEC'
            elif 'ema' in source:
                chunk.metadata['type'] = 'regulation_international'
                chunk.metadata['authority'] = 'EMA'
            elif 'fda' in source:
                chunk.metadata['type'] = 'regulation_international'
                chunk.metadata['authority'] = 'FDA'
            elif 'protocol' in source:
                chunk.metadata['type'] = 'example_protocol'
            else:
                chunk.metadata['type'] = 'general'
        
        return chunks
```

---

## 🔢 **Шаг 2: Векторизация (Embeddings)**

### **2.1 Что такое Embeddings**
```
Текст: "При CV > 50% требуется 4-way replicate дизайн"
       ↓ (Embedding model)
Vector: [0.23, -0.45, 0.89, ..., 0.12]  # 384 числа