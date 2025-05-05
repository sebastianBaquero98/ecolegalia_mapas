# app.py - Chatbot para verificador geoespacial ambiental con interface conversacional

import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
from fpdf import FPDF
import streamlit as st

# Funciones para generar PDFs (sin cambios)
def generar_formato_permiso_emisiones_pdf(lat, lon, logo_path):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=8, w=40)
        pdf.set_xy(50, 15)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Formato de Solicitud de Permiso de Emisiones Atmosféricas", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"""
1. DATOS DEL SOLICITANTE
Nombre del solicitante: ERCO S.A.S
NIT: ____________________
Representante legal: ____________________
Dirección: ____________________
Correo electrónico: ____________________
Teléfono: ____________________
Autoridad Ambiental Competente: CORPOGUAJIRA

2. UBICACIÓN DEL PROYECTO
Departamento: La Guajira
Municipio: ____________________
Coordenadas: LAT {lat}, LON {lon}

3. DESCRIPCIÓN DEL PROYECTO
Nombre del Proyecto: Instalación de subestación eléctrica
Justificación técnica: Instalación necesaria para garantizar confiabilidad energética en zona rural de La Guajira.

4. FUENTES DE EMISIÓN (ejemplos)
Planta de respaldo - Fija - Diésel - 500 kW - 4 h/día - MP, CO, NOx
Sistema de climatización - Fija - Eléctrico - - - 8 h/día - COVs
Compresor de aire - Fija - Eléctrico - 200 HP - 6 h/día - Aceite, ruido
Soldadura - Móvil - - - Variable - MP fino, óxidos metálicos

5. DOCUMENTOS ANEXOS
- Cámara de comercio actualizada
- Planos técnicos
- Certificado de fabricante
- Manual de operación y mantenimiento
- Inventario de emisiones
- Formato único de solicitud
- Pago de tasas ambientales

6. NORMATIVA APLICABLE
- Decreto 1076 de 2015
- Resolución 909 de 2008
- Resolución 2254 de 2017
    """)
    pdf_path = "formato_permiso_emisiones.pdf"
    pdf.output(pdf_path)
    return pdf_path

def generar_formato_permiso_vertimientos_pdf(lat, lon, logo_path):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=8, w=40)
        pdf.set_xy(50, 15)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Formato de Solicitud de Permiso de Vertimientos", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"""
1. DATOS DEL SOLICITANTE
Nombre del solicitante: ERCO S.A.S
NIT: ____________________
Representante legal: ____________________
Dirección: ____________________
Correo electrónico: ____________________
Teléfono: ____________________
Autoridad Ambiental Competente: CORPOGUAJIRA

2. UBICACIÓN DEL PUNTO DE VERTIMIENTO
Cuerpo receptor: ____________________
Tipo: Superficial / Suelo
Coordenadas: LAT {lat}, LON {lon}
Descripción: ____________________

3. CARACTERIZACIÓN DEL VERTIMIENTO
Origen: Doméstico / Industrial / Mixto
Caudal (l/s): __________
Frecuencia: Continua / Intermitente
Carga contaminante estimada: __________

4. PARÁMETROS A ANALIZAR (Resolución 0631/2015)
- DBO5, DQO, SST, pH, temperatura
- Grasas y aceites
- Coliformes totales y fecales
- Metales (si aplica)

5. SISTEMA DE TRATAMIENTO
Tecnología: ____________________
Eficiencia esperada: _______%
Plan de mantenimiento: ____________________

6. PLAN DE MONITOREO
Frecuencia: Trimestral / Semestral
Método analítico: NTC IDEAM
Laboratorio: ____________________

7. DOCUMENTOS ANEXOS
- Cámara de comercio actualizada
- Planos del sistema y punto de vertimiento
- Estudio de caracterización
- Registro fotográfico del sitio
- Declaración juramentada
- Pago de tasas por evaluación

