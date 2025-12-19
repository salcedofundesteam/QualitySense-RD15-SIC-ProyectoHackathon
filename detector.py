import cv2
import argparse
from ultralytics import YOLO
import numpy as np
import sqlite3
from datetime import datetime


DB_NAME = 'avocado_detections.db'


# Aqui importamos lo que son las utilidades de la base de datos
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

    # Insertaael registro de conteo por frame
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

# Importante recuerda llamar a create_table() al inicio del script principal.

# Estos son los umbrales basados en el área "ancho * alto" del Bounding Box en píxeles.
AREA_SMALL_MAX = 5000     # Bounding Box Area < 5000 -> Small
AREA_MEDIUM_MAX = 15000   # 5000 <= Area < 15000 -> Medium
# Large > 15000

# Colores BGR para poder dibujar las detecciones en la pantalla, me base en la que tenia el video.
COLORS = {
    'Small': (0, 0, 255),    # Rojo para Pequeño
    'Medium': (0, 255, 255), # Amarillo para Mediano
    'Large': (255, 0, 0),    # Azul para Grande
}

def classify_by_area(box_area):
    """Clasifica el aguacate basándose en el área del Bounding Box."""
    if box_area < AREA_SMALL_MAX:
        return 'Small'
    elif box_area < AREA_MEDIUM_MAX:
        return 'Medium'
    else:
        return 'Large'

def main(model_path, source, resolution='1280x720'):
    # Prepara la Base de Datos
    create_table()

    # Carga el Modelo YOLO
    print(f"Cargando modelo YOLO desde: {model_path}")
    try:
        model = YOLO(model_path)
    except Exception as e:
        print(f"Error al cargar el modelo. Asegúrate de que '{model_path}' es un archivo .pt válido. Error: {e}")
        return

    # Configura de la Captura de Video tanto en Vivo o en Video
    if source.isdigit():
        cap = cv2.VideoCapture(int(source)) # Esta es la cámara en vivo (ej: '0')
    else:
        print(f"Usando archivo de video: {source}")
        cap = cv2.VideoCapture(source)

    if not cap.isOpened():
        print(f"Error: No se pudo abrir la fuente de video/cámara: {source}")
        return

    # Configurar resolución si es cámara en vivo
    if source.isdigit():
        w, h = map(int, resolution.split('x'))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

    print("Iniciando detección. Presiona 'q' para salir del feed.")
    frame_counter = 0

    # Bucle principal de detección
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Fin del video o error al leer el frame.")
            break

        frame_counter += 1

        # Realiza Inferencia y Conteo
        results = model(frame, verbose=False)
        counts = {'Total': 0, 'Small': 0, 'Medium': 0, 'Large': 0}

        for r in results:
            # Itera sobre las detecciones del modelo
            boxes = r.boxes.xyxy.cpu().numpy()

            for box in boxes:
                x1, y1, x2, y2 = map(int, box)

                # Aqui calculamos el área y clasificar por tamaño
                width = x2 - x1
                height = y2 - y1
                area = width * height

                size_category = classify_by_area(area)

                # Actualiza el contador
                counts[size_category] += 1
                counts['Total'] += 1

                # Dibuja resultados en el frame
                color = COLORS.get(size_category, (255, 255, 255))
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                label = f"{size_category}: {area} px"
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Esto es para poder mostrar el Resumen de Conteo para el Front-End
        display_y_start = 50
        cv2.putText(frame, f"Total Aguacates: {counts['Total']}", (10, display_y_start), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"Pequeño: {counts['Small']}", (10, display_y_start + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS['Small'], 2)
        cv2.putText(frame, f"Mediano: {counts['Medium']}", (10, display_y_start + 80), cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS['Medium'], 2)
        cv2.putText(frame, f"Grande: {counts['Large']}", (10, display_y_start + 120), cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS['Large'], 2)

        # Loguea la detección en SQLite (Cada 30 frames para evitar sobresaturación)
        if frame_counter % 30 == 0:
             log_detection(counts)

        # Muestra el frame que proceso
        cv2.imshow('Avocado Classifier & Counter', frame)

        # Para salir presionar 'q'y bye
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Aqui liberamos los recursos
    cap.release()
    cv2.destroyAllWindows()
    print("Detección y logging finalizado.")

# -- Configuración de Argumentos (Para ejecutar desde la consola) --
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Clasificador/Contador de Aguacates (YOLO + OpenCV).")
    parser.add_argument('--model', type=str, required=True, help="Ruta al archivo .pt del modelo YOLO entrenado (ej: my_model.pt).")
    parser.add_argument('--source', type=str, default='0', help="Fuente: '0' para cámara en vivo o ruta del video (ej: video_prueba.mp4).")
    parser.add_argument('--resolution', type=str, default='1280x720', help="Resolución para cámara en vivo (ej: 640x480).")

    args = parser.parse_args()
    main(args.model, args.source, args.resolution)