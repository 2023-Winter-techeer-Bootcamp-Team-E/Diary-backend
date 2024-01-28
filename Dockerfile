FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /backend

RUN pip install --upgrade pip

# U-2-Net 모델 다운로드 및 포함,     rembg다운로드 시간이 너무 길어서 단축용
RUN mkdir -p /root/.u2net \
    && curl -L -o /root/.u2net/u2net.onnx https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY haruProject/ .
COPY haruProject/.env ./

# EXPOSE 8000

# Django 프로젝트 실행
# CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
