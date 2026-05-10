## 🧠 RAG 进阶总目标

把你现在的 Demo 升级为：

* 支持 PDF / 长文档
* 更合理的 chunk（避免信息丢失）
* 检索更准（rerank）
* 更稳的 prompt（减少胡说）
* 可扩展（后面接数据库/服务都方便）
## 🧭 架构升级（先看全局）
```
文档 → 清洗 → 分块(chunk) → embedding → 向量库
                                      ↓
用户问题 → embedding → 检索(top-k) → rerank → top-n
                                      ↓
                         prompt拼接（带引用）
                                      ↓
                                 LLM回答
```                                 
## 🟢 Part 1：PDF / 文档加载

推荐：PyPDF2（轻量）
```python
from PyPDF2 import PdfReader

def load_pdf(path):
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text
```
👉 先把 PDF 变成纯文本
## 清洗
清洗 = 把“人类阅读的文档”变成“模型能理解的干净文本”
你从 PDF / 网页拿到的原始文本，通常问题：
* ❌ 页眉页脚重复
* ❌ 换行混乱
* ❌ 空白 / 垃圾字符
* ❌ OCR错误（有些PDF）
* ❌ 表格 / 代码被打乱
#### 常见清洗内容
1. 去噪（最基础）
多个换行 → 一个
多空格 → 一个
2. 去页眉页脚
3. 合并断行
4. 去无意义字符
5. 去重复内容
## 🟡 Part 2：Chunk（最重要🔥）
#### ❗ 为什么要 chunk？
* 文档太长（LLM吃不下）
* embedding 长文本效果差
* 检索粒度太粗
#### ✅ 推荐策略（不是随便切）
```python
def split_text(text, chunk_size=300, overlap=50):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

        start += chunk_size - overlap  # ⭐ 重叠很关键

    return chunks
```
#### 🧠 关键参数
|参数	|作用|
|-|-|
|chunk_size	|200~500（推荐）|
|overlap	|20~50（避免断句）|
## 🔵 Part 3：Embedding（可升级）

基础你用的是：

👉 all-MiniLM-L6-v2

#### 🔥 进阶推荐（更准）

👉 BGE / E5 系列（效果更好）

但先用 MiniLM 完全够

## 🟣 Part 4：Rerank（关键提升准确率🔥）
#### ❗ 问题

FAISS 只做“向量相似度”

👉 不等于“最相关语义”

#### ✅ 解决：rerank
推荐：

>👉 BAAI/bge-reranker-base

从 FAISS 完成初筛后，再进行一轮重排序（Rerank），是提升搜索精度的“黄金组合”。

* Bi-Encoder (双编码器)：将问题和候选文档分别编码成独立向量后，进行快速匹配。它属于“海选”阶段，优点是速度快，但会损失一些细微的语义信息，适合处理千万级文档的初筛。

* Cross-Encoder (交叉编码器)：不预先计算向量，它把(问题, 文档)这对组合在一起，通过一个深层模型同时进行分析和打分，直接给出最终的相关性分数。它就像一位专家，对候选结果进行逐一评审，给出精确分数。


#### 🧪 简单实现
```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("BAAI/bge-reranker-base")

def rerank(query, docs):
    # 创建 (query, document) 对，并计算得分
    pairs = [[query, doc] for doc in docs]
    scores = reranker.predict(pairs)

    ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
    # 将 docs 和 scores 两个列表“拉链式”地组合成一个新的可迭代对象。
    # zip 后相当于 [("文档A", 0.87), ("文档B", 0.12), ("文档C", 0.95)]

    # key=lambda x: x[1]：指定使用每个元组的第二个元素（即分数）作为排序依据。
    # reverse=True：表示降序排列（分数高的在前）。
    # 因此，上面的例子排序后会变成 [("文档C", 0.95), ("文档A", 0.87), ("文档B", 0.12)]

    return [doc for doc, _ in ranked]
```
我们代码中加载的 `BAAI/bge-reranker-base` 是智源研究院 (BAAI) 开源的中英文重排序模型。它的设计目标也很清晰：
* 精度优先：它牺牲了速度，换来了对文档语义的深刻理解
* 架构：基于 XLM-RoBERTa-Base 模型构建，拥有约2.78亿 (278M) 参数，在模型大小和性能间取得了极佳的平衡。
* 双语专长：专门针对中文和英文数据训练，为中英文场景优化



#### 🧠 流程
```
top_k=5（粗筛）
→ rerank
→ 取前2（精筛）
```
## 🟠 Part 5：Prompt 优化（非常重要🔥）
#### ❌ 错误（你之前）
Context: ...

