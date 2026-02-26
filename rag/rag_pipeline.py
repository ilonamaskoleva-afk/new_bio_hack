from vector_store import VectorStore
from models.llm_handler import get_llm
from prompts.prompts import Prompts
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self):
        self.vectorstore = VectorStore()
        self.vectorstore.load("vectorstore_index")
        self.llm = get_llm()
    
    def retrieve_context(self, query: str, k: int = 3) -> str:
        """
        Получить релевантный контекст из базы знаний
        """
        results = self.vectorstore.search(query, k=k)
        
        # Формируем контекст
        context_parts = []
        for i, (doc, score) in enumerate(results, 1):
            source = doc.metadata.get('source', 'Unknown')
            context_parts.append(f"""
[Источник {i}: {source}]
{doc.page_content}
""")
        
        return "\n\n".join(context_parts)
    
    def answer_with_rag(self, question: str, context_type: str = "general") -> dict:
        """
        Ответ на вопрос с использованием RAG
        
        Args:
            question: вопрос пользователя
            context_type: тип контекста ("regulation", "protocol", "pk_data", "general")
        """
        logger.info(f"RAG запрос: {question}")
        
        # 1. Retrieve: поиск релевантного контекста
        context = self.retrieve_context(question, k=5)
        
        # 2. Augment: дополнение промпта контекстом
        augmented_prompt = f"""
Ты - эксперт по клинической фармакологии и регуляторным требованиям.

КОНТЕКСТ ИЗ БАЗЫ ЗНАНИЙ:
{context}

ВОПРОС ПОЛЬЗОВАТЕЛЯ:
{question}

ИНСТРУКЦИИ:
1. Используй ТОЛЬКО информацию из предоставленного контекста
2. Всегда указывай источник (например: "Согласно Решению №85...")
3. Если информации недостаточно - скажи об этом честно
4. Ответ должен быть точным и профессиональным

ОТВЕТ:
"""
        
        # 3. Generate: генерация ответа
        response = self.llm.generate(
            augmented_prompt,
            system_prompt=Prompts.SYSTEM_PROMPT,
            max_tokens=1024
        )
        
        return {
            "answer": response,
            "context_used": context,
            "sources": [doc.metadata.get('source') for doc, _ in self.vectorstore.search(question, k=3)]
        }
    
    def design_recommendation_with_rag(self, inn: str, cvintra: float, 
                                       administration_mode: str) -> dict:
        """
        Рекомендация дизайна с использованием RAG
        """
        # Формируем специфичный запрос
        query = f"""
Какой дизайн исследования биоэквивалентности рекомендуется для препарата 
с внутрисубъектной вариабельностью CVintra={cvintra}%?
Режим приёма: {administration_mode}.
Укажите требования регуляторных органов (Решение №85, EMA, FDA).
"""
        
        # Получаем контекст из регуляторных документов
        context = self.retrieve_context(query, k=5)
        
        # Промпт с контекстом
        prompt = f"""
РЕГУЛЯТОРНЫЕ ТРЕБОВАНИЯ:
{context}

ПРЕПАРАТ: {inn}
CVintra: {cvintra}%
Режим приёма: {administration_mode}

На основе регуляторных требований выбери оптимальный дизайн исследования.

Ответь в формате JSON:
{{
    "recommended_design": "название дизайна",
    "rationale": "обоснование со ссылками на документы",
    "regulatory_basis": ["список требований"],
    "sample_size_formula": "формула для расчета",
    "washout_requirements": "требования к washout периоду",
    "citations": ["конкретные пункты документов"]
}}
"""
        
        result = self.llm.generate_json(prompt, Prompts.SYSTEM_PROMPT)
        result['context_used'] = context
        
        return result
    
    def generate_synopsis_with_rag(self, study_data: dict) -> str:
        """
        Генерация синопсиса с использованием RAG
        """
        # Получаем примеры протоколов
        query = f"Пример синопсиса протокола BE исследования для {study_data.get('inn')}"
        context = self.retrieve_context(query, k=3)
        
        prompt = f"""
ПРИМЕРЫ ПРОТОКОЛОВ ИЗ БАЗЫ:
{context}

ДАННЫЕ ДЛЯ СИНОПСИСА:
{study_data}

Сгенерируй профессиональный синопсис протокола BE исследования в стиле 
примеров из базы. Используй медицинскую терминологию и структуру ICH-GCP.

Включи все необходимые разделы с цитированием регуляторных требований.
"""
        
        synopsis = self.llm.generate(prompt, Prompts.SYSTEM_PROMPT, max_tokens=4096)
        
        return synopsis