import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
import seaborn as sns

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

    # Gráfico de barras
    st.subheader("Diagrama de Barras")
    fig_bar, ax_bar = plt.subplots(figsize=(10, 5))
    sns.barplot(data=df_grouped, x="Tipo_Residuo", y=variable_numerica, palette="viridis", ax=ax_bar)
    ax_bar.set_ylabel(f"Suma de {variable_numerica.replace('_', ' ')}")
    ax_bar.set_xlabel("Tipo de residuo")
    ax_bar.set_title(f"Suma de {variable_numerica.replace('_', ' ')} por tipo de residuo")
    plt.xticks(rotation=45)
    st.pyplot(fig_bar)

    # Gráfico de torta
    st.subheader("Distribución proporcional (Gráfico de Torta)")
    fig_pie, ax_pie = plt.subplots(figsize=(6, 6))
    ax_pie.pie(
        df_grouped[variable_numerica],
        labels=df_grouped["Tipo_Residuo"],
        autopct="%1.1f%%",
        startangle=90,
        colors=sns.color_palette("viridis", len(df_grouped))
    )
    ax_pie.axis("equal")  # Mantener el círculo redondo
    ax_pie.set_title(f"Proporción de {variable_numerica.replace('_', ' ')} por tipo de residuo")
    st.pyplot(fig_pie)


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

    # Crear el histograma
    fig, ax = plt.subplots(figsize=(10, 5))

    sns.histplot(
        data=df_filtrado, 
        x=variable_hist, 
        kde=True,  # Puedes quitar esta línea si no quieres curva de densidad
        bins=10,
        color='skyblue',
        edgecolor='black',
        ax=ax
    )

    ax.set_title(f"Distribución de {variable_hist.replace('_', ' ')} para {tipo_residuo}")
    ax.set_xlabel(variable_hist.replace('_', ' '))
    ax.set_ylabel("Frecuencia")

    st.pyplot(fig)


# Página 4: Mapa
elif selected == "Mapa":
    st.title("Mapa Interactivo de Recolección de Residuos")

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

