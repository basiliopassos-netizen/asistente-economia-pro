import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
import re
from pypdf import PdfReader
import os
import plotly.express as px

# 1. Configuración con estilo visual profundo
st.set_page_config(page_title="Mi Guía de Bienestar", layout="centered", page_icon="🌳")

# --- DISEÑO CSS PERSONALIZADO (Pestañas gorditas y tipografía) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital@1&family=Source+Sans+Pro:wght@300;400&display=swap');

    /* Títulos con tipografía elegante */
    h2, h3, .stSubheader {
        font-family: 'Playfair Display', serif;
        color: #4A5859;
    }

    /* Fondo de la app más suave */
    .stApp {
        background-color: #F9F7F2;
    }

    /* Pestañas estilo "Botón Gordito" */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px; /* Más altas */
        background-color: #FFFFFF;
        border-radius: 15px; /* Redondeadas */
        border: 1px solid #E0DDCF;
        padding: 0px 20px;
        font-weight: 600;
        font-size: 16px !format;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #F0EDE4;
    }
    .stTabs [aria-selected="true"] {
        background-color: #DDE5B6 !important; /* Color verde suave cuando está activo */
        border: 1px solid #A9B388 !important;
    }

    /* Ajuste de la planta */
    .planta-header {
        font-size: 60px;
        filter: drop-shadow(2px 4px 6px rgba(0,0,0,0.1));
    }
    </style>
    """, unsafe_allow_html=True)

ARCHIVO_DATOS = "mis_gastos.csv"
ARCHIVO_IDENTIDAD = "identidad.txt"

# --- FUNCIONES BASE ---
def obtener_identidad():
    if os.path.exists(ARCHIVO_IDENTIDAD):
        with open(ARCHIVO_IDENTIDAD, "r") as f:
            datos = f.read().split("|")
            return {"nombre": datos[0], "genero": datos[1]}
    return None

def guardar_identidad(nombre, genero):
    with open(ARCHIVO_IDENTIDAD, "w") as f: f.write(f"{nombre}|{genero}")

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

def mostrar_evolucion(df):
    num = len(df)
    if num == 0: return "🌱", "Tu semilla está lista."
    elif num < 15: return "🌿", "Tu bambú crece contigo."
    elif num < 40: return "🎋", "Tienes el control absoluto."
    else: return "🌳", "Tu árbol de paz ya te protege."

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
        n = st.text_input("¿Qué nombre me das?")
        g = st.selectbox("Género", ["Femenino", "Masculino"])
        if st.button("Crear vínculo"):
            if n: guardar_identidad(n, g); st.rerun()
        return

    nombre = identidad['nombre']
    df_total = cargar_datos()
    icono, frase = mostrar_evolucion(df_total)
    
    # Header con Planta a la derecha
    c_izq, c_der = st.columns([3, 1])
    with c_izq:
        st.subheader(f"{nombre} & tú")
        st.caption(frase)
    with c_der:
        st.markdown(f"<div class='planta-header'>{icono}</div>", unsafe_allow_html=True)

    # Pestañas Gorditas con Iconos Emocionales
    t1, t2, t3 = st.tabs(["📥 Registro", "🧭 Mi Mapa", "📖 Mi Diario"])

    with t1:
        archivos = st.file_uploader("", accept_multiple_files=True)
        if archivos and st.button(f"✨ Confiar a {nombre}"):
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

    with t2:
        if not df_total.empty:
            st.write("### Tus prioridades actuales")
            fig = px.pie(df_total, values='Precio', names='Categoría', hole=0.6, 
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("Sube un registro para orientarte.")

    with t3:
        st.write("### Pasos registrados")
        st.dataframe(df_total, use_container_width=True)
        if st.button("🗑️ Limpiar Diario"):
            if os.path.exists(ARCHIVO_DATOS): os.remove(ARCHIVO_DATOS); st.rerun()

    # Reset oculto
    with st.expander("Opciones"):
        if st.button("⚠️ Reiniciar todo"):
            if os.path.exists(ARCHIVO_IDENTIDAD): os.remove(ARCHIVO_IDENTIDAD)
            st.rerun()

if __name__ == "__main__":
    main()
