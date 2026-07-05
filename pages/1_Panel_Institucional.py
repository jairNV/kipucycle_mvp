import streamlit as str_web
import pandas as pd
from database import get_connection

str_web.set_page_config(page_title="Panel Institucional - KipuCycle", layout="wide")
str_web.title("📊 Panel Institucional de Monitoreo")

conn = get_connection()

# Métricas Principales de Control Municipal
total_consultas = pd.read_sql_query("SELECT COUNT(*) as total FROM interactions", conn).iloc[0]['total']
pendientes = pd.read_sql_query("SELECT COUNT(*) as total FROM collection_requests WHERE status='Pendiente'", conn).iloc[0]['total']
confirmadas = pd.read_sql_query("SELECT COUNT(*) as total FROM deliveries WHERE status='Confirmado'", conn).iloc[0]['total']
tot_entregas = pd.read_sql_query("SELECT COUNT(*) as total FROM deliveries", conn).iloc[0]['total']

tasa = (confirmadas / tot_entregas * 100) if tot_entregas > 0 else 0.0

c1, c2, c3, c4 = str_web.columns(4)
c1.metric("Total Consultas", total_consultas)
c2.metric("Solicitudes de Recojo Pendientes", pendientes)
c3.metric("Entregas Verificadas", confirmadas)
c4.metric("Tasa de Conversión", f"{tasa:.1f}%")

str_web.subheader("📋 Solicitudes de Recolección a Domicilio")
df_reqs = pd.read_sql_query("SELECT id, category, district, quantity_range, risk_level, status FROM collection_requests", conn)
str_web.dataframe(df_reqs, use_container_width=True)

# Simulación de Campaña Masiva Exigida por el PDF
str_web.subheader("📢 Simulación Inteligente de Campañas de Reciclaje")
dist_campana = str_web.selectbox("Selecciona Distrito para simular campaña:", ["San Miguel", "Pueblo Libre", "Cercado de Lima"])
cat_campana = str_web.selectbox("Selecciona Categoría:", ["Botella PET", "Lata metálica", "Papel o cartón", "Pila o batería", "Residuo electrónico pequeño"])

if str_web.button("🚀 Lanzar Campaña de Agrupamiento"):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM collection_requests 
        WHERE district = ? AND category = ? AND status = 'Pendiente'
    """, (dist_campana, cat_campana))
    conteo = cursor.fetchone()[0]
    
    if conteo >= 3:
        cursor.execute("""
            UPDATE collection_requests SET status = 'Agrupado en Campaña' 
            WHERE district = ? AND category = ? AND status = 'Pendiente'
        """, (dist_campana, cat_campana))
        conn.commit()
        str_web.success(f"¡Éxito! Se agruparon {conteo} solicitudes de **{cat_campana}** en **{dist_campana}** y se trazó la ruta óptima del camión municipal.")
    else:
        str_web.warning(f"No se cumple el requisito mínimo: Se necesitan al menos 3 solicitudes pendientes (Actuales: {conteo}).")

conn.close()