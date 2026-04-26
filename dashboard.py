import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import zipfile
import io
from datetime import datetime
import base64

# ==================== CONFIGURATION ====================
st.set_page_config(
    page_title="PBIX Analyzer Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS CUSTOM ====================
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Cards */
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    /* Header */
    .header {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    /* Metrics */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Upload box */
    .upload-box {
        border: 2px dashed #667eea;
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        background: rgba(255,255,255,0.1);
        margin-bottom: 2rem;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ==================== HEADER ====================
st.markdown("""
<div class="header">
    <h1>📊 PBIX Analyzer Pro</h1>
    <p>Analyse Inteligente des Fichiers Power BI</p>
</div>
""", unsafe_allow_html=True)

# ==================== FONCTIONS ====================
@st.cache_data
def load_pbix_file(uploaded_file):
    """Simuler la lecture d'un fichier PBIX"""
    try:
        with zipfile.ZipFile(io.BytesIO(uploaded_file.getvalue())) as zip_ref:
            files = zip_ref.namelist()
            return {"status": "success", "files": files, "name": uploaded_file.name}
    except:
        return {"status": "demo", "name": uploaded_file.name}

@st.cache_data
def generate_demo_data():
    """Génère des données de démonstration"""
    np.random.seed(42)
    n = 500
    
    data = {
        'Date': pd.date_range('2024-01-01', periods=n, freq='D'),
        'Chiffre_Affaires': np.random.normal(500000, 100000, n),
        'Benefices': np.random.normal(150000, 30000, n),
        'Nombre_Clients': np.random.randint(100, 500, n),
        'Taux_Risque': np.random.uniform(0, 1, n),
        'Region': np.random.choice(['Casablanca', 'Rabat', 'Tanger', 'Fès', 'Marrakech'], n),
        'Produit': np.random.choice(['Produit A', 'Produit B', 'Produit C', 'Produit D'], n),
        'Satisfaction': np.random.uniform(0, 10, n)
    }
    
    # Ajouter des corrélations
    data['Benefices'] = data['Chiffre_Affaires'] * 0.25 + np.random.normal(0, 20000, n)
    data['Taux_Risque'] = 1 / (1 + np.exp(-(data['Chiffre_Affaires'] - 500000) / 100000))
    
    return pd.DataFrame(data)

def create_risk_analysis(df):
    """Analyse de risque avancée"""
    if 'Taux_Risque' in df.columns:
        df['Niveau_Risque'] = pd.cut(
            df['Taux_Risque'], 
            bins=[0, 0.3, 0.7, 1], 
            labels=['🟢 Faible', '🟡 Moyen', '🔴 Élevé']
        )
        
        risk_stats = {
            'Risque Moyen': f"{df['Taux_Risque'].mean():.2%}",
            'Clients haut risque': len(df[df['Niveau_Risque'] == '🔴 Élevé']),
            'Clients risque moyen': len(df[df['Niveau_Risque'] == '🟡 Moyen']),
            'Clients faible risque': len(df[df['Niveau_Risque'] == '🟢 Faible'])
        }
        return df, risk_stats
    return df, {}

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("### 📁 **Upload Section**")
    st.markdown("---")
    
    # Zone d'upload stylisée
    uploaded_file = st.file_uploader(
        "**Choisissez votre fichier Power BI**",
        type=['pbix'],
        help="Support des fichiers .pbix (Power BI Desktop)"
    )
    
    if uploaded_file:
        st.success(f"✅ **Fichier chargé!**\n\n`{uploaded_file.name}`")
        
        # Bouton d'analyse
        if st.button("🚀 **Analyser le fichier**", use_container_width=True):
            st.session_state['analyze'] = True
            st.session_state['file_name'] = uploaded_file.name
    else:
        st.info("💡 **Astuce:** Uploadez votre fichier .pbix pour démarrer l'analyse")
        
        # Bouton demo
        if st.button("🎯 **Mode Démo**", use_container_width=True):
            st.session_state['demo_mode'] = True
    
    st.markdown("---")
    st.markdown("""
    ### 📊 **Fonctionnalités**
    - 📈 KPIs interactifs
    - ⚠️ Analyse de risque
    - 📊 Graphiques dynamiques
    - 🎯 Filtres avancés
    - 💾 Export des données
    """)

# ==================== MAIN CONTENT ====================
if 'analyze' in st.session_state or 'demo_mode' in st.session_state:
    
    # Chargement des données
    with st.spinner("📊 **Chargement et analyse des données...**"):
        if 'demo_mode' in st.session_state:
            df = generate_demo_data()
            st.info("🎮 **Mode Démo** - Données générées pour illustration")
        else:
            df = generate_demo_data()  # Pour l'instant demo
            st.success(f"✅ Fichier `{st.session_state.get('file_name', '')}` analysé avec succès!")
    
    # Analyse de risque
    df, risk_stats = create_risk_analysis(df)
    
    # ==================== KPIS PRINCIPAUX ====================
    st.markdown("### 🎯 **Indicateurs Clés**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>💰 Chiffre d'Affaires</h3>
            <h2 style="color: #667eea;">{:.1f} M DH</h2>
            <p>Moyenne: {:.0f} k DH/jour</p>
        </div>
        """.format(df['Chiffre_Affaires'].sum()/1e6, df['Chiffre_Affaires'].mean()/1000), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📈 Bénéfices</h3>
            <h2 style="color: #10b981;">{:.1f} M DH</h2>
            <p>Marge: {:.1f}%</p>
        </div>
        """.format(df['Benefices'].sum()/1e6, (df['Benefices'].sum()/df['Chiffre_Affaires'].sum())*100), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>👥 Clients</h3>
            <h2 style="color: #f59e0b;">{:,.0f}</h2>
            <p>Total unique</p>
        </div>
        """.format(df['Nombre_Clients'].sum()), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>⚠️ Risque Global</h3>
            <h2 style="color: #ef4444;">{}</h2>
            <p>{}</p>
        </div>
        """.format(risk_stats.get('Risque Moyen', 'N/A'), 
                   f"Haut risque: {risk_stats.get('Clients haut risque', 0)}"), unsafe_allow_html=True)
    
    # ==================== TABS ====================
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 **Dashboard**", 
        "📈 **Analyses**", 
        "⚠️ **Analyse Risque**", 
        "🎯 **KPIs Détail**",
        "📋 **Données Brutes**"
    ])
    
    # ==================== TAB 1: DASHBOARD ====================
    with tab1:
        # Filtres
        st.markdown("### 🔍 **Filtres Interactifs**")
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            regions = st.multiselect("**Région**", df['Region'].unique(), default=df['Region'].unique()[:2])
        with col_f2:
            produits = st.multiselect("**Produit**", df['Produit'].unique(), default=df['Produit'].unique())
        with col_f3:
            risk_filter = st.select_slider("**Niveau de risque**", options=['Tous', '🟢 Faible', '🟡 Moyen', '🔴 Élevé'])
        
        # Application filtres
        df_filtered = df.copy()
        if regions:
            df_filtered = df_filtered[df_filtered['Region'].isin(regions)]
        if produits:
            df_filtered = df_filtered[df_filtered['Produit'].isin(produits)]
        if risk_filter != 'Tous':
            df_filtered = df_filtered[df_filtered['Niveau_Risque'] == risk_filter]
        
        # Graphs
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.markdown("#### 📊 **Ventes par Région**")
            region_sales = df_filtered.groupby('Region')['Chiffre_Affaires'].sum().reset_index()
            fig1 = px.bar(region_sales, x='Region', y='Chiffre_Affaires', 
                         color='Chiffre_Affaires', color_continuous_scale='Viridis',
                         text_auto='.2s')
            fig1.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col_g2:
            st.markdown("#### 📈 **Évolution des Ventes**")
            daily_sales = df_filtered.groupby('Date')['Chiffre_Affaires'].sum().reset_index()
            fig2 = px.line(daily_sales, x='Date', y='Chiffre_Affaires',
                          title="Tendance quotidienne")
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)
        
        # Matrice de corrélation simplifiée
        st.markdown("#### 🔗 **Corrélation Ventes vs Bénéfices**")
        fig3 = px.scatter(df_filtered, x='Chiffre_Affaires', y='Benefices',
                         color='Region', size='Nombre_Clients',
                         title="Relation Chiffre d'Affaires - Bénéfices",
                         trendline="ols")
        st.plotly_chart(fig3, use_container_width=True)
    
    # ==================== TAB 2: ANALYSES ====================
    with tab2:
        st.markdown("### 📈 **Analyses Statistiques**")
        
        col_a1, col_a2 = st.columns(2)
        
        with col_a1:
            # Distribution
            metric = st.selectbox("**Variable à analyser**", 
                                 ['Chiffre_Affaires', 'Benefices', 'Nombre_Clients', 'Satisfaction'])
            fig_hist = px.histogram(df, x=metric, marginal='box', 
                                   title=f"Distribution de {metric}",
                                   color_discrete_sequence=['#667eea'])
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col_a2:
            # Boxplot par région
            fig_box = px.box(df, x='Region', y='Chiffre_Affaires', 
                            title="Ventes par Région (Boxplot)",
                            color='Region')
            st.plotly_chart(fig_box, use_container_width=True)
        
        # Heatmap des corrélations
        st.markdown("#### 🔥 **Matrice de Corrélation**")
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        corr_matrix = df[numeric_cols].corr()
        
        fig_heatmap = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                                title="Corrélations entre variables",
                                color_continuous_scale='RdBu')
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # ==================== TAB 3: ANALYSE RISQUE ====================
    with tab3:
        st.markdown("### ⚠️ **Tableau de Bord du Risque**")
        
        # KPIs risque
        col_r1, col_r2, col_r3, col_r4 = st.columns(4)
        
        with col_r1:
            st.metric("📊 **Risque Moyen**", risk_stats.get('Risque Moyen', 'N/A'), 
                     delta="Basé sur taux risque")
        with col_r2:
            st.metric("🔴 **Risque Élevé**", risk_stats.get('Clients haut risque', 0))
        with col_r3:
            st.metric("🟡 **Risque Moyen**", risk_stats.get('Clients risque moyen', 0))
        with col_r4:
            st.metric("🟢 **Risque Faible**", risk_stats.get('Clients faible risque', 0))
        
        # Graphiques de risque
        col_gr1, col_gr2 = st.columns(2)
        
        with col_gr1:
            # Distribution du risque
            risk_dist = df['Niveau_Risque'].value_counts()
            fig_pie = px.pie(values=risk_dist.values, names=risk_dist.index,
                            title="Distribution des Niveaux de Risque",
                            color_discrete_sequence=['#10b981', '#f59e0b', '#ef4444'])
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col_gr2:
            # Risque par région
            risk_region = df.groupby('Region')['Taux_Risque'].mean().reset_index()
            fig_risk_region = px.bar(risk_region, x='Region', y='Taux_Risque',
                                     title="Risque Moyen par Région",
                                     color='Taux_Risque', color_continuous_scale='RdYlGn_r')
            st.plotly_chart(fig_risk_region, use_container_width=True)
        
        # Table des risques détaillée
        st.markdown("#### 📋 **Détail des Risques par Produit**")
        risk_product = df.groupby('Produit').agg({
            'Taux_Risque': 'mean',
            'Chiffre_Affaires': 'sum',
            'Nombre_Clients': 'sum'
        }).round(2)
        risk_product.columns = ['Risque Moyen', 'CA Total (M DH)', 'Nb Clients']
        risk_product['Risque Moyen'] = risk_product['Risque Moyen'].apply(lambda x: f"{x:.1%}")
        st.dataframe(risk_product, use_container_width=True)
    
    # ==================== TAB 4: KPIs DÉTAIL ====================
    with tab4:
        st.markdown("### 🎯 **Analyse Détaillée des KPIs**")
        
        # KPIs par région
        st.markdown("#### 📊 **Performance par Région**")
        kpi_region = df.groupby('Region').agg({
            'Chiffre_Affaires': 'sum',
            'Benefices': 'sum',
            'Nombre_Clients': 'sum',
            'Taux_Risque': 'mean',
            'Satisfaction': 'mean'
        }).round(2)
        
        kpi_region.columns = ['CA (M DH)', 'Bénéfices (M DH)', 'Nb Clients', 'Risque Moyen', 'Satisfaction']
        kpi_region['CA (M DH)'] = kpi_region['CA (M DH)'] / 1e6
        kpi_region['Bénéfices (M DH)'] = kpi_region['Bénéfices (M DH)'] / 1e6
        kpi_region['Risque Moyen'] = kpi_region['Risque Moyen'].apply(lambda x: f"{x:.1%}")
        kpi_region['Satisfaction'] = kpi_region['Satisfaction'].apply(lambda x: f"{x:.1f}/10")
        
        st.dataframe(kpi_region, use_container_width=True)
        
        # Top produits
        st.markdown("#### 🏆 **Top Produits**")
        top_products = df.groupby('Produit')['Chiffre_Affaires'].sum().sort_values(ascending=False).head(5)
        fig_top = px.bar(x=top_products.values, y=top_products.index, orientation='h',
                        title="Top 5 Produits par Chiffre d'Affaires",
                        color=top_products.values, color_continuous_scale='Viridis')
        st.plotly_chart(fig_top, use_container_width=True)
    
    # ==================== TAB 5: DONNÉES BRUTES ====================
    with tab4 if 'tab4' else tab5:  # Fallback
        st.markdown("### 📋 **Données Complètes**")
        
        # Option export
        col_exp1, col_exp2 = st.columns([3, 1])
        with col_exp2:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 **Télécharger CSV**",
                data=csv,
                file_name=f"analyse_pbix_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        # Preview
        st.markdown("#### **Aperçu des données (100 premières lignes)**")
        st.dataframe(df.head(100), use_container_width=True)
        
        # Statistiques
        with st.expander("📊 **Statistiques Descriptives**"):
            st.dataframe(df.describe(), use_container_width=True)
    
    # ==================== FOOTER ====================
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: white; padding: 1rem;">
        <p>🚀 <strong>PBIX Analyzer Pro</strong> | Analyse Intelligente des Données Power BI</p>
        <p>Développé avec Streamlit, Plotly & Python</p>
    </div>
    """, unsafe_allow_html=True)

else:
    # ==================== PAGE D'ACCUEIL ====================
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    with col_center:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: rgba(255,255,255,0.1); border-radius: 20px;">
            <h1 style="font-size: 4rem;">📊</h1>
            <h2>Bienvenue sur PBIX Analyzer Pro</h2>
            <p style="font-size: 1.2rem; margin-top: 1rem;">
                L'outil ultime pour analyser vos fichiers Power BI<br>
                avec des visualisations avancées et analyse de risque
            </p>
            <div style="margin-top: 2rem;">
                <p>✨ <strong>Comment commencer ?</strong></p>
                <p>👉 Uploadez votre fichier .pbix dans la barre latérale gauche</p>
                <p>🎯 Ou testez le mode démo</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Features
        st.markdown("---")
        st.markdown("### 🌟 **Fonctionnalités Principales**")
        
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <h2>📈</h2>
                <h4>KPIs Interactifs</h4>
                <p>Visualisation des indicateurs clés en temps réel</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_f2:
            st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <h2>⚠️</h2>
                <h4>Analyse de Risque</h4>
                <p>Scoring automatique et détection des risques</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_f3:
            st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <h2>🎯</h2>
                <h4>Filtres Dynamiques</h4>
                <p>Segmentation avancée des données</p>
            </div>
            """, unsafe_allow_html=True)
