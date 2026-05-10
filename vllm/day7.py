from sentence_transformers import SentenceTransformer
import day6 as day6
import faiss
import numpy as np
import gradio as gr

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

    index = create_faiss_index(texts, model)

    # 2. 检索
    D, I = index.search(np.array(q_emb), k=2)

    print("I[0]:", I[0])
    docs = [texts[i] for i in I[0]]

    # 3. 拼 prompt
    prompt = build_prompt(query, docs)

    print("==== Retrieved Docs ====")
    for doc in docs:
        print("-", doc)

    print("\n==== Prompt ====")
    print(prompt)

    # 4. 调 LLM
    answer = day6.call_llm(prompt)
    return answer

def chat_with_rag(message, history):
    context = ""
    for msg in history:
        if msg["role"] == "user":
            context += f"User: {msg['content']}\n"
        elif msg["role"] == "assistant":
            context += f"Assistant: {msg['content']}\n"

    context += f"User: {message}\nAssistant:"

    response = rag_query(context)

    return response
#print(rag_query("How to speed up LLM inference?"))

gr.ChatInterface(fn=chat_with_rag).launch()