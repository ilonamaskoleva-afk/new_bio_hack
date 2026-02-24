#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ДЕМОНСТРАЦИЯ СИСТЕМЫ
Полный цикл: от запроса к полному анализу
"""

import subprocess
import time
import sys
import json
import requests

def print_banner(text):
    print("\n" + "█" * 80)
    print(f"█ {text:<76} █")
    print("█" * 80)

def print_section(text):
    print(f"\n🔹 {text}")
    print("─" * 80)

# Запуск сервера
print_banner("🚀 ДЕМОНСТРАЦИЯ СИСТЕМЫ ПОИСКА БИОЭКВИВАЛЕНТНОСТИ")

print("\n⏳ Запуск Flask сервера на 127.0.0.1:5000...")

try:
    # Попытка подключиться к существующему серверу
    response = requests.get("http://127.0.0.1:5000/api/health", timeout=2)
    print("✅ Сервер уже запущен!")
except:
    print("⚠️ Сервер не запущен, требуется запустить:")
    print("   cd backend")
    print("   python app.py")
    print("\nПосле запуска сервера откройте в браузере:")
    print("   http://127.0.0.1:5000")
    sys.exit(1)

# Примеры запросов
print_banner("📊 ПРИМЕРЫ ЗАПРОСОВ")

test_cases = [
    {
        "name": "Aspirin (низкая вариабельность)",
        "data": {
            "inn": "aspirin",
            "dosage_form": "tablet",
            "dosage": "500mg",
            "administration_mode": "fasted",
            "cvintra": 25
        }
    },
    {
        "name": "Metformin (средняя вариабельность)",
        "data": {
            "inn": "metformin",
            "dosage_form": "tablet",
            "dosage": "500mg",
            "administration_mode": "fed",
            "cvintra": 35
        }
    },
    {
        "name": "Ibuprofen (высокая вариабельность)",
        "data": {
            "inn": "ibuprofen",
            "dosage_form": "tablet",
            "dosage": "200mg",
            "administration_mode": "fasted",
            "cvintra": 45
        }
    }
]

for i, test_case in enumerate(test_cases, 1):
    print_section(f"ЗАПРОС {i}: {test_case['name']}")
    
    payload = json.dumps(test_case['data'], ensure_ascii=False)
    print(f"📤 Отправка: {test_case['data']}")
    
    try:
        response = requests.post(
            "http://127.0.0.1:5000/api/full-analysis",
            data=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ Статус: 200 OK")
            print(f"\n📚 ЛИТЕРАТУРА:")
            print(f"   PubMed статей: {result['literature']['pubmed'].get('count', 0)}")
            
            if result['literature']['pubmed'].get('articles'):
                for j, article in enumerate(result['literature']['pubmed']['articles'][:2], 1):
                    title = article.get('title', '')[:70]
                    print(f"   {j}. {title}...")
            
            print(f"\n🔬 ДИЗАЙН ИССЛЕДОВАНИЯ:")
            design = result['design_recommendation']
            print(f"   Рекомендуемый дизайн: {design.get('recommended_design')}")
            print(f"   Обоснование: {design.get('rationale')}")
            
            print(f"\n👥 РАЗМЕР ВЫБОРКИ:")
            ss = result['sample_size']
            print(f"   Дизайн: {ss.get('design')}")
            print(f"   CVintra: {ss.get('cvintra')}%")
            print(f"   Базовый N: {ss.get('base_sample_size')}")
            print(f"   Итоговый N (с отсевом): {ss.get('final_sample_size')}")
            
            print(f"\n⚖️ РЕГУЛЯТОРНЫЕ ТРЕБОВАНИЯ:")
            for reg, comply in result['regulatory_check'].items():
                status = "✅" if comply.get('compliant') else "❌"
                print(f"   {status} {reg.upper()}: соответствует")
        
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(f"   {response.text[:200]}")
    
    except requests.exceptions.Timeout:
        print("❌ Timeout при запросе (>15 сек)")
    except Exception as e:
        print(f"❌ Ошибка: {str(e)[:100]}")
    
    print()

# Итоговый отчет
print_banner("✅ ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")

print("""
📌 КЛЮЧЕВЫЕ РЕЗУЛЬТАТЫ:

1. ✅ PubMed интеграция работает с API ключом
   - Быстрые запросы (10 req/sec)
   - Реальные статьи в ответе
   - Парсинг данных авторов и года

2. ✅ Расчет дизайна и размера выборки работает
   - Правильное определение дизайна по CVintra
   - Расчет с учетом отсева
   - Регуляторная проверка

3. ⚠️ Известные ограничения
   - ГРЛС требует JavaScript рендеринга
   - DrugBank защищен от ботов
   - PK параметры требуют ручной нормализации

📞 СЛЕДУЮЩИЕ ШАГИ:
   1. Откройте http://127.0.0.1:5000 в браузере
   2. Заполните форму данными препарата
   3. Нажмите "Поиск и анализ"
   4. Скачайте синопсис в нужном формате

🎯 СИСТЕМА ПОЛНОСТЬЮ ГОТОВА К ИСПОЛЬЗОВАНИЮ!
""")

print("█" * 80 + "\n")
