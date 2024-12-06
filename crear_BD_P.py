import sqlite3
import json

# Creo BD y tabla para acumular historia
def crear_base_de_datos():
    conexion = sqlite3.connect("finanzas_P.db")
    cursor = conexion.cursor()

    # Creo la tabla 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS financial_data_polygon (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            date DATE NOT NULL,
            volume REAL NOT NULL,
            vwap REAL NOT NULL,
            open REAL NOT NULL,
            close REAL NOT NULL,
            high REAL NOT NULL,
            low REAL NOT NULL,
            transactions INTEGER NOT NULL
        )
    ''')
    
    conexion.commit()
    conexion.close()


# ejecuto la funcion para crear la BD y tabla
crear_base_de_datos()
print("Base de datos y tabla creadas exitosamente.")

####################################################################################3

# Creo la tabla maestra de tickers vacia
conexion = sqlite3.connect("finanzas_P.db")
cursor = conexion.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS maestra_tickers (
    ticker TEXT PRIMARY KEY,         -- Símbolo bursátil único
    nombre_compania TEXT NOT NULL    -- Nombre completo de la compañía
)
""")
conexion.commit()
conexion.close()

print("Tabla 'maestra_tickers' creada.")

# Importo tabla maestra de tickers desde un archivo json que encontré en KAggle
archivo_json = "company_tickers.json"

# Conexión a la base de datos
conexion = sqlite3.connect("finanzas_P.db")
cursor = conexion.cursor()

# leo el archivo JSON y cargo datos
with open(archivo_json, "r", encoding="utf-8") as archivo:
    datos = json.load(archivo)
    registros = [(valor["ticker"], valor["title"]) for valor in datos.values()]

# Inserto los datos del archivo en la tabla maestra de la BD
cursor.executemany("""
INSERT OR IGNORE INTO maestra_tickers (ticker, nombre_compania)
VALUES (?, ?)
""", registros)

# Confirmar cambios y cerrar conexión
conexion.commit()
conexion.close()

print(f"Se han insertado {len(registros)} registros en la tabla maestra de tickers.")