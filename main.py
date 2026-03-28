import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
import re

# Configuración avanzada
st.set_page_config(page_title="PocketAdmin Pro - Inteligencia Financiera", layout="wide")

# --- DICCIONARIO INTELIGENTE (El cerebro que clasifica ítems) ---
CATEGORIAS_PRODUCTOS = {
    "Saludable": ["manzana", "pera", "verdura", "pollo", "pescado", "agua", "leche"],
    "Caprichos/Fugas": ["chuches", "gominolas", "patatas", "refresco", "coca", "cerveza", "alcohol", "chocolate", "bolleria"],
    "Higiene/Cosmética": ["champu", "gel", "crema", "desodorante", "jabon", "pasta dent"]
}

def analizar_lineas_ticket(texto_bruto):
    """Analiza línea por línea el ticket para separar productos y precios"""
    lineas = texto_bruto.split('\n')
    productos_detectados = []
    
    for linea in lineas:
        # Buscamos algo que parezca un precio (ej: 2.50 o 2,50)
        precio_match = re.search(r'(\d+[\.,]\d{2})', linea)
        if precio_match:
            precio = float(precio_match.group(1).replace(',', '.'))
            # El resto de la línea suele ser el nombre del producto
            nombre = linea.replace(precio_match.group(1), "").strip()
            
            if len(nombre) > 3: # Evitamos ruidos cortos
                # Clasificación automática por palabras clave
                categoria = "Otros"
                nombre_min = nombre.lower()
                for cat, palabras in CATEGORIAS_PRODUCTOS.items():
                    if any(p in nombre_min for p in palabras):
                        categoria = cat
                        break
                
                productos_detectados.append([nombre, categoria, precio])
    
    return productos_detectados

# --- INTERFAZ ---
def main():
    st.title("🏦 PocketAdmin: Analizador de Ticket Detallado")
    
    if 'base_datos' not in st.session_state:
        st.session_state.base_datos = pd.DataFrame(columns=['Producto', 'Categoría', 'Precio'])

    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("📸 Escanear Compra")
        archivo = st.file_uploader("Sube el ticket del súper", type=['jpg', 'png', 'jpeg'])
        
        if archivo:
            img = Image.open(archivo)
            st.image(img, width=300)
            
            if st.button("🔍 Desglosar Productos"):
                texto = pytesseract.image_to_string(img)
                items = analizar_lineas_ticket(texto)
                
                if items:
                    nuevo_df = pd.DataFrame(items, columns=['Producto', 'Categoría', 'Precio'])
                    st.session_state.base_datos = pd.concat([st.session_state.base_datos, nuevo_df], ignore_index=True)
                    st.success(f"He detectado {len(items)} productos individuales.")
                else:
                    st.error("No he podido leer los precios. Intenta con una foto más nítida.")

    with col2:
        st.header("📊 Análisis de Gastos Reales")
        if not st.session_state.base_datos.empty:
            df = st.session_state.base_datos
            
            # Gráfico de gastos por categoría
            resumen = df.groupby('Categoría')['Precio'].sum().reset_index()
            st.bar_chart(resumen.set_index('Categoría'))
            
            # Alerta de Fugas
            fugas = df[df['Categoría'] == "Caprichos/Fugas"]['Precio'].sum()
            if fugas > 0:
                st.warning(f"⚠️ **Fuga detectada:** Te has gastado {fugas:.2f}€ en productos no esenciales (caprichos).")
            
            st.write("### Desglose completo:")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Sube un ticket para ver el desglose por productos.")

if __name__ == "__main__":
    main()
