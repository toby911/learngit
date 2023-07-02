import hashlib
import logging
import os
import shutil
import sys
import uuid

from configs.config import DEVELOPMENT, LLP_DEV, PRODUCTION

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# 判断当前环境
if os.environ.get("PRODUCTION"):
    config = PRODUCTION
elif os.environ.get("DEVELOPMENT"):
    config = DEVELOPMENT
elif os.environ.get("LLP_DEV"):
    config = LLP_DEV
else:
    config= DEVELOPMENT
    
def save_tmp(collection_name, file_name, content: bytes):
    tmp_path = os.path.join(config.TMP_DIR, collection_name)
    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)
    file_tmp_path = os.path.join(tmp_path, file_name)
    print(file_tmp_path)
    with open(file_tmp_path, "wb") as f:
        f.write(content)
    return file_tmp_path

    
def get_file_extension(file_path):
    return os.path.splitext(file_path)[1]
    
def save_file(collection_name, file_path, filename):
    doc_type = get_file_extension(filename)
    data_dir = os.path.join(config.BASE_DOCS_DIR, collection_name)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    if doc_type == '.docx' or doc_type == '.pptx' :
        os.system("docker exec -t libreoffice unoconv --connection 'socket,host=127.0.0.1,port=8100,tcpNoDelay=1;urp;StarOffice.ComponentContext' -f pdf {}".format(file_path))
        filename = filename.rsplit(".", 1)[0] + ".pdf"
    tmp_file_path = os.path.join(config.TMP_DIR, collection_name, filename)
    destination_file = os.path.join(data_dir, filename)
    if not os.path.exists(destination_file):
        shutil.move(tmp_file_path, data_dir)
        return destination_file, filename
    else:
        os.remove(tmp_file_path)
        return False, filename