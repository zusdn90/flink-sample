from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, DataTypes
from pyflink.table.udf import udf
from pyflink.datastream.functions import SourceFunction
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

# Flink 커스텀 HTTP Source Function
class HttpSourceFunction(SourceFunction):
    def __init__(self):
        self.running = True  # 스트림 실행 상태 변수

    def run(self, ctx):
        while self.running:
            try:
                response = requests.get('http://data-producer:5000/data')  # Flask API 호출
                if response.status_code == 200:
                    ctx.collect(response.text)  # 데이터를 Flink 스트림에 추가
                time.sleep(5)  # 5초마다 HTTP 요청
            except Exception as e:
                print(f"Error fetching data: {e}")

    def cancel(self):
        self.running = False  # 스트림을 중단하도록 플래그 설정

# Flink 실행 함수
def main():
    env = StreamExecutionEnvironment.get_execution_environment()
    table_env = StreamTableEnvironment.create(env)

    # HTTP Source 추가
    data_stream = env.add_source(HttpSourceFunction())

    # 데이터 스트림을 PyFlink Table로 변환
    table = table_env.from_data_stream(data_stream, DataTypes.STRING())

    # UDF 등록
    table_env.create_temporary_function("parse_json", parse_json)

    # JSON 파싱 및 테이블 변환
    table_env.create_temporary_view("input_table", table)
    parsed_table = table_env.sql_query("SELECT parse_json(f0) FROM input_table")

    # 사용자 행동 카운트 집계
    action_counts = (
        parsed_table
        .group_by("f0.action")
        .select("f0.action, COUNT(f0.action) AS action_count")
    )

    # Console Sink 생성
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

if __name__ == "__main__":
    main()

