import pandas as pd
import os

def optimizar_base_de_datos(ruta_origen, ruta_destino, columnas_a_dejar, separador=';', encoding='utf-8'):
    if not os.path.exists(ruta_origen):
        print(f"Error: El archivo de origen no existe en: {ruta_origen}")
        return

    print(f"Procesando: {os.path.basename(ruta_origen)}")
    
    try:
        df = pd.read_csv(ruta_origen, sep=separador, encoding=encoding, usecols=columnas_a_dejar, low_memory=False)
        df = df[columnas_a_dejar]
        
        carpeta_destino = os.path.dirname(ruta_destino)
        if carpeta_destino and not os.path.exists(carpeta_destino):
            os.makedirs(carpeta_destino, exist_ok=True)
            
        df.to_csv(ruta_destino, index=False, sep=';', encoding='utf-8')
        print(f"Optimizado con exito -> {ruta_destino}")
        print(f"Filas procesadas: {len(df)}\n")
        
    except ValueError as e:
        print(f"Error de columnas: Algum nombre no coincide con el archivo original.")
        print(f"Detalle: {e}\n")
    except Exception as e:
        print(f"Error inesperado: {e}\n")

if __name__ == "__main__":
    print("Iniciando pipeline de optimizacion completo...\n")
    
    optimizar_base_de_datos(
        ruta_origen="dashboard/csv_dashboard/BaseINDICES-2020-2025.csv",
        ruta_destino="dashboard/csv_dashboard/clean_indices_dashboard.csv",
        columnas_a_dejar=[
            "Año", 
            "Nombre Region", 
            "Carrera Genérica", 
            "Matrícula primer año hombres", 
            "Matrícula primer año mujeres", 
            "Matrícula Total", 
            "Valor de arancel"
        ],
        separador=";",
        encoding="utf-8"
    )
    
    optimizar_base_de_datos(
        ruta_origen="dashboard/csv_dashboard/todas_las_ingenierias_chile.csv",
        ruta_destino="dashboard/csv_dashboard/clean_kpis_nacional.csv",
        columnas_a_dejar=[
            "Institución", 
            "Carrera", 
            "Retención de 1er año", 
            "Empleabilidad al 2º Año", 
            "Duración Real (semestres)", 
            "Ingreso promedio al 4° año"
        ],
        separador=";",
        encoding="utf-16"
    )
    
    optimizar_base_de_datos(
        ruta_origen="csv/ArchivoB_Adm2025.csv",
        ruta_destino="dashboard/csv_dashboard/clean_demre_2025.csv",
        columnas_a_dejar=[
            "ID_aux", 
            "GRUPO_DEPENDENCIA"
        ],
        separador=";",
        encoding="utf-8"
    )