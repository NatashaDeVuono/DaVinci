import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuração inicial
st.set_page_config(layout="wide", page_title="Hub de Análise Contratual", page_icon="📊")

# Carregar dados
@st.cache_data
def load_data():
    return pd.read_csv('inteligencia_contratual_limpa.csv', parse_dates=['Data_Assinatura', 'Data_Termino'])

df = load_data()

# Sidebar - Filtros
st.sidebar.header("Filtros")
projetos = st.sidebar.multiselect("Projetos", options=df['Projeto'].unique(), default=df['Projeto'].unique())
status = st.sidebar.multiselect("Status", options=df['Status'].unique(), default=df['Status'].unique())
risco = st.sidebar.multiselect("Risco Contratual", options=df['Risco_Contratual'].unique(), default=df['Risco_Contratual'].unique())

# Aplicar filtros
filtered_df = df[
    (df['Projeto'].isin(projetos)) &
    (df['Status'].isin(status)) &
    (df['Risco_Contratual'].isin(risco))
]

# Layout principal
st.title("📊 Hub de Inteligência Contratual")
st.markdown("""
Análise integrada de contratos com foco em Jurimetria, ESG, Compliance e Business Intelligence.
""")

# Métricas principais
st.subheader("Visão Geral")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Contratos", len(filtered_df))
col2.metric("Valor Total (R$)", f"R$ {filtered_df['Valor_Total_R$'].sum():,.2f}")
col3.metric("Média ESG Score", f"{filtered_df['ESG_Score'].mean():.1f}")
col4.metric("Taxa de Compliance", f"{filtered_df['Score_Compliance_%'].mean():.1f}%")

# Abas para diferentes análises
tab1, tab2, tab3, tab4 = st.tabs(["📈 Business Intelligence", "🌱 ESG", "⚖️ Jurimetria", "🔍 Detalhes"])

with tab1:  # Business Intelligence
    st.subheader("Análise de Negócios")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Valor por Projeto
        fig = px.bar(filtered_df.groupby('Projeto')['Valor_Total_R$'].sum().reset_index(), 
                     x='Projeto', y='Valor_Total_R$', title='Valor Total por Projeto (R$)')
        st.plotly_chart(fig, use_container_width=True)
        
        # Contratos por Status
        fig = px.pie(filtered_df, names='Status', title='Distribuição por Status')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Valor por Tipo de Contrato
        fig = px.bar(filtered_df.groupby('Tipo_Contrato')['Valor_Total_R$'].sum().reset_index(), 
                     x='Tipo_Contrato', y='Valor_Total_R$', title='Valor por Tipo de Contrato (R$)')
        st.plotly_chart(fig, use_container_width=True)
        
        # Top Fornecedores
        fig = px.bar(filtered_df.groupby('Fornecedor')['Valor_Total_R$'].sum().reset_index().sort_values('Valor_Total_R$', ascending=False).head(5), 
                     x='Fornecedor', y='Valor_Total_R$', title='Top 5 Fornecedores por Valor (R$)')
        st.plotly_chart(fig, use_container_width=True)

with tab2:  # ESG
    st.subheader("Análise ESG")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribuição ESG Score
        fig = px.histogram(filtered_df, x='ESG_Score', nbins=20, title='Distribuição de ESG Score')
        st.plotly_chart(fig, use_container_width=True)
        
        # ESG por Fornecedor
        fig = px.bar(filtered_df.groupby('Fornecedor')['ESG_Score'].mean().reset_index().sort_values('ESG_Score', ascending=False), 
                     x='Fornecedor', y='ESG_Score', title='Média de ESG Score por Fornecedor')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Correlação ESG-Compliance
        fig = px.scatter(filtered_df, x='ESG_Score', y='Score_Compliance_%', color='Risco_Contratual',
                         title='Relação entre ESG Score e Compliance')
        st.plotly_chart(fig, use_container_width=True)
        
        # Clausulas ESG
        clausulas = filtered_df[['Clausula_Multa', 'Clausula_Confidencialidade', 'Clausula_ESG']].sum().reset_index()
        clausulas.columns = ['Clausula', 'Contagem']
        fig = px.bar(clausulas, x='Clausula', y='Contagem', title='Presença de Cláusulas nos Contratos')
        st.plotly_chart(fig, use_container_width=True)

