import datetime
import requests
import sqlite3
from prettytable import PrettyTable

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

# Función para generar el resumen
def generar_resumen():
    conexion = sqlite3.connect("finanzas_P.db")  # Actualización del nombre de la base de datos
    cursor = conexion.cursor()

    consulta = """
    SELECT 
        f.ticker,
        m.nombre_compania,
        MIN(f.date) AS fecha_desde,
        MAX(f.date) AS fecha_hasta
    FROM financial_data_polygon f
    LEFT JOIN maestra_tickers m ON f.ticker = m.ticker
    GROUP BY f.ticker
    ORDER BY f.ticker
    """
    
    cursor.execute(consulta)
    resultados = cursor.fetchall()
    conexion.close()

    # Crear la tabla para imprimir
    tabla = PrettyTable()
    tabla.field_names = ["Ticker", "Nombre de la Compañía", "Fecha Desde", "Fecha Hasta"]
    for fila in resultados:
        tabla.add_row(fila)

    print(tabla)

# Función para solicitar datos a la API
def solicitud_de_datos(ticker, fecha_inicio, fecha_fin):
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{fecha_inicio}/{fecha_fin}"
    api_key = "7EuDFFydcjhpG3G0JaoJmBUgpNDOZnp8"
    params = {"sort": "asc", "apiKey": api_key}
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        print("Pidiendo datos...")
        datos = response.json()
        if datos.get('results'):
            print("Datos obtenidos correctamente. Guardando en la base de datos...")
            guardar_datos_en_bd(ticker, datos['results'])
        else:
            print("No se encontraron resultados para el rango de fechas proporcionado.")
    else:
        print(f"Error al pedir los datos. Status code: {response.status_code}")
        print("Respuesta de error:", response.text)

# Función para guardar datos en la base de datos
def guardar_datos_en_bd(ticker, resultados):
    conexion = sqlite3.connect("finanzas_P.db")
    cursor = conexion.cursor()
    
    for dato in resultados:
        date = datetime.datetime.utcfromtimestamp(dato['t'] / 1000).strftime('%Y-%m-%d')  # Convertir timestamp a fecha
        volume = dato['v']
        vwap = dato['vw']
        open_price = dato['o']
        close_price = dato['c']
        high = dato['h']
        low = dato['l']
        transactions = dato['n']

        # Insertar datos en la tabla
        cursor.execute('''
            INSERT INTO financial_data_polygon (ticker, date, volume, vwap, open, close, high, low, transactions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ticker, date, volume, vwap, open_price, close_price, high, low, transactions))

    conexion.commit()
    conexion.close()
    print("Datos guardados en la base de datos correctamente.")

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
            ticker = input("Ingrese el ticker a pedir: ").upper()
            ticker = validar_ticker(ticker)
            if ticker:
                break

        while True:
            fecha_inicio = input("Ingrese la fecha de inicio (YYYY-MM-DD): ")
            fecha_inicio_valida = validar_fecha(fecha_inicio)
            if fecha_inicio_valida:
                break

        while True:
            fecha_fin = input("Ingrese la fecha fin (YYYY-MM-DD): ")
            fecha_fin_valida = validar_fecha(fecha_fin)
            if fecha_fin_valida:
                break

        if fecha_fin_valida < fecha_inicio_valida:
            print("La fecha de fin no puede ser anterior a la fecha de inicio. Por favor ingrese fechas válidas.")
            continue

        print(f"Pidiendo los datos solicitados para el ticker '{ticker}' desde {fecha_inicio} hasta {fecha_fin}.")
        solicitud_de_datos(ticker, fecha_inicio, fecha_fin)

    elif seleccion == 2:
        resumen = input("¿Deseas ver el Resumen del Ticker? (si/no): ").strip().lower()
        if resumen == "si":
            generar_resumen()
        else:
            print("Funcionalidad del gráfico en construcción.")

    elif seleccion == 3:
        print("Saliendo del programa...")
        break

    else:
        print("Opción no válida. Por favor, seleccione una opción entre 1 y 3.")