Question: ...
#### ✅ 推荐（加约束）
```python
def build_prompt(query, docs):
    context = "\n\n".join(docs)

    return f"""
You are a helpful assistant.

Answer ONLY based on the provided context.
If the answer is not in the context, say "I don't know".

Context:
{context}

Question:
{query}

Answer:
"""
```
#### 🧠 关键点
* 防止 hallucination
* 提升可控性
## 🔴 Part 6：完整进阶 RAG（核心函数🔥）
```python
def rag_query_advanced(query, top_k=5, top_n=2):
    # 1️⃣ embedding
    q_emb = embed_model.encode([query])

    # 2️⃣ 检索
    D, I = index.search(np.array(q_emb), top_k)
    docs = [chunks[i] for i in I[0]]

    # 3️⃣ rerank
    docs = rerank(query, docs)
    docs = docs[:top_n]

    # 4️⃣ prompt
    prompt = build_prompt(query, docs)

    # 5️⃣ LLM
    return call_llm(prompt)
```
🧪 Part 7：接入你的 Chat UI
```python
def chat(message, history):
    return rag_query_advanced(message)
```
## Part 7: 加入rag后，chat history如何做
#### ❌ 错误做法：把整个 history 都丢进检索
(history + query) → embedding
### Step 1：用 history 改写 query（最重要🔥）
👉 目标：
>把“上下文相关问题” → “独立问题”
#### 🧪 示例
```
历史：
User: What is RAG?
Assistant: ...

当前：
User: How does it work?
```
👉 改写：
```
How does RAG work?
```
#### 方法：用 LLM 做 query rewrite
```python
def rewrite_query(history, query):
    prompt = f"""
Rewrite the user question into a standalone question.

Conversation:
{history}

Question:
{query}

Rewritten question:
"""
    return call_llm(prompt)
```
rewrite可以用同chat一个模型，但效率低。

方案二：直接将所有问题拼接，不rewrite.

方案三：使用小模型专门做 rewrite
### Step 2：用“改写后的 query”做 RAG
#### Prompt 结构（推荐🔥）
```
Conversation History:
...

Context:
...

Question:
...

Answer:
```
#### 🧪 代码
```
def build_prompt(history, query, docs):
    history_text = ""

    for msg in history:
        role = msg["role"]
        content = normalize_content(msg["content"])

        if role == "user":
            history_text += f"User: {content}\n"
        else:
            history_text += f"Assistant: {content}\n"

    context = "\n\n".join(docs)

    return f"""
You are a helpful assistant.

Conversation History:
{history_text}

Context:
{context}

Question:
{query}

Answer:
"""
```
### Step 4：完整流程
```python
def rag_chat(message, history):
    # 1️⃣ 改写 query
    rewritten_query = rewrite_query(history, message)

    # 2️⃣ 检索
    q_emb = embed_model.encode([rewritten_query])
    D, I = index.search(np.array(q_emb), 5)

    docs = [chunks[i] for i in I[0]]

    # 3️⃣ prompt
    prompt = build_prompt(history, message, docs)

    # 4️⃣ LLM
    return call_llm(prompt)
```
### history & RAG 进阶优化（你后面可以做）
#### 1. history 截断
```python
history = history[-5:]
```

👉 防止 prompt 过长

#### 2. history summary

👉 长对话压缩

#### 3. multi-query RAG
👉 多种 query 提升召回

`Multi-Query RAG` 是一种通过生成多个不同角度的查询，来显著提升检索覆盖率和完整性的高级技术
```python
from langchain.retrievers.multi_query import MultiQueryRetriever
```
## 🧠 进阶核心认知（非常重要）
#### ❗ RAG质量 = 3件事
|环节	|重要性|
|-|-|
|chunk	|⭐⭐⭐|
|检索	|⭐⭐⭐|
|prompt	|⭐⭐⭐|
#### ❗ LLM 不是关键

>👉 80% 问题在检索，不在模型

## 🚀 你现在已经达到什么水平？

你已经能做：

* PDF问答
* 私有知识库
* 检索 + rerank
* Prompt控制

👉 这已经是：

🔥 企业级 RAG 初级工程师

## 🔥 下一步（真正高手方向）

如果你继续，我可以带你做：

#### 🚀 进阶1：向量数据库
Milvus

Weaviate

#### 🚀 进阶2：RAG优化
多查询（query expansion）

Hybrid search（BM25 + vector）

rerank优化

memory系统

#### 🚀 进阶3：Agent
自动调用工具

多步推理