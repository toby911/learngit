import re
from logging import Logger
from pathlib import Path
from typing import Any, Iterable, List, Optional

from langchain.text_splitter import (CharacterTextSplitter,
                                     RecursiveCharacterTextSplitter)


class ChineseTextSplitter(CharacterTextSplitter):
    def __init__(self, pdf: bool = False, sentence_size=100, **kwargs):
        super().__init__(**kwargs)
        self.sentence_size = sentence_size
        self.pdf = pdf
    def split_text(self, text: str) -> List[str]:   ##此处需要进一步优化逻辑
        if self.pdf:
            text = re.sub(r"\n{3,}", r"\n", text)
            text = re.sub('\s', " ", text)
            text = re.sub("\n\n", "", text)
            text = re.sub(r'(\.{8})', " ", text)  #  去除目录页的连续句点

        text = re.sub(r'([;；.!?。！？\?])([^”’])', r"\1\n\2", text)  # 单字符断句符
        text = re.sub(r'(\.{6})([^"’”」』])', r"\1\n\2", text)  # 英文省略号
        text = re.sub(r'(\…{2})([^"’”」』])', r"\1\n\2", text)  # 中文省略号
        text = re.sub(r'([;；!?。！？\?]["’”」』]{0,2})([^;；!?，。！？\?])', r'\1\n\2', text)
        # 使用正则表达式替换两个字符中间的换行符
        text = re.sub(r'(\w)\n(\w)', r'\1\2', text)
        #去除两个中文字之间的空格
        text = re.sub(r'([\u4e00-\u9fa5])\s([\u4e00-\u9fa5])', r'\1\2', text)

        # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
        text = text.rstrip()  # 段尾如果有多余的\n就去掉它
        # 很多规则中会考虑分号;，但是这里我把它忽略不计，破折号、英文双引号等同样忽略，需要的再做些简单调整即可。
        ls = [i for i in text.split("\n") if i]
        for ele in ls:
            if len(ele) > self.sentence_size:
                ele1 = re.sub(r'([,，.]["’”」』]{0,2})([^,，.])', r'\1\n\2', ele)
                ele1_ls = ele1.split("\n")
                for ele_ele1 in ele1_ls:
                    if len(ele_ele1) > self.sentence_size:
                        ele_ele2 = re.sub(r'([\n]{1,}| {2,}["’”」』]{0,2})([^\s])', r'\1\n\2', ele_ele1)
                        ele2_ls = ele_ele2.split("\n")
                        for ele_ele2 in ele2_ls:
                            if len(ele_ele2) > self.sentence_size:
                                ele_ele3 = re.sub('( ["’”」』]{0,2})([^ ])', r'\1\n\2', ele_ele2)
                                ele2_id = ele2_ls.index(ele_ele2)
                                ele2_ls = ele2_ls[:ele2_id] + [i for i in ele_ele3.split("\n") if i] + ele2_ls[ele2_id + 1:]
                        ele_id = ele1_ls.index(ele_ele1)
                        ele1_ls = ele1_ls[:ele_id] + [i for i in ele2_ls if i] + ele1_ls[ele_id + 1:]

                id = ls.index(ele)
                ls = ls[:id] + [i for i in ele1_ls if i] + ls[id + 1:]
        chunks = self._merge_splits(ls, '')
        return chunks


class ChineseRecursivePDFSplitter(RecursiveCharacterTextSplitter):
    """Implementation of splitting text that looks at characters.
    Recursively tries to split by different characters to find one
    that works.
    """

    def __init__(self, separators: Optional[List[str]] = None, **kwargs: Any):
        """Create a new TextSplitter."""
        super().__init__(**kwargs)
        self._separators = separators or ["\n\n", "\n", " ", ""]

    def split_text(self, text: str) -> List[str]:
        """Split incoming text and return chunks."""
        text = re.sub(r"\n{3,}", "\n", text)
        text = re.sub('\s', ' ', text)
        text = text.replace("\n\n", "")
        sent_sep_pattern = re.compile('([﹒﹔﹖﹗．。！？]["’”」』]{0,2}|(?=["‘“「『]{1,2}|$))')  # del ：；
        blank_pattern = re.compile('\s+')  # 匹配一个或多个空格
        final_chunks = []
        # Get appropriate separator to use
        separator = self._separators[-1]
        for _s in self._separators:
            if _s == "":
                separator = _s
                break
            if _s in text:
                separator = _s
                break
        # Now that we have the separator, split the text
        if separator:
            splits = text.split(separator)
        else:
            splits = list(text)
        # Now go merging things, recursively splitting longer texts.
        _good_splits = []
        for s in splits:
            s = blank_pattern.sub('', s)
            if self._length_function(s) < self._chunk_size:
                _good_splits.append(s)
            else:
                if _good_splits:
                    merged_text = self._merge_splits(_good_splits, separator)
                    final_chunks.extend(merged_text)
                    _good_splits = []
                other_info = self.split_text(s)
                final_chunks.extend(other_info)
        if _good_splits:
            merged_text = self._merge_splits(_good_splits, separator)
            final_chunks.extend(merged_text)
        return final_chunks

