#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тест PubMed API с проверкой парсинга и API ключа
"""
import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from scrapers.pubmed_scraper import PubMedScraper
import json

def test_pubmed_api():
    """Тест PubMed API с разными препаратами"""
    
    print("=" * 70)
    print("ТЕСТ PubMed API И ПАРСИНГА")
    print("=" * 70)
    
    # Проверка API ключа
    print(f"\n📋 Конфигурация:")
    print(f"   API Key: {Config.NCBI_API_KEY[:10]}..." if Config.NCBI_API_KEY else "   API Key: ❌ НЕ УСТАНОВЛЕН")
    print(f"   Email: {Config.NCBI_EMAIL}")
    
    # Тестовые препараты
    test_drugs = [
        ("aspirin", "Ожидается: CVintra ~15%, 2×2 дизайн"),
        ("ibuprofen", "Ожидается: CVintra ~20%, 2×2 дизайн"),
        ("metformin", "Ожидается: CVintra ~35%, 3-way дизайн"),
        ("propranolol", "Ожидается: CVintra ~55%, 4-way дизайн"),
    ]
    
    scraper = PubMedScraper()
    
    if not scraper.api_key:
        print("\n⚠️  ВНИМАНИЕ: API ключ не установлен!")
        print("   Лимит запросов: 3 запроса/сек (без ключа)")
        print("   С ключом: 10 запросов/сек")
    else:
        print(f"\n✅ API ключ установлен: {scraper.api_key[:10]}...")
        print("   Лимит запросов: 10 запросов/сек")
    
    print("\n" + "=" * 70)
    
    for inn, expected in test_drugs:
        print(f"\n🔍 Тестирую препарат: {inn}")
        print(f"   {expected}")
        print("-" * 70)
        
        try:
            result = scraper.get_drug_pk_data(inn)
            
            # Статистика
            print(f"   📊 Найдено статей: {result.get('count', 0)}")
            
            articles = result.get('articles', [])
            if articles:
                print(f"   📄 Примеры статей:")
                for i, article in enumerate(articles[:3], 1):
                    title = article.get('title', 'No title')[:60]
                    year = article.get('year', 'N/A')
                    authors = ', '.join(article.get('authors', [])[:2]) if article.get('authors') else 'N/A'
                    print(f"      {i}. {title}... ({year}) - {authors}")
            
            # PK параметры
            pk_params = result.get('pk_parameters', {})
            print(f"\n   📈 Извлеченные PK параметры:")
            
            if pk_params.get('cvintra', {}).get('value'):
                cv = pk_params['cvintra']['value']
                print(f"      ✅ CVintra: {cv}%")
                if cv <= 30:
                    design = "2×2 Cross-over"
                elif cv <= 50:
                    design = "3-way Replicate"
                else:
                    design = "4-way Replicate (RSABE)"
                print(f"      ✅ Рекомендуемый дизайн: {design}")
            else:
                print(f"      ⚠️  CVintra: не найден в статьях")
            
            if pk_params.get('cmax', {}).get('value'):
                print(f"      ✅ Cmax: {pk_params['cmax']['value']} {pk_params['cmax'].get('unit', 'N/A')}")
            else:
                print(f"      ⚠️  Cmax: не найден")
            
            if pk_params.get('auc', {}).get('value'):
                print(f"      ✅ AUC: {pk_params['auc']['value']} {pk_params['auc'].get('unit', 'N/A')}")
            else:
                print(f"      ⚠️  AUC: не найден")
            
            if pk_params.get('tmax', {}).get('value'):
                print(f"      ✅ Tmax: {pk_params['tmax']['value']} {pk_params['tmax'].get('unit', 'N/A')}")
            
            if pk_params.get('t_half', {}).get('value'):
                print(f"      ✅ T½: {pk_params['t_half']['value']} {pk_params['t_half'].get('unit', 'N/A')}")
            
            # Источники
            sources_count = sum([
                len(pk_params.get('cvintra', {}).get('sources', [])),
                len(pk_params.get('cmax', {}).get('sources', [])),
                len(pk_params.get('auc', {}).get('sources', []))
            ])
            if sources_count > 0:
                print(f"\n   🔗 Источников данных: {sources_count}")
            
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print("=" * 70)
    print("\n✅ Тест завершен!")
    print("\n💡 Рекомендации:")
    print("   - Если CVintra не извлекается, проверьте наличие статей с данными")
    print("   - Убедитесь, что biopython установлен: py -m pip install biopython")
    print("   - С API ключом запросы выполняются быстрее (10 req/sec vs 3 req/sec)")
    print()

if __name__ == '__main__':
    test_pubmed_api()
