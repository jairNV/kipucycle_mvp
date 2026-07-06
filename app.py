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

# ---- BARRA LATERAL (CONFIGURACIÓN Y CONTROL) ----
st.sidebar.title("♻️ KipuCycle MVP")
st.sidebar.markdown("Simulador de Chatbot de reciclaje con Inteligencia Artificial.")

# Historial de interacciones registradas en la BD
st.sidebar.subheader("📊 Métricas de la Sesión")
historial_db = obtener_historial()
st.sidebar.metric(label="Imágenes Procesadas", value=len(historial_db))

# CONTROLADOR SECRETO PARA LA DEMOSTRACIÓN EN VIVO
st.sidebar.markdown("---")
with st.sidebar.expander("⚙️ Simulación de IA (Modo Demo)"):
    st.session_state['demo_target'] = st.selectbox(
        "Forzar detección para la presentación:",
        ["Automático (Por nombre)", "Botella PET", "Papel o cartón", "Lata metálica", "Pila o batería"]
    )

# ---- CUERPO PRINCIPAL: INTERFAZ DE WHATSAPP ----
st.title("📱 KipuCycle AI")
st.caption("Chatbot de Reciclaje Automatizado vía WhatsApp")

# Contenedor para simular la ventana del chat
chat_placeholder = st.container()

# Renderizar el historial acumulado en la pantalla
with chat_placeholder:
    # Mensaje de bienvenida fijo del Bot
    st.chat_message("assistant").write("¡Hola! Soy el asistente de **KipuCycle**. Envíame una foto de cualquier residuo para decirte cómo reciclarlo correctamente en tu localidad. ♻️")
    
    for msg in historial_db:
        # Mostrar lo que envió el usuario (Se guarda una referencia de que envió una imagen)
        st.chat_message("user").write(f"📷 [Imagen Enviada]: {msg[1]}")
        # Mostrar la respuesta almacenada del bot
        st.chat_message("assistant").write(f"**Resultado:** {msg[2]} (Confianza: {msg[3]:.2f})")
        st.chat_message("assistant").info(msg[4])

# ---- ZONA DE CARGA DE IMÁGENES (CÁMARA O GALERÍA) ----
st.markdown("---")
archivo_imagen = st.file_uploader("Enviar imagen al chat...", type=["jpg", "jpeg", "png"])

if archivo_imagen is not None:
    # Evitar procesar la misma imagen múltiples veces seguidas
    ultimo_procesado = st.session_state.get('ultimo_archivo', "")
    
    if archivo_imagen.name != ultimo_procesado:
        # Mostrar una vista previa de la foto en el chat inmediatamente
        st.chat_message("user").image(archivo_imagen, caption="Imagen cargada", width=250)
        
        # Capturar el estado del selector secreto de la barra lateral
        target_demo = st.session_state.get('demo_target', "Automático (Por nombre)")
        
        # 1. Ejecutar el motor de clasificación (Pasando el selector secreto)
        categoria, confianza = predict_waste_category(archivo_imagen, target_demo)
        
        # 2. Buscar las reglas de reciclaje correspondientes en la base de conocimientos
        consejo = obtener_recomendacion(categoria)
        
        # 3. Guardar el registro completo en la base de datos local SQLite
        guardar_mensaje(archivo_imagen.name, categoria, confianza, consejo)
        
        # Registrar el archivo en el estado de la sesión
        st.session_state['ultimo_archivo'] = archivo_imagen.name
        
        # Forzar recarga rápida de la página para pintar la nueva burbuja de conversación
        st.rerun()
