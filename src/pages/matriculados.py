# Lectura de librerias
import streamlit as st
import pandas as pd
import numpy as np
from dplython import *
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from janitor import clean_names
import utils 

utils.local_css('estilos.css')
utils.remote_css("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css")
utils.remote_css("https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap")



# from src.pages import utils


# Lectura de datos desde el archivo excel localizado en la carpeta..\src\data
df = pd.read_excel("data/matricula_colegio.xlsx")

# Limpieza y transformacion de datos
df = DplyFrame(df.clean_names())
df['fecha_matricula'] = pd.to_datetime(df['fecha_matricula'], errors='coerce')
# ---------------------- SELECCIÓN DE FECHA ----------------------
with st.sidebar:
    st.header("Filtros")
    años_disponibles = sorted(df['fecha_matricula'].dt.year.dropna().astype(int).unique(), reverse=True)
    año_selec = st.selectbox("Seleccione el año:", años_disponibles)

#---------------------------------------------------------------------
st.markdown("""
    <style>
    .custom-title {
        display: flex;
        align-items: left;
        justify-content: left; /* Centra el contenido */
        margin-bottom: 40px; /* Espacio debajo del título */
        margin-top: -30px;
        font-family: 'Poppins', sans-serif; /* Fuente del título */
        font-weight: bold; /* Grosor del título */
        font-size: 1.5em; /* Tamaño del título */
    }
    </style>
    <div class="custom-title">
        <div>TABLERO DE MATRICULADOS COLEGIO 1</div>
    </div>
""", unsafe_allow_html=True)

cols = st.columns([1,1,1])


df['fecha_matricula'] = pd.to_datetime(df['fecha_matricula'], errors='coerce')

temp = df >> sift(X.fecha_matricula.dt.year == año_selec)
df = df >> sift(X.fecha_matricula.dt.year <= año_selec)

# ---------------------- MÉTRICAS ----------------------

# temp = df >> group_by(X.fecha_matricula.dt.year == 2022) >> summarize(tot = X.id_estudiante.count())


with st.container():
    with cols[0]:
        st.write("""
        <div style="
            display: flex; 
            align-items: center; 
            justify-content: center; 
            height: 74px; 
            text-align: center; 
            color: #7b7b7b; 
            font-size: 0.8em">
            Este tablero muestra el número de matriculados en el colegio 1
        </div>
    """, unsafe_allow_html=True)

    with cols[1]:
        # Con delta se puede poner que tanto ha aumentado o disminuido
        st.metric('Número de matriculados',temp['id_estudiante'].nunique())

    with cols[2]:
        # Matricula por genero
        genero_counts = temp >> group_by(X.sexo) >> summarize(tot=X.id_estudiante.count())
        hombres = temp['sexo'].value_counts().get('M', 0)
        mujeres = temp['sexo'].value_counts().get('F', 0)
        
        # Mostrar en st.metric con formato de texto
        st.metric("Matrícula por Género", f"👦🏻 {hombres} | 🧒🏻 {mujeres}")

        


# ---------------------- GRÁFICA DE BARRAS - MATRICULADOS POR GRADO ----------------------
col1, col2 = st.columns(2)

with col1:
    # Matricula por grado
    grado_counts = temp >> group_by(X.grado) >> summarize(tot=X.id_estudiante.count())
    grado_counts = grado_counts.rename(columns={'grado': 'Grado', 'tot': 'Número de Matriculados'})
    grado_counts = grado_counts.sort_values(by='Grado', key=lambda x: x.str.replace('°', '', regex=False).astype(int), ascending=True)
    
    fig_grado = px.bar(grado_counts, x='Grado', y='Número de Matriculados', title='Matriculados por Grado')
    fig_grado.update_layout(
        width=500,  # Ancho en píxeles
        title_font=dict(size=14),  # Tamaño del título
        margin=dict(l=20, r=20, t=80, b=20),  # Márgenes ajustados
        xaxis=dict(title_font=dict(size=12)),  # Tamaño del título del eje X
        yaxis=dict(title_font=dict(size=12))   # Tamaño del título del eje Y
    )
    fig_grado.update_traces(
        text=grado_counts['Número de Matriculados'], 
        textposition='outside'  # Posición del texto fuera de las barras
    )
    st.plotly_chart(fig_grado)

