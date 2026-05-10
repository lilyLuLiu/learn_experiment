很好，来到Day 7：RAG（检索增强生成）——这是把“会聊天的模型”变成**能用你自己数据回答问题的系统**的关键一步。

## 🧠 Day 7 总目标

今天结束你要能做一个：

* 上传文档（txt / PDF）
* 自动切分 + 向量化
* 相似度检索
* 把检索结果喂给 LLM 回答
* 集成到你 Day6 的 Chat UI

👉 这就是企业里最常见的“私有知识库问答”。

## 🧭 今日路线（5步）
1. 什么是 RAG（结构理解）
2. 文档 → 向量（Embedding）
3. 向量数据库（FAISS）
4. 检索 + Prompt 拼接
5. 接入你现有 Chat 系统

## 🔴 Part 1：RAG 是什么（核心理解）
#### 🧠 一句话
>RAG = 检索（Retrieve） + 生成（Generate）

#### 📦 流程
```
用户问题
   ↓
向量检索（找相关文档）
   ↓
拼进 prompt
   ↓
LLM 生成答案
```
#### ❗ 为什么需要 RAG？
* LLM 不知道你私有数据
* 微调成本高
* RAG 更简单、更可控

## 🟢 Part 2：文本 → 向量（Embedding）

我们用：

👉 sentence-transformers

### 安装
```bash
pip install sentence-transformers faiss-cpu
```
1. `faiss-cpu`
是一个高效相似性搜索和稠密向量聚类的Python库，是在中央处理器上运行的CPU版本。它与需要NVIDIA GPU的`faiss-gpu`是同一底层库的打包变体，两者核心功能一致。`faiss-cpu`是一个纯CPU的软件包，完全不支持GPU，专为在ARM/macOS/Windows等非NVIDIA CUDA环境运行而设计.

2. `sentence-transformers` 
就是一个“句子翻译机”，把任何句子“翻译”成一串能代表它含义的数字（向量）。它就像给每个句子测一个“语义体温”，测出来的不是36.5°C，而是一串几百个数字（比如 [0.2, -0.5, 0.8, ...]）。这串数字就是句子的“语义指纹”。
```
“我想借一本编程书” → 指纹A
“哪里有 Python 教程？” → 指纹B
“今天天气真好” → 指纹C
```
指纹A 和 指纹B 非常像（因为意思相近），指纹C 和它们差很远。

你不用告诉它规则，它自己从海量数据里学会了：哪些词、哪种结构往往表达相似的意思。


### 代码
```python
from sentence_transformers import SentenceTransformer

# 加载模型，只需这一行！
#    - 若本地无缓存，库会自动从 Hugging Face 官网下载模型文件
model = SentenceTransformer("all-MiniLM-L6-v2")

texts = [
    "LLM deployment involves serving models via APIs",
    "RAG combines retrieval and generation",
]

embeddings = model.encode(texts)

print(embeddings.shape)
```
#### 🧠 输出
>(2, 384)

👉 每段文本 → 384维向量

二维数组可以看作一个表格：2 行（每行对应一句话），384 列（每列是这句话的一个特征数值）。
* 第一维 (2)：表示你输入的 texts 列表中包含 2 个文本（比如两句话或两段话）。
* 第二维 (384)：表示每个文本被模型转换成的向量维度是 384。也就是说，每个句子用一个由 384 个浮点数组成的数组（向量）来表示其语义。

## 🟡 Part 3：向量数据库（FAISS）

我们用：

👉 FAISS
`FAISS`（Facebook AI Similarity Search） 负责的是大规模向量数据的“高效检索”.
索引是FAISS的灵魂，根据数据量和查询模式，FAISS提供了“精确索引”(Flat)和“近似索引” (Approximate)两大流派

