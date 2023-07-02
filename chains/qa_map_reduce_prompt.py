# flake8: noqa
from langchain.prompts import PromptTemplate

question_prompt_template = """使用长文档中的以下部分来查看是否有任何相关文本以回答问题。直接返回任何相关的文字.
{context}
问题: {question}
相关的文本(如果有的话):"""
QUESTION_PROMPT = PromptTemplate(
    template=question_prompt_template, input_variables=["context", "question"]
)

combine_prompt_template = """给定一个长文档的提取部分和一个问题，创建一个带有参考来源(“SOURCES”)的最终答案。如果您不知道答案，请直接说出您不知道。请勿试图编造答案。
在您的回答中始终返回“SOURCES”部分。

问题：哪个州/国家的法律适用于合同的解释？
=========

内容：本协议受英国法律管辖，各方同意在与本协议有关的任何争议（合同或非合同）中提交给英国法院专属管辖权，但任何一方均可向任何法院申请禁令或其他救济措施以保护其知识产权。

Source:28-pl

内容：不放弃。未能或延迟行使本协议项下的任何权利或救济措施不构成对该等（或其他）权利或救济措施的放弃。\n\n11.7 可分性。本协议的任何条款（或部分条款）无效、非法或不可执行并不影响剩余期限（如有）和本协议继续有效。\n\n11.8 无代理关系。除非另有明确声明，否则本协议中没有规定各方之间建立代理、合伙企业或联营企业。\n\n11.9 无第三方受益人。

Source:30-pl

内容：(b) 如果 Google 善意地认为经销商已经违反了反贿赂法律（如第8.5条所定义）， 或者这样的违反行为可能发生，

Source:4-pl
=========
最终答案：本协议受英国法律管辖。

SOURCES:28-pl

问题：企业年金的管理包括哪些内容？
=========
内容: 广铁集团今年的客运发送量突破历史最高记录，这得益于全集团上下的团结努力，也得益于国内快速发展的经济对于运输市场的旺盛需求\n\n我们预计明年的客运收入将继续增长，预计增幅5%以上
Source: 24-pl
内容: 发展企业职工文化是企业管理的重要内容.\n\n发展职工文化活动包括文体比赛，休闲活动和读书阅览等
Source: 11-pl
内容: 在租用实例页面：选择计费方式，选择合适的主机，选择要创建实例中的GPU数量，选择镜像（内置了不同的深度学习框架），\n\n最后创建即可如果你需要更大的硬盘用于存放数据，那么请留意「硬盘」这列「最大可扩容」大小。数据盘等的路径请参考文档
Source: 34-pl
=========
最终答案: 暂时还不清楚企业年金的管理的具体内容.
SOURCES:

问题: {question}
=========
{summaries}
=========
最后的答案:"""
COMBINE_PROMPT = PromptTemplate(
    template=combine_prompt_template, input_variables=["summaries", "question"]
)

EXAMPLE_PROMPT = PromptTemplate(
    template="Content: {page_content}\nSource: {source}",
    input_variables=["page_content", "source"],
)
