好，进入 Day 4：把模型变成“服务”。从今天开始，你不只是“跑模型的人”，而是开始做LLM 工程系统。

## 🧠 Day 4 总目标

今天结束你要做到：
* ✔ 把本地模型变成 HTTP API
* ✔ 用代码调用（像调用 OpenAI）
* ✔ 理解“LLM 服务架构”
* ✔ 跑一个真正可用的本地 Chat API

## 🧭 今日路线（4步走）
1. LLM ≠ 脚本 → LLM = 服务
2. FastAPI 封装模型
3. 用 Ollama / vLLM 做标准 API
4. 统一成 OpenAI 调用方式
## 🔴 Part 1：关键认知升级（最重要）
❗ LLM 正确用法不是这样：
```python
pipe("Hello")  ❌
```
✅ 而是这样：
```
Client → HTTP API → LLM → 返回结果
```
🧠 为什么？
* 模型很大（不能每次加载）
* 需要并发处理
* 要给前端 / 其他服务调用

## 🟢 Part 2：用 FastAPI 把模型变成服务
#### 1️⃣ 安装
```bash
pip install fastapi uvicorn transformers torch
```
#### 2️⃣ 写最小服务
```python
from fastapi import FastAPI
from transformers import pipeline

app = FastAPI()

pipe = pipeline("text-generation", model="distilgpt2")

@app.get("/chat")
def chat(q: str):
    result = pipe(q, max_new_tokens=50)
    return {"response": result[0]["generated_text"]}
```
#### 3️⃣ 启动
```bash
uvicorn app:app --reload
```
#### 4️⃣ 调用
```bash
curl "http://127.0.0.1:8000/chat?q=hello"
```
#### 🧠 你刚刚完成了
🎉 第一个 LLM API 服务

#### Uvicorn
Uvicorn是一个基于 uvloop 和 httptools 构建的 闪电般快速的 ASGI 服务器，为 Python 异步 Web 框架而生。你可以把它看作运行现代异步 Python Web 应用的核心引擎。
##### 🚀 核心概念：理解 ASGI
要理解 Uvicorn，首先需要明白 ASGI 是什么。
* WSGI 的局限：传统的 WSGI 标准是同步的。当一个请求处理时，服务器进程会被“阻塞”，必须等这个请求完全处理完，才能处理下一个。这对需要长时间等待数据库查询或网络响应的 I/O 密集型任务效率不高。

* ASGI 的革新：ASGI 是 WSGI 的异步继承者，它引入了异步/等待 (async/await) 范式，让服务器在等待 I/O 操作时可以去处理其他请求，从而极大地提升了单进程的并发能力。

##### ⚙️ 核心特性：Uvicorn 为何如此之快？
Uvicorn 的高性能主要归功于其核心技术栈：

* uvloop：uvloop 是标准库 asyncio 事件循环的直接替代品，基于 Cython 实现，速度比默认的 asyncio 快 2-4 倍。

* httptools：httptools 是 node.js 中 HTTP 解析器的 Python 实现，用于高速解析 HTTP 协议，显著提升请求处理效率。

## 🟡 Part 3：用 Ollama（更真实生产方式）
#### 1️⃣ 启动模型
```bash
ollama run llama3
```
#### 2️⃣ HTTP 调用
```python
import requests

res = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3",
        "prompt": "Explain LLM deployment",
        "stream": False
    }
)

print(res.json()["response"])
```
#### 🧠 优势
* 不用自己管理模型加载
* 已经优化推理
* 更接近生产

## 🔵 Part 4：用 vLLM（高性能🔥）
#### 1️⃣ 安装
```bash
pip install vllm
```
#### 2️⃣ 启动 OpenAI API
```bash
python -m vllm.entrypoints.openai.api_server \
  --model mistralai/Mistral-7B-Instruct
```
命令本身在本地运行，不强制要求网络连接。是否联网取决于你的 --model 参数：
* 无需联网：如果 --model 指向的是本地路径，或模型已存在于 Hugging Face 缓存中。
* 需要联网：如果模型在本地不存在，且指定了 Hugging Face 模型ID，vLLM 会尝试联网下载。默认的 Hugging Face 缓存目录 (~/.cache/huggingface/) 可能占用系统盘空间。

