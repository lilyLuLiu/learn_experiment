好，Day 5 是整个路线里最像“工程师水平”的一天。前面你已经能跑、能服务化了，今天解决一个核心问题：

❗ 为什么你的 LLM 慢 / 吃显存 / 扛不住并发？

## 🧠 Day 5 总目标（工程核心）

今天结束你要能：
* 理解 KV Cache 如何提升速度
* 理解 batch inference（吞吐 vs 延迟）
* 知道为什么 vLLM 比普通推理快很多
* 能做简单性能优化（不再“傻跑模型”）
* 理解 GPU 利用率问题

## 🧭 今日路线
1. 推理为什么慢（本质）
2. KV Cache（速度核心🔥）
3. Batch 推理（吞吐核心）
4. vLLM 为什么快（工程秘密）
5. 实战优化（你可以立刻做）
## 🔴 Part 1：为什么 LLM 推理慢？
#### ❗ 核心问题
生成一句话：
>Hello → token1 → token2 → token3 ...

👉 每一步都要：
>完整 forward 一次模型
#### 🧠 时间复杂度（直觉版）
>长度 N → 计算量 ~ N²
#### ❗ 没优化时
|token数	|计算量|
|-|-|
|10	|100|
|100	|10000|

👉 越生成越慢（你应该已经感觉到了）

## 🟢 Part 2：KV Cache（速度核心🔥）
#### ❗ 没 KV Cache
每次都：
>重新计算所有历史 token

#### ✅ 有 KV Cache
只计算：
>新 token + 历史缓存

#### 🧠 原理（简化）

在 attention 中：

>Q（当前） × K（历史） → V

👉 K / V 可以缓存！

#### 🚀 效果
|模式	|速度|
|-|-|
|无 cache	|慢|
|有 cache	|快 10~20倍|

#### 🧪 你要知道的点
* transformers 默认开启 KV cache
* 但不同框架实现效率差很多

## 🟡 Part 3：Batch 推理（吞吐核心）
#### ❗ 问题

一次只处理一个请求：
```
用户1 → GPU
用户2 → 等待
用户3 → 等待
```
👉 GPU 很空闲

#### ✅ Batch 推理
```
用户1
用户2  → 一起跑
用户3
```
#### 🧠 本质

>GPU 更擅长“大批量计算”

#### ⚠️ trade-off
|指标	|影响|
|-|-|
|吞吐（QPS）	|↑|
|单个请求延迟	|↑|

## 🔵 Part 4：为什么 vLLM 快（核心理解🔥）
🚀 vLLM 的 3 个关键优化
#### 1️⃣ PagedAttention（最重要🔥）
👉 把 KV cache 做成“虚拟内存”
好处：
* 避免显存碎片
* 支持更多并发
* 动态分配
#### 2️⃣ Continuous batching（连续批处理）

👉 请求不是“等一批再跑”，而是：
>新请求随时加入 batch

#### 3️⃣ 高效 CUDA kernel

👉 底层算子优化
#### CUDA介绍
CUDA 就像是给 NVIDIA 显卡量身打造的“神经中枢”，一个能让 GPU 的计算潜力得以尽情释放的并行计算平台和编程模型。NVIDIA CUDA的诞生，让GPU不再局限于图形处理，而是成为强大的通用计算引擎。

一个典型的CUDA程序遵循异构计算模型：
1. 在CPU上执行主机代码。
2. 将需要大量计算的数据从内存复制到GPU的显存。
3. 在GPU上启动内核，这是CUDA程序的核心，由GPU上的大量线程并行执行。
4. 将计算结果从GPU显存复制回内存。

CUDA利用GPU内部的流式多处理器（SM） 来执行这些并行任务，每个SM就像一个小型处理中心，包含自己的计算核心和共享内存。



#### 🧠 一句话总结

>vLLM = KV cache + 动态 batching + 显存管理

## 🟣 Part 5：实战优化（你现在就能做）
#### ✅ 优化 1：减少 max_new_tokens
```python
max_new_tokens=50  # 不要默认256
```
👉 直接减少计算量

#### ✅ 优化 2：控制 temperature
```python
temperature=0.7
```
👉 更稳定，减少无效生成

#### ✅ 优化 3：限制并发（非常关键）

FastAPI 示例：
```python
import asyncio

semaphore = asyncio.Semaphore(2)

async def chat(q):
    async with semaphore:
        return pipe(q)
```
👉 防止 GPU 被打爆

#### ✅ 优化 4：用 Ollama / vLLM 替代 HF

👉 不要自己硬写推理服务（除非学习）

## 🧪 今日实验（必须做）
#### ✔ 实验1：对比速度
```python
time pipe("Hello", max_new_tokens=50)
time pipe("Hello", max_new_tokens=200)
```
👉 观察差异

#### ✔ 实验2：并发测试

用 curl 多次请求：
```bash
for i in {1..5}; do curl ... & done
```
👉 看响应时间

#### ✔ 实验3：Ollama vs HF

👉 对比响应速度

## 🧠 Day 5 核心认知（必须掌握）
#### 1️⃣ LLM 慢的根本原因
逐 token 生成 + attention 复杂度
#### 2️⃣ KV Cache = 推理加速核心
#### 3️⃣ Batch = 吞吐优化核心
#### 4️⃣ vLLM = 工程优化集合体
#### 5️⃣ GPU 利用率 ≠ 100%（默认很低）

## 🚀 你现在的能力

你已经可以：
* ✔ 搭建 LLM 服务
* ✔ 理解性能瓶颈
* ✔ 做基础优化
* ✔ 选择正确推理框架