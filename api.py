# Api key= SKFVCGWGLDMAR34N (Alpha Vantage)
import requests

def obtener_datos_alpha_vantage(ticker, fecha_inicio, fecha_fin):
    api_key = "SKFVCGWGLDMAR34N"
    base_url = "https://www.alphavantage.co/query"
    
    parametros = {
        "function": "TIME_SERIES_DAILY",  # Datos diarios ajustados
        "symbol": ticker,
        "apikey": api_key,
        "outputsize": "full"  # Devuelve datos históricos completos
    }
    
    respuesta = requests.get(base_url, params=parametros)

    if respuesta.status_code == 200:
        datos = respuesta.json()
        # Filtrar fechas y devolver solo las relevantes
        serie_temporal = datos.get("Time Series (Daily)", {})
        datos_filtrados = {
            fecha: info for fecha, info in serie_temporal.items()
            if fecha_inicio <= fecha <= fecha_fin
        }
        return datos_filtrados
    else:
        print("Error al consultar la API:", respuesta.status_code)
        return None

# Ejemplo de uso
ticker = "AAPL"
fecha_inicio = "2024-11-01"
fecha_fin = "2024-11-07"

datos = obtener_datos_alpha_vantage(ticker, fecha_inicio, fecha_fin)
if datos:
    print(f"Datos para {ticker} entre {fecha_inicio} y {fecha_fin}:")
    for fecha, info in datos.items():
        print(f"{fecha}: {info}")