>注意：python -m vllm.entrypoints.openai.api_server 是旧版方式，新版本中已统一为 vllm serve。
#### 3️⃣ 调用（OpenAI格式）
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="test"
)

resp = client.chat.completions.create(
    model="mistral",
    messages=[{"role": "user", "content": "Explain LLM"}]
)

print(resp.choices[0].message.content)
```
#### 🧠 关键点

vLLM = 高性能 + OpenAI兼容

## Ollama VS vLLM
vLLM 是一条为高负载、低延迟场景设计的“性能赛道”，而 Ollama 则是为快速上手和灵活开发打造的“便捷通道”。

它们并非简单的优劣之分，而是针对不同问题域的优秀解决方案。下面的表格可以帮你快速理解它们的核心差异：

|对比维度	|vLLM (通过 vllm serve)	|Ollama|
|-|-|-|
|核心理念	|高性能、可扩展的生产级推理引擎	|开箱即用、用户友好的本地化开发工具|
|性能表现	|高吞吐量，高并发下延迟更低	|低负载场景下首字延迟有优势，单次交互响应快|
|并发能力	|极高，专为高并发（>32）设计	|有限，适合个人或小团队低并发场景|
|硬件支持	|主要为 NVIDIA GPU 优化，支持多卡并行	|广泛，支持CPU、NVIDIA、AMD、Apple Silicon（Mac）|
|易用性	|较复杂，需配置Python环境、CUDA等	|非常简单，提供预编译二进制文件，一条命令即可安装|
|模型格式	|原生支持Hugging Face模型（如Safetensors）	|主打GGUF量化格式，官方和社区提供丰富模型库|
|API兼容性	|提供与 OpenAI API 高度兼容 的服务接口	|同样提供 OpenAI 兼容的 API 接口|
|最佳场景	|企业级应用、高并发API服务、对延迟和吞吐量有严格要求的场景	|个人开发者、快速原型验证、边缘计算、需要在Mac上运行的场景|

* vLLM：追求极致性能的“赛车”：它的设计初衷就是为了在高负载下榨干每一分算力。其核心创新 PagedAttention 技术大幅提升了GPU内存利用率，实现了2-24倍的吞吐量提升。这使得它能从容应对每秒处理数千个请求的企业级服务，在Red Hat的测试中，高并发下吞吐量甚至能达到Ollama的19倍以上。

* Ollama：主打开箱即用的“自行车”：它就像一个一站式的模型商店和运行环境，专为让开发者能在几分钟内跑起模型而设计。你无需关心底层CUDA或Python环境，简单的 ollama run 命令就能完成下载和运行。这也让它特别适合原型验证、本地开发或个人使用。

## 🟣 Part 5：统一调用接口（非常重要🔥）
#### ollama使用openAI格式
```python 
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",  # Ollama 的 OpenAI 兼容端点
    api_key="ollama",                      # 任意非空字符串，Ollama 不校验
)

response = client.chat.completions.create(
    model="llama3",
    messages=[
        {"role": "user", "content": "Explain LLM deployment"}
    ],
    stream=False
)

print(response.choices[0].message.content)
```
#### 你最终应该做到：
```python
def call_llm(prompt):
    return client.chat.completions.create(...)
```
#### 🧠 为什么？

以后你可以随便换：

* Ollama
* vLLM
* OpenAI
* Azure

👉 代码不用改

## 🧪 今日实战任务（必须完成）
#### ✔ Task 1：FastAPI 服务
能启动
能 curl 调用
#### ✔ Task 2：调用 Ollama API
成功返回结果
#### ✔ Task 3：统一接口

写一个函数：

def chat(prompt):
    ...
## 🧠 Day 4 核心认知
1️⃣ LLM = 服务，不是函数

2️⃣ 推理 ≠ 调用

模型推理（内部）

API调用（外部）

3️⃣ OpenAI API = 行业标准

4️⃣ Ollama / vLLM = 本地替代

#### 🚀 你现在的能力升级

你已经从：
写脚本的人

升级为：
能做 AI 服务的人