'''
import requests

res = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3",
        "prompt": "give me a example of shell that add two numbers",
        "stream": False
    }
)
print(res.json()["response"])
'''

from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",  # Ollama 的 OpenAI 兼容端点
    api_key="ollama",                      # 任意非空字符串，Ollama 不校验
)

response = client.chat.completions.create(
    model="llama3",
    messages=[
        {"role": "user", "content": "Tell me the difference between Ollama and OpenAI?"}
    ],
    stream=False
)

print(response.choices[0].message.content)
