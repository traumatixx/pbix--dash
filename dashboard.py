import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

st.set_page_config(page_title="PBIX Analyzer", layout="wide")

st.title("📊 PBIX Analyzer")

# Generate demo data
@st.cache_data
def generate_data():
    np.random.seed(42)
    n = 500
    data = {
        'Date': pd.date_range('2024-01-01', periods=n, freq='D'),
        'CA': np.random.normal(500000, 100000, n),
        'Benefices': np.random.normal(150000, 30000, n),
        'Clients': np.random.randint(50, 300, n),
        'Risque': np.random.uniform(0, 1, n),
        'Region': np.random.choice(['Casablanca', 'Rabat', 'Tanger', 'Fes'], n),
    }
    data['Benefices'] = data['CA'] * 0.3 + np.random.normal(0, 20000, n)
    return pd.DataFrame(data)

# Sidebar
with st.sidebar:
    st.header("📁 Upload")
    uploaded_file = st.file_uploader("Fichier .pbix", type=["pbix"])
    
    if uploaded_file:
        st.success(f"✅ {uploaded_file.name}")
    else:
        if st.button("Mode Démo"):
            st.session_state['demo'] = True

# Main
if uploaded_file or 'demo' in st.session_state:
    df = generate_data()
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 CA Total", f"{df['CA'].sum()/1e6:.1f} M DH")
    col2.metric("📈 Bénéfices", f"{df['Benefices'].sum()/1e6:.1f} M DH")
    col3.metric("👥 Clients", f"{df['Clients'].sum():,}")
    col4.metric("⚠️ Risque", f"{df['Risque'].mean():.1%}")
    
    # Graph with plotly.graph_objects (not express)
    fig = go.Figure()
    
    # Bar chart
    region_sales = df.groupby('Region')['CA'].sum().reset_index()
    fig.add_trace(go.Bar(
        x=region_sales['Region'],
        y=region_sales['CA'],
        marker_color='#667eea',
        name='CA par Region'
    ))
    
    fig.update_layout(
        title="Chiffre d'Affaires par Région",
        height=400,
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Line chart
    daily_sales = df.groupby('Date')['CA'].sum().reset_index()
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=daily_sales['Date'],
        y=daily_sales['CA'],
        mode='lines',
        line=dict(color='#10b981', width=2),
        name='Tendance CA'
    ))
    fig2.update_layout(title="Evolution du CA", height=400)
    st.plotly_chart(fig2, use_container_width=True)
    
    # Risk analysis
    st.subheader("⚠️ Analyse Risque")
    df['Niveau'] = pd.cut(df['Risque'], bins=[0, 0.3, 0.7, 1], labels=['Faible', 'Moyen', 'Elevé'])
    
    risk_counts = df['Niveau'].value_counts()
    
    cols = st.columns(3)
    colors = ['#10b981', '#f59e0b', '#ef4444']
    for i, (level, count) in enumerate(risk_counts.items()):
        cols[i].metric(f"{level}", count)
    
    # Pie chart with go
    fig3 = go.Figure(data=[go.Pie(
        labels=risk_counts.index,
        values=risk_counts.values,
        marker_colors=colors,
        hole=0.4
    )])
    fig3.update_layout(title="Distribution des Risques", height=400)
    st.plotly_chart(fig3, use_container_width=True)
    
    # Data table
    st.subheader("📋 Données")
    st.dataframe(df.head(100))
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 CSV", csv, "data.csv", "text/csv")

else:
    st.info("👈 Upload fichier .pbix ou clique Mode Démo")
