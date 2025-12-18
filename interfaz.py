import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from detector.avocado_detector import run_detector

# -----------------------------
# Configuración general
# -----------------------------
DB_NAME = "avocado_detections.db"

st.set_page_config(
    page_title="Sistema de Monitoreo - Clasificación de Aguacates 🥑",
    layout="wide",
    page_icon="🥑"
)

st.title("Sistema de Monitoreo de Clasificación de Aguacates")
st.markdown("Análisis, métricas y visualización de detecciones")

# -----------------------------
# Funciones auxiliares
# -----------------------------
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

    categoria = max(
        [("Pequeño", small), ("Mediano", medium), ("Grande", large)],
        key=lambda x: x[1]
    )[0]

    return {
        "total": total,
        "categoria": categoria
    }

def grafico_barras(df):
    data = {
        "Pequeño": df["small_count"].sum(),
        "Mediano": df["medium_count"].sum(),
        "Grande": df["large_count"].sum()
    }

    fig, ax = plt.subplots()
    ax.bar(data.keys(), data.values())
    ax.set_title("Distribución por tamaño")
    ax.set_ylabel("Cantidad")
    return fig

def grafico_tendencia(df):
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df_grouped = df.groupby(df["timestamp"].dt.date)["total_count"].sum().reset_index()

    fig, ax = plt.subplots()
    ax.plot(df_grouped["timestamp"], df_grouped["total_count"], marker="o")
    ax.set_title("Tendencia diaria de detecciones")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Total de aguacates")
    return fig

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Navegación")

opcion = st.sidebar.radio(
    "Elige una opción:",
    ["Dashboard", "Datos", "Gráficas", "Detector"]
)

# -----------------------------
# Dashboard
# -----------------------------
if opcion == "Dashboard":
    st.header("Dashboard Informativo")

    df = obtener_datos()
    stats = estadisticas_generales(df)

    if stats is None:
        st.warning("No hay datos registrados todavía.")
    else:
        col1, col2 = st.columns(2)
        col1.metric("Total de Aguacates Detectados", int(stats["total"]))
        col2.metric("Tamaño más frecuente", stats["categoria"])

# -----------------------------
# Datos
# -----------------------------
elif opcion == "Datos":
    st.header("Datos Registrados")

    df = obtener_datos()

    if df.empty:
        st.info("No hay registros almacenados.")
    else:
        st.dataframe(df, use_container_width=True)

# -----------------------------
# Gráficas
# -----------------------------
elif opcion == "Gráficas":
    st.header("Visualizaciones")

    df = obtener_datos()

    if df.empty:
        st.warning("No hay datos para graficar.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Distribución por tamaño")
            fig1 = grafico_barras(df)
            st.pyplot(fig1)

        with col2:
            st.subheader("Tendencia temporal")
            fig2 = grafico_tendencia(df)
            st.pyplot(fig2)

# -----------------------------
# Detector
# -----------------------------
elif opcion == "Detector":
    st.header("Ejecución del Detector")

    st.markdown(
        """
        Esta acción ejecuta el modelo YOLO y registra los resultados
        en la base de datos.  
        **La interfaz no se congela, pero el proceso puede tardar.**
        """
    )

    model_path = st.text_input("Ruta del modelo YOLO (.pt)", value="modelos/avocado.pt")
    source = st.text_input("Fuente de video (0 = cámara)", value="0")

    if st.button("Iniciar detección"):
        with st.spinner("Ejecutando detección..."):
            src = int(source) if source.isdigit() else source
            run_detector(model_path, source=src)
        st.success("Detección finalizada y datos guardados.")

