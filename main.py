import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
import re
from pypdf import PdfReader
import os
import plotly.express as px

# Configuración con icono de "Brote" (Crecimiento)
st.set_page_config(page_title="Mi Guía de Bienestar", layout="wide", page_icon="🌱")

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

# --- MOTOR DE ACOMPAÑAMIENTO ---
def obtener_mensaje(df, nombre, genero, modo_control):
    adj = "tu guía" if genero == "Femenino" else "tu compañero"
    total = df['Precio'].sum() if not df.empty else 0
    
    # FRASE CENTRAL EMOCIONAL
    frase_base = f"Hola, soy **{nombre}**, {adj}. Estoy aquí para cuidar de ti y que caminemos juntos hacia tu tranquilidad."
    
    if modo_control:
        return f"⚓ **Ancla de Calma**: {frase_base}\n\nEn este momento de control, tenemos **{total:.2f}€** registrados. No tienes que cargar con estos números en tu cabeza, yo los guardo por ti. Todo está en orden."
    else:
        return f"🌱 **Creciendo juntos**: {frase_base}\n\nHemos registrado **{total:.2f}€** de tus pasos este mes. Cada decisión que tomas es una semilla para tu bienestar futuro."

# --- PROCESADOR LIMPIO ---
CATEGORIAS = {
    "Bienestar (Esencial)": ["manzana", "pera", "verdura", "pollo", "pescado", "agua", "leche", "huevos", "pan", "luz", "gasolina", "alquiler"],
    "Momentos (Caprichos)": ["chuches", "refresco", "coca", "cerveza", "vino", "chocolate", "bolleria", "pizza", "netflix"]
}

PALABRAS_FILTRO = ["mastercard", "visa", "tarjeta", "total", "iva", "base imponible", "subtotal", "efectivo", "cif", "atendido", "factura"]

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
                cat = "Otros"
                for c, palabras in CATEGORIAS.items():
                    if any(p in nombre.lower() for p in palabras): cat = c; break
                datos.append([fecha_hoy, nombre.capitalize(), cat, precio])
    return datos

# --- INTERFAZ ---
def main():
    # Menú Lateral - Personalidad bloqueada en la mente de la app
    st.sidebar.markdown("### ✨ Tu Guía Personal")
    nombre_guia = st.sidebar.text_input("¿Quién te acompaña hoy?", value="Ana")
    genero_guia = st.sidebar.selectbox("¿Cómo prefieres que te hable?", ["Femenino", "Masculino"])
    modo_control = st.sidebar.toggle("⚓ Modo Calma (Hiper-foco)", value=False)
    
    df_total = cargar_datos()
    
    # Encabezado Humano
    st.markdown(f"## {nombre_guia} & Tu Bienestar")
    with st.chat_message("assistant", avatar="🌱"):
        st.write(obtener_mensaje(df_total, nombre_guia, genero_guia, modo_control))

    # Pestañas con nombres humanos
    tab1, tab2, tab3 = st.tabs(["📥 Liberar mi Mente", "📉 Mi Camino Visual", "📖 Mi Diario de Paz"])

    with tab1:
        st.write("### Vuelca aquí tus registros para soltar la carga mental")
        archivos = st.file_uploader("Puedes subir varios a la vez (PDF/Fotos)", 
                                   type=['pdf', 'jpg', 'png', 'jpeg'], 
                                   accept_multiple_files=True)
        
        if archivos:
            if st.button(f"✨ {nombre_guia}, guarda esto por mí"):
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
                    st.success("Registros guardados. Tu mente ya puede descansar de estos datos.")
                    st.rerun()

    with tab2:
        if not df_total.empty:
            st.write("### Cómo florecen tus finanzas")
            fig_pie = px.pie(df_total, values='Precio', names='Categoría', hole=0.6, 
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Aún no hemos empezado a dibujar tu camino. Sube un registro cuando quieras.")

    with tab3:
        st.write("### Tu diario de pasos dados")
        st.dataframe(df_total, use_container_width=True)
        if st.button("🗑️ Limpiar Diario"):
            if os.path.exists(ARCHIVO_DATOS): os.remove(ARCHIVO_DATOS); st.rerun()

if __name__ == "__main__":
    main()
