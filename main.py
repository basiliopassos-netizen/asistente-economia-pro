import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
import re
from pypdf import PdfReader
import os
import plotly.express as px

st.set_page_config(page_title="PocketAdmin: Control y Calma", layout="wide", page_icon="🛡️")

ARCHIVO_DATOS = "mis_gastos.csv"

# --- LÓGICA DE DATOS ---
def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        df = pd.read_csv(ARCHIVO_DATOS)
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        return df
    return pd.DataFrame(columns=['Fecha', 'Producto', 'Categoría', 'Precio'])

def guardar_datos(df_nuevo):
    df_historial = cargar_datos()
    df_actualizado = pd.concat([df_historial, df_nuevo], ignore_index=True)
    df_actualizado.to_csv(ARCHIVO_DATOS, index=False)
    return df_actualizado

# --- MOTOR DE APOYO EMOCIONAL (HIPER FOCO) ---
def obtener_mensaje_apoyo(df, nombre, modo_ansiedad):
    total = df['Precio'].sum() if not df.empty else 0
    
    if modo_ansiedad:
        # Mensajes diseñados para bajar las pulsaciones y dar control
        return f"""
        🛡️ **Modo Control Activado**: Hola {nombre}, respira. Tener hiper foco en tus gastos hoy es tu **superpoder**, no tu enemigo. 
        Estamos registrando todo con precisión. Llevamos **{total:.2f}€** bajo control absoluto. 
        No hay sorpresas, solo datos. Vamos paso a paso, ticket a ticket. Estás al mando.
        """
    else:
        return f"🌟 **Modo Optimista**: ¡Hola {nombre}! Llevamos un registro de {total:.2f}€. Cada ticket subido es una decisión consciente para tu futuro."

# --- PROCESADOR ---
CATEGORIAS = {
    "Esencial": ["agua", "leche", "huevos", "verdura", "pollo", "pan", "fruta", "arroz", "detergente", "jabon"],
    "Capricho/Impulso": ["coca", "refresco", "chuches", "vino", "cerveza", "chocolate", "bolleria", "pizza", "patatas"],
}

def analizar_texto(texto):
    lineas = texto.split('\n')
    datos = []
    fecha_hoy = pd.Timestamp.now().date()
    for linea in lineas:
        match = re.search(r'(\d+[\.,]\d{2})', linea)
        if match:
            precio = float(match.group(1).replace(',', '.'))
            nombre = linea.replace(match.group(1), "").strip().lower()
            if len(nombre) > 2:
                cat = "Otros"
                for c, palabras in CATEGORIAS.items():
                    if any(p in nombre for p in palabras): cat = c; break
                datos.append([fecha_hoy, nombre.capitalize(), cat, precio])
    return pd.DataFrame(datos, columns=['Fecha', 'Producto', 'Categoría', 'Precio'])

# --- INTERFAZ ---
def main():
    # Menú Lateral para el estado mental
    st.sidebar.header("🧠 Estado Mental")
    nombre_asistente = st.sidebar.text_input("Nombre de tu guía", value="Ana")
    modo_ansiedad = st.sidebar.toggle("Modo Control (Si sientes ansiedad)", value=False)
    
    df_total = cargar_datos()
    
    # El mensaje de la IA se adapta a tu estado mental
    st.chat_message("assistant").write(obtener_mensaje_apoyo(df_total, nombre_asistente, modo_ansiedad))

    tab1, tab2, tab3 = st.tabs(["📥 Registro de Control", "📈 Visualización de Calma", "📜 Mi Diario de Gastos"])

    with tab1:
        st.write("### Vuelca aquí tus gastos para sacarlos de tu cabeza")
        archivo = st.file_uploader("Sube tu ticket (PDF o Foto)", type=['pdf', 'jpg', 'png', 'jpeg'])
        if archivo:
            if st.button("🚀 Registrar para ganar control"):
                texto = ""
                if archivo.type == "application/pdf":
                    reader = PdfReader(archivo)
                    for page in reader.pages: texto += page.extract_text()
                else:
                    texto = pytesseract.image_to_string(Image.open(archivo))
                
                nuevos_datos = analizar_texto(texto)
                if not nuevos_datos.empty:
                    guardar_datos(nuevos_datos)
                    st.success("Dato registrado. Ya no tienes que recordarlo, yo lo guardo por ti.")
                    st.rerun()

    with tab2:
        if not df_total.empty:
            st.write("### Análisis de tu seguridad financiera")
            # Gráfico de líneas (Evolución)
            fig_evol = px.line(df_total.groupby('Fecha')['Precio'].sum().reset_index(), 
                               x='Fecha', y='Precio', title="Tu camino recorrido")
            st.plotly_chart(fig_evol, use_container_width=True)
            
            # Categorías
            fig_pie = px.pie(df_total, values='Precio', names='Categoría', hole=0.5, 
                             color_discrete_sequence=px.colors.sequential.Teal)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Cuando estés listo, registra tu primer movimiento.")

    with tab3:
        st.write("### Historial detallado")
        st.table(df_total) # Uso tabla simple para más claridad
        if st.button("🗑️ Resetear (Empezar de cero)"):
            if os.path.exists(ARCHIVO_DATOS): os.remove(ARCHIVO_DATOS); st.rerun()

if __name__ == "__main__":
    main()
