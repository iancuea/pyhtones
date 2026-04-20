from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://mifuturo.cl/buscador-de-empleabilidad-e-ingresos/")

print("🔍 Iniciando diagnóstico de la página...")
# Esperamos un poco a que cargue todo
import time
time.sleep(10)

# 1. Contar cuántos iframes hay
iframes = driver.find_elements(By.TAG_NAME, "iframe")
print(f"✅ Se encontraron {len(iframes)} iframes en total.")

# 2. Listar los IDs y fuentes de los iframes
for i, frame in enumerate(iframes):
    f_id = frame.get_attribute("id")
    f_name = frame.get_attribute("name")
    f_src = frame.get_attribute("src")
    print(f"--- Iframe #{i} ---")
    print(f"ID: {f_id} | Name: {f_name}")
    print(f"Fuente: {f_src[:100]}...") # Solo los primeros 100 caracteres

driver.quit()