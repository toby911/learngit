from fastapi import FastAPI, Request
from transformers import AutoTokenizer, AutoModel
import uvicorn, json, datetime
import torch
import asyncio

DEVICE = "cuda"
DEVICE_ID = "0"
CUDA_DEVICE = f"{DEVICE}:{DEVICE_ID}" if DEVICE_ID else DEVICE
MAX_LENGTH = 4096


def torch_gc():
    if torch.cuda.is_available():
        with torch.cuda.device(CUDA_DEVICE):
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()


app = FastAPI()
gpu_lock = asyncio.Lock()

async def process_request(tokenizer, prompt, history, max_length, top_p, temperature):
    async with gpu_lock:
        # 处理请求，调用GPU
        # response, history = model.chat(tokenizer,
        #                     prompt,
        #                     history,
        #                     max_length,
        #                     top_p,
        #                     temperature)
        
        response, history = model.chat(tokenizer,
                                   prompt,
                                   history=history,
                                   max_length=max_length if max_length else 4096,
                                   top_p=top_p if top_p else 0.7,
                                   temperature=temperature if temperature else 0.3)
        
        return response, history
 

@app.post("/")
async def create_item(request: Request):
    global model, tokenizer
    json_post_raw = await request.json()
    json_post = json.dumps(json_post_raw)
    json_post_list = json.loads(json_post)
    prompt = json_post_list.get('prompt')
    history = json_post_list.get('history')
    max_length = json_post_list.get('max_length')
    top_p = json_post_list.get('top_p')
    temperature = json_post_list.get('temperature')
    max_length=max_length if max_length else MAX_LENGTH
    answer = {}
    # print(f"client:{request.client.host}..........")
    if len(prompt) > max_length:
        answer = {
            "response": f"输入的长度{len(prompt)}超过{max_length}, 目前AI的能力还无法处理这么长的输入...",
            "history": history,
            "status": 200,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    else:
        start_time = datetime.datetime.now()
        time = start_time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{time}]:prompt length={len(prompt)}")
        
        response, history = await process_request(tokenizer= tokenizer, 
                        prompt= prompt, 
                        history= history, 
                        max_length= max_length if max_length else MAX_LENGTH, 
                        top_p=top_p if top_p else 0.7, 
                        temperature=temperature if temperature else 0.3)
        answer = {
            "response": response,
            "history": history,
            "status": 200,
            "time": time
        }
        end_time = datetime.datetime.now()
        total_secs = (end_time - start_time).total_seconds()
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]:response length={len(response)},total used {total_secs} secs")
        torch_gc()
    
    return answer


if __name__ == '__main__':
    tokenizer = AutoTokenizer.from_pretrained("/root/autodl-tmp/models/chatglm-6b", trust_remote_code=True)
    model = AutoModel.from_pretrained("/root/autodl-tmp/models/chatglm-6b", trust_remote_code=True).half().cuda()
    model.eval()
    uvicorn.run(app, host='0.0.0.0', port=6006, workers=1)
