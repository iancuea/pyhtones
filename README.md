#  Dashboard de Analítica Educacional & Modelos de IA

Este proyecto es un entorno interactivo de software desarrollado en **Python** diseñado para analizar el panorama de las carreras de ingeniería en Chile. Utiliza datos oficiales del Servicio de Información de Educación Superior (SIES) y MiFuturo, acoplados con algoritmos de **Machine Learning** (Supervisados y No Supervisados) para proyectar ingresos reales, agrupar perfiles universitarios y visualizar brechas multidimensionales.

---

##  Requisitos Previos

* **Python 3.10** o superior.
* **Git** (para clonar el repositorio).
* **Instalar requirements.txt** en su **venv** con los siguentes comandos si está en windows:
```
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```
---

##  Instrucciones de Instalación y Ejecución

* 1. Clonar el repositorio e ingresar a la carpeta.
* 2. En la carpeta de la ruta \pyhtones\dashboard ejecutar el archivo dashboard_final.ipynb, la primera ejecucion demora por la generación de mapas interactivos, luego ya es rápido.
* 3. Ingresar al dashboard con el usuario "admin" y contraseña "admin".


# Estructura de carpeta dashboard

```
dashboard/
├── csv_dashboard
│   ├── BaseINDICES-2020-2025.csv
│   ├── clean_kpis.csv
│   └── todas_las_ingenierias_chile.csv
├── html_mapas
│   ├── mapa_emp.html
│   ├── mapa_ret.html
│   └── mapa_sue.html
├── dashboard_final.ipynb
├── dashboard_ml.ipynb
├── kmeans.py
├── pca.py
├── preprocesamiento.py
└── rlm.py
```
