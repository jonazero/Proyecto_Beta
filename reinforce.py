import random

# Define las palabras a utilizar para el entrenamiento
words = ["hola", "adios", "perro", "gato", "casa"]

# Define la función para calcular la recompensa del agente


def get_reward(user_input, target_word):
    if user_input == target_word:
        return 1
    else:
        return -1

# Define la función para que el agente seleccione la siguiente palabra para el usuario


def select_next_word(agent, words):
    # Utiliza la política del agente para seleccionar la siguiente palabra
    selected_word = agent.select_word(words)
    return selected_word

# Define la clase del agente


class Agent:
    def __init__(self):
        self.policy = {}  # Crea un diccionario vacío para la política del agente

    # Define la función para seleccionar la siguiente palabra
    def select_word(self, words):
        # Selecciona aleatoriamente una palabra
        selected_word = random.choice(words)

        # Si la palabra ya está en la política del agente, devuelve la misma palabra
        if selected_word in self.policy:
            return selected_word

        # Si la palabra no está en la política del agente, añádela y devuelve la palabra
        else:
            self.policy[selected_word] = 1
            return selected_word

    # Define la función para actualizar la política del agente con la recompensa obtenida
    def update_policy(self, word, reward):
        self.policy[word] += reward


# Entrena el modelo
agent = Agent()
for i in range(20):
    # Selecciona la siguiente palabra para el usuario
    next_word = select_next_word(agent, words)

    # Solicita la entrada del usuario para la palabra seleccionada
    user_input = input(
        "Escribe la palabra '{}' en el teclado: ".format(next_word))

    # Calcula la recompensa del agente
    reward = get_reward(user_input, next_word)

    # Actualiza la política del agente con la recompensa obtenida
    agent.update_policy(next_word, reward)

# Muestra la política aprendida por el agente
print("Política aprendida por el agente:")
print(agent.policy)
