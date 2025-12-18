#Crear una interfaz en la cual el operador del programa pueda operar e
#interactuar con ella para otener estadisticas de los registrado en la
#base de datos que guarda la informacion del los aguagates procesados 
# en la planta

#establecer conexion con la base de datos de SQLite 
import sqlite3

PATH = "avocados_detection.db"

#funcion para realizar consultas y conectar a la base de datos
def obtener_conexion ():
    conn = sqlite3.connect(PATH)
    conn.row_factory = sqlite3.Row
    return conn
#Funcion para realizar las consultad del Select que luego seran usadas
#por el chatbot para interactuar con el operador de la pplanta,
#luego de conectarme a  la base de datos puedo reslizar diferentes consultas

def consulta_db (sql:str, params : tuple = ()):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    resultados = cursor.fetchall()
    conn.close()

    return [dict(row)for row in resultados]


def ejecucion(sql:str, params: tuple = ()):
    conn =obtener_conexion ()
    cursor = conn.cursor()


    cursor.execute(sql,params)
    conn.commit()

    conn.close()

    return True






