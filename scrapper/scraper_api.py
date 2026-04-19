import requests
import pandas as pd
import json


def scraper_api_pokemons():
    """
    Obtener datos de Pokémon usando la API pública PokéAPI
    """
    url = "https://pokeapi.co/api/v2/pokemon"
    
    # Obtener lista de pokémon
    response = requests.get(url)
    
    if response.status_code == 200:
        datos_api = response.json()
        
        # Extraer información de los primeros 20 pokémon
        pokemons = []
        for pokemon in datos_api['results'][:20]:
            # Obtener detalles de cada pokémon
            details = requests.get(pokemon['url']).json()
            
            pokemons.append({
                'nombre': pokemon['name'],
                'id': details['id'],
                'altura': details['height'],
                'peso': details['weight'],
                'tipo': ', '.join([t['type']['name'] for t in details['types']])
            })
            #print(f"Descargado: {pokemon['name']}")
        
        # Crear DataFrame
        df = pd.DataFrame(pokemons)
        print("\n" + df.to_string(index=False))
        
        # Guardar
        df.to_csv('pokemons.csv', index=False, encoding='utf-8', sep=';')
        print("\nDatos guardados en 'pokemons.csv'")
        
        return df
    else:
        print(f"Error: {response.status_code}")
        return None


def scraper_api_openweather():
    """
    Obtener datos del clima usando OpenWeatherMap API
    Nota: Requiere API key gratuita (se obtiene en openweathermap.org)
    """
    # Debes registrarte en https://openweathermap.org/api para obtener tu API key
    API_KEY = "tu_api_key_aqui"  # Reemplaza con tu API key
    
    ciudad = "Santiago"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={API_KEY}&units=metric&lang=es"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            datos = response.json()
            
            print(f"Ciudad: {datos['name']}")
            print(f"Temperatura: {datos['main']['temp']}°C")
            print(f"Sensación térmica: {datos['main']['feels_like']}°C")
            print(f"Humedad: {datos['main']['humidity']}%")
            print(f"Descripción: {datos['weather'][0]['description']}")
            print(f"Velocidad del viento: {datos['wind']['speed']} m/s")
        else:
            print(f"Error: {response.status_code}")
            print("Verifica tu API key y conexión")
    except Exception as e:
        print(f"Error: {e}")




if __name__ == "__main__":
    """print("=" * 60)
    print("1. API PokéAPI - Pokémon")
    print("=" * 60)"""
    scraper_api_pokemons()
    
    """print("\n" + "=" * 60)
    print("2. API OpenWeatherMap - Clima")
    print("=" * 60)
    print("(Requiere API key - omitido)")"""
    # scraper_api_openweather()
    
