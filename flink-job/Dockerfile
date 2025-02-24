FROM flink:1.0

# 작업 디렉토리 설정
WORKDIR /app

# 필수 패키지 설치
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y software-properties-common && \
    apt-get install -y python3 python3-pip

# PyFlink 설치
RUN pip3 install pyflink requests

# 애플리케이션 코드 복사
COPY . .

# PyFlink 실행
CMD ["flink","run","-m","jobmanager:8081","--python","flink_job.py"]
