FROM python:3.8
MAINTAINER HospitalBackend
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /project/app

 # 设置容器内工作目录
WORKDIR /project/app

 # 将当前目录文件拷贝一份到工作目录中（. 表示当前目录）
ADD . /project/app

 # 利用 pip 安装依赖
RUN pip install -r requirements.txt
RUN chmod 777 /project/app/media

ENV DATABASE_USER=root
ENV DATABASE_PASSWORD=123456
ENV DATABASE_HOST=localhost
ENV DATABASE_PORT=3306

EXPOSE 8000

CMD python manage.py makemigrations && python manage.py migrate && uwsgi --ini /project/app/uwsgi.ini
