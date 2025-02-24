from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.typeinfo import Types
import requests
import json
import time

# JSON 데이터를 파싱하는 함수
def parse_json(json_str):
    data = json.loads(json_str)
    return (data["user_id"], data["action"], data["amount"], data["timestamp"])

# HTTP 데이터를 가져오는 함수
def fetch_data_from_http():
    while True:
        response = requests.get('http://data-producer:5000/data')  # Flask API 호출
        if response.status_code == 200:
            yield response.text  # API에서 받은 데이터를 반환
        time.sleep(5)  # 5초마다 HTTP 요청

# PyFlink에서 HTTP 소스를 가져오는 방법
def main():
    env = StreamExecutionEnvironment.get_execution_environment()

    # HTTP 요청을 받아오는 스트리밍 데이터 생성
    data_stream = env.from_collection(fetch_data_from_http(), type_info=Types.STRING())
    print("data stream: ", data_stream)    

    # JSON 데이터를 파싱
    parsed_stream = data_stream.map(lambda x: parse_json(x), output_type=Types.TUPLE([Types.INT(), Types.STRING(), Types.FLOAT(), Types.LONG()]))
    print("parse stream: ", parsed_stream) 

    # 사용자 행동 통계 생성 (예: 특정 행동 카운트)
    action_counts = parsed_stream \
        .map(lambda x: (x[1], 1), output_type=Types.TUPLE([Types.STRING(), Types.INT()])) \
        .key_by(lambda x: x[0]) \
        .sum(1)
    print("action count: ", action_counts)

    # 콘솔에 출력
    action_counts.print()

    # 실행 시작
    env.execute("Flink Real-Time Processing")

if __name__ == "__main__":
    main()

