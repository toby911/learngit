from langchain.prompts import PromptTemplate

question_prompt_template = """以下的部分来自长文档，请查看是否有任何文本与回答的问题相关
{context}
问题: {question}
如果有与问题相关的文本，请进行简洁明确的摘要，如果没有，请写"没有相关文本"""
    
QUESTION_PROMPT = PromptTemplate(
    template=question_prompt_template, input_variables=["context", "question"]
)

combine_prompt_template = """在下面给定的长文档的摘要和问题的基础上，写出最终的答案，如果不知道答案，就写"不知道"，不要编造答案。

问题: {question}
=========
{summaries}
=========
用中文回答:"""

COMBINE_PROMPT = PromptTemplate(
    template=combine_prompt_template, input_variables=["summaries", "question"]
)