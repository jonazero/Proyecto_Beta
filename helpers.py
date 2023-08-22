import json
import random

def json2dic(myfile):
    with open(myfile, encoding='utf-8') as json_file:
        dis = json.load(json_file)
    return dis


def dic2json(myfile, dic):
    with open(myfile, "w", encoding='utf-8') as outfile:
        json.dump(dic, outfile)

def lists2tuples(data):
    key_counts = {}
    key_none_count = {}
    result = []
    for key, coordinates, _ in data:
        key_counts[key] = key_counts.get(key, 0) + 1
        key_none_count[key] = key_none_count.get(key, 0) + (coordinates is None)

    for key in key_counts:
        result.append((key, key_counts[key], key_none_count[key]))
    return result

def lists2TimeTuples(data):
    result = {}
    for i in range(len(data) - 1):
        if data[i][1] is not None and data[i + 1][1] is not None:
            pair = (data[i][0], data[i + 1][0])
            time_difference = data[i + 1][2] - data[i][2]
            if pair in result:
                result[pair] += time_difference
            else:
                result[pair] = time_difference

    return result

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