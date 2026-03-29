import streamlit as st
import pandas as pd
import random
from datetime import datetime

# --- CONFIGURACIÓN DE IDENTIDAD ---
def presentacion_laura():
    st.markdown("""
        <div style="background-color: #f0f4f8; padding: 20px; border-radius: 15px; border-left: 5px solid #2e7d32; margin-bottom: 20px;">
            <h1 style="margin: 0; color: #1b5e20;">Hola, soy Laura 👩‍🌾</h1>
            <p style="font-size: 1.2em; color: #455a64;"><b>"He abierto tus tickets y he anotado cada producto en el diario para que podamos calcular tus ahorros."</b></p>
        </div>
    """, unsafe_allow_html=True)

# --- INICIALIZAR LA MEMORIA REAL (Desglosada por productos) ---
if 'diario_detallado' not in st.session_state:
    # Datos iniciales desglosados (como los de tu captura de pantalla)
    st.session_state.diario_detallado = [
        {"Fecha": "2024-05-20", "Producto": "Queso gouda tierno", "Precio": 7.8, "Categoría": "Comida"},
        {"Fecha": "2024-05-20", "Producto": "Magdalena azúcar", "Precio": 2.6, "Categoría": "Dulces"},
        {"Fecha": "2024-05-21", "Producto": "Nectarina bandeja", "Precio": 1.9, "Categoría": "Fruta"}
    ]

# --- FUNCIÓN DEL JARDÍN VISUAL ---
def dibujar_jardin(items):
    st.markdown("""<style>.escena-jardin { background: linear-gradient(180deg, #87CEEB 0%, #B2EBF2 50%, #7CFC00 50%, #228B22 100%); border-radius: 20px; padding: 10px; }</style>""", unsafe_allow_html=True)
    svg = '<div class="escena-jardin"><svg width="100%" height="450" viewBox="0 0 800 450" xmlns="http://www.w3.org/2000/svg">'
    # Sol, Tronco y Copa
    svg += '<circle cx="700" cy="60" r="30" fill="#FFD700"><animate attributeName="r" values="28;32;28" dur="3s" repeatCount="indefinite"/></circle>'
    svg += '<rect x="390" y="220" width="20" height="130" fill="#5D4037" />'
    svg += '<circle cx="400" cy="180" r="120" fill="#2E7D32" opacity="0.85" />'
    
    # Dibujar cada producto como un fruto
    for item in items:
        cx, cy = random.randint(330, 470), random.randint(110, 250)
        radio = min(max(float(item['Precio']) * 2.5, 10), 35)
        svg += f'<g cursor="pointer"><title>{item["Producto"]}: {item["Precio"]}€</title><circle cx="{cx}" cy="{cy}" r="{radio}" fill="#FF4444" stroke="white"/><text x="{cx}" y="{cy+4}" text-anchor="middle" fill="white" font-size="7" font-weight="bold">{item["Producto"][:4]}</text></g>'
    
    svg += "</svg></div>"
    st.markdown(svg, unsafe_allow_html=True)

# --- PROGRAMA PRINCIPAL ---
def main():
    presentacion_laura()
    tab1, tab2, tab3 = st.tabs(["📤 Subir Tickets", "🌳 Mi Árbol", "📜 Diario Desglosado"])

    with tab1:
        st.subheader("Cargador de Tickets")
        archivos = st.file_uploader("Sube tus fotos o PDFs", type=['png', 'jpg', 'pdf'], accept_multiple_files=True)
        
        if archivos:
            if st.button("Procesar y desglosar tickets"):
                for arc in archivos:
                    # SIMULACIÓN: Al subir un ticket, Laura "encuentra" productos dentro
                    # En el futuro, aquí irá el código que lee la foto de verdad
                    nuevos_items = [
                        {"Fecha": datetime.now().strftime("%Y-%m-%d"), "Producto": f"Item 1 de {arc.name[:10]}", "Precio": round(random.uniform(1, 10), 2), "Categoría": "Supermercado"},
                        {"Fecha": datetime.now().strftime("%Y-%m-%d"), "Producto": f"Item 2 de {arc.name[:10]}", "Precio": round(random.uniform(1, 5), 2), "Categoría": "Varios"}
                    ]
                    st.session_state.diario_detallado.extend(nuevos_items)
                st.success("¡Tickets desglosados! Mira el Diario o el Árbol.")

    with tab2:
        st.subheader("Tu Árbol de Productos Reales")
        dibujar_jardin(st.session_state.diario_detallado)
        
        # Cálculo rápido
        total = sum(item['Precio'] for item in st.session_state.diario_detallado)
        st.metric("Gasto Total Acumulado", f"{total:.2f} €")

    with tab3:
        st.subheader("📜 Desglose Detallado de Gastos")
        if st.session_state.diario_detallado:
            df = pd.DataFrame(st.session_state.diario_detallado)
            
            # Buscador/Filtro por nombre
            busqueda = st.text_input("🔍 Buscar producto (ej: Queso)")
            if busqueda:
                df = df[df['Producto'].str.contains(busqueda, case=False)]
            
            st.dataframe(df, use_container_width=True)
            
            # Resumen semanal (Agrupado)
            st.write("### 📊 Resumen por Categoría")
            resumen = df.groupby('Categoría')['Precio'].sum()
            st.bar_chart(resumen)
        else:
            st.info("Aún no hay productos desglosados.")

if __name__ == "__main__":
    main()
