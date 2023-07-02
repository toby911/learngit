# flake8: noqa
from langchain.prompts import PromptTemplate

KB_SELECT_PROMPT_TMPL = """请从下面的文本中提取关键信息，并用json格式输出，我先给你几个例子，你将严格按照例子里的json格式输出，不要添加任何其他内容
问题：请从建设部的文件中查找关于建设项目资金管理方面的内容
回答："department': '建设部,'search_query': '建设资金管理','知识库': '建设部知识库"
====================
问题：请检索建设部下发的文件，查找关于建设资金管理的信息
回答："department": "建设部","search_query": "建设项目资金管理","知识库": "建设部知识库"
====================
问题：请打开建设部知识库，查找关于建设资金管理的信息
回答："department": "建设部"， "search_query": "建设项目资金管理","知识库": "建设部知识库"
====================
问题：请打开建设部知识库
回答："department": "建设部","search_query": "","知识库": "建设部知识库"
====================
问题：在建设部的文件中有哪些关于建设资金管理的内容
回答："department": "建设部","search_query": "建设项目资金管理","知识库": "建设部知识库"

问题：{question}
回答：
"""



KB_SELECT_PROMPT = PromptTemplate(
    input_variables=["question"],
    template=KB_SELECT_PROMPT_TMPL,
)
