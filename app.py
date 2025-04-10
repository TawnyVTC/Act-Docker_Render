import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

# Cargar datos
@st.cache_data
def load_data():
    return pd.read_csv("data/residuos.csv", encoding="utf-8")

df = load_data()

# Sidebar con menú
with st.sidebar:
    selected = option_menu(
        "Menú Principal",
        ["Contexto", "Diagrama de Barras y Proporción", "Histograma", "Mapa"],
        icons=["house", "bar-chart", "bar-chart-line", "map"],
        menu_icon="cast",
        default_index=0,
    )

# Página 1: Contexto
if selected == "Contexto":
    st.title("Contexto del Proyecto")
    st.markdown("""
    Este dashboard muestra el análisis de residuos recolectados por departamento en Colombia.
    
    Explora:
    - Visualizaciones por tipo de residuo y métricas.
    - Distribución de variables.
    - Ubicación geográfica con un mapa interactivo filtrable.
    """)

# Página 2: Análisis de variables
elif selected == "Diagrama de Barras y Proporción":
    st.title("Análisis por Tipo de Residuo")

    # Selector de variable numérica
    variable_numerica = st.selectbox(
        "Selecciona una variable numérica a comparar:",
        ["Cantidad_Kg", "Frecuencia_Semanal"]
    )

    # Agrupar datos por tipo de residuo
    df_grouped = df.groupby("Tipo_Residuo")[variable_numerica].sum().reset_index()

    # Gráfico de barras interactivo
    st.subheader("Diagrama de Barras")
    fig_bar = px.bar(
        df_grouped,
        x="Tipo_Residuo",
        y=variable_numerica,
        color="Tipo_Residuo",
        title=f"Suma de {variable_numerica.replace('_', ' ')} por tipo de residuo",
        labels={variable_numerica: f"Suma de {variable_numerica.replace('_', ' ')}"},
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    fig_bar.update_layout(xaxis_title="Tipo de residuo", yaxis_title=variable_numerica.replace('_', ' '))
    st.plotly_chart(fig_bar)

    # Gráfico de torta interactivo
    st.subheader("Distribución Proporcional por Tipo de Residuo")
    fig_pie = px.pie(
        df_grouped,
        names="Tipo_Residuo",
        values=variable_numerica,
        title=f"Proporción de {variable_numerica.replace('_', ' ')} por tipo de residuo",
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    st.plotly_chart(fig_pie)

# Página 3: Histograma
elif selected == "Histograma":
    st.title("Distribución de Residuos")

    # Seleccionar la variable
    variable_hist = st.selectbox(
        "Selecciona la variable para el histograma:", 
        options=["Cantidad_Kg", "Frecuencia_Semanal"]
    )

    # Seleccionar un solo tipo de residuo
    tipo_residuo = st.selectbox(
        "Selecciona el tipo de residuo:", 
        options=df["Tipo_Residuo"].unique()
    )

    # Filtrar el DataFrame
    df_filtrado = df[df["Tipo_Residuo"] == tipo_residuo]

    # Crear el histograma interactivo
    fig_hist = px.histogram(
        df_filtrado,
        x=variable_hist,
        nbins=10,
        title=f"Distribución de {variable_hist.replace('_', ' ')} para {tipo_residuo}",
        color_discrete_sequence=["blue"]
    )
    fig_hist.update_layout(
        xaxis_title=variable_hist.replace('_', ' '),
        yaxis_title="Frecuencia",
        bargap=0.1
    )
    st.plotly_chart(fig_hist)

# Página 4: Mapa
elif selected == "Mapa":
    st.title("Mapa de Recolección de Residuos")

    tipo_residuo = st.selectbox("Selecciona el tipo de residuo a visualizar en el mapa:", 
                                 df["Tipo_Residuo"].unique())

    df_mapa = df[df["Tipo_Residuo"] == tipo_residuo]

    # Crear el mapa centrado en Colombia
    m = folium.Map(location=[4.5709, -74.2973], zoom_start=5, tiles="CartoDB positron")

    for _, row in df_mapa.iterrows():
        folium.Marker(
            location=[row["Latitud"], row["Longitud"]],
            popup=folium.Popup(f"""
                <b>Departamento:</b> {row['Departamento']}<br>
                <b>Tipo de residuo:</b> {row['Tipo_Residuo']}<br>
                <b>Cantidad (Kg):</b> {row['Cantidad_Kg']}<br>
                <b>Frecuencia semanal:</b> {row['Frecuencia_Semanal']}
            """, max_width=300),
            icon=folium.Icon(color="blue", icon="trash", prefix="fa")
        ).add_to(m)

    st_folium(m, width=800, height=500)
