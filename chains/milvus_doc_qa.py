from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import UnstructuredFileLoader
from models.chatglm_llm import ChatGLM
import sentence_transformers
import os
from configs.model_config import *
import datetime
from typing import List

# return top-k text chunk from vector store
VECTOR_SEARCH_TOP_K = 6

# LLM input history length
LLM_HISTORY_LEN = 3

# Show reply with source text from input document
REPLY_WITH_SOURCE = True


class MilvusDocQA:
    llm: object = None
    embeddings: object = None
    

    def init_cfg(self,llm_history_len: int = LLM_HISTORY_LEN,
                 llm_model: str = LLM_MODEL,
                 llm_device=LLM_DEVICE,
                 top_k=VECTOR_SEARCH_TOP_K,
                 ):
        self.llm = ChatGLM()
        self.llm.load_model(model_name_or_path=llm_model_dict[llm_model], llm_device=llm_device)
        self.llm.history_len = llm_history_len
        self.top_k = top_k
        

    def init_vectorstore_and_embeddings(self, milvus, embeddings):
        self.milvus_db = milvus
        #  self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model_dict[embedding_model], )
        self.embeddings = embeddings
        self.embeddings.client = sentence_transformers.SentenceTransformer(self.embeddings.model_name, device=EMBEDDING_DEVICE)
        
    def get_knowledge_based_answer(self,
                                   query,
                                   chat_history=[], ):
        prompt_template = """基于以下已知信息，简洁和专业的来回答用户的问题。
    如果无法从中得到答案，请说 "根据已知信息无法回答该问题" 或 "没有提供足够的相关信息"，不允许在答案中添加编造成分，答案请使用中文。
    
    已知内容:
    {context}
    
    问题:
    {question}"""
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        self.llm.history = chat_history
        # search_kwargs={"k": self.top_k}
        knowledge_chain = RetrievalQA.from_llm(
            llm=self.llm,
            retriever= self.milvus_db.as_retriever(),
            prompt=prompt
        )
        knowledge_chain.combine_documents_chain.document_prompt = PromptTemplate(
            input_variables=["page_content"], template="{page_content}"
        )

        knowledge_chain.return_source_documents = True

        result = knowledge_chain({"query": query})
        self.llm.history[-1][0] = query
        return result, self.llm.history
