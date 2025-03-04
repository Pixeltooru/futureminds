@echo off
:: Устанавливаем кодировку UTF-8 для консоли
chcp 65001 >nul

:: Указываем полный путь к PowerShell
set "psCmd=C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%psCmd%" (
    echo [ERROR] Не найден PowerShell по пути: %psCmd%
    pause
    exit /b 1
)

:: Проверка наличия Python в системе
echo ============================================
echo Проверка наличия Python в системе...
echo ============================================

python --version >nul 2>&1
if %errorlevel%==0 (
    echo [OK] Python установлен в системе.
    goto :check_files
) else (
    echo [ERROR] Python не найден в системе.
    echo.
    set /p installPython="Хотите скачать и установить Python? (y/n): "
    if /i "%installPython%"=="y" (
        echo.
        echo Выберите версию Python для установки:
        echo 1. Python 3.12
        echo 2. Python 3.10
        echo 3. Python 3.8
        echo 4. Python 3.7
        echo 5. Python 3.6
        echo 6. Python 3.5
        echo 7. Python 3.4
        echo 8. Python 3.3
        echo 9. Python 3.2
        echo 10. Python 3.1
        set /p pythonVersion="Введите номер версии (1-10): "
        
        :: Создаем папку для установщика Python
        if not exist "python_setuper" (
            mkdir "python_setuper"
        )
        
        :: Скачиваем установщик Python в зависимости от выбранной версии
        echo.
        echo Скачивание установщика Python...
        if "%pythonVersion%"=="1" (
            set "pythonUrl=https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe"
        ) else if "%pythonVersion%"=="2" (
            set "pythonUrl=https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe"
        ) else if "%pythonVersion%"=="3" (
            set "pythonUrl=https://www.python.org/ftp/python/3.8.0/python-3.8.0-amd64.exe"
        ) else if "%pythonVersion%"=="4" (
            set "pythonUrl=https://www.python.org/ftp/python/3.7.0/python-3.7.0-amd64.exe"
        ) else if "%pythonVersion%"=="5" (
            set "pythonUrl=https://www.python.org/ftp/python/3.6.0/python-3.6.0-amd64.exe"
        ) else if "%pythonVersion%"=="6" (
            set "pythonUrl=https://www.python.org/ftp/python/3.5.0/python-3.5.0-amd64.exe"
        ) else if "%pythonVersion%"=="7" (
            set "pythonUrl=https://www.python.org/ftp/python/3.4.0/python-3.4.0-amd64.exe"
        ) else if "%pythonVersion%"=="8" (
            set "pythonUrl=https://www.python.org/ftp/python/3.3.0/python-3.3.0-amd64.exe"
        ) else if "%pythonVersion%"=="9" (
            set "pythonUrl=https://www.python.org/ftp/python/3.2.0/python-3.2.0-amd64.exe"
        ) else if "%pythonVersion%"=="10" (
            set "pythonUrl=https://www.python.org/ftp/python/3.1.0/python-3.1.0-amd64.exe"
        ) else (
            echo [ERROR] Неверный выбор версии Python.
            pause
            exit /b 1
        )
        
        "%psCmd%" -NoProfile -Command ^
          "try { " ^
          "    $ErrorActionPreference = 'Stop'; " ^
          "    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; " ^
          "    Invoke-WebRequest -Uri '%pythonUrl%' -OutFile 'python_setuper\python_installer.exe'; " ^
          "} catch { " ^
          "    Write-Error ('Ошибка загрузки установщика Python: ' + $_.Exception.Message); exit 1 " ^
          "}"
        
        if errorlevel 1 (
            echo [ERROR] Не удалось загрузить установщик Python!
            pause
            exit /b 1
        )
        
        echo Установщик Python успешно скачан.
        echo.
        echo Запуск установщика Python...
        start "" "python_setuper\python_installer.exe"
        echo Установите Python и перезапустите этот скрипт.
        pause
        exit /b 0
    ) else (
        echo [INFO] Установка Python отменена.
        pause
        exit /b 1
    )
)

:check_files
echo.
echo ============================================
echo Проверка необходимых файлов...
echo ============================================

:: Список необходимых файлов
set "files=FutureMinds.ico launcher.py pialn_handler.py start.ico starter.py starter.spec launcher.spec"
set "missingFileFound=0"

for %%f in (%files%) do (
    if not exist "%%f" (
        echo [!] Файл "%%f" не найден!
        set "missingFileFound=1"
    ) else (
        echo [OK] Файл "%%f" найден.
    )
)

