import hashlib
import logging
import os
import shutil
import sys
import threading
import time
import uuid

from configs.config import DEVELOPMENT, LLP_DEV, PRODUCTION
from db.db_collections import Collections
from db.db_docs import Docs
from db.MySQLDAO import MySQLDAO
from loader.excel_loader import XLSXLoader
from loader.pdf_loader import loadDocsFromPDF
from milvusUtil import add_docs, get_kb_collection_name, search_go

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# 判断当前环境
if os.environ.get("PRODUCTION"):
    config = PRODUCTION
elif os.environ.get("DEVELOPMENT"):
    config = DEVELOPMENT
elif os.environ.get("LLP_DEV"):
    config = LLP_DEV
else:
    config= DEVELOPMENT
    
async def upload_file_handler(embedding_function, dao, collection_name: str, collection:str, file, user: str):
    start = time.time()
    try:
        filename = file.filename.replace(' ', '')
        size = file.size
        data = await file.read()
        temp_file_path = save_tmp(collection_name, filename, data)
        is_succ, msg = file_task(embedding_function, dao, collection_name, collection, temp_file_path, filename)
        if is_succ:
            return {"message": "success", 'time': time.time() - start, 'filename': file.filename}
        else:
            print({"message": msg, 'time': time.time() - start, 'filename': file.filename})
            return {"message": "error", 'time': time.time() - start, 'filename': file.filename}
    except Exception as e:
        print(e)
        return {"message": str(e), 'time': time.time() - start, 'filename': file.filename}

def file_task(embedding_function, dao, collection_name, collection, temp_file_path, filename):
    file_lock = threading.Lock()
    file_lock.acquire()
    status = False
    try:
        doc_type = get_file_extension(filename)
        if doc_type == '.xlsx' :
            load_xlsx(embedding_function, dao, collection_name, collection, temp_file_path, filename)
        else:
            is_succ, msg = load_pdf(embedding_function, dao, collection_name, collection, temp_file_path, filename)
            if is_succ:
                Collections().insert(dao, collection_name)
                doc_id = hashlib.md5((collection_name + '/' + filename).encode('utf8')).hexdigest()
                doc = Docs(collection_name = collection_name, 
                    doc_id = doc_id, 
                    doc_name = filename, 
                    doc_type = 'application/pdf', 
                    size = 0)
                doc.insert(dao)         
    finally:
        file_lock.release()
    return is_succ, msg

def load_pdf(embedding_function, dao, collection_name, collection, temp_file_path, filename):
    pdf_path, pdf_name = save_file(collection_name, temp_file_path, filename)
    docs = loadDocsFromPDF(pdf_path, chunk_size = 1000, chunk_overlap = 50)
    r = add_docs(embedding_function, collection, docs)
    if len(r) >0:
        return(True, f"{filename} added to vectordb!")
    else:
        return(False, f"{filename} Nothing added to VectorDB")


def load_xlsx(embedding_function, dao, collection_name, collection, file_path, filename):
    file_path, file_name = save_file(collection_name, file_path, filename)
    if(file_path):
        loader = XLSXLoader(file_path)
        docs = loader.load()
        r = add_docs(embedding_function, collection, docs)
        docs = []
        r = add_docs(embedding_function, collection + "_QA", docs)
        Collections().insert(dao, collection_name)
        doc_id = hashlib.md5((collection_name + '/' + filename)
                             .encode('utf8')).hexdigest()
        Docs(collection_name = collection_name
             , doc_id = doc_id
             , doc_name = filename
             , doc_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
             , size = os.path.getsize(file_path)).insert(dao)
    else:
        return("Destination file already exists.")

def save_tmp(collection_name, file_name, content: bytes):
    tmp_path = os.path.join(config.TMP_DIR, collection_name)
    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)
    file_tmp_path = os.path.join(tmp_path, file_name)
    print(file_tmp_path)
    with open(file_tmp_path, "wb") as f:
        f.write(content)
    return file_tmp_path
    
def get_file_extension(file_path):
    return os.path.splitext(file_path)[1]
    
def save_file(collection_name, file_path, filename):
    doc_type = get_file_extension(filename)
    data_dir = os.path.join(config.BASE_DOCS_DIR, collection_name)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    if doc_type == '.docx' or doc_type == '.pptx' :
        os.system("docker exec -t libreoffice unoconv --connection 'socket,host=127.0.0.1,port=8100,tcpNoDelay=1;urp;StarOffice.ComponentContext' -f pdf {}".format(file_path))
        filename = filename.rsplit(".", 1)[0] + ".pdf"
    tmp_file_path = os.path.join(config.TMP_DIR, collection_name, filename)
    destination_file = os.path.join(data_dir, filename)
    if not os.path.exists(destination_file):
        shutil.move(tmp_file_path, data_dir)
    
    os.remove(tmp_file_path)
    return destination_file, filename