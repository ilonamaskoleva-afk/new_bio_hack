# BE Study Design AI Assistant

Веб-приложение для поддержки проектирования исследований биоэквивалентности (BE):
- фронтенд-форма для ввода параметров исследования;
- backend на Flask с расчетами и поисковыми API;
- утилиты для расчета размера выборки, поиска литературы и генерации синопсиса.

## Возможности

- Рекомендация дизайна исследования на основе `CVintra`.
- Расчет размера выборки для типовых crossover/replicate дизайнов.
- Поиск данных по препарату через PubMed, DrugBank и ГРЛС.
- Endpoint для проверки состояния сервиса.
- Веб-интерфейс отдается напрямую через Flask (`index.html` + `css/` + `js/`).

## Технологический стек

- Python 3.9+
- Flask + Flask-CORS
- Requests, BeautifulSoup, lxml
- Дополнительные модули: BioPython, python-docx, transformers, langchain, FAISS

## Структура проекта

```text
new_bio_hack/
├── app.py                 # Точка входа Flask-приложения
├── config.py              # Конфигурация приложения
├── index.html             # Страница фронтенда
├── css/style.css          # Стили фронтенда
├── js/app.js              # Логика фронтенда
├── scrapers/              # Модули для парсинга данных
├── utils/                 # Калькуляторы и вспомогательные утилиты
├── rag/                   # Модули RAG (опциональный стек)
├── models/                # Модельный слой (опциональный стек)
└── requirements.txt       # Полный список зависимостей
```

## Быстрый старт

### 1) Клонирование и вход в проект

```bash
git clone https://github.com/ilonamaskoleva-afk/new_bio_hack.git
cd new_bio_hack
```

### 2) Создание виртуального окружения (рекомендуется)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Для Windows PowerShell:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3) Установка зависимостей

Минимальный набор:
```bash
pip install Flask flask-cors python-dotenv requests beautifulsoup4 lxml biopython python-docx
```

Полная установка:
```bash
pip install -r requirements.txt
```

### 4) Запуск приложения

```bash
python app.py
```

Адреса сервиса:
- Приложение: `http://127.0.0.1:8000`
- Health-check: `http://127.0.0.1:8000/api/health`

## Основные API endpoint'ы

- `GET /api/health` — проверка состояния сервиса.
- `POST /api/sample-size` — расчет размера выборки и/или дизайна.
- `POST /api/search/pubmed` — поиск данных в PubMed по INN.
- `POST /api/search/drugbank` — получение данных из DrugBank.
- `POST /api/search/grls` — получение данных из ГРЛС.
- `POST /api/full-analysis` — агрегированный анализ.
- `POST /api/generate-synopsis` — генерация синопсиса протокола (если включено).
- `POST /api/design/select_with_rag` — подбор дизайна с RAG (если включено).
- `POST /api/ask` — QA endpoint (если включен в окружении).

## Конфигурация

Настройки загружаются из `config.py` и переменных окружения (`.env`, если есть).

Типовые переменные:
- `PORT` (по умолчанию: 8000)
- внешние API-ключи (для подключенных провайдеров)

Не коммитьте секреты. Файл `.env` должен оставаться локальным.

## Примечания

- Для части расширенных возможностей нужны тяжелые ML/RAG зависимости из `requirements.txt`.
- Если нужен только веб-интерфейс и базовые endpoint'ы, достаточно минимального набора зависимостей.
- Дополнительная документация: `INSTALL.md`, `START.md`, `PUBMED_API_SETUP.md`.
