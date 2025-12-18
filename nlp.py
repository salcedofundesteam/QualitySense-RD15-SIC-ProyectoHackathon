
#desarrollo del chatbot para interactuar con el operador de manera fluida
import re
from typing import Optional, Dict, Any
import spacy


nlp_sp = spacy.load("es_core_news_md")

#crear un mapa con las posisles palabraas que el operador podria entraren el programa
#y mapearlas a los valores que estan en la base de datos para poder realizar las consultas

#MAPEO DE LAS ENTRADAS PARA ESTANDIRIZAER LOS VALORES IINGRESADOS POR EL OPERADOR Y QUE
#TODOS LOS VALORES SEAN GUARDADOS EN UN MISMO FORMATO.

MAP ={
"pequeño": "Small", "pequeno": "Small", "pequeña": "Small", "pequena": "Small",
"small": "Small", "s": "Small"}
MAP.update ({
    "mediano": "Medium", "mediana": "Medium", "medium": "Medium", "m": "Medium"})
MAP.update({
    "grande": "Large", "large": "Large",  "l": "Large"})
CALIDAD_MAP = {
    "a": "A", "b": "B", "c": "C", "calidad a": "A", "calidad b": "B", "calidad c": "C" }

PALABRAS_CLAVES = { "count": ["cuánt", "cuantos", "cantidad", "contar", "¿cuántos", "numero", "número"],
    "avg_weight": ["promedio", "peso promedio", "peso medio", "promedio de peso", "peso"],
    "most_common_size": ["común", "frecuente", "más común", "mas comun", "tamaño más común", "tamaño mas comun"],
    "trend_hour": ["hora", "productividad", "pico", "mayor productividad", "hora con más", "hora con mas"],
    "count_by_quality": ["por calidad", "por calid", "conteo por calidad"] }

#funcion para dectetar expresiones temporales en los textos que ingresen los operadoes

def periodos_temporales(texto: str) -> Optional[str]:
   
   textos= texto.lower()

   if "hoy" in textos:
      return {"type": "day_named", "value": "hoy"}
   if "ayer" in textos:
      return {"type": "day_named", "value": "ayer"}  
   m = re.search(r"ultim[oa]s?\s+(\d+)\s+horas?", textos)
   if m:
      return {"type":"hours", "value": int(m.group(1))}
   m = re.search (r"ultim[oa]s?\s+(\d+)\s+d[ií]as?", textos)
   if m:
        return {"type":"days", "value": int(m.group(1))}
   
   if "última hora" in textos or "ultima hora" in textos:
        return {"type":"hours", "value": 1}
   if "ultimo dia" in textos or "último día" in textos:
        return {"type":"days", "value": 1}
   
  #para las fechas
   m = re.search (r"desde\s+(\d{4}-\d{2}-\d{2})\s+hasta\s+(\d{4}-\d{2}-\d{2})", texto)
   if m: 
       return {"type": "range", "value": (m.group(1), m.group(2))}   
   
   #en caso quee no pase una palabra devuelve NONE
   return None

#para buscar el tama;o y la calidad y normalizarlo

def detectar_tamaño_calidad (doc): 
    tamaño = None
    calidad = None
    for token in doc:
        t =token.text.lower()
        if t in MAP:
            tamaño = MAP[t]
        elif t in CALIDAD_MAP:
            calidad = CALIDAD_MAP[t]
    m= re.search(r"calidad\s*[:]?\s*([abcABC])", doc.text)
    if m:
        calidad = m.group(1).upper()

    m = re.search(r"tamañ?o\s*[:]?\s*(pequeñ[oa]|pequeno|pequena|small|mediano|mediana|medium|grande|large)", 
                  doc.text.lower())
    if m:
        s = m.group(1)
        if s in MAP:
            tamaño = MAP[s]

    return tamaño, calidad

def detectar_intencion (texto: str, doc) -> Optional[str]:
    textos = texto.lower()
    combinaciones ={}
    for intento, llaves in PALABRAS_CLAVES.items():
        for k in llaves:
            if k in textos:
                combinaciones[intento] = combinaciones.get(intento, 0) + 1
    prioridades = ["avg_weight", "most_common_size", "trend_hour", "count_by_quality", "count"]
    for p in prioridades:
        if p in combinaciones:
            return p
    if "promedio" in textos or "promedia" in textos:
        return "avg_weight"
    
    if "hora" in textos or "productividad" in textos or "pico" in textos:
        return "trend_hour"
    return "count"

def preguntas (texto:str)-> Dict [str, Any]:
    doc = nlp_sp(texto)
    intencion = detectar_intencion (texto, doc)
    tamaño , calidad = detectar_tamaño_calidad (doc)
    periodo= periodos_temporales (texto)

    analizado = {   
        "final" : texto,
        "intencion": intencion,
        "tamaño" : tamaño,
        "calidad": calidad,
        "tiempo_promedio": periodo, 
        }
    
    return analizado

def generar_respuesta(intencion: str, datos: dict) -> str:
    if datos is None:
        return "No existe información para tu solicitud"
    if intencion == "estadistica_diaria":
        fila = datos[0] if isinstance(datos, list) else datos

        total = fila.get("total")
        categoria =fila.get("categoria")
        tamaño = fila.get("tamaño")

        respuesta = f"Hoy se procesaron {total} aguacates" 
        
        if categoria:
            respuesta += f"La categoria mas comun fue {categoria}"
        
        if tamaño:
            respuesta += f"El tamaño mas frecuente es {tamaño}"
        
        return respuesta
    
    if intencion == "tamaño frecuente":

        if isinstance (datos, list):
            fila =datos[0]
        else: 
            fila = datos


        tam = fila.get("tamaño")
        frecuencia = datos.get("frecuencia", "N/A")

        if tam:
            return f"El tamaño mas frecuente es {tam}, con unafrecuendia de {frecuencia}"
        
    
        return f"No encontre esta informacon"
    
    return "La solicitud no fue lo suficiente clara. ¿podrias reformularla?"



    