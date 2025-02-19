from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import HttpSource
from pyflink.common.typeinfo import Types
import json

def parse_json(json_str):
    """ JSON 데이터를 파싱하는 함수 """
    data = json.loads(json_str)
    return (data["user_id"], data["action"], data["amount"], data["timestamp"])

def main():
    env = StreamExecutionEnvironment.get_execution_environment()

    # HTTP Source로 Flask API에서 데이터 가져오기
    data_stream = env.add_source(
        HttpSource("http://data-producer:5000/data"),
        Types.STRING()
    )

    # JSON 데이터를 파싱
    parsed_stream = data_stream.map(parse_json, output_type=Types.TUPLE([Types.INT(), Types.STRING(), Types.FLOAT(), Types.LONG()]))

    # 사용자 행동 통계 생성 (예: 특정 행동 카운트)
    action_counts = parsed_stream \
        .map(lambda x: (x[1], 1), output_type=Types.TUPLE([Types.STRING(), Types.INT()])) \
        .key_by(lambda x: x[0]) \
        .sum(1)

    # 콘솔에 출력
    action_counts.print()

    # 실행 시작
    env.execute("Flink Real-Time Processing")

if __name__ == "__main__":
    main()

