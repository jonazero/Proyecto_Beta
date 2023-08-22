import random

# Ejemplo de datos de tiempos entre teclas (teclas: a, b, c, d)
data = {
    ('a', 'b'): 100,
    ('b', 'c'): 500,
    ('c', 'd'): 150,
    # ... otros pares de teclas y tiempos
}

# Calcula las probabilidades basadas en los tiempos entre teclas
total_time = sum(data.values())
probabilities = {pair: time / total_time for pair, time in data.items()}

# Genera pares de teclas aleatoriamente utilizando las probabilidades


def generate_random_key_pairs(probabilities, num_pairs):
    key_pairs = []
    for _ in range(num_pairs):
        key_pairs.append(random.choices(
            list(probabilities.keys()), list(probabilities.values()))[0])
    return key_pairs


# Genera 10 pares de teclas aleatoriamente
random_key_pairs = generate_random_key_pairs(probabilities, 1)
print(random_key_pairs)
