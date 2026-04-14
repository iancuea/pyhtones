import time
import pandas as pd
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

def scraper_detallado_carreras():
    url = "https://www.mifuturo.cl/buscador-de-estadisticas-por-carrera/"
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Opcional: correr sin ver la ventana
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(url)
        # Maximizamos para que los botones siempre sean visibles
        driver.maximize_window()
        wait = WebDriverWait(driver, 20)

        # 1. Aplicamos los filtros de Tecnología y Universidad
        print("🔍 Aplicando filtros...")
        area_select = wait.until(EC.visibility_of_element_located((By.XPATH, "//select[option[contains(text(), 'Tecnología')]]")))
        Select(area_select).select_by_visible_text("Tecnología")
        
        tipo_select = wait.until(EC.visibility_of_element_located((By.XPATH, "//select[option[contains(text(), 'Universidad')]]")))
        Select(tipo_select).select_by_visible_text("Universidad")
        
        boton_buscar = driver.find_element(By.XPATH, "//button[contains(text(), 'Buscar')]")
        driver.execute_script("arguments[0].click();", boton_buscar)
        
        time.sleep(5) # Esperamos que la tabla cargue

        # 2. Obtenemos las filas de la tabla
        filas = driver.find_elements(By.XPATH, "//table//tr[td]")
        total_carreras = len(filas)
        print(f"Se encontraron {total_carreras} carreras. Iniciando extracción de sueldos...")

        datos_finales = []

        for i in range(total_carreras):
            # RE-BUSCAMOS las filas para evitar el error de 'Stale Element'
            filas = driver.find_elements(By.XPATH, "//table//tr[td]")
            columnas = filas[i].find_elements(By.TAG_NAME, "td")
            
            # El nombre de la carrera está en la segunda columna (índice 1)
            # Limpiamos el texto para quitar el "Ver estadísticas"
            nombre_carrera = columnas[1].text.replace("Ver estadísticas", "").strip()
            
            print(f"🚀 Procesando: {nombre_carrera} ({i+1}/{total_carreras})")
            
            # Clic en el botón "Ver estadísticas" de esa fila
            boton_ver = columnas[1].find_element(By.TAG_NAME, "a")
            driver.execute_script("arguments[0].click();", boton_ver)
            
            # ESPERA A QUE CARGUE LA FICHA MODAL
            # Esperamos que el texto 'Ingresos brutos mensuales' aparezca
            wait.until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Ingresos brutos')]")))
            time.sleep(2) # Pausa para que el gráfico cargue los valores
            
            try:
                # Buscamos todos los elementos que tengan el signo '$' (los valores del gráfico)
                elementos_sueldo = driver.find_elements(By.XPATH, "//*[contains(text(), '$')]")
                sueldos = [s.text for s in elementos_sueldo if len(s.text) > 5]
                
                # Según tu imagen: el primer valor es el 5to año y el último es el 1er año
                sueldo_1_ano = sueldos[-1] if len(sueldos) > 0 else "N/D"
                sueldo_5_ano = sueldos[0] if len(sueldos) > 0 else "N/D"

                datos_finales.append({
                    'Carrera': nombre_carrera,
                    'Sueldo 1er Año': sueldo_1_ano,
                    'Sueldo 5to Año': sueldo_5_ano
                })
                print(f"✅ Capturado: 1er Año {sueldo_1_ano} | 5to Año {sueldo_5_ano}")
            
            except Exception as e_inner:
                print(f"⚠️ Error extrayendo datos de {nombre_carrera}: {e_inner}")

            # 3. CERRAR LA VENTANA MODAL (Botón azul 'Cerrar' abajo a la derecha)
            print("💾 Cerrando ficha...")
            btn_cerrar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Cerrar')]")))
            driver.execute_script("arguments[0].click();", btn_cerrar)
            
            # Esperar un momento a que el modal desaparezca totalmente antes de la siguiente fila
            time.sleep(2)

        # 4. Guardar resultados en el CSV para tu informe de la UACh
        df = pd.DataFrame(datos_finales)
        df.to_csv('sueldos_tecnologia_uach.csv', index=False, sep=';', encoding='utf-16')
        print(f"\n✅ Proceso completado. Archivo 'sueldos_tecnologia_uach.csv' creado con {len(df)} registros.")

    except Exception as e:
        print(f"❌ Error general: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scraper_detallado_carreras()