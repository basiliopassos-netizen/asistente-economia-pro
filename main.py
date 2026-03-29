import streamlit as st
import pandas as pd
import random
from datetime import datetime

# --- CONFIGURACIÓN DE IDENTIDAD ---
def presentacion_laura():
    st.markdown("""
        <div style="background-color: #f0f4f8; padding: 20px; border-radius: 15px; border-left: 5px solid #2e7d32; margin-bottom: 20px;">
            <h1 style="margin: 0; color: #1b5e20;">Hola, soy Laura 👩‍🌾</h1>
            <p style="font-size: 1.2em; color: #455a64;"><b>"He limpiado el jardín. Ahora podemos empezar de cero a cuidar tu dinero."</b></p>
        </div>
    """, unsafe_allow_html=True)

# --- GESTIÓN DE LA MEMORIA (Limpieza y Reset) ---
if 'diario_detallado' not in st.session_state or st.sidebar.button("🗑️ Borrar todo y empezar de cero"):
    st.session_state.diario_detallado = []
    # Al borrar, forzamos que la página se actualice
    if 'diario_detallado' in st.session_state and len(st.session_state.diario_detallado) == 0:
        st.toast("Jardín reseteado con éxito")

# --- FUNCIÓN DEL JARDÍN VISUAL ---
def dibujar_jardin(items):
    st.markdown("""<style>.escena-jardin { background: linear-gradient(180deg, #87CEEB 0%, #B2EBF2 50%, #7CFC00 50%, #228B22 100%); border-radius: 20px; padding: 10px; }</style>""", unsafe_allow_html=True)
    svg = '<div class="escena-jardin"><svg width="100%" height="450" viewBox="0 0 800 450" xmlns="http://www.w3.org/2000/svg">'
    
    # Sol y Árbol
    svg += '<circle cx="700" cy="60" r="30" fill="#FFD700"><animate attributeName="r" values="28;32;28" dur="3s" repeatCount="indefinite"/></circle>'
    svg += '<rect x="390" y="220" width="20" height="130" fill="#5D4037" />'
    svg += '<circle cx="400" cy="180" r="120" fill="#2E7D32" opacity="0.85" />'
    
    # Yoga (Chica y Chico)
    svg += '<g transform="translate(280, 350) scale(0.7)"><circle cx="0" cy="0" r="10" fill="#FFCCBC"/><path d="M0 10 L-15 40 M0 10 L15 40" stroke="#E91E63" stroke-width="5" fill="none"/></g>'
    svg += '<g transform="translate(520, 350) scale(0.7)"><circle cx="0" cy="0" r="10" fill="#FFCCBC"/><path d="M0 10 L-15 40 M0 10 L15 40" stroke="#2196F3" stroke-width="5" fill="none"/></g>'
    
    # Dibujar frutos (solo si hay datos)
    for i, item in enumerate(items):
        random.seed(i) # Para que no bailen cada vez que refrescas
        cx, cy = random.randint(330, 470), random.randint(110, 250)
        radio = min(max(float(item['Precio']) * 2.5, 10), 35)
        svg += f'<g cursor="pointer"><title>{item["Producto"]}: {item["Precio"]}€</title><circle cx="{cx}" cy="{cy}" r="{radio}" fill="#FF4444" stroke="white"/><text x="{cx}" y="{cy+4}" text-anchor="middle" fill="white" font-size
