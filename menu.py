import requests
import datetime
import sqlite3

# Función para mostrar el menú
def mostrar_menu():
    print("\n--- Menú ---")
    print("1. Actualizar Datos")
    print("2. Visualizar Datos")
    print("3. Salir")

# Función para validar fechas
def validar_fecha(fecha_str):
    try:
        fecha = datetime.datetime.strptime(fecha_str, "%Y-%m-%d")
        return fecha
    except ValueError:
        print("Fecha inválida. Por favor, use el formato YYYY-MM-DD.")
        return None

# Función para validar ticker
def validar_ticker(ticker):
    try:
        float(ticker)
        print("Ticker inválido. No puede ser un número.")
        return None
    except ValueError:
        if isinstance(ticker, str) and ticker.strip():
            return ticker.strip()
        else:
            print("Ticker inválido. Debe ser un texto no vacío.")
            return None

# Función para obtener los datos de la API de Alpha Vantage
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
        serie_temporal = datos.get("Time Series (Daily)", {})
        datos_filtrados = {
            fecha: info for fecha, info in serie_temporal.items()
            if fecha_inicio <= fecha <= fecha_fin
        }
        return datos_filtrados
    else:
        print("Error al consultar la API:", respuesta.status_code)
        return None

# Función para guardar los datos en la base de datos
def guardar_datos_en_db(datos, ticker):
    try:
        conexion = sqlite3.connect("finanzas.db")
        cursor = conexion.cursor()

        for fecha, info in datos.items():
            apertura = float(info["1. open"])
            maximo = float(info["2. high"])
            minimo = float(info["3. low"])
            cierre = float(info["4. close"])
            volumen = int(info["5. volume"])

            cursor.execute('''
                INSERT INTO datos_financieros (ticker, fecha, apertura, maximo, minimo, cierre, volumen)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (ticker, fecha, apertura, maximo, minimo, cierre, volumen))

        conexion.commit()
        print("Datos guardados en la base de datos con éxito.")

    except sqlite3.Error as e:
        print("Error al guardar los datos en la base de datos:", e)

    finally:
        conexion.close()

# Ciclo principal
while True:
    mostrar_menu()
    try:
        seleccion = int(input("¿Cuál de las siguientes acciones deseas realizar? "))
    except ValueError:
        print("Por favor, ingrese un número válido.")
        continue

    if seleccion == 1:
        while True:
            ticker = input("Ingrese el ticker a pedir: ")
            ticker = validar_ticker(ticker)
            if ticker:
                break

        while True:
            fecha_inicio = input("Ingrese la fecha de inicio (YYYY-MM-DD): ")
            if validar_fecha(fecha_inicio):
                break

        while True:
            fecha_fin = input("Ingrese la fecha fin (YYYY-MM-DD): ")
            if validar_fecha(fecha_fin):
                break

        print(f"Pidiendo los datos solicitados para el ticker '{ticker}' desde {fecha_inicio} hasta {fecha_fin}.")

        # Obtener los datos de la API
        datos = obtener_datos_alpha_vantage(ticker, fecha_inicio, fecha_fin)
        
        if datos:
            # Guardar los datos en la base de datos
            guardar_datos_en_db(datos, ticker)
    
    elif seleccion == 2:
        resumen = input("¿Deseas ver el Resumen del Ticket? (sí/no): ").strip().lower()
        if resumen == "sí":
            print("Mostrando resumen de los datos...")
        else:
            print("Mostrando gráfico del ticker...")
    
    elif seleccion == 3:
        print("Saliendo del programa...")
        break
    
    else:
        print("Opción no válida. Por favor, seleccione una opción entre 1 y 3.")