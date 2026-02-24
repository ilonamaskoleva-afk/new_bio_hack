#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapers.pubmed_scraper import PubMedScraper
from scrapers.grls_scraper import GRLSScraper
from scrapers.drugbank_scraper import DrugBankScraper
import json

print("\n" + "=" * 60)
print("🧪 ТЕСТ СКРЕПЕРОВ")
print("=" * 60 + "\n")

# Тест 1: PubMed
print("1️⃣  PUBMED SCRAPER")
print("-" * 60)
try:
    pubmed = PubMedScraper()
    result = pubmed.get_drug_pk_data('aspirin')
    print(f"✅ Статус: {result.get('status', 'N/A')}")
    print(f"📊 Найдено статей: {result.get('count', 0)}")
    if result.get('articles'):
        print(f"📄 Первая статья: {result['articles'][0].get('title', '')[:80]}...")
    if result.get('pk_parameters'):
        print(f"📈 Найденные параметры: {list(result['pk_parameters'].keys())}")
except Exception as e:
    print(f"❌ Ошибка: {str(e)[:100]}")

print("\n2️⃣  GRLS SCRAPER")
print("-" * 60)
try:
    grls = GRLSScraper()
    result = grls.get_be_studies('aspirin')
    print(f"✅ Статус: {result.get('status', 'N/A')}")
    print(f"📊 Найдено препаратов: {result.get('count', 0)}")
    print(f"🔗 URL: {result.get('search_url', 'N/A')}")
except Exception as e:
    print(f"❌ Ошибка: {str(e)[:100]}")

print("\n3️⃣  DRUGBANK SCRAPER")
print("-" * 60)
try:
    drugbank = DrugBankScraper()
    result = drugbank.get_drug_info('aspirin')
    print(f"✅ Статус: {result.get('status', 'N/A')}")
    print(f"🔗 URL: {result.get('search_url', 'N/A')}")
except Exception as e:
    print(f"❌ Ошибка: {str(e)[:100]}")

print("\n" + "=" * 60)
print("✅ ТЕСТ ЗАВЕРШЕН")
print("=" * 60 + "\n")
