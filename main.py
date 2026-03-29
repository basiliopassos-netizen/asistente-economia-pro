import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
import re
from pypdf import PdfReader
import os
import plotly.express as px

# 1. Configuración de página y Estilo Visual Avanzado
st.set_page_config(page_title="PocketAdmin Pro", layout="wide", page_icon="🧘")

st.markdown("""
    <style>
    /* Estilo para las pestañas */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        padding: 8px 15px; 
        font-size: 16px;
        font-weight: 500;
    }
    /* Tarjetas de métricas personalizadas */
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #00c0f2;
        margin-bottom: 20px;
    }
    .block-container { padding-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)

ARCHIVO_DATOS = "mis_gastos.csv"

# --- FUNCIONES DE DATOS ---
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

# --- MOTOR DE TEXTO ---
PALABRAS_FILTRO = ["mastercard", "visa", "tarjeta", "total", "iva", "base imponible", "subtotal", "efectivo", "cambio", "cif", "telefono", "atendido", "ticket", "factura", "mercadona", "importe", "pago"]

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
    # Menú Lateral
    with st.sidebar:
        st.header("👤 Tu Perfil")
        nombre_guia = st.text_input("Asistente", value="Ana")
        genero_guia = st.selectbox("Voz", ["Femenino", "Masculino"])
        modo_control = st.toggle("🛡️ Modo Control", value=False)
        st.divider()
        st.write("Configura tu experiencia para reducir el estrés financiero.")

    df_total = cargar_datos()
    total_acumulado = df_total['Precio'].sum() if not df_total.empty else 0.0

    # Cabecera Emocional
    adj = "lista" if genero_guia == "Femenino" else "listo"
    with st.container():
        col_avatar, col_text = st.columns([1, 5])
        with col_avatar:
            st.write("# 🧘")
        with col_text:
            msg = f"Hola, soy **{nombre_guia}**. Estoy {adj} para **cuidar de ti y de tu dinero**."
            if modo_control:
                st.info(f"{msg}\n\n🛡️ **Modo Control:** Tenemos **{total_acumulado:.2f}€** bajo vigilancia total. Relájate, yo guardo los detalles.")
            else:
                st.success(f"{msg}\n\n🌟 Llevamos un registro de **{total_acumulado:.2f}€**.")

    # Pestañas con Iconos y mejor diseño
    tab1, tab2, tab3 = st.tabs(["📥 **Subir Tickets**", "📊 **Análisis**", "📋 **Historial**"])

    with tab1:
        st.markdown(f"### 📥 Registro Múltiple")
        archivos = st.file_uploader("Puedes arrastrar varios PDFs o Fotos a la vez", type=['pdf', 'jpg', 'png', 'jpeg'], accept_multiple_files=True)
        if archivos:
            if st.button(f"🚀 Procesar {len(archivos)} archivos de golpe"):
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
                    st.toast("¡Datos guardados con éxito!", icon='✅')
                    st.rerun()

    with tab2:
        if not df_total.empty:
            st.markdown("### 📊 ¿En qué estamos invirtiendo?")
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(px.pie(df_total, values='Precio', names='Categoría', hole=0.5, height=350, 
                                     color_discrete_sequence=px.colors.qualitative.Pastel), use_container_width=True)
            with c2:
                df_fecha = df_total.groupby('Fecha')['Precio'].sum().reset_index()
                st.plotly_chart(px.line(df_fecha, x='Fecha', y='Precio', title="Ritmo de gasto", height=350), use_container_width=True)
        else:
            st.info("Aún no hay datos para analizar.")

    with tab3:
        st.markdown("### 📋 Mi Diario de Gastos")
        st.dataframe(df_total, use_container_width=True)
        if st.button("🗑️ Limpiar Historial"):
            if os.path.exists(ARCHIVO_DATOS): os.remove(ARCHIVO_DATOS); st.rerun()

if __name__ == "__main__":
    main()
