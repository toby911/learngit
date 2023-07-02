# flake8: noqa
from langchain.prompts import PromptTemplate

DEFAULT_REFINE_PROMPT_TMPL = (
    "原始问题如下: {question}\n"
    "我们已经提供了一个现有的答案，包括来源： {existing_answer}\n"
    "我们有机会完善现有的答案。"
    "（仅在需要时）下面提供更多上下文。\n"
    "------------\n"
    "{context_str}\n"
    "------------\n"
    "鉴于新的上下文，修改原始答案以更好地回答问题。 "
    "如果你更新了答案，请同时更新来源. "
    "如果新的上下文没有帮助请返回原来的答案."
)
DEFAULT_REFINE_PROMPT = PromptTemplate(
    input_variables=["question", "existing_answer", "context_str"],
    template=DEFAULT_REFINE_PROMPT_TMPL,
)


DEFAULT_TEXT_QA_PROMPT_TMPL = (
    "上下文信息如下. \n"
    "---------------------\n"
    "{context_str}"
    "\n---------------------\n"
    "根据上下文信息而非先前的知识"
    "回答问题: {question}\n"
)
DEFAULT_TEXT_QA_PROMPT = PromptTemplate(
    input_variables=["context_str", "question"], template=DEFAULT_TEXT_QA_PROMPT_TMPL
)

EXAMPLE_PROMPT = PromptTemplate(
    template="Content: {page_content}\nSource: {source}",
    input_variables=["page_content", "source"],
)
