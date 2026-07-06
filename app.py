import streamlit as st
import os
from PIL import Image
from database import inicializar_db, guardar_mensaje, obtener_historial
from classifier import predict_waste_category
from rules import obtener_recomendacion

# Configuración inicial de la página
st.set_page_config(page_title="KipuCycle AI - WhatsApp Simulator", page_icon="♻️", layout="centered")

# Inicializar la base de datos SQLite local
inicializar_db()

# ---- BARRA LATERAL LIMPIA ----
st.sidebar.title("♻️ KipuCycle MVP")
st.sidebar.markdown("Simulador de Chatbot de reciclaje con Inteligencia Artificial Autónoma.")

# Historial de interacciones registradas en la BD
st.sidebar.subheader("📊 Métricas de la Sesión")
historial_db = obtener_historial()
st.sidebar.metric(label="Imágenes Procesadas", value=len(historial_db))

# ---- CUERPO PRINCIPAL: INTERFAZ DE WHATSAPP ----
st.title("📱 KipuCycle AI")
st.caption("Chatbot de Reciclaje Automatizado vía WhatsApp")

chat_placeholder = st.container()

with chat_placeholder:
    st.chat_message("assistant").write("¡Hola! Soy el asistente de **KipuCycle**. Envíame una foto de cualquier residuo para decirte cómo reciclarlo correctamente en tu localidad. ♻️")
    
    for msg in historial_db:
        st.chat_message("user").write(f"📷 [Imagen Enviada]: {msg[1]}")
        st.chat_message("assistant").write(f"**Resultado:** {msg[2]} (Confianza: {msg[3]:.2f})")
        st.chat_message("assistant").info(msg[4])

# ---- CARGA DE IMÁGENES AUTOMÁTICA ----
st.markdown("---")
archivo_imagen = st.file_uploader("Enviar imagen al chat...", type=["jpg", "jpeg", "png"])

if archivo_imagen is not None:
    ultimo_procesado = st.session_state.get('ultimo_archivo', "")
    
    if archivo_imagen.name != ultimo_procesado:
        st.chat_message("user").image(archivo_imagen, caption="Imagen cargada", width=250)
        
        # Llama a la función de forma 100% automática procesando la imagen pura
        categoria, confianza = predict_waste_category(archivo_imagen)
        
        consejo = obtener_recomendacion(categoria)
        guardar_mensaje(archivo_imagen.name, categoria, confianza, consejo)
        
        st.session_state['ultimo_archivo'] = archivo_imagen.name
        st.rerun()
