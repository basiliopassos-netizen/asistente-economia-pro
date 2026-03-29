import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
import re
from pypdf import PdfReader
import os
import plotly.express as px

st.set_page_config(page_title="PocketAdmin: Economía con Corazón", layout="wide", page_icon="🧠")

ARCHIVO_DATOS = "mis_gastos.csv"

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

# --- MOTOR DE EMOCIONES Y CONSEJOS ---
def obtener_consejo_emocional(df):
    if df.empty:
        return "👋 ¡Hola! Estoy listo para ayudarte a cuidar tu dinero. Sube tu primer ticket y empezamos este viaje juntos."
    
    hoy = pd.Timestamp.now()
    dia_mes = hoy.day
    total_mes = df['Precio'].sum()
    caprichos = df[df['Categoría'] == "Fugas/Caprichos"]['Precio'].sum()
    
    # Lógica de mensajes emocionales
    if dia_mes <= 7:
        mensaje = f"🌟 **Mentalidad de Abundancia:** Acabas de empezar el mes. Es el momento donde nos sentimos ricos, pero recuerda: el 'tú' de final de mes te agradecerá que hoy cuides esos pequeños caprichos de {caprichos:.2f}€. ¡Tú puedes con esto!"
    elif dia_mes >= 20:
        mensaje = "🧗 **Recta Final:** Estamos llegando a fin de mes. Si sientes estrés, respira. Has hecho un gran trabajo registrando tus gastos. ¡Ya queda poco para el próximo ingreso!"
    else:
        mensaje = "⚖️ **Equilibrio:** Estás a mitad de camino. Revisa tu lista, ¿hay algo que te haga sentir orgulloso de tu ahorro hoy?"
        
    if caprichos > (total_mes * 0.2):
        mensaje += "\n\n⚠️ **Nota:** He notado que las emociones han guiado algunas compras de caprichos. ¡No te castigues! Solo intenta que mañana sea un día de 'gasto cero' en antojos."
    
    return mensaje

# --- PROCESADOR ---
CATEGORIAS = {
    "Saludable": ["manzana", "pera", "verdura", "pollo", "pescado", "agua", "leche", "avena", "huevos", "legumbres"],
    "Fugas/Caprichos": ["chuches", "gominolas", "refresco", "coca", "cerveza", "vino", "chocolate", "bolleria", "pizza", "hamburguesa"],
    "Higiene/Hogar": ["detergente", "champu", "gel", "papel", "limpiador", "suavizante"]
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
    df_total = cargar_datos()
    
    st.title("🧠 PocketAdmin: Economía e Impulsos")
    
    # SECCIÓN EMOCIONAL (Lo que tú querías)
    st.chat_message("assistant").write(obtener_consejo_emocional(df_total))

    tab1, tab2, tab3 = st.tabs(["📸 Escáner de Tickets", "📊 Tu Mapa de Gastos", "📜 Diario de Compras"])

    with tab1:
        archivo = st.file_uploader("Sube tu ticket de hoy", type=['pdf', 'jpg', 'png', 'jpeg'])
        if archivo:
            if st.button("🚀 Analizar mi compra"):
                texto = ""
                if archivo.type == "application/pdf":
                    reader = PdfReader(archivo)
                    for page in reader.pages: texto += page.extract_text()
                else:
                    texto = pytesseract.image_to_string(Image.open(archivo))
                
                nuevos_datos = analizar_texto(texto)
                if not nuevos_datos.empty:
                    df_total = guardar_datos(nuevos_datos)
                    st.success("Ticket guardado en tu historial.")
                    st.rerun()

    with tab2:
        if not df_total.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(px.pie(df_total, values='Precio', names='Categoría', hole=.4, title="Distribución"), use_container_width=True)
            with col2:
                # Evolución Temporal
                df_fecha = df_total.groupby('Fecha')['Precio'].sum().reset_index()
                st.plotly_chart(px.line(df_fecha, x='Fecha', y='Precio', title="Tu ritmo de gasto"), use_container_width=True)
        else:
            st.info("Sube algo para ver tu mapa mental de gastos.")

    with tab3:
        st.dataframe(df_total, use_container_width=True)
        if st.button("🗑️ Resetear (Empezar de cero)"):
            if os.path.exists(ARCHIVO_DATOS): os.remove(ARCHIVO_DATOS); st.rerun()

if __name__ == "__main__":
    main()
