FROM python:alpine

LABEL Name=crawl_xuexi Version=1.0.1
EXPOSE 3000

WORKDIR /app
ADD . /app
RUN python3 -m pip install -r requirements.txt
CMD ["python3", "-m", "main.py"]