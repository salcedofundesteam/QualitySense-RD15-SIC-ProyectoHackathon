# QualitySense
_Samsung Innovation Campus - RD16_

## Descripción

QualitySense es un sistema de monitoreo en tiempo real que utiliza visión artificial y procesamiento de lenguaje natural para automatizar la clasificación y análisis de aguacates en entornos industriales.

## Instalación Rápida

```bash
# Clonar repositorio
git clone https://github.com/samsung-innovation-campus/qualitysense-rd16.git
cd qualitysense-rd16

# Instalar dependencias
pip install -r requirements.txt
python -m spacy download es_core_news_md

# Inicializar base de datos
python base_temporal.py
```

## Uso Básico

### Ejecutar interfaz web:
```bash
streamlit run interfaz.py
```

### Ejecutar sistema de detección:
```bash
python insightdom_model.py --model modelos/avocado.pt --source 0
```

## Estructura del Proyecto

```
qualitysense-rd16/
├── interfaz.py              # Dashboard principal
├── insightdom_model.py      # Sistema de detección YOLO
├── nlp.py                   # Procesamiento de lenguaje natural
├── conexion.py              # Gestión de base de datos
├── graficos.py              # Generación de gráficos
├── consultas.py             # Consultas SQL comunes
├── requirements.txt         # Dependencias
└── modelos/ --> optional layer
    └── avocado.pt          # Modelo YOLO entrenado
```

## Documentación Completa

Para información detallada sobre arquitectura, configuración avanzada y solución de problemas, consulte [DOCUMENTATION.md](DOCUMENTATION.md).

---
