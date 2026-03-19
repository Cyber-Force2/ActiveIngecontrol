import io
from typing import Dict, List

import pandas as pd
import streamlit as st


REQUIRED_COLUMNS: List[str] = [
    "OP_Card",
    "SU_Card",
    "Country",
    "Maintainer",
    "End date & time",
    "EMS",
    "Terminal ID",
    "Terminal processed",
    "Status&result",
]

COLUMN_DISPLAY_MAP: Dict[str, str] = {
    "OP_Card": "U-key Oper",
    "SU_Card": "U-key Sup",
    "Maintainer": "CR",
    "End date & time": "Data de Ativacao",
    "EMS": "Fabrica",
    "Terminal ID": "Serial Number",
    "Terminal processed": "Part Number",
    "Status&result": "Status",
}

STATUS_SUCCESS = "SUCCESS"


st.set_page_config(page_title="Customizations Analysis", layout="wide")

st.title("Customizations Analysis")
st.caption("Analise de customizacoes por centro de reparo e pais")

uploaded_file = st.file_uploader("Envie o arquivo Excel", type=["xlsx", "xls"])

if not uploaded_file:
    st.info("Carregue um arquivo Excel para iniciar a analise.")
    st.stop()

try:
    file_bytes = uploaded_file.read()
    data = pd.read_excel(io.BytesIO(file_bytes))
except Exception as exc:
    st.error("Nao foi possivel ler o arquivo. Verifique o formato do Excel.")
    st.exception(exc)
    st.stop()

missing_columns = [col for col in REQUIRED_COLUMNS if col not in data.columns]
if missing_columns:
    st.error(
        "O arquivo nao contem todas as colunas necessarias. "
        "Colunas faltando: " + ", ".join(missing_columns)
    )
    st.stop()

# Parse date column and create a clean copy for filtering
filtered_data = data.copy()
filtered_data["End date & time"] = pd.to_datetime(
    filtered_data["End date & time"], dayfirst=True, errors="coerce"
)

# Sidebar filters
st.sidebar.header("Filtros")

countries = sorted(filtered_data["Country"].dropna().unique().tolist())
maintainers = sorted(filtered_data["Maintainer"].dropna().unique().tolist())
op_cards = sorted(filtered_data["OP_Card"].dropna().unique().tolist())
statuses = sorted(filtered_data["Status&result"].dropna().unique().tolist())

selected_countries = st.sidebar.multiselect("Pais", countries, default=countries)
selected_maintainers = st.sidebar.multiselect("CR", maintainers, default=maintainers)
selected_op_cards = st.sidebar.multiselect("U-key Oper", op_cards, default=op_cards)
selected_statuses = st.sidebar.multiselect("Status", statuses, default=statuses)

min_date = filtered_data["End date & time"].min()
max_date = filtered_data["End date & time"].max()

if pd.isna(min_date) or pd.isna(max_date):
    date_range = None
else:
    date_range = st.sidebar.date_input(
        "Data de Ativacao (intervalo)",
        value=(min_date.date(), max_date.date()),
        min_value=min_date.date(),
        max_value=max_date.date(),
    )

mask = (
    filtered_data["Country"].isin(selected_countries)
    & filtered_data["Maintainer"].isin(selected_maintainers)
    & filtered_data["OP_Card"].isin(selected_op_cards)
    & filtered_data["Status&result"].isin(selected_statuses)
)

if date_range:
    start_date, end_date = date_range
    mask &= filtered_data["End date & time"].between(
        pd.to_datetime(start_date), pd.to_datetime(end_date), inclusive="both"
    )

filtered_data = filtered_data.loc[mask].copy()

# KPI calculations
active_terminals = (
    filtered_data.loc[filtered_data["Status&result"] == STATUS_SUCCESS, "Terminal ID"]
    .dropna()
    .nunique()
)

col1, col2, col3 = st.columns(3)
col1.metric("Terminais ativos", f"{active_terminals}")
col2.metric("Registros filtrados", f"{len(filtered_data)}")
col3.metric("Terminais unicos", f"{filtered_data['Terminal ID'].nunique()}")

# Display table with renamed columns
present_data = filtered_data.rename(columns=COLUMN_DISPLAY_MAP)

st.subheader("Dados filtrados")
st.dataframe(present_data, use_container_width=True)

# Download filtered data
csv_data = present_data.to_csv(index=False).encode("utf-8")
st.download_button(
    "Baixar CSV filtrado",
    data=csv_data,
    file_name="customizations_filtrado.csv",
    mime="text/csv",
)
