import asyncio
import hashlib
import os
import threading
import time
import uuid

import requests
import uvicorn
from fastapi import (BackgroundTasks, Depends, FastAPI, File, HTTPException,
                     Request, UploadFile)
from fastapi.responses import FileResponse
from fastapi.security import (HTTPAuthorizationCredentials, HTTPBasic,
                              HTTPBasicCredentials, HTTPBearer,
                              OAuth2PasswordRequestForm)
from fastapi.staticfiles import StaticFiles
from langchain import PromptTemplate
from langchain.chains import (ConversationalRetrievalChain,
                              RetrievalQAWithSourcesChain)
from langchain.chains.llm import LLMChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores.base import VectorStoreRetriever
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import Response

import file_utils
import milvusUtil as milvus
from chains.condense_quest_prompt import CONDENSE_QUESTION_PROMPT_ZH
from chains.my_vectordb import My_VectorStore
from chains.qa_refine_prompt import (DEFAULT_REFINE_PROMPT,
                                     DEFAULT_TEXT_QA_PROMPT, EXAMPLE_PROMPT)
from chains.query_collection_name import query_collection_name
from chat_with_vectordb import chat_with_vectordb
from collection_handler import (add_collection, get_all_collections,
                                get_all_docs, get_collection,
                                get_docs_in_collection, query_collection)
from configs.config import DEVELOPMENT, LLP_DEV, PRODUCTION
from db.db_collections import Collections
from db.db_docs import Docs
from db.db_msg import Msg
from db.db_users import Users
from db.MySQLDAO import MySQLDAO
from file_handling import upload_file_handler
from loader.excel_loader import XLSXLoader
from loader.pdf_loader import loadDocsFromPDF
from milvusUtil import add_docs, get_kb_collection_name, search_go
from models.glm_api_client import glm_api_client as glm_cli
from models.glm_llm import glm_llm
from search_with_vectordb import qa_vectordb, query_vectordb
from security import api_security

app = FastAPI()

'''
    初始化
    dao
    LLM
    embedding_function
'''
# 判断当前环境
if os.environ.get("PRODUCTION"):
    config = PRODUCTION
elif os.environ.get("DEVELOPMENT"):
    config = DEVELOPMENT
elif os.environ.get("LLP_DEV"):
    config = LLP_DEV
else:
    config= DEVELOPMENT
print(f"current run in {config} mode")

if not os.path.exists(config.BASE_DOCS_DIR):
    os.makedirs(config.BASE_DOCS_DIR)
    
embedding_function = HuggingFaceEmbeddings(
    model_name=config.EMBEDDING_MODEL, model_kwargs={'device': config.EMBEDDING_DEVICE})

os.environ["OPENAI_API_BASE"] = config.LLM_URL
os.environ["OPENAI_API_KEY"] = "EMPTY"

from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(model=config.LLM_MODEL)
# llm = glm_cli()

app.add_middleware(
    SessionMiddleware,
    secret_key="key12345678",
    session_cookie="session",)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 设置允许的origins来源
    allow_credentials=True,
    allow_methods=["*"],  # 设置允许跨域的http方法，比如 get、post、put等。
    allow_headers=["*"])  # 允许跨域的headers，可以用来鉴别来源等作用。


@app.middleware("http")
async def http_middleware(request: Request, call_next):
    response = await call_next(request)
    session = request.cookies.get('session')
    if session:
        response.set_cookie(
            key='session', value=request.cookies.get('session'), httponly=True)
    return response


# 创建一个全局的Semaphore实例
semaphore = asyncio.Semaphore(config.MAX_API_COENNECTION_LIMITE)
# 限制前端的连接数
async def connection_limiter(request: Request, call_next):
    async with semaphore:
        response = await call_next(request)
    return response


app.middleware("http")(connection_limiter)


class Para_Add_Collection(BaseModel):
    collection_name: str


class Para_Search(BaseModel):
    collection_name: str
    collection: str
    file_name: str
    question: str


