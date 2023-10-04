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

def lists2TimeTuples(keypress_data):
    # Initialize a dictionary to store time differences for each key pair
    time_diffs = {}

    # Iterate through the list and calculate time differences
    for i in range(1, len(keypress_data)):
        key1 = keypress_data[i - 1]['key']
        key2 = keypress_data[i]['key']
        time1 = keypress_data[i - 1]['time']
        time2 = keypress_data[i]['time']
        diff = time2 - time1

        # Check if this key pair exists in the dictionary
        if (key1, key2) in time_diffs:
            time_diffs[(key1, key2)].append(diff)
        else:
            time_diffs[(key1, key2)] = [diff]

    # Calculate the average time difference for equal key pairs
    averages = {}
    for key_pair, diffs in time_diffs.items():
        if len(diffs) > 1:
            average_diff = sum(diffs) / len(diffs)
            averages[key_pair] = average_diff

    return averages

def generate_chars_probability(teclas_datos, cantidad):
    probabilidades = [(tecla, veces_equivocada / veces_presionada) for tecla, veces_presionada, veces_equivocada in teclas_datos]
    probabilidades.sort(key=lambda x: x[1], reverse=True)
    total_probabilidades = sum(p[1] for p in probabilidades)
    if total_probabilidades == 0:
        return
    probabilidades_normalizadas = [(tecla, probabilidad / total_probabilidades) for tecla, probabilidad in probabilidades]
    
    selecciones = random.choices([p[0] for p in probabilidades_normalizadas], [p[1] for p in probabilidades_normalizadas], k=cantidad)
    return selecciones

def generate_sequences_probability(probabilities, num_pairs):
    key_pairs = []
    keys = list(probabilities.keys())
    probabilities_list = list(probabilities.values())
    
    for _ in range(num_pairs):
        chosen_pair = random.choices(keys, probabilities_list, k=1)
        key_pairs.append(chosen_pair[0])  # Append the selected key (not a list with one element)
    
    return key_pairs