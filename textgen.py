from transformers import BloomForCausalLM, BloomTokenizerFast
import torch

# Usar GPU si está disponible, sino usar CPU
torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'

tokenizer = BloomTokenizerFast.from_pretrained("bigscience/bloom-1b1")
model = BloomForCausalLM.from_pretrained("bigscience/bloom-1b1").to(torch_device)

# Añadir un nuevo token especial para usarlo como token de relleno
tokenizer.add_special_tokens({'pad_token': '[PAD]'})

# Lista de textos de inicio para generar oraciones desde ellos
starting_text = ["El", "La", "Mi", "Ella",
                 "Había", "Una", "Su", "Sus", "Ellos", "Las", "Los", "De"]

# Lista de palabras que el modelo debe intentar incluir en las oraciones generadas si es posible
force_flexible = [' gato', ' ciudad', ' libro', "casa"] 


def generateSentences(force_flexible: list, starting_text: list):
    # Convertir las palabras forzadas a ids de entrada para el modelo
    force_words_ids = [tokenizer(
        force_flexible, add_special_tokens=False).input_ids]

    # Convertir los textos de inicio a ids de entrada para el modelo
    input_ids = tokenizer(starting_text, return_tensors="pt", truncation=True, padding=True).to(
        torch_device).input_ids

    # Generar oraciones usando el modelo
    outputs = model.generate(
        input_ids,
        max_length=20,  # Longitud máxima de las oraciones generadas
        # Palabras que el modelo debe intentar incluir si es posible
        force_words_ids=force_words_ids,
        num_beams=5,  # Número de beams para usar en la búsqueda por beams
        no_repeat_ngram_size=2,  # Evitar que el modelo repita n-gramas en el texto generado
        remove_invalid_values=True,  # Eliminar los valores inválidos generados por el modelo
        pad_token_id=tokenizer.pad_token_id,  # Establecer el id del token de relleno
    )

    # Convertir la salida generada a texto y formatearla
    generated_texts = []
    for output in outputs:
        generated_text = tokenizer.decode(output, skip_special_tokens=True)
        # Eliminar cualquier texto después del primer punto
        opt = generated_text.split('.')[0] + '.'
        if len(opt.split()) > 5:
            generated_text = opt
        generated_texts.append(generated_text)

    # Devolver una lista de oraciones generadas
    return generated_texts

print(generateSentences(force_flexible, starting_text))
