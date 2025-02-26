import requests
import json
from pyflink.datastream import StreamExecutionEnvironment

def fetch_data_from_api(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API 호출 실패: 상태 코드 {response.status_code}")

def transform_data(data):
    transformed_data = []
    for item in data:
        transformed_data.append((item['user_id'], json.dumps(item)))
    return transformed_data

def process_data(element):
    user_id, json_str = element
    data = json.loads(json_str)
    return user_id, data['action'], data['amount'], data['timestamp']

api_url = "http://data-producer:5000/data"  # 실제 API 엔드포인트로 변경
data = fetch_data_from_api(api_url)

env = StreamExecutionEnvironment.get_execution_environment()
transformed_data = transform_data(data)
ds = env.from_collection(collection=transformed_data)

result = ds.map(process_data)
result.print()

env.execute("API Data Processing")
