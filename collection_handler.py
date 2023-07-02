from fastapi import HTTPException
from typing import List
from chains.query_collection_name import query_collection_name
from milvusUtil import add_docs, search_go, get_kb_collection_name
from db.db_collections import Collections
from db.db_docs import Docs
from db.MySQLDAO import MySQLDAO
from configs.config import DEVELOPMENT, PRODUCTION, LLP_DEV

class Para_Add_Collection:
    pass


async def query_collection(llm, embedding_function, question):
    kb_name = query_collection_name(llm=llm, question=question)
    collection_name_zh = None
    collection_name = None
    if kb_name and len(kb_name) > 0:
        collection_name_zh, collection_name = get_kb_collection_name(embedding_function=embedding_function, query=kb_name)
    return {"collection_name_zh": collection_name_zh, "collection_name": collection_name}


async def get_collection(dao, collection_name):
    if collection_name == None:
        c = Collections.get_all(dao)
    else:
        c = Collections.get_by_collection_name(collection_name=collection_name)
    return {"data": c}

async def get_all_collections(dao):
    c = Collections().get_all(dao)
    return {"data": c}

async def add_collection(dao, para: Para_Add_Collection):
    collection_name = para.dict()['collection_name']
    Collections().insert(dao, collection_name)
    return {"collection_name": collection_name}

async def get_all_docs(dao):
    docs = Docs.get_all(dao)
    return {"data": docs}

async def get_docs_in_collection(dao, collection_name):
    doc_info = Docs("", "", "").get_all_by_collection(dao, collection_name)
    return {"data": doc_info}
