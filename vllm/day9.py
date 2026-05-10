from pymilvus import *
import random

connections.connect("default", host="localhost", port="19530")

# 1. 定义字段
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=500),
]
# 2. 定义 Schema
schema = CollectionSchema(fields)
# 3. 创建 Collection
collection = Collection("rag_demo", schema)


# 准备 10 条伪造数据
data = [
    ["Title_" + str(i) for i in range(10)], # title 字段
    [[random.random() for _ in range(384)] for _ in range(10)] # vector 字段
]

# 插入数据
collection.insert(data)

# 将 Collection 加载到内存（检索前必须执行）
collection.load()

# 创建索引
index_params = {
    "index_type": "HNSW",  # 索引算法：HNSW 性能更好，IVF 内存占用更平衡
    "metric_type": "L2",   # 度量方式：L2 (欧氏距离) 或 IP (内积)
    "params": {"M": 8, "efConstruction": 64}
}

collection.create_index("my_fast_index", index_params)
#collection.create_index(field_name="vector", index_params=index_params)

#collection.load()

results = collection.search(
    data=q_emb.tolist(),
    anns_field="embedding",
    param={"metric_type": "L2", "params": {"ef": 64}},
    limit=3,
    output_fields=["text"]
)

for hit in results[0]:
    print(hit.entity.get("text"))
