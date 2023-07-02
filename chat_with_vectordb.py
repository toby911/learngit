import asyncio
import os
from functools import partial
from typing import List

from fastapi import HTTPException
from langchain.chains import (ConversationalRetrievalChain,
                              RetrievalQAWithSourcesChain)
from langchain.chains.llm import LLMChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores.base import VectorStoreRetriever

import milvusUtil as milvus
from chains.condense_quest_prompt import CONDENSE_QUESTION_PROMPT_ZH
from chains.qa_refine_prompt import (DEFAULT_REFINE_PROMPT,
                                     DEFAULT_TEXT_QA_PROMPT, EXAMPLE_PROMPT)
from configs.config import DEVELOPMENT, LLP_DEV, PRODUCTION
from models.glm_api_client import glm_api_client as glm_cli

# 判断当前环境
if os.environ.get("PRODUCTION"):
    config = PRODUCTION
elif os.environ.get("DEVELOPMENT"):
    config = DEVELOPMENT
elif os.environ.get("LLP_DEV"):
    config = LLP_DEV
else:
    config= DEVELOPMENT
    
async def chat_with_vectordb(llm, embedding_function, collection_name, collection, query: str, chat_history):
    try:
        results = []
        vectorstore = milvus.get_vectordb(collection_name= collection
                            , embedding_function= embedding_function
                            , connection_args= {"host": config.MILVUS_HOST, "port": config.MILVUS_PORT, "alias": collection})
        retriever = vectorstore.as_retriever(search_type = "similarity", search_kwargs = {"k":config.VECTOR_SEARCH_TOP_K, "score_threshold":config.QA_MAX_SCORE})
        func = partial(conversational_qa_task, 
                       llm, 
                       retriever, 
                       collection_name, 
                       query, 
                       chat_history)
        answer= await asyncio.get_event_loop().run_in_executor(None, func) 
        chat_history.append([query, answer["answer"]])                                        
        return answer,chat_history
    except Exception as e:
        raise HTTPException(status_code=500, detail="Search failed")

def build_none_return(question, collection_name):
    result = {"question": question, "answer": f"在《{collection_name}》 知识库中没有检索出相关的内容，无法回答关于【{question}】的问题", "source_documents":[]}
    return result

def build_qa_result(qa_chain_result):
    question = qa_chain_result["question"]
    answer = qa_chain_result["output_text"]
    source_documents = [{"file_path": d.metadata["file_path"], "page_number": d.metadata["page_number"], "score": d.metadata["score"]} for d in qa_chain_result["input_documents"]]
    result = {"question": question, "answer": answer, "source_documents": source_documents}
    return result


def get_chat_history(inputs) -> str:
    res = []
    for human, ai in inputs:
        res.append(f"Human:{human}\nAI:{ai}")
    return "\n".join(res)

def conversational_qa_task(llm, retriever:VectorStoreRetriever, collection_name, question, chat_history):
    question_generator = LLMChain(llm=llm, prompt=CONDENSE_QUESTION_PROMPT_ZH)
    doc_chain = load_qa_with_sources_chain(llm, chain_type="refine", question_prompt = DEFAULT_TEXT_QA_PROMPT, refine_prompt = DEFAULT_REFINE_PROMPT, document_prompt = EXAMPLE_PROMPT)
    chain = ConversationalRetrievalChain(
        retriever=retriever,
        question_generator=question_generator,
        combine_docs_chain=doc_chain,
        return_source_documents = True,
        get_chat_history=get_chat_history
    )
    revelant_docs = retriever.get_relevant_documents(query=question)
    if len(revelant_docs)>0:
        result = chain({"question": question, "chat_history": chat_history})
        docs = result["source_documents"]
        source_documents = [{'file_path': doc.metadata['file_path'], 'page_number': doc.metadata['page_numbers']} for doc in docs]
        answer = {"question":result["question"], "answer":result['answer'], "source_documents":source_documents}
    else:
        answer= build_none_return(question, collection_name)

    return answer
