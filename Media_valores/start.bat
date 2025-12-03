@echo off
echo Ativando ambiente virtual...

call venv\Scripts\activate

echo Iniciando sistema Streamlit...
streamlit run app.py

pause
