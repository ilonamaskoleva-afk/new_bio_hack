import requests
from bs4 import BeautifulSoup
import time
import logging
import os

try:
    from Bio import Entrez
    BIO_AVAILABLE = True
except ImportError:
    BIO_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Bio.Entrez не доступен. Установите biopython для работы с PubMed API.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PubMedScraper:
    def __init__(self, email: str = None, api_key: str = None):
        """
        Инициализация PubMed scraper
        
        Args:
            email: Email для Entrez API (требование NCBI). Если не указан, берется из конфига
            api_key: API ключ для Entrez API (увеличивает лимит запросов). Если не указан, берется из конфига
        """
        if not BIO_AVAILABLE:
            logger.warning("Bio.Entrez не доступен. Установите biopython для работы с PubMed API.")
            return
        
        # Загружаем конфиг если доступен
        try:
            from config import Config
            self.email = email or Config.NCBI_EMAIL
            self.api_key = api_key or Config.NCBI_API_KEY
        except ImportError:
            # Если конфиг недоступен, используем значения по умолчанию
            self.email = email or os.getenv("NCBI_EMAIL", "your.email@example.com")
            self.api_key = api_key or os.getenv("NCBI_API_KEY", "")
        
        # Устанавливаем email и API ключ для Entrez
        Entrez.email = self.email
        if self.api_key:
            Entrez.api_key = self.api_key
            logger.info(f"✅ PubMed API ключ установлен: {self.api_key[:10]}...")
        else:
            logger.warning("⚠️ PubMed API ключ не установлен. Лимит запросов: 3 запроса/сек")
        
        self.base_url = "https://pubmed.ncbi.nlm.nih.gov"
    
    def search_drug(self, inn: str, keywords: list = None) -> list:
        """
        Поиск статей о препарате в PubMed
        
        Args:
            inn: International Nonproprietary Name препарата
            keywords: дополнительные ключевые слова (pharmacokinetics, bioequivalence, etc.)
        
        Returns:
            list: список PMID статей
        """
        if keywords is None:
            keywords = ["pharmacokinetics", "bioequivalence", "Cmax", "AUC"]
        
        query = f"{inn} AND ({' OR '.join(keywords)})"
        
        if not BIO_AVAILABLE:
            logger.warning("Bio.Entrez не доступен. Установите biopython для работы с PubMed API.")
            return []
        
        try:
            logger.info(f"Поиск в PubMed: {query}")
            
            # Используем API ключ если доступен (увеличивает лимит запросов)
            search_params = {
                "db": "pubmed",
                "term": query,
                "retmax": 20,  # максимум 20 статей
                "sort": "relevance",
                "usehistory": "y"  # Используем history для более эффективных запросов
            }
            
            handle = Entrez.esearch(**search_params)
            record = Entrez.read(handle)
            handle.close()
            
            pmids = record["IdList"]
            total_found = record.get("Count", len(pmids))
            logger.info(f"Найдено {len(pmids)} статей (всего найдено: {total_found})")
            
            return pmids
            
        except Exception as e:
            logger.error(f"Ошибка поиска в PubMed: {e}")
            return []
    
    def fetch_article_details(self, pmid: str) -> dict:
        """
        Получить детали статьи по PMID
        """
        if not BIO_AVAILABLE:
            return {}
        
        try:
            handle = Entrez.efetch(
                db="pubmed",
                id=pmid,
                rettype="abstract",
                retmode="xml"
            )
            
            record = Entrez.read(handle)
            handle.close()
            
            article = record['PubmedArticle'][0]
            medline = article['MedlineCitation']
            
            title = medline['Article']['ArticleTitle']
            abstract = ""
            
            if 'Abstract' in medline['Article']:
                abstract_texts = medline['Article']['Abstract']['AbstractText']
                abstract = ' '.join([str(text) for text in abstract_texts])
            
            authors = []
            if 'AuthorList' in medline['Article']:
                for author in medline['Article']['AuthorList']:
                    if 'LastName' in author and 'Initials' in author:
                        authors.append(f"{author['LastName']} {author['Initials']}")
            
            year = ""
            if 'PubDate' in medline['Article']['Journal']['JournalIssue']:
                pub_date = medline['Article']['Journal']['JournalIssue']['PubDate']
                year = pub_date.get('Year', '')
            
            return {
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "year": year,
                "url": f"{self.base_url}/{pmid}"
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения статьи {pmid}: {e}")
            return {}
    
    def extract_pk_parameters(self, articles: list) -> dict:
        """
        Извлечение PK параметров из абстрактов статей
        Использует regex для базового извлечения
        """
        import re
        
        pk_data = {
            "cmax": {"value": None, "unit": "ng/mL", "sources": []},
            "auc": {"value": None, "unit": "ng·h/mL", "sources": []},
            "tmax": {"value": None, "unit": "h", "sources": []},
            "t_half": {"value": None, "unit": "h", "sources": []},
            "cvintra": {"value": None, "unit": "%", "sources": []}
        }
        
        cvintra_values = []
        
        for article in articles:
            abstract = article.get("abstract", "").lower()
            title = article.get("title", "").lower()
            full_text = f"{title} {abstract}"
            
            # Извлечение CVintra (внутрисубъектная вариабельность)
            # Улучшенные паттерны для более точного извлечения
            cv_patterns = [
                r'cv\s*intra[-\s]?subject[:\s]+(\d+\.?\d*)\s*%',
                r'intra[-\s]?subject\s+cv[:\s]+(\d+\.?\d*)\s*%',
                r'cv\s*intra[:\s]+(\d+\.?\d*)\s*%',
                r'intra[-\s]?individual\s+cv[:\s]+(\d+\.?\d*)\s*%',
                r'within[-\s]?subject\s+cv[:\s]+(\d+\.?\d*)\s*%',
                r'cv\s*intra[-\s]?subject\s*[=:]\s*(\d+\.?\d*)\s*%',
                r'intra[-\s]?subject\s+coefficient\s+of\s+variation[:\s]+(\d+\.?\d*)\s*%',
                r'cv\s*intra[:\s]*(\d+\.?\d*)\s*%',
                r'cv\s*intra[-\s]?subject[:\s]*(\d+\.?\d*)',  # без % в конце
                r'intra[-\s]?subject\s+cv[:\s]*(\d+\.?\d*)',  # без % в конце
            ]
            
            for pattern in cv_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    try:
                        cv_value = float(match.group(1))
                        if 5 <= cv_value <= 100:  # Разумный диапазон
                            cvintra_values.append(cv_value)
                            pk_data["cvintra"]["sources"].append(article["url"])
                            break
                    except ValueError:
                        continue
            
            # Извлечение Cmax
            cmax_patterns = [
                r'cmax[:\s]*(\d+\.?\d*)\s*(ng/ml|mg/l|μg/ml|mcg/ml|ng·ml[-1]|mg·l[-1])',
                r'maximum\s+concentration[:\s]*(\d+\.?\d*)\s*(ng/ml|mg/l|μg/ml|mcg/ml|ng·ml[-1]|mg·l[-1])',
                r'c\s*max[:\s]*(\d+\.?\d*)\s*(ng/ml|mg/l|μg/ml|mcg/ml)',
                r'peak\s+concentration[:\s]*(\d+\.?\d*)\s*(ng/ml|mg/l|μg/ml|mcg/ml)',
            ]
            for pattern in cmax_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match and not pk_data["cmax"]["value"]:
                    try:
                        pk_data["cmax"]["value"] = float(match.group(1))
                        pk_data["cmax"]["unit"] = match.group(2)
                        pk_data["cmax"]["sources"].append(article["url"])
                        break
                    except (ValueError, IndexError):
                        continue
            
            # Извлечение AUC
            auc_patterns = [
                r'auc[:\s]*(\d+\.?\d*)\s*(ng·h/ml|ng\s*h/ml|mg·h/l|μg·h/ml|mcg·h/ml|ng·h·ml[-1]|mg·h·l[-1])',
                r'area\s+under\s+curve[:\s]*(\d+\.?\d*)\s*(ng·h/ml|ng\s*h/ml|mg·h/l|μg·h/ml|mcg·h/ml)',
                r'auc0[-\s]?t[:\s]*(\d+\.?\d*)\s*(ng·h/ml|ng\s*h/ml|mg·h/l)',
                r'auc0[-\s]?∞[:\s]*(\d+\.?\d*)\s*(ng·h/ml|ng\s*h/ml|mg·h/l)',
                r'auc\s*\(0[-\s]?t\)[:\s]*(\d+\.?\d*)\s*(ng·h/ml|ng\s*h/ml)',
            ]
            for pattern in auc_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match and not pk_data["auc"]["value"]:
                    try:
                        pk_data["auc"]["value"] = float(match.group(1))
                        pk_data["auc"]["unit"] = match.group(2)
                        pk_data["auc"]["sources"].append(article["url"])
                        break
                    except (ValueError, IndexError):
                        continue
            
            # Извлечение Tmax
            tmax_patterns = [
                r'tmax[:\s]*(\d+\.?\d*)\s*(h|hours|hr|hour)',
                r'time\s+to\s+cmax[:\s]*(\d+\.?\d*)\s*(h|hours|hr|hour)',
                r'time\s+to\s+maximum\s+concentration[:\s]*(\d+\.?\d*)\s*(h|hours|hr)',
                r't\s*max[:\s]*(\d+\.?\d*)\s*(h|hours|hr)',
            ]
            for pattern in tmax_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match and not pk_data["tmax"]["value"]:
                    try:
                        pk_data["tmax"]["value"] = float(match.group(1))
                        pk_data["tmax"]["sources"].append(article["url"])
                        break
                    except (ValueError, IndexError):
                        continue
            
            # Извлечение T1/2
            t_half_patterns = [
                r't1/2[:\s]*(\d+\.?\d*)\s*(h|hours|hr|hour)',
                r't\s*1/2[:\s]*(\d+\.?\d*)\s*(h|hours|hr)',
                r'hal[fv][-\s]?life[:\s]*(\d+\.?\d*)\s*(h|hours|hr|hour)',
                r'elimination\s+half[-\s]?life[:\s]*(\d+\.?\d*)\s*(h|hours|hr)',
                r'terminal\s+half[-\s]?life[:\s]*(\d+\.?\d*)\s*(h|hours|hr)',
                r'apparent\s+half[-\s]?life[:\s]*(\d+\.?\d*)\s*(h|hours|hr)',
            ]
            for pattern in t_half_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match and not pk_data["t_half"]["value"]:
                    try:
                        pk_data["t_half"]["value"] = float(match.group(1))
                        pk_data["t_half"]["sources"].append(article["url"])
                        break
                    except (ValueError, IndexError):
                        continue
        
        # Вычисляем среднее CVintra если найдено несколько значений
        if cvintra_values:
            pk_data["cvintra"]["value"] = round(sum(cvintra_values) / len(cvintra_values), 2)
            logger.info(f"📊 Извлечено {len(cvintra_values)} значений CVintra, среднее: {pk_data['cvintra']['value']}%")
        
        return pk_data
    
    def get_drug_pk_data(self, inn: str) -> dict:
        """
        Полный цикл: поиск + извлечение PK параметров
        """
        if not BIO_AVAILABLE:
            logger.warning("Bio.Entrez не доступен. Установите biopython для работы с PubMed API.")
            return {
                "articles": [],
                "count": 0,
                "search_url": f"https://pubmed.ncbi.nlm.nih.gov/?term={inn}+AND+(bioequivalence+OR+pharmacokinetics)",
                "message": f"Поиск статей о {inn} на PubMed (biopython не установлен)",
                "pk_parameters": {},
                "status": "error",
                "error": "biopython not installed"
            }
        
        try:
            pmids = self.search_drug(inn)
            
            if not pmids:
                logger.info(f"Статьи не найдены для {inn}")
                return {
                    "articles": [],
                    "count": 0,
                    "search_url": f"https://pubmed.ncbi.nlm.nih.gov/?term={inn}+AND+(bioequivalence+OR+pharmacokinetics)",
                    "message": f"Статьи о {inn} не найдены на PubMed",
                    "pk_parameters": {}
                }
            
            articles = []
            # С API ключом можно делать больше запросов (10 req/sec вместо 3 req/sec)
            delay = 0.1 if self.api_key else 0.5
            
            logger.info(f"Загружаю детали {min(len(pmids), 10)} статей...")
            for i, pmid in enumerate(pmids[:10], 1):  # Берем топ 10
                try:
                    article = self.fetch_article_details(pmid)
                    if article:
                        articles.append(article)
                        logger.debug(f"  [{i}/{min(len(pmids), 10)}] Загружена статья {pmid}")
                    else:
                        logger.warning(f"  [{i}/{min(len(pmids), 10)}] Не удалось загрузить статью {pmid}")
                except Exception as e:
                    logger.warning(f"  [{i}/{min(len(pmids), 10)}] Ошибка загрузки статьи {pmid}: {str(e)[:50]}")
                
                if i < min(len(pmids), 10):  # Не ждем после последней статьи
                    time.sleep(delay)  # Rate limiting
            
            logger.info(f"Загружено {len(articles)} статей из {len(pmids)} найденных")
            
            # Извлекаем PK параметры
            pk_data = self.extract_pk_parameters(articles)
            
            return {
                "articles": articles,
                "count": len(articles),
                "search_url": f"https://pubmed.ncbi.nlm.nih.gov/?term={inn}+AND+(bioequivalence+OR+pharmacokinetics)",
                "message": f"Найдено {len(articles)} статей о {inn}",
                "pk_parameters": pk_data
            }
            
        except Exception as e:
            logger.error(f"Ошибка в get_drug_pk_data для {inn}: {e}", exc_info=True)
            return {
                "articles": [],
                "count": 0,
                "search_url": f"https://pubmed.ncbi.nlm.nih.gov/?term={inn}+AND+(bioequivalence+OR+pharmacokinetics)",
                "message": f"Ошибка поиска статей о {inn}",
                "pk_parameters": {},
                "status": "error",
                "error": str(e)
            }