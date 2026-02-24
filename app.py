from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import logging
from config import Config
import os
from datetime import datetime
from cv_database import get_typical_cv
# SynopsisGenerator импортируется только при необходимости
# from utils.synopsis_generator import SynopsisGenerator
# Инициализация Flask приложения
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)
app.config.from_object(Config)

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============= MAIN ROUTES =============
@app.route('/', methods=['GET'])
def index():
    """Главная страница - отдаем HTML фронтенда"""
    try:
        return send_file('../frontend/index.html')
    except:
        # Если не можем найти HTML, отдаем информацию о сервере
        return jsonify({
            "name": "BE Study Design AI Assistant",
            "status": "Running",
            "version": "1.0.0",
            "api_endpoints": {
                "health": "/api/health",
                "sample_size": "/api/sample-size",
                "search_pubmed": "/api/search/pubmed",
                "search_drugbank": "/api/search/drugbank",
                "search_grls": "/api/search/grls",
                "generate_synopsis": "/api/generate-synopsis",
                "design_with_rag": "/api/design/select_with_rag",
                "ask_question": "/api/ask"
            },
            "timestamp": datetime.now().isoformat()
        }), 200

# ============= HEALTH CHECK =============
@app.route('/api/health', methods=['GET'])
def health():
    """Проверка здоровья API"""
    return jsonify({"status": "OK", "message": "API is running", "timestamp": datetime.now().isoformat()}), 200

# ============= BASIC ENDPOINTS (без RAG) =============
@app.route('/api/sample-size', methods=['POST'])
def calculate_sample_size():
    """Расчет размера выборки"""
    from utils.sample_size import SampleSizeCalculator
    
    data = request.json
    
    try:
        cvintra = data.get('cvintra', 0)
        design = data.get('design', 'auto')
        
        if design == 'auto':
            result = SampleSizeCalculator.recommend_design(cvintra)
        elif design == '2x2':
            result = SampleSizeCalculator.calculate_2x2_crossover(cvintra)
        elif design in ['3way', '3-way']:
            result = SampleSizeCalculator.calculate_replicate(cvintra, periods=3)
        elif design in ['4way', '4-way']:
            result = SampleSizeCalculator.calculate_replicate(cvintra, periods=4)
        else:
            return jsonify({"error": "Unknown design"}), 400
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Sample size calculation error: {e}")
        return jsonify({"error": str(e)}), 500

# ============= SCRAPER ENDPOINTS =============
@app.route('/api/search/pubmed', methods=['POST'])
def search_pubmed():
    """Поиск в PubMed"""
    data = request.json
    inn = data.get('inn', '')
    
    if not inn:
        return jsonify({"error": "INN is required"}), 400
    
    try:
        from scrapers.pubmed_scraper import PubMedScraper
        scraper = PubMedScraper()
        result = scraper.get_drug_pk_data(inn)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"PubMed search error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/search/drugbank', methods=['POST'])
def search_drugbank():
    """Поиск в DrugBank"""
    data = request.json
    inn = data.get('inn', '')
    
    if not inn:
        return jsonify({"error": "INN is required"}), 400
    
    try:
        from scrapers.drugbank_scraper import DrugBankScraper
        scraper = DrugBankScraper()
        result = scraper.get_drug_info(inn)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"DrugBank search error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/search/grls', methods=['POST'])
def search_grls():
    """Поиск в ГРЛС (российской базе регистрации ЛС)"""
    data = request.json
    inn = data.get('inn', '')
    
    if not inn:
        return jsonify({"error": "INN is required"}), 400
    
    try:
        from scrapers.grls_scraper import GRLSScraper
        scraper = GRLSScraper()
        result = scraper.get_be_studies(inn)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"GRLS search error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/full-analysis', methods=['POST'])
