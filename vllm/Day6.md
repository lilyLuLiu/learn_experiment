很好，来到 Day 6：做一个“真正能用的本地 ChatGPT” 🚀
今天是从“工程能力”走向“产品能力”的关键一步。

## 🧠 Day 6 总目标

今天结束你要有一个：
* ✔ 本地 Chat 界面（像 ChatGPT）
* ✔ 能连续对话（有上下文）
* ✔ 后端调用你的 LLM（Ollama / vLLM）
* ✔ 一个“可以给别人用”的 demo

## 🧭 今日路线（4步）
1. UI：做一个聊天界面
2. 对话记忆（history）
3. 接入 LLM API（Ollama / vLLM）
4. 做成完整聊天系统

## 🟢 Part 1：用 UI 框架做 Chat 界面

推荐两个：
* 简单：Gradio（首选）
* 更像产品：Streamlit

👉 今天先用 Gradio（最快）

#### ✅ 安装
```bash
pip install gradio
```
#### ✅ 最小 Chat UI
```python
import gradio as gr

def chat(message, history):
    return "Hello! You said: " + message

gr.ChatInterface(fn=chat).launch()
```

#### 🎉 你已经有 UI 了
👉 浏览器打开 → 输入 → 返回结果

## 🟡 Part 2：加入“对话记忆”（核心🔥）
#### ❗ 没 history 会怎样？
```
Q1: Who are you?
A1: I am AI

Q2: What did I ask?
A2: ❌ 不知道
```
#### ✅ 加入 history
```python
def chat(message, history):
    context = ""
    for user, bot in history:
        context += f"User: {user}\nAssistant: {bot}\n"

    context += f"User: {message}\nAssistant:"

    return context[-200:]  # 简化处理
```
#### 🧠 核心理解

>LLM 没记忆，所谓“记忆”是你拼 prompt

## 🔵 Part 3：接入 Ollama
#### ✅ 后端调用
```python
import requests

def call_ollama(prompt):
    res = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )
    return res.json()["response"]
```
#### ✅ 接入 UI
```python
def chat(message, history):
    context = ""
    for user, bot in history:
        context += f"User: {user}\nAssistant: {bot}\n"

    context += f"User: {message}\nAssistant:"

    response = call_ollama(context)

    return response
```
## 🟣 Part 4：完整 ChatGPT Demo（🔥关键）
✅ 最终代码（可直接跑）
```python

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

gr.ChatInterface(fn=chat).launch()

```
#### 🎉 到这里你已经实现：
>浏览器聊天 → 调用本地模型 → 返回回答

👉 这就是一个“迷你版 ChatGPT”

## 🧪 今日任务（必须完成）
#### ✔ Task 1：跑 UI
能输入

能返回
#### ✔ Task 2：接入 Ollama
返回真实模型回答
#### ✔ Task 3：多轮对话
问 2 次以上

模型能记住上下文

## 🧠 Day 6 核心认知
#### 1️⃣ ChatGPT 本质
>UI + Prompt + LLM
#### 2️⃣ “记忆”不是模型能力
>是你拼出来的 prompt
#### 3️⃣ 产品 ≠ 模型
👉 模型只是引擎

👉 UI + 逻辑才是产品

## 🚀 你现在的能力（很重要）

你已经可以：

* 本地部署 LLM
* 做 API 服务
* 做 UI
* 做完整应用

👉 这已经是初级 LLM 工程师能力