class ChineseProvisionsSplitter(CharacterTextSplitter):
    def __init__(self, pdf: bool = False, sentence_size=100, **kwargs):
        super().__init__(**kwargs)
        self.sentence_size = sentence_size
        self.pdf = pdf
    
    def split_paragraphs(self, text: str):
        # 使用正则表达式匹配“第x条”
        pattern = r'(第[一二三四五六七八九十百]+条)'
        
        # 使用split函数分割字符串
        parts = re.split(pattern, text)
        
        # 将相邻的两个元素（即“第x条”和对应的内容）组合在一起
        parts = [parts[n] + '  ' + parts[n+1] for n in range(1, len(parts)-1, 2)]
        processed_p = []
        for p in parts:
            # 使用正则表达式将数字序号后的换行符替换为空格
            clean_text = re.sub(r'(\d)\.\n', r'\1. ', p)
            # 使用replace函数去除不必要的换行符
            clean_text = clean_text.replace("\n\n", "\n")
            processed_p.append(clean_text)
        return processed_p
        
    def split_text(self, text: str) -> List[str]:   ##此处需要进一步优化逻辑
        if self.pdf:
            text = re.sub(r"\n{3,}", r"\n", text)
            text = re.sub('\s', " ", text)
            text = re.sub("\n\n", "", text)
            text = re.sub(r'(\.{8})', " ", text)  #  去除目录页的连续句点

        text = re.sub(r'([;；.!?。！？\?])([^”’])', r"\1\n\2", text)  # 单字符断句符
        text = re.sub(r'(\.{6})([^"’”」』])', r"\1\n\2", text)  # 英文省略号
        text = re.sub(r'(\…{2})([^"’”」』])', r"\1\n\2", text)  # 中文省略号
        text = re.sub(r'([;；!?。！？\?]["’”」』]{0,2})([^;；!?，。！？\?])', r'\1\n\2', text)
        # 使用正则表达式替换两个字符中间的换行符
        text = re.sub(r'(\w)\n(\w)', r'\1\2', text)
        #去除两个中文字之间的空格
        text = re.sub(r'([\u4e00-\u9fa5])\s([\u4e00-\u9fa5])', r'\1\2', text)

        # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
        text = text.rstrip()  # 段尾如果有多余的\n就去掉它

        # 按照每一条分割
        chunks = self.split_paragraphs(text)
        

        return chunks


if __name__ == '__main__':
    from langchain.document_loaders import (DirectoryLoader, PyMuPDFLoader,
                                            PyPDFLoader,
                                            UnstructuredFileLoader)
    pdf_path = "/apps/docs/铁路车号自动识别系统AEI设备管理检修运行规程.pdf"
    
    loader = PyMuPDFLoader(pdf_path)
    # loader = DirectoryLoader(document)
    textsplitter = ChineseTextSplitter(pdf=True, sentence_size = 100, chunk_size = 1000, chunk_overlap = 20)
    # textsplitter = ChineseRecursivePDFSplitter(chunk_size = 2000, chunk_overlap = 200)
    docs = loader.load_and_split(textsplitter)
    # docs = textsplitter.split_documents(docs)
    print(len(docs))
    for doc in docs:
        print(f"###  length = {len(doc.page_content)}   ###\n metadata = {doc.metadata} \n page_content = {doc.page_content}")
        print("###### length=", len(doc.page_content))
