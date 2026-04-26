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
    
    /* Tab styling */
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
        'Produit': np.random.choice(['Produit A', 'Produit B', 'Produit C', 'Produit D'], n)
    }
    
    # Add correlations
    data['Benefices_MAD'] = data['CA_MAD'] * 0.3 + np.random.normal(0, 20000, n)
    data['Taux_Risque'] = 1 / (1 + np.exp(-(data['CA_MAD'] - 500000) / 100000))
    
    df = pd.DataFrame(data)
    
    # Add risk levels
    df['Niveau_Risque'] = pd.cut(
        df['Taux_Risque'], 
        bins=[0, 0.3, 0.7, 1], 
        labels=['🟢 Faible', '🟡 Moyen', '🔴 Élevé']
    )
    
    return df

def create_bar_chart(data, x_col, y_col, title, color='#667eea'):
    """Create bar chart using matplotlib"""
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(data[x_col], data[y_col], color=color, edgecolor='white', linewidth=2)
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel(x_col, fontsize=12)
    ax.set_ylabel(y_col, fontsize=12)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height/1e6:.1f}M' if height > 1e6 else f'{height:,.0f}',
                ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    return fig

def create_line_chart(data, x_col, y_col, title, color='#10b981'):
    """Create line chart using matplotlib"""
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
    """Create pie chart using matplotlib"""
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

def create_histogram(data, column, title, color='#667eea'):
    """Create histogram using matplotlib"""
    fig, ax = plt.subplots(figsize=(10, 6))
    n, bins, patches = ax.hist(data[column], bins=30, color=color, edgecolor='white', alpha=0.7)
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel(column, fontsize=12)
    ax.set_ylabel('Fréquence', fontsize=12)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    return fig

