import hashlib
import os
import threading
from typing import Any, Iterable, List, Optional, Tuple

from langchain.document_loaders import UnstructuredFileLoader
from langchain.document_loaders.pdf import PyMuPDFLoader
from langchain.embeddings.base import Embeddings
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Milvus
from pymilvus import (Collection, CollectionSchema, DataType, FieldSchema,
                      MilvusException, connections, utility)

from chains.my_vectordb import My_VectorStore
from configs.config import DEVELOPMENT, LLP_DEV, PRODUCTION
from db.db_docs import Docs
from loader.chinese_text_splitter import (ChineseRecursivePDFSplitter,
                                          ChineseTextSplitter)
from loader.pdf_loader import PyMuPDFOCRLoader

# 判断当前环境
if os.environ.get("PRODUCTION"):
    config = PRODUCTION
elif os.environ.get("DEVELOPMENT"):
    config = DEVELOPMENT
elif os.environ.get("LLP_DEV"):
    config = LLP_DEV
else:
    config= DEVELOPMENT

def add_docs(embedding_function, collection:str, docs) ->List[str]:
    '''
    Add documents to the collection with the given name
    '''
    results = []
    if not connections.has_connection(collection):
        connections.connect(alias=collection, host=config.MILVUS_HOST, port=config.MILVUS_PORT)
    if not utility.has_collection(collection_name=collection, using=collection):
        add_doc_collection(embedding_function, collection)
    try:
        if docs:
            vectordb = Milvus(collection_name= collection, embedding_function= embedding_function, connection_args={"host": config.MILVUS_HOST, "port": config.MILVUS_PORT, "alias": collection})
            results = vectordb.add_documents(docs)
        return results
    except MilvusException as e:
        print(e)
        raise e

def search_go(embedding_function, collection_name, collection, question, expr= None, top_k = 5):
    '''
    Search the collection with the given name and question
    '''
    res1 = search(embedding_function = embedding_function, collection_name = collection, question = question, top_k = top_k, expr = expr)
    res2 = search(embedding_function = embedding_function, collection_name = collection +"_QA", question = question, top_k = top_k, expr = expr)
    return res1, res2
    
    
def search(embedding_function, collection_name, question, top_k= config.VECTOR_SEARCH_TOP_K, expr= None):
    '''
    Search the collection with the given name and question
    '''
    if not connections.has_connection(collection_name):
        connections.connect(alias=collection_name, host=config.MILVUS_HOST, port=config.MILVUS_PORT)
    results = []
    if utility.has_collection(collection_name= collection_name, using= collection_name):
        vectordb = Milvus(collection_name= collection_name
                          , embedding_function= embedding_function
                          , connection_args={"host": config.MILVUS_HOST, "port": config.MILVUS_PORT, "alias": collection_name})
        if expr:
            results = vectordb.similarity_search_with_score(question, top_k, expr=expr)
        else:
            results = vectordb.similarity_search_with_score(question, top_k)
    
    for doc, score in results:
        doc.metadata["score"] = score

    return results




def add_kb_name_collection(embedding_function):
    primary_field = "pk"
    text_field = "text"
    collection_name_field = "collection_name"
    fields = []
    fields.append(
        FieldSchema(text_field, DataType.VARCHAR, max_length=64)
    )
    fields.append(
        FieldSchema(collection_name_field, DataType.VARCHAR, max_length=32)
    )
    fields.append(
        FieldSchema(primary_field, DataType.INT64, is_primary=True, auto_id=True)
    )
    _add_collection(embedding_function= embedding_function, collection_name=config.KB_NAME_COLLECTION, fields=fields)

    


def add_doc_collection(embedding_function, collection_name):
    if not connections.has_connection(collection_name):
        connections.connect(alias=collection_name, host=config.MILVUS_HOST, port=config.MILVUS_PORT)
    # Generate unique names
    primary_field = "pk"
    text_field = "text"
    page_field = "page_numbers"
    file_field = "file_path"
    source_field = "source"
    collection_name = collection_name
    fields = []
    fields.append(
        FieldSchema(file_field, DataType.VARCHAR, max_length=200)
    )
    fields.append(
        FieldSchema(page_field, DataType.VARCHAR, max_length=32)
    )
    fields.append(
        FieldSchema(source_field, DataType.VARCHAR, max_length=200)
    )
    fields.append(
        FieldSchema(text_field, DataType.VARCHAR, max_length=3000)
    )    
    fields.append(
        FieldSchema(primary_field, DataType.INT64, is_primary=True, auto_id=True)
    )
    _add_collection(embedding_function= embedding_function, collection_name=collection_name, fields=fields)

