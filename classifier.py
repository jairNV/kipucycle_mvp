from PIL import Image
import numpy as np

def predict_waste_category(image_file) -> tuple:
    """
    Motor de simulación avanzada para KipuCycle AI.
    Analiza tanto el nombre como los colores reales de los píxeles de la imagen.
    """
    if image_file is None:
        return "No identificado", 0.0
    
    try:
        # 1. Abrir y procesar la imagen real 
        img = Image.open(image_file)
        img_rgb = img.convert('RGB')
        
        # Redimensionar a tamaño pequeño para procesar los colores velozmente
        img_small = img_rgb.resize((50, 50))
        pixels = list(img_small.getdata())
        
        # Calcular los promedios de Rojo (R), Verde (G) y Azul (B)
        r_vals = [p[0] for p in pixels]
        g_vals = [p[1] for p in pixels]
        b_vals = [p[2] for p in pixels]
        
        avg_r = sum(r_vals) / len(pixels)
        avg_g = sum(g_vals) / len(pixels)
        avg_b = sum(b_vals) / len(pixels)
        
        # 2. EVALUACIÓN POR COLOR REAL 
        # El cartón/papel tiende a ser marrón o beige (Rojo alto, Verde medio, Azul bajo)
        if avg_r > 120 and avg_g > 100 and avg_b < 110:
            return "Papel o carton", 0.91
        
        # Las latas de aluminio tienden a ser grisáceas o metálicas (R, G, B muy parecidos y brillantes)
        if abs(avg_r - avg_g) < 15 and abs(avg_g - avg_b) < 15 and avg_r > 100:
            return "Lata metalica", 0.89
            
        # Las pilas o residuos electrónicos suelen tener colores muy oscuros o contrastes vivos
        if avg_r < 60 and avg_g < 60 and avg_b < 60:
            return "Pila o bateria", 0.94

        # 3. EVALUACIÓN POR NOMBRE (Como respaldo por si falla el color)
        filename = getattr(image_file, 'name', '').lower()
        if "botella" in filename or "pet" in filename or "plastico" in filename:
            return "Botella PET", 0.95
        elif "lata" in filename or "metal" in filename or "aluminio" in filename:
            return "Lata metalica", 0.92
        elif "carton" in filename or "papel" in filename or "caja" in filename:
            return "Papel o carton", 0.88
            
        # Por defecto, si es un entorno mixto o transparente (plástico)
        return "Botella PET", 0.82
        
    except Exception:
        # Si ocurre un error leyendo los píxeles, devuelve una clasificación base segura
        return "Botella PET", 0.70
