@echo off
echo Compilando FalaMemo (versao completa)...
echo.

REM Ativar ambiente virtual
call venv\Scripts\activate.bat

REM Instalar PyInstaller se ainda não estiver instalado
pip install pyinstaller

REM Executar script para preparar os arquivos de recursos do Whisper
echo Preparando arquivos de recursos do Whisper...
python fix_whisper_assets.py
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Falha ao preparar arquivos de recursos do Whisper.
    pause
    exit /b 1
)

REM Obter o caminho do módulo Whisper
for /f "tokens=*" %%i in ('python -c "import whisper; print(whisper.__path__[0])"') do set WHISPER_PATH=%%i
echo Caminho do Whisper: %WHISPER_PATH%

REM Obter o caminho do diretório temporário
for /f "tokens=*" %%i in ('python -c "import os; print(os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'temp'))"') do set TEMP_DIR=%%i
echo Diretório temporário: %TEMP_DIR%

REM Compilar o aplicativo com inclusão dos recursos necessários
echo Compilando aplicativo...
pyinstaller --name=FalaMemo ^
  --onefile ^
  --windowed ^
  --clean ^
  --add-data="%WHISPER_PATH%\assets;whisper\assets" ^
  --add-data="requirements.txt;." ^
  --collect-all=whisper ^
  --collect-all=customtkinter ^
  --hidden-import=whisper ^
  --hidden-import=whisper.tokenizer ^
  --hidden-import=whisper.audio ^
  --hidden-import=whisper.model ^
  --hidden-import=whisper.transcribe ^
  --hidden-import=whisper.utils ^
  --hidden-import=whisper.decoding ^
  --hidden-import=customtkinter ^
  --hidden-import=tkinter ^
  --hidden-import=torch ^
  --hidden-import=numpy ^
  --hidden-import=webbrowser ^
  main.py

REM Verificar se a compilação foi bem-sucedida
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Falha na compilação.
    pause
    exit /b 1
)

echo.
echo Compilação concluída com sucesso!
echo O executável está na pasta 'dist'.
echo Para distribuir o FalaMemo, compartilhe o arquivo 'dist\FalaMemo.exe'.
echo.

pause
