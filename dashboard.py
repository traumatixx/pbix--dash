import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import io

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
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 1rem;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 10px;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: rgba(102, 126, 234, 0.1);
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

# ==================== FUNCTIONS ====================
@st.cache_data
def generate_demo_data():
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
        'Produit': np.random.choice(['Produit A', 'Produit B', 'Produit C', 'Produit D'], n)
    }
    
    data['Benefices_MAD'] = data['CA_MAD'] * 0.3 + np.random.normal(0, 20000, n)
    data['Taux_Risque'] = 1 / (1 + np.exp(-(data['CA_MAD'] - 500000) / 100000))
    
    df = pd.DataFrame(data)
    df['Niveau_Risque'] = pd.cut(df['Taux_Risque'], bins=[0, 0.3, 0.7, 1], labels=['🟢 Faible', '🟡 Moyen', '🔴 Élevé'])
    
    return df

def create_bar_chart(data, x_col, y_col, title, color='#667eea'):
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(data[x_col], data[y_col], color=color, edgecolor='white', linewidth=2)
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel(x_col, fontsize=12)
    ax.set_ylabel(y_col, fontsize=12)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', alpha=0.3)
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height/1e6:.1f}M' if height > 1e6 else f'{height:,.0f}',
                ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    return fig

def create_line_chart(data, x_col, y_col, title, color='#10b981'):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(data[x_col], data[y_col], color=color, linewidth=2, marker='o', markersize=4)
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel(x_col, fontsize=12)
    ax.set_ylabel(y_col, fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    return fig

def create_pie_chart(labels, values, title, colors=['#10b981', '#f59e0b', '#ef4444']):
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%',
                                        colors=colors, startangle=90,
                                        textprops={'fontsize': 12})
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    return fig

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
        "**Choisissez votre fichier .pbix**",
        type=['pbix'],
        help="Upload your Power BI Desktop file (.pbix)"
    )
    
    if uploaded_file:
        st.success(f"✅ **Fichier chargé!**\n\n`{uploaded_file.name}`")
        st.session_state['file_uploaded'] = True
        st.session_state['file_name'] = uploaded_file.name
    else:
        st.info("💡 **Mode Démo disponible**")
        
        if st.button("🎯 **Lancer Mode Démo**", use_container_width=True):
            st.session_state['demo_mode'] = True
    
    st.markdown("---")
    st.markdown("### 📊 **Fonctionnalités**")
    st.markdown("""
    - 📈 KPIs Interactifs
    - ⚠️ Analyse de Risque
    - 📊 Graphiques Dynamiques
    - 🎯 Filtres Avancés
    - 💾 Export CSV & Excel
    """)

