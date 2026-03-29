import streamlit as st
import pandas as pd
import random

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Mi Árbol Financiero", layout="wide")

# --- 1. FUNCIÓN QUE CREA EL JARDÍN VISUAL ---
# Esta función es la que dibuja el cielo, el sol, los personajes y las "frutas" (tus gastos)
def generar_jardin_visual(datos_gastos):
    # Estilos para el contenedor
    st.markdown("""
        <style>
            .escena-jardin {
                background: linear-gradient(180deg, #87CEEB 0%, #B2EBF2 50%, #7CFC00 50%, #228B22 100%);
                border-radius: 20px;
                padding: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                text-align: center;
            }
        </style>
    """, unsafe_allow_html=True)

    # Iniciamos el dibujo SVG
    # El viewBox="0 0 800 500" define nuestro "lienzo" de dibujo
    svg_inicio = '<div class="escena-jardin"><svg width="100%" height="550" viewBox="0 0 800 500" xmlns="http://www.w3.org/2000/svg">'
    
    # Dibujamos el Sol con una pequeña animación de pulso
    sol = '<circle cx="700" cy="70" r="35" fill="#FFD700"><animate attributeName="r" values="33;37;33" dur="4s" repeatCount="indefinite"/></circle>'
    
    # Dibujamos el Árbol (Tronco y Copa)
    tronco = '<rect x="385" y="240" width="30" height="160" fill="#5D4037" />'
    copa = '<circle cx="400" cy="200" r="130" fill="#2E7D32" opacity="0.9" />'

    # Personajes haciendo Yoga (Chica en rosa, Chico en azul)
    # Son formas simplificadas para que el código no sea infinito
    chica_yoga = """
    <g transform="translate(260, 390)">
        <circle cx="0" cy="0" r="10" fill="#FFCCBC"/> <path d="M0 10 L-15 40 M0 10 L15 40 M0 10 L0 30" stroke="#E91E63" stroke-width="5" fill="none"/> <text x="0" y="55" text-anchor="middle" font-size="10" fill="white">Yoga Girl</text>
    </g>"""
    
    chico_yoga = """
    <g transform="translate(540, 390)">
        <circle cx="0" cy="0" r="10" fill="#FFCCBC"/> <path d="M0 10 L-15 40 M0 10 L15 40 M0 10 L0 30" stroke="#2196F3" stroke-width="5" fill="none"/> <text x="0" y="55" text-anchor="middle" font-size="10" fill="white">Yoga Boy</text>
    </g>"""

    # Generamos los Frutos (Gastos) dinámicamente
    frutos_html = ""
    for nombre, precio in datos_gastos.items():
        # Posicionamos las frutas de forma aleatoria dentro de la copa del árbol
        cx = random.randint(320, 480)
        cy = random.randint(120, 280)
        # El tamaño de la fruta depende del precio (mínimo 12, máximo 40)
        radio = min(max(float(precio) * 2, 12), 40)
        
        frutos_html += f"""
        <g cursor="help">
            <title>{nombre}: {precio}€</title>
            <circle cx="{cx}" cy="{cy}" r="{radio}" fill="#FF4444" stroke="white" stroke-width="1">
                <animate attributeName="opacity" values="0.8;1;0.8" dur="{random.uniform(2, 5)}s" repeatCount="indefinite" />
            </circle>
            <text x="{cx}" y="{cy+4}" text-anchor="middle" fill="white" font-size="8" font-weight="bold">{nombre[:5]}</text>
        </g>
        """

    svg_fin = "</svg></div>"
    
    # Mostramos todo el conjunto en Streamlit
    st.markdown(svg_inicio + sol + tronco + copa + chica_yoga + chico_yoga + frutos_html + svg_fin, unsafe_allow_html=True)

# --- 2. LÓGICA PRINCIPAL DEL PROGRAMA ---
def main():
    st.title("🌳 Mi Jardín de Economía Personal")
    
    # Simulamos o cargamos tus datos (Aquí es donde iría tu carga de Excel/CSV)
    # He creado este diccionario de ejemplo basado en tu imagen anterior
    datos_ejemplo = {
        "Queso Gouda": 7.8,
        "Magdalena": 2.6,
        "Tiramisu": 5.4,
        "Horchata": 1.5,
        "Nectarina": 1.9,
        "Bronchales": 3.0,
        "Nachos": 2.2,
        "Pan": 0.8
    }

    # Creamos pestañas para organizar el contenido como tenías antes
    tab1, tab2, tab3 = st.tabs(["📤 Subir Datos", "🌳 Mi Árbol", "📜 Diario"])

    with tab1:
        st.info("Aquí puedes subir tus archivos de gastos.")

    with tab2:
        st.subheader("Copa de Mi Árbol Financiero")
        # Llamamos a nuestra función mágica enviándole los datos
        generar_jardin_visual(datos_ejemplo)
        st.write("---")
        st.caption("Cada fruta roja representa un gasto. Cuanto más grande es la fruta, mayor fue el gasto.")

    with tab3:
        st.write("Aquí aparecerá el histórico de tus movimientos.")

# Ejecutamos la aplicación
if __name__ == "__main__":
    main()
