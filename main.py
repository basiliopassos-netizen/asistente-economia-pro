import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
import re
from pypdf import PdfReader
import os
import plotly.express as px

# Configuración con CSS para juntar las pestañas
st.set_page_config(page_title="PocketAdmin", layout="wide", page_icon="🛡️")

# --- ESTILO CSS PERSONALIZADO ---
st.markdown("""
    <style>
    /* Juntar las pestañas y quitar márgenes excesivos */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-left: 10px;
        padding-right: 10px;
        font-size: 14px;
    }
    /* Hacer que el contenedor principal sea menos ancho para evitar scroll lateral */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

ARCHIVO_DATOS = "mis_gastos.csv"

# --- LÓGICA DE DATOS ---
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

# --- MOTOR EMOCIONAL ---
def obtener_mensaje(df, nombre, genero, modo_control):
    adj = "lista" if genero == "Femenino" else "listo"
    total = df['Precio'].sum() if not df.empty else 0
    base = f"Hola, soy **{nombre}** y estoy {adj} para **cuidar de ti y de tu dinero**."
    
    if modo_control:
        return f"🛡️ {base}\n\n**Modo Control:** Todo bajo vigilancia. Llevamos **{total:.2f}€** registrados."
    else:
        return f"🌟 {base}\n\nLlevamos **{total:.2f}€** acumulados."

# --- PROCESADOR ---
PALABRAS_FILTRO = ["mastercard", "visa", "tarjeta", "total", "iva", "base imponible", "subtotal", "efectivo", "cambio", "cif", "telefono", "atendido", "ticket", "factura"]

def analizar_texto(texto):
    lineas = texto.split('\n')
    datos = []
    fecha_hoy = pd.Timestamp.now().date()
    for linea in lineas:
        linea_min = linea.lower()
        match = re.search(r'(\d+[\.,]\d{2})', linea)
        es_basura = any(p in linea_min for p in PALABRAS_FILTRO)
        
        if match and not es_basura:
            precio = float(match.group(1).replace(',', '.'))
            nombre = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ ]', '', linea.replace(match.group(1), "")).strip()
            if len(nombre) > 2:
                datos.append([fecha_hoy, nombre.capitalize(), "Varios", precio])
    return datos

# --- INTERFAZ ---
def main():
    # Menú Lateral más discreto
    with st.sidebar:
        st.header("⚙️ Tú")
        nombre_guia = st.text_input("Asistente", value="Ana")
        genero_guia = st.selectbox("Voz", ["Femenino", "Masculino"])
        modo_control = st.toggle("🆘 Modo Control", value=False)
    
    df_total = cargar_datos()
    st.chat_message("assistant").write(obtener_mensaje(df_total, nombre_guia, genero_guia, modo_control))

    # Pestañas con nombres más cortos para que quepan
    tab1, tab2, tab3 = st.tabs(["📥 Subir", "📊 Análisis", "📋 Historial"])

    with tab1:
        archivos = st.file_uploader("Sube Tickets", type=['pdf', 'jpg', 'png', 'jpeg'], accept_multiple_files=True)
        if archivos:
            if st.button(f"🚀 Procesar {len(archivos)} archivos"):
                todos_los_items = []
                for archivo in archivos:
                    texto = ""
                    if archivo.type == "application/pdf":
                        reader = PdfReader(archivo)
                        for page in reader.pages: texto += page.extract_text()
                    else:
                        texto = pytesseract.image_to_string(Image.open(archivo))
                    todos_los_items.extend(analizar_texto(texto))
                
                if todos_los_items:
                    guardar_datos(pd.DataFrame(todos_los_items, columns=['Fecha', 'Producto', 'Categoría', 'Precio']))
                    st.success("Guardado.")
                    st.rerun()

    with tab2:
        if not df_total.empty:
            st.plotly_chart(px.pie(df_total, values='Precio', names='Categoría', hole=0.5, height=300), use_container_width=True)
            st.plotly_chart(px.line(df_total.groupby('Fecha')['Precio'].sum().reset_index(), x='Fecha', y='Precio', height=300), use_container_width=True)
        else:
            st.info("Sin datos.")

    with tab3:
        st.write("### Mi Diario")
        st.dataframe(df_total, use_container_width=True)
        if st.button("🗑️ Limpiar"):
            if os.path.exists(ARCHIVO_DATOS): os.remove(ARCHIVO_DATOS); st.rerun()

if __name__ == "__main__":
    main()
