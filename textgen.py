from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

# Use GPU if available, otherwise use CPU
torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Load pre-trained GPT-2 model and tokenizer for Spanish
model = GPT2LMHeadModel.from_pretrained(
    "mrm8488/spanish-gpt2").to(torch_device)
tokenizer = GPT2Tokenizer.from_pretrained("mrm8488/spanish-gpt2")

# List of starting text prompts to generate sentences from
starting_text = ["El", "La", "Mi", "Ella",
                 "Había", "Una", "Hombre", "Mujer", "Un", "Hace", "De", "Que", "Y", "En", "El", "A", "Los", "Se", "Un", "De", "Las", "Con", "Por"]

# List of words that the model should try to include in the generated sentences if possible
force_flexible = ["quería", "usába", "felíz", "amaba", "usar",
                  "balon", "perico", "mundo", "amor", "acaba", "mentira", "canción", "enfermo"]


def generateSentences(force_flexible: list, starting_text: list):
    # Convert the force words to input ids for the model
    force_words_ids = [tokenizer(
        force_flexible, add_prefix_space=True, add_special_tokens=False).input_ids]

    # Convert the starting text prompts to input ids for the model
    input_ids = tokenizer(starting_text, return_tensors="pt").to(
        torch_device).input_ids

    # Generate sentences using the model
    outputs = model.generate(
        input_ids,
        max_length=40,  # Maximum length of generated sentences
        # Words that the model should try to include if possible
        force_words_ids=force_words_ids,
        num_beams=5,  # Number of beams to use for beam search
        no_repeat_ngram_size=2,  # Prevent the model from repeating n-grams in the generated text
        remove_invalid_values=True  # Remove any invalid values generated by the model
    )

    # Convert the generated output to text and format it
    generated_texts = []
    for output in outputs:
        generated_text = tokenizer.decode(output, skip_special_tokens=True)
        # Remove any text after the first period
        opt = generated_text.split('.')[0] + '.'
        if len(opt.split()) > 5:
            generated_text = opt 
        generated_texts.append(generated_text)

    # Return a list of generated sentences
    return generated_texts


# Generate sentences using the `generateSentences` function and print them
generated_sentences = generateSentences(force_flexible, starting_text)
for sentence in generated_sentences:
    print(sentence)
