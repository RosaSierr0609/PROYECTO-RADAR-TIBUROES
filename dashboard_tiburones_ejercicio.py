import streamlit as st
import pandas as pd
from pathlib import Path
import pydeck as pdk

# =============================================================================
# CONFIGURACIÓN BÁSICA DE LA PÁGINA
# =============================================================================
st.set_page_config(page_title="Radar de Tiburones", page_icon="🦈", layout="wide")

st.title("🦈 Base de Datos Global: Ataques de Tiburón")
st.markdown("Sistema Táctico Oceanográfico | Demostrador de Clasificación Cartográfica de Incidentes Históricos.")

# =============================================================================
# CARGA Y LIMPIEZA DE DATOS
# =============================================================================
# TODO 1: Crea una función que cargue el archivo usando @st.cache_data
# Archivo a cargar: "geocoded-global-shark-attacks.csv"

@st.cache_data(show_spinner=False)
def cargar_datos_tiburones():
    df = pd.read_csv('geocoded-global-shark-attacks.csv', keep_default_na=False)

# TODO 2: Una vez cargado el CSV, debes transformar el DataFrame.
# Transforma la serie de origen. Para el mapeo las librerías necesitan un namespace estandarizado.
# "NEW_Latitude_Location_Area_Country" a -> "lat"
# "NEW_Longitude_Location_Area_Country" a -> "lon"
    df = df.rename(columns={"NEW_Latitude_Location_Area_Country":"lat", "NEW_Longitude_Location_Area_Country": "lon"})

# TODO 3: Usa pd.to_numeric con errors="coerce" para limpiarlas y dropna() para borrar filas corruptas. 
    for columna in ['lat','lon','age']:
        df[columna] = pd.to_numeric(df[columna], errors='coerce')
    df = df.dropna(subset=['lat','lon','type'])
    
# TODO 4: Aplica un filtro .between() estricto de Latitud (-90 a 90) y Longitud (-180 a 180).
    df = df[df["lat"].between(-90, 90) & df["lon"].between(-180, 180)]
  
    return df

# Descomenta esta línea cuando hagas las funciones:
df = cargar_datos_tiburones()

# =============================================================================
# PANEL DE CONTROL LATERAL (FILTROS)
# =============================================================================
# TODO 5: Abre una barra lateral (with st.sidebar:)
with st.sidebar:
    st.header('Panel de Control')

# TODO 6: Añade un st.selectbox para filtrar por Pais ("Todos" + los únicos que haya en df["country"])
    paises_disponibles = ["Todas"] + sorted(df["country"].unique().tolist())
    paises = st.selectbox(
        'Paises',
        options=paises_disponibles
    )
# TODO 7: Añade un st.multiselect para que el usuario elija y filtre la columna Tipo de Ataque (columna "type")
    tipo_de_ataque = ["Todas"] + sorted(df["type"].unique().tolist())
    ataque = st.multiselect(
        'Tipo de ataque',
        options=tipo_de_ataque,
        default=tipo_de_ataque,
        help='Seleccione una o varias opciones'
    )
# TODO 8: Recuerda hacer una copia del dataset (df_filtrado) y aplicarle estos filtros matemáticos con Pandas.

df_filtrado = df.copy()
if paises != 'Todas':
    df_filtrado = df_filtrado[df_filtrado["country"] == paises]

if ataque != 'Todas':
    df_filtrado = df_filtrado[df_filtrado["type"].isin(ataque)]

# =============================================================================
# MÉTRICAS ESTÁTICAS SUPERIORES (KPIs)
# =============================================================================
# TODO 9: Crea 3 columnas de Streamlit.
# Muestra un st.metric con: 
#   - El número total de casos.
#   - La cantidad de países afectados.
#   - El tipo de actividad más pelígroso (el más repetido estadísticamente usando df["activity"].mode().iloc[0]).

col1,col2,col3 = st.columns(3)

col1.metric('Total de casos',len(df_filtrado))
col2.metric('Paises afectados',df_filtrado['country'].nunique())
col3.metric('Tipo de actividad más peligrosa', df_filtrado["type"].mode().iloc[0])

st.markdown("---")

# =============================================================================
# PINTANDO EL MAPA CARTOGRÁFICO
# =============================================================================
st.header("🗺️ Sonar Submarino")

# TODO 10: Inicializa una proyección de mapbox mediante st.map() referenciando explícitamente a las columnas vectoriales espaciales.
# Opcional: Define un renderizado cromático unificado usando el parámetro `color`.
# st.map( ... )
st.map(
    df_filtrado,
    latitude="lat",
    longitude="lon",
    color="#F91F1F"
)

# Extra: Intenta recrear un Radar 3D como en el laboratorio Pokémon usando pydeck (pdk.Layer)
st.header("🗺️ Sonar Submarino 3D")

def obtener_datos(df_filtrado, max_puntos):
    if len(df_filtrado) <= max_puntos:return df_filtrado
    return df_filtrado.sample(max_puntos, random_state= 42)

df_mapa = obtener_datos(df_filtrado, 3000)

layer = pdk.Layer(
    'ScatterplotLayer',
    data = df_mapa,
    get_position = ['lon','lat'],
    get_fill_color = [255,75,75],
    get_radius = [50000],
    pickable = True,
)

view_state = pdk.ViewState(
    latitude = df_mapa['lat'].mean(),
    longitude = df_mapa['lon'].mean(),
    zoom = 2,
    pitch = 50,
)

st.pydeck_chart(pdk.Deck(
    initial_view_state = view_state,
    layers = [layer],
    tooltip={"text": "País: {country}\nFatal: {type}"}
))

# =============================================================================
# TABLA DE CONSULTA FINAL
# =============================================================================
st.subheader("Expedientes de los Incidentes")
# TODO 11: Usa st.dataframe para mostrar columnas de interés de los ataques ("date", "year", "country", "location", "activity", "sharkspecies", "fatal_y_n")
st.dataframe(
    df_filtrado[["date", "year", "country", "location", "activity", "species", "fatal_y_n"]]
)