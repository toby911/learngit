import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import random
import re
import string
import uuid
from logging import Logger
from pathlib import Path
from typing import Any, Iterable, List, Optional

import fitz
import requests
from langchain.docstore.document import Document
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders.pdf import (BasePDFLoader, PDFMinerLoader,
                                            PDFPlumberLoader, PyMuPDFLoader,
                                            PyPDFLoader)
# from loader.ali_text_splitter import AliTextSplitter
from langchain.text_splitter import CharacterTextSplitter
from PIL import Image

from configs.config import DEVELOPMENT, LLP_DEV, PRODUCTION
from loader.chinese_text_splitter import (ChineseProvisionsSplitter,
                                          ChineseTextSplitter)

# 判断当前环境
if os.environ.get("PRODUCTION"):
    config = PRODUCTION
elif os.environ.get("DEVELOPMENT"):
    config = DEVELOPMENT
elif os.environ.get("LLP_DEV"):
    config = LLP_DEV
else:
    config= DEVELOPMENT
    
class PyMuPDFOCRLoader(BasePDFLoader):
    """Loader that uses PyMuPDF to load PDF files.Exacte Images and OCR"""
    def __init__(self, file_path: str):
        """Initialize with file path."""
        try:
            import fitz  # noqa:F401
        except ImportError:
            raise ValueError(
                "PyMuPDF package not found, please install it with "
                "`pip install pymupdf`"
            )
        self.file_path = file_path
        super().__init__(file_path)

    def generate_random_string(length):
        # string.ascii_letters 包括所有大小写英文字母
        letters = string.ascii_letters
        result_str = ''.join(random.choice(letters) for i in range(length))
        return result_str
        
    def load(self) -> List[Document]:
        """Load file."""
        import fitz
        doc = fitz.open(self.file_path)  # open document
        file_path = self.file_path if self.web_path is None else self.web_path
        # full_dir_path = os.path.join(os.path.dirname(file_path), "temp_files")
        if not os.path.exists(config.OCR_TEMP_DIR):
            os.makedirs(config.OCR_TEMP_DIR)
       
        result = []
        for page in doc:
            page_content = self._page_ocr(page)
            if len(page_content) > 0:
                metadata = {
                    "source": file_path,
                    "file_path": file_path,
                    "page_number": page.number + 1,
                    "total_pages": len(doc),
                }
                metadata.update({k: doc.metadata[k] for k in doc.metadata if type(doc.metadata[k]) in [str, int]})
                document = Document(
                    page_content=page_content,
                    metadata=metadata
                )
                result.append(document)
        return result

        
 
  
    def _page_ocr(self, page):
        zoom_x, zoom_y = 2, 2
        matrix = fitz.Matrix(zoom_x, zoom_y)
        image = page.get_pixmap(matrix=matrix)
        output_path = os.path.join(config.OCR_TEMP_DIR, str(uuid.uuid4())+".jpg")
        # 以 PNG 格式将图像保存到指定的输出文件夹中
        image.save(output_path)
        result = self._ocr_txt(output_path)
        return "".join(result)
    
    def _ocr_txt(self, img_name):
        # result = self._ocr_local(img_name)
        result = self._ocr_online(img_name)
        os.remove(img_name)
        return result


    def _ocr_local(self, img_name):
        from paddleocr import PaddleOCR
        ocr = PaddleOCR(lang="ch", use_gpu=False, show_log=True)
        result = ocr.ocr(img_name)
        ocr_result = [i[1][0] for line in result for i in line]
        return ocr_result
    
    def _ocr_online(self, file_name):
        with open(file_name, "rb") as f:
            paras = {"file": f}
            response = requests.post(config.OCR_URL, files=paras)

        if response.status_code == 200:
            return json.loads(response.text)['text']
        else:
            return ""
        
         
