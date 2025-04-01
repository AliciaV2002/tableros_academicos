import streamlit as st
import pandas as pd 
import numpy as np 
from janitor import clean_names
from dplython import *
import plotly.express as px
import utils

utils.local_css('estilos.css')
utils.remote_css("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css")
utils.remote_css("https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap")




# Cargar datos>
df = pd.read_csv("data/datos_colegio.csv")

# Limpiar nombres de columnas
df = df.clean_names()

# Convertir fecha de ingreso a datetime
df['fecha_de_ingreso'] = pd.to_datetime(df['fecha_de_ingreso'], errors='coerce')

# ---------------------- SELECCIÓN DE GRADO ----------------------
st.sidebar.header("Filtros")
grados_disponibles = sorted(df['grado'].dropna().unique())
grados_selec = st.sidebar.multiselect("Seleccione grado(s)", grados_disponibles, default=grados_disponibles)

# Filtrar datos
df_filtrado = df[df['grado'].isin(grados_selec)]

df_filtrado = DplyFrame(df_filtrado)

# ---------------------- AGRUPACIÓN POR GRADO Y SEGUNDA LENGUA ----------------------
df_grado_lengua = (
    df_filtrado >>
    group_by(X.grado, X.segunda_lengua) >>
    summarize(Conteo=X.id.count())
)


coldf_grado_lengua, grafico_grado_lengua = st.columns(2)
with coldf_grado_lengua:
    # Mostrar tabla
    st.caption("**Nivel de Segunda Lengua por Grado**")
    st.dataframe(df_grado_lengua, hide_index=True)

# ---------------------- GRÁFICO DE BARRAS ----------------------
with grafico_grado_lengua:
    st.caption("**Gráfico de Barras - Nivel de Segunda Lengua por Grado**")
    fig_barras = px.bar(df_grado_lengua, x='grado', y='Conteo', color='segunda_lengua', 
                        title="Distribución de Segunda Lengua por Grado",
                        labels={'grado': 'Grado', 'Conteo': 'Cantidad'})
    fig_barras.update_layout(
        height=385,  # Ancho en píxeles
        title_font=dict(size=14),  # Tamaño del título
        margin=dict(l=20, r=20, t=80, b=10),  # Márgenes ajustados
        xaxis=dict(title_font=dict(size=12)),  # Tamaño del título del eje X
        yaxis=dict(title_font=dict(size=12)),  # Tamaño del título del eje Y
        legend=dict(orientation="h", yanchor="bottom", y=-0.7, xanchor="center", x=0.5)  # Etiquetas en la parte inferior
    )
    st.plotly_chart(fig_barras, use_container_width=True)

# ---------------------- AGRUPACIÓN POR GÉNERO ----------------------
df_genero_lengua = (
    df_filtrado >>
    group_by(X.genero, X.segunda_lengua) >>
    summarize(Conteo=X.id.count())
)

col_genero = st.columns([1])
# Mostrar tabla
col_genero[0].header("Nivel de Segunda Lengua por Género")
col_genero[0].dataframe(df_genero_lengua, hide_index=True)


# ---------------------- GRÁFICO DE BARRAS POR GÉNERO ----------------------
col_graph_genero = st.columns([1])
col_graph_genero[0].subheader("Gráfico de Barras - Nivel de Segunda Lengua por Género")
fig_barras_genero = px.bar(df_genero_lengua, x='genero', y='Conteo', color='segunda_lengua', 
                           title="Distribución de Segunda Lengua por Género",
                           labels={'genero': 'Genero', 'Conteo': 'Cantidad'})
col_graph_genero[0].plotly_chart(fig_barras_genero, use_container_width=True)

# ---------------------- GRÁFICO DE LÍNEAS - SEGUNDA LENGUA POR AÑO ----------------------
df_fecha_lengua = (
    df_filtrado >>
    mutate(año_ingreso=X.fecha_de_ingreso.dt.year) >>
    sift(X.año_ingreso.notna()) >>
    group_by(X.año_ingreso, X.segunda_lengua) >>
    summarize(Conteo=X.id.count())
)

col_fecha = st.columns([1])

col_fecha[0].subheader("Gráfico de Líneas - Nivel de Segunda Lengua por Año de Ingreso")
fig_lineas = px.line(df_fecha_lengua, x='año_ingreso', y='Conteo', color='segunda_lengua', 
                     title="Evolución del Nivel de Segunda Lengua por Año de Ingreso",
                     labels={'año_ingreso': 'Año de Ingreso', 'Conteo': 'Cantidad'})
col_fecha[0].plotly_chart(fig_lineas, use_container_width=True)
