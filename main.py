import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
import re
from pypdf import PdfReader
import os
import plotly.express as px

st.set_page_config(page_title="PocketAdmin: Tu Vínculo", layout="wide", page_icon="🌱")

ARCHIVO_DATOS = "mis_gastos.csv"
ARCHIVO_IDENTIDAD = "identidad.txt"

# --- GESTIÓN DE IDENTIDAD FIJA ---
def obtener_identidad():
    if os.path.exists(ARCHIVO_IDENTIDAD):
        with open(ARCHIVO_IDENTIDAD, "r") as f:
            datos = f.read().split("|")
            return {"nombre": datos[0], "genero": datos[1]}
    return None

def guardar_identidad(nombre, genero):
    with open(ARCHIVO_IDENTIDAD, "w") as f:
        f.write(f"{nombre}|{genero}")

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

# --- INTERFAZ ---
def main():
    identidad = obtener_identidad()
    
    # 1. PANTALLA DE NACIMIENTO (Si no hay nombre)
    if identidad is None:
        st.title("🌱 El nacimiento de tu guía")
        st.write("Para empezar a cuidar de ti, necesito una identidad. Este nombre será para siempre, como un vínculo entre nosotros.")
        
        col1, col2 = st.columns(2)
        with col1:
            nuevo_nombre = st.text_input("¿Qué nombre me das?", placeholder="Ej: Ana, Lucas, Gaia...")
        with col2:
            nuevo_genero = st.selectbox("¿Cómo quieres que te hable?", ["Femenino", "Masculino"])
        
        if st.button("✨ Crear vínculo"):
            if nuevo_nombre:
                guardar_identidad(nuevo_nombre, nuevo_genero)
                st.success(f"Hola, ahora soy {nuevo_nombre}. Vamos a cuidar de ti.")
                st.rerun()
            else:
                st.warning("Por favor, dame un nombre para poder empezar.")
        return # Detiene la app aquí hasta que se asigne nombre

    # 2. APLICACIÓN PRINCIPAL (Si ya hay identidad)
    nombre_guia = identidad['nombre']
    genero_guia = identidad['genero']
    adj = "lista" if genero_guia == "Femenino" else "listo"
    
    st.sidebar.markdown(f"### ✨ Tu Guía: **{nombre_guia}**")
    modo_control = st.sidebar.toggle("⚓ Modo Calma", value=False)
    
    df_total = cargar_datos()
    total_acumulado = df_total['Precio'].sum() if not df_total.empty else 0
    
    # Mensaje emocional
    with st.chat_message("assistant", avatar="🌱"):
        mensaje = f"Hola, soy **{nombre_guia}**. Estoy {adj} para cuidar de ti y de tu dinero."
        if modo_control:
            st.write(f"⚓ {mensaje}\n\nLlevamos **{total_acumulado:.2f}€** bajo control absoluto. No te preocupes, yo guardo el peso de los datos por ti.")
        else:
            st.write(f"🌟 {mensaje}\n\nLlevamos **{total_acumulado:.2f}€** en nuestro camino compartido.")

    tab1, tab2, tab3 = st.tabs(["📥 Liberar mi Mente", "📉 Mi Camino Visual", "📖 Mi Diario de Paz"])

    with tab1:
        st.write(f"### Confía en {nombre_guia} para guardar tus registros")
        archivos = st.file_uploader("Sube tus PDFs o Fotos", accept_multiple_files=True)
        if archivos:
            if st.button(f"✨ Guardar con {nombre_guia}"):
                # (Aquí iría el código de análisis que ya tenemos...)
                st.info("Procesando... (Asegúrate de copiar también las funciones de análisis anteriores)")
                st.rerun()

    # Botón de reset (Única forma de cambiar nombre, pero borra TODO)
    if st.sidebar.button("⚠️ Resetear Vínculo"):
        if os.path.exists(ARCHIVO_IDENTIDAD): os.remove(ARCHIVO_IDENTIDAD)
        if os.path.exists(ARCHIVO_DATOS): os.remove(ARCHIVO_DATOS)
        st.rerun()

if __name__ == "__main__":
    main()
