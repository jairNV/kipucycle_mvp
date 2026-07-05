from PIL import Image

def predict_waste_category(image_file) -> tuple:
    """
    Simula el motor de clasificacion por IA.
    Analiza la imagen o el nombre del archivo para sugerir una categoria.
    """
    if image_file is None:
        return "No identificado", 0.0
    try:
        img = Image.open(image_file)
        img.verify()
        
        filename = getattr(image_file, 'name', '').lower()
        if "botella" in filename or "pet" in filename or "plastico" in filename:
            return "Botella PET", 0.95
        elif "lata" in filename or "metal" in filename or "aluminio" in filename:
            return "Lata metalica", 0.92
        elif "carton" in filename or "papel" in filename or "caja" in filename:
            return "Papel o carton", 0.88
        elif "pila" in filename or "bateria" in filename:
            return "Pila o bateria", 0.97
        elif "electronico" in filename or "celular" in filename or "mouse" in filename:
            return "Residuo electronico pequeno", 0.91
            
        return "Botella PET", 0.75
    except Exception:
        return "No identificado", 0.0