import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- FUNCIÓN PARA ENCONTRAR ARCHIVOS ---
def buscar_archivo(nombre):
    posibles_rutas = [nombre, os.path.join('csv', nombre)]
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            return ruta
    return None

# 1. CARGA DE DATOS
print("Buscando archivos...")
ruta_csv = buscar_archivo('ArchivoC_Adm2026REG.csv')
ruta_regiones = buscar_archivo('Libro_CódigosADM2026_ArchivoB.xlsx - Anexo - Region-Provincia-Comuna.csv')

df = pd.read_csv(ruta_csv, sep=';', low_memory=False)

# Diccionario de Regiones con NOMBRES CORTOS para que se lean bien
dict_regiones = {
    15: 'Arica y Parinacota', 1: 'Tarapacá', 2: 'Antofagasta', 3: 'Atacama',
    4: 'Coquimbo', 5: 'Valparaíso', 13: 'Metropolitana', 6: 'O\'Higgins',
    7: 'Maule', 16: 'Ñuble', 8: 'Biobío', 9: 'Araucanía',
    14: 'Los Ríos', 10: 'Los Lagos', 11: 'Aysén', 12: 'Magallanes'
}

dict_dependencia = {1: 'Particular Pagado', 2: 'Particular Subvencionado', 3: 'Municipal', 4: 'Servicio Local (SLEP)'}

# 2. LIMPIEZA
df['PROMEDIO_NOTAS'] = pd.to_numeric(df['PROMEDIO_NOTAS'].astype(str).str.replace(',', '.'), errors='coerce')
df['PTJE_NEM'] = pd.to_numeric(df['PTJE_NEM'], errors='coerce')
df['PTJE_RANKING'] = pd.to_numeric(df['PTJE_RANKING'], errors='coerce')

# Asegurarnos de que el código de región sea un número entero para mapearlo bien
df['CODIGO_REGION'] = pd.to_numeric(df['CODIGO_REGION'], errors='coerce').fillna(0).astype(int)

df_clean = df[(df['PROMEDIO_NOTAS'] > 0) & (df['PTJE_NEM'] > 0)].copy()

# Aplicar los diccionarios limpios
df_clean['NOMBRE_REGION'] = df_clean['CODIGO_REGION'].map(dict_regiones).fillna("Sin Registro")
df_clean['NOMBRE_DEPENDENCIA'] = df_clean['GRUPO_DEPENDENCIA'].map(dict_dependencia).fillna("Otra")

# 3. GRÁFICOS
print("Generando gráficos mejorados...")
sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(3, 2, figsize=(18, 20))

# A. Histograma
sns.histplot(df_clean['PROMEDIO_NOTAS'], bins=40, kde=True, ax=axes[0,0], color='skyblue')
axes[0,0].set_title('Distribución de Promedio de Notas', fontsize=14)

# B. Scatter Plot
sample = df_clean.sample(min(5000, len(df_clean)))
axes[0,1].scatter(sample['PTJE_NEM'], sample['PTJE_RANKING'], alpha=0.3, s=10, color='purple')
axes[0,1].set_title('Relación NEM vs Ranking', fontsize=14)

# C. Boxplot
sns.boxplot(data=df_clean, x='NOMBRE_DEPENDENCIA', y='PTJE_NEM', ax=axes[1,0], hue='NOMBRE_DEPENDENCIA', palette='Set2', legend=False)
axes[1,0].set_title('NEM por Tipo de Establecimiento', fontsize=14)
axes[1,0].tick_params(axis='x', rotation=15)

# D. EL ARREGLO: Gráfico de Barras Horizontales para las Regiones (Se lee 100% perfecto)
reg_counts = df_clean['NOMBRE_REGION'].value_counts().reset_index()
reg_counts.columns = ['Región', 'Cantidad']
# Filtramos "Sin Registro" si no aporta y graficamos
reg_counts = reg_counts[reg_counts['Región'] != 'Sin Registro']

sns.barplot(data=reg_counts, x='Cantidad', y='Región', ax=axes[1,1], hue='Región', palette='magma', legend=False)
axes[1,1].set_title('Estudiantes por Región (Ordenado)', fontsize=14)
axes[1,1].set_xlabel('Cantidad de Estudiantes')
axes[1,1].set_ylabel('') # Quitamos el título del eje Y porque es obvio

# E. Countplot
sns.countplot(data=df_clean, x='NOMBRE_DEPENDENCIA', ax=axes[2,0], hue='NOMBRE_DEPENDENCIA', palette='viridis', legend=False)
axes[2,0].set_title('Cantidad de Estudiantes por Dependencia', fontsize=14)
axes[2,0].tick_params(axis='x', rotation=15)

# F. Violin Plot
melted = df_clean[['PTJE_NEM', 'PTJE_RANKING']].melt(var_name='Tipo', value_name='Puntaje')
sns.violinplot(data=melted, x='Tipo', y='Puntaje', ax=axes[2,1], hue='Tipo', palette='muted', legend=False)
axes[2,1].set_title('Distribución de Puntajes: NEM vs Ranking', fontsize=14)

plt.tight_layout()
carpeta_salida = 'resultados'
os.makedirs(carpeta_salida, exist_ok=True) # Crea la carpeta mágicamente si no está
ruta_guardado = os.path.join(carpeta_salida, 'graficos_VIP.png')
plt.savefig(ruta_guardado, dpi=150)
print("🚀 ¡GRÁFICO VIP CREADO! Revisa el archivo 'graficos_VIP.png'")
