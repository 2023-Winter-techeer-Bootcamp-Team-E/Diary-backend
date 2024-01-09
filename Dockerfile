FROM python:3.11

# Python은 가끔 소스 코드를 컴파일할 때 확장자가 .pyc인 파일을 생성한다.
# 도커를 이용할 때, .pyc 파일이 필요하지 않으므로 .pyc 파일을 생성하지 않도록 한다.
ENV PYTHONDONTWRITEBYTECODE 1
# Python 로그가 버퍼링 없이 출력
ENV PYTHONUNBUFFERED 1

# 이미지에 내에서 명령을 실행할 때 사용할 기본 작업 디렉토리를 설정
WORKDIR /backend

RUN pip install --upgrade pip

#현재 로컬 디렉토리에 있는 requirements.txt를 컨테이너 안의 /backend/ 디렉토리에 복사
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY haruProject/ .
COPY haruProject/.env ./

## Django 프로젝트 실행
#EXPOSE 8000
#
#CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
