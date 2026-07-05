WASTE_CATEGORIES = ["Botella PET", "Lata metálica", "Papel o cartón", "Pila o batería", "Residuo electrónico pequeño"]

WASTE_RULES = {
    "Botella PET": {
        "question": "¿La botella contiene restos de líquido o bebidas?",
        "safe_answer": "No",
        "risk_if_yes": "Amarillo", "risk_if_no": "Verde",
        "instruction_yes": "Vacía el líquido por completo y enjuágala antes de reciclarla.",
        "instruction_no": "¡Excelente! Aplástala y guárdala seca.",
        "can_wait": True
    },
    "Lata metálica": {
        "question": "¿La lata contiene grasas o aceites pegajosos?",
        "safe_answer": "No",
        "risk_if_yes": "Amarillo", "risk_if_no": "Verde",
        "instruction_yes": "Lávala con un poco de detergente para evitar plagas en el centro de acopio.",
        "instruction_no": "Perfecto, colócala directo en el contenedor de metales.",
        "can_wait": True
    },
    "Papel o cartón": {
        "question": "¿El cartón está mojado o manchado con comida/grasa (ej. caja de pizza)?",
        "safe_answer": "No",
        "risk_if_yes": "Amarillo", "risk_if_no": "Verde",
        "instruction_yes": "Recorta las partes limpias. El cartón con grasa va al residuo común.",
        "instruction_no": "Mantén las hojas planas, secas y amarradas.",
        "can_wait": True
    },
    "Pila o batería": {
        "question": "¿La pila está sulfatada, oxidada o hinchada?",
        "safe_answer": "No",
        "risk_if_yes": "Rojo", "risk_if_no": "Amarillo",
        "instruction_yes": "¡Peligro! Manipula con guantes, aíslala en una bolsa plástica y evacúala rápido.",
        "instruction_no": "Guárdala en un recipiente plástico lejos de la luz solar.",
        "can_wait": False
    },
    "Residuo electrónico pequeño": {
        "question": "¿El dispositivo tiene cables expuestos o baterías rotas/infladas?",
        "safe_answer": "No",
        "risk_if_yes": "Rojo", "risk_if_no": "Amarillo",
        "instruction_yes": "Riesgo químico/eléctrico detectado. Llévalo directo al Punto RAEE sin desarmar.",
        "instruction_no": "Puedes acumularlo en un lugar seco hasta su entrega.",
        "can_wait": False
    }
}

def evaluate_waste(category, answer):
    if category not in WASTE_RULES:
        return {"risk_level": "Verde", "instruction": "Dispón según las normas generales.", "can_wait": True}
    rule = WASTE_RULES[category]
    is_safe = (answer == rule["safe_answer"])
    return {
        "risk_level": rule["risk_if_no"] if is_safe else rule["risk_if_yes"],
        "instruction": rule["instruction_no"] if is_safe else rule["instruction_yes"],
        "can_wait": rule["can_wait"] if is_safe else False
    }