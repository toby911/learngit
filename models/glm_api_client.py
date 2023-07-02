import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
from typing import Any, List, Mapping, Optional

import httpx
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
class glm_api_client(LLM):
    max_token: int = 1024*4
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
    

    async def _acall(
        self,
        prompt: str,
        stop: Optional[List[str]] = None) -> str:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        qa_data = {}
        qa_data["prompt"] = prompt
        qa_data["history"] = self.history
        result = await self._arequest_api(qa_data)
        response = result.get('response', '抱歉，AI发生了错误，没有返回!')
        return response
    
  
    
    async def _arequest_api(self, qa_data):
        result_data = {}
        json_data = {}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(config.LLM_URL, json=qa_data)
            
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

        except httpx.HTTPError as e:
            result_data['status'] = "ERROR"
            result_data['response'] = f"大模型调用失败:{e}"
            result_data['history'] = []
            print(f"An HTTP error occurred: {e}")
        except httpx.RequestError as e:
            result_data['status'] = "ERROR"
            result_data['response'] = f"大模型调用失败:{e}"
            result_data['history'] = []
            print(f"An HTTP error occurred: {e}")
        return json_data


async def main():
    # 创建一个glm_llm实例
    my_glm_llm = glm_api_client()

    # 设置一个要询问的问题
    question = "What is the capital of France?"

    # 调用_call方法来获取答案
    answer = await my_glm_llm._acall(question)
    # 输出答案
    print(f"Question: {question}")
    print(f"Answer: {answer}")

    # 设置一个要询问的问题
    question = "What is the capital of England?"
    answer = await my_glm_llm._acall(question)
    # 输出答案
    print(f"Question: {question}")
    print(f"Answer: {answer}")

    # 设置一个要询问的问题
    question = "What is the capital of Japen?"
    # 调用_call方法来获取答案
    answer = await my_glm_llm._acall(question)
    # 输出答案
    print(f"Question: {question}")
    print(f"Answer: {answer}")

    # 设置一个要询问的问题
    question = "What is the capital of China?"
    answer = await my_glm_llm._acall(question)
    # 输出答案
    print(f"Question: {question}")
    print(f"Answer: {answer}")


# 使用asyncio运行main函数
if __name__ == "__main__":
    asyncio.run(main())