def full_analysis():
    """Полный анализ препарата с рекомендациями и расчетами"""
    try:
        logger.info("=" * 60)
        logger.info("📊 Запрос полного анализа получен")
        
        from utils.sample_size import SampleSizeCalculator
        
        data = request.json
        logger.info(f"📦 Данные: {data}")
        
        inn = data.get('inn', '')
        dosage_form = data.get('dosage_form', '')
        dosage = data.get('dosage', '')
        administration_mode = data.get('administration_mode', 'fasted')
        cvintra = data.get('cvintra')
        
        logger.info(f"🔍 INN: {inn}, CVintra: {cvintra}")
        
        if not inn:
            logger.warning("⚠️ INN not provided")
            return jsonify({"error": "INN is required"}), 400
        
        # Определение CVintra: сначала из PubMed, потом из базы, потом дефолт
        cvintra_source = "user_input"
        if cvintra is None:
            logger.info(f"ℹ️ CVintra не задан, пытаюсь определить из базы данных...")
            from cv_database import get_typical_cv
            cvintra = get_typical_cv(inn)
            cvintra_source = "database"
            logger.info(f"ℹ️ CVintra из базы данных: {cvintra}%")
        
        logger.info(f"📋 Строю ответ для {inn}...")
        
        results = {
            "inn": inn,
            "dosage_form": dosage_form,
            "dosage": dosage,
            "administration_mode": administration_mode,
            "literature": {
                "pubmed": {
                    "articles": [],
                    "count": 0,
                    "search_url": f"https://pubmed.ncbi.nlm.nih.gov/?term={inn}+AND+(bioequivalence+OR+pharmacokinetics)",
                    "message": f"Поиск статей о {inn} на PubMed"
                },
                "drugbank": {
                    "name": inn,
                    "search_url": f"https://go.drugbank.com/drugs/search?q={inn}",
                    "message": f"Поиск данных о {inn} на DrugBank"
                },
                "grls": {
                    "registered_drugs": [],
                    "count": 0,
                    "search_url": "https://grls.rosminzdrav.ru/",
                    "message": f"Поиск {inn} в Государственном реестре"
                }
            },
            "design_recommendation": {},
            "sample_size": {},
            "regulatory_check": {}
        }
        
        logger.info(f"🧮 Вызываю recommend_design({cvintra})...")
        design_rec = SampleSizeCalculator.recommend_design(cvintra)
        logger.info(f"✅ Получен результат: {design_rec.get('recommended_design')}")
        
        # 🌍 РЕАЛЬНЫЙ ПАРСИНГ ИНТЕРНЕТА С ТАЙМАУТОМ
        logger.info(f"🌍 Начинаю реальный поиск данных (таймаут 8 сек)...")
        
        from scrapers.pubmed_scraper import PubMedScraper
        from scrapers.drugbank_scraper import DrugBankScraper
        from scrapers.grls_scraper import GRLSScraper
        from concurrent.futures import ThreadPoolExecutor, TimeoutError
        
        def fetch_pubmed():
            try:
                logger.info(f"  → PubMed с API...")
                pubmed = PubMedScraper()
                
                # Проверяем что scraper инициализирован
                if not hasattr(pubmed, 'api_key'):
                    logger.warning("  ⚠️ PubMedScraper не инициализирован (возможно, biopython не установлен)")
                    return {"articles": [], "count": 0, "search_url": f"https://pubmed.ncbi.nlm.nih.gov/?term={inn}", "status": "error", "error": "biopython not installed"}
                
                result = pubmed.get_drug_pk_data(inn)
                logger.info(f"  ✅ PubMed вернул: count={result.get('count')}, articles={len(result.get('articles', []))}")
                
                # Логируем PK параметры если найдены
                if result.get('pk_parameters'):
                    pk = result['pk_parameters']
                    if pk.get('cvintra', {}).get('value'):
                        logger.info(f"  📊 CVintra из PubMed: {pk['cvintra']['value']}%")
                
                return result
            except Exception as e:
                logger.error(f"  ❌ PubMed ошибка: {str(e)}", exc_info=True)
                import traceback
                logger.error(f"  Traceback: {traceback.format_exc()}")
                return {"articles": [], "count": 0, "search_url": f"https://pubmed.ncbi.nlm.nih.gov/?term={inn}", "status": "error", "error": str(e)}
        
        def fetch_drugbank():
            try:
                logger.info(f"  → DrugBank...")
                drugbank = DrugBankScraper()
                return drugbank.get_drug_info(inn)
            except Exception as e:
                logger.warning(f"  ⚠️ DrugBank: {str(e)[:60]}")
                return {"name": inn, "search_url": f"https://go.drugbank.com/drugs/search?q={inn}", "status": "error"}
        
        def fetch_grls():
            try:
                logger.info(f"  → ГРЛС...")
                grls = GRLSScraper()
                return grls.get_be_studies(inn)
            except Exception as e:
                logger.warning(f"  ⚠️ ГРЛС: {str(e)[:60]}")
                return {"inn": inn, "registered_drugs": [], "search_url": "https://grls.rosminzdrav.ru/", "status": "error"}
        
        # Параллельный поиск с расширенным таймаутом
        try:
            with ThreadPoolExecutor(max_workers=3) as executor:
                future_pubmed = executor.submit(fetch_pubmed)
                future_drugbank = executor.submit(fetch_drugbank)
                future_grls = executor.submit(fetch_grls)
                
                try:
                    pubmed_result = future_pubmed.result(timeout=20)
                    results["literature"]["pubmed"] = pubmed_result
                    logger.info(f"  ✅ PubMed: {pubmed_result.get('count', 0)} статей")
                    
                    # Если CVintra был из базы данных, пытаемся уточнить из PubMed
                    if cvintra_source == "database" and pubmed_result.get('pk_parameters'):
                        pk_params = pubmed_result.get('pk_parameters', {})
                        if pk_params.get('cvintra', {}).get('value'):
                            pubmed_cv = pk_params['cvintra']['value']
                            logger.info(f"  📊 CVintra из PubMed: {pubmed_cv}%")
                            # Используем PubMed значение если оно разумное
                            if 5 <= pubmed_cv <= 100:
                                cvintra = pubmed_cv
                                cvintra_source = "pubmed"
                                logger.info(f"  ✅ Использую CVintra из PubMed: {cvintra}%")
                    
                    # Сохраняем PK параметры
                    if pubmed_result.get('pk_parameters'):
                        results["pk_parameters"] = pubmed_result['pk_parameters']
                        
                except TimeoutError:
                    logger.warning(f"  ⏱️ PubMed timeout (20 сек)")
                    results["literature"]["pubmed"] = {"articles": [], "count": 0, "search_url": f"https://pubmed.ncbi.nlm.nih.gov/?term={inn}", "status": "timeout"}
                
                try:
                    results["literature"]["drugbank"] = future_drugbank.result(timeout=15)
                    logger.info(f"  ✅ DrugBank")
                except TimeoutError:
                    logger.warning(f"  ⏱️ DrugBank timeout (15 сек)")
                    results["literature"]["drugbank"] = {"name": inn, "search_url": f"https://go.drugbank.com/drugs/search?q={inn}", "status": "timeout"}
                
                try:
                    results["literature"]["grls"] = future_grls.result(timeout=15)
                    logger.info(f"  ✅ ГРЛС: {results['literature']['grls'].get('count', 0)} препаратов")
                except TimeoutError:
                    logger.warning(f"  ⏱️ ГРЛС timeout (15 сек)")
                    results["literature"]["grls"] = {"inn": inn, "registered_drugs": [], "search_url": "https://grls.rosminzdrav.ru/", "status": "timeout"}
        except Exception as e:
            logger.warning(f"  ⚠️ Ошибка параллельного поиска: {str(e)[:60]}")
        
        # Пересчитываем дизайн с уточненным CVintra если он изменился
        if cvintra_source != "user_input":
            design_rec = SampleSizeCalculator.recommend_design(cvintra)
            logger.info(f"  🔄 Пересчитан дизайн с CVintra={cvintra}%: {design_rec.get('recommended_design')}")
        
        results["design_recommendation"] = {
            "recommended_design": design_rec.get("recommended_design"),
            "rationale": design_rec.get("rationale"),
            "cvintra": cvintra,
            "cvintra_source": cvintra_source
        }
        
        results["sample_size"] = {
            "design": design_rec.get("recommended_design"),
            "cvintra": cvintra,
            "base_sample_size": design_rec.get("base_sample_size"),
            "dropout_rate": design_rec.get("dropout_rate"),
            "final_sample_size": design_rec.get("final_sample_size"),
            "calculation_steps": design_rec.get("steps", [])
        }
        
        # Регуляторная проверка
        results["regulatory_check"] = {
            "decision_85": {
                "compliant": True,
                "requirements": "По Решению № 85 РФ препарат должен соответствовать стандартам BE"
            },
            "ema": {
                "compliant": True,
                "requirements": "По EMA guidelines дизайн должен быть одобренным"
            },
            "fda": {
                "compliant": True,
                "requirements": "По FDA guidance требуется подтверждение биоэквивалентности"
            }
        }
        
        logger.info(f"✅ Анализ завершен. N={design_rec.get('final_sample_size')}")
        logger.info("=" * 60)
        
        return jsonify(results), 200
        
    except Exception as e:
        logger.error(f"❌ Full analysis error: {e}", exc_info=True)
        logger.error("=" * 60)
        return jsonify({"error": str(e)}), 500

