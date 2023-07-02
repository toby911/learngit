import torch.cuda
import torch.backends


embedding_model_dict = {
    "ernie-tiny": "nghuyong/ernie-3.0-nano-zh",
    "ernie-base": "nghuyong/ernie-3.0-base-zh",
    "text2vec": "/apps/models/GanymedeNil/text2vec-base-chinese/GanymedeNil_text2vec-base-chinese",
}

# Embedding model name
# EMBEDDING_MODEL = "/apps/models/GanymedeNil/text2vec-base-chinese/GanymedeNil_text2vec-base-chinese"
EMBEDDING_MODEL = "/Users/llp/llm/models/text2vec-base-chinese"
# Embedding running device
EMBEDDING_DEVICE = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

# supported LLM models
llm_model_dict = {
    "chatglm-6b-int4-qe": "THUDM/chatglm-6b-int4-qe",
    "chatglm-6b-int4": "/apps/models/THUDM/chatglm-6b-int4/models--THUDM--chatglm-6b-int4/snapshots/63d66b0572d11cedd5574b38da720299599539b3",
    "chatglm-6b": "/content/drive/MyDrive/chatglm-6b",
}

# LLM model name
LLM_MODEL = "chatglm-6b"

# LLM running device
LLM_DEVICE = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

LLM_URL = 'http://192.168.50.77:7861/chat'
# LLM_URL = 'http://192.168.50.80:7007/'
OCR_URL = 'http://192.168.50.77:7001/upload'

