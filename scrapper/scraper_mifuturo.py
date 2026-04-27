import time
import io
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

def scraper_definitivo_numerico():
    url = "https://mifuturo.cl/buscador-de-empleabilidad-e-ingresos/"
    driver = webdriver.Chrome()
    driver.maximize_window()

    try:
        print("Entrando a la página...")
        driver.get(url)
        time.sleep(5)

        # 1. SELECCIONAR UNIVERSIDAD
        xpath_select = "//select[option[contains(text(), 'Universidad')]]"
        tipo_inst = driver.find_element(By.XPATH, xpath_select)
        Select(tipo_inst).select_by_visible_text("Universidad")
        print("'Universidad' seleccionado.")
        time.sleep(2)

        # 2. CLICK EN BUSCAR
        print(" Presionando Buscar...")
        xpath_btn = "//button[contains(., 'Buscar')] | //input[contains(@value, 'Buscar')]"
        btn_buscar = driver.find_element(By.XPATH, xpath_btn)
        driver.execute_script("arguments[0].click();", btn_buscar)

        print(" Esperando 15 segundos para la carga inicial...")
        time.sleep(15)

        datos_acumulados = []
        pag = 1

        # --- BUCLE INFINITO DE PAGINACIÓN ---
        while True:
            print(f"Procesando página {pag}...")
            
            html = driver.page_source
            try:
                # Usamos io.StringIO(html) para que la consola esté limpia
                tablas = pd.read_html(io.StringIO(html))
                df_temp = max(tablas, key=len) 
                datos_acumulados.append(df_temp)
                print(f" {len(df_temp)} filas capturadas de la página {pag}.")
            except Exception as e:
                print(f"Error leyendo tabla en pág {pag}: {e}")
                break

            # 4. PASAR A LA SIGUIENTE PÁGINA (Buscando el número exacto)
            siguiente_pag = pag + 1
            try:
                # Como tú dijiste, buscamos exactamente el NÚMERO que toca
                xpath_num = f"//a[text()='{siguiente_pag}'] | //span[text()='{siguiente_pag}'] | //a[contains(@class, 'paginate_button') and text()='{siguiente_pag}']"
                btn_next = driver.find_element(By.XPATH, xpath_num)
                
                driver.execute_script("arguments[0].click();", btn_next)
                pag += 1
                
                # Pausa para que la nueva página cargue antes de sacar la foto
                print(f" Saltando a la página {pag}...")
                time.sleep(4) 
            except:
                # Si falla, es porque llegamos a la 119 y ya no hay más números
                print(f" No se encontró el número {siguiente_pag}. Fin del recorrido.")
                break

        # 5. PROCESAMIENTO FINAL CON PANDAS
        if datos_acumulados:
            print("\n Juntando todas las páginas...")
            df_total = pd.concat(datos_acumulados, ignore_index=True)
            
            # Filtramos solo ingenierías
            filtro = df_total.iloc[:, 2].str.contains('ingenier', case=False, na=False)
            df_final = df_total[filtro]
            
            # Guardamos el CSV maestro
            df_final.to_csv('todas_las_ingenierias_chile.csv', index=False, sep=';', encoding='utf-16')
            print(f" ¡MISIÓN COMPLETA! Se guardaron {len(df_final)} ingenierías de todo Chile.")
        else:
            print(" No se recolectaron datos.")

    except Exception as e:
        print(f"❌ Error crítico: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scraper_definitivo_numerico()