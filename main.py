import streamlit as st
import pandas as pd
import random

# --- CONFIGURACIÓN DE IDENTIDAD ---
def presentacion_laura():
    st.markdown("""
        <div style="background-color: #f0f4f8; padding: 20px; border-radius: 15px; border-left: 5px solid #2e7d32; margin-bottom: 20px;">
            <h1 style="margin: 0; color: #1b5e20;">Hola, soy Laura 👩‍🌾</h1>
            <p style="font-size: 1.2em; color: #455a64;"><b>"Estoy aquí para cuidar tu dinero. Todo lo que subas quedará guardado en nuestro diario."</b></p>
        </div>
    """, unsafe_allow_html=True)

# --- INICIALIZAR LA MEMORIA (La libreta de Laura) ---
if 'lista_de_gastos' not in st.session_state:
    # Empezamos con unos pocos para que el árbol no esté vacío al principio
    st.session_state.lista_de_gastos = [
        {"Producto": "Gastos Iniciales", "Precio": 5.0, "Fecha": "2024-01-01"}
    ]

# --- FUNCIÓN DEL JARDÍN VISUAL ---
def dibujar_jardin(datos_lista):
    st.markdown("""
        <style>
            .escena-jardin {
                background: linear-gradient(180deg, #87CEEB 0%, #B2EBF2 50%, #7CFC00 50%, #228B22 100%);
                border-radius: 20px; padding: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            }
        </style>
    """, unsafe_allow_html=True)

    svg = '<div class="escena-jardin"><svg width="100%" height="500" viewBox="0 0 800 500" xmlns="http://www.w3.org/2000/svg">'
    svg += '<circle cx="700" cy="70" r="35" fill="#FFD700"><animate attributeName="r" values="33;37;33" dur="4s" repeatCount="indefinite"/></circle>'
    svg += '<rect x="385" y="240" width="30" height="160" fill="#5D4037" />'
    svg += '<circle cx="400" cy="200" r="130" fill="#2E7D32" opacity="0.9" />'
    
    # Personajes Yoga
    svg += '<g transform="translate(260, 390)"><circle cx="0" cy="0" r="10" fill="#FFCCBC"/><path d="M0 10 L-15 40 M0 10 L15 40" stroke="#E91E63" stroke-width="5" fill="none"/></g>'
    svg += '<g transform="translate(540, 390)"><circle cx="0" cy="0" r="10" fill="#FFCCBC"/><path d="M0 10 L-15 40 M0 10 L15 40" stroke="#2196F3" stroke-width="5" fill="none"/></g>'

    # Dibujar frutos basados en la MEMORIA REAL
    for gasto in datos_lista:
        cx, cy = random.randint(320, 480), random.randint(120, 280)
        precio = float(gasto['Precio'])
        r = min(max(precio * 2, 12), 40)
        svg += f'<g cursor="help"><title>{gasto["Producto"]}: {precio}€</title><circle cx="{cx}" cy="{cy}" r="{r}" fill="#FF4444" stroke="white"/><text x="{cx}" y="{cy+4}" text-anchor="middle" fill="white" font-size="8" font-weight="bold">{gasto["Producto"][:5]}</text></g>'
    
    svg += "</svg></div>"
    st.markdown(svg, unsafe_allow_html=True)

# --- PROGRAMA PRINCIPAL ---
def main():
    presentacion_laura()

    tab1, tab2, tab3 = st.tabs(["📤 Subir Tickets", "🌳 Mi Árbol", "📜 Diario de Gastos"])

    with tab1:
        st.subheader("Sube los tickets de las abuelas")
        archivos = st.file_uploader("Arrastra fotos o PDFs aquí", type=['png', 'jpg', 'jpeg', 'pdf'], accept_multiple_files=True)
        
        if archivos:
            for archivo in archivos:
                # Si el archivo NO está ya en la lista, lo añadimos
                if not any(g['Producto'] == archivo.name for g in st.session_state.lista_de_gastos):
                    # Aquí simulamos que el precio es 10€ por defecto hasta que pongamos el lector automático
                    nuevo_gasto = {"Producto": archivo.name, "Precio": 10.0, "Fecha": "Hoy"}
                    st.session_state.lista_de_gastos.append(nuevo_gasto)
            
            st.success(f"¡Laura ha anotado {len(archivos)} nuevos archivos en el diario!")

    with tab2:
        st.subheader("Copa de tu Árbol Financiero")
        # Usamos los datos de la memoria
        dibujar_jardin(st.session_state.lista_de_gastos)

    with tab3:
        st.subheader("📜 Diario de Gastos de Laura")
        if st.session_state.lista_de_gastos:
            # Convertimos la lista de la memoria en una tabla bonita
            df_diario = pd.DataFrame(st.session_state.lista_de_gastos)
            st.table(df_diario)
        else:
            st.write("El diario está vacío. ¡Sube algún ticket!")

if __name__ == "__main__":
    main()
