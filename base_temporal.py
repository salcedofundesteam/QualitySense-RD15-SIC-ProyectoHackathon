import sqlite3

conn= sqlite3.connect("aguacates.db")
cursor= conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS  aguacates(
    id INTEGER PRIMARY KEY , 
    calidad TEXT,
    tamaño TEXT, 
    fecha TEXT,
    categoria TEXT
)
""")

conn.commit()
conn.close()

print("Base de datos creada")