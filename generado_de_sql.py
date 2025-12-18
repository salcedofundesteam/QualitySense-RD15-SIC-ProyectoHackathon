#Chatbot interactivo para responder preguntas estadoiticas de la produccion  de la planta

#con este chatbot los operadores tienen la oportinadad de dar seguimiento a la 
#produccion diariaria registrada en la base de datos de aguacates procesados en la planta

#mediante este codigo se genrrara una consulta en SQL tomando el diccionario "analizado" que se 
# va a devolver del codigo del nlp
# 

#el peso promedio no se si se va extraer, primero debo de saber si el pso promedio
#ser una de las variables que voy a obtener
from typing import Optional, Tuple, Dict, Any

def plazos_para_sql (tp: Dict[str, Any])-> Tuple [str, tuple]:
    if not tp:
        return ("DATE (timestamp)= DATE('now', 'localtime')",  ()) 
    ttype =tp.get("type")
    val = tp.get("value")

    if ttype =="day_named":
        if val == "hoy":
            return ("DATE(timestamp)=DATE('now','localtime')", ())
        if val == "ayer":
            return ("DATE(timestamp)=DATE('now','localtime','-1 day')", ())
        if ttype == "hours":
            return ("DATE(timestamp)= DATE ('now', 'localtime',?)", (f"-{int(val)} hours",))
    
    return ("DATE(timestamp)=DATE('now','localtime')", ())

#funcion para generr un SQl y plos parametrostomando el diccionario devuelto 
#de la funcion "preguntas" del nlp 

def generar_sql (analizado):
    intentos = analizado.get("intentos")
    tamaño = analizado.get("tamaño")
    calidad= analizado.get("calidad")
    tp = analizado.get("tiempo_promedio")

    #prapar filtros y parametros para realizar las consultas 

    filtros = []
    parametros =[]

    if tamaño:
        filtros.append("tamaño = ?")
        parametros.append(tamaño)
    if calidad:
        filtros.append("calidad=?")
        parametros.append(calidad)

    tp_sql, tp_parametros = plazos_para_sql(tp)
    if tp_parametros: 
        parametros.extend(tp_parametros)
        filtros.append(tp_sql)
    else:
        filtros.append(tp_sql)
    
    clausula_where = "AND".join(filtros) if filtros else "1=1"

    if intentos == "count":
        sql = f"SELECT COUNT(*) AS resultado FROM aguacates WHERE {clausula_where}", 
    
        return (sql, tuple(parametros))

    if intentos == "count_by_quality" or (intentos == "count" and not tamaño and not calidad and "por calidad" in analizado.get("raw","").lower()):
        #para devolver el conteo por calidad   
        sql = f"SELECT calidad, COUNT(*) AS C FROM aguacates WHERE{clausula_where} GROUP BYcalidad;" 
        return (sql, tuple(parametros))


    if intentos == "avg_weight" or analizado.get("raw","").lower().find("promedio") != -1 or analizado.get("raw","").lower().find("peso") != -1:
        sql = f"SELECT peso_promedio AS avg_weight, COUNT(*) AS total FROM aguacates WHERE {clausula_where}" 

    if intentos == "most_common_size":
        sql = f"SELECT tamaño, COUNT(*) AS T FROM  aguacates WHERE {clausula_where} GROUP BY tamaño ORDER BY T DESC LIMIT 1;" 
        return (sql, tuple(parametros))
    
    if intentos == "trend_hour":
        sql = f"""
        SELECT 
        strftime('%Y-%m-%d %H:00:00', timestamp) AS horas,
        COUNT (*) AS H
        FROM aguacates
        WHERE {clausula_where}
        GROUP BY horas
        ORDER BY horas;
        """
        return (sql, tuple(parametros))
    
    return (f"SELECT COUNT(*) AS resultados FROM aguacates WHERE{clausula_where},", tuple(parametros))