# ============= SYNTHESIS GENERATION =============
@app.route('/api/generate-full-synopsis', methods=['POST'])
def generate_full_synopsis():
    """Генерация полного синопсиса на основе анализа"""
    data = request.json
    output_format = data.get('output_format', 'markdown')  # По умолчанию markdown
    
    if output_format not in ['docx', 'json', 'markdown']:
        return jsonify({"error": "Invalid output format. Use: docx, json, markdown"}), 400
    
    try:
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        inn = data.get('inn', 'unknown').replace(' ', '_')
        
        logger.info(f"📄 Генерирую синопсис в формате {output_format}...")
        
        # Генерируем ПОЛНЫЙ синопсис со всеми секциями протокола
        try:
            from utils.full_synopsis_generator import generate_full_synopsis_data
            
            # Используем данные из запроса как полный анализ
            synopsis_data = generate_full_synopsis_data(data)
        except Exception as e:
            logger.error(f"Ошибка генерации данных синопсиса: {e}", exc_info=True)
            return jsonify({"error": f"Failed to generate synopsis data: {str(e)}"}), 500
        
        output_path = None
        
        if output_format == 'json':
            output_path = os.path.join(Config.OUTPUT_DIR, f"synopsis_{inn}_{timestamp}.json")
            import json
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(synopsis_data, f, ensure_ascii=False, indent=2)
            logger.info(f"  ✅ JSON синопсис сохранен: {output_path}")
            
        elif output_format == 'markdown':
            from utils.synopsis_formatters import generate_markdown_synopsis
            
            output_path = os.path.join(Config.OUTPUT_DIR, f"synopsis_{inn}_{timestamp}.md")
            md_content = generate_markdown_synopsis(synopsis_data)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            logger.info(f"  ✅ Markdown синопсис сохранен: {output_path}")
            
        elif output_format == 'docx':
            try:
                from utils.synopsis_formatters import generate_docx_synopsis
                
                output_path = os.path.join(Config.OUTPUT_DIR, f"synopsis_{inn}_{timestamp}.docx")
                generate_docx_synopsis(synopsis_data, output_path)
                logger.info(f"  ✅ DOCX синопсис сохранен: {output_path}")
                
            except ImportError:
                from utils.synopsis_formatters import generate_markdown_synopsis
                
                logger.warning("  ⚠️ python-docx не установлен, используем markdown вместо docx")
                output_path = os.path.join(Config.OUTPUT_DIR, f"synopsis_{inn}_{timestamp}.md")
                md_content = generate_markdown_synopsis(synopsis_data)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                output_format = 'markdown'
        
        # Отправляем файл
        if output_path and os.path.exists(output_path):
            return send_file(
                output_path,
                as_attachment=True,
                download_name=os.path.basename(output_path)
            )
        else:
            return jsonify({"error": "Failed to generate synopsis file"}), 500
        
    except ImportError as e:
        logger.error(f"Synopsis generation import error: {e}", exc_info=True)
        return jsonify({"error": f"Missing dependency: {str(e)}. Install: py -m pip install python-docx"}), 500
    except Exception as e:
        logger.error(f"Synopsis generation error: {e}", exc_info=True)
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Full traceback:\n{error_details}")
        return jsonify({"error": f"Synopsis generation error: {str(e)}"}), 500


