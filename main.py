import streamlit as st
import pandas as pd
import google.generativeai as genai
from PIL import Image
from datetime import datetime
import random

# --- 1. CONFIGURACIÓN DE LA IA (Aquí pones tu llave gratuita) ---
# Puedes conseguir una en: https://aistudio.google.com/
API_KEY = "TU_API_KEY_AQUI" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def presentacion_laura():
    st.markdown("""
        <div style="background-color: #f0f4f8; padding: 20px; border-radius: 15px; border-left: 5px solid #2e7d32; margin-bottom: 20px;">
            <h1 style="margin: 0; color: #1b5e20;">Hola, soy Laura 👩‍🌾</h1>
            <p style="font-size: 1.2em; color: #455a64;"><b>"Ahora uso mi inteligencia para leer tus tickets sin que tengas que instalar nada raro. ¡Pruébame!"</b></p>
        </div>
    """, unsafe_allow_html=True)

# --- GESTIÓN DE MEMORIA ---
if 'diario_detallado' not in st.session_state:
    st.session_state.diario_detallado = []

if st.sidebar.button("🗑️ Borrar todo"):
    st.session_state.diario_detallado = []
    st.rerun()

# --- 2. FUNCIÓN DE LECTURA CON IA ---
def leer_ticket_con_ia(archivo_imagen):
    img = Image.open(archivo_imagen)
    prompt = """
    Analiza esta imagen de un ticket de compra. 
    Extrae los productos y sus precios en un formato de lista simple.
    Si no ves productos, no inventes. 
    Responde solo con el formato: Producto - Precio
    """
    try:
        # La IA mira la foto y lee el texto
        respuesta = model.generate_content([prompt, img])
        lineas = respuesta.text.strip().split('\n')
        
        items = []
        for linea in lineas:
            if "-" in linea:
                partes = linea.split("-")
                nombre = partes[0].strip()
                try:
                    # Limpiamos el precio de símbolos de euro, etc.
                    precio = float(partes[1].replace('€', '').replace('$', '').strip().replace(',', '.'))
                except:
                    precio = 0.0
                
                items.append({
                    "Fecha": datetime.now().strftime("%d/%m/%Y"),
                    "Producto": nombre,
                    "Precio": precio,
                    "Categoría": "Supermercado" # Esto lo podemos mejorar luego
                })
        return items
    except Exception as e:
        st.error(f"Error con la IA: {e}")
        return []

# --- 3. DIBUJAR EL JARDÍN ---
def dibujar_jardin(items):
    st.markdown("""<style>.escena-jardin { background: linear-gradient(180deg, #87CEEB 0%, #B2EBF2 50%, #7CFC00 50%, #228B22 100%); border-radius: 20px; padding: 10px; }</style>""", unsafe_allow_html=True)
    svg = '<div class="escena-jardin"><svg width="100%" height="450" viewBox="0 0 800 450" xmlns="http://www.w3.org/2000/svg">'
    svg += '<circle cx="700" cy="60" r="30" fill="#FFD700"><animate attributeName="r" values="28;32;28" dur="3s" repeatCount="indefinite"/></circle>'
    svg += '<rect x="390" y="220" width="20" height="130" fill="#5D4037" />'
    svg += '<circle cx="400" cy="180" r="120" fill="#2E7D32" opacity="0.85" />'
    
    # Personajes haciendo yoga
    svg += '<g transform="translate(280, 360) scale(0.7)"><circle cx="0" cy="0" r="10" fill="#FFCCBC"/><path d="M0 10 L-15 40 M0 10 L15 40" stroke="#E91E63" stroke-width="5" fill="none"/></g>'
    svg += '<g transform="translate(520, 360) scale(0.7)"><circle cx="0" cy="0" r="10" fill="#FFCCBC"/><path d="M0 10 L-15 40 M0 10 L15 40" stroke="#2196F3" stroke-width="5" fill="none"/></g>'

    for i, item in enumerate(items):
        random.seed(i)
        cx, cy = random.randint(330, 470), random.randint(110, 250)
        r = min(max(float(item['Precio']) * 2, 10), 30)
        svg += f'<g cursor="pointer"><title>{item["Producto"]}: {item["Precio"]}€</title><circle cx="{cx}" cy="{cy}" r="{r}" fill="#FF4444" stroke="white"/><text x="{cx}" y="{cy+4}" text-anchor="middle" fill="white" font-size="7" font-weight="bold">{item["Producto"][:4]}</text></g>'
    
    svg += "</svg></div>"
    st.markdown(svg, unsafe_allow_html=True)

# --- MAIN ---
def main():
    presentacion_laura()
    t1, t2, t3 = st.tabs(["📤 Subir Tickets", "🌳 Mi Árbol", "📜 Diario"])

    with t1:
        st.subheader("Sube tus fotos reales")
        archivos = st.file_uploader("Fotos de tickets (JPG/PNG)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
        if archivos and st.button("✨ Laura, lee los tickets con IA"):
            for arc in archivos:
                with st.spinner(f"Laura está leyendo {arc.name}..."):
                    items = leer_ticket_con_ia(arc)
                    st.session_state.diario_detallado.extend(items)
            st.success("¡Lectura terminada!")

    with t2:
        if st.session_state.diario_detallado:
            dibujar_jardin(st.session_state.diario_detallado)
            total = sum(i['Precio'] for i in st.session_state.diario_detallado)
            st.metric("Gasto Total", f"{total:.2f} €")
        else:
            st.info("Sube un ticket para ver los frutos.")

    with t3:
        if st.session_state.diario_detallado:
            st.dataframe(pd.DataFrame(st.session_state.diario_detallado), use_container_width=True)

if __name__ == "__main__":
    main()
