import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

from detector import main as run_detector

# --------------------------------------------------
# Configuración general
# --------------------------------------------------
DB_NAME = "avocado_detections.db"

if "running" not in st.session_state:
    st.session_state["running"] = False

st.set_page_config(
    page_title="Sistema de Monitoreo - QualitySense 🥑",
    layout="wide",
    page_icon="🥑"
)

st.title("Sistema de Monitoreo QualitySense 🥑")
st.markdown("Análisis y métricas basadas en detección con visión computacional")

# --------------------------------------------------
# Funciones de acceso a datos
# --------------------------------------------------
def obtener_datos():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM detections", conn)
    conn.close()
    return df

def estadisticas_generales(df):
    if df.empty:
        return None

    total = df["total_count"].sum()
    small = df["small_count"].sum()
    medium = df["medium_count"].sum()
    large = df["large_count"].sum()

    tamaño_frecuente = max(
        [("Pequeño", small), ("Mediano", medium), ("Grande", large)],
        key=lambda x: x[1]
    )[0]

    return total, tamaño_frecuente

# --------------------------------------------------
# Gráficos
# --------------------------------------------------
def grafico_barras(df):
    valores = [
        df["small_count"].sum(),
        df["medium_count"].sum(),
        df["large_count"].sum()
    ]

    fig, ax = plt.subplots()
    ax.bar(["Pequeño", "Mediano", "Grande"], valores)
    ax.set_title("Distribución por tamaño de aguacate")
    ax.set_ylabel("Cantidad")
    return fig

def grafico_tendencia(df):
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df_group = df.groupby(df["timestamp"].dt.date)["total_count"].sum()

    fig, ax = plt.subplots()
    ax.plot(df_group.index, df_group.values, marker="o")
    ax.set_title("Tendencia diaria de detecciones")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Total de aguacates")
    return fig

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
st.sidebar.title("Navegación")

opcion = st.sidebar.radio(
    "Seleccione una opción:",
    ["Dashboard", "Datos", "Gráficas", "Detector"]
)

# --------------------------------------------------
# Dashboard
# --------------------------------------------------
if opcion == "Dashboard":
    st.header("Dashboard Informativo")

    df = obtener_datos()
    stats = estadisticas_generales(df)

    if stats is None:
        st.warning("Aún no hay datos registrados.")
    else:
        total, tamaño_frecuente = stats

        col1, col2 = st.columns(2)
        col1.metric("Total de Aguacates Detectados", int(total))
        col2.metric("Tamaño más frecuente", tamaño_frecuente)

# --------------------------------------------------
# Datos
# --------------------------------------------------
elif opcion == "Datos":
    st.header("Registros almacenados")

    df = obtener_datos()

    if df.empty:
        st.info("No hay datos disponibles.")
    else:
        st.dataframe(df, use_container_width=True)

# --------------------------------------------------
# Gráficas
# --------------------------------------------------
elif opcion == "Gráficas":
    st.header("Visualizaciones")

    df = obtener_datos()

    if df.empty:
        st.warning("No hay datos para mostrar.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Distribución por tamaño")
            st.pyplot(grafico_barras(df))

        with col2:
            st.subheader("Tendencia temporal")
            st.pyplot(grafico_tendencia(df))

# --------------------------------------------------
# Detector
# --------------------------------------------------
elif opcion == "Detector":
    st.header("Ejecución del Detector YOLO")

    st.markdown(
        """
        Ejecuta el modelo de detección y guarda los resultados
        directamente en la base de datos.
        """
    )

    model_path = st.text_input(
        "Ruta del modelo YOLO",
        value="my_model_best.pt"
    )

    source = st.text_input(
        "Fuente de video (0 = cámara)",
        value="0"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶ Iniciar detección"):
            st.session_state.running = True

    with col2:
        if st.button("⏹ Parar detección"):
            st.session_state.running = False

    if st.session_state.running:
        with st.spinner("Detectando aguacates..."):
            src = source
            run_detector(model_path=model_path, source=src)

