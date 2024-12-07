import datetime
import requests
import sqlite3
import matplotlib.pyplot as plt
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
            ticker = input("Ingrese el ticker a graficar: ").upper()
            graficar_ticker(ticker)        
        
    elif seleccion == 3:
        print("Saliendo del programa...")
        break

    else:
        print("Opción no válida. Por favor, seleccione una opción entre 1 y 3.")