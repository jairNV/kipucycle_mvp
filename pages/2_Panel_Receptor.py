import streamlit as str_web
from database import get_connection
from datetime import datetime

str_web.set_page_config(page_title="Panel Receptor - KipuCycle", layout="centered")
str_web.title("🏪 Módulo de Recepción Física de Residuos")

codigo_buscar = str_web.text_input("Ingresar Código Alfanumérico de la Entrega (Ej: KP-XXXXXX):").strip()

if codigo_buscar:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, category, district, point_name, risk_level, status FROM deliveries WHERE delivery_code = ?", (codigo_buscar,))
    entrega = cursor.fetchone()
    
    if entrega:
        str_web.info(f"📋 **Entrega Encontrada:** \n📦 *Material:* {entrega[1]}  \n📍 *Punto:* {entrega[3]}  \n⚠️ *Riesgo Técnico:* {entrega[4]}  \n🟢 *Estado Actual:* {entrega[5]}")
        
        if entrega[5] == "Confirmado":
            str_web.warning("⚠️ Esta entrega ya fue verificada y procesada previamente. No se permite doble confirmación.")
        else:
            cantidad = str_web.number_input("Cantidad física recibida:", min_value=0.1, value=1.0, step=0.5)
            unidad = str_web.selectbox("Unidad de medida:", ["Unidades", "Kilogramos (kg)"])
            
            c1, c2 = str_web.columns(2)
            if c1.button("✅ Confirmar y Verificar Recepción"):
                cursor.execute("""
                    UPDATE deliveries 
                    SET status = 'Confirmado', confirmed_quantity = ?, unit = ?, confirmed_at = ? 
                    WHERE delivery_code = ?
                """, (cantidad, unidad, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), codigo_buscar))
                conn.commit()
                str_web.success(f"Entrega {codigo_buscar} verificada correctamente en el sistema relacional.")
                
            if c2.button("❌ Rechazar Entrega"):
                cursor.execute("UPDATE deliveries SET status = 'Rechazado' WHERE delivery_code = ?", (codigo_buscar,))
                conn.commit()
                str_web.error(f"Entrega {codigo_buscar} marcada como rechazada.")
    else:
        str_web.error("El código ingresado no existe en el registro del ecosistema KipuCycle.")
    conn.close()