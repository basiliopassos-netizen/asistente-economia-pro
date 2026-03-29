import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
import re
from pypdf import PdfReader
import os
import plotly.express as px

# Configuración con un toque más cálido
st.set_page_config(page_title="PocketAdmin: Bienestar Financiero", layout="wide", page_icon="🧘")

ARCHIVO_DATOS = "mis_gastos.csv"

# --- FUNCIONES DE MEMORIA ---
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

# --- MOTOR EMOCIONAL PERSONALIZADO ---
def obtener_consejo_emocional(df, nombre_asistente, genero):
    # Ajuste de género
    bienvenida = "listo" if genero == "Masculino" else "lista" if genero == "Femenino" else "preparado"
    
    if df.empty:
        return f"👋 ¡Hola! Soy **{nombre_asistente}**. Estoy {bienvenida} para ayudarte a **cuidar de ti y de tu dinero**. Sube tu primer ticket y empezamos este viaje juntos."
    
    hoy = pd.Timestamp.now()
    dia_mes = hoy.day
    caprichos = df[df['Categoría'] == "Caprichos/Fugas"]['Precio'].sum()
    
    # Mensaje basado en el momento del mes
    if dia_mes <= 7:
        mensaje = f"🌟 **Fuerza inicial:** Soy {nombre_asistente}. Estamos a principios de mes. Es el mejor momento para cuidar de ti evitando gastos impulsivos. ¡Llevas {caprichos:.2f}€ en caprichos, mantén el foco!"
    elif dia_mes >= 20:
        mensaje = f"🧗 **Ánimo en la recta final:** Soy {nombre_asistente}. Queda poco para terminar el mes. Cuidar de tu dinero hoy es darte tranquilidad para mañana. ¡Respira, lo estás haciendo bien!"
    else:
        mensaje = f"⚖️ **Punto de equilibrio:** Soy {nombre_asistente}. Vamos a mitad de camino. Revisa tus compras de hoy, ¿te hacen sentir bien o son solo un impulso?"
        
    return mensaje

# --- PROCESADOR DE TEXTO ---
CATEGORIAS = {
    "Saludable": ["manzana", "pera", "verdura", "pollo", "pescado", "agua", "leche", "avena", "huevos", "legumbre", "fruta"],
    "Caprichos/Fugas": ["chuches", "gominolas", "refresco", "coca", "cerveza", "vino", "alcohol", "chocolate", "bolleria", "donuts", "pizza", "patatas"],
    "Higiene/Hogar": ["detergente", "champu", "gel", "crema", "desodorante", "jabon", "limpiador"]
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
    # --- CONFIGURACIÓN DE PERSONALIDAD EN EL LATERAL ---
    st.sidebar.header("⚙️ Personalización")
    nombre_asistente = st.sidebar.text_input("¿Cómo quieres que me llame?", value="Ana")
    genero_asistente = st.sidebar.selectbox("Género del asistente", ["Femenino", "Masculino", "Neutro"])
    
    df_total = cargar_datos()
    
    st.title("🧘 PocketAdmin: Cuidando de ti")
    
    # EL MENSAJE HUMANO
    with st.chat_message("assistant"):
        st.write(obtener_consejo_emocional(df_total, nombre_asistente, genero_asistente))

    tab1, tab2, tab3 = st.tabs(["📸 Escáner de Bienestar", "📊 Mapa de Gastos", "📜 Diario Personal"])

    with tab1:
        st.write("### Sube tus tickets para que yo los analice por ti")
        archivo = st.file_uploader("Arrastra aquí tu PDF o Foto", type=['pdf', 'jpg', 'png', 'jpeg'])
        if archivo:
            if st.button(f"🚀 {nombre_asistente}, analiza mi compra"):
                texto = ""
                if archivo.type == "application/pdf":
                    reader = PdfReader(archivo)
                    for page in reader.pages: texto += page.extract_text()
                else:
                    texto = pytesseract.image_to_string(Image.open(archivo))
                
                nuevos_datos = analizar_texto(texto)
                if not nuevos_datos.empty:
                    df_total = guardar_datos(nuevos_datos)
                    st.success(f"¡Hecho! He guardado los datos para cuidar de tu economía.")
                    st.rerun()

    with tab2:
        if not df_total.empty:
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(px.pie(df_total, values='Precio', names='Categoría', hole=.4, 
                                     title="Distribución de tus prioridades",
                                     color_discrete_sequence=px.colors.qualitative.Pastel), use_container_width=True)
            with c2:
                df_fecha = df_total.groupby('Fecha')['Precio'].sum().reset_index()
                st.plotly_chart(px.line(df_fecha, x='Fecha', y='Precio', title="Tu ritmo emocional de gasto"), use_container_width=True)
        else:
            st.info("Cuando subas tu primer ticket, aquí verás cómo evoluciona tu bienestar.")

    with tab3:
        st.write("### Tu historial completo")
        st.dataframe(df_total, use_container_width=True)
        if st.button("🗑️ Resetear Diario"):
            if os.path.exists(ARCHIVO_DATOS): os.remove(ARCHIVO_DATOS); st.rerun()

if __name__ == "__main__":
    main()
