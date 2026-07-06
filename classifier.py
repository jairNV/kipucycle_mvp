from PIL import Image

def predict_waste_category(image_file) -> tuple:
    """
    Motor de simulación avanzado y tolerante para KipuCycle AI.
    Analiza tanto el nombre como los colores reales (con lógica flexible).
    """
    if image_file is None:
        return "No identificado", 0.0
    
    try:
        # 1. EVALUACIÓN POR NOMBRE (Primera barrera, es la más rápida)
        filename = getattr(image_file, 'name', '').lower()
        if "botella" in filename or "pet" in filename or "plastico" in filename:
            return "Botella PET", 0.95
        elif "lata" in filename or "metal" in filename or "aluminio" in filename:
            return "Lata metalica", 0.92
        elif "carton" in filename or "papel" in filename or "caja" in filename:
            return "Papel o carton", 0.88
            
        # 2. EVALUACIÓN POR COLOR REAL (Para archivos de WhatsApp como IMG-XXXX)
        # Abrir y procesar la imagen real enviada
        img = Image.open(image_file)
        img_rgb = img.convert('RGB')
        
        # Redimensionar a tamaño súper pequeño para procesar los colores velozmente
        img_small = img_rgb.resize((30, 30))
        pixels = list(img_small.getdata())
        
        # Calcular los promedios de Rojo (R), Verde (G) y Azul (B)
        avg_r = sum(p[0] for p in pixels) / len(pixels)
        avg_g = sum(p[1] for p in pixels) / len(pixels)
        avg_b = sum(p[2] for p in pixels) / len(pixels)
        
        # --- LÓGICA DE COLOR OPTIMIZADA ---

        # [REGLA CARTÓN: Tolerante] El cartón tiende a ser marrón/beige (Rojo alto, Verde medio, Azul bajo)
        # Usamos condiciones más flexibles para ignorar blancos/negros parciales.
        if avg_r > 100 and avg_g > 80 and avg_b < 140:
            return "Papel o carton", 0.93

        # [REGLA LATA: Gris brillante] Colores R, G y B muy parecidos y brillantes.
        if abs(avg_r - avg_g) < 20 and abs(avg_g - avg_b) < 20 and avg_r > 150:
            return "Lata metalica", 0.91
            
        # [REGLA ELECTRÓNICO/PILAS: Muy oscuro o contraste]
        if avg_r < 70 and avg_g < 70 and avg_b < 70:
            return "Pila o bateria", 0.94

        # [REGLA PLÁSTICO/TRANSPARENTE] Por defecto, si es un entorno mixto o transparente
        return "Botella PET", 0.82
        
    except Exception:
        # Si ocurre un error leyendo los píxeles, devuelve una clasificación base segura
        return "Botella PET", 0.70
