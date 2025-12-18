"""
Estas consultas van a permitir obtener las estadisticas diarias
de la planta , mediantes estas funciones en ell chatbot el operador interactuar  
demanera mas fluida con el programa.
"""
from conexion import consulta_db

def estadisticas_diarias (): #La funcion sirve para obtener los totalesy categorias de los aguacates pasados por la cinta.
    sql = """
        SELECT
            COUNT(*) as total,
            calidad,
            SUM(CASE WHEN tamaño = 'Small' THEN 1 ELSE 0 END) AS small,
            SUM(CASE WHEN tamaño = 'Medium' THEN 1 ELSE 0 END) AS medium,
            SUM(CASE WHEN tamaño = 'Large' THEN 1 ELSE 0 END) AS large
        FROM aguacates
        WHERE DATE(fecha) = DATE('now','localtime');
            """
    resultados = consulta_db (sql)
    return resultados if resultados else [{"total": 0, "small": 0, "medium": 0, "large": 0}]

#una funcion para clacular los aguacates pasados por la cinta en la ultima hora

def contados_ultima_hora ():
    sql = """
        SELECCT
            COUNT(*)AS aguacates__en_ultima_hora
        FROM aguacates
        WHERE fecha >= DATETIME('now','localtime','-1 hour');
                """
    resultado = consulta_db (sql)
    return resultado [0]["aguacates_en_ultima_hora"] if resultado else 0

#para evaluar cual es el tama;o que mas se repitio o se ha repetido en el proceso,
#  se crea una funcion para evaluar cual es el tama;o, la funcion realiza un select en la base de
#datos y los filtrara y ordenara de manera descendente para obtener el tama;o mas frecuente.

def tamaño_mas_frecuente():
    sql ="""
        SELECT
            tamaño,
            COUNT(*) AS c
        FROM aguacates
        GROUP BY tamaño
        ORDER BY c DESC
        LIMIT 1;
            """
    respuesta = consulta_db(sql)
    return respuesta[0]  if respuesta else {}

def categoria_de_calidad():
    sql ="""
         SELECT 
            calidad,
            COUNT(*) AS cantidad_por_calidad
        FROM aguacates
        GROUP BY calidad
        ORDER BY calidad;
        """
    respuesta = consulta_db(sql)
    return respuesta
