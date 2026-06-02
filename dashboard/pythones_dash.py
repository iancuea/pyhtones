# %% [markdown]
# ### CONSTRUCCIÓN DEL DASHBOARD INTERACTIVO VIP

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ipywidgets as ipw
from IPython.display import display

# %%
# Función auxiliar para sacar valores únicos de una columna y añadir la opción "TODO"
def getColumnToDim(dataframe, columnName):
    dfAux = dataframe.groupby([columnName]).size().reset_index(name='COUNT')
    resp = dfAux[columnName].to_numpy()
    resp = np.append(resp, "TODO")
    return resp

# Generamos las opciones para nuestros menús desplegables
dependencias_colegio = getColumnToDim(df_clean, 'NOMBRE_DEPENDENCIA')
regiones_chile = getColumnToDim(df_clean, 'NOMBRE_REGION')

# %% [markdown]
# #### PANEL 1: SISTEMA DE LOGIN CHETO

# %%
title = ipw.HTML(value="<h2 style='color:#2c3e50;'><b>🔐 ACCESO AL PANEL DE ADMISIÓN</b></h2>")
txt_userName = ipw.Text(value='', placeholder='Nombre de usuario', description='Usuario:', disabled=False)
txt_pass = ipw.Password(value='', placeholder='Contraseña', description='Password:', disabled=False)
btn_login = ipw.Button(description='Ingresar', disabled=False, button_style='success', tooltip='Login', icon='check')
login_valid = ipw.Valid(value=False)
login_valid.layout.visibility = "hidden"
login_row = ipw.HBox([btn_login, login_valid])

def verificar_usuario(b):
    # Aquí puedes poner tus credenciales de prueba, ej: uach / 2026
    if txt_userName.value == "uach" and txt_pass.value == "2026":
        login_valid.value = True
        login_valid.layout.visibility = "visible"
    else:    
        login_valid.value = False
        login_valid.layout.visibility = "visible"

btn_login.on_click(verificar_usuario)

panel_login = ipw.VBox([title, txt_userName, txt_pass, login_row],
                       layout=ipw.Layout(
                           display='flex',
                           flex_flow='column',
                           border='solid 1px #bdc3c7',
                           padding='20px',
                           border_radius='8px',
                           align_items='stretch',
                           width='35%'
                       ))

# %% [markdown]
# #### PANEL 2: MÉTRICAS COMPLEMENTARIAS DINÁMICAS (Usando Observe)

# %%
# Widget de control para filtrar métricas por Región
sel_regiones = ipw.Dropdown(options=regiones_chile, value='TODO', description='Filtrar Región:')
cuadro_metricas = ipw.HTML(value="<i>Selecciona una región para ver el resumen...</i>")

def calcular_metricas_region(change):
    sel = change['new']
    
    # Filtrado lógico
    if sel == "TODO":
        df_filtrado = df_clean
    else:         
        df_filtrado = df_clean[df_clean['NOMBRE_REGION'] == sel]
        
    # Calculamos valores educativos reales de tu dataset
    total_estudiantes = len(df_filtrado)
    promedio_nem = round(df_filtrado["PTJE_NEM"].mean(), 1) if total_estudiantes > 0 else 0
    promedio_ranking = round(df_filtrado["PTJE_RANKING"].mean(), 1) if total_estudiantes > 0 else 0
    promedio_notas = round(df_filtrado["PROMEDIO_NOTAS"].mean(), 2) if total_estudiantes > 0 else 0

    # Construimos la tablita HTML interactiva
    cuadro_metricas.value = f"""
    <table border='1' style='border-collapse: collapse; width: 100%; text-align: center; border-color: #bdc3c7;'>
        <tr style='background-color: #34495e; color: white;'>
            <th colspan='2' style='padding: 8px;'>Resumen Académico - {sel}</th>
        </tr>
        <tr>
            <td style='padding: 6px; text-align: left;'><b>Total Postulantes:</b></td>
            <td style='padding: 6px;'>{total_estudiantes:,}</td>
        </tr>
        <tr style='background-color: #f9f9f9;'>
            <td style='padding: 6px; text-align: left;'><b>Promedio Notas (NEM):</b></td>
            <td style='padding: 6px; color: #2980b9;'><b>{promedio_notas}</b></td>
        </tr>
        <tr>
            <td style='padding: 6px; text-align: left;'><b>Puntaje Promedio NEM:</b></td>
            <td style='padding: 6px;'>{promedio_nem} pts</td>
        </tr>
        <tr style='background-color: #f9f9f9;'>
            <td style='padding: 6px; text-align: left;'><b>Puntaje Promedio Ranking:</b></td>
            <td style='padding: 6px;'>{promedio_ranking} pts</td>
        </tr>
    </table>
    """

