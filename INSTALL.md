# Инструкция по установке и запуску

## Установка зависимостей

### Минимальные зависимости (обязательные)

```bash
py -m pip install Flask flask-cors python-dotenv requests beautifulsoup4 lxml --user
```

### Полная установка (все зависимости)

```bash
py -m pip install -r requirements.txt --user
```

## Запуск сервиса

### Способ 1: Использование скрипта проверки

```bash
py check_and_run.py
```

Скрипт автоматически проверит зависимости и запустит сервис.

### Способ 2: Прямой запуск

```bash
py app.py
```

Сервис будет доступен по адресу: http://127.0.0.1:8000

## Проверка работы

Откройте в браузере:
- http://127.0.0.1:8000 - главная страница
- http://127.0.0.1:8000/api/health - проверка здоровья API

## Решение проблем

### Проблема с прокси

Если возникают проблемы с установкой пакетов из-за прокси:

1. Отключите прокси в настройках pip:
   ```bash
   py -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org Flask flask-cors python-dotenv --user
   ```

2. Или используйте зеркало:
   ```bash
   py -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple Flask flask-cors python-dotenv --user
   ```

### Проблема с кодировкой

Если возникают проблемы с кодировкой в Windows консоли, установите переменную окружения:

```powershell
$env:PYTHONIOENCODING="utf-8"
py app.py
```

## Структура проекта

- `app.py` - основной файл Flask приложения
- `config.py` - конфигурация
- `scrapers/` - модули для парсинга данных
- `utils/` - утилиты (расчет размера выборки и т.д.)
- `rag/` - модули RAG (требуют transformers, langchain)
- `models/` - модели LLM (требуют transformers, torch)

## Примечания

- Некоторые функции требуют дополнительных зависимостей (RAG, LLM модели)
- PubMed scraper требует biopython для работы с API
- Генерация DOCX требует python-docx