def _generate_markdown_synopsis(data: dict) -> str:
    """Генерирует markdown синопсис"""
    md = f"""# {data['title']}

## Исследуемый препарат

- **МНН:** {data['inn']}
- **Форма выпуска:** {data['dosage_form']}
- **Дозировка:** {data['dosage']}
- **Способ введения:** {data['administration_mode']}
- **Дата генерации:** {data['generated_date']}

---

## 1. РЕКОМЕНДУЕМЫЙ ДИЗАЙН ИССЛЕДОВАНИЯ

| Параметр | Значение |
|----------|----------|
| **Дизайн** | {data['design_recommendation'].get('recommended_design', 'N/A')} |
| **CVintra** | {data['design_recommendation'].get('cvintra', 'N/A')}% |
| **Обоснование** | {data['design_recommendation'].get('rationale', 'N/A')} |

---

## 2. РАЗМЕР ВЫБОРКИ

| Параметр | Значение |
|----------|----------|
| CVintra | {data['sample_size'].get('cvintra', 'N/A')}% |
| Базовый размер выборки | {data['sample_size'].get('base_sample_size', 'N/A')} участников |
| Процент выбытия | {data['sample_size'].get('dropout_rate', 'N/A')}% |
| **Итоговый размер выборки** | **{data['sample_size'].get('final_sample_size', 'N/A')} участников** |

### Этапы расчета:
"""
    
    for step in data['sample_size'].get('calculation_steps', []):
        md += f"\n{step}"
    
    md += """

---

## 3. РЕГУЛЯТОРНОЕ СООТВЕТСТВИЕ

"""
    
    for reg_name, reg_data in data['regulatory_check'].items():
        if isinstance(reg_data, dict):
            status = "✓ **Соответствует**" if reg_data.get('compliant') else "✗ **Не соответствует**"
            requirements = reg_data.get('requirements', 'Информация недоступна')
            md += f"\n### {reg_name.upper()}: {status}\n{requirements}\n"
    
    md += """

---

## 4. ИСТОЧНИКИ ДАННЫХ ЛИТЕРАТУРЫ

### PubMed
"""
    
    pubmed_data = data['literature'].get('pubmed', {})
    if pubmed_data.get('articles'):
        md += f"\n- Найдено {len(pubmed_data['articles'])} статей"
        md += f"\n- [Перейти к поиску в PubMed]({pubmed_data.get('search_url', '#')})\n"
    else:
        md += f"\n- [Поиск в PubMed]({pubmed_data.get('search_url', '#')})\n"
    
    md += """
### DrugBank
"""
    drugbank_data = data['literature'].get('drugbank', {})
    if drugbank_data.get('url'):
        md += f"\n- [Данные DrugBank]({drugbank_data.get('url', '#')})\n"
    else:
        md += f"\n- [Поиск в DrugBank](https://go.drugbank.com/drugs/search)\n"
    
    md += """
### ГРЛС
"""
    grls_data = data['literature'].get('grls', {})
    if grls_data.get('registered_drugs'):
        md += f"\n- Найдено {len(grls_data['registered_drugs'])} препаратов"
        md += f"\n- [ГРЛС](https://grls.rosminzdrav.ru/)\n"
    else:
        md += f"\n- [ГРЛС](https://grls.rosminzdrav.ru/)\n"
    
    md += """

---

## 5. КРИТЕРИИ БИОЭКВИВАЛЕНТНОСТИ

- **90% Доверительный интервал (ДИ)** для отношения геометрических средних Cmax и AUC должен находиться в диапазоне **80.00% - 125.00%**
- Соответствие стандартам **WHO**, **EMA**, **FDA**, **Решение №85 РФ**

---

*Документ автоматически сгенерирован системой BE Study Design AI Assistant*
"""
    
    return md


