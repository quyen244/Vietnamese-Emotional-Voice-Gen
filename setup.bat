@echo off
echo ==================================
echo  Vn-EmoVoice Setup Script (Windows) 
echo ==================================

:: Create virtual environment if it doesn't exist
IF NOT EXIST ".venv" (
    echo [*] Creating virtual environment .venv...
    python -m venv .venv
) ELSE (
    echo [*] Virtual environment .venv already exists.
)

:: Activate virtual environment
call .venv\Scripts\activate.bat

:: Install dependencies
echo [*] Installing requirements...
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Create necessary directories
if not exist "models" mkdir models
if not exist "data\outputs" mkdir data\outputs

:: Prompt to download models
set /p download_ans="Do you want to download the model weights now? (y/n): "
IF /I "%download_ans%" EQU "y" (
    echo [*] Triggering model downloader...
    python tools\download_models.py
) ELSE (
    echo [*] Skipping model download. You can run 'python tools\download_models.py' later.
)

echo [+] Setup complete! Run '.venv\Scripts\activate.bat' to activate the environment.
echo [+] Start server using: 'uvicorn src.api:app --reload'
pause