def create_boxplot(data, x_col, y_col, title):
    """Create boxplot using matplotlib"""
    fig, ax = plt.subplots(figsize=(10, 6))
    regions = data[x_col].unique()
    box_data = [data[data[x_col] == region][y_col].dropna() for region in regions]
    bp = ax.boxplot(box_data, labels=regions, patch_artist=True)
    
    # Customize box colors
    for patch, color in zip(bp['boxes'], ['#667eea', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel(x_col, fontsize=12)
    ax.set_ylabel(y_col, fontsize=12)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    return fig

# ==================== HEADER ====================
st.markdown("""
<div class="main-header">
    <h1>📊 PBIX Analyzer Pro</h1>
    <p>Analyse avancée des fichiers Power BI - Sans Plotly</p>
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
    - 📈 **KPIs Interactifs**
    - ⚠️ **Analyse de Risque**
    - 📊 **Graphiques Dynamiques**
    - 🎯 **Filtres Avancés**
    - 💾 **Export CSV**
    - 🟢 **100% Stable sur Cloud**
    """)
    
    st.markdown("---")
    st.markdown("### 📌 **Instructions**")
    st.markdown("""
    1. Uploadez votre fichier .pbix
    2. Utilisez les filtres
    3. Explorez les 4 onglets
    4. Exportez vos résultats
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
    
    # ==================== KPIS (using columns with custom styling) ====================
    st.markdown("### 🎯 **Indicateurs Clés de Performance**")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ca_total = df['CA_MAD'].sum() / 1e6
        ca_evolution = ((df['CA_MAD'].tail(30).mean() - df['CA_MAD'].head(30).mean()) / df['CA_MAD'].head(30).mean()) * 100
        st.metric(
            label="💰 **Chiffre d'Affaires Total**",
            value=f"{ca_total:.1f} M DH",
            delta=f"{ca_evolution:.1f}% vs début",
            delta_color="normal"
        )
    
    with col2:
        benef_total = df['Benefices_MAD'].sum() / 1e6
        marge = (benef_total / ca_total) * 100 if ca_total > 0 else 0
        st.metric(
            label="📈 **Bénéfices Totaux**",
            value=f"{benef_total:.1f} M DH",
            delta=f"Marge: {marge:.1f}%",
            delta_color="normal"
        )
    
    with col3:
        clients_total = df['Nbre_Clients'].sum()
        clients_moyen = df['Nbre_Clients'].mean()
        st.metric(
            label="👥 **Total Clients**",
            value=f"{clients_total:,.0f}",
            delta=f"Moyenne: {clients_moyen:.0f}/jour",
            delta_color="off"
        )
    
    with col4:
        risque_moyen = df['Taux_Risque'].mean()
        risque_evolution = df['Taux_Risque'].tail(30).mean() - df['Taux_Risque'].head(30).mean()
        st.metric(
            label="⚠️ **Risque Global**",
            value=f"{risque_moyen:.1%}",
            delta=f"{risque_evolution:.1%} vs début",
            delta_color="inverse" if risque_evolution > 0 else "normal"
        )
    
    # Additional KPIs row
    st.markdown("---")
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        satisfaction_moyenne = df['Satisfaction'].mean()
        st.metric("⭐ **Satisfaction Client**", f"{satisfaction_moyenne:.1f}/10")
    
    with col6:
        top_region = df.groupby('Region')['CA_MAD'].sum().idxmax()
        st.metric("🏆 **Meilleure Région**", top_region)
    
    with col7:
        top_produit = df.groupby('Produit')['CA_MAD'].sum().idxmax()
        st.metric("🎯 **Produit Phare**", top_produit)
    
    with col8:
        clients_haut_risque = len(df[df['Niveau_Risque'] == '🔴 Élevé'])
        st.metric("⚠️ **Clients Haut Risque**", f"{clients_haut_risque}", delta=f"{(clients_haut_risque/len(df))*100:.0f}% du total")
    
    # ==================== TABS ====================
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 **Dashboard Principal**", 
        "📈 **Analyses Statistiques**", 
        "⚠️ **Analyse de Risque**",
        "📋 **Données & Export**"
    ])
    
    # ==================== TAB 1: DASHBOARD ====================
    with tab1:
        st.markdown("### 🔍 **Filtres Interactifs**")
        
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            regions_selected = st.multiselect(
                "**Sélectionnez les régions**",
                df['Region'].unique(),
                default=df['Region'].unique().tolist()
            )
        
        with col_f2:
            produits_selected = st.multiselect(
                "**Sélectionnez les produits**",
                df['Produit'].unique(),
                default=df['Produit'].unique().tolist()
            )
        
        with col_f3:
            risque_filter = st.selectbox(
                "**Niveau de risque**",
                ['Tous', '🟢 Faible', '🟡 Moyen', '🔴 Élevé']
            )
        
        # Apply filters
        df_filtered = df.copy()
        if regions_selected:
            df_filtered = df_filtered[df_filtered['Region'].isin(regions_selected)]
        if produits_selected:
            df_filtered = df_filtered[df_filtered['Produit'].isin(produits_selected)]
        if risque_filter != 'Tous':
            df_filtered = df_filtered[df_filtered['Niveau_Risque'] == risque_filter]
        
        st.markdown(f"**📊 Données filtrées:** {len(df_filtered)} lignes sur {len(df)}")
        
        # Charts row 1
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.markdown("#### 📊 **Chiffre d'Affaires par Région**")
            region_sales = df_filtered.groupby('Region')['CA_MAD'].sum().reset_index()
            fig1 = create_bar_chart(region_sales, 'Region', 'CA_MAD', 'CA par Région (MAD)', '#667eea')
            st.pyplot(fig1)
            plt.close()
        
        with col_g2:
            st.markdown("#### 📈 **Évolution du Chiffre d'Affaires**")
            daily_sales = df_filtered.groupby('Date')['CA_MAD'].sum().reset_index()
            fig2 = create_line_chart(daily_sales, 'Date', 'CA_MAD', 'Tendance CA Journalier', '#10b981')
            st.pyplot(fig2)
            plt.close()
        
        # Charts row 2
        st.markdown("#### 🔗 **Relation CA vs Bénéfices**")
        
        fig3, ax = plt.subplots(figsize=(12, 6))
        
        # Scatter plot with different colors per region
        regions_list = df_filtered['Region'].unique()
        colors_region = ['#667eea', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
        
        for i, region in enumerate(regions_list[:5]):
            region_data = df_filtered[df_filtered['Region'] == region]
            ax.scatter(region_data['CA_MAD'], region_data['Benefices_MAD'], 
                      label=region, alpha=0.6, s=30, color=colors_region[i % len(colors_region)])
        
        ax.set_xlabel('Chiffre d\'Affaires (MAD)', fontsize=12)
        ax.set_ylabel('Bénéfices (MAD)', fontsize=12)
        ax.set_title('Relation CA vs Bénéfices par Région', fontsize=16, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        st.pyplot(fig3)
        plt.close()
        
        # Additional KPIs after filters
        st.markdown("#### 📊 **KPIs après Filtrage**")
        
        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
        
        with kpi_col1:
            ca_filtered = df_filtered['CA_MAD'].sum() / 1e6
            st.metric("CA Filtré", f"{ca_filtered:.1f} M DH", delta=f"{(ca_filtered/ca_total-1)*100:.1f}% du total")
        
        with kpi_col2:
            benef_filtered = df_filtered['Benefices_MAD'].sum() / 1e6
            st.metric("Bénéfices Filtrés", f"{benef_filtered:.1f} M DH")
        
        with kpi_col3:
            risque_filtered = df_filtered['Taux_Risque'].mean()
            st.metric("Risque Moyen Filtré", f"{risque_filtered:.1%}")
    
    # ==================== TAB 2: ANALYSES STATISTIQUES ====================
    with tab2:
        st.markdown("### 📈 **Analyses Statistiques Avancées**")
        
        # Distribution analysis
        col_s1, col_s2 = st.columns(2)
        
        with col_s1:
            st.markdown("#### 📊 **Distribution des Ventes**")
            fig_hist = create_histogram(df, 'CA_MAD', 'Distribution du Chiffre d\'Affaires', '#667eea')
            st.pyplot(fig_hist)
            plt.close()
        
        with col_s2:
            st.markdown("#### 📦 **Boxplot CA par Région**")
            fig_box = create_boxplot(df, 'Region', 'CA_MAD', 'Distribution CA par Région')
            st.pyplot(fig_box)
            plt.close()
        
        # Statistics table
        st.markdown("#### 📋 **Statistiques Descriptives**")
        
        stats_df = df[['CA_MAD', 'Benefices_MAD', 'Nbre_Clients', 'Taux_Risque', 'Satisfaction']].describe()
        stats_df.index = ['Count', 'Mean', 'Std', 'Min', '25%', '50%', '75%', 'Max']
        
        # Format numbers
        stats_formatted = stats_df.copy()
        stats_formatted['CA_MAD'] = stats_formatted['CA_MAD'].apply(lambda x: f"{x:,.0f}")
        stats_formatted['Benefices_MAD'] = stats_formatted['Benefices_MAD'].apply(lambda x: f"{x:,.0f}")
        stats_formatted['Nbre_Clients'] = stats_formatted['Nbre_Clients'].apply(lambda x: f"{x:,.0f}")
        stats_formatted['Taux_Risque'] = stats_formatted['Taux_Risque'].apply(lambda x: f"{x:.2%}")
        stats_formatted['Satisfaction'] = stats_formatted['Satisfaction'].apply(lambda x: f"{x:.2f}")
        
        st.dataframe(stats_formatted, use_container_width=True)
        
        # Correlation analysis
        st.markdown("#### 🔗 **Analyse des Corrélations**")
        
        corr_cols = ['CA_MAD', 'Benefices_MAD', 'Nbre_Clients', 'Taux_Risque', 'Satisfaction']
        corr_matrix = df[corr_cols].corr()
        
        # Display correlation as colored table
        st.dataframe(corr_matrix.style.background_gradient(cmap='RdBu', vmin=-1, vmax=1), use_container_width=True)
        
        # Top performers
        st.markdown("#### 🏆 **Top Performers**")
        
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            st.markdown("**Top 5 Produits par CA**")
            top_products = df.groupby('Produit')['CA_MAD'].sum().sort_values(ascending=False).head(5)
            fig_top = create_bar_chart(top_products.reset_index(), 'Produit', 'CA_MAD', '', '#10b981')
            st.pyplot(fig_top)
            plt.close()
        
        with col_t2:
            st.markdown("**Top 5 Régions par CA**")
            top_regions = df.groupby('Region')['CA_MAD'].sum().sort_values(ascending=False).head(5)
            fig_top_reg = create_bar_chart(top_regions.reset_index(), 'Region', 'CA_MAD', '', '#f59e0b')
            st.pyplot(fig_top_reg)
            plt.close()
    
    # ==================== TAB 3: ANALYSE DE RISQUE ====================
    with tab3:
        st.markdown("### ⚠️ **Tableau de Bord du Risque**")
        
        # Risk KPIs
        col_r1, col_r2, col_r3, col_r4 = st.columns(4)
        
        risk_counts = df['Niveau_Risque'].value_counts()
        risk_high_pct = (risk_counts.get('🔴 Élevé', 0) / len(df)) * 100
        risk_medium_pct = (risk_counts.get('🟡 Moyen', 0) / len(df)) * 100
        risk_low_pct = (risk_counts.get('🟢 Faible', 0) / len(df)) * 100
        
        with col_r1:
            st.metric("🔴 **Risque Élevé**", f"{risk_counts.get('🔴 Élevé', 0)}", delta=f"{risk_high_pct:.0f}%")
        
        with col_r2:
            st.metric("🟡 **Risque Moyen**", f"{risk_counts.get('🟡 Moyen', 0)}", delta=f"{risk_medium_pct:.0f}%")
        
        with col_r3:
            st.metric("🟢 **Risque Faible**", f"{risk_counts.get('🟢 Faible', 0)}", delta=f"{risk_low_pct:.0f}%")
        
        with col_r4:
            risque_moyen = df['Taux_Risque'].mean()
            st.metric("📊 **Score Risque Moyen**", f"{risque_moyen:.1%}")
        
        # Risk charts
        col_rg1, col_rg2 = st.columns(2)
        
        with col_rg1:
            st.markdown("#### 🥧 **Distribution des Niveaux de Risque**")
            fig_pie = create_pie_chart(
                risk_counts.index.tolist(),
                risk_counts.values.tolist(),
                'Distribution du Risque'
            )
            st.pyplot(fig_pie)
            plt.close()
        
        with col_rg2:
            st.markdown("#### 📊 **Risque Moyen par Région**")
            risk_region = df.groupby('Region')['Taux_Risque'].mean().sort_values(ascending=False).reset_index()
            fig_risk_region = create_bar_chart(risk_region, 'Region', 'Taux_Risque', '', '#ef4444')
            st.pyplot(fig_risk_region)
            plt.close()
        
        # Detailed risk table
        st.markdown("#### 📋 **Détail du Risque par Catégorie**")
        
        risk_detail = df.groupby('Produit').agg({
            'Taux_Risque': ['mean', 'std', 'count'],
            'CA_MAD': 'sum',
            'Nbre_Clients': 'sum'
        }).round(4)
        
        risk_detail.columns = ['Risque Moyen', 'Écart-Type', 'Nb Transactions', 'CA Total (M MAD)', 'Nb Clients']
        risk_detail['Risque Moyen'] = risk_detail['Risque Moyen'].apply(lambda x: f"{x:.1%}")
        risk_detail['CA Total (M MAD)'] = risk_detail['CA Total (M MAD)'] / 1e6
        risk_detail['CA Total (M MAD)'] = risk_detail['CA Total (M MAD)'].apply(lambda x: f"{x:.1f}")
        
        st.dataframe(risk_detail, use_container_width=True)
        
        # Risk recommendations
        st.markdown("#### 💡 **Recommandations**")
        
        high_risk_regions = df[df['Niveau_Risque'] == '🔴 Élevé'].groupby('Region').size().sort_values(ascending=False).head(3)
        
        if len(high_risk_regions) > 0:
            st.warning(f"⚠️ **Zones à risque élevé:** {', '.join(high_risk_regions.index.tolist())}")
        
        st.info("💡 **Actions recommandées:** Analyser en détail les régions à risque élevé, revoir les conditions de crédit, renforcer le suivi client.")
    
    # ==================== TAB 4: DONNÉES & EXPORT ====================
    with tab4:
        st.markdown("### 📋 **Données Brutes & Export**")
        
        # Export options
        col_e1, col_e2 = st.columns([1, 3])
        
        with col_e1:
            # CSV export
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 **Télécharger CSV**",
                data=csv_data,
                file_name=f"pbix_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            # Excel export option
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Data', index=False)
                risk_detail.to_excel(writer, sheet_name='Risk_Analysis')
            
            st.download_button(
                label="📊 **Télécharger Excel**",
                data=buffer.getvalue(),
                file_name=f"pbix_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col_e2:
            st.info("📌 **Formats disponibles:** CSV pour analyse, Excel pour rapport complet")
        
        # Data preview
        st.markdown("#### 📄 **Aperçu des données (100 premières lignes)**")
        st.dataframe(df.head(100), use_container_width=True)
        
        # Data info
        with st.expander("ℹ️ **Informations sur les données**"):
            col_info1, col_info2 = st.columns(2)
            
            with col_info1:
                st.write("**Dimensions:**")
                st.write(f"- Lignes: {len(df)}")
                st.write(f"- Colonnes: {len(df.columns)}")
                st.write(f"- Valeurs manquantes: {df.isnull().sum().sum()}")
            
            with col_info2:
                st.write("**Types de données:**")
                dtype_df = pd.DataFrame({
                    'Colonne': df.dtypes.index,
                    'Type': df.dtypes.values
                })
                st.dataframe(dtype_df, use_container_width=True)

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1rem;">
    <p>🚀 <strong>PBIX Analyzer Pro</strong> | Version Stable sans Plotly</p>
    <p>Développé avec Streamlit, Matplotlib & Pandas</p>
</div>
""", unsafe_allow_html=True)

else:
    # Welcome page
    st.markdown("""
    <div style="text-align: center; padding: 3rem;">
        <h1 style="font-size: 4rem;">📊</h1>
        <h2>Bienvenue sur PBIX Analyzer Pro</h2>
        <p style="font-size: 1.2rem; margin-top: 1rem;">
            L'outil ultime pour analyser vos fichiers Power BI
        </p>
        <p style="margin-top: 2rem;">
            👈 <strong>Uploadez votre fichier .pbix</strong> dans la barre latérale<br>
            ou cliquez sur <strong>Mode Démo</strong> pour tester
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features grid
    st.markdown("---")
    st.markdown("### 🌟 **Fonctionnalités**")
    
    col_w1, col_w2, col_w3, col_w4 = st.columns(4)
    
    with col_w1:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h2>📈</h2>
            <h4>KPIs Interactifs</h4>
            <p>Indicateurs clés en temps réel</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_w2:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h2>⚠️</h2>
            <h4>Analyse de Risque</h4>
            <p>Scoring et détection automatique</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_w3:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h2>📊</h2>
            <h4>Visualisations</h4>
            <p>Graphiques Matplotlib</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_w4:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h2>💾</h2>
            <h4>Export Multi-format</h4>
            <p>CSV & Excel</p>
        </div>
        """, unsafe_allow_html=True)