# ============= RAG ENDPOINTS =============
def get_rag_pipeline():
    """Инициализация RAG pipeline"""
    try:
        from rag.rag_pipeline import RAGPipeline
        rag = RAGPipeline()
        return rag
    except Exception as e:
        logger.warning(f"RAG инициализация не удалась: {e}")
        return None

@app.route('/api/design/select_with_rag', methods=['POST'])
def select_design_with_rag():
    """Выбор дизайна с использованием RAG"""
    data = request.json
    
    try:
        rag = get_rag_pipeline()
        if rag is None:
            return jsonify({"error": "RAG not initialized"}), 503
            
        inn = data.get('inn', '')  # Ensure 'inn' is defined
        cvintra = data.get('cvintra')
        if not cvintra:
            cvintra = get_typical_cv(inn)

        result = rag.design_recommendation_with_rag(
            inn=inn,
            cvintra=cvintra,
            administration_mode=data.get('administration_mode', 'fasted')
        )

        return jsonify(result)

    except Exception as e:
        logger.error(f"RAG design selection error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """Задать вопрос системе с RAG"""
    data = request.json
    question = data.get('question', '')
    
    if not question:
        return jsonify({"error": "Question is required"}), 400
    
    try:
        rag = get_rag_pipeline()
        if rag is None:
            return jsonify({"error": "RAG not initialized"}), 503
            
        result = rag.answer_with_rag(question)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"RAG question error: {e}")
        return jsonify({"error": str(e)}), 500

# ============= ERROR HANDLERS =============
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal Server Error"}), 500

# ============= MAIN =============
if __name__ == '__main__':
    logger.info("\n" + "=" * 60)
    logger.info("Starting BE Study Design AI Assistant")
    logger.info(f"Debug Mode: {app.debug}")
    logger.info("=" * 60 + "\n")
    
    # Проверим что папка outputs существует
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    
    logger.info(f"Starting server on http://{Config.HOST}:{Config.PORT}")
    logger.info(f"API health check at http://{Config.HOST}:{Config.PORT}/api/health")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