def loadDocsFromPDF(file_path:str, chunk_size = 300, chunk_overlap = 20) ->List[Document]:
    textsplitter = ChineseTextSplitter(pdf=True, 
                                       sentence_size= config.SENTENCE_SIZE, 
                                       chunk_size= chunk_size, 
                                       chunk_overlap= chunk_overlap)
    processed_docs = []
    if is_scanned_pdf(file_path):
        loader = PyMuPDFOCRLoader(file_path)
    else:
        loader = PyMuPDFLoader(file_path)
        
    try:
        docs = loader.load()
        page_idx =0
        for d in docs:
            page_idx = page_idx + 1
            d.page_content = f"<PAGE:{page_idx}/PAGE>" + d.page_content

        text = "".join([doc.page_content for doc in docs])
        results = textsplitter.split_text(text=text)
        
        # 定义正则表达式
        # pattern = r'—\s*(\d{1,4})\s*—'
        pattern = r'<PAGE:(\d+)/PAGE>'
        processed_docs = []
        pre_numbers = ""
        for text_chunk in results:
            # 使用 re.findall() 函数查找所有符合条件的数字
            matches = re.findall(pattern, text_chunk)
            if matches:
                page_numbers = ",".join(matches)
                pre_numbers = page_numbers
            else:
                page_numbers = pre_numbers.split(",")[-1]
            
            # 移除匹配到的页码
            text_chunk = re.sub(pattern, "", text_chunk)
            
            # # 提取第一个匹配到的页码，如果存在的话
            # first_page_number = int(page_numbers.split(',')[0]) if page_numbers else 1
            
            doc = Document(page_content=text_chunk,
                           metadata=dict({
                               "source": file_path.split('/')[-1],
                               "file_path": file_path,
                               "page_numbers": page_numbers,
                           },)
                          )
            processed_docs.append(doc)
        
        # split_docs = textsplitter.split_documents(docs)
        # for d in split_docs:
        #     pattern = r'—\s*(\d{1,4})\s*—'
        #     doc = Document(page_content=re.sub(pattern, "", d.page_content),
        #                         metadata={
        #                             "source": file_path.split('/')[-1],
        #                             "file_path": file_path,
        #                             "page_number": d.metadata['page'],
        #                         }
        #                   )
        #     processed_docs.append(doc)
    except Exception as e:
        print("加载过程中发生错误:", e)
        raise e    
    return processed_docs

def loadDocsFromPDF2(textsplitter, file_path:str, chunk_size = 300, chunk_overlap = 20) ->List[Document]:
    processed_docs = []
    if is_scanned_pdf(file_path):
        loader = PyMuPDFOCRLoader(file_path)
    else:
        loader = PyMuPDFLoader(file_path)       
    try:
        docs = loader.load()
        text = "".join([doc.page_content for doc in docs])
        results = textsplitter.split_text(text=text)
        processed_docs = []
        pre_numbers = ""
        page_numbers = ""
        pattern = r'—\s*(\d{1,4})\s*—'
        for text_chunk in results:
            # 移除匹配到的页码
            text_chunk = re.sub(pattern, "", text_chunk)
            doc = Document(page_content=text_chunk,
                           metadata=dict({
                               "source": file_path.split('/')[-1],
                               "file_path": file_path,
                               "page_numbers": page_numbers,
                           },)
                          )
            processed_docs.append(doc)       
    except Exception as e:
        print("加载过程中发生错误:", e)
        raise e    
    return processed_docs

def is_scanned_pdf(filepath):
    # 打开PDF文件
    pdf_document = fitz.open(filepath)

    # 遍历PDF的每一页
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        # 检查该页是否有文本内容
        if page.get_text():
            # 如果有文本内容，则说明不是扫描版PDF
            pdf_document.close()
            return False

    # 如果所有页面都没有文本内容，则可能是扫描版PDF
    pdf_document.close()
    return True
        

    
if __name__ == "__main__":
    # os.environ.setdefault("LLP_DEV", True)
    pdf_path = "/Users/llp/llm/chatdoc-server/content/客规/广九客段乘发〔2020〕81号 广九客运段关于发布《广九客运段铁路运输技术规章管理实施细则》的通知.pdf"
    print(f"{pdf_path} is exists {os.path.exists(pdf_path)}")
    textsplitter = ChineseProvisionsSplitter(pdf=True)
    docs = loadDocsFromPDF2(textsplitter= textsplitter,
                            file_path= pdf_path,
                            chunk_size= config.CHUNK_SIZE, 
                            chunk_overlap= config.CHUNK_OVERLAP)
    # textsplitter = ChineseTextSplitter(pdf=True, sentence_size = 100, chunk_size = 1000, chunk_overlap = 20)
    # p_docs = textsplitter.split_documents(docs)
    for doc in docs :
        # print(doc)
        page_numbers = doc.metadata["page_numbers"]
        content = doc.page_content
        print(f"content = {content}")
        
    