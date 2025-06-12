@echo off
echo Installing required components...
python -m pip install --upgrade pip

echo Installing required Python packages...
python -m pip install qrcode pillow

echo Building executable from source code...
pyinstaller --onefile --windowed --icon=app.png --name QR-POS app.py

echo Build complete.
pause