with col2: 
    # promedio de calificaciones por grado
    promedio_calificaciones = temp >> group_by(X.grado) >> summarize(promedio=X.promedio_anual.mean())
    promedio_calificaciones = promedio_calificaciones.rename(columns={'grado': 'Grado', 'promedio': 'Promedio de Calificaciones'})
    promedio_calificaciones = promedio_calificaciones.sort_values(by='Grado', key=lambda x: x.str.replace('°', '', regex=False).astype(int), ascending=True)
    promedio_calificaciones['Promedio de Calificaciones'] = promedio_calificaciones['Promedio de Calificaciones'].round(2)
    
    fig_calificaciones = px.bar(promedio_calificaciones, x='Grado', y='Promedio de Calificaciones', title='Distribución de Calificaciones por Grado')
    fig_calificaciones.update_layout(
        width=500,  # Ancho en píxeles
        title_font=dict(size=14),  # Tamaño del título
        margin=dict(l=20, r=20, t=80, b=20),  # Márgenes ajustados
        xaxis=dict(title_font=dict(size=12)),  # Tamaño del título del eje X
        yaxis=dict(title_font=dict(size=12))   # Tamaño del título del eje Y
    )
    fig_calificaciones.update_traces(
        text=promedio_calificaciones['Promedio de Calificaciones'], 
        textposition='outside'  # Posición del texto fuera de las barras
    )
    st.plotly_chart(fig_calificaciones)

estrato, estado = st.columns(2)

with estrato:	
    # Matricula por estrato socioeconómico
    estrato_counts = temp >> group_by(X.estrato) >> summarize(tot=X.id_estudiante.count())
    estrato_counts = estrato_counts.rename(columns={'estrato': 'Estrato', 'tot': 'Número de Matriculados'})
    estrato_counts = estrato_counts.sort_values(by='Estrato', ascending=True)
    fig_estrato = px.bar(estrato_counts, x='Estrato', y='Número de Matriculados', title='Matriculados por Estrato Socioeconómico')
    fig_estrato.update_layout(
        xaxis=dict(
            tickmode='linear',  # Asegura que todos los valores del eje X se muestren
            tick0=1,  # Valor inicial del eje X
            dtick=1   # Incremento entre ticks
        )
    )
    fig_estrato.update_layout(
        width=500,  # Ancho en píxeles
        height=537, # Alto en píxeles
        title_font=dict(size=14),  # Tamaño del título
        margin=dict(l=20, r=20, t=80, b=20),  # Márgenes ajustados
        xaxis=dict(title_font=dict(size=12)),  # Tamaño del título del eje X
        yaxis=dict(title_font=dict(size=12))   # Tamaño del título del eje Y
    )
    fig_estrato.update_traces(
        text=grado_counts['Número de Matriculados'], 
        textposition='outside'  # Posición del texto fuera de las barras
    )
    st.plotly_chart(fig_estrato)
    
