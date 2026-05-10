from fastapi import FastAPI
from transformers import pipeline

app = FastAPI()

#pipe = pipeline("text-generation", model="distilgpt2")
pipe = pipeline("text-generation", model="gpt2")


@app.get("/chat")
def chat(q: str):
    result = pipe(q, max_new_tokens=50)
    return {"response": result[0]["generated_text"]}