8. NORMATIVA APLICABLE
- Decreto 1076 de 2015
- Resolución 0631 de 2015
- Ley 99 de 1993
    """)
    pdf_path = "formato_permiso_vertimientos.pdf"
    pdf.output(pdf_path)
    return pdf_path

# Función para realizar el análisis ambiental
def realizar_analisis_ambiental(lat, lon):
    punto = Point(lon, lat)
    
    # Cargar capas GeoJSON
    try:
        areas = gpd.read_file("areas_protegidas.geojson")
        ecosistemas = gpd.read_file("ecosistemas.geojson")
        humedales = gpd.read_file("humedales.geojson")
        inundaciones = gpd.read_file("riesgos_inundacion.geojson")
        suelo = gpd.read_file("uso_suelo.geojson")
    except Exception as e:
        return f"Error al cargar las capas geográficas: {str(e)}", None
    
    # Intersección espacial
    inter_areas = areas[areas.geometry.intersects(punto)]
    inter_ecos = ecosistemas[ecosistemas.geometry.intersects(punto)]
    inter_humedales = humedales[humedales.geometry.intersects(punto)]
    inter_inundacion = inundaciones[inundaciones.geometry.intersects(punto)]
    inter_suelo = suelo[suelo.geometry.intersects(punto)]
    
    # Crear mapa
    mapa = folium.Map(location=[lat, lon], zoom_start=13, tiles='Esri.WorldImagery')
    folium.Marker([lat, lon], tooltip="📍 Proyecto: Subestación en La Guajira").add_to(mapa)
    
    # Función para verificar si un campo está disponible
    def campo_disponible(gdf, campo):
        return campo if campo in gdf.columns else None
    
    # Añadir capas al mapa
    if campo_disponible(areas, "nombre"):
        folium.GeoJson(areas, name="Áreas protegidas", tooltip=folium.GeoJsonTooltip(fields=["nombre"])).add_to(mapa)
    else:
        folium.GeoJson(areas, name="Áreas protegidas").add_to(mapa)

    if campo_disponible(ecosistemas, "nombre"):
        folium.GeoJson(ecosistemas, name="Ecosistemas estratégicos", tooltip=folium.GeoJsonTooltip(fields=["nombre"])).add_to(mapa)
    else:
        folium.GeoJson(ecosistemas, name="Ecosistemas estratégicos").add_to(mapa)

    if campo_disponible(humedales, "nombre"):
        folium.GeoJson(humedales, name="Humedales", tooltip=folium.GeoJsonTooltip(fields=["nombre"])).add_to(mapa)
    else:
        folium.GeoJson(humedales, name="Humedales").add_to(mapa)

    if campo_disponible(inundaciones, "nivel_riesgo"):
        folium.GeoJson(inundaciones, name="Zonas de inundación", tooltip=folium.GeoJsonTooltip(fields=["nivel_riesgo"])).add_to(mapa)
    else:
        folium.GeoJson(inundaciones, name="Zonas de inundación").add_to(mapa)

    if campo_disponible(suelo, "uso"):
        folium.GeoJson(suelo, name="Uso del suelo", tooltip=folium.GeoJsonTooltip(fields=["uso"])).add_to(mapa)
    else:
        folium.GeoJson(suelo, name="Uso del suelo").add_to(mapa)

    folium.LayerControl().add_to(mapa)
    
    # Generar resultado textual
    resultado_texto = ""
    if not inter_areas.empty:
        nombre_area = inter_areas.iloc[0].get('nombre', 'Área sin nombre')
        resultado_texto += f"🔴 [APROBADO] Área protegida: {nombre_area}\n- Requiere permiso de CORPOGUAJIRA y evaluación técnica.\n\n"
    if not inter_ecos.empty:
        nombre_area = inter_ecos.iloc[0].get('nombre', 'Ecosistema sin nombre')
        resultado_texto += f"🔴 [APROBADO] Ecosistema estratégico: {nombre_area}\n- Priorizar medidas de conservación.\n\n"
    if not inter_humedales.empty:
        nombre_area = inter_humedales.iloc[0].get('nombre', 'Humedal sin nombre')
        resultado_texto += f"⚠️ [ALERTA] Humedal: {nombre_area}\n- Posible restricción del POT y necesidad de EIA.\n\n"
    if not inter_inundacion.empty:
        riesgo = inter_inundacion.iloc[0].get('nivel_riesgo', 'N/A')
        resultado_texto += f"⚠️ [ALERTA] Zona de riesgo de inundación: Nivel {riesgo}\n- Evaluar rediseño del proyecto o medidas de mitigación.\n\n"
    if not inter_suelo.empty:
        uso = inter_suelo.iloc[0].get('uso', 'Sin información')
        resultado_texto += f"ℹ️ [INFO] Uso del suelo según POT: {uso}\n\n"

    if not resultado_texto:
        resultado_texto = "✅ El predio no presenta intersección con restricciones ambientales conocidas en la zona."
    
    return resultado_texto, mapa

# Configuración de la página Streamlit
st.set_page_config(
    page_title="EcoChatBot | Verificador Ambiental", 
    layout="centered",
    page_icon="🌱"
)

# Inicializar el estado de la sesión
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 ¡Hola! Soy el asistente virtual del Verificador Ambiental Geoespacial. Puedo ayudarte a evaluar si tu proyecto en La Guajira intersecta con áreas protegidas u otras zonas ambientalmente sensibles. ¿Cómo te llamas?"}
    ]
if 'nombre' not in st.session_state:
    st.session_state.nombre = ""
if 'lat' not in st.session_state:
    st.session_state.lat = None
if 'lon' not in st.session_state:
    st.session_state.lon = None
if 'resultado_analisis' not in st.session_state:
    st.session_state.resultado_analisis = None
if 'mapa_generado' not in st.session_state:
    st.session_state.mapa_generado = None
if 'mostrar_mapa' not in st.session_state:
    st.session_state.mostrar_mapa = False

# Título y descripción
st.title("🌱 EcoChatBot - Verificador Ambiental")
st.markdown("""
Este chatbot te guiará para verificar si tu proyecto en La Guajira se encuentra en áreas protegidas u otras zonas ambientalmente sensibles.
""")

# Mostrar mensajes del chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Mostrar mapa si está disponible
if st.session_state.mostrar_mapa and st.session_state.mapa_generado:
    with st.chat_message("assistant"):
        st.markdown("🗺️ **Aquí está el mapa de tu ubicación con las capas ambientales:**")
        st_folium(st.session_state.mapa_generado, width=700, height=400)

# Lógica del chatbot
def procesar_respuesta(mensaje_usuario):
    st.session_state.messages.append({"role": "user", "content": mensaje_usuario})
    
    if st.session_state.step == 0:
        # Capturar el nombre
        st.session_state.nombre = mensaje_usuario
        respuesta = f"¡Gracias, {st.session_state.nombre}! Ahora necesito la latitud del proyecto. Por ejemplo, para La Guajira un valor típico sería 11.5448."
        st.session_state.step = 1
    
    elif st.session_state.step == 1:
        # Capturar la latitud
        try:
            st.session_state.lat = float(mensaje_usuario)
            respuesta = "Perfecto. Ahora necesito la longitud del proyecto. Por ejemplo, para La Guajira un valor típico sería -72.9083."
            st.session_state.step = 2
        except ValueError:
            respuesta = "Parece que no ingresaste un número válido. Por favor, ingresa solo el valor numérico de la latitud (por ejemplo: 11.5448)."
    
    elif st.session_state.step == 2:
        # Capturar la longitud
        try:
            st.session_state.lon = float(mensaje_usuario)
            respuesta = f"Gracias, {st.session_state.nombre}. Estoy analizando las coordenadas (Latitud: {st.session_state.lat}, Longitud: {st.session_state.lon})..."
            
            # Realizar análisis ambiental
            resultado, mapa = realizar_analisis_ambiental(st.session_state.lat, st.session_state.lon)
            st.session_state.resultado_analisis = resultado
            st.session_state.mapa_generado = mapa
            
            respuesta += f"\n\n📋 **Resultado del análisis:**\n\n{resultado}\n\nPuedo mostrarte el mapa o generar documentos PDF para permisos. ¿Qué prefieres?\n1️⃣ Ver mapa\n2️⃣ Generar PDF de permiso de emisiones\n3️⃣ Generar PDF de permiso de vertimientos\n4️⃣ Iniciar nuevo análisis"
            
            st.session_state.step = 3
        except ValueError:
            respuesta = "Parece que no ingresaste un número válido. Por favor, ingresa solo el valor numérico de la longitud (por ejemplo: -72.9083)."
    
    elif st.session_state.step == 3:
        # Procesar opciones
        if "1" in mensaje_usuario or "mapa" in mensaje_usuario.lower():
            respuesta = "Mostrando el mapa con las capas ambientales."
            st.session_state.mostrar_mapa = True
        
        elif "2" in mensaje_usuario or "emisiones" in mensaje_usuario.lower():
            logo = "logo_ecolegalia.png"  # Asegúrate de tener este archivo
            try:
                ruta_pdf = generar_formato_permiso_emisiones_pdf(st.session_state.lat, st.session_state.lon, logo)
                respuesta = f"He generado el PDF de permiso de emisiones para tus coordenadas. Puedes descargarlo usando el botón que aparece debajo."
                # Nota: El botón de descarga se añadirá fuera de esta función
                st.session_state.pdf_emisiones = True
            except Exception as e:
                respuesta = f"Lo siento, hubo un error al generar el PDF: {str(e)}"
        
        elif "3" in mensaje_usuario or "vertimientos" in mensaje_usuario.lower():
            logo = "logo_ecolegalia.png"  # Asegúrate de tener este archivo
            try:
                ruta_pdf = generar_formato_permiso_vertimientos_pdf(st.session_state.lat, st.session_state.lon, logo)
                respuesta = f"He generado el PDF de permiso de vertimientos para tus coordenadas. Puedes descargarlo usando el botón que aparece debajo."
                # Nota: El botón de descarga se añadirá fuera de esta función
                st.session_state.pdf_vertimientos = True
            except Exception as e:
                respuesta = f"Lo siento, hubo un error al generar el PDF: {str(e)}"
        
        elif "4" in mensaje_usuario or "nuevo" in mensaje_usuario.lower() or "reiniciar" in mensaje_usuario.lower():
            respuesta = "Iniciando un nuevo análisis. ¿Cuál es tu nombre?"
            st.session_state.step = 0
            st.session_state.lat = None
            st.session_state.lon = None
            st.session_state.resultado_analisis = None
            st.session_state.mapa_generado = None
            st.session_state.mostrar_mapa = False
            if 'pdf_emisiones' in st.session_state:
                del st.session_state.pdf_emisiones
            if 'pdf_vertimientos' in st.session_state:
                del st.session_state.pdf_vertimientos
        
        else:
            respuesta = "No entendí tu selección. Por favor, elige una de estas opciones:\n1️⃣ Ver mapa\n2️⃣ Generar PDF de permiso de emisiones\n3️⃣ Generar PDF de permiso de vertimientos\n4️⃣ Iniciar nuevo análisis"
    
    st.session_state.messages.append({"role": "assistant", "content": respuesta})

# Input para usuario
if mensaje_usuario := st.chat_input("Escribe tu mensaje aquí..."):
    procesar_respuesta(mensaje_usuario)
    st.rerun()

# Botones de descarga para los PDFs si están disponibles
if st.session_state.step == 3:
    col1, col2 = st.columns(2)
    
    if 'pdf_emisiones' in st.session_state and st.session_state.pdf_emisiones:
        with col1:
            with open("formato_permiso_emisiones.pdf", "rb") as f:
                st.download_button("📥 Descargar PDF Permiso Emisiones", f, file_name="formato_permiso_emisiones.pdf", mime="application/pdf")
    
    if 'pdf_vertimientos' in st.session_state and st.session_state.pdf_vertimientos:
        with col2:
            with open("formato_permiso_vertimientos.pdf", "rb") as f:
                st.download_button("📥 Descargar PDF Permiso Vertimientos", f, file_name="formato_permiso_vertimientos.pdf", mime="application/pdf")