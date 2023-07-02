import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
from typing import Any, List, Mapping, Optional

import requests
from langchain import PromptTemplate
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM

from configs.config import DEVELOPMENT, LLP_DEV, PRODUCTION

# 判断当前环境
if os.environ.get("PRODUCTION"):
    config = PRODUCTION
elif os.environ.get("DEVELOPMENT"):
    config = DEVELOPMENT
elif os.environ.get("LLP_DEV"):
    config = LLP_DEV
else:
    config= DEVELOPMENT
    
class glm_llm(LLM):
    max_token: int = 10000
    temperature: float = 0.01
    top_p = 0.9
    history = []
    tokenizer: object = None
    history_len: int = 10
    
    def __init__(self):
        super().__init__()

    @property
    def _llm_type(self) -> str:
        return "glm_api"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None) -> str:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        qa_data = {}
        qa_data["prompt"] = prompt
        qa_data["history"] = self.history
        result = self._request_api(qa_data)
        response = result.get('response', '抱歉，AI发生了错误，没有返回!')
        return response
    
  
    
    def _request_api(self, qa_data):
        result_data = {}
        json_data = {}
        try:
            # 记录当前时间戳
            start_time = time.time()
            print("begin to requests.post...........")
            response = requests.post(config.LLM_URL, json=qa_data, timeout=config.LLM_TIMEOUT)
            end_time = time.time()
            print(f"Execution time: {(end_time - start_time):.1f} seconds")
            
            # 检查HTTP状态码是否表示错误
            response.raise_for_status()

            # 获取响应的JSON数据
            json_data = response.json()

            # 在此处检查JSON数据是否包含特定的错误信息
            if "error" in json_data:
                result_data['status'] = "ERROR"
                result_data['response'] = "大模型调用失败！"
                result_data['history'] = []
            else:
                result_data['status'] = "SUCCESS"
                result_data['response'] = json_data['response']
                result_data['history'] = json_data['history']

        except requests.exceptions.HTTPError as e:
            result_data['status'] = "ERROR"
            result_data['response'] = f"大模型调用失败:{e}"
            result_data['history'] = []
            print(f"An HTTP error occurred: {e}")
        except requests.exceptions.RequestException as e:
            result_data['status'] = "ERROR"
            result_data['response'] = f"大模型调用失败:{e}"
            result_data['history'] = []
            print(f"An HTTP error occurred: {e}")
        return json_data
    
    

    
if __name__ == '__main__':
    question = "AI知识库用到的开源软件有哪些"
    context = "以OpenAI公司GPT4为代表的⼤语⾔模型（LLM）涌现出很多强大的能力，利用LLM搭建具有语义检索和知识总结的新⼀代知识库成为了可能。LLM在铁路企业落地应⽤⾸先要解决⼤模型如何在本地部署的问题。今年以来，随着60亿650亿参数的LLaMA开源基础语⾔模型的快速发展，针对这类可以负担得起的大模型进行微调来完成企业特定任务成为新趋势。AI知识库⽤到的开源软件包括向量数据库和⼤模型两部分。向量数据库主要解决对⽂档进⾏语义检索，然后利⽤LLM对检索出来的结果进⾏提炼和总结并输出。我们选⽤的Milvus向量数据库和ChatGLM-6B⼤语⾔模型都是国内⽐较出⾊的开源软件，对中文语料支持较好。ChatGLM-6B对算⼒有⼀定要求，最好是支持Tensor Core的高性能显卡，在消费级显卡中，英伟达的RTX4090有24G显存，能满足Transformer模型的最低要求。目前京东上的公开报价约1.6w⼀张。在现阶段我们建议配置⼀台双RTX4090的工作站"
    prompt_template = """基于以下已知信息，简洁和专业的来回答用户的问题。如果无法从中得到答案，请说 "根据已知信息无法回答该问题" 或 "没有提供足够的相关信息"，不允许在答案中添加编造成分，答案请使用中文。
    ==========
    已知内容:
    '''
    {context}
    '''
    ==========
    问题:
    '''
    {question}
    '''
    """
    question = "我们应该如何选择显卡，大概需要多少钱？"
    prompt = PromptTemplate(template=prompt_template,
                            input_variables=["context", "question"]).format(question=question, 
                                                                            context = context)
    qa_data = {}
    qa_data["question"] = prompt
    qa_data["history"] = []
    llm = glm_llm()
    llm.history = qa_data["history"]
    result = llm._call(prompt=qa_data["question"])
    print(f"prompt:{prompt}\n response:{result}")
    
