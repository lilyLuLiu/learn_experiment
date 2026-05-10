from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection
from sentence_transformers import SentenceTransformer

# 1. 连接 Milvus
connections.connect("default", host="localhost", port="19530")

# 2. 初始化向量化模型 (使用 384 维的小巧模型，适合练习)
model = SentenceTransformer('all-MiniLM-L6-v2')
DIMENSION = 384 

# 3. 定义 Schema (结构)
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=DIMENSION),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=1000)
]
schema = CollectionSchema(fields, "TXT Vectorization Demo")
collection = Collection("txt_collection", schema)

# 4. 读取并处理文本
def process_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text_content = f.read()
    
    # 简单的切片策略：按换行符切分，或者每 200 字切一段
    # 实际应用建议使用更高级的 RecursiveCharacterTextSplitter
    chunks = [line.strip() for line in text_content.split('\n') if len(line.strip()) > 5]
    return chunks

# 5. 向量化并插入
def insert_txt_to_milvus(file_path):
    chunks = process_txt(file_path)
    
    # 将文本转化为向量
    print(f"正在向量化 {len(chunks)} 条文本...")
    vectors = model.encode(chunks).tolist()
    
    # 组织数据 (由于开启了 auto_id，所以不传 ID 列)
    data = [
        vectors,  # embedding 列
        chunks    # text 列
    ]
    
    collection.insert(data)
    collection.flush()
    print("数据插入完成！")

# 6. 创建索引并加载 (搜索前必须)
def prepare_search():
    index_params = {
        "index_type": "HNSW",
        "metric_type": "L2",
        "params": {"M": 8, "efConstruction": 64}
    }
    collection.create_index("embedding", index_params)
    collection.load()

# 执行流程
#file_path = "/Users/lul/log.txt"  # 替换为你的文本文件路径
#insert_txt_to_milvus(file_path) 
#prepare_search()