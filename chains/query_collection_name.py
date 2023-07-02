import os
import pathlib
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
from typing import Any, List, Mapping, Optional

from langchain import LLMChain, PromptTemplate
from langchain.base_language import BaseLanguageModel
from langchain.chains.combine_documents.base import BaseCombineDocumentsChain
from langchain.chains.combine_documents.map_reduce import \
    MapReduceDocumentsChain
from langchain.chains.combine_documents.refine import RefineDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.chains.summarize import (LoadingCallable,
                                        _load_map_reduce_chain,
                                        _load_refine_chain, _load_stuff_chain,
                                        map_reduce_prompt, refine_prompts,
                                        stuff_prompt)
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.output_parsers import OutputFixingParser, PydanticOutputParser
from langchain.prompts import (ChatPromptTemplate, HumanMessagePromptTemplate,
                               PromptTemplate)
from langchain.prompts.base import BasePromptTemplate
from pydantic import BaseModel, Field, validator

import milvusUtil as milvus
from loader.pdf_loader import loadDocsFromPDF
from models.glm_api_client import glm_api_client as glm_cli
from prompts import mapreduce_prompt, refine_prompt, stuff_prompt


def query_collection_name(llm, question):
    KB_SELECT_PROMPT_TMPL = """请从下面的文本中提取关键信息,并用json格式输出,我先给你几个例子,你将严格按照例子里的json格式输出,不要添加任何其他内容
    问题:请从建设部的文件中查找关于建设项目资金管理方面的内容
    回答:"department':"建设部", "search_query":"建设资金管理", "knowledge_base":"建设部知识库"
    ====================
    问题:请检索建设部下发的文件，查找关于建设资金管理的信息
    回答:"department":"建设部","search_query":"建设项目资金管理", "knowledge_base":"建设部知识库"
    ====================
    问题:请打开建设部知识库，查找关于建设资金管理的信息
    回答:"department":"建设部", "search_query":"建设项目资金管理", "knowledge_base":"建设部知识库"
    ====================
    问题:请打开建设部知识库
    回答:"department":"建设部", "search_query": "", "knowledge_base":"建设部知识库"
    ====================
    问题:在建设部的文件中有哪些关于建设资金管理的内容
    回答:"department":"建设部", "search_query":"建设项目资金管理", "knowledge_base":"建设部知识库"
    ====================
    问题:请从客运部文件中查找安全生产的资料
    回答:"department":"客运部", "search_query":"安全生产", "knowledge_base":"客运部知识库"
    ====================
    问题:请打开langchain知识库
    回答:"department":"", "search_query":"", "knowledge_base":"langchain知识库"
    ====================
    问题:请打开安全生产问答知识库
    回答:"department":"", "search_query":"", "knowledge_base":"安全生产问答知识库"
    ====================
    问题:从word文档中查找关于建设资金管理的内容
    回答:"department":"", "search_query":"查找关于建设资金管理的内容", "knowledge_base":"word文档知识库"
    ====================
    问题:搜寻word文档知识库
    回答:"department":"", "search_query":"", "knowledge_base":"word文档知识库"

    现在请从下面的文本中提取关键信息,直接输出结果：
    {question}
    """
    prompt = PromptTemplate(template=KB_SELECT_PROMPT_TMPL,input_variables=["question"])
    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt
    )
    answer = llm_chain.predict(question = question)
    sub_str = '"'
    index = answer.find(sub_str)
    answer = answer[index:] if index != -1 else answer
    class kb_selector(BaseModel):
        knowledge_base: str = Field(description="name of an knowledge_base")
        search_query: str = Field(description="query of a search")
        department: str = Field(description="department")      
    parser = PydanticOutputParser(pydantic_object=kb_selector)
    new_parser = OutputFixingParser.from_llm(parser=parser, llm=llm)
    print(answer)
    try:
        kb = new_parser.parse(answer)
    except Exception as e:
        kb = kb_selector(knowledge_base="", search_query="", department="")
    return kb.knowledge_base

if __name__ == '__main__':
    llm = glm_cli()
    kb = query_collection_name(llm=llm, question="从建设部的文件中查找关于劳动安全的资料")
    print(f"知识库={kb}")
    
    