# ============================================
# DASHBOARD ECONÔMICO GLOBAL
# Streamlit + APIs Oficiais
# Início do Projeto (Arquitetura Base)
# ============================================

import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(
    page_title="Dashboard Econômico Global",
    layout="wide"
)

st.title("📊 Dashboard Econômico Global")
st.caption("Dados oficiais | Atualização automática | Projeto de BI Econômico")

# ============================================
# FUNÇÕES DE COLETA DE DADOS
# ============================================

# --- EUA | FRED API ---
def get_fred_series(series_id, api_key):
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json"
    }
    r = requests.get(url, params=params)
    data = r.json()["observations"]

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    return df[["date", "value"]]

# ============================================
# SIDEBAR
# ============================================

st.sidebar.header("⚙️ Configurações")
fred_api_key = st.sidebar.text_input("FRED API Key", type="password")

st.sidebar.markdown("---")
st.sidebar.info("Este Dashboard utiliza apenas fontes oficiais (FRED, World Bank, Eurostat)")

# ============================================
# DASHBOARD | EUA (MÓDULO COMPLETO)
# ============================================

st.subheader("🇺🇸 Estados Unidos")

if fred_api_key:
    col1, col2, col3, col4 = st.columns(4)

    gdp = get_fred_series("GDPC1", fred_api_key)
    cpi = get_fred_series("CPIAUCSL", fred_api_key)
    unrate = get_fred_series("UNRATE", fred_api_key)
    fedfunds = get_fred_series("FEDFUNDS", fred_api_key)

    col1.metric("PIB Real (QoQ)", f"{gdp['value'].iloc[-1]:.2f}%")
    col2.metric("CPI", f"{cpi['value'].iloc[-1]:.2f}")
    col3.metric("Desemprego", f"{unrate['value'].iloc[-1]:.2f}%")
    col4.metric("Fed Funds", f"{fedfunds['value'].iloc[-1]:.2f}%")

    tab1, tab2 = st.tabs(["PIB", "Inflação"])

    with tab1:
        st.line_chart(gdp.set_index("date"))

    with tab2:
        st.line_chart(cpi.set_index("date"))

else:
    st.warning("🔑 Insira sua FRED API Key para carregar os dados dos EUA")

# ============================================
# EUROPA | EUROSTAT (INTEGRAÇÃO)
# ============================================

st.subheader("🇪🇺 Europa")

@st.cache_data

def get_eurostat_gdp():
    url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/namq_10_gdp"
    params = {
        "geo": "EA19",
        "unit": "CP_MEUR",
        "na_item": "B1GQ",
        "time": "2020-2025"
    }
    r = requests.get(url, params=params)
    data = r.json()["value"]
    dates = r.json()["dimension"]["time"]["category"]["index"]

    df = pd.DataFrame({
        "date": list(dates.keys()),
        "value": list(data.values())
    })
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date")

try:
    euro_gdp = get_eurostat_gdp()
    st.metric("PIB Zona do Euro", f"{euro_gdp['value'].iloc[-1]:,.0f}")
    st.line_chart(euro_gdp.set_index("date"))
except:
    st.warning("Erro ao carregar dados do Eurostat")

# ============================================
# CHINA | WORLD BANK (INTEGRAÇÃO)
# ============================================

st.subheader("🇨🇳 China")

@st.cache_data

def get_worldbank_series(indicator):
    url = f"https://api.worldbank.org/v2/country/CHN/indicator/{indicator}?format=json"
    r = requests.get(url)
    data = r.json()[1]

    df = pd.DataFrame(data)
    df = df[["date", "value"]].dropna()
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date")

try:
    china_gdp = get_worldbank_series("NY.GDP.MKTP.KD.ZG")
    st.metric("PIB China (YoY)", f"{china_gdp['value'].iloc[-1]:.2f}%")
    st.line_chart(china_gdp.set_index("date"))
except:
    st.warning("Erro ao carregar dados do World Bank")

# ============================================
# FUNÇÕES DE MÉTRICAS
# ============================================

def calc_yoy(df):
    df = df.copy()
    df["YoY"] = df["value"].pct_change(4) * 100
    return df

# ============================================
# FILTROS GLOBAIS
# ============================================

st.sidebar.header("🔎 Filtros Globais")
periodo = st.sidebar.slider("Período", 2000, datetime.now().year, (2015, datetime.now().year))

# ============================================
# VISÃO GLOBAL COMPARATIVA
# ============================================

st.subheader("🌍 Visão Global – Comparativo")

try:
    gdp_us = calc_yoy(gdp).rename(columns={"YoY": "EUA"}).set_index("date")
    gdp_eu = calc_yoy(euro_gdp).rename(columns={"YoY": "Europa"}).set_index("date")
    gdp_cn = calc_yoy(china_gdp).rename(columns={"YoY": "China"}).set_index("date")

    global_df = gdp_us[["EUA"]].join(gdp_eu[["Europa"]], how="outer").join(gdp_cn[["China"]], how="outer")
    global_df = global_df[str(periodo[0]):str(periodo[1])]

    st.line_chart(global_df)
except:
    st.info("Dados insuficientes para o comparativo global")

# ============================================
# METODOLOGIA E FONTES
# ============================================

st.subheader("📘 Metodologia & Fontes")

st.markdown("""
**Metodologia:**
- Todos os dados são coletados via APIs oficiais.
- Frequências originais são preservadas.
- Métricas YoY calculadas automaticamente.

**Fontes Oficiais:**
- EUA: Federal Reserve (FRED)
- Europa: Eurostat / ECB
- China: World Bank / IMF

**Objetivo do Projeto:**
Criar um Dashboard Econômico Global automatizado, reprodutível e utilizável para análise macroeconômica e apresentações profissionais.
""")

# ============================================
# PUBLICAÇÃO
# ============================================

st.info("🚀 Pronto para publicação no Streamlit Cloud")

# ============================================
# RODAPÉ
# ============================================

st.markdown("---")
st.caption("Projeto em desenvolvimento | Arquitetura profissional de BI Econômico")
