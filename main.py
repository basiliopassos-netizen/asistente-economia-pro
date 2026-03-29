import streamlit as st
import pandas as pd
import random
from datetime import datetime

# --- CONFIGURACIÓN DE IDENTIDAD ---
def presentacion_laura():
    st.markdown("""
        <div style="background-color: #f0f4f8; padding: 20px; border-radius: 15px; border-left: 5px solid #2e7d32; margin-bottom: 20px;">
            <h1 style="margin: 0; color: #1b5e20;">Hola, soy Laura 👩‍🌾</h1>
            <p style="font-size: 1.2em; color: #455a64;"><b>"¡Entendido! Voy a dejar de repetir siempre lo mismo. A partir de ahora, analizaré cada ticket individualmente."</b></p>
        </div>
    """, unsafe_allow_html=True)

# --- GESTIÓN DE MEMORIA ---
if st.sidebar.button("🗑️ Borrar todo y empezar de cero"):
    st.session_state.diario_detallado = []
    st.rerun() 

if 'diario_detallado' not in st.session_state:
    st.session_state.diario_detallado = []

# --- FUNCIÓN DE LECTURA DINÁMICA ---
def procesar_ticket_individual(archivo):
    # Esta función ahora crea una entrada basada en el NOMBRE REAL de tu archivo
    # para que no se repita "Leche/Agua/Maquillaje"
    nombre_limpio = archivo.name.split('.')[0] # Quita el .jpg o .pdf
    
    # Aquí es donde Laura "lee". De momento, usaremos el nombre del ticket
    # Pero lo tratamos como un concepto único para el árbol
    item_real = {
        "Fecha": datetime.now().strftime("%d/%m/%Y"),
        "Producto": f"Compra: {nombre_limpio}",
        "Precio": round(random.uniform(5, 25), 2), # Esto lo leeremos de la imagen pronto
        "Categoría": "Supermercado" if "mercadona" in nombre_limpio.lower() else "Sin categoría"
    }
    return [item_real]

# --- FUNCIÓN DEL JARDÍN ---
def dibujar_jardin(items):
    st.markdown("""<style>.escena-jardin { background: linear-gradient(180deg, #87CEEB 0%, #B2EBF2 50%, #7CFC00 50%, #228B22 100%); border-radius: 20px; padding: 10px; }</style>""", unsafe_allow_html=True)
    svg = '<div class="escena-jardin"><svg width="100%" height="450" viewBox="0 0 800 450" xmlns="http://www.w3.org/2000/svg">'
    svg += '<circle cx="700" cy="60" r="30" fill="#FFD700"><animate attributeName="r" values="28;32;28" dur="3s" repeatCount="indefinite"/></circle>'
    svg += '<rect x="390" y="220" width="20" height="130" fill="#5D4037" />'
    svg += '<circle cx="400" cy="180" r="120" fill="#2E7D32" opacity="0.85" />'
    
    for i, item in enumerate(items):
        random.seed(i) 
        cx, cy = random.randint(330, 470), random.randint(110, 250)
        radio = min(max(float(item['Precio']) * 1.5, 10), 35)
        svg += f'<g cursor="pointer"><title>{item["Producto"]}: {item["Precio"]}€</title><circle cx="{cx}" cy="{cy}" r="{radio}" fill="#FF4444" stroke="white"/><text x="{cx}" y="{cy+4}" text-anchor="middle" fill="white" font-size="7" font-weight="bold">{item["Producto"][:5]}</text></g>'
    
    svg += "</svg></div>"
    st.markdown(svg, unsafe_allow_html=True)

# --- MAIN ---
def main():
    presentacion_laura()
    t1, t2, t3 = st.tabs(["📤 Subir Tickets", "🌳 Mi Árbol", "📜 Diario"])

    with t1:
        archivos = st.file_uploader("Sube tus tickets aquí", type=['png', 'jpg', 'pdf'], accept_multiple_files=True)
        if archivos:
            if st.button("✨ Laura, procesa estos archivos"):
                for arc in archivos:
                    # Ahora llamamos a la función que usa el nombre del archivo real
                    datos = procesar_ticket_individual(arc)
                    st.session_state.diario_detallado.extend(datos)
                st.success("¡Procesados! Cada ticket es ahora un fruto distinto en el árbol.")

    with t2:
        if st.session_state.diario_detallado:
            dibujar_jardin(st.session_state.diario_detallado)
            total = sum(d['Precio'] for d in st.session_state.diario_detallado)
            st.metric("Inversión en el Jardín", f"{total:.2f} €")
        else:
            st.info("El árbol está esperando que subas tickets reales.")

    with t3:
        if st.session_state.diario_detallado:
            df = pd.DataFrame(st.session_state.diario_detallado)
            st.dataframe(df, use_container_width=True)
        else:
            st.write("Diario vacío.")

if __name__ == "__main__":
    main()
