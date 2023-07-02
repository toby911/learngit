import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langchain import PromptTemplate, LLMChain
from models.glm_llm import glm_llm as glm


question = "AI知识库用到的开源软件有哪些"
context = "以OpenAI公司GPT4为代表的⼤语⾔模型（LLM）涌现出很多强大的能力，利用LLM搭建具有语义检索和知识总结的新⼀代知识库成为了可能。LLM在铁路企业落地应⽤⾸先要解决⼤模型如何在本地部署的问题。今年以来，随着60亿650亿参数的LLaMA开源基础语⾔模型的快速发展，针对这类可以负担得起的大模型进行微调来完成企业特定任务成为新趋势。AI知识库⽤到的开源软件包括向量数据库和⼤模型两部分。向量数据库主要解决对⽂档进⾏语义检索，然后利⽤LLM对检索出来的结果进⾏提炼和总结并输出。我们选⽤的Milvus向量数据库和ChatGLM-6B⼤语⾔模型都是国内⽐较出⾊的开源软件，对中文语料支持较好。ChatGLM-6B对算⼒有⼀定要求，最好是支持Tensor Core的高性能显卡，在消费级显卡中，英伟达的RTX4090有24G显存，能满足Transformer模型的最低要求。目前京东上的公开报价约1.6w⼀张。在现阶段我们建议配置⼀台双RTX4090的工作站"
prompt_template = """基于以下已知信息，简洁和专业的来回答用户的问题。
                    如果无法从中得到答案，请说 "根据已知信息无法回答该问题" 或 "没有提供足够的相关信息"，不允许在答案中添加编造成分，答案请使用中文。
                    已知内容:
                    {context}
                    问题:
                    {question}"""
prompt = PromptTemplate(template=prompt_template,input_variables=["context", "question"])


llm = glm()
llm_chain = LLMChain(
    llm=llm,
    prompt=prompt
)
print(llm_chain.predict(context = context, question = question))