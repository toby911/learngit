from langchain.prompts.prompt import PromptTemplate

_template = """给定以下对话和后续问题，请将后续问题重新表述为一个独立的问题，使用中文回答.

对话历史:
{chat_history}
接下来的输入: {question}
独立问题:"""
CONDENSE_QUESTION_PROMPT_ZH = PromptTemplate.from_template(_template)

prompt_template = """使用下面的上下文来回答最后的问题。如果你不知道答案，只需要说你不知道，不要试图编造一个答案.

{context}

问题: {question}
有帮助的回答:"""
QA_PROMPT_ZH = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)
