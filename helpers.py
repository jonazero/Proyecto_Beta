import json
import random


def json2dic(myfile):
    with open(myfile, encoding='utf-8') as json_file:
        dis = json.load(json_file)
    return dis


def dic2json(myfile, dic):
    with open(myfile, "w", encoding='utf-8') as outfile:
        json.dump(dic, outfile)

def list2Tuples(data):
    # Inicializar una lista de tuplas para almacenar las cuentas y errores para cada clave
    data_structure = []

    # Iterar a través de los datos
    for item in data:
        key = item['key']
        coords = item['coords']
        count = 1

        # Verificar si 'coords' es None (considerado un error)
        if coords is None:
            error_count = 1
        else:
            error_count = 0

        # Verificar si la clave ya está en la estructura de datos
        found = False
        for i, (k, c, e) in enumerate(data_structure):
            if k == key:
                data_structure[i] = (k, c + count, e + error_count)
                found = True
                break

        # Si la clave no está en la estructura de datos, agregar una nueva entrada
        if not found:
            data_structure.append((key, count, error_count))

    # Devolver la estructura de datos
    return data_structure

def lists2TimeTuples(data):
    prev_event = None
    total_time = {}
    pair_count = {}

    for event in data:
        if prev_event is not None:
            key1_coords = prev_event['coords']
            key2_coords = event['coords']
            
            # Verificar si alguna de las teclas tiene coordenadas None y saltar el par si es así
            if key1_coords is not None and key2_coords is not None:
                key_pair = (prev_event['key'], event['key'])
                time_diff = event['time'] - prev_event['time']
                if key_pair in total_time:
                    total_time[key_pair] += time_diff
                    pair_count[key_pair] += 1
                else:
                    total_time[key_pair] = time_diff
                    pair_count[key_pair] = 1
        prev_event = event

    # Calcular el tiempo promedio para pares de teclas iguales y almacenar en tuplas
    average_key_pairs = []
    for key_pair, time_sum in total_time.items():
        count = pair_count[key_pair]
        average_time = time_sum / count
        average_key_pairs.append((key_pair[0], key_pair[1], average_time))

    return average_key_pairs

def generate_chars_probability(teclas_datos, cantidad):
    probabilidades = [(tecla, veces_equivocada / veces_presionada) for tecla, veces_presionada, veces_equivocada in teclas_datos]
    probabilidades.sort(key=lambda x: x[1], reverse=True)
    total_probabilidades = sum(p[1] for p in probabilidades)
    if total_probabilidades == 0:
        return
    probabilidades_normalizadas = [(tecla, probabilidad / total_probabilidades) for tecla, probabilidad in probabilidades]
    
    selecciones = random.choices([p[0] for p in probabilidades_normalizadas], [p[1] for p in probabilidades_normalizadas], k=cantidad)
    return selecciones

def generate_sequences_probability(probability_tuples, num_pairs):
    key_pairs = []
    for _ in range(num_pairs):
        chosen_pair = random.choices(probability_tuples, [p for _, _, p in probability_tuples], k=1)
        key_pairs.append(chosen_pair[0][:2])  # Append the selected key pair
        
    return key_pairs