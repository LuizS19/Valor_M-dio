"""
Interface Streamlit conforme fluxograma:
- Upload CSV (A1)
- Validacao e Insercao (A2, B2)
- Filtros na sidebar (C1)
- Cálculo média e exibição (C2, C3)
- CRUD: deletar registros (B3)
"""

import streamlit as st
import pandas as pd
from data_management import setup_database, importar_csv, load_data, deletar_registro
from typing import List

st.set_page_config(page_title="Preços Internet - Dashboard", layout="wide")
setup_database()  # garante que o DB e a tabela existam

st.title("📡 Preços de Internet — Painel de Análise")

# --- Upload e Importação CSV ---
st.header("Importar CSV")
with st.expander("Instruções e exemplo de colunas"):
    st.markdown("""
    O CSV deve conter, no mínimo, as seguintes colunas (nomes flexíveis, serão normalizados):
    - link_dedicado, velocidade, bloco_ip, valor, cidade, uf, tipo_servico

    **Observações**
    - Valor será convertido para numérico (ponto decimal).
    - UF e Cidade serão convertidos para MAIÚSCULAS sem acentuação.
    - Registros sem `link_dedicado` serão ignorados (PK).
    """)
uploaded_file = st.file_uploader("Escolha o arquivo CSV", type=["csv"])
if uploaded_file is not None:
    # 1. Chamar a função de importação de data_management.py aqui
    # 2. Recarregar os dados na interface
    pass

# --- Carregamento de Dados (cache) ---
@st.cache_data(ttl=600)
def get_data_cached():
    return load_data()
df = get_data_cached()

st.sidebar.header("Filtros (C1)")
# opções de filtro
ufs = sorted(df['uf'].dropna().unique()) if not df.empty else []
cidades = sorted(df['cidade'].dropna().unique()) if not df.empty else []
vels = sorted(df['velocidade'].dropna().unique()) if not df.empty else []
servicos = sorted(df['tipo_servico'].dropna().unique()) if not df.empty else []

selected_ufs = st.sidebar.multiselect("UF", options=ufs, default=ufs)
selected_cidades = st.sidebar.multiselect("Cidade", options=cidades, default=cidades)
selected_velocidades = st.sidebar.multiselect("Velocidade", options=vels, default=vels)
selected_servicos = st.sidebar.multiselect("Tipo de Serviço", options=servicos, default=servicos)

# Aplicar filtros (Processamento C2)
df_filtered = df.copy()
if selected_ufs:
    df_filtered = df_filtered[df_filtered['uf'].isin(selected_ufs)]
if selected_cidades:
    df_filtered = df_filtered[df_filtered['cidade'].isin(selected_cidades)]
if selected_velocidades:
    df_filtered = df_filtered[df_filtered['velocidade'].isin(selected_velocidades)]
if selected_servicos:
    df_filtered = df_filtered[df_filtered['tipo_servico'].isin(selected_servicos)]

# --- Métricas e Exibição ---
st.header("Resultados")
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    mean_valor = df_filtered['valor'].mean() if not df_filtered.empty else 0
    st.metric("Valor Médio (R$)", f"{mean_valor:,.2f}")
with col2:
    st.metric("Registros", len(df_filtered))
with col3:
    st.markdown("**Resumo por UF**")
    if not df_filtered.empty:
        resumo_uf = df_filtered.groupby("uf").agg(
            count=("valor", "count"),
            mean_valor=("valor", "mean")
        ).reset_index().sort_values("count", ascending=False)
        st.dataframe(resumo_uf, height=200)
    else:
        st.write("Sem dados para exibir.")

# Tabela detalhada e gráfico
st.subheader("Tabela Detalhada")
st.dataframe(df_filtered.reset_index(drop=True), use_container_width=True)

st.subheader("Gráfico — Valor Médio por Velocidade")
if not df_filtered.empty:
    graf_df = df_filtered.groupby("velocidade", as_index=False).agg(mean_valor=("valor", "mean"))
    st.bar_chart(graf_df.rename(columns={"velocidade": "index"}).set_index("index")["mean_valor"])
else:
    st.write("Sem dados para plotar.")

# --- CRUD: Deletar registros (B3) ---
st.header("Gerenciamento de Registros (Deleção)")
with st.expander("Deletar por link_dedicado"):
    link_to_delete = st.text_input("Link Dedicado (exatamente como está no banco):")
    if st.button("Deletar registro"):
        if link_to_delete.strip() == "":
            st.warning("Informe o link_dedicado para deletar.")
        else:
            affected = deletar_registro(link_to_delete)
            if affected:
                st.success(f"Registro deletado ({affected} linha afetada).")
                # limpar cache
                get_data_cached.clear()
                df = get_data_cached()
            else:
                st.info("Nenhum registro encontrado com esse link_dedicado.")

st.markdown("---")
st.caption("Fluxo: Upload CSV → validação → INSERT OR REPLACE → filtros → AVG(valor) e exibição.")

