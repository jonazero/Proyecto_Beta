import torch
from transformers import GPT2LMTokenizer, GPT2LMHeadModel

# Set the device to CUDA if available, else use CPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load the tokenizer and model
tokenizer = GPT2LMTokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2').to(device)

# Set the letter constraints
constraints = ['e', 's']

# Generate sentences with the given constraints
while True:
    input_str = input('Enter the starting phrase (or press q to quit): ')
    if input_str.lower() == 'q':
        break

    # Tokenize the input and add the constraints to the end of the tokenized sequence
    input_ids = tokenizer.encode(input_str, return_tensors='pt').to(device)
    constraints_ids = tokenizer.convert_tokens_to_ids(constraints)
    input_ids = torch.cat([input_ids, torch.tensor(
        constraints_ids, device=device).unsqueeze(0)], dim=-1)

    # Generate the output sequence
    output = model.generate(input_ids=input_ids, max_length=50)

    # Decode the output and print the generated sentence
    generated_str = tokenizer.decode(output[0], skip_special_tokens=True)
    print(generated_str)
