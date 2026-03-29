import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
import re
from pypdf import PdfReader
import os
import plotly.express as px

st.set_page_config(page_title="PocketAdmin: Control Total", layout="wide", page_icon="🛡️")

ARCHIVO_DATOS = "mis_gastos.csv"

# --- LÓGICA DE DATOS ---
def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        df = pd.read_csv(ARCHIVO_DATOS)
        # Convertimos a fecha y luego a solo fecha (sin hora)
        df['Fecha'] = pd.to_datetime(df['Fecha']).dt.date
        return df
    return pd.DataFrame(columns=['Fecha', 'Producto', 'Categoría', 'Precio'])

def guardar_datos(df_nuevo):
    df_historial = cargar_datos()
    df_actualizado = pd.concat([df_historial, df_nuevo], ignore_index=True)
    # Guardamos como CSV manteniendo el formato
    df_actualizado.to_csv(ARCHIVO_DATOS, index=False)
    return df_actualizado

# --- MOTOR EMOCIONAL ---
def obtener_mensaje(df, nombre, genero, modo_control):
    adj = "lista" if genero == "Femenino" else "listo"
    total = df['Precio'].sum() if not df.empty else 0
    base = f"Hola, soy **{nombre}** y estoy {adj} para **cuidar de ti y de tu dinero**."
    
    if modo_control:
        return f"🛡️ {base}\n\n**Modo Control:** Todo bajo vigilancia. Llevamos **{total:.2f}€** registrados con precisión."
    else:
        return f"🌟 {base}\n\nLlevamos un registro acumulado de **{total:.2f}€**."

# --- PROCESADOR CON FILTRO ANTI-RUIDO ---
CATEGORIAS = {
    "Esencial": ["manzana", "pera", "verdura", "pollo", "pescado", "agua", "leche", "huevos", "pan", "arroz", "detergente", "luz", "alquiler", "gasolina"],
    "Capricho": ["chuches", "gominolas", "refresco", "coca", "cerveza", "vino", "chocolate", "bolleria", "pizza", "netflix", "hbo"]
}

# Palabras que queremos ignorar (Mastercard, IVA, etc.)
PALABRAS_FILTRO = ["mastercard", "visa", "tarjeta", "total", "iva", "base imponible", "subtotal", "efectivo", "cambio", "cif", "telefono", "atendido", "ticket", "factura"]

def analizar_texto(texto):
    lineas = texto.split('\n')
    datos = []
    # Fecha de hoy limpia (sin hora)
    fecha_hoy = pd.Timestamp.now().date()
    
    for linea in lineas:
        linea_min = linea.lower()
        
        # 1. ¿Contiene un precio?
        match = re.search(r'(\d+[\.,]\d{2})', linea)
        
        # 2. ¿Es una línea de "basura" (IVA, Tarjeta, etc)?
        es_basura = any(p in linea_min for p in PALABRAS_FILTRO)
        
        if match and not es_basura:
            precio = float(match.group(1).replace(',', '.'))
            nombre = linea.replace(match.group(1), "").strip()
            
            # Limpiar símbolos raros del nombre
            nombre = re.sub(r'[^a-zA-ZáéíóúÁÉÍÓÚñÑ ]', '', nombre).strip()
            
            if len(nombre) > 2:
                cat = "Otros"
                nombre_min = nombre.lower()
                for c, palabras in CATEGORIAS.items():
                    if any(p in nombre_min for p in palabras): cat = c; break
                datos.append([fecha_hoy, nombre.capitalize(), cat, precio])
    return datos

# --- INTERFAZ ---
def main():
    st.sidebar.header("⚙️ Personalización")
    nombre_guia = st.sidebar.text_input("Nombre de tu guía", value="Ana")
    genero_guia = st.sidebar.selectbox("Género", ["Femenino", "Masculino"])
    modo_control = st.sidebar.toggle("🆘 Modo Control (Ansiedad)", value=False)
    
    df_total = cargar_datos()
    st.chat_message("assistant").write(obtener_mensaje(df_total, nombre_guia, genero_guia, modo_control))

    tab1, tab2, tab3 = st.tabs(["📥 Registro Múltiple", "📊 Análisis", "📋 Historial"])

    with tab1:
        archivos = st.file_uploader("Sube uno o varios tickets (PDF/Fotos)", 
                                   type=['pdf', 'jpg', 'png', 'jpeg'], 
                                   accept_multiple_files=True)
        
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
                    
                    items = analizar_texto(texto)
                    todos_los_items.extend(items)
                
                if todos_los_items:
                    nuevos_df = pd.DataFrame(todos_los_items, columns=['Fecha', 'Producto', 'Categoría', 'Precio'])
                    guardar_datos(nuevos_df)
                    st.success("Tickets procesados y limpios.")
                    st.rerun()

    with tab2:
        if not df_total.empty:
            st.plotly_chart(px.pie(df_total, values='Precio', names='Categoría', hole=0.5, title="Tus Prioridades"), use_container_width=True)
        else:
            st.info("Sin datos para analizar.")

    with tab3:
        # Mostramos la tabla. Streamlit detecta que es fecha y la muestra limpia.
        st.dataframe(df_total, use_container_width=True)
        if st.button("🗑️ Borrar Todo"):
            if os.path.exists(ARCHIVO_DATOS): os.remove(ARCHIVO_DATOS); st.rerun()

if __name__ == "__main__":
    main()
