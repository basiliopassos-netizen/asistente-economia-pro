import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
import re
from pypdf import PdfReader
import os
import plotly.express as px

# 1. Configuración de página compacta
st.set_page_config(page_title="PocketAdmin Pro", layout="centered", page_icon="🌱")

# Estilo CSS para que las pestañas se vean bien en móvil
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        padding: 10px 5px; 
        font-size: 14px;
    }
    div.block-container { padding-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)

ARCHIVO_DATOS = "mis_gastos.csv"
ARCHIVO_IDENTIDAD = "identidad.txt"

# --- FUNCIONES DE IDENTIDAD Y DATOS ---
def obtener_identidad():
    if os.path.exists(ARCHIVO_IDENTIDAD):
        with open(ARCHIVO_IDENTIDAD, "r") as f:
            datos = f.read().split("|")
            return {"nombre": datos[0], "genero": datos[1]}
    return None

def guardar_identidad(nombre, genero):
    with open(ARCHIVO_IDENTIDAD, "w") as f:
        f.write(f"{nombre}|{genero}")

def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        df = pd.read_csv(ARCHIVO_DATOS)
        df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
        return df
    return pd.DataFrame(columns=['Fecha', 'Producto', 'Categoría', 'Precio'])

def guardar_datos(df_nuevo):
    df_historial = cargar_datos()
    df_actualizado = pd.concat([df_historial, df_nuevo], ignore_index=True)
    df_actualizado.to_csv(ARCHIVO_DATOS, index=False)
    return df_actualizado

# --- MOTOR DE CRECIMIENTO VISUAL (LA PLANTA) ---
def mostrar_planta_evolutiva(df):
    num_registros = len(df)
    if num_registros == 0:
        st.markdown("<h1 style='text-align: center;'>🌱</h1>", unsafe_allow_html=True)
        return "Tu camino empieza aquí con una semilla."
    elif num_registros < 10:
        st.markdown("<h1 style='text-align: center;'>🌿</h1>", unsafe_allow_html=True)
        return "Tu diario está brotando con fuerza."
    else:
        st.markdown("<h1 style='text-align: center;'>🌸</h1>", unsafe_allow_html=True)
        return "Tu bienestar financiero está floreciendo."

# --- PROCESADOR DE TEXTO LIMPIO ---
CATEGORIAS = {
    "Bienestar": ["manzana", "verdura", "pollo", "pescado", "agua", "leche", "huevos", "pan", "luz", "gasolina"],
    "Momentos": ["chuches", "refresco", "coca", "cerveza", "vino", "chocolate", "bolleria", "pizza", "netflix"]
}
FILTRO = ["mastercard", "visa", "tarjeta", "total", "iva", "subtotal", "cif", "factura"]

def analizar_texto(texto):
    lineas = texto.split('\n')
    datos = []
    fecha_hoy = pd.Timestamp.now().date()
    for linea in lineas:
        match = re.search(r'(\d+[\.,]\d{2})', linea)
        if match and not any(p in linea.lower() for p in FILTRO):
            precio = float(match.group(1).replace(',', '.'))
            nombre = re.sub(r'[^a-zA-Z ]', '', linea.replace(match.group(1), "")).strip()
            if len(nombre) > 2:
                cat = "Otros"
                for c, palabras in CATEGORIAS.items():
                    if any(p in nombre.lower() for p in palabras): cat = c; break
                datos.append([fecha_hoy, nombre.capitalize(), cat, precio])
    return datos

# --- INTERFAZ PRINCIPAL ---
def main():
    identidad = obtener_identidad()
    
    if identidad is None:
        st.title("✨ Crea tu Guía")
        n = st.text_input("¿Qué nombre le das?")
        g = st.selectbox("Género", ["Femenino", "Masculino"])
        if st.button("Bautizar"):
            guardar_identidad(n, g); st.rerun()
        return

    # App Activa
    nombre = identidad['nombre']
    df_total = cargar_datos()
    
    # Header Compacto
    col_plant, col_text = st.columns([1, 3])
    with col_plant:
        msj_planta = mostrar_planta_evolutiva(df_total)
    with col_text:
        st.write(f"**{nombre}** & tú")
        st.caption(msj_planta)

    # Pestañas con Iconos para móvil
    tab1, tab2, tab3 = st.tabs(["📥 Registro", "📊 Mapa", "📖 Diario"])

    with tab1:
        archivos = st.file_uploader("Sube tickets", accept_multiple_files=True)
        if archivos and st.button("✨ Guardar Todo"):
            items = []
            for a in archivos:
                txt = ""
                if a.type == "application/pdf":
                    for p in PdfReader(a).pages: txt += p.extract_text()
                else:
                    txt = pytesseract.image_to_string(Image.open(a))
                items.extend(analizar_texto(txt))
            if items:
                guardar_datos(pd.DataFrame(items, columns=['Fecha', 'Producto', 'Categoría', 'Precio']))
                st.success("Guardado."); st.rerun()

    with tab2:
        if not df_total.empty:
            st.plotly_chart(px.pie(df_total, values='Precio', names='Categoría', hole=0.6, 
                             color_discrete_sequence=px.colors.qualitative.Pastel), use_container_width=True)
        else: st.info("Sin datos.")

    with tab3:
        st.dataframe(df_total, use_container_width=True)
        if st.sidebar.button("⚠️ Resetear Todo"):
            if os.path.exists(ARCHIVO_IDENTIDAD): os.remove(ARCHIVO_IDENTIDAD)
            if os.path.exists(ARCHIVO_DATOS): os.remove(ARCHIVO_DATOS)
            st.rerun()

if __name__ == "__main__":
    main()