with estado:	
    # Matricula por estado
    estado_counts = temp >> group_by(X.estado_matricula) >> summarize(tot=X.id_estudiante.count())
    estado_counts = estado_counts.rename(columns={'estado_matricula': 'Estado', 'tot': 'Número de Matriculados'})
    fig_estado = px.pie(estado_counts, names='Estado', values='Número de Matriculados', title='Distribución de Matriculados por Estado')
    fig_estado.update_layout(
        width=500,  # Ancho en píxeles
        height=260, # Alto en píxeles
        title_font=dict(size=14),  # Tamaño del título
        margin=dict(l=20, r=20, t=80, b=20),  # Márgenes ajustados
        xaxis=dict(title_font=dict(size=12)),  # Tamaño del título del eje X
        yaxis=dict(title_font=dict(size=12))   # Tamaño del título del eje Y
    )
    fig_estado.update_layout(
        legend=dict(
            orientation="h",  # Orientación horizontal
            yanchor="bottom",  # Alineación vertical
            y=-0.3,  # Posición vertical (debajo de la gráfica)
            xanchor="center",  # Alineación horizontal
            x=0.5  # Posición horizontal (centrado)
        )
    )
    st.plotly_chart(fig_estado)

    # Matricula por beca
    beca_counts = temp >> group_by(X.beca) >> summarize(tot=X.id_estudiante.count())
    beca_counts = beca_counts.rename(columns={'beca': 'Beca', 'tot': 'Número de Matriculados'})
    beca_counts = beca_counts.sort_values(by='Beca', ascending=True)
    fig_beca = px.pie(beca_counts, names='Beca', values='Número de Matriculados', title='Matriculados Beca')
    fig_beca.update_layout(
        width=500,  # Ancho en píxeles
        height=260, # Alto en píxeles
        title_font=dict(size=14),  # Tamaño del título
        margin=dict(l=20, r=20, t=80, b=20),  # Márgenes ajustados
        xaxis=dict(title_font=dict(size=12)),  # Tamaño del título del eje X
        yaxis=dict(title_font=dict(size=12))   # Tamaño del título del eje Y
    )
    fig_beca.update_layout(
        legend=dict(
            orientation="h",  # Orientación horizontal
            yanchor="bottom",  # Alineación vertical
            y=-0.3,  # Posición vertical (debajo de la gráfica)
            xanchor="center",  # Alineación horizontal
            x=0.5  # Posición horizontal (centrado)
        )
    )
    st.plotly_chart(fig_beca, key = "beca")


edad, tabla= st.columns(2)

with edad:
    # Matricula por edad
    edad_counts = temp >> group_by(X.edad) >> summarize(tot=X.id_estudiante.count())
    edad_counts = edad_counts.rename(columns={'edad': 'Edad', 'tot': 'Número de Matriculados'})
    edad_counts = edad_counts.sort_values(by='Edad', ascending=True)
    fig_edad = px.bar(edad_counts, x='Número de Matriculados', y='Edad', title='Matriculados por Edad', orientation='h')
    fig_edad.update_layout(
        width=500,  # Ancho en píxeles
        height=450, # Alto en píxeles
        title_font=dict(size=14),  # Tamaño del título
        margin=dict(l=20, r=20, t=80, b=20),  # Márgenes ajustados
        xaxis=dict(title_font=dict(size=12)),  # Tamaño del título del eje X
        yaxis=dict(title_font=dict(size=12))   # Tamaño del título del eje Y
    )
    fig_edad.update_traces(
        text=edad_counts['Número de Matriculados'], 
        textposition='outside'  # Posición del texto fuera de las barras
    )
    st.plotly_chart(fig_edad, key = "edad")

with tabla:
    edad_counts2 = temp >> group_by(X.grado, X.edad) >> summarize(tot = X.id_estudiante.count())
    edad_counts2 = edad_counts2.rename(columns={'edad': 'Edad', 'grado': 'Grado', 'tot': 'Número de Matriculados'})
    edad_counts2 = edad_counts2.sort_values(by='Grado', key=lambda x: x.str.replace('°', '', regex=False).astype(int), ascending=True)
    # utils.generateTable(edad_counts2)
    def hide_repeated_values(df, col_name):
        """Reemplaza valores repetidos con cadenas vacías en una columna específica."""
        mask = df[col_name].duplicated()
        df.loc[mask, col_name] = ""  # Reemplaza valores duplicados con vacío
        return df

    edad_counts2 = hide_repeated_values(edad_counts2, "Grado")
    st.caption('<span style="color:black;"><b>Matriculados por Grado y Edad</b></span>', unsafe_allow_html=True)
    st.dataframe(edad_counts2, hide_index=True, height=404)


