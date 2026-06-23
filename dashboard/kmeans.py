"""
================================================================================
MÓDULO: K-Means Clustering
OBJETIVO: Agrupar carreras por similitud en métricas educativas
MÉTODO: Auto-detecta K óptimo usando Elbow Method
================================================================================
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')


def obtener_k_optimo(df_data, features, k_max=8):
    """
    Detecta el número óptimo de clusters usando Elbow Method.
    
    Returns: int (k_optimo)
    """
    X = df_data[features].dropna().values
    
    if len(X) < 3:
        return 2
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    inertias = []
    K_range = range(2, min(k_max + 1, len(X)))
    
    for k in K_range:
        kmeans_temp = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans_temp.fit(X_scaled)
        inertias.append(kmeans_temp.inertia_)
    
    # Heurística simple: elegir donde hay "codo"
    # Calcula la diferencia de pendientes
    if len(inertias) > 2:
        differences = np.diff(inertias)
        second_diff = np.diff(differences)
        k_optimo = list(K_range)[np.argmax(second_diff) + 1]
    else:
        k_optimo = 2
    
    return max(2, min(k_optimo, len(X) // 2))  # Asegura 2 <= k <= n/2


def clustering_carreras(df_data):
    """
    Agrupa carreras usando K-Means basado en métricas de desempeño.
    
    Parameters
    ----------
    df_data : pd.DataFrame
        DataFrame con datos de carreras e instituciones
        
    Returns
    -------
    dict
        {
            'figura_elbow': go.Figure,
            'figura_clusters_2d': go.Figure,
            'figura_clusters_3d': go.Figure,
            'tabla_clusters': pd.DataFrame,
            'metricas': dict
        }
    """
    
    # === 1. SELECCIÓN DE FEATURES ===
    features_clustering = [
        'Empleabilidad al 2º Año',
        'Retención de 1er año',
        'Duración Real (semestres)',
        'Ingreso promedio al 4° año',
        'Empleabilidad al 1er año'
    ]
    
    # Identificador de carrera
    id_carrera = 'Carrera'
    id_institucion = 'Institución'
    
    # Filtrar features disponibles
    features_disponibles = [f for f in features_clustering if f in df_data.columns]
    
    if not features_disponibles:
        return {
            'error': 'No hay features disponibles para clustering',
            'figura_elbow': None,
            'figura_clusters_2d': None,
            'figura_clusters_3d': None,
            'tabla_clusters': None,
            'metricas': {}
        }
    
    # === 2. PREPARACIÓN DE DATOS ===
    df_clean = df_data[[id_institucion, id_carrera] + features_disponibles].copy()
    df_clean = df_clean.dropna(subset=features_disponibles)
    
    if len(df_clean) < 3:
        return {
            'error': f'Datos insuficientes: {len(df_clean)} registros',
            'figura_elbow': None,
            'figura_clusters_2d': None,
            'figura_clusters_3d': None,
            'tabla_clusters': None,
            'metricas': {}
        }
    
    X = df_clean[features_disponibles].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # === 3. AUTO-DETECCIÓN DE K ÓPTIMO ===
    k_optimo = obtener_k_optimo(df_clean, features_disponibles, k_max=8)
    
    # === 4. FIGURA 1: ELBOW METHOD ===
    inertias = []
    silhuetas = []
    K_range = range(2, min(9, len(df_clean)))
    
    for k in K_range:
        kmeans_temp = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans_temp.fit(X_scaled)
        inertias.append(kmeans_temp.inertia_)
    
    fig_elbow = go.Figure()
    
    fig_elbow.add_trace(go.Scatter(
        x=list(K_range), y=inertias,
        mode='lines+markers',
        name='Inercia',
        line=dict(color='#5cb85c', width=3),
        marker=dict(size=8)
    ))
    
    fig_elbow.add_vline(
        x=k_optimo, line_dash='dash', line_color='#d9534f',
        annotation_text=f'K Óptimo = {k_optimo}',
        annotation_position='top right'
    )
    
    fig_elbow.update_layout(
        title='Elbow Method: Selección de Clusters Óptimos',
        xaxis_title='Número de Clusters (K)',
        yaxis_title='Inercia (Suma de Distancias)',
        hovermode='x unified',
        height=350,
        width=590,
        margin=dict(l=60, r=20, t=60, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(240,240,240,0.5)',
        font=dict(size=11)
    )
    
    # === 5. ENTRENAMIENTO FINAL CON K ÓPTIMO ===
    kmeans = KMeans(n_clusters=k_optimo, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    
    df_clean['Cluster'] = clusters
    
    # === 6. REDUCCIÓN A 2D CON PCA ===
    pca_2d = PCA(n_components=2)
    X_pca_2d = pca_2d.fit_transform(X_scaled)
    
    df_plot_2d = pd.DataFrame({
        'PC1': X_pca_2d[:, 0],
        'PC2': X_pca_2d[:, 1],
        'Cluster': [f'Cluster {c}' for c in clusters],
        'Carrera': df_clean[id_carrera].values,
        'Institución': df_clean[id_institucion].values
    })
    
    fig_2d = px.scatter(
        df_plot_2d,
        x='PC1', y='PC2',
        color='Cluster',
        hover_data=['Carrera', 'Institución'],
        title=f'K-Means Clustering: Carreras Agrupadas (K={k_optimo})',
        labels={'PC1': f'PC1 ({pca_2d.explained_variance_ratio_[0]*100:.1f}%)',
                'PC2': f'PC2 ({pca_2d.explained_variance_ratio_[1]*100:.1f}%)'},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    
    fig_2d.update_traces(marker=dict(size=10, opacity=0.8))
    fig_2d.update_layout(
        height=380, width=590,
        margin=dict(l=60, r=20, t=40, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(240,240,240,0.5)',
        font=dict(size=11),
        hovermode='closest'
    )
    
    # === 7. REDUCCIÓN A 3D CON PCA ===
    pca_3d = PCA(n_components=3)
    X_pca_3d = pca_3d.fit_transform(X_scaled)
    
    df_plot_3d = pd.DataFrame({
        'PC1': X_pca_3d[:, 0],
        'PC2': X_pca_3d[:, 1],
        'PC3': X_pca_3d[:, 2],
        'Cluster': [f'Cluster {c}' for c in clusters],
        'Carrera': df_clean[id_carrera].values
    })
    
    colores_clusters = px.colors.qualitative.Set2[:k_optimo]
    color_map = {f'Cluster {i}': colores_clusters[i % len(colores_clusters)] 
                 for i in range(k_optimo)}
    
    fig_3d = px.scatter_3d(
        df_plot_3d,
        x='PC1', y='PC2', z='PC3',
        color='Cluster',
        hover_data=['Carrera'],
        title=f'Vista 3D: K-Means Clustering (K={k_optimo})',
        labels={
            'PC1': f'PC1 ({pca_3d.explained_variance_ratio_[0]*100:.1f}%)',
            'PC2': f'PC2 ({pca_3d.explained_variance_ratio_[1]*100:.1f}%)',
            'PC3': f'PC3 ({pca_3d.explained_variance_ratio_[2]*100:.1f}%)'
        },
        color_discrete_map=color_map
    )
    
    fig_3d.update_traces(marker=dict(size=6, opacity=0.8))
    fig_3d.update_layout(
        height=380, width=590,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=10)
    )
    
    # === 8. TABLA DE RESUMEN POR CLUSTER ===
    tabla_clusters = df_clean.groupby('Cluster')[features_disponibles].agg(['mean', 'std']).round(2)
    
    metricas = {
        'K_optimo': k_optimo,
        'n_carreras': len(df_clean),
        'varianza_explicada_2d': sum(pca_2d.explained_variance_ratio_) * 100,
        'varianza_explicada_3d': sum(pca_3d.explained_variance_ratio_) * 100,
        'inertia': kmeans.inertia_
    }
    
    return {
        'error': None,
        'figura_elbow': fig_elbow,
        'figura_clusters_2d': fig_2d,
        'figura_clusters_3d': fig_3d,
        'tabla_clusters': tabla_clusters,
        'metricas': metricas
    }