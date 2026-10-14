"""
Dashboard Streamlit — Temperaturas IoT.

Uso:
    streamlit run src/dashboard.py
"""
import pandas as pd
import plotly.express as px
import streamlit as st

from config import get_engine

st.set_page_config(page_title="Dashboard de Temperaturas IoT", layout="wide")

engine = get_engine()


@st.cache_data(ttl=300)
def load_data(view_name: str) -> pd.DataFrame:
    """Carrega os dados de uma view do PostgreSQL."""
    allowed = {"avg_temp_por_dispositivo", "leituras_por_hora", "temp_max_min_por_dia"}
    if view_name not in allowed:  # evita SQL injection em nome de view
        raise ValueError(f"View não permitida: {view_name}")
    return pd.read_sql(f"SELECT * FROM {view_name}", engine)


st.title("Dashboard de Temperaturas IoT")
st.caption("Pipeline: CSV (Kaggle) → Python/pandas → PostgreSQL (Docker) → Streamlit")

try:
    df_avg_temp = load_data("avg_temp_por_dispositivo")
    df_leituras_hora = load_data("leituras_por_hora")
    df_temp_max_min = load_data("temp_max_min_por_dia")
except Exception as exc:  # banco fora do ar ou sem dados
    st.error(
        "Não foi possível ler as views do PostgreSQL. Verifique se o contêiner "
        "está ativo e se `python src/ingest.py` foi executado."
    )
    st.exception(exc)
    st.stop()

# Indicadores gerais
col1, col2, col3 = st.columns(3)
col1.metric("Total de leituras", f"{int(df_avg_temp['total_leituras'].sum()):,}")
col2.metric("Temperatura máxima (°C)", f"{df_temp_max_min['temp_max'].max():.1f}")
col3.metric("Temperatura mínima (°C)", f"{df_temp_max_min['temp_min'].min():.1f}")

# Gráfico 1: Média de temperatura por dispositivo
st.header("Média de Temperatura por Dispositivo")
fig1 = px.bar(
    df_avg_temp, x="device_id", y="avg_temp",
    labels={"device_id": "Dispositivo", "avg_temp": "Temperatura média (°C)"},
)
st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: Contagem de leituras por hora
st.header("Leituras por Hora do Dia")
fig2 = px.line(
    df_leituras_hora, x="hora", y="contagem", markers=True,
    labels={"hora": "Hora do dia", "contagem": "Nº de leituras"},
)
st.plotly_chart(fig2, use_container_width=True)

# Gráfico 3: Temperaturas máximas e mínimas por dia
st.header("Temperaturas Máximas e Mínimas por Dia")
fig3 = px.line(
    df_temp_max_min, x="data", y=["temp_max", "temp_min"],
    labels={"data": "Data", "value": "Temperatura (°C)", "variable": "Medida"},
)
st.plotly_chart(fig3, use_container_width=True)

with st.expander("Ver dados das views"):
    st.subheader("avg_temp_por_dispositivo")
    st.dataframe(df_avg_temp)
    st.subheader("leituras_por_hora")
    st.dataframe(df_leituras_hora)
    st.subheader("temp_max_min_por_dia")
    st.dataframe(df_temp_max_min)
