"""
================================================================================
MÓDULO: Regresión Lineal Múltiple
OBJETIVO: Predecir "Ingreso promedio al 4° año" basado en métricas de desempeño
================================================================================
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')


def entrenar_regresion_ingresos(df_data):
    """
    Entrena modelo de regresión lineal múltiple para predecir ingresos al egreso.
    
    Parameters
    ----------
    df_data : pd.DataFrame
        DataFrame con columnas de métricas educativas
        
    Returns
    -------
    dict
        {
            'figura_prediccion': go.Figure (Plotly),
            'figura_residuales': go.Figure (Plotly),
            'figura_importancia': go.Figure (Plotly),
            'metricas': dict con R2, RMSE, MAE
        }
    """
    
    # === 1. SELECCIÓN Y PREPARACIÓN DE FEATURES ===
    features_requeridas = [
        'Retención de 1er año',
        'Duración Real (semestres)',
        'Empleabilidad al 1er año',
        'Empleabilidad al 2º Año',
        '% Titulados continuidad de estudios'
    ]
    
    target = 'Ingreso promedio al 4° año'
    
    # Verificar disponibilidad de columnas
    columnas_disponibles = [col for col in features_requeridas if col in df_data.columns]
    
    if target not in df_data.columns:
        return {
            'error': f'Columna target "{target}" no encontrada',
            'figura_prediccion': None,
            'figura_residuales': None,
            'figura_importancia': None,
            'metricas': {}
        }
    
    # Crear subset con datos válidos
    df_clean = df_data[columnas_disponibles + [target]].copy()
    df_clean = df_clean.dropna()
    
    if len(df_clean) < 10:
        return {
            'error': f'Datos insuficientes: {len(df_clean)} registros válidos',
            'figura_prediccion': None,
            'figura_residuales': None,
            'figura_importancia': None,
            'metricas': {}
        }
    
    X = df_clean[columnas_disponibles].values
    y = df_clean[target].values
    
    # === 2. NORMALIZACIÓN Y SPLIT ===
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    
    # === 3. ENTRENAMIENTO ===
    modelo = LinearRegression()
    modelo.fit(X_train, y_train)
    
    y_pred_train = modelo.predict(X_train)
    y_pred_test = modelo.predict(X_test)
    
    # === 4. EVALUACIÓN ===
    r2_train = r2_score(y_train, y_pred_train)
    r2_test = r2_score(y_test, y_pred_test)
    rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))
    mae_test = mean_absolute_error(y_test, y_pred_test)
    
    metricas = {
        'R² Train': round(r2_train, 4),
        'R² Test': round(r2_test, 4),
        'RMSE Test': round(rmse_test, 2),
        'MAE Test': round(mae_test, 2),
        'n_samples': len(df_clean)
    }
    
    # === 5. FIGURA 1: PREDICCIÓN VS ACTUAL ===
    df_pred = pd.DataFrame({
        'Actual': np.concatenate([y_train, y_test]),
        'Predicción': np.concatenate([y_pred_train, y_pred_test]),
        'Set': ['Train'] * len(y_train) + ['Test'] * len(y_test)
    })
    
    fig_pred = go.Figure()
    
    # Diagonal de referencia (perfecta predicción)
    y_min, y_max = df_pred['Actual'].min(), df_pred['Actual'].max()
    fig_pred.add_trace(go.Scatter(
        x=[y_min, y_max], y=[y_min, y_max],
        mode='lines', name='Predicción Perfecta',
        line=dict(color='rgba(150,150,150,0.5)', width=2, dash='dash')
    ))
    
    # Train set
    fig_pred.add_trace(go.Scatter(
        x=df_pred[df_pred['Set']=='Train']['Actual'],
        y=df_pred[df_pred['Set']=='Train']['Predicción'],
        mode='markers', name='Train',
        marker=dict(size=7, color='#5cb85c', opacity=0.6)
    ))
    
    # Test set
    fig_pred.add_trace(go.Scatter(
        x=df_pred[df_pred['Set']=='Test']['Actual'],
        y=df_pred[df_pred['Set']=='Test']['Predicción'],
        mode='markers', name='Test',
        marker=dict(size=8, color='#d9534f', opacity=0.8, symbol='diamond')
    ))
    
    fig_pred.update_layout(
        title='Predicción vs Ingreso Real (Modelo Regresión Lineal)',
        xaxis_title='Ingreso Actual ($)',
        yaxis_title='Ingreso Predicho ($)',
        hovermode='closest',
        height=380,
        width=590,
        margin=dict(l=60, r=20, t=40, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(240,240,240,0.5)',
        font=dict(size=11)
    )
    
    # === 6. FIGURA 2: RESIDUALES ===
    residuales = np.concatenate([y_train - y_pred_train, y_test - y_pred_test])
    predicciones = np.concatenate([y_pred_train, y_pred_test])
    sets = ['Train'] * len(y_train) + ['Test'] * len(y_test)
    
    df_residuales = pd.DataFrame({
        'Predicción': predicciones,
        'Residual': residuales,
        'Set': sets
    })
    
    fig_res = px.scatter(
        df_residuales,
        x='Predicción',
        y='Residual',
        color='Set',
        color_discrete_map={'Train': '#5cb85c', 'Test': '#d9534f'},
        title='Análisis de Residuales (Errores de Predicción)',
        labels={'Predicción': 'Valor Predicho ($)', 'Residual': 'Error ($)'},
        hover_data={'Set': False}
    )
    
    # Línea de referencia en 0
    fig_res.add_hline(
        y=0, line_dash='dash', line_color='gray',
        annotation_text='Error = 0', annotation_position='right'
    )
    
    fig_res.update_traces(marker=dict(size=8, opacity=0.7))
    fig_res.update_layout(
        height=380, width=590,
        margin=dict(l=60, r=20, t=40, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(240,240,240,0.5)',
        font=dict(size=11)
    )
    
    # === 7. FIGURA 3: IMPORTANCIA DE FEATURES ===
    feature_importance = pd.DataFrame({
        'Feature': columnas_disponibles,
        'Coeficiente': np.abs(modelo.coef_)
    }).sort_values('Coeficiente', ascending=True)
    
    fig_imp = px.barh(
        feature_importance,
        x='Coeficiente',
        y='Feature',
        color='Coeficiente',
        color_continuous_scale='Viridis',
        title='Importancia de Features (Valor Absoluto de Coeficientes)',
        labels={'Coeficiente': 'Magnitud del Coeficiente'}
    )
    
    fig_imp.update_layout(
        height=380, width=590,
        margin=dict(l=200, r=20, t=40, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(240,240,240,0.5)',
        font=dict(size=11),
        showlegend=False
    )
    
    return {
        'error': None,
        'figura_prediccion': fig_pred,
        'figura_residuales': fig_res,
        'figura_importancia': fig_imp,
        'metricas': metricas
    }