# 定义一个依赖项来检查并获取身份验证令牌
auth_scheme = HTTPBearer()
security = HTTPBasic()

# 定义一个权限检查函数
def check_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """
    This function checks the credentials of a user.

    Args:
        credentials (HTTPBasicCredentials, optional): An instance of HTTPBasicCredentials class 
        which holds the username and password provided by the user. 
        Defaults to Depends(security) which is an instance of HTTPBasic class.

    Raises:
        HTTPException: If the credentials are not valid, it raises an HTTPException with a status code of 401.

    Returns:
        bool: Returns True if the credentials are valid, otherwise it raises an HTTPException.
    """

    # 在这里验证用户名和密码
    if credentials.username == "user" and credentials.password == "password":
        return True
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")

# 定义一个中间件来处理静态文件请求
class StaticFilesAuthorizationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/static"):
            try:
                # 在访问静态文件之前检查权限
                await check_credentials(request)
            except HTTPException as e:
                return Response(status_code=e.status_code, content=e.detail)
        return await call_next(request)

# 将中间件添加到应用程序中
# app.add_middleware(StaticFilesAuthorizationMiddleware)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    return api_security.authenticate_user(credentials.credentials)

# app.mount("/static", StaticFiles(directory=BASE_DOCS_DIR), name="static")
app.mount("/static", StaticFiles(directory=config.BASE_DOCS_DIR), name="static")


class UserModel(BaseModel):
    username: str = ""
    password: str = ""

class UserToken(BaseModel):
    code: int = 0
    access_token: str = Field(description='本次登录的token')
    token_type: str = Field(
        default='Bearer', description='token的类型，统一为 Bearer')


@app.post("/login", response_model=UserToken)
async def login_for_access_token(usermodel: UserModel, dao_instance= Depends(MySQLDAO.get_dao)):
    user_name = usermodel.username
    password = usermodel.password

    user_list = Users.get_by_name(dao_instance, username=user_name)
    print(user_list)
    user_valid = False
    if len(user_list) > 0:
        user = user_list[0]
        if user["user_name"] == user_name and user["password"] == password:
            user_valid = True
    # user_valid =  api_security.authenticate_user(username= user_name , password= password)

    if user_valid:
        access_token_expires = api_security.timedelta(minutes=120)
        access_token = api_security.create_access_token(
            data={"sub": "admin"}, expires_delta=access_token_expires)
        return UserToken(code=0, access_token=access_token, token_type='Bearer')
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/protected")
async def protected_route(user: str = Depends(get_current_user)):
    return {"message": f"Hello, {user}. This route is protected."}


@app.get("/download/{collection_name}/{doc_name}")
async def download_file(collection_name: str, doc_name: str, user: str = Depends(get_current_user)):
    # 在这里实现授权逻辑，验证用户是否有权限下载该文件
    # file_list = Docs.get_by_doc_name(dao, collection_name = collection_name, doc_name = doc_name)
    # file = file_list[0]
    # print(file)
    # if file:
    fileRes = FileResponse(
        path=(config.BASE_DOCS_DIR+"/"+collection_name + "/"+doc_name), filename=doc_name)
    # 如果授权通过，返回文件作为响应
    return fileRes


@app.post("/query_collection")
async def handle(question, user: str = Depends(get_current_user)):
    return await query_collection(llm=glm_cli(), embedding_function=embedding_function, question=question)


@app.get("/get_collection", )
async def handle(collection_name, dao_instance= Depends(MySQLDAO.get_dao), user: str = Depends(get_current_user)):
    return await get_collection(dao_instance, collection_name=collection_name)


@app.get("/collections", )
async def handle(dao_instance= Depends(MySQLDAO.get_dao), user: str = Depends(get_current_user)):
    return await get_all_collections(dao_instance)
 

@app.post("/add_collection")
async def handle(para: Para_Add_Collection, dao_instance= Depends(MySQLDAO.get_dao), user: str = Depends(get_current_user)):
    collection_name = para.dict()['collection_name']
    Collections().insert(dao_instance, collection_name)
    return {"collection_name": collection_name}


