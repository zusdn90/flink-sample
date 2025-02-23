# Flink 공식 이미지 사용
FROM flink:1.16.1

# 작업 디렉토리 설정
WORKDIR /app

# 필수 패키지 설치
RUN apt-get update && \
    apt-get install -y python3 python3-pip openjdk-11-jdk && \
    pip3 install apache-flink==1.16.1

# JDK 환경 변수 설정
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# JDK의 include 폴더가 필요한 위치에 존재하도록 심볼릭 링크 생성
RUN mkdir -p /opt/java/openjdk && \
    ln -s $JAVA_HOME/include /opt/java/openjdk/include

# JDK include 디렉터리 확인
RUN ls -al /opt/java/openjdk/include

# 애플리케이션 코드 복사
COPY . .

# Flink 및 Flask API 포트 개방
EXPOSE 8081 5000

# Flink 애플리케이션 실행
CMD ["python3", "flink_job.py"]

