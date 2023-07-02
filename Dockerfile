FROM  chatglm-api:latest
LABEL MAINTAINER="chatGLM"

#COPY . /chatGLM/

WORKDIR /chatGLM

#RUN apt-get update -y && apt-get install python3 python3-pip curl -y  && apt-get clean
#RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py 

#RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn && rm -rf `pip3 cache dir`
RUN pip3 install PyPDF2 filetype pymilvus -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn && rm -rf `pip3 cache dir`

CMD ["python3","-u", "main.py"]
