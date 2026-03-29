import streamlit as st
import pandas as pd
import google.generativeai as genai
from PIL import Image
import random
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Laura: Tu Jardín Financiero", layout="wide")

# --- 1. CONFIGURACIÓN DE LA IA ---
# Consigue tu llave en: https://aistudio.google.com/app/apikey (Es gratis)
API_KEY = "TU_API_KEY_AQUI" 

if API_KEY != "TU_API_KEY_AQUI":
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    IA_LISTA = True
else:
    IA_LISTA = False

# --- 2. GESTIÓN DE MEMORIA ---
if 'diario_detallado' not in st.session_state:
    st.session_state.diario_detallado = []

if st.sidebar.button("🗑️ Resetear Jardín"):
    st.session_state.diario_detallado = []
    st.rerun()

# --- 3. FUNCIÓN DE DIBUJO (El Árbol con Yoga) ---
def dibujar_jardin(items):
    st.markdown("""<style>.escena-jardin { background: linear-gradient(180deg, #87CEEB 0%, #B2EBF2 50%, #7CFC00 50%, #228B22 100%); border-radius: 20px; padding: 20px; }</style>""", unsafe_allow_html=True)
    
    svg = '<div class="escena-jardin"><svg width="100%" height="450" viewBox="0 0 800 450">'
    # Sol y Paisaje
    svg += '<circle cx="700" cy="60" r="30" fill="#FFD700"><animate attributeName="r" values="28;32;28" dur="3s" repeatCount="indefinite"/></circle>'
    svg += '<rect x="390" y="240" width="20" height="110" fill="#5D4037" />'
    svg += '<circle cx="400" cy="190" r="130" fill="#2E7D32" opacity="0.9" />'
    
    # Personajes Yoga (Chica y Chico)
    svg += '<g transform="translate(280, 360) scale(0.7)"><circle cx="0" cy="0" r="10" fill="#FFCCBC"/><path d="M0 10 L-15 40 M0 10 L15 40" stroke="#E91E63" stroke-width="5" fill="none"/></g>'
    svg += '<g transform="translate(520, 360) scale(0.7)"><circle cx="0" cy="0" r="10" fill="#FFCCBC"/><path d="M0 10 L-15 40 M0 10 L15 40" stroke="#2196F3" stroke-width="5" fill="none"/></g>'

    # Frutos (Productos del ticket)
    for i, item in enumerate(items):
        random.seed(i)
        cx, cy = random.randint(320, 480), random.randint(110, 270)
        r = min(max(float(item['Precio']) * 1.5, 10), 30)
        svg += f'<g cursor="pointer"><title>{item["Producto"]}: {item["Precio"]}€</title><circle cx="{cx}" cy="{cy}" r="{r}" fill="#FF4444" stroke="white"/><text x="{cx}" y="{cy+4}" text-anchor="middle" fill="white" font-size="7" font-weight="bold">{item["Producto"][:4]}</text></g>'
    
    svg += "</svg></div>"
    st.markdown(svg, unsafe_allow_html=True)

# --- 4. FUNCIÓN PARA LEER EL TICKET DE VERDAD ---
def leer_ticket_real(archivo):
    img = Image.open(archivo)
    prompt = """
    Actúa como un experto contable. Analiza este ticket de compra y extrae:
    1. Nombre del producto (simplificado).
    2. Precio por unidad o total de esa línea.
    3. Categoría (Lácteos, Belleza, Bebidas, Limpieza, etc.)
    Responde SOLO con una tabla separada por guiones: Producto - Precio - Categoria
    """
    try:
        response = model.generate_content([prompt, img])
        lineas = response.text.strip().split('\n')
        nuevos_items = []
        for linea in lineas:
            if "-" in linea:
                partes = linea.split("-")
                if len(partes) >= 2:
                    nuevos_items.append({
                        "Fecha": datetime.now().strftime("%d/%m/%Y"),
                        "Producto": partes[0].strip(),
                        "Precio": float(partes[1].replace('€', '').replace(',', '.').strip()),
                        "Categoría": partes[2].strip() if len(partes) > 2 else "Varios"
                    })
        return nuevos_items
    except Exception as e:
        st.error(f"Laura no pudo leer este ticket: {e}")
        return []

# --- INTERFAZ PRINCIPAL ---
def main():
    st.markdown("<h1 style='text-align: center; color: #2e7d32;'>🌸 Laura: Tu Jardín Financiero</h1>", unsafe_allow_html=True)
    
    if not IA_LISTA:
        st.warning("⚠️ Laura necesita su 'cerebro'. Por favor, añade la API KEY en el código.")
        st.info("Consíguela gratis en [Google AI Studio](https://aistudio.google.com/app/apikey)")
        return

    tab1, tab2, tab3 = st.tabs(["📤 Subir Tickets", "🌳 Ver Árbol", "📜 Diario"])

    with tab1:
        archivos = st.file_uploader("Arrastra aquí tus fotos de tickets de Mercadona, etc.", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)
        if archivos and st.button("✨ Laura, lee mis tickets"):
            for arc in archivos:
                with st.spinner(f"Analizando {arc.name}..."):
                    items = leer_ticket_real(arc)
                    st.session_state.diario_detallado.extend(items)
            st.success("¡Tickets leídos con éxito!")

    with tab2:
        if st.session_state.diario_detallado:
            dibujar_jardin(st.session_state.diario_detallado)
            total = sum(float(i['Precio']) for i in st.session_state.diario_detallado)
            st.metric("Inversión en el Jardín", f"{total:.2f} €")
        else:
            st.info("El árbol florecerá cuando subas tu primer ticket.")

    with tab3:
        if st.session_state.diario_detallado:
            df = pd.DataFrame(st.session_state.diario_detallado)
            st.dataframe(df, use_container_width=True)
            # Gráfico de gastos por categoría
            st.bar_chart(df.groupby('Categoría')['Precio'].sum())

if __name__ == "__main__":
    main()
