from pymilvus import *
import insert_txt_to_milvus

# 1. 连接 Milvus
connections.connect("default", host="localhost", port="19530")

collection_names = utility.list_collections()
print("当前 Milvus 中的集合:", collection_names)

collection = Collection("txt_collection")


collection.load()

user_query = "mac1"
query_vectors = insert_txt_to_milvus.model.encode([user_query]).tolist()

results = collection.search(
    data=query_vectors,
    anns_field="embedding",
    param={"metric_type": "L2", "params": {"ef": 64}},
    limit=3,
    output_fields=["text"]
)

for hit in results[0]:
    print(hit.entity.get("text"))