if "%missingFileFound%"=="1" (
    echo.
    echo Некоторые файлы отсутствуют. Будет произведена загрузка архива FutureMinds.zip с сервера...
    echo Загрузка FutureMinds.zip...
    
    :: Выполняем загрузку архива через PowerShell с нужными заголовками и установкой TLS 1.2
    "%psCmd%" -NoProfile -Command ^
      "try { " ^
      "    $ErrorActionPreference = 'Stop'; " ^
      "    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; " ^
      "    $headers = @{ 'User-Agent'='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36'; 'Accept'='*/*' }; " ^
      "    Invoke-WebRequest -Uri 'https://futureminds.pixeltoo.ru/ass/app/FutureMinds.zip' -OutFile 'FutureMinds.zip' -Headers $headers; " ^
      "    $firstLine = Get-Content 'FutureMinds.zip' -TotalCount 1; " ^
      "    if ($firstLine -match '<HTML>') { Write-Error 'Скачанный файл содержит HTML. Возможно, ошибка авторизации.' } " ^
      "} catch { " ^
      "    Write-Error ('Ошибка загрузки архива: ' + $_.Exception.Message); exit 1 " ^
      "}"
    
    if errorlevel 1 (
        echo [ERROR] Не удалось загрузить корректный архив FutureMinds.zip! Проверьте URL и параметры авторизации!
        pause
        exit /b 1
    )
    
    echo Распаковка архива FutureMinds.zip...
    "%psCmd%" -NoProfile -Command "Expand-Archive -Force 'FutureMinds.zip' 'temp_extracted'"
    if errorlevel 1 (
        echo [ERROR] Не удалось распаковать FutureMinds.zip!
        pause
        exit /b 1
    )
    
    echo Копирование зависимостей из папки "temp_extracted\py--not compiled"...
    copy /Y "temp_extracted\FutureMinds.ico" .
    copy /Y "temp_extracted\launcher.py" .
    copy /Y "temp_extracted\pialn_handler.py" .
    copy /Y "temp_extracted\start.ico" .
    copy /Y "temp_extracted\starter.py" .
    copy /Y "temp_extracted\starter.spec" .
    copy /Y "temp_extracted\launcher.spec" .
    if errorlevel 1 (
        echo [ERROR] Ошибка копирования зависимостей!
        pause
        exit /b 1
    )
    echo Зависимости успешно скопированы.
    echo.
) else (
    echo Все необходимые файлы на месте.
)

echo.
echo =================================
echo Установка библиотек...
echo =================================
:: Устанавливаем необходимые библиотеки:
:: • PyQt6 и PyQt6-WebEngine для GUI и WebEngine
:: • requests и urllib3 для работы с HTTP
pip install PyQt6 PyQt6-WebEngine requests urllib3 pyinstaller
if errorlevel 1 (
    echo [ERROR] Ошибка установки библиотек!
    pause
    exit /b 1
)
echo Установка библиотек завершена!
pause

echo.
echo =================================
echo Компиляция launcher...
echo =================================
echo [0%%] Запуск сборки launcher...
pyinstaller launcher.spec
if errorlevel 1 (
    echo [ERROR] Ошибка компиляции launcher!
    pause
    exit /b 1
)
echo [50%%] Launcher успешно скомпилирован!

:: Копируем файлы из dist в compiled
echo Копирование файлов из dist в compiled...
if not exist "compiled" (
    mkdir "compiled"
)
xcopy /E /I /Y "dist\*" "compiled\"
if errorlevel 1 (
    echo [ERROR] Ошибка копирования файлов в папку compiled!
    pause
    exit /b 1
)
echo Файлы успешно скопированы в папку compiled.


echo.
echo =================================
echo Компиляция starter...
echo =================================
echo [50%%] Запуск сборки starter...
pyinstaller starter.spec
if errorlevel 1 (
    echo [ERROR] Ошибка компиляции starter!
    pause
    exit /b 1
)
echo [100%%] Starter успешно скомпилирован!

:: Копируем файлы из dist в compiled
echo Копирование файлов из dist в compiled...
xcopy /E /I /Y "dist\*" "compiled\"
if errorlevel 1 (
    echo [ERROR] Ошибка копирования файлов в папку compiled!
    pause
    exit /b 1
)
echo Файлы успешно скопированы в папку compiled.

echo.
echo Открытие папки "compiled" в проводнике...
set "currentDir=%~dp0"
set "compiledPath=%currentDir%compiled"

:: Открываем папку в Проводнике
%SystemRoot%\explorer.exe "%compiledPath%"

pause