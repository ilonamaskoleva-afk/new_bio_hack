# cv_database.py
# Словарь типичных CVintra для популярных препаратов
# Используется для автоматического определения вариабельности

cv_typical = {
    "aspirin": 15,
    "metformin": 35,
    "ibuprofen": 20,
    "paracetamol": 18,
    "amlodipine": 22,
    "simvastatin": 30,
    "atorvastatin": 28,
    "omeprazole": 40,
    "warfarin": 45,
    "levothyroxine": 50,
    "propranolol": 55,  # Высоковариабельный препарат
    "phenytoin": 30,
    "digoxin": 25,
    "theophylline": 20,
    "carbamazepine": 25,
    "valproic acid": 18,
    "lithium": 22,
    "cyclosporine": 35,
    "tacrolimus": 30,
    "sirolimus": 28,
    # ... можно расширять
}

def get_typical_cv(inn: str) -> float:
    """
    Возвращает типичный CVintra для данного INN.
    Если не найдено — возвращает 25.
    """
    inn_lower = inn.lower()
    return cv_typical.get(inn_lower, 25)
