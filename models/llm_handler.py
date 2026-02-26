from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
import json
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMHandler:
    def __init__(self, model_name: str = "mistralai/Mistral-7B-Instruct-v0.2"):
        """
        Инициализация LLM модели из HuggingFace
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Загрузка модели {model_name} на {self.device}...")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                low_cpu_mem_usage=True
            )
            
            self.pipe = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=2048,
                temperature=0.7,
                top_p=0.95,
                do_sample=True
            )
            
            logger.info("Модель успешно загружена!")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки модели: {e}")
            raise
    
    def generate(self, prompt: str, system_prompt: str = "", max_tokens: int = 2048) -> str:
        """
        Генерация ответа от LLM
        """
        try:
            # Форматируем промпт для Mistral/Llama формата
            if system_prompt:
                full_prompt = f"<s>[INST] {system_prompt}\n\n{prompt} [/INST]"
            else:
                full_prompt = f"<s>[INST] {prompt} [/INST]"
            
            logger.info(f"Генерация ответа (max_tokens={max_tokens})...")
            
            response = self.pipe(
                full_prompt,
                max_new_tokens=max_tokens,
                return_full_text=False
            )
            
            result = response[0]['generated_text'].strip()
            logger.info(f"Ответ получен ({len(result)} символов)")
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка генерации: {e}")
            return f"Ошибка: {str(e)}"
    
    def generate_json(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        """
        Генерация JSON ответа (пытается распарсить JSON из ответа)
        """
        response = self.generate(prompt, system_prompt, max_tokens=1024)
        
        try:
            # Попытка извлечь JSON из ответа
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                logger.warning("JSON не найден в ответе, возвращаем как текст")
                return {"raw_response": response}
                
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            return {"error": "Failed to parse JSON", "raw_response": response}
    
    def chat(self, messages: list, max_tokens: int = 2048) -> str:
        """
        Поддержка многошагового диалога
        messages: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]
        """
        conversation = ""
        
        for msg in messages:
            if msg["role"] == "user":
                conversation += f"[INST] {msg['content']} [/INST]\n"
            elif msg["role"] == "assistant":
                conversation += f"{msg['content']}\n"
        
        return self.generate(conversation, max_tokens=max_tokens)


# Singleton instance
_llm_instance = None

def get_llm() -> LLMHandler:
    """Получить singleton инстанс LLM"""
    global _llm_instance
    if _llm_instance is None:
        from config import Config
        _llm_instance = LLMHandler(Config.HF_MODEL)
    return _llm_instance