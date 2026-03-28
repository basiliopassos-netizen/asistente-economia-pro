import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
import re
from pypdf import PdfReader # Nueva herramienta para PDFs

st.set_page_config(page_title="PocketAdmin Pro - Multi-formato", layout="wide")

# Diccionario de categorías (puedes añadir más palabras aquí)
CATEGORIAS_PRODUCTOS = {
    "Saludable": ["manzana", "pera", "verdura", "pollo", "pescado", "agua", "leche", "avena", "yogur"],
    "Caprichos/Fugas": ["chuches", "gominolas", "patatas", "refresco", "coca", "cerveza", "vino", "alcohol", "chocolate", "bolleria", "donuts"],
    "Higiene/Cosmética": ["champu", "gel", "crema", "desodorante", "jabon", "pasta dent", "colonia"]
}

def analizar_texto(texto_bruto):
    lineas = texto_bruto.split('\n')
    productos_detectados = []
    for linea in lineas:
        precio_match = re.search(r'(\d+[\.,]\d{2})', linea)
        if precio_match:
            precio = float(precio_match.group(1).replace(',', '.'))
            nombre = linea.replace(precio_match.group(1), "").strip()
            if len(nombre) > 3:
                categoria = "Otros"
                nombre_min = nombre.lower()
                for cat, palabras in CATEGORIAS_PRODUCTOS.items():
                    if any(p in nombre_min for p in palabras):
                        categoria = cat
                        break
                productos_detectados.append([nombre, categoria, precio])
    return productos_detectados

def main():
    st.title("🏦 PocketAdmin: Analizador Multi-ticket")
    st.subheader("Sube fotos de tickets físicos o PDFs de tickets digitales")
    
    if 'base_datos' not in st.session_state:
        st.session_state.base_datos = pd.DataFrame(columns=['Producto', 'Categoría', 'Precio'])

    # CAMBIO AQUÍ: Ahora aceptamos PDF también
    archivo = st.file_uploader("Sube tu ticket (JPG, PNG o PDF)", type=['jpg', 'png', 'jpeg', 'pdf'])
    
    if archivo:
        texto_extraido = ""
        
        # Lógica si es PDF
        if archivo.type == "application/pdf":
            st.info("📄 PDF detectado. Extrayendo datos digitales...")
            reader = PdfReader(archivo)
            for page in reader.pages:
                texto_extraido += page.extract_text()
        
        # Lógica si es Imagen
        else:
            st.info("📸 Imagen detectada. Usando escáner OCR...")
            img = Image.open(archivo)
            st.image(img, width=250)
            texto_extraido = pytesseract.image_to_string(img)

        if st.button("🚀 Analizar Compra"):
            items = analizar_texto(texto_extraido)
            if items:
                nuevo_df = pd.DataFrame(items, columns=['Producto', 'Categoría', 'Precio'])
                st.session_state.base_datos = pd.concat([st.session_state.base_datos, nuevo_df], ignore_index=True)
                st.balloons()
            else:
                st.error("No he podido encontrar productos. Asegúrate de que el archivo sea legible.")

    # Mostrar resultados
    if not st.session_state.base_datos.empty:
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.write("### Desglose de productos")
            st.dataframe(st.session_state.base_datos, use_container_width=True)
        with c2:
            st.write("### Fugas y Gastos por Categoría")
            resumen = st.session_state.base_datos.groupby('Categoría')['Precio'].sum().reset_index()
            st.bar_chart(resumen.set_index('Categoría'))

if __name__ == "__main__":
    main()
