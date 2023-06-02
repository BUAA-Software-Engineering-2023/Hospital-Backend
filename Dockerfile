FROM python:3.8
MAINTAINER HospitalBackend
ENV PYTHONUNBUFFERED 1
COPY pip.conf /root/.pip/pip.conf
RUN mkdir -p /project/app

 # 设置容器内工作目录
WORKDIR /project/app

 # 将当前目录文件拷贝一份到工作目录中（. 表示当前目录）
ADD . /project/app

 # 利用 pip 安装依赖
RUN pip install -r requirements.txt

 # Windows环境下编写的start.sh每行命令结尾有多余的\r字符，需移除。
RUN sed -i 's/\r//' ./start.sh

 # 设置start.sh文件可执行权限
RUN chmod +x ./start.sh