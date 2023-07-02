from pathlib import Path
from langchain.text_splitter import CharacterTextSplitter
from modelscope.outputs import OutputKeys
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import re
from typing import List
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class AliTextSplitter(CharacterTextSplitter):
    def __init__(self, pdf: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.pdf = pdf
        self.pipeline = pipeline(
            task="document-segmentation",
            model='damo/nlp_bert_document-segmentation_chinese-base',
            device="gpu:1")
 

    def split_text(self, text: str) -> List[str]:
        # use_document_segmentation参数指定是否用语义切分文档，此处采取的文档语义分割模型为达摩院开源的nlp_bert_document-segmentation_chinese-base，论文见https://arxiv.org/abs/2107.09278
        # 如果使用模型进行文档语义切分，那么需要安装modelscope[nlp]：pip install "modelscope[nlp]" -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html
        # 考虑到使用了三个模型，可能对于低配置gpu不太友好，因此这里将模型load进cpu计算，有需要的话可以替换device为自己的显卡id
        if self.pdf:
            text = re.sub(r"\n{3,}", r"\n", text)
            text = re.sub('\s', " ", text)
            text = re.sub("\n\n", "", text)
            # 使用正则表达式替换两个字符中间的换行符
            text = re.sub(r'(\w)\n(\w)', r'\1\2', text)
            #去除两个中文字之间的空格
            text = re.sub(r'([\u4e00-\u9fa5])\s([\u4e00-\u9fa5])', r'\1\2', text)
            
        result = self.pipeline(documents=text)
        splits = [i for i in result["text"].split("\n\t") if i]
        
        blank_pattern = re.compile('\s+')  # 匹配一个或多个空格
        _good_splits = []
        final_chunks = []
        for s in splits:
            s = blank_pattern.sub('', s)
            if self._length_function(s) < self._chunk_size:
                _good_splits.append(s)
            else:
                if _good_splits:
                    merged_text = self._merge_splits(_good_splits, "\n")
                    final_chunks.extend(merged_text)
                    _good_splits = []
                other_info = self.split_text(s)
                final_chunks.extend(other_info)
        if _good_splits:
            merged_text = self._merge_splits(_good_splits, "\n")
            final_chunks.extend(merged_text)
        return final_chunks
        
        

if __name__ == "__main__":

    # #filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), "content", "source", "1-中国铁路广州局集团有限公司企业年金财务管理办法.pdf")
    # filepath = "/apps/docs/文件上传测试/铁路车号自动识别系统AEI设备管理检修运行规程.pdf"
    # # filepath = "tmp/1-中国铁路广州局集团有限公司企业年金财务管理办法.pdf"
    # docs = loadDocsFromPDF(filepath)
    # print(docs)
    file_path = Path(__file__).parent.parent / "content/a1.txt"
    with open(file_path) as f:
        doc = f.read()
    splitter = AliTextSplitter(chunk_size = 2000, chunk_overlap = 200)
    results = splitter.split_text(text = doc)
    merge_text = splitter._merge_splits(results, '')
    for m in merge_text:
        print(f"######\n{m}")

    # results = splitter.split_text(text = doc)
    # merge_text = splitter._merge_splits(results, '')
    # for m in merge_text:
    #     print(f"######\n{m}")

    # results = splitter.split_text(text = doc)
    # merge_text = splitter._merge_splits(results, '')
    # for m in merge_text:
    #     print(f"######\n{m}")
