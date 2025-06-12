@echo off
echo Installing required Python packages...
python -m pip install --upgrade pip
python -m pip install qrcode pillow

echo Launching app...

start "" pythonw app.py

exit
