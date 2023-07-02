from __future__ import annotations

import asyncio
import warnings
from abc import ABC, abstractmethod
from functools import partial
from typing import Any, Dict, Iterable, List, Optional, Tuple, Type, TypeVar
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from pydantic import BaseModel, Field, root_validator
import logging
from langchain.docstore.document import Document
from langchain.embeddings.base import Embeddings
from langchain.schema import BaseRetriever
from langchain.vectorstores.base import VectorStore
from langchain.vectorstores.milvus import Milvus
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility

logger = logging.getLogger(__name__)
DEFAULT_MILVUS_CONNECTION = {
    "host": "localhost",
    "port": "19530",
    "user": "",
    "password": "",
    "secure": False,
}

class My_VectorStore(Milvus):
    def __init__(
        self,
        embedding_function: Embeddings,
        collection_name: str = "LangChainCollection",
        connection_args: Optional[dict[str, Any]] = None,
        consistency_level: str = "Session",
        index_params: Optional[dict] = None,
        search_params: Optional[dict] = None,
        drop_old: Optional[bool] = False,
    ):
        # In order for a collection to be compatible, pk needs to be auto'id and int
        self._primary_field = "pk"
        # In order for compatiblility, the text field will need to be called "text"
        self._text_field = "text"
        # In order for compatbility, the vector field needs to be called "vector"
        self._vector_field = "vector"

        self.collection_name = collection_name
        super(My_VectorStore, self).__init__(
            embedding_function= embedding_function,
            collection_name= collection_name,
            connection_args= connection_args,
            consistency_level= "Session",
            index_params= None,
            search_params= None,
            drop_old= False,
        )

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        param: Optional[dict] = None,
        expr: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> List[Document]:
        """Perform a similarity search against the query string.

        Args:
            query (str): The text to search.
            k (int, optional): How many results to return. Defaults to 4.
            param (dict, optional): The search params for the index type.
                Defaults to None.
            expr (str, optional): Filtering expression. Defaults to None.
            timeout (int, optional): How long to wait before timeout error.
                Defaults to None.
            kwargs: Collection.search() keyword arguments.

        Returns:
            List[Document]: Document results for search.
        """
        if self.col is None:
            logger.debug("No existing collection to search.")
            return []
        res = self.similarity_search_with_score(
            query=query, k=k, param=param, expr=expr, timeout=timeout, **kwargs
        )
        # for d,s in res:
        #     d.metadata["score"] = s
        return [doc.metadata.update({"score": score}) or doc for doc, score in res if score < kwargs["score_threshold"]]

def test():
    embedding = HuggingFaceEmbeddings(model_name="/apps/models/GanymedeNil/text2vec-base-chinese/GanymedeNil_text2vec-base-chinese", )
    question = "关于人事制度内容有哪些"
    collection_name= 'k7635e3ebfe08'
    MILVUS_HOST = '192.168.50.77'
    MILVUS_PORT = 19530

    if not connections.has_connection(collection_name):
        connections.connect(alias=collection_name, host=MILVUS_HOST, port=MILVUS_PORT)
    connection_args = {"host": MILVUS_HOST, "port": MILVUS_PORT, "alias": collection_name}

    # vectordb = Milvus(collection_name= collection_name
    #                       , embedding_function= embedding
    #                       , connection_args=connection_args)    

    vectordb = My_VectorStore(collection_name= collection_name
                          , embedding_function= embedding
                          , connection_args=connection_args)    


    results = vectordb.similarity_search(query=question, k=5, score_threshold=510)
    for doc in results:
        print(f"file={doc.metadata['source']}, page = {doc.metadata['page_number']}")
    
    print(f"len = {len(results)}")


if __name__ == '__main__':
    test()