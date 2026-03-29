import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
import re
from pypdf import PdfReader
import os
import plotly.express as px

# 1. Configuración de página con más aire
st.set_page_config(page_title="Mi Guía de Bienestar", layout="centered", page_icon="🌱")

# Estilo CSS para arreglar el corte de la planta y mejorar las pestañas
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { padding: 8px 4px; font-size: 13px; }
    div.block-container { padding-top: 2.5rem; } /* Más espacio arriba */
    .stChatFloatingInputContainer { bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

ARCHIVO_DATOS = "mis_gastos.csv"
ARCHIVO_IDENTIDAD = "identidad.txt"

# --- FUNCIONES DE PERSISTENCIA ---
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

# --- LÓGICA DE LA PLANTA (ÁRBOL/BAMBÚ) ---
def mostrar_evolucion(df):
    num = len(df)
    if num == 0:
        return "🌱", "Tu semilla está lista para brotar."
    elif num < 15:
        return "🌿", "Tu bambú está creciendo con cada registro."
    elif num < 40:
        return "🎋", "¡Mira cómo sube! Tienes el control."
    else:
        return "🌳", "Tu árbol de bienestar ya da sombra y paz."

# --- PROCESADOR ---
CATEGORIAS = {
    "Bienestar": ["manzana", "verdura", "pollo", "pescado", "agua", "leche", "huevos", "pan", "luz", "gasolina"],
    "Momentos": ["chuches", "refresco", "coca", "cerveza", "vino", "chocolate", "bolleria", "pizza"]
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

# --- INTERFAZ ---
def main():
    identidad = obtener_identidad()
    
    if identidad is None:
        st.title("✨ Bienvenida")
        n = st.text_input("¿Qué nombre me das para siempre?")
        g = st.selectbox("Género", ["Femenino", "Masculino"])
        if st.button("Crear vínculo"):
            if n: guardar_identidad(n, g); st.rerun()
        return

    nombre = identidad['nombre']
    df_total = cargar_datos()
    icono, frase = mostrar_evolucion(df_total)
    
    # Header Compacto y Visual
    col_texto, col_icono = st.columns([3, 1])
    with col_texto:
        st.subheader(f"{nombre} & tú")
        st.caption(frase)
    with col_icono:
        st.markdown(f"<h1 style='font-size: 50px; margin:0;'>{icono}</h1>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📥 Registro", "📊 Mapa", "📖 Diario"])

    with tab1:
        archivos = st.file_uploader("Tickets (PDF/Fotos)", accept_multiple_files=True, label_visibility="collapsed")
        if archivos:
            if st.button(f"✨ Guardar en mi historial"):
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
                    st.success("Guardado con éxito."); st.rerun()

    with tab2:
        if not df_total.empty:
            fig = px.pie(df_total, values='Precio', names='Categoría', hole=0.6, 
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("Sube algo para ver tu mapa.")

    with tab3:
        st.write("### Tu historial de pasos")
        st.dataframe(df_total, use_container_width=True)
        
        st.divider()
        # BOTÓN DE BORRAR DEVUELTO A SU SITIO
        if st.button("🗑️ Borrar todo el historial"):
            if os.path.exists(ARCHIVO_DATOS): os.remove(ARCHIVO_DATOS)
            st.rerun()

    # Opción de resetear identidad (Oculto al final)
    with st.expander("Opciones de identidad"):
        if st.button("⚠️ Resetear nombre y vínculo"):
            if os.path.exists(ARCHIVO_IDENTIDAD): os.remove(ARCHIVO_IDENTIDAD)
            st.rerun()

if __name__ == "__main__":
    main()
