import torch.backends
import torch.cuda


class DEVELOPMENT:
    MILVUS_HOST = '192.168.50.77'
    MILVUS_PORT = 19530
    MILVUS_MAX_CONNECTION = 10
    WSS_HOST = '192.168.50.77'
    WSS_PORT = 8765
    MAX_SCORE = 500
    QA_MAX_SCORE = 500
    VECTOR_SEARCH_TOP_K = 3
    SENTENCE_SIZE = 100
    CHUNK_SIZE = 300
    CHUNK_OVERLAP = 20
    BASE_DOCS_DIR = "/apps/docs"
    # LLM_URL = 'http://192.168.50.77:7861/chat'
    # LLM_URL = 'http://192.168.50.80:7007/'
    # LLM_URL = 'https://u152649-b607-e934aa4f.westa.seetacloud.com:8443/'
    LLM_URL = 'https://u152649-b607-e934aa4f.westa.seetacloud.com:8443/v1'
    LLM_MODEL= 'chatglm2-6b'
    LLM_TIMEOUT = 30
    OCR_URL = 'http://192.168.50.77:7001/upload'
    OCR_TEMP_DIR = '/apps/ocr_working'
    TMP_DIR = '/apps/docs/upload_temp_files'
    MYSQL_HOST = '192.168.50.77'
    MYSQL_DATABASE = 'chatdoc'
    MYSQL_USER = 'root'
    MYSQL_PWD = 'Ztrx@1234_'
    KB_NAME_COLLECTION = 'KB_NAME'
    CHAT_HISTORY_LEN=-3
    MAX_SIM_COLLECTION = 400
    # 定义最大连接数
    MAX_API_COENNECTION_LIMITE= 2
    # Embedding running device
    EMBEDDING_DEVICE = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    EMBEDDING_MODEL_NAME= "m3e-base"
    # EMBEDDING_MODEL_NAME= "text2vec"
    embedding_model_dict = {
        "m3e-base": "/apps/models/m3e-base",
        "text2vec": "/apps/models/GanymedeNil/text2vec-base-chinese/GanymedeNil_text2vec-base-chinese",
    }
    EMBEDDING_MODEL = embedding_model_dict[EMBEDDING_MODEL_NAME]


class PRODUCTION:
    MILVUS_HOST = '192.168.50.77'
    MILVUS_PORT = 19530
    MILVUS_MAX_CONNECTION = 10
    WSS_HOST = '192.168.50.77'
    WSS_PORT = 8765
    MAX_SCORE = 550
    QA_MAX_SCORE = 550
    VECTOR_SEARCH_TOP_K = 3
    SENTENCE_SIZE = 100
    CHUNK_SIZE = 300
    CHUNK_OVERLAP = 20
    BASE_DOCS_DIR = "/apps/docs"
    # LLM_URL = 'http://192.168.50.77:7861/chat'
    # LLM_URL = 'http://192.168.50.80:7007/'
    # LLM_URL = 'https://u152649-b607-e934aa4f.westa.seetacloud.com:8443/'
    LLM_URL = 'https://u152649-b607-e934aa4f.westa.seetacloud.com:8443/v1'
    LLM_MODEL= 'chatglm2-6b'
    LLM_TIMEOUT = 30
    OCR_URL = 'http://192.168.50.77:7001/upload'
    OCR_TEMP_DIR = '/apps/ocr_working'
    TMP_DIR = '/apps/docs/upload_temp_files'
    MYSQL_HOST = '192.168.50.77'
    MYSQL_DATABASE = 'chatdoc'
    MYSQL_USER = 'root'
    MYSQL_PWD = 'Ztrx@1234_'
    KB_NAME_COLLECTION = 'KB_NAME'
    CHAT_HISTORY_LEN=-3
    MAX_SIM_COLLECTION = 400
    # 定义最大连接数
    MAX_API_COENNECTION_LIMITE= 2
    # Embedding running device
    EMBEDDING_DEVICE = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    EMBEDDING_MODEL_NAME= "text2vec"
    embedding_model_dict = {
        "m3e-base": "/apps/models/m3e-base",
        "text2vec": "/apps/models/GanymedeNil/text2vec-base-chinese/GanymedeNil_text2vec-base-chinese",
    }
    EMBEDDING_MODEL = embedding_model_dict[EMBEDDING_MODEL_NAME]

class LLP_DEV:
    MILVUS_HOST = '192.168.50.77'
    MILVUS_PORT = 19530
    MILVUS_MAX_CONNECTION = 10
    WSS_HOST = '192.168.50.77'
    WSS_PORT = 8765
    MAX_SCORE = 500
    QA_MAX_SCORE = 500
    VECTOR_SEARCH_TOP_K = 5
    SENTENCE_SIZE = 100
    CHUNK_SIZE = 300
    CHUNK_OVERLAP = 20    
    BASE_DOCS_DIR = "/Users/llp/apps/docs"
    # LLM_URL = 'http://192.168.50.77:7861/chat'
    # LLM_URL = 'http://192.168.50.80:7007/'
    # LLM_URL = 'https://u152649-b607-e934aa4f.westa.seetacloud.com:8443/'
    LLM_URL = 'https://u152649-b607-e934aa4f.westa.seetacloud.com:8443/v1'
    LLM_MODEL= 'chatglm2-6b'
    LLM_TIMEOUT = 30
    OCR_URL = 'http://192.168.50.77:7001/upload'
    OCR_TEMP_DIR = '/Users/llp/apps/ocr_working'
    TMP_DIR = '/Users/llp/apps/docs/upload_temp_files'
    MYSQL_HOST = '192.168.50.77'
    MYSQL_DATABASE = 'chatdoc'
    MYSQL_USER = 'root'
    MYSQL_PWD = 'Ztrx@1234_'
    KB_NAME_COLLECTION = 'KB_NAME'
    CHAT_HISTORY_LEN=-3
    MAX_SIM_COLLECTION = 400
    # 定义最大连接数
    MAX_API_COENNECTION_LIMITE= 2
    # EMBEDDING_MODEL = "/Users/llp/llm/models/text2vec-base-chinese"
    EMBEDDING_MODEL_NAME= "m3e-base"
    embedding_model_dict = {
        "m3e-base": "/Users/llp/llm/models/m3e-base",
        "text2vec": "/Users/llp/llm/models/text2vec-base-chinese",
    }
    EMBEDDING_MODEL = embedding_model_dict[EMBEDDING_MODEL_NAME]
    
    # Embedding running device
    EMBEDDING_DEVICE = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
