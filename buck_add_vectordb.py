# from doc_util import Doc
import hashlib
import os
# import asyncio
# import json
import threading
# import websockets
import time
import uuid

import requests
import uvicorn
from fastapi import BackgroundTasks, FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
from langchain import PromptTemplate
from langchain.docstore.document import Document
# from langchain.text_splitter import CharacterTextSplitter
# from langchain.document_loaders import UnstructuredFileLoader
from langchain.embeddings import HuggingFaceEmbeddings
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

import file_utils
# from chains.milvus_doc_qa import MilvusDocQA
from configs.app_config import *
from configs.config import DEVELOPMENT, LLP_DEV, PRODUCTION
from configs.model_config import EMBEDDING_DEVICE, EMBEDDING_MODEL
from db.db_collections import Collections
from db.db_docs import Docs
from db.db_msg import Msg
from db.MySQLDAO import MySQLDAO
from loader.excel_loader import XLSXLoader
from loader.pdf_loader import loadDocsFromPDF
from milvusUtil import add_doc_collection, add_docs, search_go

if os.environ.get("PRODUCTION"):
    config= PRODUCTION
elif os.environ.get("DEVELOPMENT"):
    config= DEVELOPMENT
elif os.environ.get("LLP_DEV"):
    config= LLP_DEV
else:
    config= DEVELOPMENT
    
print(f"current run in {config} mode, embedding_model={config.EMBEDDING_MODEL}")
# embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL, model_kwargs={'device': config.EMBEDDING_DEVICE})
    
def add_to_vectordb(collection_name, pdf_path) :
    if pdf_path:
        docs = loadDocsFromPDF(pdf_path, chunk_size = config.CHUNK_SIZE, chunk_overlap = config.CHUNK_OVERLAP)
        print(f"begin to add pdf_path total docs = {len(docs)}......")
        r = add_docs(embeddings, collection_name, docs)
        print(f"added {pdf_path} to {collection_name}\n\n{r}")
 
    
def bulk_load(dir,collection_name):
    for root, dirs, files in os.walk(dir):
        for f in files:
            fpath = os.path.join(root, dir, f)
            print(f"Begin to add {fpath}......")
            add_to_vectordb(collection_name, fpath)
            print(f"Success......")
            
if __name__ == '__main__':
    # bulk_load("/apps/docs/m3e_base", "m3e_base")
    bulk_load("/apps/docs/text2vec", "text2vec")
    