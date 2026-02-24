#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapers.pubmed_scraper import PubMedScraper
import json

print('\n' + '='*70)
print('🔍 ТЕСТ PUBMED SCRAPER - ОТЛАДКА')
print('='*70 + '\n')

scraper = PubMedScraper()

# Тест 1: search_drug
print('1️⃣ Поиск по МНН (search_drug):')
pmids = scraper.search_drug('aspirin')
if pmids:
    print(f'   ✅ Найдено PMID ({len(pmids)}): {pmids[:3]}')
else:
    print(f'   ❌ PMID НЕ НАЙДЕНЫ!')

# Тест 2: fetch_article_details
if pmids:
    print(f'\n2️⃣ Получение деталей статьи PMID={pmids[0]}:')
    article = scraper.fetch_article_details(pmids[0])
    if article:
        print(f'   ✅ Статья получена:')
        print(f'      Название: {article.get("title", "N/A")[:80]}')
        print(f'      Авторы: {article.get("authors", [])}')
        print(f'      Год: {article.get("year", "N/A")}')
    else:
        print(f'   ❌ Не удалось получить статью')

# Тест 3: get_drug_pk_data (главный метод)
print(f'\n3️⃣ Полный поиск (get_drug_pk_data):')
result = scraper.get_drug_pk_data('aspirin')
print(f'   Статус: {result.get("status")}')
print(f'   Статей найдено: {result.get("count", 0)}')
print(f'   Обработано статей: {result.get("articles_processed", 0)}')
print(f'   Всего статей в поиске: {result.get("total_articles_found", 0)}')

if result.get('articles'):
    print(f'\n   📄 Статьи:')
    for i, art in enumerate(result['articles'][:3], 1):
        print(f'      {i}. {art.get("title", "N/A")[:70]}')
        print(f'         PMID: {art.get("pmid")} | Год: {art.get("year", "N/A")}')
else:
    print(f'   ❌ Статьи не получены!')

if result.get('pk_parameters'):
    print(f'\n   📈 Найденные PK параметры: {list(result["pk_parameters"].keys())}')

print('\n' + '='*70 + '\n')
