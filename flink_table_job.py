from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment
import requests
import json
import time

# Flink 실행 환경 설정
env = StreamExecutionEnvironment.get_execution_environment()
t_env = StreamTableEnvironment.create(env)

# 데이터를 가져오는 함수
def fetch_data():
    url = "http://host.docker.internal:5000/data"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return json.loads(response.text)
    except Exception as e:
        print(f"Error fetching data: {e}")
    return []

# Flask 데이터 소스
class FlaskDataSource:
    def __iter__(self):
        while True:
            data = fetch_data()
            for row in data:
                yield row
            time.sleep(1)

# Flink Table 생성 (DDL 방식 사용)
t_env.execute_sql("""
    CREATE TABLE actions (
        user_id INT,
        action STRING,
        amount DOUBLE,
        event_time BIGINT,
        proc_time AS PROCTIME()
    ) WITH (
        'connector' = 'datagen', -- 데이터 소스는 실제 Kafka, Filesystem 등으로 변경 가능
        'rows-per-second' = '10'
    )
""")

# DataStream 변환
ds = env.from_collection(FlaskDataSource())
table = t_env.from_data_stream(ds, ["user_id", "action", "amount", "timestamp"])

# 집계 쿼리 실행
result_table = t_env.sql_query("""
    SELECT
        action,
        COUNT(*) AS action_count,
        SUM(amount) AS total_amount,
        TUMBLE_START(proc_time, INTERVAL '10' SECOND) AS window_start
    FROM actions
    GROUP BY action, TUMBLE(proc_time, INTERVAL '10' SECOND)
""")

# 결과 출력
t_env.to_append_stream(result_table).print()

# Flink Job 실행
env.execute("Flink Streaming Analysis")

