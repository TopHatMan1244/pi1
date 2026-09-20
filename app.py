import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Operacional Ferroviário",
    page_icon="🚆",
    layout="wide",
)

def load_data():
    data = pd.read_csv("C:\\Users\\adils\\PyProject\\Atividade_01\\dataset_sinalizacao_ferroviaria.csv")
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    return data

df = load_data()

st.title("🚆 Dashboard Operacional Ferroviário")
st.caption("Exploração dos dados de circulação, sinalização, headway e ocupação de circuito.")

# Sidebar filters
st.sidebar.header("Filtros")

linhas = st.sidebar.multiselect(
    "Linha",
    options=sorted(df["linha"].dropna().unique()),
    default=sorted(df["linha"].dropna().unique()),
)

sinalizacoes = st.sidebar.multiselect(
    "Tipo de sinalização",
    options=sorted(df["tipo_sinalizacao"].dropna().unique()),
    default=sorted(df["tipo_sinalizacao"].dropna().unique()),
)

aspectos = st.sidebar.multiselect(
    "Aspecto do sinal",
    options=sorted(df["aspecto_sinal"].dropna().unique()),
    default=sorted(df["aspecto_sinal"].dropna().unique()),
)

filtered = df[
    df["linha"].isin(linhas)
    & df["tipo_sinalizacao"].isin(sinalizacoes)
    & df["aspecto_sinal"].isin(aspectos)
].copy()

if filtered.empty:
    st.warning("Nenhum registro corresponde aos filtros selecionados.")
    st.stop()

# KPI cards
c1, c2, c3, c4 = st.columns(4)
c1.metric("Registros", f"{len(filtered):,}".replace(",", "."))
c2.metric("Trens", f"{filtered['id_trem'].nunique():,}".replace(",", "."))
c3.metric("Headway médio", f"{filtered['headway_seg'].mean():.1f} s")
c4.metric("Ocupação média", f"{filtered['tempo_ocupacao_circuito_seg'].mean():.1f} s")

st.divider()

# Graph 1: average headway over time
time_series = (
    filtered.set_index("timestamp")
    .resample("15min")["headway_seg"]
    .mean()
    .reset_index()
)

fig1 = px.line(
    time_series,
    x="timestamp",
    y="headway_seg",
    markers=True,
    title="Headway médio ao longo do tempo",
    labels={
        "timestamp": "Horário",
        "headway_seg": "Headway médio (s)",
    },
)
fig1.update_layout(hovermode="x unified")

# Graph 2: average occupation by block
block_summary = (
    filtered.groupby("id_bloco", as_index=False)
    .agg(
        ocupacao_media=("tempo_ocupacao_circuito_seg", "mean"),
        registros=("id_bloco", "size"),
    )
    .sort_values("ocupacao_media", ascending=False)
)

fig2 = px.bar(
    block_summary,
    x="id_bloco",
    y="ocupacao_media",
    title="Tempo médio de ocupação por bloco",
    labels={
        "id_bloco": "Bloco",
        "ocupacao_media": "Ocupação média (s)",
    },
    text_auto=".1f",
)
fig2.update_layout(xaxis_tickangle=-45)

left, right = st.columns(2)
with left:
    st.plotly_chart(fig1, use_container_width=True)
with right:
    st.plotly_chart(fig2, use_container_width=True)

# Optional third graph for signal aspect distribution
aspect_summary = (
    filtered["aspecto_sinal"]
    .value_counts()
    .rename_axis("aspecto_sinal")
    .reset_index(name="quantidade")
)

fig3 = px.pie(
    aspect_summary,
    names="aspecto_sinal",
    values="quantidade",
    title="Distribuição dos aspectos de sinal",
    hole=0.35,
)
st.plotly_chart(fig3, use_container_width=True)

with st.expander("Ver dados filtrados"):
    st.dataframe(filtered, use_container_width=True)

st.caption(
    f"Período: {filtered['timestamp'].min():%d/%m/%Y %H:%M} "
    f"até {filtered['timestamp'].max():%d/%m/%Y %H:%M}."
)