@app.get("/all_docs")
async def handle(dao_instance= Depends(MySQLDAO.get_dao)):
    docs = Docs.get_all(dao_instance)
    return {"data": docs}


@app.get("/docs_in_collection")
async def handle(collection_name,dao_instance= Depends(MySQLDAO.get_dao)):
    return await get_docs_in_collection(dao_instance, collection_name)


@app.post("/upload")
async def handle(background_task: BackgroundTasks, 
                 collection_name: str, 
                 collection: str, 
                 file: UploadFile = File(...), 
                 dao_instance= Depends(MySQLDAO.get_dao), 
                 user: str = Depends(get_current_user)):
    return await upload_file_handler(embedding_function, 
                                     dao_instance, 
                                     collection_name, 
                                     collection, 
                                     file, 
                                     user)


@app.post("/search")
async def search(background_task: BackgroundTasks,
                 para: Para_Search,
                 user: str = Depends(get_current_user), ):
    collection_name = para.dict()['collection_name']
    collection = para.dict()['collection']
    file_name = para.dict()['file_name']
    question = para.dict()['question']

    result = await qa_vectordb(llm, 
                               embedding_function=embedding_function, 
                               collection_name=collection_name, 
                               collection=collection, 
                               query=question)

    return result


@app.post("/searchTest")
async def search(background_task: BackgroundTasks,
                 para: Para_Search,
                 user: str = Depends(get_current_user), ):
    collection_name = para.dict()['collection_name']
    collection = para.dict()['collection']
    file_name = para.dict()['file_name']
    question = para.dict()['question']

    embedding_function_m3e = HuggingFaceEmbeddings(model_name= config.embedding_model_dict['m3e-base'], 
                                                   model_kwargs={'device': config.EMBEDDING_DEVICE})
    embedding_function_t2v = HuggingFaceEmbeddings(model_name= config.embedding_model_dict['text2vec'], 
                                                   model_kwargs={'device': config.EMBEDDING_DEVICE})
    
    result_t2v = await query_vectordb(embedding_function=embedding_function_t2v, 
                                      collection_name='text2vec', 
                                      collection='text2vec', 
                                      query=question)
    result_m3e = await query_vectordb(embedding_function=embedding_function_m3e, 
                                      collection_name='m3e_base', 
                                      collection='m3e_base', 
                                      query=question)
    result_t2v["source_documents"] = [{**d, 'collection': 'text2vec'} for d in result_t2v["source_documents"]]
    result_m3e["source_documents"] = [{**d, 'collection': 'm3e_base'} for d in result_m3e["source_documents"]]
    
    result_t2v["source_documents"].extend(result_m3e["source_documents"])
    return result_t2v


@app.post("/chat_collection")
async def chat(request: Request,
               para: Para_Search,
               user: str = Depends(get_current_user), ):
    collection_name = para.dict()['collection_name']
    collection = para.dict()['collection']
    file_name = para.dict()['file_name']
    question = para.dict()['question']

    # request.session.update({'chat_history': []})

    chat_history = request.session.get('chat_history', [])
    print(f"chat_history length = {len(chat_history)}")

    answer, history = await chat_with_vectordb(llm, 
                                               embedding_function=embedding_function, 
                                               collection_name=collection_name, 
                                               collection=collection, 
                                               query=question, 
                                               chat_history=chat_history)
   
    # print(f"history length= {len(history)}")
    # request.session.update({'chat_history': history})
    # print(f"after session update length= {len(request.session.get('chat_history', []))}")
    
    print(f"before session = {dict(request.session)}")
    print(f"history = {history}")
    request.session['chat_history'] = history
    print(f"after session = {dict(request.session)}")

    return answer


if __name__ == '__main__':
    # export LLP_Dev=True
    uvicorn.run('main:app', host="0.0.0.0", port=8080, reload=False)
