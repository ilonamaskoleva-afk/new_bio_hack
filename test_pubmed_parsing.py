#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тест парсинга PubMed с проверкой API ключа
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from scrapers.pubmed_scraper import PubMedScraper

def test_pubmed_parsing():
    """Тест парсинга PubMed"""
    
    print("=" * 70)
    print("ТЕСТ ПАРСИНГА PubMed")
    print("=" * 70)
    
    # Проверка конфигурации
    print(f"\n📋 Конфигурация:")
    print(f"   API Key: {Config.NCBI_API_KEY[:15]}..." if Config.NCBI_API_KEY else "   API Key: ❌ НЕ УСТАНОВЛЕН")
    print(f"   Email: {Config.NCBI_EMAIL}")
    
    # Инициализация scraper
    print(f"\n🔧 Инициализация PubMedScraper...")
    try:
        scraper = PubMedScraper()
        
        if not hasattr(scraper, 'api_key'):
            print("   ❌ Ошибка: scraper не инициализирован (возможно, biopython не установлен)")
            return
        
        if scraper.api_key:
            print(f"   ✅ API ключ установлен: {scraper.api_key[:15]}...")
        else:
            print("   ⚠️  API ключ не установлен")
        
        print(f"   ✅ Email установлен: {scraper.email}")
        
    except Exception as e:
        print(f"   ❌ Ошибка инициализации: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Тест поиска
    test_inn = "aspirin"
    print(f"\n🔍 Тест поиска для: {test_inn}")
    print("-" * 70)
    
    try:
        result = scraper.get_drug_pk_data(test_inn)
        
        print(f"   📊 Результаты:")
        print(f"      Найдено статей: {result.get('count', 0)}")
        
        articles = result.get('articles', [])
        if articles:
            print(f"      ✅ Статьи получены успешно")
            for i, article in enumerate(articles[:3], 1):
                title = article.get('title', 'No title')[:50]
                print(f"         {i}. {title}...")
        else:
            print(f"      ⚠️  Статьи не найдены")
        
        # PK параметры
        pk_params = result.get('pk_parameters', {})
        print(f"\n   📈 PK параметры:")
        
        if pk_params.get('cvintra', {}).get('value'):
            print(f"      ✅ CVintra: {pk_params['cvintra']['value']}%")
        else:
            print(f"      ⚠️  CVintra: не найден")
        
        if pk_params.get('cmax', {}).get('value'):
            print(f"      ✅ Cmax: {pk_params['cmax']['value']} {pk_params['cmax'].get('unit', '')}")
        else:
            print(f"      ⚠️  Cmax: не найден")
        
        if pk_params.get('auc', {}).get('value'):
            print(f"      ✅ AUC: {pk_params['auc']['value']} {pk_params['auc'].get('unit', '')}")
        else:
            print(f"      ⚠️  AUC: не найден")
        
        print(f"\n   ✅ Парсинг завершен успешно")
        
    except Exception as e:
        print(f"   ❌ Ошибка парсинга: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    test_pubmed_parsing()
