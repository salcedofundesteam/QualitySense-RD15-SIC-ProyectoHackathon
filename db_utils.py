import sqlite3
from datetime import datetime


DB_NAME = 'avocado_detections.db'

def create_table():
    """Crea la tabla de detecciones si no existe."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            total_count INTEGER,
            small_count INTEGER,
            medium_count INTEGER,
            large_count INTEGER
        )
    """)
    conn.commit()
    conn.close()
    print(f"Tabla 'detections' asegurada en {DB_NAME}")

def log_detection(counts):
    """
    Aqui lo que hacemos en el registra de los conteos de aguacates clasificados en la base de datos.
    :param counts: Diccionario con los conteos: {'Total': X, 'Small': Y, 'Medium': Z, 'Large': W}
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Inserta el registro de conteo por frame
    cursor.execute("""
        INSERT INTO detections (timestamp, total_count, small_count, medium_count, large_count)
        VALUES (?, ?, ?, ?, ?)
    """, (
        timestamp,
        counts['Total'],
        counts['Small'],
        counts['Medium'],
        counts['Large']
    ))

    conn.commit()
    conn.close()

