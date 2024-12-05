import sqlite3

# Crear o conectar a la base de datos
def crear_base_datos():
    conexion = sqlite3.connect("finanzas.db")  # Crea el archivo finanzas.db si no existe
    cursor = conexion.cursor()

    # Crear la tabla
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS datos_financieros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            fecha TEXT NOT NULL,
            apertura REAL,
            maximo REAL,
            minimo REAL,
            cierre REAL,
            volumen INTEGER
        )
    ''')
    print("Tabla 'datos_financieros' creada correctamente (si no existía).")

    # Cerrar la conexión
    conexion.commit()
    conexion.close()

# Ejecutar la creación de la base de datos y la tabla
if __name__ == "__main__":
    crear_base_datos()