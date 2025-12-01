import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="B2B Attribution AI", layout="wide")

# --- 1. GERAÇÃO DE DADOS FICTÍCIOS (SIMULAÇÃO B2B) ---
@st.cache_data
def generate_b2b_data(n_leads=1000):
    np.random.seed(42)
    
    # Canais de Marketing
    channels = ['LinkedIn Ads', 'Webinar', 'Email Marketing', 'Google Search', 'Eventos Offline']
    
    data = []
    
    for i in range(n_leads):
        # Simula interações (1 = interagiu, 0 = não interagiu)
        linkedin = np.random.choice([0, 1], p=[0.6, 0.4])
        webinar = np.random.choice([0, 1], p=[0.7, 0.3])
        email = np.random.choice([0, 1], p=[0.5, 0.5])
        search = np.random.choice([0, 1], p=[0.8, 0.2])
        evento = np.random.choice([0, 1], p=[0.9, 0.1])
        
        # Lógica de negócio: Webinars e Eventos aumentam muito a chance de conversão
        score = (linkedin * 1) + (webinar * 3) + (email * 1.5) + (search * 0.5) + (evento * 4) + np.random.normal(0, 1)
        
        # Probabilidade de virar cliente (Sigmoid function simulada)
        prob = 1 / (1 + np.exp(-(score - 3)))
        converted = 1 if prob > 0.5 else 0
        
        # Valor do Contrato (ACV) - Só existe se converteu
        deal_value = np.round(np.random.normal(15000, 3000), 2) if converted else 0
        
        # Define o "Último Clique" para comparação
        interactions = []
        if linkedin: interactions.append('LinkedIn Ads')
        if webinar: interactions.append('Webinar')
        if email: interactions.append('Email Marketing')
        if search: interactions.append('Google Search')
        if evento: interactions.append('Eventos Offline')
        
        last_touch = interactions[-1] if interactions else 'Direct'
        
        data.append({
            'Lead_ID': i,
            'LinkedIn': linkedin,
            'Webinar': webinar,
            'Email': email,
            'Google_Search': search,
            'Eventos': evento,
            'Score_Interno': score,
            'Converted': converted,
            'Deal_Value': deal_value,
            'Last_Touch_Channel': last_touch
        })
        
    return pd.DataFrame(data)

df = generate_b2b_data()

# --- 2. TREINAMENTO DO MODELO DE IA ---
# Vamos usar os canais para prever a conversão
X = df[['LinkedIn', 'Webinar', 'Email', 'Google_Search', 'Eventos']]
y = df['Converted']

model = LogisticRegression()
model.fit(X, y)

# Coeficientes do modelo (Impacto de cada canal)
feature_importance = pd.DataFrame({
    'Canal': X.columns,
    'Peso_IA': model.coef_[0]
}).sort_values(by='Peso_IA', ascending=False)

# --- INTERFACE DO APLICATIVO ---

# Cabeçalho
st.title("🤖 B2B Pipeline Predictor & Attribution")
st.markdown("""
Este aplicativo demonstra o uso de **Machine Learning** para superar modelos de atribuição baseados apenas no último clique.
Simulando um cenário **SaaS B2B**, analisamos quais touchpoints realmente geram receita.
""")

st.divider()

# Colunas principais
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Comparativo de Modelos: Last Touch vs. Influência Real (IA)")
    
    # 1. Dados Last Touch
    last_touch_data = df[df['Converted'] == 1]['Last_Touch_Channel'].value_counts().reset_index()
    last_touch_data.columns = ['Canal', 'Conversões (Last Touch)']
    
    # 2. Dados Peso IA (Normalizando para escala comparável visualmente)
    # Multiplicamos o peso pelo total de conversões para ter uma ordem de grandeza similar no gráfico
    total_conversions = df['Converted'].sum()
    feature_importance['Conversões Estimadas (IA)'] = (feature_importance['Peso_IA'] / feature_importance['Peso_IA'].sum()) * total_conversions
    
    # Merge para gráfico
    comparison = pd.merge(last_touch_data, feature_importance[['Canal', 'Conversões Estimadas (IA)']], on='Canal', how='outer').fillna(0)
    
    # Transformar para formato longo (tidy) para o Plotly
    comparison_melted = comparison.melt(id_vars='Canal', var_name='Modelo', value_name='Volume Atribuído')
    
    fig = px.bar(comparison_melted, x='Canal', y='Volume Atribuído', color='Modelo', barmode='group',
                 color_discrete_map={'Conversões (Last Touch)': '#d3d3d3', 'Conversões Estimadas (IA)': '#00CC96'})
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("""
    **Insight Gerado:** Note como o modelo *Last Click* (cinza) supervaloriza o 'Email Marketing' e 'Google Search'. 
    O modelo de IA (verde) revela que **Webinars** e **Eventos** são os verdadeiros impulsionadores de decisão, 
    mesmo que a venda não seja fechada imediatamente neles.
    """)

with col2:
    st.subheader("🔮 Simulador de Pipeline (Lead Scoring)")
    st.write("Configure a jornada de um lead fictício para prever o fechamento.")
    
    # Inputs do Simulador
    input_linkedin = st.checkbox("Viu anúncio no LinkedIn?", value=True)
    input_webinar = st.checkbox("Assistiu ao Webinar?", value=False)
    input_email = st.checkbox("Abriu sequência de E-mails?", value=True)
    input_search = st.checkbox("Pesquisou no Google?", value=False)
    input_evento = st.checkbox("Participou de Evento Presencial?", value=False)
    
    # Botão de Previsão
    if st.button("Calcular Probabilidade de Venda"):
        # Prepara input
        input_data = np.array([[input_linkedin, input_webinar, input_email, input_search, input_evento]])
        
        # Predição
        probabilidade = model.predict_proba(input_data)[0][1] # Pega a prob de ser 1 (Venda)
        ticket_medio = df[df['Converted']==1]['Deal_Value'].mean()
        receita_esperada = probabilidade * ticket_medio
        
        # Exibição dos Resultados (Metrics)
        st.metric(label="Probabilidade de Fechamento (Win Rate)", value=f"{probabilidade:.1%}")
        st.metric(label="Receita Esperada (Pipeline Weighted)", value=f"R$ {receita_esperada:,.2f}")
        
        if probabilidade > 0.6:
            st.success("🚀 **Lead Quente (SQL):** Prioridade Alta para Vendas!")
        elif probabilidade > 0.3:
            st.warning("⚠️ **Lead em Nutrição (MQL):** Enviar mais conteúdos.")
        else:
            st.error("❄️ **Lead Frio:** Manter em automação básica.")

# --- DADOS BRUTOS (Opcional, para mostrar transparência) ---
with st.expander("Ver amostra dos dados gerados (Raw Data)"):
    st.dataframe(df.head(20))