# Conectamos el selector de regiones con la función de actualización
sel_regiones.observe(calcular_metricas_region, names='value')

# Ejecutamos una vez al inicio para que no aparezca vacío
calcular_metricas_region({'new': 'TODO'})

bloque_metricas = ipw.VBox([sel_regiones, ipw.HTML("<br>"), cuadro_metricas], 
                           layout=ipw.Layout(width='90%', padding='10px'))

# %% [markdown]
# #### PANEL 3: GRÁFICOS INTERACTIVOS (Usando Interactive)

# %%
# Gráfico A: Distribución de Notas filtrado por Dependencia de Colegio
def grafico_distribucion_notas(dependencia):
    plt.figure(figsize=(7, 4))
    if dependencia == "TODO":
        data_plot = df_clean
    else:
        data_plot = df_clean[df_clean['NOMBRE_DEPENDENCIA'] == dependencia]
        
    sns.histplot(data=data_plot, x='PROMEDIO_NOTAS', bins=35, kde=True, color='skyblue')
    plt.title(f'Distribución de Notas - {dependencia}', fontsize=12, fontweight='bold')
    plt.xlabel('Notas de Enseñanza Media')
    plt.ylabel('Cantidad')
    plt.show()

interact_notas = ipw.interactive(grafico_distribucion_notas, dependencia=dependencias_colegio)

# Gráfico B: Relación NEM vs Ranking según Tipo de Dependencia
def grafico_scatter_nem_ranking(dependencia):
    plt.figure(figsize=(7, 4))
    if dependencia == "TODO":
        data_plot = df_clean
    else:
        data_plot = df_clean[df_clean['NOMBRE_DEPENDENCIA'] == dependencia]
    
    # Muestra optimizada de 2000 datos para que la app responda al instante
    muestra = data_plot.sample(min(2000, len(data_plot)))
    plt.scatter(muestra['PTJE_NEM'], muestra['PTJE_RANKING'], alpha=0.4, s=12, color='purple')
    plt.title(f'NEM vs Ranking (Muestra) - {dependencia}', fontsize=12, fontweight='bold')
    plt.xlabel('Puntaje NEM')
    plt.ylabel('Puntaje Ranking')
    plt.show()

interact_scatter = ipw.interactive(grafico_scatter_nem_ranking, dependencia=dependencias_colegio)

# %% [markdown]
# #### NÚCLEO CENTRAL: ARMADO DE PESTAÑAS (TABS)

# %%
title_tab1 = ipw.HTML("<h3><b>📊 Estadísticas por Región</b></h3>")
title_tab2 = ipw.HTML("<h3><b>📈 Filtros de Distribución Educativa</b></h3>")

# Estructura de la Pestaña de Gráficos (Alineados horizontalmente con HBox)
bloque_graficos = ipw.HBox([
    ipw.VBox([title_tab2, interact_notas]),
    ipw.VBox([ipw.HTML("<br><br>"), interact_scatter])
], layout=ipw.Layout(gap='20px'))

# Creamos el contenedor global de pestañas
tab_dashboard = ipw.Tab()
tab_dashboard.children = [
    panel_login, 
    ipw.VBox([title_tab1, bloque_metricas], layout=ipw.Layout(padding='10px')), 
    bloque_graficos
]

# Títulos de las solapas
tab_dashboard.set_title(0, "🔑 Autenticación")
tab_dashboard.set_title(1, "📋 Métricas Regionales")
tab_dashboard.set_title(2, "📊 Análisis Gráfico")

# Desplegamos el componente final en pantalla
tab_dashboard