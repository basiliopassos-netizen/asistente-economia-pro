import streamlit as st
import pandas as pd
from PIL import Image

# 1. Configuración de la Identidad de la App
st.set_page_config(page_title="PocketAdmin - Economía Doméstica", layout="centered")

def main():
    st.title("📱 PocketAdmin Pro")
    st.markdown("### Control de Microeconomía Inteligente")
    
    # --- BARRA LATERAL: ENTRADA DE DATOS ---
    st.sidebar.header("Panel de Control")
    tipo_entrada = st.sidebar.selectbox(
        "¿Qué deseas registrar hoy?",
        ["Subir Ticket (Foto)", "Cargar Extracto (PDF/Excel)", "Ver Análisis de Fugas"]
    )

    archivo = st.sidebar.file_uploader("Arrastra tu archivo aquí", type=['png', 'jpg', 'jpeg', 'pdf', 'xlsx'])

    # --- CUERPO PRINCIPAL ---
    if archivo:
        if tipo_entrada == "Subir Ticket (Foto)":
            procesar_ticket(archivo)
        elif tipo_entrada == "Cargar Extracto (PDF/Excel)":
            procesar_documento(archivo)
    else:
        st.info("👋 Bienvenido. Por favor, sube un archivo en el panel lateral para comenzar el análisis.")

# 2. Función para procesar Fotos (Tickets)
def procesar_ticket(imagen_subida):
    imagen = Image.open(imagen_subida)
    st.image(imagen, caption="Ticket detectado", use_container_width=True)
    st.warning("🔍 Analizando productos e importes del ticket...")
    # Aquí insertaremos el código de OCR en el siguiente paso
    
# 3. Función para procesar Documentos (Bancos)
def procesar_documento(doc_subido):
    st.success("📄 Documento recibido correctamente.")
    # Aquí insertaremos la lógica de lectura de tablas
    st.write("Analizando variaciones de saldo y gastos fijos...")

if __name__ == "__main__":
    main()
