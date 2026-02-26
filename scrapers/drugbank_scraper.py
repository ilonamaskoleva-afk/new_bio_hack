import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DrugBankScraper:
    def __init__(self):
        self.base_url = "https://go.drugbank.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def search_drug(self, inn: str) -> str:
        """
        Поиск препарата в DrugBank и получение URL
        """
        search_url = f"{self.base_url}/search?q={inn}&type=drugs"
        
        try:
            logger.info(f"Поиск в DrugBank: {inn}")
            response = requests.get(search_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Найти первую ссылку на препарат
            drug_link = soup.find('a', class_='search-result-title')
            
            if drug_link:
                drug_url = self.base_url + drug_link['href']
                logger.info(f"Найден препарат: {drug_url}")
                return drug_url
            else:
                logger.warning("Препарат не найден в DrugBank")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка поиска в DrugBank: {e}")
            return None
    
    def get_drug_info(self, inn: str) -> dict:
        """
        Получить информацию о препарате
        """
        drug_url = self.search_drug(inn)
        
        if not drug_url:
            return {
                "name": inn,
                "search_url": f"https://go.drugbank.com/drugs/search?q={inn}",
                "message": f"Поиск данных о {inn} на DrugBank",
                "status": "not_found"
            }
        
        try:
            response = requests.get(drug_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Извлечение данных (структура может измениться)
            drug_info = {
                "name": inn,
                "url": drug_url,
                "search_url": f"https://go.drugbank.com/drugs/search?q={inn}",
                "message": f"Данные о {inn} найдены на DrugBank",
                "description": "",
                "pharmacokinetics": "",
                "half_life": "",
                "absorption": ""
            }
            
            # Попытка найти секцию Pharmacology
            pk_section = soup.find('section', id='pharmacology')
            if pk_section:
                drug_info["pharmacokinetics"] = pk_section.get_text(strip=True)
            
            # Half-life
            half_life_dt = soup.find('dt', string='Half Life')
            if half_life_dt:
                half_life_dd = half_life_dt.find_next('dd')
                drug_info["half_life"] = half_life_dd.get_text(strip=True)
            
            logger.info(f"Информация о {inn} получена")
            return drug_info
            
        except Exception as e:
            logger.error(f"Ошибка получения информации: {e}")
            return {
                "name": inn,
                "search_url": f"https://go.drugbank.com/drugs/search?q={inn}",
                "message": f"Ошибка при получении данных о {inn}",
                "status": "error",
                "error": str(e)
            }