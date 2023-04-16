from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = GPT2LMHeadModel.from_pretrained(
    "mrm8488/spanish-gpt2").to(torch_device)
tokenizer = GPT2Tokenizer.from_pretrained("mrm8488/spanish-gpt2")

starting_text = ["El", "La", "Mi", "Ella",
                 "Había", "Una", "Hombre", "Mujer", "Un", "Hace"]
force_flexible = ["qu", "us", "f", "am", "b", "p", "m", "a", "ac", "men", "ca"]


def generateSentences(force_flexible: list, starting_text: list, num_sequences: int = 1):
    force_words_ids = [tokenizer(
        force_flexible, add_prefix_space=True, add_special_tokens=False).input_ids]
    input_ids = tokenizer(starting_text, return_tensors="pt").to(
        torch_device).input_ids
    outputs = model.generate(
        input_ids,
        max_length=21,
        force_words_ids=force_words_ids,
        num_beams=10,
        num_return_sequences=num_sequences,
        no_repeat_ngram_size=2,
        remove_invalid_values=True)
    generated_texts = []
    for output in outputs:
        generated_text = tokenizer.decode(output, skip_special_tokens=True)
        generated_text = generated_text.split('.')[0] + '.'
        generated_texts.append(generated_text)
    return generated_texts


generated_sentences = generateSentences(
    force_flexible, starting_text, num_sequences=1)
for sentence in generated_sentences:
    print(sentence)
