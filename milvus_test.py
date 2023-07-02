from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores.milvus import Milvus
MILVUS_HOST = '192.168.50.77'
MILVUS_PORT = 19530
collection_name = 'k7635e3ebfe08'
embeddings = HuggingFaceEmbeddings(model_name="/apps/models/GanymedeNil/text2vec-base-chinese/GanymedeNil_text2vec-base-chinese")
vectordb = Milvus(embedding_function = embeddings, connection_args={"host": MILVUS_HOST, "port": MILVUS_PORT}, collection_name=collection_name)

def add_collection():
    metadata={"page": 0}

