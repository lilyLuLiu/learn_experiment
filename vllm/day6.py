
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",  # Ollama 的 OpenAI 兼容端点
    api_key="ollama",                      # 任意非空字符串，Ollama 不校验
)


def call_llm(prompt):
    response = client.chat.completions.create(
        model="llama3",
        messages=[
            {"role": "user", "content": prompt}
        ],
        stream=False
    )
    content = response.choices[0].message.content

    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                texts.append(item.get("text", ""))
        return "".join(texts)

    return content

import gradio as gr

def normalize_content(content):
    # 如果已经是字符串
    if isinstance(content, str):
        return content

    # 如果是 list（你现在的情况）
    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                texts.append(item["text"])
        return "".join(texts)

    return str(content)
    
def chat(message, history):
    context = ""
    for msg in history:
        if msg["role"] == "user":
            context += f"User: {msg['content']}\n"
        elif msg["role"] == "assistant":
            context += f"Assistant: {msg['content']}\n"

    context += f"User: {message}\nAssistant:"

    response = call_llm(context)

    return response

#gr.ChatInterface(fn=chat).launch()
