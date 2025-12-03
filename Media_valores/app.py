import streamlit as st
import pandas as pd

from data_management import (
    setup_database, importar_csv, load_data,
    deletar_registro,
    get_all_service_types, get_all_meios, calcular_medias
)

# ----------------------------------------------------------
# 🔧 Inicialização do Banco de Dados
# ----------------------------------------------------------
setup_database()

st.set_page_config(page_title="Gerenciamento Preços", layout="wide")
st.title("📡 Sistema de Preços de Internet — Médias e Gráficos")

# ----------------------------------------------------------
# 📥 IMPORTAÇÃO DE CSV
# ----------------------------------------------------------
st.sidebar.header("Importação de Dados")
uploaded = st.sidebar.file_uploader("Importar CSV", type=["csv"])

# Importa somente UMA VEZ
if uploaded and "csv_importado" not in st.session_state:
    with open("temp_import.csv", "wb") as f:
        f.write(uploaded.getbuffer())

    importar_csv("temp_import.csv")
    st.session_state["csv_importado"] = True
    st.sidebar.success("Dados importados com sucesso!")
    st.rerun()

# Botão opcional para permitir nova importação
if st.sidebar.button("Permitir nova importação"):
    if "csv_importado" in st.session_state:
        del st.session_state["csv_importado"]
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.write("O CSV deve ter cabeçalhos compatíveis com o padrão utilizado.")

# ----------------------------------------------------------
# 📊 CARREGAMENTO DOS DADOS (CACHEADO)
# ----------------------------------------------------------
@st.cache_data(ttl=30)
def get_df():
    return load_data()

df = get_df()

# ----------------------------------------------------------
# 🔎 FILTROS
# ----------------------------------------------------------
st.subheader("Filtros")

service_types = get_all_service_types()
meios = get_all_meios()

ufs = sorted(df['uf'].dropna().unique()) if not df.empty else []
cidades = sorted(df['cidade'].dropna().unique()) if not df.empty else []

f1, f2, f3, f4 = st.columns(4)

sel_service = f1.multiselect("Tipo Serviço", options=service_types, default=service_types)
sel_meio = f2.multiselect("Meio Físico", options=meios, default=meios)
sel_ufs = f3.multiselect("UF", options=ufs, default=ufs)
sel_cidades = f4.multiselect("Cidade", options=cidades, default=cidades)

df_filtered = df.copy()

if sel_service:
    df_filtered = df_filtered[df_filtered['tipo_servico'].isin(sel_service)]
if sel_meio:
    df_filtered = df_filtered[df_filtered['meio_fisico'].isin(sel_meio)]
if sel_ufs:
    df_filtered = df_filtered[df_filtered['uf'].isin(sel_ufs)]
if sel_cidades:
    df_filtered = df_filtered[df_filtered['cidade'].isin(sel_cidades)]

# ----------------------------------------------------------
# 📈 MÉTRICAS E MÉDIAS
# ----------------------------------------------------------
st.subheader("📊 Indicadores e Médias")

media_mensal, media_ativacao, media_combinada = calcular_medias(df_filtered)

col1, col2, col3 = st.columns(3)
col1.metric("Total de Registros", len(df_filtered))
col2.metric("Média Mensal (R$)", f"R$ {media_mensal:,.2f}" if media_mensal else "—")
col3.metric("Média Ativação (R$)", f"R$ {media_ativacao:,.2f}" if media_ativacao else "—")

st.metric("Média combinada ( (mensal + ativação) / 2 )",
          f"R$ {media_combinada:,.2f}" if media_combinada else "—")

st.markdown("---")

# ----------------------------------------------------------
# 📉 GRÁFICOS
# ----------------------------------------------------------
st.subheader("📈 Gráficos")

c1, c2 = st.columns(2)

with c1:
    st.markdown("**Valor médio mensal por UF**")
    if not df_filtered.empty:
        gr = df_filtered.groupby("uf")["mensal"].mean().sort_values(ascending=False)
        st.bar_chart(gr)
    else:
        st.write("Sem dados para exibir.")

with c2:
    st.markdown("**Valor médio mensal por Tipo de Serviço**")
    if not df_filtered.empty:
        gr2 = df_filtered.groupby("tipo_servico")["mensal"].mean().sort_values(ascending=False)
        st.bar_chart(gr2)
    else:
        st.write("Sem dados para exibir.")

st.markdown("---")

# ----------------------------------------------------------
# 📋 TABELA FINAL
# ----------------------------------------------------------
st.subheader("📋 Tabela de Dados (Filtrada)")
st.dataframe(df_filtered.reset_index(drop=True), use_container_width=True)

st.markdown("---")

st.caption("Observação: média combinada = (Mensal + Ativação) / 2.")
