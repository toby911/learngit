import asyncio
import os
from functools import partial
from typing import List

from fastapi import HTTPException
from langchain.chains import (ConversationalRetrievalChain,
                              RetrievalQAWithSourcesChain)
from langchain.chains.llm import LLMChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.docstore.document import Document
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

async def qa_vectordb(llm, embedding_function, collection_name, collection, query: str):
    try:
        revelant_docs = milvus.search(embedding_function= embedding_function, collection_name=collection, question= query)
        filtered_docs: list[Document] = [doc.metadata.update({"score": score}) or doc for doc, score in revelant_docs if score <config.MAX_SCORE]
        func = partial(qa_task, llm, filtered_docs, query)
        # return qa_task(docs=filtered_docs, question=query) if len(filtered_docs) > 0 else build_none_return(question=query, collection_name=collection_name)
        return await asyncio.get_event_loop().run_in_executor(None, func) if len(filtered_docs) > 0 else build_none_return(question=query, collection_name=collection_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Search failed")

async def query_vectordb(embedding_function, collection_name, collection, query: str):
    try:
        revelant_docs = milvus.search(embedding_function= embedding_function, collection_name=collection, question= query)
        filtered_docs: list[Document] = [doc.metadata.update({"score": score}) or doc for doc, score in revelant_docs if score <config.MAX_SCORE]
        source_documents = [{"file_path": d.metadata["file_path"], "page_numbers": d.metadata["page_numbers"], "score": d.metadata["score"]} for d in filtered_docs]
        result = {"question": query, "answer": "", "source_documents": source_documents}
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Search failed")


def qa_task(llm, docs, question):
    chain = load_qa_with_sources_chain(llm, chain_type="refine", question_prompt = DEFAULT_TEXT_QA_PROMPT, refine_prompt = DEFAULT_REFINE_PROMPT, document_prompt = EXAMPLE_PROMPT)
    result = build_qa_result(chain({"input_documents": docs, "question": question}, return_only_outputs=False))
    return result

def build_none_return(question, collection_name):
    result = {"question": question, "answer": f"在《{collection_name}》 知识库中没有检索出相关的内容，无法回答关于【{question}】的问题", "source_documents":[]}
    return result

def build_qa_result(qa_chain_result):
    question = qa_chain_result["question"]
    answer = qa_chain_result["output_text"]
    source_documents = [{"file_path": d.metadata["file_path"], "page_numbers": d.metadata["page_numbers"], "score": d.metadata["score"]} for d in qa_chain_result["input_documents"]]
    result = {"question": question, "answer": answer, "source_documents": source_documents}
    return result
    
