import io
from typing import Dict, List, Optional, Tuple

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

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }

    .app-bg {
        background: radial-gradient(1200px 800px at 10% -20%, #dbe8ff 0%, rgba(255,255,255,0) 55%),
                    radial-gradient(900px 700px at 100% 0%, #fde7d0 0%, rgba(255,255,255,0) 50%),
                    linear-gradient(180deg, #f6f4f1 0%, #f0ede7 100%);
        padding: 1.2rem 1.6rem 0 1.6rem;
        border-radius: 18px;
        border: 1px solid rgba(20, 20, 20, 0.06);
    }

    .hero {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1.5rem;
        padding: 1.2rem 1.6rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #1f2a44 0%, #2f3a56 45%, #5a3f2f 100%);
        color: #f7f6f2;
        box-shadow: 0 20px 60px rgba(35, 45, 70, 0.25);
    }

    .hero h1 {
        font-family: 'Playfair Display', serif;
        font-size: 2.2rem;
        margin: 0;
    }

    .hero p {
        margin: 0.35rem 0 0 0;
        opacity: 0.85;
    }

    .eyebrow {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.18rem;
        opacity: 0.7;
    }

    .glass {
        background: rgba(255, 255, 255, 0.85);
        border-radius: 16px;
        border: 1px solid rgba(20, 20, 20, 0.05);
        padding: 1.1rem 1.2rem;
        box-shadow: 0 16px 40px rgba(20, 20, 20, 0.08);
    }

    .metric-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 1rem 1.2rem;
        border: 1px solid rgba(30, 30, 30, 0.08);
        box-shadow: 0 12px 26px rgba(20, 20, 20, 0.07);
    }

    .metric-card h3 {
        margin: 0 0 0.4rem 0;
        font-size: 0.9rem;
        font-weight: 600;
        color: #2b2b2b;
        text-transform: uppercase;
        letter-spacing: 0.08rem;
    }

    .metric-card p {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
        color: #1c1c1c;
    }

    .metric-card span {
        display: block;
        margin-top: 0.25rem;
        font-size: 0.85rem;
        color: #5a5a5a;
    }

    .tag {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.12rem;
        background: rgba(255, 255, 255, 0.2);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='hero'>", unsafe_allow_html=True)
st.markdown(
    """
    <div>
        <div class="eyebrow">Customizations</div>
        <h1>Customizations Analysis</h1>
        <p>Analise de customizacoes por centro de reparo e pais com foco em KPI.</p>
    </div>
    <div class="tag">Streamlined KPI</div>
    """,
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='app-bg'>", unsafe_allow_html=True)

top_left, top_right = st.columns([1.2, 1])
with top_left:
    uploaded_file = st.file_uploader("Envie o arquivo Excel", type=["xlsx", "xls"])

if not uploaded_file:
    st.info("Carregue um arquivo Excel para iniciar a analise.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

try:
    file_bytes = uploaded_file.read()
    data = pd.read_excel(io.BytesIO(file_bytes))
except Exception as exc:
    st.error("Nao foi possivel ler o arquivo. Verifique o formato do Excel.")
    st.exception(exc)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

missing_columns = [col for col in REQUIRED_COLUMNS if col not in data.columns]
if missing_columns:
    st.error(
        "O arquivo nao contem todas as colunas necessarias. "
        "Colunas faltando: " + ", ".join(missing_columns)
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

data = data.copy()
data["End date & time"] = pd.to_datetime(
    data["End date & time"], dayfirst=True, errors="coerce"
)

min_date = data["End date & time"].min()
max_date = data["End date & time"].max()

with top_right:
    st.markdown(
        """
        <div class="glass">
            <strong>Resumo do arquivo</strong>
            <div style="margin-top:0.6rem; font-size:0.9rem; color:#3c3c3c;">
                Linhas carregadas: <strong>{rows}</strong><br/>
                Terminais unicos: <strong>{terminals}</strong><br/>
                Periodo: <strong>{periodo}</strong>
            </div>
        </div>
        """.format(
            rows=len(data),
            terminals=data["Terminal ID"].nunique(),
            periodo=(
                f"{min_date.date()} a {max_date.date()}"
                if pd.notna(min_date) and pd.notna(max_date)
                else "Indefinido"
            ),
        ),
        unsafe_allow_html=True,
    )


def build_filter_options(values: pd.Series) -> List[str]:
    return sorted(values.dropna().unique().tolist())


def apply_text_filter(values: pd.Series, query: str) -> pd.Series:
    if not query:
        return pd.Series([True] * len(values), index=values.index)
    query = query.strip().lower()
    return values.fillna("").str.lower().str.contains(query)


with st.expander("Filtros e pesquisa", expanded=True):
    f1, f2, f3 = st.columns(3)
    f4, f5, f6 = st.columns(3)

    countries = build_filter_options(data["Country"])
    maintainers = build_filter_options(data["Maintainer"])
    op_cards = build_filter_options(data["OP_Card"])
    statuses = build_filter_options(data["Status&result"])

    selected_countries = f1.multiselect("Pais", countries, default=countries)
    selected_maintainers = f2.multiselect("CR", maintainers, default=maintainers)
    selected_op_cards = f3.multiselect("U-key Oper", op_cards, default=op_cards)

    selected_statuses = f4.multiselect("Status", statuses, default=statuses)
    quick_status = f5.selectbox(
        "Filtro rapido de Status",
        options=["Todos", "SUCCESS", "FAILURE"],
        index=0,
    )
    serial_search = f6.text_input("Buscar Serial Number")

    f7, f8, f9 = st.columns(3)
    part_search = f7.text_input("Buscar Part Number")
    op_search = f8.text_input("Buscar U-key Oper (contendo)")

    if pd.isna(min_date) or pd.isna(max_date):
        date_range: Optional[Tuple[pd.Timestamp, pd.Timestamp]] = None
        f9.info("Datas invalidas no arquivo")
    else:
        date_range = f9.date_input(
            "Data de Ativacao (intervalo)",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date(),
        )

mask = (
    data["Country"].isin(selected_countries)
    & data["Maintainer"].isin(selected_maintainers)
    & data["OP_Card"].isin(selected_op_cards)
    & data["Status&result"].isin(selected_statuses)
)

if quick_status != "Todos":
    mask &= data["Status&result"] == quick_status

mask &= apply_text_filter(data["Terminal ID"], serial_search)
mask &= apply_text_filter(data["Terminal processed"], part_search)
mask &= apply_text_filter(data["OP_Card"], op_search)

if date_range:
    start_date, end_date = date_range
    mask &= data["End date & time"].between(
        pd.to_datetime(start_date), pd.to_datetime(end_date), inclusive="both"
    )

filtered_data = data.loc[mask].copy()

success_count = filtered_data["Status&result"].eq(STATUS_SUCCESS).sum()
total_count = len(filtered_data)
active_terminals = (
    filtered_data.loc[filtered_data["Status&result"] == STATUS_SUCCESS, "Terminal ID"]
    .dropna()
    .nunique()
)
unique_terminals = filtered_data["Terminal ID"].dropna().nunique()
success_rate = (success_count / total_count) * 100 if total_count else 0

st.markdown("<div style='margin-top:1.2rem'></div>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
for column, label, value, sublabel in [
    (c1, "Terminais ativos", f"{active_terminals}", "Status SUCCESS"),
    (c2, "Registros filtrados", f"{total_count}", "Linhas selecionadas"),
    (c3, "Terminais unicos", f"{unique_terminals}", "Serial Number"),
    (c4, "Taxa de sucesso", f"{success_rate:.1f}%", "SUCCESS / total"),
]:
    with column:
        st.markdown(
            """
            <div class="metric-card">
                <h3>{label}</h3>
                <p>{value}</p>
                <span>{sublabel}</span>
            </div>
            """.format(label=label, value=value, sublabel=sublabel),
            unsafe_allow_html=True,
        )

st.markdown("<div style='margin-top:1.4rem'></div>", unsafe_allow_html=True)

tab_overview, tab_details = st.tabs(["Visao geral", "Detalhes"])

with tab_overview:
    left, right = st.columns([1.1, 1])
    with left:
        st.subheader("Ativacoes por CR")
        if filtered_data.empty:
            st.info("Sem dados para o filtro atual.")
        else:
            cr_counts = (
                filtered_data.groupby("Maintainer")["Terminal ID"]
                .nunique()
                .sort_values(ascending=False)
                .head(12)
            )
            st.bar_chart(cr_counts)

        st.subheader("Uso por CR (quantidade)")
        if not filtered_data.empty:
            cr_usage = (
                filtered_data.groupby("Maintainer")["Terminal ID"]
                .size()
                .sort_values(ascending=False)
                .head(12)
            )
            st.bar_chart(cr_usage)

    with right:
        st.subheader("Ativacoes por Pais")
        if not filtered_data.empty:
            country_counts = (
                filtered_data.groupby("Country")["Terminal ID"]
                .nunique()
                .sort_values(ascending=False)
            )
            st.bar_chart(country_counts)

        st.subheader("Uso por Pais (quantidade)")
        if not filtered_data.empty:
            country_usage = (
                filtered_data.groupby("Country")["Terminal ID"]
                .size()
                .sort_values(ascending=False)
            )
            st.bar_chart(country_usage)

    st.subheader("Uso por data (quantidade)")
    if not filtered_data.empty:
        usage_series = (
            filtered_data.dropna(subset=["End date & time"])
            .groupby(filtered_data["End date & time"].dt.date)["Terminal ID"]
            .size()
            .rename("Quantidade")
        )
        st.line_chart(usage_series)

    st.subheader("Linha do tempo de ativacoes")
    if not filtered_data.empty:
        time_series = (
            filtered_data.dropna(subset=["End date & time"])
            .groupby(filtered_data["End date & time"].dt.date)["Terminal ID"]
            .nunique()
            .rename("Ativacoes")
        )
        st.line_chart(time_series)

with tab_details:
    present_data = filtered_data.rename(columns=COLUMN_DISPLAY_MAP)
    st.dataframe(present_data, use_container_width=True)

    csv_data = present_data.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Baixar CSV filtrado",
        data=csv_data,
        file_name="customizations_filtrado.csv",
        mime="text/csv",
    )

st.markdown("</div>", unsafe_allow_html=True)
