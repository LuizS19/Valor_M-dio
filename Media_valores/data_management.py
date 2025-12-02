import sqlite3
import pandas as pd
import os
from typing import List # Importando para tipagem

# Variável GLOBAL para o nome do banco
DB_NAME = "precos.db"

# ==============================================================
# 1. Criar e preparar o banco de dados
# ==============================================================

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS precos_internet (
            id INTEGER PRIMARY KEY,
            link TEXT,
            velocidade INTEGER,
            bloco_ip TEXT,
            valor REAL NOT NULL,
            cidade TEXT NOT NULL,
            uf TEXT NOT NULL,
            tipo_servico TEXT NOT NULL, 
            UNIQUE (cidade, uf, link, velocidade, tipo_servico) 
        );
    """)

    conn.commit()
    conn.close()
    print("✔ Banco de dados configurado.")

# ==============================================================
# 2. Importar CSV (Corrigido para UPSERT com tipo_servico)
# ==============================================================

def importar_csv(csv_file):
    if not os.path.exists(csv_file):
        print(f"Arquivo CSV não encontrado: {csv_file}")
        return

    # Lendo o arquivo CSV
    df = pd.read_csv(csv_file)

    # Normaliza os nomes das colunas
    df.columns = [c.strip().lower() for c in df.columns]

    # Conecta ao banco
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Usamos INSERT OR REPLACE, e a lista de colunas foi ATUALIZADA
    sql_insert_or_replace = """
        INSERT OR REPLACE INTO precos_internet 
        (link, velocidade, bloco_ip, valor, cidade, uf, tipo_servico) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    
    # Prepara os dados para inserção (lista de tuplas)
    data_to_insert = [
        (
            linha.get("link"),
            linha.get("velocidade"),
            linha.get("bloco_ip"),
            linha.get("valor"),
            linha.get("cidade"),
            linha.get("uf"),
            linha.get("tipo_servico") # ADICIONADO: Novo campo 'tipo_servico'
        )
        for _, linha in df.iterrows()
    ]
    
    # Execução em lote para melhor performance
    cursor.executemany(sql_insert_or_replace, data_to_insert)

    conn.commit()
    conn.close()
    print(f"✔ {len(df)} registros importados/atualizados com sucesso.")

# ==============================================================
# 3. Função para deletar registros (Atualizada para incluir tipo_servico)
# ==============================================================

def deletar_registro(uf=None, cidade=None, tipo_servico=None): # ADICIONADO: tipo_servico como parâmetro
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    sql = "DELETE FROM precos_internet WHERE 1=1"
    params = []

    if uf:
        sql += " AND uf = ?"
        params.append(uf)
    if cidade:
        sql += " AND cidade = ?"
        params.append(cidade)
    
    if tipo_servico: # NOVO FILTRO: Adiciona tipo_servico na cláusula WHERE
        sql += " AND tipo_servico = ?"
        params.append(tipo_servico)

    cursor.execute(sql, params)
    conn.commit()
    print(f"✔ {cursor.rowcount} registros deletados com sucesso.")
    conn.close()

# ==============================================================
# 4. Carregar todos os dados (Para a exibição principal)
# ==============================================================

def load_data():
    """Carrega todos os dados do banco de dados para um DataFrame."""
    conn = sqlite3.connect(DB_NAME) 
    try:
        df = pd.read_sql_query("SELECT * FROM precos_internet", conn)
    except pd.io.sql.DatabaseError:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

# ==============================================================
# 5. NOVO: Obter Tipos de Serviço Únicos (Para os filtros do Streamlit)
# ==============================================================

def get_all_service_types() -> List[str]:
    """Retorna uma lista de todos os tipos de serviço únicos no banco."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # DISTINCT garante que não haverá repetição (ex: só 'Link Dedicado' e 'Link Banda Larga')
    cursor.execute("SELECT DISTINCT tipo_servico FROM precos_internet ORDER BY tipo_servico")
    tipos = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tipos


# ==============================================================
# Execução direta do script (opcional)
# ==============================================================

if __name__ == "__main__":
    setup_database()
    if os.path.exists("dados.csv"): 
        importar_csv("dados.csv")
    else:
        print("Atenção: 'dados.csv' não encontrado. Use o Streamlit para importar.")