col3 = st.columns([1])

with col3[0]:
    matriculados_por_año = df.groupby(df['fecha_matricula'].dt.year)['id_estudiante'].nunique().reset_index()
    matriculados_por_año.columns = ['Año', 'Número de Matriculados']
    fig = px.line(matriculados_por_año, x='Año', y='Número de Matriculados', title='Historico de Matriculados', markers=True )
    fig.update_layout(
        width=500,  # Ancho en píxeles
        height=350, # Alto en píxeles
        title_font=dict(size=14),  # Tamaño del título
        margin=dict(l=20, r=20, t=80, b=20),  # Márgenes ajustados
        xaxis=dict(title_font=dict(size=12)),  # Tamaño del título del eje X
        yaxis=dict(title_font=dict(size=12))   # Tamaño del título del eje Y
    )
    st.plotly_chart(fig)

col_graph_grados = st.columns([1])

with col_graph_grados[0]:
    # grafico de lineas que muesta anualmente la evolucion de la matricula de los grados
    # Filtrar grados de 1° a 5°
    grados_1_5 = df[df['grado'].str.replace('°', '', regex=False).astype(int).between(1, 5)]
    matriculados_por_grado_año_1_5 = grados_1_5.groupby([grados_1_5['fecha_matricula'].dt.year, 'grado'])['id_estudiante'].nunique().reset_index()
    matriculados_por_grado_año_1_5.columns = ['Año', 'Grado', 'Número de Matriculados']
    matriculados_por_grado_año_1_5 = matriculados_por_grado_año_1_5.sort_values(by=['Año', 'Grado'], key=lambda x: x if x.name != 'Grado' else x.str.replace('°', '', regex=False).astype(int))
    
    fig_grados_1_5 = px.line(
        matriculados_por_grado_año_1_5, 
        x='Año', 
        y='Número de Matriculados', 
        color='Grado', 
        title='Evolución Anual de la Matrícula por Grado (1° a 5°)', 
        markers=True
    )
    fig_grados_1_5.update_layout(
        width=800,  # Ancho en píxeles
        height=450, # Alto en píxeles
        title_font=dict(size=14),  # Tamaño del título
        margin=dict(l=20, r=20, t=80, b=20),  # Márgenes ajustados
        xaxis=dict(title_font=dict(size=12)),  # Tamaño del título del eje X
        yaxis=dict(title_font=dict(size=12))   # Tamaño del título del eje Y
    )
    st.plotly_chart(fig_grados_1_5)

    # Filtrar grados de 6° a 11°
    grados_6_11 = df[df['grado'].str.replace('°', '', regex=False).astype(int).between(6, 11)]
    matriculados_por_grado_año_6_11 = grados_6_11.groupby([grados_6_11['fecha_matricula'].dt.year, 'grado'])['id_estudiante'].nunique().reset_index()
    matriculados_por_grado_año_6_11.columns = ['Año', 'Grado', 'Número de Matriculados']
    matriculados_por_grado_año_6_11 = matriculados_por_grado_año_6_11.sort_values(by=['Año', 'Grado'], key=lambda x: x if x.name != 'Grado' else x.str.replace('°', '', regex=False).astype(int))
    
    fig_grados_6_11 = px.line(
        matriculados_por_grado_año_6_11, 
        x='Año', 
        y='Número de Matriculados', 
        color='Grado', 
        title='Evolución Anual de la Matrícula por Grado (6° a 11°)', 
        markers=True
    )
    fig_grados_6_11.update_layout(
        width=800,  # Ancho en píxeles
        height=450, # Alto en píxeles
        title_font=dict(size=14),  # Tamaño del título
        margin=dict(l=20, r=20, t=80, b=20),  # Márgenes ajustados
        xaxis=dict(title_font=dict(size=12)),  # Tamaño del título del eje X
        yaxis=dict(title_font=dict(size=12))   # Tamaño del título del eje Y
    )
    st.plotly_chart(fig_grados_6_11)
