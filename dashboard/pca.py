"""
================================================================================
MÓDULO: Principal Component Analysis (PCA)
OBJETIVO: Reducir dimensionalidad y visualizar correlaciones entre métricas
MÉTODOS: Biplot 2D, Scree Plot, Loadings Heatmap
================================================================================
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')


def analisis_pca_completo(df_data):
    """
    Realiza análisis PCA completo con múltiples visualizaciones.
    
    Parameters
    ----------
    df_data : pd.DataFrame
        DataFrame con datos de educación superior
        
    Returns
    -------
    dict
        {
            'figura_scree': go.Figure (varianza explicada),
            'figura_biplot': go.Figure (scatter con loadings),
            'figura_loadings_heatmap': go.Figure (mapa de calor),
            'figura_pca_3d': go.Figure (visualización 3D),
            'tabla_componentes': pd.DataFrame,
            'metricas': dict
        }
    """
    
    # === 1. SELECCIÓN DE FEATURES NUMÉRICOS ===
    features_pca = [
        'Retención de 1er año',
        'Duración Real (semestres)',
        'Empleabilidad al 1er año',
        'Empleabilidad al 2º Año',
        '% Titulados continuidad de estudios',
        'Ingreso promedio al 4° año'
    ]
    
    # Filtrar solo features disponibles
    features_disponibles = [f for f in features_pca if f in df_data.columns]
    
    if len(features_disponibles) < 2:
        return {
            'error': 'Insuficientes features numéricos para PCA',
            'figura_scree': None,
            'figura_biplot': None,
            'figura_loadings_heatmap': None,
            'figura_pca_3d': None,
            'tabla_componentes': None,
            'metricas': {}
        }
    
    # === 2. PREPARACIÓN DE DATOS ===
    df_clean = df_data[features_disponibles + ['Carrera', 'Institución']].copy()
    df_clean = df_clean.dropna(subset=features_disponibles)
    
    if len(df_clean) < 3:
        return {
            'error': f'Datos insuficientes: {len(df_clean)} registros',
            'figura_scree': None,
            'figura_biplot': None,
            'figura_loadings_heatmap': None,
            'figura_pca_3d': None,
            'tabla_componentes': None,
            'metricas': {}
        }
    
    X = df_clean[features_disponibles].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # === 3. PCA COMPLETO ===
    pca_completo = PCA()
    X_pca_completo = pca_completo.fit_transform(X_scaled)
    
    # === 4. FIGURA 1: SCREE PLOT (Varianza Explicada) ===
    varianza_acumulada = np.cumsum(pca_completo.explained_variance_ratio_)
    n_components = min(len(features_disponibles), len(X))
    
    df_scree = pd.DataFrame({
        'PC': [f'PC{i+1}' for i in range(n_components)],
        'Varianza Individual': pca_completo.explained_variance_ratio_[:n_components] * 100,
        'Varianza Acumulada': varianza_acumulada[:n_components] * 100
    })
    
    fig_scree = go.Figure()
    
    fig_scree.add_trace(go.Bar(
        x=df_scree['PC'],
        y=df_scree['Varianza Individual'],
        name='Varianza Individual',
        marker_color='#5cb85c',
        opacity=0.7
    ))
    
    fig_scree.add_trace(go.Scatter(
        x=df_scree['PC'],
        y=df_scree['Varianza Acumulada'],
        name='Varianza Acumulada',
        mode='lines+markers',
        line=dict(color='#d9534f', width=3),
        marker=dict(size=8),
        yaxis='y2'
    ))
    
    fig_scree.update_layout(
        title='Scree Plot: Varianza Explicada por Componente Principal',
        xaxis_title='Componente Principal',
        yaxis_title='Varianza Individual (%)',
        yaxis2=dict(title='Varianza Acumulada (%)', overlaying='y', side='right'),
        hovermode='x unified',
        height=350,
        width=590,
        margin=dict(l=60, r=60, t=40, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(240,240,240,0.5)',
        font=dict(size=11),
        barmode='group'
    )
    
    # Línea de referencia 80% varianza acumulada
    n_pc_80 = np.argmax(varianza_acumulada >= 80) + 1
    fig_scree.add_hline(y=80, line_dash='dash', line_color='gray', 
                        annotation_text='80% Varianza')
    
    # === 5. FIGURA 2: BIPLOT (PC1 vs PC2 con Loadings) ===
    pca_2d = PCA(n_components=2)
    X_pca_2d = pca_2d.fit_transform(X_scaled)
    
    loadings = pca_2d.components_.T * np.sqrt(pca_2d.explained_variance_)
    
    # Scatter de observaciones
    df_plot = pd.DataFrame({
        'PC1': X_pca_2d[:, 0],
        'PC2': X_pca_2d[:, 1],
        'Carrera': df_clean['Carrera'].values,
        'Institución': df_clean['Institución'].values
    })
    
    fig_biplot = px.scatter(
        df_plot,
        x='PC1', y='PC2',
        hover_data=['Carrera', 'Institución'],
        title=f'PCA Biplot: PC1 ({pca_2d.explained_variance_ratio_[0]*100:.1f}%) vs PC2 ({pca_2d.explained_variance_ratio_[1]*100:.1f}%)',
        color_discrete_sequence=['#5cb85c']
    )
    
    # Agregar flechas de loadings
    scale_factor = 3
    for i, feature in enumerate(features_disponibles):
        fig_biplot.add_annotation(
            x=loadings[i, 0] * scale_factor,
            y=loadings[i, 1] * scale_factor,
            ax=0, ay=0,
            showarrow=True,
            arrowsize=2,
            arrowwidth=2,
            arrowcolor='#d9534f',
            text=feature,
            font=dict(size=10, color='#d9534f'),
            xanchor='center'
        )
    
    fig_biplot.update_traces(marker=dict(size=8, opacity=0.7))
    fig_biplot.update_layout(
        height=380, width=590,
        margin=dict(l=60, r=20, t=40, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(240,240,240,0.5)',
        font=dict(size=10),
        hovermode='closest',
        showlegend=False
    )
    
    # === 6. FIGURA 3: LOADINGS HEATMAP ===
    loadings_df = pd.DataFrame(
        pca_2d.components_.T,
        columns=[f'PC{i+1}' for i in range(2)],
        index=features_disponibles
    )
    
    fig_heatmap = px.imshow(
        loadings_df.T,
        labels=dict(x='Features', y='Componentes', color='Valor'),
        title='Loading Plot: Contribución de Features a Componentes',
        color_continuous_scale='RdBu',
        color_continuous_midpoint=0,
        aspect='auto'
    )
    
    fig_heatmap.update_layout(
        height=380, width=590,
        margin=dict(l=120, r=20, t=40, b=80),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=10)
    )
    
    # === 7. FIGURA 4: PCA 3D ===
    pca_3d = PCA(n_components=3)
    X_pca_3d = pca_3d.fit_transform(X_scaled)
    
    df_plot_3d = pd.DataFrame({
        'PC1': X_pca_3d[:, 0],
        'PC2': X_pca_3d[:, 1],
        'PC3': X_pca_3d[:, 2],
        'Carrera': df_clean['Carrera'].values
    })
    
    fig_3d = px.scatter_3d(
        df_plot_3d,
        x='PC1', y='PC2', z='PC3',
        hover_data=['Carrera'],
        title=f'PCA 3D: {pca_3d.explained_variance_ratio_.sum()*100:.1f}% Varianza Explicada',
        color_discrete_sequence=['#5cb85c'],
        labels={
            'PC1': f'PC1 ({pca_3d.explained_variance_ratio_[0]*100:.1f}%)',
            'PC2': f'PC2 ({pca_3d.explained_variance_ratio_[1]*100:.1f}%)',
            'PC3': f'PC3 ({pca_3d.explained_variance_ratio_[2]*100:.1f}%)'
        }
    )
    
    fig_3d.update_traces(marker=dict(size=6, opacity=0.8))
    fig_3d.update_layout(
        height=380, width=590,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=10)
    )
    
    # === 8. TABLA DE COMPONENTES ===
    tabla_componentes = pd.DataFrame(
        pca_completo.components_[:n_pc_80].T,
        columns=[f'PC{i+1}' for i in range(n_pc_80)],
        index=features_disponibles
    ).round(3)
    
    metricas = {
        'n_features_original': len(features_disponibles),
        'n_componentes_80_varianza': n_pc_80,
        'varianza_explicada_2d': pca_2d.explained_variance_ratio_.sum() * 100,
        'varianza_explicada_3d': pca_3d.explained_variance_ratio_.sum() * 100,
        'n_samples': len(df_clean)
    }
    
    return {
        'error': None,
        'figura_scree': fig_scree,
        'figura_biplot': fig_biplot,
        'figura_loadings_heatmap': fig_heatmap,
        'figura_pca_3d': fig_3d,
        'tabla_componentes': tabla_componentes,
        'metricas': metricas
    }