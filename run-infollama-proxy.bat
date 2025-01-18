:: Navigate to the directory containing the virtual environment
cd /d venv\Scripts
:: Activate the virtual environment
call activate

:: Navigate to the app directory 
cd ../..
:: Run the proxy script
python proxy.py
