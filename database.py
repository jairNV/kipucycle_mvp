import sqlite3
import json
import os
from datetime import datetime

DB_PATH = "data/kipucycle.db"

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            confidence REAL,
            district TEXT,
            risk_level TEXT,
            action TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collection_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            district TEXT NOT NULL,
            quantity_range TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            can_wait INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pendiente',
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS deliveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            delivery_code TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            district TEXT NOT NULL,
            point_name TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            declared_quantity TEXT DEFAULT '1 unidad',
            confirmed_quantity REAL,
            unit TEXT,
            status TEXT NOT NULL DEFAULT 'Pendiente',
            created_at TEXT NOT NULL,
            confirmed_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collection_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            district TEXT NOT NULL,
            address TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            schedule TEXT,
            accepted_json TEXT NOT NULL,
            specialized INTEGER NOT NULL DEFAULT 0,
            active INTEGER NOT NULL DEFAULT 1
        )
    ''')
    
    conn.commit()
    conn.close()

def seed_collection_points():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM collection_points")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    DEMO_POINTS = [
        ("EcoPunto San Miguel", "San Miguel", "Av. La Marina 1200", -12.0785, -77.0855, "Lunes a sabado, 09:00 a 18:00", ["Botella PET", "Lata metalica", "Papel o carton"], 0),
        ("Punto RAEE San Miguel", "San Miguel", "Av. Universitaria 800", -12.0735, -77.0830, "Lunes a viernes, 09:00 a 17:00", ["Pila o bateria", "Residuo electronico pequeno"], 1),
        ("Estacion Circular Costanera", "San Miguel", "Av. Costanera 1450", -12.0880, -77.0910, "Martes y jueves, 10:00 a 16:00", ["Botella PET", "Lata metalica"], 0),
        ("EcoPunto Pueblo Libre", "Pueblo Libre", "Av. Bolivar 950", -12.0740, -77.0630, "Lunes a sabado, 08:00 a 17:00", ["Botella PET", "Lata metalica", "Papel o carton"], 0),
        ("Centro RAEE Pueblo Libre", "Pueblo Libre", "Av. Sucre 600", -12.0710, -77.0670, "Miercoles y sabado, 09:00 a 15:00", ["Pila o bateria", "Residuo electronico pequeno"], 1),
        ("Punto Circular Bolivar", "Pueblo Libre", "Jr. Cueva 210", -12.0760, -77.0590, "Lunes a viernes, 10:00 a 18:00", ["Papel o carton", "Botella PET"], 0),
        ("EcoPunto Centro de Lima", "Cercado de Lima", "Av. Uruguay 350", -12.0540, -77.0410, "Lunes a viernes, 09:00 a 17:00", ["Botella PET", "Lata metalica", "Papel o carton"], 0),
        ("Punto Especializado RAEE Lima", "Cercado de Lima", "Av. Argentina 1000", -12.0490, -77.0580, "Lunes a sabado, 09:00 a 16:00", ["Pila o bateria", "Residuo electronico pequeno"], 1),
        ("Estacion Circular Universitaria", "Cercado de Lima", "Av. Universitaria 500", -12.0600, -77.0660, "Martes a sabado, 10:00 a 18:00", ["Botella PET", "Lata metalica", "Papel o carton"], 0)
    ]
    
    for pt in DEMO_POINTS:
        cursor.execute('''
            INSERT INTO collection_points (name, district, address, latitude, longitude, schedule, accepted_json, specialized, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        ''', (pt[0], pt[1], pt[2], pt[3], pt[4], pt[5], json.dumps(pt[6]), pt[7]))
        
    conn.commit()
    conn.close()

def save_interaction(category, confidence, district, risk_level, action):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO interactions (category, confidence, district, risk_level, action, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (category, confidence, district, risk_level, action, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def create_collection_request(category, district, quantity_range, risk_level, can_wait):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO collection_requests (category, district, quantity_range, risk_level, can_wait, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (category, district, quantity_range, risk_level, 1 if can_wait else 0, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    req_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return req_id

def create_delivery(delivery_code, category, district, point_name, risk_level):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO deliveries (delivery_code, category, district, point_name, risk_level, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (delivery_code, category, district, point_name, risk_level, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    del_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return del_id