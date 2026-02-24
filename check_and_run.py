#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для проверки зависимостей и запуска сервиса
"""
import sys
import importlib

def check_imports():
    """Проверка критических импортов"""
    required_modules = {
        'flask': 'Flask',
        'flask_cors': 'flask-cors',
        'dotenv': 'python-dotenv',
        'requests': 'requests',
        'bs4': 'beautifulsoup4',
    }
    
    optional_modules = {
        'Bio': 'biopython',
        'docx': 'python-docx',
        'transformers': 'transformers',
        'torch': 'torch',
        'langchain': 'langchain',
    }
    
    missing_required = []
    missing_optional = []
    
    print("=" * 60)
    print("Проверка зависимостей...")
    print("=" * 60)
    
    # Проверка обязательных модулей
    for module_name, package_name in required_modules.items():
        try:
            importlib.import_module(module_name)
            print(f"[OK] {package_name}")
        except ImportError:
            print(f"[MISSING] {package_name} - ОБЯЗАТЕЛЬНО")
            missing_required.append(package_name)
    
    # Проверка опциональных модулей
    for module_name, package_name in optional_modules.items():
        try:
            importlib.import_module(module_name)
            print(f"[OK] {package_name} (опционально)")
        except ImportError:
            print(f"[WARN] {package_name} - опционально")
            missing_optional.append(package_name)
    
    print("=" * 60)
    
    if missing_required:
        print("\n[ERROR] Отсутствуют обязательные модули:")
        for mod in missing_required:
            print(f"   - {mod}")
        print("\nУстановите их командой:")
        print(f"   py -m pip install {' '.join(missing_required)}")
        return False
    
    if missing_optional:
        print("\n[WARN] Отсутствуют опциональные модули (некоторые функции могут не работать):")
        for mod in missing_optional:
            print(f"   - {mod}")
    
    print("\n[SUCCESS] Все обязательные зависимости установлены!")
    return True

if __name__ == '__main__':
    if check_imports():
        print("\nЗапуск сервиса...")
        print("=" * 60 + "\n")
        try:
            from app import app
            app.run(host='127.0.0.1', port=8000, debug=True)
        except Exception as e:
            print(f"\n[ERROR] Ошибка при запуске: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print("\n[ERROR] Установите недостающие зависимости перед запуском")
        sys.exit(1)
