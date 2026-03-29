import streamlit as st
import pandas as pd
import random

# --- CONFIGURACIÓN DE IDENTIDAD ---
def presentacion_laura():
    st.markdown("""
        <div style="background-color: #f0f4f8; padding: 20px; border-radius: 15px; border-left: 5px solid #2e7d32; margin-bottom: 20px;">
            <h1 style="margin: 0; color: #1b5e20;">Hola, soy Laura 👩‍🌾</h1>
            <p style="font-size: 1.2em; color: #455a64;"><b>"Estoy aquí para cuidar tu dinero y hacer que tu jardín financiero florezca."</b></p>
        </div>
    """, unsafe_allow_html=True)

# --- FUNCIÓN DEL JARDÍN VISUAL ---
def dibujar_jardin(datos):
    st.markdown("""
        <style>
            .escena-jardin {
                background: linear-gradient(180deg, #87CEEB 0%, #B2EBF2 50%, #7CFC00 50%, #228B22 100%);
                border-radius: 20px; padding: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            }
        </style>
    """, unsafe_allow_html=True)

    svg = '<div class="escena-jardin"><svg width="100%" height="500" viewBox="0 0 800 500" xmlns="http://www.w3.org/2000/svg">'
    # Sol y Árbol
    svg += '<circle cx="700" cy="70" r="35" fill="#FFD700"><animate attributeName="r" values="33;37;33" dur="4s" repeatCount="indefinite"/></circle>'
    svg += '<rect x="385" y="240" width="30" height="160" fill="#5D4037" />'
    svg += '<circle cx="400" cy="200" r="130" fill="#2E7D32" opacity="0.9" />'
    
    # Pareja Yoga (Chica y Chico)
    svg += '<g transform="translate(260, 390)"><circle cx="0" cy="0" r="10" fill="#FFCCBC"/><path d="M0 10 L-15 40 M0 10 L15 40" stroke="#E91E63" stroke-width="5" fill="none"/></g>'
    svg += '<g transform="translate(540, 390)"><circle cx="0" cy="0" r="10" fill="#FFCCBC"/><path d="M0 10 L-15 40 M0 10 L15 40" stroke="#2196F3" stroke-width="5" fill="none"/></g>'

    # Frutos del dinero
    for nombre, precio in datos.items():
        cx, cy = random.randint(320, 480), random.randint(120, 280)
        r = min(max(float(precio) * 2, 12), 40)
        svg += f'<g cursor="help"><title>{nombre}: {precio}€</title><circle cx="{cx}" cy="{cy}" r="{r}" fill="#FF4444" stroke="white"/><text x="{cx}" y="{cy+4}" text-anchor="middle" fill="white" font-size="8" font-weight="bold">{nombre[:5]}</text></g>'
    
    svg += "</svg></div>"
    st.markdown(svg, unsafe_allow_html=True)

# --- PROGRAMA PRINCIPAL ---
def main():
    presentacion_laura()

    # Pestañas de navegación
    tab1, tab2, tab3 = st.tabs(["📤 Subir Tickets", "🌳 Mi Árbol", "📜 Diario de Gastos"])

    with tab1:
        st.subheader("Sube las fotos de los gastos de las abuelas")
        # Aquí permitimos múltiples archivos y fotos
        fotos_tickets = st.file_uploader("Puedes arrastrar varias fotos a la vez", 
                                        type=['png', 'jpg', 'jpeg', 'pdf'], 
                                        accept_multiple_files=True)
        
        if fotos_tickets:
            st.success(f"Has subido {len(fotos_tickets)} archivos correctamente.")
            for foto in fotos_tickets:
                st.image(foto, width=100, caption=foto.name)

    with tab2:
        # Datos de ejemplo (Esto se conectará con tus tickets subidos)
        gastos_actuales = {"Leche": 1.5, "Queso": 8.0, "Fruta": 4.2, "Pan": 1.0, "Carne": 12.5}
        st.subheader("Copa de tu Árbol Financiero")
        dibujar_jardin(gastos_actuales)

    with tab3:
        st.info("Aquí verás la lista detallada de todo lo que Laura está cuidando por ti.")

if __name__ == "__main__":
    main()
