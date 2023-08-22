import random

def generate_random_char(teclas_datos, cantidad):
    probabilidades = [(tecla, veces_equivocada / veces_presionada) for tecla, veces_presionada, veces_equivocada in teclas_datos]
    probabilidades.sort(key=lambda x: x[1], reverse=True)
    
    total_probabilidades = sum(p[1] for p in probabilidades)
    probabilidades_normalizadas = [(tecla, probabilidad / total_probabilidades) for tecla, probabilidad in probabilidades]
    
    selecciones = random.choices([p[0] for p in probabilidades_normalizadas], [p[1] for p in probabilidades_normalizadas], k=cantidad)
    return selecciones

def generate_random_pairs(probabilities, num_pairs):
    key_pairs = []
    for _ in range(num_pairs):
        key_pairs.append(random.choices(list(probabilities.keys()), list(probabilities.values()))[0])
    return key_pairs

