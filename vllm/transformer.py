'''
from transformers import pipeline
#pipe = pipeline("text-generation", model="gpt2")

pipe = pipeline("text-generation", model="sshleifer/tiny-gpt2")
res = pipe("Explain LLM in simple words", max_length=50)
print(res)
'''

'''
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("gpt2")

tokens = tokenizer("Hello world")
print(tokens)


text = tokenizer.decode(tokens["input_ids"])
print(text)


from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("gpt2")

import torch

input_ids = torch.tensor([tokens["input_ids"]])

outputs = model(input_ids)
print(outputs.logits.shape)
'''

