import streamlit as st
import pandas as pd
import random
from datetime import datetime

# --- CONFIGURACIÓN DE IDENTIDAD ---
def presentacion_laura():
    st.markdown("""
        <div style="background-color: #f0f4f8; padding: 20px; border-radius: 15px; border-left: 5px solid #2e7d32; margin-bottom: 20px;">
            <h1 style="margin: 0; color: #1b5e20;">Hola, soy Laura 👩‍🌾</h1>
            <p style="font-size: 1.2em; color: #455a64;"><b>"Estoy aprendiendo a leer tus tickets. Ahora intentaré identificar si es agua, leche o maquillaje."</b></p>
        </div>
    """, unsafe_allow_html=True)

# --- MEMORIA ---
if st.sidebar.button("🗑️ Borrar todo y empezar de cero"):
    st.session_state.diario_detallado = []
    st.rerun() 

if 'diario_detallado' not in st.session_state:
    st.session_state.diario_detallado = []

# --- FUNCIÓN DE "LECTURA" (Aquí es donde ocurre la magia) ---
def leer_ticket_real(nombre_archivo):
    # Diccionario de aprendizaje para Laura
    # Esto simula lo que Laura "lee" en la imagen
    palabras_clave = {
        "mercadona": ["Agua Mineral", "Leche Entera", "Crema Facial", "Queso Gouda"],
        "ticket": ["Pan de agua", "Detergente", "Sombra de ojos", "Yogur"]
    }
    
    # Buscamos qué productos asignar según el nombre del archivo (simulación de lectura)
    nombre_lower = nombre_archivo.lower()
    
    # Si detecta que es de Mercadona, asigna productos reales de ese super
    if "mercadona" in nombre_lower:
        productos_detectados = [
            {"Producto": "Leche Hacendado", "Precio": 1.20, "Categoría": "Lácteos"},
            {"Producto": "Agua 5L", "Precio": 0.75, "Categoría": "Bebidas"},
            {"Producto": "Maquillaje Deliplus", "Precio": 4.50, "Categoría": "Belleza"}
        ]
    else:
        # Si no sabe qué es, lo deja "Sin categoría" o "Varios"
        productos_detectados = [
            {"Producto": "Producto Desconocido", "Precio": 2.00, "Categoría": "Sin categoría"}
        ]
    
    return productos_detectados

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
        radio = min(max(float(item['Precio']) * 3, 12), 35)
        svg += f'<g cursor="pointer"><title>{item["Producto"]}: {item["Precio"]}€</title><circle cx="{cx}" cy="{cy}" r="{radio}" fill="#FF4444" stroke="white"/><text x="{cx}" y="{cy+4}" text-anchor="middle" fill="white" font-size="7" font-weight="bold">{item["Producto"][:4]}</text></g>'
    
    svg += "</svg></div>"
    st.markdown(svg, unsafe_allow_html=True)

# --- MAIN ---
def main():
    presentacion_laura()
    t1, t2, t3 = st.tabs(["📤 Subir", "🌳 Árbol", "📜 Diario"])

    with t1:
        archivos = st.file_uploader("Sube tickets (Prueba con uno que diga 'Mercadona')", type=['png', 'jpg', 'pdf'], accept_multiple_files=True)
        if archivos and st.button("✨ Laura, lee estos tickets"):
            for arc in archivos:
                datos_leidos = leer_ticket_real(arc.name)
                for d in datos_leidos:
                    d["Fecha"] = datetime.now().strftime("%d/%m/%Y")
                    st.session_state.diario_detallado.append(d)
            st.success("¡Leído! He identificado productos como Leche, Agua y Maquillaje.")

    with t2:
        if st.session_state.diario_detallado:
            dibujar_jardin(st.session_state.diario_detallado)
        else:
            st.info("Sube algo para que el árbol florezca.")

    with t3:
        if st.session_state.diario_detallado:
            df = pd.DataFrame(st.session_state.diario_detallado)
            st.dataframe(df, use_container_width=True)
            st.write("### Gastos por Categoría")
            st.bar_chart(df.groupby('Categoría')['Precio'].sum())

if __name__ == "__main__":
    main()
