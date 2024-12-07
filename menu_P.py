import datetime
import requests
import sqlite3
import matplotlib.pyplot as plt
from prettytable import PrettyTable
import matplotlib.dates as mdates

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

# Función para hacer la solicitud de datos a la API
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

        

# Función para generar el resumen
def generar_resumen():
    conexion = sqlite3.connect("finanzas_P.db")
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

# Función para graficar un ticker
def graficar_ticker(ticker):
    conexion = sqlite3.connect("finanzas_P.db")
    cursor = conexion.cursor()

    consulta = """
    SELECT date, close FROM financial_data_polygon
    WHERE ticker = ?
    ORDER BY date ASC
    """
    cursor.execute(consulta, (ticker,))
    resultados = cursor.fetchall()
    conexion.close()

    if not resultados:
        print(f"No hay datos almacenados para el ticker '{ticker}'.")
        return

    fechas = [fila[0] for fila in resultados]
    precios_cierre = [fila[1] for fila in resultados]

    plt.figure(figsize=(10, 6))
    plt.plot(fechas, precios_cierre, marker="o", linestyle="-", color="b", label=f"{ticker} - Precio de Cierre")
    plt.xlabel("Fecha")
    plt.ylabel("Precio de Cierre (USD)")
    plt.title(f"Evolución del Precio de Cierre para {ticker}")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


# Función para graficar precio con volumen


def graficar_con_volumen(ticker):
    conexion = sqlite3.connect("finanzas_P.db")
    cursor = conexion.cursor()
    
    consulta = """
    SELECT date, close, volume FROM financial_data_polygon
    WHERE ticker = ?
    ORDER BY date ASC
    """
    cursor.execute(consulta, (ticker,))
    resultados = cursor.fetchall()
    conexion.close()

    if not resultados:
        print(f"No hay datos almacenados para el ticker '{ticker}'.")
        return

    fechas = [fila[0] for fila in resultados]
    precios_cierre = [fila[1] for fila in resultados]
    volumen = [fila[2] for fila in resultados]

    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Gráfico de precio de cierre
    ax1.plot(fechas, precios_cierre, color='b', label='Precio de Cierre', marker='o')
    ax1.set_xlabel('Fecha')
    ax1.set_ylabel('Precio de Cierre (USD)', color='b')
    ax1.tick_params(axis='y', labelcolor='b')

    # Gráfico de volumen en el segundo eje Y
    ax2 = ax1.twinx()
    ax2.bar(fechas, volumen, color='g', alpha=0.3, label='Volumen')
    ax2.set_ylabel('Volumen', color='g')
    ax2.tick_params(axis='y', labelcolor='g')

    # Mejorar la visualización de las fechas en el eje X
    plt.xticks(rotation=45)  # Rotar las fechas
    plt.tight_layout()  # Ajustar el espaciado
    plt.title(f'Evolución del Precio de Cierre y Volumen para {ticker}')
    plt.show()

# Función para graficar comparativa entre precio apertura y precio cierre
def graficar_comparativa(ticker):
    conexion = sqlite3.connect("finanzas_P.db")
    cursor = conexion.cursor()
    
    consulta = """
    SELECT date, open, close FROM financial_data_polygon
    WHERE ticker = ?
    ORDER BY date ASC
    """
    cursor.execute(consulta, (ticker,))
    resultados = cursor.fetchall()
    conexion.close()

    if not resultados:
        print(f"No hay datos almacenados para el ticker '{ticker}'.")
        return

    fechas = [fila[0] for fila in resultados]
    apertura = [fila[1] for fila in resultados]
    cierre = [fila[2] for fila in resultados]

    plt.figure(figsize=(10, 6))
    plt.plot(fechas, apertura, marker="o", linestyle="-", color="r", label="Precio de Apertura")
    plt.plot(fechas, cierre, marker="o", linestyle="-", color="b", label="Precio de Cierre")
    plt.xlabel("Fecha")
    plt.ylabel("Precio (USD)")
    plt.title(f"Comparativa entre Precios de Apertura y Cierre para {ticker}")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()    


    
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
        resumen = input("¿Deseas ver el Resumen del Tickers disponibles? (si/no): ").strip().lower()
        if resumen == "si":
            generar_resumen()
            continue  # Esto asegura que el programa vuelva al menú y no siga pidiendo el ticker para graficar
        else:
            print("\n--- Opciones de Gráficos ---")
            print("1. Evolución del Precio de Cierre")
            print("2. Evolución con Volumen")
            print("3. Comparativa entre Precios (Apertura vs Cierre)")
            grafico_opcion = input("¿Qué gráfico deseas ver? (1/2/3): ").strip()

            if grafico_opcion == "1":
                ticker = input("Ingrese el ticker a graficar: ").upper()
                graficar_ticker(ticker)
            elif grafico_opcion == "2":
                ticker = input("Ingrese el ticker a graficar: ").upper()
                graficar_con_volumen(ticker)
            elif grafico_opcion == "3":
                ticker = input("Ingrese el ticker a graficar: ").upper()
                graficar_comparativa(ticker)
            else:
                print("Opción no válida. Volviendo al menú principal.")

                  
    elif seleccion == 3:
        print("Saliendo del programa...")
        break

    else:
        print("Opción no válida. Por favor, seleccione una opción entre 1 y 3.")