import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- Configuração Inicial ---
st.set_page_config(layout="wide", page_title="Hub Contratos", page_icon="📊")

# --- Carregamento de Dados À PROVA DE FALHAS ---
@st.cache_data
def load_data():
    try:
        # Tenta carregar do arquivo local (mesma pasta)
        df = pd.read_csv('inteligencia_contratual_limpa.csv', 
                        parse_dates=['Data_Assinatura', 'Data_Termino'])
        st.success("Dados carregados localmente!")
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()  # Retorna dataframe vazio para não quebrar o app

df = load_data()

# --- Verifica se os dados foram carregados ---
if df.empty:
    st.stop()  # Para a execução se não houver dados

# --- Restante do Seu Código (como anteriormente) ---
st.title("📊 Análise de Contratos")
# ... (cole aqui o resto do seu código original de visualizações)
