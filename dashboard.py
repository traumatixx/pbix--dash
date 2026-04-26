import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="PBIX Analyzer Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS STYLING ====================
st.markdown("""
<style>
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    
    /* Card styling */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 1rem;
    }
    
    /* Upload box */
    .upload-box {
        border: 2px dashed #667eea;
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        background: rgba(102, 126, 234, 0.05);
        margin-bottom: 2rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 10px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ==================== FUNCTIONS ====================
@st.cache_data
def generate_demo_data():
    """Generate demo data for testing"""
    np.random.seed(42)
    n = 500
    
    dates = pd.date_range('2024-01-01', periods=n, freq='D')
    
    data = {
        'Date': dates,
        'CA_MAD': np.random.normal(500000, 100000, n),
        'Benefices_MAD': np.random.normal(150000, 30000, n),
        'Nbre_Clients': np.random.randint(50, 300, n),
        'Taux_Risque': np.random.uniform(0, 1, n),
        'Satisfaction': np.random.uniform(0, 10, n),
        'Region': np.random.choice(['Casablanca', 'Rabat', 'Tanger', 'Fès', 'Marrakech'], n),
        'Produit': np.random.choice(['Produit A', 'Produit B', 'Produit C'], n)
    }
    
    # Add correlations
    data['Benefices_MAD'] = data['CA_MAD'] * 0.3 + np.random.normal(0, 20000, n)
    data['Taux_Risque'] = 1 / (1 + np.exp(-(data['CA_MAD'] - 500000) / 100000))
    
    df = pd.DataFrame(data)
    df['Niveau_Risque'] = pd.cut(df['Taux_Risque'], bins=[0, 0.3, 0.7, 1], 
                                  labels=['🟢 Faible', '🟡 Moyen', '🔴 Élevé'])
    return df

# ==================== HEADER ====================
st.markdown("""
<div class="main-header">
    <h1>📊 PBIX Analyzer Pro</h1>
    <p>Analyse avancée des fichiers Power BI</p>
</div>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("### 📁 Upload Section")
    st.markdown("---")
    
    uploaded_file = st.file_uploader(
        "Choisissez votre fichier .pbix",
        type=['pbix'],
        help="Upload your Power BI file"
    )
    
    if uploaded_file:
        st.success(f"✅ {uploaded_file.name}")
        st.session_state['file_uploaded'] = True
    else:
        st.info("💡 Upload un fichier .pbix ou utilise Mode Démo")
        
        if st.button("🎯 Mode Démo", use_container_width=True):
            st.session_state['demo_mode'] = True
    
    st.markdown("---")
    st.markdown("### 📊 Features")
    st.markdown("""
    - 📈 KPIs Interactifs
    - ⚠️ Analyse Risque
    - 📊 Graphiques Dynamiques
    - 🎯 Filtres Avancés
    - 💾 Export CSV
    """)

# ==================== MAIN CONTENT ====================
if 'file_uploaded' in st.session_state or 'demo_mode' in st.session_state:
    
    with st.spinner("📊 Chargement des données..."):
        df = generate_demo_data()
    
    if 'file_uploaded' in st.session_state:
        st.success(f"✅ Analyse du fichier terminée!")
    else:
        st.info("🎮 Mode Démo - Données générées pour illustration")
    
    # ==================== KPIS ====================
    st.markdown("### 🎯 Indicateurs Clés")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ca_total = df['CA_MAD'].sum() / 1e6
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰 CA Total</h3>
            <h2 style="color: #667eea;">{ca_total:.1f} M DH</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        benef_total = df['Benefices_MAD'].sum() / 1e6
        st.markdown(f"""
        <div class="metric-card">
            <h3>📈 Bénéfices</h3>
            <h2 style="color: #10b981;">{benef_total:.1f} M DH</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        clients_total = df['Nbre_Clients'].sum()
        st.markdown(f"""
        <div class="metric-card">
            <h3>👥 Clients</h3>
            <h2 style="color: #f59e0b;">{clients_total:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        risque_moyen = df['Taux_Risque'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <h3>⚠️ Risque Global</h3>
            <h2 style="color: #ef4444;">{risque_moyen:.1%}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # ==================== TABS ====================
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard", 
        "📈 Analyses", 
        "⚠️ Analyse Risque",
        "📋 Données"
    ])
    
    # ==================== TAB 1: DASHBOARD ====================
    with tab1:
        st.markdown("### 🔍 Filtres")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            regions = st.multiselect("Régions", df['Region'].unique(), default=df['Region'].unique()[:2])
        with col_f2:
            risque_filter = st.select_slider("Niveau Risque", ['Tous', '🟢 Faible', '🟡 Moyen', '🔴 Élevé'])
        
        df_filtered = df.copy()
        if regions:
            df_filtered = df_filtered[df_filtered['Region'].isin(regions)]
        if risque_filter != 'Tous':
            df_filtered = df_filtered[df_filtered['Niveau_Risque'] == risque_filter]
        
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.markdown("#### Ventes par Région")
            region_sales = df_filtered.groupby('Region')['CA_MAD'].sum().reset_index()
            fig1 = px.bar(region_sales, x='Region', y='CA_MAD', 
                         title="",
                         color='CA_MAD',
                         color_continuous_scale='Viridis')
            st.plotly_chart(fig1, use_container_width=True)
        
        with col_g2:
            st.markdown("#### Tendance des Ventes")
            daily_sales = df_filtered.groupby('Date')['CA_MAD'].sum().reset_index()
            fig2 = px.line(daily_sales, x='Date', y='CA_MAD', title="")
            st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("#### Relation CA vs Bénéfices")
        fig3 = px.scatter(df_filtered, x='CA_MAD', y='Benefices_MAD',
                         color='Region', size='Nbre_Clients',
                         title="Corrélation Chiffre d'Affaires - Bénéfices",
                         trendline="ols")
        st.plotly_chart(fig3, use_container_width=True)
    
    # ==================== TAB 2: ANALYSES ====================
    with tab2:
        st.markdown("### 📊 Analyses Statistiques")
        
        col_a1, col_a2 = st.columns(2)
        
        with col_a1:
            metric = st.selectbox("Variable à analyser", 
                                 ['CA_MAD', 'Benefices_MAD', 'Nbre_Clients', 'Satisfaction'])
            fig_hist = px.histogram(df, x=metric, marginal='box',
                                   title=f"Distribution - {metric}",
                                   color_discrete_sequence=['#667eea'])
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col_a2:
            fig_box = px.box(df, x='Region', y='CA_MAD', 
                            title="CA par Région",
                            color='Region')
            st.plotly_chart(fig_box, use_container_width=True)
        
        st.markdown("#### Matrice de Corrélation")
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        corr_matrix = df[numeric_cols].corr()
        fig_heat = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                             title="Corrélations entre variables",
                             color_continuous_scale='RdBu')
        st.plotly_chart(fig_heat, use_container_width=True)
    
    # ==================== TAB 3: ANALYSE RISQUE ====================
    with tab3:
        st.markdown("### ⚠️ Analyse de Risque")
        
        col_r1, col_r2, col_r3 = st.columns(3)
        
        risk_counts = df['Niveau_Risque'].value_counts()
        
        with col_r1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🔴 Risque Élevé</h3>
                <h2 style="color: #ef4444;">{risk_counts.get('🔴 Élevé', 0)}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col_r2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🟡 Risque Moyen</h3>
                <h2 style="color: #f59e0b;">{risk_counts.get('🟡 Moyen', 0)}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col_r3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🟢 Risque Faible</h3>
                <h2 style="color: #10b981;">{risk_counts.get('🟢 Faible', 0)}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        col_rg1, col_rg2 = st.columns(2)
        
        with col_rg1:
            fig_pie = px.pie(values=risk_counts.values, names=risk_counts.index,
                            title="Distribution du Risque",
                            color_discrete_sequence=['#10b981', '#f59e0b', '#ef4444'])
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col_rg2:
            risk_region = df.groupby('Region')['Taux_Risque'].mean().reset_index()
            fig_risk = px.bar(risk_region, x='Region', y='Taux_Risque',
                             title="Risque Moyen par Région",
                             color='Taux_Risque',
                             color_continuous_scale='RdYlGn_r')
            st.plotly_chart(fig_risk, use_container_width=True)
        
        st.markdown("#### Détail Risque par Produit")
        risk_product = df.groupby('Produit').agg({
            'Taux_Risque': 'mean',
            'CA_MAD': 'sum',
            'Nbre_Clients': 'sum'
        }).round(2)
        risk_product.columns = ['Risque Moyen', 'CA Total (M DH)', 'Nb Clients']
        risk_product['Risque Moyen'] = risk_product['Risque Moyen'].apply(lambda x: f"{x:.1%}")
        risk_product['CA Total (M DH)'] = risk_product['CA Total (M DH)'] / 1e6
        st.dataframe(risk_product, use_container_width=True)
    
    # ==================== TAB 4: DONNÉES ====================
    with tab4:
        st.markdown("### 📋 Données Brutes")
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger CSV",
            data=csv,
            file_name=f"pbix_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        st.dataframe(df.head(100), use_container_width=True)
        
        with st.expander("📊 Statistiques Descriptives"):
            st.dataframe(df.describe(), use_container_width=True)

else:
    # Page d'accueil
    st.markdown("""
    <div style="text-align: center; padding: 3rem;">
        <h1 style="font-size: 3rem;">📊</h1>
        <h2>Bienvenue sur PBIX Analyzer Pro</h2>
        <p style="font-size: 1.2rem; margin-top: 1rem;">
            Upload votre fichier .pbix pour commencer l'analyse
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**📈 KPIs**\n\nVisualisation des indicateurs clés")
    with col2:
        st.markdown("**⚠️ Risque**\n\nAnalyse avancée des risques")
    with col3:
        st.markdown("**📊 Graphiques**\n\nVisualisations interactives")
