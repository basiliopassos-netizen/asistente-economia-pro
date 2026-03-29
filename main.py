import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
import re
from pypdf import PdfReader
import os
import plotly.express as px # Para gráficas más bonitas

st.set_page_config(page_title="PocketAdmin Pro", layout="wide", page_icon="📈")

# --- BASE DE DATOS LOCAL ---
ARCHIVO_DATOS = "mis_gastos.csv"

def cargar_datos_historicos():
    if os.path.exists(ARCHIVO_DATOS):
        df = pd.read_csv(ARCHIVO_DATOS)
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        return df
    return pd.DataFrame(columns=['Fecha', 'Producto', 'Categoría', 'Precio'])

def guardar_nuevo_ticket(df_nuevo):
    df_historial = cargar_datos_historicos()
    # Unimos lo viejo con lo nuevo
    df_actualizado = pd.concat([df_historial, df_nuevo], ignore_index=True)
    df_actualizado.to_csv(ARCHIVO_DATOS, index=False)
    return df_actualizado

# --- MOTOR DE INTELIGENCIA ---
CATEGORIAS = {
    "Alimentación": ["manzana", "pera", "pollo", "pescado", "leche", "huevos", "pan", "arroz", "pasta", "yogur"],
    "Fugas/Caprichos": ["chuches", "bolleria", "coca", "refresco", "cerveza", "vino", "patatas", "chocolate", "donuts"],
    "Limpieza/Higiene": ["detergente", "champu", "jabon", "papel", "suavizante", "crema"],
    "Hogar/Otros": ["pila", "bombilla", "plato", "vaso"]
}

def procesar_texto_a_tabla(texto):
    lineas = texto.split('\n')
    datos = []
    fecha_hoy = pd.Timestamp.now().date()
    
    for linea in lineas:
        # Busca precios (ej: 1,50 o 1.50)
        match = re.search(r'(\d+[\.,]\d{2})', linea)
        if match:
            precio = float(match.group(1).replace(',', '.'))
            nombre = linea.replace(match.group(1), "").strip().lower()
            
            if len(nombre) > 2:
                cat_detectada = "Otros"
                for cat, palabras in CATEGORIAS.items():
                    if any(p in nombre for p in palabras):
                        cat_detectada = cat
                        break
                datos.append([fecha_hoy, nombre.capitalize(), cat_detectada, precio])
    return pd.DataFrame(datos, columns=['Fecha', 'Producto', 'Categoría', 'Precio'])

# --- INTERFAZ ---
def main():
    st.title("💰 PocketAdmin: Tu Historial de Gastos")
    
    # Menú lateral para ver el total rápido
    df_total = cargar_datos_historicos()
    gasto_acumulado = df_total['Precio'].sum() if not df_total.empty else 0.0
    st.sidebar.metric("Gasto Total Acumulado", f"{gasto_acumulado:.2f} €")
    
    tab1, tab2, tab3 = st.tabs(["📥 Subir Ticket", "📊 Análisis de Fugas", "📋 Lista Completa"])

    with tab1:
        st.header("Añadir nueva compra")
        archivo = st.file_uploader("Arrastra tu PDF de Mercadona o Foto", type=['pdf', 'jpg', 'jpeg', 'png'])
        
        if archivo:
            if st.button("🚀 Analizar y Sumar al Historial"):
                texto = ""
                if archivo.type == "application/pdf":
                    reader = PdfReader(archivo)
                    for page in reader.pages: texto += page.extract_text()
                else:
                    texto = pytesseract.image_to_string(Image.open(archivo))
                
                nuevos_datos = procesar_texto_a_tabla(texto)
                
                if not nuevos_datos.empty:
                    df_total = guardar_nuevo_ticket(nuevos_datos)
                    st.success(f"¡Hecho! He sumado {len(nuevos_datos)} productos a tu cuenta.")
                    st.rerun() # Refresca para actualizar gráficas
                else:
                    st.error("No se han detectado productos claros en este archivo.")

    with tab2:
        if not df_total.empty:
            st.header("¿Dónde se va tu dinero?")
            
            # Gráfica Circular Pro
            fig = px.pie(df_total, values='Precio', names='Categoría', hole=.3, 
                         title="Distribución por Categorías")
            st.plotly_chart(fig, use_container_width=True)
            
            # Alerta de Fugas
            caprichos = df_total[df_total['Categoría'] == "Fugas/Caprichos"]['Precio'].sum()
            st.metric("Gasto en Caprichos", f"{caprichos:.2f} €", delta="-¡Cuidado!", delta_color="inverse")
        else:
            st.info("Sube tu primer ticket para ver el análisis.")

    with tab3:
        st.header("Historial de todos tus productos")
        st.dataframe(df_total, use_container_width=True)
        
        if st.button("🗑️ Resetear Aplicación (Borrar todo)"):
            if os.path.exists(ARCHIVO_DATOS):
                os.remove(ARCHIVO_DATOS)
                st.rerun()

if __name__ == "__main__":
    main()