# ==================== MAIN CONTENT ====================
if 'file_uploaded' in st.session_state or 'demo_mode' in st.session_state:
    
    with st.spinner("📊 **Chargement et analyse des données...**"):
        df = generate_demo_data()
    
    if 'file_uploaded' in st.session_state:
        st.balloons()
        st.success(f"✅ **Analyse terminée!** Fichier: `{st.session_state.get('file_name', '')}`")
        st.info("📌 **Note:** Actuellement en mode démonstration. Pour vos données réelles, exportez-les en CSV depuis Power BI Desktop.")
    else:
        st.info("🎮 **Mode Démo** - Données générées pour illustration des fonctionnalités")
    
    # ==================== KPIS ====================
    st.markdown("### 🎯 **Indicateurs Clés de Performance**")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ca_total = df['CA_MAD'].sum() / 1e6
        st.metric("💰 **CA Total**", f"{ca_total:.1f} M DH")
    
    with col2:
        benef_total = df['Benefices_MAD'].sum() / 1e6
        st.metric("📈 **Bénéfices Totaux**", f"{benef_total:.1f} M DH")
    
    with col3:
        clients_total = df['Nbre_Clients'].sum()
        st.metric("👥 **Total Clients**", f"{clients_total:,.0f}")
    
    with col4:
        risque_moyen = df['Taux_Risque'].mean()
        st.metric("⚠️ **Risque Global**", f"{risque_moyen:.1%}")
    
    # ==================== TABS ====================
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard Principal", 
        "📈 Analyses Statistiques", 
        "⚠️ Analyse de Risque",
        "📋 Données & Export"
    ])
    
    # ==================== TAB 1: DASHBOARD ====================
    with tab1:
        st.markdown("### 🔍 **Filtres Interactifs**")
        
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            regions_selected = st.multiselect(
                "**Régions**",
                df['Region'].unique(),
                default=df['Region'].unique().tolist()
            )
        
        with col_f2:
            produits_selected = st.multiselect(
                "**Produits**",
                df['Produit'].unique(),
                default=df['Produit'].unique().tolist()
            )
        
        with col_f3:
            risque_filter = st.selectbox(
                "**Niveau de risque**",
                ['Tous', '🟢 Faible', '🟡 Moyen', '🔴 Élevé']
            )
        
        df_filtered = df.copy()
        if regions_selected:
            df_filtered = df_filtered[df_filtered['Region'].isin(regions_selected)]
        if produits_selected:
            df_filtered = df_filtered[df_filtered['Produit'].isin(produits_selected)]
        if risque_filter != 'Tous':
            df_filtered = df_filtered[df_filtered['Niveau_Risque'] == risque_filter]
        
        st.markdown(f"**📊 Données filtrées:** {len(df_filtered)} lignes")
        
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.markdown("#### CA par Région")
            region_sales = df_filtered.groupby('Region')['CA_MAD'].sum().reset_index()
            fig1 = create_bar_chart(region_sales, 'Region', 'CA_MAD', '', '#667eea')
            st.pyplot(fig1)
            plt.close()
        
        with col_g2:
            st.markdown("#### Évolution du CA")
            daily_sales = df_filtered.groupby('Date')['CA_MAD'].sum().reset_index()
            fig2 = create_line_chart(daily_sales, 'Date', 'CA_MAD', '', '#10b981')
            st.pyplot(fig2)
            plt.close()
    
    # ==================== TAB 2: ANALYSES ====================
    with tab2:
        st.markdown("### 📈 **Statistiques Descriptives**")
        
        stats_df = df[['CA_MAD', 'Benefices_MAD', 'Nbre_Clients', 'Taux_Risque', 'Satisfaction']].describe()
        st.dataframe(stats_df, use_container_width=True)
        
        st.markdown("### 🔗 **Matrice de Corrélation**")
        corr_cols = ['CA_MAD', 'Benefices_MAD', 'Nbre_Clients', 'Taux_Risque', 'Satisfaction']
        corr_matrix = df[corr_cols].corr()
        st.dataframe(corr_matrix.style.background_gradient(cmap='RdBu', vmin=-1, vmax=1), use_container_width=True)
    
    # ==================== TAB 3: RISQUE ====================
    with tab3:
        st.markdown("### ⚠️ **Analyse de Risque**")
        
        col_r1, col_r2, col_r3 = st.columns(3)
        
        risk_counts = df['Niveau_Risque'].value_counts()
        
        with col_r1:
            st.metric("🔴 **Risque Élevé**", risk_counts.get('🔴 Élevé', 0))
        with col_r2:
            st.metric("🟡 **Risque Moyen**", risk_counts.get('🟡 Moyen', 0))
        with col_r3:
            st.metric("🟢 **Risque Faible**", risk_counts.get('🟢 Faible', 0))
        
        col_rg1, col_rg2 = st.columns(2)
        
        with col_rg1:
            fig_pie = create_pie_chart(
                risk_counts.index.tolist(),
                risk_counts.values.tolist(),
                'Distribution du Risque'
            )
            st.pyplot(fig_pie)
            plt.close()
        
        with col_rg2:
            risk_region = df.groupby('Region')['Taux_Risque'].mean().sort_values(ascending=False).reset_index()
            fig_risk = create_bar_chart(risk_region, 'Region', 'Taux_Risque', 'Risque par Région', '#ef4444')
            st.pyplot(fig_risk)
            plt.close()
    
    # ==================== TAB 4: DONNÉES ====================
    with tab4:
        st.markdown("### 📋 **Export des Données**")
        
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 **Télécharger CSV**",
            data=csv_data,
            file_name=f"pbix_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        st.markdown("### 📄 **Aperçu des données**")
        st.dataframe(df.head(100), use_container_width=True)

else:
    # ==================== PAGE D'ACCUEIL ====================
    st.markdown("""
    <div style="text-align: center; padding: 3rem;">
        <h1 style="font-size: 4rem;">📊</h1>
        <h2>Bienvenue sur PBIX Analyzer Pro</h2>
        <p style="font-size: 1.2rem; margin-top: 1rem;">
            Uploadez votre fichier .pbix ou testez le mode démo
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_w1, col_w2, col_w3, col_w4 = st.columns(4)
    
    with col_w1:
        st.markdown("**📈 KPIs**\n\nIndicateurs clés")
    with col_w2:
        st.markdown("**⚠️ Risque**\n\nAnalyse avancée")
    with col_w3:
        st.markdown("**📊 Graphiques**\n\nVisualisations")
    with col_w4:
        st.markdown("**💾 Export**\n\nCSV & Excel")
