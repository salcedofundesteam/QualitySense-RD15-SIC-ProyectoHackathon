"""Para generar los graficos utilizare las librerias matplotlib y seaborn
estas funciones permitiran que los graficos se puedan mostrar en la interfaz de Stremlit
"""
from typing import List, Tuple, Dict, Any, Optional
import io
import matplotlib.pyplot as plt
import seaborn as sn
import pandas as pd

sn.set_style("whitegrid")
plt.rcParams.update({
    "figure.autolayout": True,
    "figure.dpi" : 100 })

#funcion para convertir el grafico generado por matplotlib a bytes PNG, lo cual Permite que 
#que los graficos se puedan ver en Stermlit.

def ajustar_bytes (fig) -> bytes:

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    data = buf.getvalue()
    buf.close()
    plt.close(fig)
    return data

#funcion para combertir las series ede tuplas a un dataframe

def dataframe_de_las_series (series: List[Tuple[Any]], columnas: Tuple[str, str]) -> pd.DataFrame:
    if not series: 
        return pd.DataFrame({columnas[0]: [], columnas[1]: []})
    df = pd.DataFrame(series, columnas)
    return df

"""Para construir los graficos de barras. mostrara barras simples, 
con informacion relevante como el conteo por las categorias"""
def barras_por_categoria(series: List[Tuple[str, int]],
                         title: str = "Conteo por Categiria", #el grafico mostrara la antidad de aguacates pasados por la cinte
                         xlabel: str = "",
                         ylabel: str = "Cantidad",
                         rotate_xtictks : int = 0, 
                         figsize: Tuple[int,int] = (6,4)) -> plt.Figure:
    df = dataframe_de_las_series (series, ("category", "count"))
    fig, ax=plt.subplots(figsize=figsize)
    sn.barplot(x="category", y="count", data=df,ax=ax) 
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if rotate_xtictks:
        plt.setp(ax.get_xticklabels(), rotation=rotate_xtictks)  
    for p in ax.patches:
        height  = p.get_height()
        ax.annotate(f'{int(height)}', (p.get_x()+ p.get_width()/2.,height),
                    ha='center', va='bottom', fontsize=9)
    return fig 
###############################################################################################
""" HISTOGRAMA PARA EL PESO, PERO EN CASO DE NO TENER COLUMNA DEL PESO SE PUEDE HACER UN HISTOGRAMA CON EL TAMA;O O ELIMINAR ESTE GRAFICO"""
############################################################################################### 
#grafico para linea de tendencia por horas

def linea_de_tendencia_por_hora (series: List[Tuple[str,int]],
                                 title: str = "Producción por hora",
                                 xlabel: str = "Hora",
                                 ylabel: str = "Cantidad",
                                 figsize: Tuple[int,int] = (8,4),
                                 rotate_xticks: int = 45) -> plt.Figure:
    df = dataframe_de_las_series (series, ("hour", "count"))

    try: 
        df["hour_dp"] = pd.to_datetime(df["hour"])
        x = df["hour_dp"]   
    except Exception:
        x = df["hour"]
    y=df["count"]
    fig, ax = plt.subplots(figsize=figsize)
    sn.lineplot(x=x, y=y, marker = "o", ax=ax)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if rotate_xticks:
        plt.setp(ax.get_xticklabels(), rotation=rotate_xticks)
    if len(y) <= 24:
        for xi,yi in zip (ax.get_lines()[0].get_xdata(),ax.get_lines()[0].get_ydata()):
            ax.annotate(f'{int(yi)}', (xi,yi),textcoords="offset points", xytext=(0,5), ha='center', fontsize=8)
    return fig

def cuadro_a_imagen(fig) -> bytes:
    return ajustar_bytes(fig)


def barra_categorica_en_bytes(series:List[Tuple[str,int]], **kwargs) -> bytes:
    fig = barras_por_categoria(series, **kwargs)
    return ajustar_bytes(fig)

def tendencia_por_hora_en_bytes (series: List[Tuple[str, int]], **kwargs) ->bytes:
    fig = linea_de_tendencia_por_hora(series, **kwargs)
    return ajustar_bytes(fig)