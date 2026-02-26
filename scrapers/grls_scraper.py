import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GRLSScraper:
    def __init__(self):
        self.base_url = "https://grls.rosminzdrav.ru"
        self.search_url = f"{self.base_url}/Grls_View_v2.aspx"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def search_drug(self, inn: str) -> list:
        """
        Поиск препарата в ГРЛС
        """
        params = {
            "searchKey": inn,
            "t": ""
        }
        
        try:
            logger.info(f"Поиск в ГРЛС: {inn}")
            response = requests.get(
                self.search_url,
                params=params,
                headers=self.headers,
                timeout=15
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Парсинг результатов поиска
            results = []
            
            # Поиск таблицы с результатами
            table = soup.find('table', class_='grid')
            
            if table:
                rows = table.find_all('tr')[1:]  # Пропускаем заголовок
                
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        drug_name = cols[0].get_text(strip=True)
                        dosage_form = cols[1].get_text(strip=True)
                        manufacturer = cols[2].get_text(strip=True)
                        
                        results.append({
                            "name": drug_name,
                            "dosage_form": dosage_form,
                            "manufacturer": manufacturer
                        })
            
            logger.info(f"Найдено {len(results)} препаратов в ГРЛС")
            return results
            
        except Exception as e:
            logger.error(f"Ошибка поиска в ГРЛС: {e}")
            return []
    
    def get_be_studies(self, inn: str) -> dict:
        """
        Попытка найти информацию о ранее проведенных BE исследованиях
        """
        drugs = self.search_drug(inn)
        
        return {
            "inn": inn,
            "registered_drugs": drugs,
            "count": len(drugs),
            "search_url": "https://grls.rosminzdrav.ru/",
            "message": f"Найдено {len(drugs)} препаратов в ГРЛС для {inn}",
            "be_studies": []  # В ГРЛС обычно нет публичных данных BE исследований
        }