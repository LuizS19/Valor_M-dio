@echo off
echo ==========================================================
echo       SISTEMA DE MEDIAS - INICIALIZANDO NO WINDOWS
echo ==========================================================

REM ====== 1. Criar ambiente virtual se não existir ======
if not exist venv (
    echo Criando ambiente virtual...
    python -m venv venv
)

REM ====== 2. Liberar scripts no PowerShell ======
echo Ajustando permissoes do PowerShell para ativar o venv...
powershell -Command "Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass"

REM ====== 3. Ativar ambiente virtual ======
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM ====== 4. Instalar dependencias ======
echo Instalando dependencias do requirements.txt...
pip install --upgrade pip
pip install -r requirements.txt

REM ====== 5. Configurar o banco e importar CSV ======
echo Executando data_management.py...
python data_management.py

REM ====== 6. Iniciar Streamlit ======
echo Iniciando o sistema no navegador...
streamlit run app.py

echo ==========================================================
echo            SISTEMA ENCERRADO
echo ==========================================================

pause
