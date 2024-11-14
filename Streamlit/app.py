import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import zscore
import numpy as np
from PIL import Image

# Configuración general de Streamlit
st.set_page_config(page_title="Proyecto Inmobiliario", page_icon=":house:", layout="centered")

# CSS 
st.markdown("""
    <style>
    /* Fondo general */
    .stApp {
        background-color: #ffffff; /* Blanco */
    }

    /* Barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #00264d; /* Azul oscuro */
    }

    /* Títulos y etiquetas en la barra lateral */
    section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] div[data-baseweb="slider"] > div:first-child {
        color: #ffffff !important; /* Texto blanco */
        background-color: #B0C4DE !important; /* Fondo azul claro */
        padding: 5px 8px; /* Espacio alrededor del texto */
        border-radius: 5px; /* Bordes redondeados */
        font-family: 'Roboto', sans-serif;
    }

    /* Ajuste del margen superior del slider */
    section[data-testid="stSidebar"] div[data-baseweb="slider"] {
        margin-top: 10px !important; /* Espacio adicional superior */
        text-align: center !important; /* Centrar el slider */
        margin-left: auto !important; /* Centrar el slider automáticamente */
        margin-right: auto !important; 
    }

    /* Slider en la vista principal */
    div[data-baseweb="slider"] {
        margin-left: 40px !important; /* Espacio a la izquierda */
        margin-right: 40px !important; /* Espacio a la derecha */
    }

    /* Títulos principales */
    h1, h2, h3 {
        color: #00264d; /* Azul oscuro */
        font-family: 'Roboto', sans-serif;
    }

    /* Texto del cuerpo */
    p, label {
        color: #00264d; /* Azul oscuro */
        font-family: 'Roboto', sans-serif;
        font-size: 1.1em;
    }

    /* Gráficos de Plotly */
    .plotly-chart .title {
        color: #00264d;
        font-family: 'Roboto', sans-serif;
    }

    /* Transparencia para gráficos */
    .plotly-graph-wrapper .plot-container .svg-container {
        background-color: rgba(255, 255, 255, 0); /* Fondo transparente */
    }

    /* Ajuste del ancho de la tabla */
    .dataframe {
        width: 100% !important;
    }

    /* Quitar espacio en blanco adicional alrededor de los componentes */
    .main .block-container {
        padding: 0 !important;
    }

    /* Mapas y gráficos ocupando el ancho completo */
    .st-folium {
        width: 100% !important;
    }

    /* Slider de rango de precios */
    .css-1n76uvr .stSlider > div {
        color: #ffffff !important; /* Texto blanco */
    }

    /* Color del slider de rango de precios blanco */
    .stSlider > div > div > div:first-child {
        background-color: #ffffff !important;
    }

    /* Color del control deslizante blanco */
    .stSlider > div > div > div:nth-child(2) {
        background-color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# Ruta del archivo CSV
ruta_archivo = '../propiedades_limpio.csv'

# Función para cargar los datos con caché
@st.cache_data
def load_data(nrows=None):
    return pd.read_csv(ruta_archivo, sep=';', nrows=nrows)

# Leer el archivo CSV 
df = load_data()
df.columns = df.columns.str.strip().str.lower()

# Capitalizar nombres de provincias y tipo transacción
df['provincia'] = df['provincia'].str.title()
df['venta/alquiler'] = df['venta/alquiler'].str.capitalize()

# Crear la columna 'precio por m²' si no existe
if 'precio por m²' not in df.columns:
    df['precio por m²'] = df['precio'] / df['superficie útil']
    df['precio por m²'] = df['precio por m²'].fillna(0)

# Diccionario con coordenadas aproximadas (centroides) de cada provincia en España
provincia_centroides = {
    'a coruña': (43.3623, -8.4115),
    'alava araba': (42.8464, -2.6715),
    'albacete': (38.9943, -1.8585),
    'alicante': (38.3452, -0.4810),
    'almeria': (36.8340, -2.4637),
    'asturias': (43.3619, -5.8494),
    'avila': (40.6565, -4.6818),
    'badajoz': (38.8794, -6.9706),
    'barcelona': (41.3851, 2.1734),
    'burgos': (42.3439, -3.6969),
    'caceres': (39.4753, -6.3723),
    'cadiz': (36.5164, -6.2994),
    'cantabria': (43.1828, -3.9878),
    'castellon castello': (39.9864, -0.0513),
    'ceuta': (35.8894, -5.3198),
    'ciudad real': (38.9857, -3.9291),
    'cordoba': (37.8882, -4.7794),
    'cuenca': (40.0704, -2.1374),
    'girona': (41.9794, 2.8214),
    'granada': (37.1773, -3.5986),
    'guadalajara': (40.6332, -3.1669),
    'guipuzcoa gipuzkoa': (43.3120, -1.9784),
    'huelva': (37.2614, -6.9447),
    'huesca': (42.1401, -0.4089),
    'islas baleares illes balears': (39.6953, 3.0176),
    'jaen': (37.7796, -3.7849),
    'la rioja': (42.2871, -2.5396),
    'las palmas': (28.1235, -15.4363),
    'leon': (42.5987, -5.5671),
    'lleida': (41.6176, 0.6200),
    'lugo': (43.0125, -7.5559),
    'madrid': (40.4168, -3.7038),
    'malaga': (36.7213, -4.4214),
    'melilla': (35.2923, -2.9381),
    'murcia': (37.9834, -1.1299),
    'navarra nafarroa': (42.6954, -1.6761),
    'ourense': (42.3358, -7.8639),
    'pais vasco frances iparralde': (43.3569, -1.7650),
    'palencia': (42.0095, -4.5286),
    'pontevedra': (42.4299, -8.6444),
    'salamanca': (40.9701, -5.6635),
    'santa cruz de tenerife': (28.2916, -16.6291),
    'segovia': (40.9429, -4.1088),
    'sevilla': (37.3886, -5.9823),
    'soria': (41.7636, -2.4649),
    'tarragona': (41.1189, 1.2453),
    'teruel': (40.3440, -1.1065),
    'toledo': (39.8628, -4.0273),
    'valencia': (39.4699, -0.3763),
    'valladolid': (41.6523, -4.7245),
    'vizcaya bizkaia': (43.2630, -2.9350),
    'zamora': (41.5036, -5.7440),
    'zaragoza': (41.6488, -0.8891)
}

# Menú de navegación
menu = ["Inicio", "Vista Usuarios", "Vista Clientes", "Acerca de"]
choice = st.sidebar.selectbox("Navegación", menu)

# Control de flujo para cada sección
if choice == "Inicio":
    st.header("  Bienvenido al Análisis de Datos Inmobiliarios")
    st.write("""
    ¡Bienvenidos al proyecto final de Rodrigo, David y Raquel!
    
    Este proyecto es el resultado del trabajo en equipo en el Bootcamp de Data Analyst de la escuela Hack a Boss, donde nos propusimos analizar los datos inmobiliarios de "https://pisos.com". A través de técnicas avanzadas de extracción de datos (web scraping con Selenium) y el procesamiento de estos datos en Python, hemos desarrollado un sistema para estudiar las tendencias del mercado inmobiliario en España. La información extraída se estructuró y almacenó en una base de datos SQL, y posteriormente fue visualizada y analizada mediante dashboards interactivos en Power BI.
    
    Todo esto está integrado en esta aplicación que han abierto, hecha con Streamlit, para ofrecerles una experiencia completa y dinámica de análisis de datos inmobiliarios. Aquí podrán explorar mapas interactivos, filtros de propiedades, comparativas y estadísticas clave sobre el mercado.
    
    Durante el análisis, nos enfocamos en aspectos como la distribución de precios por metro cuadrado, el impacto de las características de los inmuebles (número de habitaciones, superficie, etc.) en su valor, así como la visualización geoespacial del mercado. Cada parte del proyecto se realizó con el objetivo de crear una herramienta útil y visualmente atractiva para cualquier persona interesada en el sector inmobiliario.
    
    ¡Esperamos que disfruten explorando estos datos tanto como nosotros disfrutamos desarrollando el proyecto!
    """)

elif choice == "Vista Usuarios":
    st.header("  Visualización de Datos y Comparador de Inmuebles")

    # Filtros de datos
    provincia = st.sidebar.selectbox("Selecciona una provincia:", df['provincia'].unique())
    tipo_transaccion = st.sidebar.selectbox("Selecciona una transacción:", df['venta/alquiler'].unique())
    
    # Filtrar el DataFrame según la provincia y el tipo de transacción
    df_filtrado = df[(df['provincia'] == provincia) & (df['venta/alquiler'] == tipo_transaccion)]

    # Excluir alquileres menores a 300 €
    if tipo_transaccion == 'Alquiler':
        df_filtrado = df_filtrado[df_filtrado['precio'] >= 300]

    # Obtener el mínimo y máximo de precio después del filtrado
    precio_min = int(df_filtrado['precio'].min()) if not df_filtrado.empty else 0
    precio_max = int(df_filtrado['precio'].max()) if not df_filtrado.empty else 1

    # Slider de rango de precio dinámico
    precio_min_slider, precio_max_slider = st.sidebar.slider(
        "Rango de precio (€):",
        min_value=precio_min,
        max_value=precio_max,
        value=(precio_min, precio_max),
        key='slider_precio' 
    )

    # Aplicar el rango de precio seleccionado al DataFrame filtrado
    df_filtrado = df_filtrado[(df_filtrado['precio'] >= precio_min_slider) & (df_filtrado['precio'] <= precio_max_slider)]

    # Mapa de propiedades por provincia con Plotly
    st.write("### Mapa de propiedades por provincia")

    # Crear el mapa con Plotly
    df_map = df_filtrado[['provincia', 'precio']].groupby('provincia').agg({'precio': ['count', 'mean']}).reset_index()
    df_map.columns = ['provincia', 'propiedades', 'precio_medio']
    df_map['lat'] = df_map['provincia'].apply(lambda x: provincia_centroides[x.lower()][0] if x.lower() in provincia_centroides else None)
    df_map['lon'] = df_map['provincia'].apply(lambda x: provincia_centroides[x.lower()][1] if x.lower() in provincia_centroides else None)

    fig_map = px.scatter_geo(
        df_map,
        lat='lat',
        lon='lon',
        text='provincia',
        size='propiedades',
        hover_name='provincia',
        hover_data={'precio_medio': ':.2f', 'lat': False, 'lon': False},
        title="Mapa de Propiedades por Provincia en España",
        projection='mercator'
    )

    # Configuración del mapa para ajustar el zoom dinámicamente
    fig_map.update_layout(
        title_font_size=20,
        geo=dict(
            center={'lat': 40, 'lon': -3},  
            projection_scale=12, 
            showland=True,
            landcolor='rgb(243, 243, 243)',
        ),
        margin={'r': 0, 't': 50, 'l': 0, 'b': 0}
    )

    if provincia in ['Las Palmas', 'Santa Cruz De Tenerife']:
        fig_map.update_layout(
            geo=dict(
                center={'lat': 35, 'lon': -10},  
                projection_scale=12, 
            )
        )

    fig_map.update_layout(mapbox_style="carto-positron")  # Estilo del mapa Carto Positron
    st.plotly_chart(fig_map, use_container_width=True)

    # Breve explicación del mapa
    st.write("""
    **Descripción del Mapa:** Este mapa muestra las propiedades disponibles en la provincia seleccionada. Cada marcador representa la ubicación aproximada de una provincia con propiedades disponibles, mostrando el número total de propiedades y el precio medio.
    """)

    # Tabla de propiedades filtradas
    st.write("### Inmuebles filtrados")
    st.dataframe(df_filtrado[['título', 'precio', 'habitaciones', 'superficie útil', 'baños', 'enlace']])
    st.write("""
    **Descripción de la Tabla:** La tabla muestra los inmuebles disponibles en la provincia seleccionada, con detalles sobre el precio, número de habitaciones, superficie útil, y más.
    """)

    # Comparador de inmuebles
    st.write("### Comparador de inmuebles")

    # Lista de opciones con título y id para evitar duplicados
    opciones_inmuebles = df_filtrado.apply(lambda x: f"{x['título']}", axis=1).tolist()
    id_map = dict(zip(opciones_inmuebles, df_filtrado['id']))

    # Seleccionar inmuebles basados en título (ID: id)
    inmueble_1 = st.selectbox("Selecciona el primer inmueble:", opciones_inmuebles, key='inmueble_1')
    inmueble_2 = st.selectbox("Selecciona el segundo inmueble:", opciones_inmuebles, key='inmueble_2')
    
    # Filtrar el comparador usando los id seleccionados
    comparador = df[df['id'].isin([id_map[inmueble_1], id_map[inmueble_2]])]

    # Mostrar comparación de características ocupando todo el ancho
    if not comparador.empty:
        st.write("### Comparativa de características")
        st.dataframe(comparador[['título', 'precio', 'habitaciones', 'superficie útil', 'baños', 'provincia']].T, width=1500)
        st.write("""
        **Descripción de la Comparativa:** Esta sección permite comparar dos propiedades seleccionadas, mostrando sus características clave como el precio, número de habitaciones, superficie útil, y más.
        """)

    # Visualización de la distribución de precios con outliers en rojo
    if not df_filtrado.empty:
        st.write("### Distribución de Precios en la Zona Seleccionada")
        
        # Calcular el z-score para identificar outliers
        df_filtrado['z_score'] = zscore(df_filtrado['precio'])
        df_filtrado['tipo_dato'] = np.where(df_filtrado['z_score'].abs() > 3, 'Datos Atípicos', 'Datos Normales')
        
        # Crear el gráfico
        fig = px.histogram(df_filtrado, x="precio", nbins=40, title="Distribución de Precios",
                           color='tipo_dato', color_discrete_map={'Datos Atípicos': 'red', 'Datos Normales': 'blue'})
        fig.update_layout(
            bargap=0.1,
            xaxis_title="Precio (€)",
            yaxis_title="Propiedades",
            legend_title_text="Tipo de Datos",
            plot_bgcolor='rgba(0,0,0,0)',  
            paper_bgcolor='rgba(0,0,0,0)' 
        )
        fig.update_xaxes(color='#00264d')  
        fig.update_yaxes(color='#00264d')  
        st.plotly_chart(fig, use_container_width=True)
        st.write("""
        **Descripción del Gráfico:** Este histograma muestra la distribución de los precios de las propiedades disponibles en la zona seleccionada. Los datos atípicos (outliers) se resaltan en rojo para identificar valores fuera del rango típico.
        """)
    else:
        st.write("No hay datos disponibles para los filtros seleccionados.")

elif choice == "Vista Clientes":
    st.title("  Análisis y Esquema de Base de Datos para Clientes")
    st.subheader("Representación de la base de datos y dashboard interactivo de Power BI")

    # Iframe del dashboard de Power BI
    st.markdown("""
    <iframe title="Dashboards alquileres (5)" width="600" height="373.5" src="https://app.powerbi.com/view?r=eyJrIjoiOWEyYWJjOTQtZmRkNy00OWU5LTgxODUtZDg4MGQ5OGRlOTMyIiwidCI6IjVlNzNkZTM1LWU4MjUtNGVkNS1iZTIyLTg4NTYzNTI3MDkxZSIsImMiOjl9" frameborder="0" allowFullScreen="true"></iframe>
    """, unsafe_allow_html=True)

    # Filtros de datos
    tipo_transaccion = st.sidebar.selectbox("Selecciona una transacción:", df['venta/alquiler'].unique(), key='selectbox_transaccion_clientes')

    # Filtrar DataFrame según los filtros seleccionados
    df_filtrado = df[df['venta/alquiler'] == tipo_transaccion]
    
    # Filtrar valores de alquiler por encima de 300 €
    if tipo_transaccion == 'Alquiler':
        df_filtrado = df_filtrado[df_filtrado['precio'] >= 300]

    # Encabezado de Análisis de Precio
    st.header("Análisis de Precio por Metro Cuadrado")
    # Multiselect para seleccionar provincias
    provincias_seleccionadas = st.multiselect(
        "Selecciona las provincias para visualizar",
        options=df_filtrado['provincia'].unique(),
        default=df_filtrado['provincia'].unique(),
        key='multiselect_provincias_clientes'
    )

    # Filtrar las provincias seleccionadas en el gráfico de cajas
    df_provincias_filtrado = df_filtrado[df_filtrado['provincia'].isin(provincias_seleccionadas)]
    # Excluir valores de "precio por m²" iguales a 0
    df_provincias_filtrado = df_provincias_filtrado[df_provincias_filtrado['precio por m²'] > 0]
    
    # Calcular la media del "precio por m²" y establecer el valor mínimo
    if not df_provincias_filtrado.empty:
        media_precio_m2 = df_provincias_filtrado['precio por m²'].mean()
        min_precio_m2 = media_precio_m2 / 2
        df_provincias_filtrado = df_provincias_filtrado[df_provincias_filtrado['precio por m²'] >= min_precio_m2]

    # Configurar el rango del eje Y basado en el tipo de transacción
    y_axis_range = [0, 200] if tipo_transaccion == 'Alquiler' else [3000, 10000]

    # Crear el gráfico de cajas si hay datos disponibles
    if not df_provincias_filtrado.empty:
        fig_box = px.box(
            df_provincias_filtrado,
            x="provincia",
            y="precio por m²",
            title="",
            labels={"precio por m²": "Precio por m² (€)"},
            width=1000,
            height=500
        )
        fig_box.update_yaxes(range=y_axis_range, title_text="Precio por m² (€)")
        fig_box.update_xaxes(tickangle=45)
        fig_box.update_traces(
            hovertemplate="<b>%{x}</b><br>Mediana: %{y:.2f}"
        )
        st.plotly_chart(fig_box, use_container_width=True)
        st.write("""
        **Descripción del Gráfico:** Este gráfico de cajas muestra la distribución de los precios por metro cuadrado en cada provincia seleccionada, permitiendo identificar rangos de precios comunes y valores atípicos.
        """)
    else:
        st.write("No hay datos disponibles para los filtros seleccionados.")
        # Análisis de correlación entre precio y otras variables
    if not df_filtrado.empty:
        st.header("Análisis de Correlación entre Variables")
        provincia_corr = st.sidebar.selectbox("Selecciona una provincia para el análisis de correlación:", df_filtrado['provincia'].unique(), key='provincia_corr_clientes')
        df_corr_filtrado = df_filtrado[df_filtrado['provincia'] == provincia_corr]

        fig_corr_superficie = px.scatter(
            df_corr_filtrado, x="superficie útil", y="precio",
            title="Correlación entre Precio y Superficie Útil",
            labels={"superficie útil": "Superficie Útil (m²)", "precio": "Precio (€)"}
        )
        fig_corr_superficie.update_xaxes(range=[0, 1000])  
        st.plotly_chart(fig_corr_superficie, use_container_width=True)
        st.write("""
        **Descripción del Gráfico:** Este gráfico de dispersión muestra la correlación entre el precio y la superficie útil de las propiedades en la provincia seleccionada. Se pueden observar tendencias y patrones que indican cómo el precio cambia con respecto al tamaño de la propiedad.
        """)

        # Agrupar por número de habitaciones y calcular el precio promedio
        df_grouped = df_corr_filtrado.groupby('habitaciones')['precio'].mean().reset_index()

        # Crear el gráfico de barras
        fig_bar = px.bar(
            df_grouped, x="habitaciones", y="precio",
            title="Precio Promedio por Número de Habitaciones",
            labels={"habitaciones": "Número de Habitaciones", "precio": "Precio Promedio (€)"},
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.write("""
        **Descripción del Gráfico:** Este gráfico de barras muestra el precio promedio de las propiedades en función del número de habitaciones, lo que permite identificar cómo varía el precio según la cantidad de habitaciones en la provincia seleccionada.
        """)
    else:
        st.write("No hay datos disponibles para el análisis de correlación.")
    
elif choice == "Acerca de":
    st.header("  Sobre el Proyecto")

    st.write("""
    Este proyecto de análisis inmobiliario ha sido desarrollado para proporcionar visualizaciones interactivas de datos
    de propiedades en venta y alquiler en España. Utiliza tecnologías de análisis geográfico y visualización para permitir
    un mejor entendimiento del mercado inmobiliario.

    **Integrantes del proyecto**:
    - Rodrigo González - LinkedIn: https://www.linkedin.com/in/rodrigo-gonzalez-ferreira
     
    - David López Patiño - LinkedIn: https://www.linkedin.com/in/david-lopez-pati%C3%B1o-29aa211a5
    
    - Raquel Bastida - LinkedIn: https://www.linkedin.com/in/raquel-bastida
    """)

    # Fotos
    st.write("**Fotos de los integrantes**")
    col1, col2, col3 = st.columns(3)

    with col1:
        img_rodrigo = Image.open("Rodrigo.png").resize((150, 200))
        st.image(img_rodrigo, caption="Rodrigo González", use_column_width=False)
    with col2:
        img_david = Image.open("David.jpeg").resize((150, 200))
        st.image(img_david, caption="David López Patiño", use_column_width=False)
    with col3:
        img_raquel = Image.open("Raquel.jpeg").resize((150, 200))
        st.image(img_raquel, caption="Raquel Bastida", use_column_width=False)

# Cargar la imagen desde la ruta y mostrarla en la parte inferior de la barra lateral
ruta_imagen = 'imagen_proyecto.png'
imagen = Image.open(ruta_imagen)

with st.sidebar:
    st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True) 
    st.image(imagen, use_column_width=True)