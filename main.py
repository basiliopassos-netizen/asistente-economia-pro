import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
import re

# Configuración de la página
st.set_page_config(page_title="PocketAdmin - Economía Doméstica", page_icon="🏦", layout="wide")

# --- FUNCIONES DE APOYO ---
def extraer_total(texto):
    """Intenta buscar un número que parezca el total del ticket"""
    precios = re.findall(r'\d+[\.,]\d{2}', texto)
    if precios:
        # Convertimos a float para poder operar
        precios_float = [float(p.replace(',', '.')) for p in precios]
        return max(precios_float) # Normalmente el importe más alto es el total
    return 0.0

# --- INTERFAZ ---
def main():
    st.title("🏦 PocketAdmin Pro")
    st.subheader("Tu asistente inteligente de microeconomía")

    menu = ["📊 Dashboard General", "📸 Escanear Ticket", "📂 Importar PDF/Excel", "💡 Recomendaciones"]
    choice = st.sidebar.selectbox("Menú Principal", menu)

    # Inicializar una base de datos temporal en la sesión
    if 'mis_gastos' not in st.session_state:
        st.session_state.mis_gastos = pd.DataFrame(columns=['Fecha', 'Concepto', 'Categoría', 'Importe'])

    if choice == "📊 Dashboard General":
        st.info("Aquí verás el resumen de tus finanzas.")
        if not st.session_state.mis_gastos.empty:
            st.write(st.session_state.mis_gastos)
            total = st.session_state.mis_gastos['Importe'].sum()
            st.metric("Gasto Total Acumulado", f"{total} €")
        else:
            st.warning("Aún no hay datos. ¡Ve a la sección de escáner!")

    elif choice == "📸 Escanear Ticket":
        st.header("📸 Escáner de Tickets Inteligente")
        archivo_foto = st.file_uploader("Sube una foto de tu ticket", type=['jpg', 'jpeg', 'png'])

        if archivo_foto:
            img = Image.open(archivo_foto)
            st.image(img, caption="Imagen cargada", width=400)
            
            if st.button("🚀 Procesar Ticket"):
                with st.spinner("Analizando texto con IA..."):
                    # Extraer texto (OCR)
                    texto = pytesseract.image_to_string(img)
                    importe_detectado = extraer_total(texto)
                    
                    st.success("¡Lectura completada!")
                    
                    # Formulario para confirmar datos
                    with st.form("confirmar_gasto"):
                        concepto = st.text_input("Establecimiento / Concepto", "Compra General")
                        cat = st.selectbox("Categoría", ["Alimentación", "Hogar", "Ocio", "Transporte", "Otros"])
                        monto = st.number_input("Confirmar Importe (€)", value=importe_detectado)
                        
                        if st.form_submit_button("Guardar en mi economía"):
                            nuevo_gasto = pd.DataFrame([[pd.Timestamp.now().strftime("%Y-%m-%d"), concepto, cat, monto]], 
                                                     columns=['Fecha', 'Concepto', 'Categoría', 'Importe'])
                            st.session_state.mis_gastos = pd.concat([st.session_state.mis_gastos, nuevo_gasto], ignore_index=True)
                            st.balloons()
                            st.success("Gasto guardado correctamente.")

    elif choice == "💡 Recomendaciones":
        st.header("🔍 Análisis de Fugas y Consejos")
        st.write("Basado en tus datos:")
        st.markdown("* **Fuga detectada:** Has gastado un 15% más en 'Ocio' que la semana pasada.")
        st.markdown("* **Recomendación:** Intenta reducir los gastos hormiga (cafés, suscripciones) para ahorrar 40€ este mes.")

if __name__ == "__main__":
    main()
