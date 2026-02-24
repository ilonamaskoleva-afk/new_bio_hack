@echo off
chcp 65001 >nul
echo ============================================================
echo Запуск BE Study Design AI Assistant
echo ============================================================
echo.

REM Проверка Python
py --version >nul 2>&1
if errorlevel 1 (
    python --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python не найден! Установите Python 3.8+
        pause
        exit /b 1
    )
    set PYTHON_CMD=python
) else (
    set PYTHON_CMD=py
)

echo [INFO] Проверка зависимостей...
%PYTHON_CMD% -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [WARN] Flask не установлен. Установка...
    %PYTHON_CMD% -m pip install Flask flask-cors python-dotenv requests beautifulsoup4 lxml biopython python-docx --user
    if errorlevel 1 (
        echo [ERROR] Не удалось установить зависимости!
        echo.
        echo Установите вручную:
        echo   %PYTHON_CMD% -m pip install Flask flask-cors python-dotenv requests beautifulsoup4 lxml biopython python-docx --user
        pause
        exit /b 1
    )
)

echo [INFO] Запуск сервиса...
echo [INFO] Сервис будет доступен по адресу: http://127.0.0.1:8000
echo [INFO] Нажмите Ctrl+C для остановки
echo.
%PYTHON_CMD% app.py

pause
