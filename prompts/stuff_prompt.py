from langchain.prompts import PromptTemplate

prompt_template = """写一个简洁的摘要，概括以下内容:


"{text}"


摘要:"""
PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])


