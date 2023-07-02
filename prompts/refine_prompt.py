from langchain.prompts import PromptTemplate
# REFINE_PROMPT_TMPL = (
#     "Your job is to produce a final summary\n"
#     "We have provided an existing summary up to a certain point: {existing_answer}\n"
#     "We have the opportunity to refine the existing summary"
#     "(only if needed) with some more context below.\n"
#     "------------\n"
#     "{text}\n"
#     "------------\n"
#     "Given the new context, refine the original summary\n"
#     "If the context isn't useful, return the original summary."
# )
REFINE_PROMPT_TMPL = """
    "你的工作是产生一个最终摘要\n"
    "我们已经提供了现有的摘要，直到某个点为止：{existing_answer}\n"
    "我们有机会通过下面一些更多的上下文来完善现有的摘要（仅在必要时）。\n"
    "------------\n"
    "{text}\n"
    "------------\n"
    "根据新的上下文，完善原始摘要\n"
    "如果上下文没有用处，请返回原始摘要。"
"""
REFINE_PROMPT = PromptTemplate(
    input_variables=["existing_answer", "text"],
    template=REFINE_PROMPT_TMPL,
)


prompt_template = """写一个简洁的摘要，概括以下内容:


"{text}"


摘要:"""
PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])
