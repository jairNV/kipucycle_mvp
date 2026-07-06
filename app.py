import streamlit as str_web
import random
import json
from database import init_database, seed_collection_points, get_connection, save_interaction, create_collection_request, create_delivery
from classifier import predict_waste_category
from rules import WASTE_CATEGORIES, WASTE_RULES, evaluate_waste

str_web.set_page_config(page_title="KipuCycle AI - WhatsApp Simulator", page_icon="🤖", layout="centered")

# Inicializar Base de Datos de manera segura
init_database()
seed_collection_points()

str_web.title("💬 KipuCycle AI — Simulador de WhatsApp")
str_web.write("Prototipo de Interacción Ciudadana para la Gestión Sostenible de Residuos.")

if str_web.button("🔄 Reiniciar Flujo de Chat"):
    for key in list(str_web.session_state.keys()):
        del str_web.session_state[key]
    str_web.rerun()

# Control de Estados del Flujo Interactivo
if "step" not in str_web.session_state:
    str_web.session_state.step = 1
    str_web.session_state.category = None
    str_web.session_state.risk_info = {}
    str_web.session_state.district = None

# PASO 1: Captura Fotográfica u Opción de Contingencia Manual
if str_web.session_state.step == 1:
    str_web.subheader("Paso 1: Identificación del Residuo")
    uploaded_file = str_web.file_uploader("Subar fotografía del residuo o activar Contingencia Manual:", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        cat_pred, conf = predict_waste_category(uploaded_file)
        str_web.info(f"🤖 IA propone: **{cat_pred}** (Confianza: {conf*100:.1f}%)")
        
        col1, col2 = str_web.columns(2)
        if col1.button("✅ Confirmar Categoría de IA"):
            str_web.session_state.category = cat_pred
            str_web.session_state.step = 2
            str_web.rerun()
        if col2.button("❌ Corregir con Menú Manual"):
            str_web.session_state.step = "manual_fix"
            str_web.rerun()
            
    str_web.write("---")
    if str_web.button("⚠️ Activar Contingencia Manual Directa"):
        str_web.session_state.step = "manual_fix"
        str_web.rerun()

elif str_web.session_state.step == "manual_fix":
    str_web.subheader("Paso 1: Selección Manual de Contingencia")
    selected_cat = str_web.selectbox("Seleccione la categoría real del residuo:", WASTE_CATEGORIES)
    if str_web.button("Continuar con Categoría Seleccionada"):
        str_web.session_state.category = selected_cat
        str_web.session_state.step = 2
        str_web.rerun()

# PASO 2: Evaluación de Condición Dinámica y Riesgo
elif str_web.session_state.step == 2:
    cat = str_web.session_state.category
    str_web.subheader(f"Paso 2: Evaluación del Estado — {cat}")
    
    if cat in WASTE_RULES:
        ans = str_web.radio(WASTE_RULES[cat]["question"], ["No", "Sí"])
        if str_web.button("Enviar Respuesta Técnico-Ambiental"):
            str_web.session_state.risk_info = evaluate_waste(cat, ans)
            str_web.session_state.step = 3
            str_web.rerun()
    else:
        str_web.session_state.risk_info = {"risk_level": "Verde", "instruction": "Dispón con normalidad.", "can_wait": True}
        str_web.session_state.step = 3
        str_web.rerun()

# PASO 3: Localización Geográfica por Distrito
elif str_web.session_state.step == 3:
    str_web.subheader("Paso 3: Ubicación y Ruteo Local")
    str_web.write(f"**Recomendación del Agente:** {str_web.session_state.risk_info['instruction']}")
    
    distrito = str_web.selectbox("Selecciona tu distrito actual en Lima Metropolitana:", ["San Miguel", "Pueblo Libre", "Cercado de Lima"])
    if str_web.button("Buscar Punto Compatible Próximo"):
        str_web.session_state.district = distrito
        str_web.session_state.step = 4
        str_web.rerun()

# PASO 4: Recomendación y Toma de Decisiones Finales
elif str_web.session_state.step == 4:
    str_web.subheader("Paso 4: Puntos de Entrega y Logística Disponibles")
    cat = str_web.session_state.category
    dist = str_web.session_state.district
    risk = str_web.session_state.risk_info["risk_level"]
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, address, schedule, accepted_json, specialized FROM collection_points WHERE district = ? AND active = 1", (dist,))
    puntos = cursor.fetchall()
    conn.close()
    
    compatibles = []
    for p in puntos:
        items_aceptados = json.loads(p[3])
        if cat in items_aceptados:
            compatibles.append(p)
            
    if compatibles:
        str_web.success(f"Se encontraron {len(compatibles)} puntos de reciclaje óptimos en {dist}:")
        for p in compatibles:
            spec_badge = " [ESPECIALIZADO RAEE]" if p[4] == 1 else ""
            str_web.markdown(f"📍 **{p[0]}**{spec_badge}  \n🏠 *Dirección:* {p[1]}  \n⏰ *Horario:* {p[2]}")
            
        str_web.write("---")
        opcion = str_web.radio("¿Cómo deseas proceder con la entrega?", ["Deseo ir al Punto Recomendado", "No puedo llevarlo (Solicitar recojo a domicilio)"])
        
        if opcion == "Deseo ir al Punto Recomendado":
            punto_elegido = str_web.selectbox("Confirma el punto al que asistirás:", [p[0] for p in compatibles])
            if str_web.button("Generar Código Alfanumérico"):
                codigo = f"KP-{random.randint(100000, 999999)}"
                create_delivery(codigo, cat, dist, punto_elegido, risk)
                save_interaction(cat, 0.90, dist, risk, f"Entrega Agendada {codigo}")
                str_web.session_state.final_msg = f"🎉 **Código de entrega generado:** `{codigo}`. Preséntalo en el punto elegido."
                str_web.session_state.step = "final"
                str_web.rerun()
                
        else:
            cant = str_web.selectbox("¿Qué cantidad aproximada posee?", ["1 unidad", "2 a 5 unidades", "Más de 5 unidades"])
            if str_web.button("Confirmar Solicitud de Recojo"):
                create_collection_request(cat, dist, cant, risk, str_web.session_state.risk_info["can_wait"])
                save_interaction(cat, 0.90, dist, risk, "Solicitud de Recolección")
                str_web.session_state.final_msg = "🚚 **Solicitud registrada con éxito**. El camión municipal circular coordinará la recolección según el nivel de urgencia."
                str_web.session_state.step = "final"
                str_web.rerun()
    else:
        str_web.warning(f"No se encontraron puntos directos para {cat} en {dist}. Tu solicitud se derivará a recolección de contingencia.")
        if str_web.button("Registrar Solicitud de Emergencia Ambiental"):
            create_collection_request(cat, dist, "1 unidad", risk, False)
            str_web.session_state.final_msg = "🚨 Solicitud de emergencia guardada."
            str_web.session_state.step = "final"
            str_web.rerun()

elif str_web.session_state.step == "final":
    str_web.success(str_web.session_state.final_msg)
    if str_web.button("Realizar nueva consulta"):
        for key in list(str_web.session_state.keys()):
            del str_web.session_state[key]
        str_web.rerun()
