from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, DataTypes
from pyflink.table.udf import udf
import requests
import json
import time

# JSON 데이터를 파싱하는 UDF
@udf(result_type=DataTypes.ROW([
    DataTypes.FIELD("user_id", DataTypes.INT()),
    DataTypes.FIELD("action", DataTypes.STRING()),
    DataTypes.FIELD("amount", DataTypes.FLOAT()),
    DataTypes.FIELD("timestamp", DataTypes.BIGINT())
]))
def parse_json(json_str: str):
    data = json.loads(json_str)
    return (data["user_id"], data["action"], data["amount"], data["timestamp"])

# HTTP 데이터를 가져오는 함수 (Generator)
def fetch_data_from_http():
    while True:
        response = requests.get('http://data-producer:5000/data')  # Flask API 호출
        if response.status_code == 200:
            yield response.text  # API에서 받은 데이터를 반환
        time.sleep(5)  # 5초마다 HTTP 요청

# Flink 실행 함수
def main():
    env = StreamExecutionEnvironment.get_execution_environment()
    table_env = StreamTableEnvironment.create(env)

    # HTTP 데이터를 Flink 스트림으로 변환
    data_stream = env.from_collection(fetch_data_from_http())

    # 데이터 스트림을 PyFlink Table로 변환
    table = table_env.from_data_stream(data_stream, DataTypes.STRING())

    # JSON 파싱 UDF 적용
    parsed_table = table.map(parse_json)

    # 사용자 행동 카운트 집계
    action_counts = (
        parsed_table
        .group_by("action")
        .select("action, COUNT(action) as action_count")
    )

    # 결과 출력 (Console Sink 사용 가능)
    table_env.execute_sql("""
        CREATE TABLE action_counts_sink (
            action STRING,
            action_count BIGINT
        ) WITH (
            'connector' = 'print'
        )
    """)

    # Sink에 데이터 삽입
    action_counts.execute_insert("action_counts_sink")

    # Flink 실행
    env.execute("Flink Table API Real-Time Processing")

if __name__ == "__main__":
    main()