### 建索引
```python
import faiss
import numpy as np

dim = embeddings.shape[1] #此处为 384

index = faiss.IndexFlatL2(dim)  # 创建 L2 距离的精确索引
index.add(np.array(embeddings)) # 将向量添加到索引中
```
### 查询
```python
query = "How to deploy LLM?"
q_emb = model.encode([query])  # 将查询转为向量

D, I = index.search(np.array(q_emb), k=2)
# k = 2 , 查找最相似的2个结果

print(I)  # 最相关文本索引
```
## 🔵 Part 4：RAG 拼接 Prompt（核心🔥）
### ❗ 错误方式（你现在的）
```
User: question
```
### ✅ 正确方式（RAG）
```
Context:
<检索到的内容>

Question:
<用户问题>

Answer:
```
### 🧪 代码
```python
def build_prompt(query, docs):
    context = "\n".join(docs)

    return f"""
You are a helpful assistant.

Context:
{context}

Question:
{query}

Answer:
"""
```
## 🟣 Part 5：整合成 RAG 系统
### 🎯 核心函数
```python
def rag_query(query):
    # 1. 向量化
    q_emb = model.encode([query])

    # 2. 检索
    D, I = index.search(np.array(q_emb), k=2)

    docs = [texts[i] for i in I[0]]

    # 3. 拼 prompt
    prompt = build_prompt(query, docs)

    # 4. 调 LLM
    return call_llm(prompt)
```
### 完整代码
```python
from sentence_transformers import SentenceTransformer
from day6 import call_llm
import faiss
import numpy as np

# ===== 1️⃣ 初始化模型 =====
model = SentenceTransformer("all-MiniLM-L6-v2")

# ===== 2️⃣ 知识库（你可以换成文件读取）=====
texts = [
    "LLM deployment involves serving models via APIs",
    "RAG combines retrieval and generation",
    "KV cache improves inference speed",
    "Quantization reduces memory usage of models",
]

def create_faiss_index(texts, model):
    # ===== 3️⃣ 向量化 =====
    embeddings = model.encode(texts)
    # ===== 4️⃣ 建立 FAISS 索引 =====
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    return index

def build_prompt(query, docs):
    context = "\n".join(docs)

    return f"""
You are a helpful assistant.

Use the following context to answer the question.

Context:
{context}

Question:
{query}

Answer:
"""


def rag_query(query):
    # 1. 向量化
    q_emb = model.encode([query])

    # 创建检索
    index = create_faiss_index(texts, model)

    # 2. 进行检索
    D, I = index.search(np.array(q_emb), k=2)

    print("I[0]:", I[0])
    docs = [texts[i] for i in I[0]]

    # 3. 拼 prompt
    prompt = build_prompt(query, docs)

    # debug 查看检索结果
    print("==== Retrieved Docs ====")
    for doc in docs:
        print("-", doc)

    print("\n==== Prompt ====")
    print(prompt)

    # 4. 调 LLM
    answer = call_llm(prompt)
    return answer

print(rag_query("How to speed up LLM inference?"))
```
### 模型使用
这里面使用了两个模型，all-MiniLM-L6-v2和llama3。这个 RAG 里确实用了两个模型，而且这是标准做法，不是冗余
>RAG = 一个“找资料”的模型 + 一个“回答问题”的模型
```
用户问题
   ↓
embedding模型（MiniLM） → 向量
   ↓
FAISS 检索相关文档
   ↓
拼进 prompt
   ↓
LLM（llama3）生成答案
```
## 🟡 下一步优化（你可以马上升级）
#### ✅ 1. 支持文件（而不是写死）
```python
with open("docs.txt") as f:
    texts = f.readlines()
```
#### ✅ 2. chunk（很重要🔥）
```python
def split_text(text, chunk_size=100):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
```
#### ✅ 3. 提高 top_k
```python
rag_query("...", top_k=3)
```
## 🔥 Part 6：接入你的 Chat UI
改 chat()
```python
def chat(message, history):
    return rag_query(message)
```
👉 现在你就是：
>🎉 “基于知识库回答问题”

## 🧪 今日实战任务（必须做）
* Task 1：跑 embedding
输入文本 → 得到向量
* Task 2：FAISS 检索
输入 query → 找到相关文本
* Task 3：拼 prompt
打印 prompt（非常重要）
* Task 4：接入 LLM
输出基于文档的答案

## 🧠 Day 7 核心认知
1️⃣ LLM ≠ 知识库

2️⃣ RAG = “外挂知识”

3️⃣ prompt 是核心控制点

4️⃣ embedding = 语义搜索

## 🚀 你现在的能力（非常重要）

你已经可以做：

✔ 本地 LLM

✔ API 服务

✔ Chat UI

✔ 多轮对话

✔ RAG 系统

👉 这就是：

>🔥 初级 → 中级 LLM 工程师

## 🔥 进阶方向（下一阶段）

如果你继续，我可以带你：

#### 🚀 进阶1
PDF解析（真正生产）

chunking策略优化
#### 🚀 进阶2
向量数据库（Milvus / Weaviate）
#### 🚀 进阶3
Agent（自动调用工具）
