FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /project/app

 # 设置容器内工作目录
WORKDIR /project/app

 # 将当前目录文件拷贝一份到工作目录中（. 表示当前目录）
ADD . /project/app

 # 利用 pip 安装依赖
RUN pip install -r requirements.txt
RUN chmod 777 /project/app/media

#安装nginx
RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx && \
    rm -rf /var/lib/apt/lists/* && \
    rm /etc/nginx/nginx.conf
RUN useradd nginx -G www-data
COPY nginx.conf /etc/nginx/nginx.conf

ENV DATABASE_USER=root
ENV DATABASE_PASSWORD=123456
ENV DATABASE_HOST=localhost
ENV DATABASE_PORT=3306

EXPOSE 8000

CMD python manage.py makemigrations && python manage.py migrate && uwsgi --ini /project/app/uwsgi.ini && service nginx start
