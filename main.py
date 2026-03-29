import streamlit as st
import pandas as pd
import google.generativeai as genai
from PIL import Image
import random
from datetime import datetime

# --- 1. CONFIGURACIÓN ---
API_KEY = "TU_API_KEY_AQUI" # <--- ¡PON TU LLAVE AQUÍ!

if API_KEY != "TU_API_KEY_AQUI":
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    IA_LISTA = True
else:
    IA_LISTA = False

# --- 2. MEMORIA ---
if 'diario' not in st.session_state:
    st.session_state.diario = []

# --- 3. DIBUJAR JARDÍN ---
def dibujar_jardin(datos):
    st.markdown("""<style>.canvas { background: linear-gradient(180deg, #87CEEB 0%, #B2EBF2 50%, #7CFC00 50%, #228B22 100%); border-radius: 20px; padding: 15px; }</style>""", unsafe_allow_html=True)
    svg = '<div class="canvas"><svg width="100%" height="450" viewBox="0 0 800 450">'
    # Paisaje y Árbol
    svg += '<circle cx="720" cy="60" r="30" fill="#FFD700"><animate attributeName="r" values="28;32;28" dur="3s" repeatCount="indefinite"/></circle>'
    svg += '<rect x="392" y="240" width="16" height="120" fill="#5D4037" />'
    svg += '<circle cx="400" cy="190" r="130" fill="#2E7D32" opacity="0.9" />'
    # Pareja Yoga
    svg += '<g transform="translate(250, 360) scale(0.7)"><circle cx="0" cy="0" r="10" fill="#FFCCBC"/><path d="M0 10 L-15 40 M0 10 L15 40" stroke="#E91E63" stroke-width="5" fill="none"/></g>'
    svg += '<g transform="translate(550, 360) scale(0.7)"><circle cx="0" cy="0" r="10" fill="#FFCCBC"/><path d="M0 10 L-15 40 M0 10 L15 40" stroke="#2196F3" stroke-width="5" fill="none"/></g>'
    # Frutos reales del ticket
    for i, g in enumerate(datos):
        random.seed(i)
        cx, cy = random.randint(320, 480), random.randint(110, 270)
        r = min(max(float(g['Precio']) * 1.8, 10), 32)
        svg += f'<g cursor="help"><title>{g["Producto"]}: {g["Precio"]}€</title><circle cx="{cx}" cy="{cy}" r="{r}" fill="#FF4444" stroke="white"/><text x="{cx}" y="{cy+4}" text-anchor="middle" fill="white" font-size="7" font-weight="bold">{g["Producto"][:4]}</text></g>'
    svg += "</svg></div>"
    st.markdown(svg, unsafe_allow_html=True)

# --- 4. FUNCIÓN LECTORA ---
def leer_ticket(archivo):
    img = Image.open(archivo)
    # Le damos instrucciones precisas a Laura
    prompt = "Analiza el ticket. Extrae productos y precios. Responde solo: Producto - Precio. Ejemplo: Leche - 1.20"
    res = model.generate_content([prompt, img])
    items = []
    for l in res.text.strip().split('\n'):
        if "-" in l:
            p = l.split("-")
            try:
                precio = float(''.join(c for c in p[1] if c.isdigit() or c in '.,').replace(',', '.'))
                items.append({"Fecha": datetime.now().strftime("%d/%m/%Y"), "Producto": p[0].strip(), "Precio": precio})
            except: continue
    return items

# --- INTERFAZ ---
st.markdown("<h1 style='text-align: center; color: #2e7d32;'>🌸 Laura: Tu Jardín Financiero</h1>", unsafe_allow_html=True)

if not IA_LISTA:
    st.warning("⚠️ Pega tu API KEY en la línea 10 del código para activar a Laura.")
    st.info("Consíguela aquí: [Google AI Studio](https://aistudio.google.com/app/apikey)")
else:
    t1, t2, t3 = st.tabs(["📤 Subir Tickets", "🌳 Ver Árbol", "📜 Diario"])
    with t1:
        fotos = st.file_uploader("Sube fotos de tus tickets", type=['jpg','png','jpeg'], accept_multiple_files=True)
        if fotos and st.button("✨ Laura, lee mis tickets"):
            for f in fotos:
                with st.spinner(f"Leyendo {f.name}..."):
                    st.session_state.diario.extend(leer_ticket(f))
            st.success("¡Tickets procesados!")
    with t2:
        if st.session_state.diario:
            dibujar_jardin(st.session_state.diario)
            st.metric("Total Gastado", f"{sum(i['Precio'] for i in st.session_state.diario):.2f}€")
    with t3:
        if st.session_state.diario:
            st.table(pd.DataFrame(st.session_state.diario))
    
