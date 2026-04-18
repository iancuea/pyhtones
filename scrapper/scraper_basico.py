import requests
from bs4 import BeautifulSoup
import pandas as pd

def scraper_quotes():
    """
    Scraper de citas de la página http://quotes.toscrape.com/
    """
    url = "http://quotes.toscrape.com/"
    
    # Obtener el contenido HTML
    response = requests.get(url)
    response.encoding = 'utf-8'
    
    # Verificar que la solicitud fue exitosa
    if response.status_code == 200:
        # Parsear el HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Encontrar todos los divs con clase 'quote'
        quotes = soup.find_all('div', class_='quote')
        
        # Extraer datos
        datos = []
        for quote in quotes:
            # Extraer el texto
            texto = quote.find('span', class_='text').get_text(strip=True)
            # Extraer el autor
            autor = quote.find('small', class_='author').get_text(strip=True)
            # Extraer los tags
            tags = [tag.get_text(strip=True) for tag in quote.find_all('a', class_='tag')]
            
            datos.append({
                'texto': texto,
                'autor': autor,
                'tags': ', '.join(tags)
            })
        
        # Crear DataFrame
        df = pd.DataFrame(datos)
        print(df.to_string())
        
        # Guardar en CSV
        df.to_csv('quotes.csv', index=False, encoding='utf-8', sep=';')
        print("\nDatos guardados en 'quotes.csv'")
        
        return df
    else:
        print(f"Error: {response.status_code}")
        return None


def scraper_wikipedia():
    """
    Scrape información de una página de Wikipedia
    """
    url = "https://es.wikipedia.org/wiki/Python_(lenguaje_de_programaci%C3%B3n)"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Obtener el título
        titulo = soup.find('h1', class_='firstHeading').get_text()
        print(f"Título: {titulo}\n")
        
        # Obtener los párrafos principales
        paragrafos = soup.find_all('p')[:3]  # Primeros 3 párrafos
        
        print("Primeros párrafos:")
        for i, p in enumerate(paragrafos, 1):
            texto = p.get_text(strip=True)
            if len(texto) > 100:  # Solo párrafos con contenido significativo
                print(f"\n{i}. {texto[:300]}...")
    else:
        print(f"Error: {response.status_code}")


if __name__ == "__main__":
    # print("1. Scrapeando Quotes")
    scraper_quotes()
    
    #print("2. Scrapeando Wikipedia")
    #scraper_wikipedia()
