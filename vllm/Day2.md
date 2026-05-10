好，Day 2 是整个学习里最关键的一天——从“会用工具”过渡到“理解模型是怎么跑的”。我帮你拆成可执行步骤 + 原理 + 常见坑 + 验收标准。

## 🧠 Day 2：Hugging Face + 手写推理（深入版）
🎯 今日目标（必须完成）

你今天结束时应该能：

✔ 用 Hugging Face + PyTorch 跑模型
✔ 理解 tokenizer / 推理流程
✔ 能控制输出（长度 / 风格）
✔ 知道“模型到底在干嘛”
## 一、环境准备（10分钟）
```bash
pip install transformers torch accelerate
```

可选（更快下载模型）：
```bash
pip install huggingface_hub
```
## 二、最简单推理（先跑起来）
```python
from transformers import pipeline

pipe = pipeline("text-generation", model="gpt2")

res = pipe("Explain LLM in simple words", max_length=50)
print(res)
```
🔍 你要观察
* 输出是“续写”，不是回答
* 每次结果不一样（随机性）
* prompt 很重要
## 三、深入：拆解 pipeline（核心🔥）

pipeline 帮你做了 3 件事：

>输入文本
  ↓
tokenizer（分词 → 数字）
  ↓
model（推理）
  ↓
decode（数字 → 文本）

#### 1️⃣ tokenizer（必须理解）
```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("gpt2")

tokens = tokenizer("Hello world")
print(tokens)
```

你会看到类似：
```json
{
  'input_ids': [15496, 995],
  'attention_mask': [1, 1]
}
```
###### 📌 关键理解
* LLM 不认识文字，只认识数字
* token ≠ 单词（可能是子词）
#### 2️⃣ 手动 decode
```python
text = tokenizer.decode(tokens["input_ids"])
print(text)
```
#### 3️⃣ model forward（真正推理）
```python
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained("gpt2")

import torch

input_ids = torch.tensor([tokens["input_ids"]])

outputs = model(input_ids)
print(outputs.logits.shape)
```
📌 你要理解
logits = 每个词的概率分布
模型是在“猜下一个词”
## 四、自己实现“生成一句话”（核心突破🔥）
```python
import torch

input_text = "The future of AI is"
input_ids = tokenizer(input_text, return_tensors="pt").input_ids

for _ in range(20):
    outputs = model(input_ids)
    next_token_logits = outputs.logits[:, -1, :]
    
    next_token = torch.argmax(next_token_logits, dim=-1)
    
    input_ids = torch.cat([input_ids, next_token.unsqueeze(0)], dim=1)

print(tokenizer.decode(input_ids[0]))
```
##### 📌 这一段非常重要

你刚刚实现了：
>❗ 一个“最小版 ChatGPT”

## 五、控制输出（让模型“听话”）
#### 1️⃣ 控制长度
```python
pipe("Hello", max_length=100)
```
#### 2️⃣ 控制随机性（temperature）
```python
pipe("Hello", temperature=0.1)
```
|参数|	效果|
|-|-|
|低 temperature	|更稳定|
|高 temperature	|更发散|
#### 3️⃣ top-k / top-p
```python
pipe("Hello", top_k=50, top_p=0.9)
```
##### 1. 核心概念：采样 (Sampling)
模型在预测下一个词时，会给词汇表里所有词打分。如果不加干预，模型可能会选一个概率只有 0.0001% 的离谱词。top_k 和 top_p 就是两道过滤网。

##### 2. top_k=50 (截断前 K 个)
原理：只保留概率最高的 50 个词。

作用：把那些概率极低的“长尾”词直接扔掉，防止模型蹦出完全不通顺的胡言乱语。

效果：如果模型本来想说 "Hello, how are..."，它会在前 50 个候选词里挑选。

##### 3. top_p=0.9 (核采样 / Nucleus Sampling)
原理：这是一种动态过滤器。它会将所有词按概率从高到低排序，然后逐个累加，直到总概率达到 0.9 (90%) 为止。只在这个范围内的词里挑选。

为什么更好：

如果模型很确定（比如 "New York" 后面大概率接 "City"），符合条件的词可能只有 1-2 个。

如果模型很犹豫，符合条件的词可能会有成百上千个。

top_p 能根据上下文的确定性自动调整候选池的大小。

##### 4. 两者结合的效果
当你同时设置 top_k=50 和 top_p=0.9 时：

模型先选出概率最高的前 50 个词（top_k 过滤）。

在这 50 个词中，再次筛选出那些加起来概率达到 90% 的词（top_p 二次过滤）。

最后，从剩下的“精华”候选词中随机抽一个。
##### 📌 核心理解

模型不是“思考”，而是：
>在概率空间中采样

## 六、换一个更强模型（重要）

试试：
```python
pipe = pipeline(
    "text-generation",
    model="mistralai/Mistral-7B-Instruct",
    device_map="auto"
)
```
##### ⚠️ 常见问题
❌ OOM（爆显存）

解决：
```python3
model="gpt2"  # 先用小模型
```
或：
```python
device_map="cpu"
```
这行代码是一个资源配置指令。它告诉 Hugging Face 的库（通常是 from_pretrained 加载模型时）：“不管我的电脑里有没有显卡（GPU），请强制把这个庞大的模型装载到中央处理器（CPU）的内存里。”
通常情况下，我们希望模型跑在显卡（CUDA/GPU）上，因为显卡处理矩阵运算快得惊人。但在以下几种情况，你会用到这个设置：

* 没有显卡：如果你的电脑只有集成显卡或纯 CPU，不加这一行，有些代码可能会因为找不到 cuda 设备而报错。

* 显存不足（OOM）：模型的体积（比如 7B 参数的模型大约需要 14GB-28GB 显存）超过了显卡的承受能力，只能退而求其次，利用电脑通常更大的内存（RAM）。

* 稳定性调试：在排查模型逻辑错误时，CPU 环境往往比复杂的 GPU 并行环境更容易观察和捕获错误。
## 七、对比 Ollama vs Transformers（理解架构）
|对比	|Ollama	|Transformers|
|-|-|-|
|使用难度|	简单|	中等|
|控制能力|	低|	高|
|适合	|快速体验	|开发|

## 八、今天必须搞懂的3个核心概念
#### 1️⃣ Token
* 输入输出单位
* 影响成本/性能
#### 2️⃣ Logits → 概率
模型输出：
```
[“cat”:0.3, “dog”:0.2, “car”:0.01]
```
#### 3️⃣ 自回归生成（最重要🔥）
>输入 → 输出一个词 → 拼接 → 再输入 → 再生成

## 九、今日验收标准（一定要做到）

你可以检查自己：
* ✔ 能解释 tokenizer 是什么
* ✔ 能解释 logits 是什么

>Logits 是模型输出的“半成品”。它是神经网络最后一层产生、但尚未经过概率归一化的原始分数值。
* ✔ 能写一个 for-loop 生成文本
* ✔ 能调 temperature 改输出风格
* ✔ 知道为什么每次输出不同
## 十、加分任务（拉开差距🔥）

如果你想比别人更强，做这个：

👉 用 prompt 控制模型
```python
prompt = """
You are a helpful AI assistant.
Answer clearly:

Q: What is LLM?
A:
"""
```
👉 观察变化
你会发现：
>prompt = 编程语言

🚀 如果你下一步要更快进阶

我可以帮你继续细化 Day 3（最关键理解）：

显存计算公式（面试必问）
KV cache 原理（性能核心）
为什么 vLLM 比 HF 快 10 倍
量化为什么能省显存