def _add_collection(embedding_function, collection_name, fields):
    '''
    Create a collection with the given name, embeddings,
    '''
    if not connections.has_connection(collection_name):
        connections.connect(alias=collection_name, host= config.MILVUS_HOST, port= config.MILVUS_PORT)
    dim = len(embedding_function.embed_query('test'))
    vector_field = "vector"
    fields.append(FieldSchema(vector_field, DataType.FLOAT_VECTOR, dim=dim))
    schema = CollectionSchema(fields)
    collection = Collection(name=collection_name, schema=schema, using=collection_name)
    # Index parameters for the collection
    index = {
        "index_type": "HNSW",
        "metric_type": "L2",
        "params": {"M": 8, "efConstruction": 64},
    }
    # Create the index
    collection.create_index(vector_field, index)
    connections.disconnect(collection_name)
    


def add_kb_name(embedding_function, collection:str, kb_names, metadatas) ->List[str]:
    '''
    Add documents to the collection with the given name
    '''
    results = []
    if not connections.has_connection(collection):
        connections.connect(alias=collection, host= config.MILVUS_HOST, port= config.MILVUS_PORT)
    vectordb = Milvus(collection_name= collection, embedding_function= embedding_function, connection_args={"host": config.MILVUS_HOST, "port": config.MILVUS_PORT, "alias": collection})
    results = vectordb.add_texts(texts=kb_names, metadatas=metadatas)
    return results

def get_kb_collection_name(embedding_function, query, connection_args = None):
    results = search(embedding_function= embedding_function, collection_name= config.KB_NAME_COLLECTION, question=query)
    doc, score  = results[0]
    print(f"question={query}, get_kb_collection_name return {doc}, score = {score}")
    commection_name_zh = None
    commection_name = None
    if score < config.MAX_SIM_COLLECTION:
        commection_name_zh = doc.page_content
        commection_name = doc.metadata["collection_name"]
    return commection_name_zh, commection_name

    
def get_vectordb(embedding_function, collection_name, connection_args):
    if not connections.has_connection(collection_name):
        connections.connect(alias=collection_name, host= config.MILVUS_HOST, port= config.MILVUS_PORT)
    if not connection_args:
        connection_args = {"host": config.MILVUS_HOST, "port": config.MILVUS_PORT, "alias": collection_name}
    vectordb = My_VectorStore(collection_name= collection_name
                          , embedding_function= embedding_function
                          , connection_args=connection_args)
    return vectordb
    



def test_query():
    collection_name = 'k7635e3ebfe08'
    embedding_function = HuggingFaceEmbeddings(model_name="/apps/models/GanymedeNil/text2vec-base-chinese/GanymedeNil_text2vec-base-chinese", )
    
    vectordb = Milvus(embedding_function = embedding_function, connection_args={"host": config.MILVUS_HOST, "port": config.MILVUS_PORT}, collection_name=collection_name)
    question = "路局如何开展科技创新？"
    expr1 = 'file_path == "/apps/docs/excel测试/（人函〔2019〕10号）关于公布《中国铁路广州局集团有限公司机关一般管理人员管理办法（试行）》的通知.pdf" '
    # expr1 = ""
    results1, results2 = search_go(embedding_function= embedding_function, collection_name=collection_name, question=question)
    for r in results1:
        print(f"result1 =  {len(results1)}")
        print(f"score = {r[1]} file = {r[0].metadata['file_path']} content = {r[0].page_content}")
    
    for r in results2:
        print(f"result2 = {len(results2)}")
        print(f"score = {r[1]} file = {r[0].metadata['file_path']} content = {r[0].page_content}")
    



def test_add_nb():
    embedding_function = HuggingFaceEmbeddings(model_name="/apps/models/GanymedeNil/text2vec-base-chinese/GanymedeNil_text2vec-base-chinese", )
    add_kb_name_collection(embedding_function)
    kb_names = []
    kb_names.append('excel测试')
    metadatas = [{"collection_name":'k7635e3ebfe08'}]
    add_kb_name(embedding_function= embedding_function, collection= config.KB_NAME_COLLECTION, kb_names= kb_names, metadatas = metadatas)    

# if __name__ == '__main__':
    # MILVUS_HOST = '192.168.50.77'
    # MILVUS_PORT = 19530
    # embedding_function = HuggingFaceEmbeddings(model_name="/apps/models/GanymedeNil/text2vec-base-chinese/GanymedeNil_text2vec-base-chinese", )
    # question = "关于人事制度内容有哪些"
    # results = search(embedding_function= embedding_function, collection_name='k7635e3ebfe08', question=question)
    # print(len(results))