with tab3:  # Jurimetria
    st.subheader("Análise Jurídica")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Risco Contratual
        fig = px.pie(filtered_df, names='Risco_Contratual', title='Distribuição de Risco Contratual')
        st.plotly_chart(fig, use_container_width=True)
        
        # Pendencias por Projeto
        fig = px.bar(filtered_df.groupby('Projeto')['Pendencias_Abertas'].sum().reset_index(), 
                     x='Projeto', y='Pendencias_Abertas', title='Pendências Abertas por Projeto')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Atrasos
        atrasos_df = filtered_df[filtered_df['Atraso_dias'] > 0]
        if not atrasos_df.empty:
            fig = px.bar(atrasos_df.sort_values('Atraso_dias', ascending=False).head(10), 
                         x='ID_Contrato', y='Atraso_dias', title='Top 10 Contratos com Maior Atraso (dias)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum contrato com atraso nos filtros selecionados")
        
        # Contratos Rescindidos/Inadimplentes
        problemas = filtered_df[filtered_df['Status'].isin(['Rescindido', 'Inadimplente'])]
        if not problemas.empty:
            fig = px.bar(problemas.groupby('Projeto')['ID_Contrato'].count().reset_index(), 
                         x='Projeto', y='ID_Contrato', title='Contratos com Problemas por Projeto')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum contrato com problemas nos filtros selecionados")

with tab4:  # Detalhes
    st.subheader("Detalhes dos Contratos")
    
    # Filtros adicionais
    col1, col2 = st.columns(2)
    with col1:
        sort_by = st.selectbox("Ordenar por", options=['Valor_Total_R$', 'ESG_Score', 'Score_Compliance_%', 'Atraso_dias'])
    with col2:
        sort_order = st.radio("Ordem", options=['Ascendente', 'Descendente'])
    
    # Aplicar ordenação
    ascending = sort_order == 'Ascendente'
    detailed_df = filtered_df.sort_values(sort_by, ascending=ascending)
    
    # Mostrar tabela
    st.dataframe(detailed_df, use_container_width=True)
    
    # Opção para download
    st.download_button(
        label="Baixar dados filtrados",
        data=detailed_df.to_csv(index=False).encode('utf-8'),
        file_name='contratos_filtrados.csv',
        mime='text/csv'
    )

# Análise temporal
st.subheader("Análise Temporal")
col1, col2 = st.columns(2)

with col1:
    # Contratos ao longo do tempo
    timeline = filtered_df.groupby(filtered_df['Data_Assinatura'].dt.to_period('M'))['ID_Contrato'].count().reset_index()
    timeline['Data_Assinatura'] = timeline['Data_Assinatura'].astype(str)
    fig = px.line(timeline, x='Data_Assinatura', y='ID_Contrato', title='Contratos Assinados ao Longo do Tempo')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Duração dos contratos
    filtered_df['Duracao_dias'] = (filtered_df['Data_Termino'] - filtered_df['Data_Assinatura']).dt.days
    fig = px.box(filtered_df, x='Tipo_Contrato', y='Duracao_dias', title='Duração dos Contratos por Tipo (dias)')
    st.plotly_chart(fig, use_container_width=True)

# Análise de Stakeholders Críticos
st.subheader("Stakeholders Críticos")
stakeholders_df = filtered_df[filtered_df['Stakeholder_Critico'] == True]
if not stakeholders_df.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(stakeholders_df.groupby('Projeto')['ID_Contrato'].count().reset_index(), 
                     x='Projeto', y='ID_Contrato', title='Stakeholders Críticos por Projeto')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(stakeholders_df.groupby('Fornecedor')['Valor_Total_R$'].sum().reset_index(), 
                     x='Fornecedor', y='Valor_Total_R$', title='Valor em Stakeholders Críticos por Fornecedor (R$)')
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Nenhum stakeholder crítico nos filtros selecionados")
