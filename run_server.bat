@echo off

cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing PyTorch with CUDA 12.1...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
    echo Installing other requirements...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

uvicorn app:app --reload --host 0.0.0.0 --port 5000
