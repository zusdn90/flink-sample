from flask import Flask, jsonify
import threading
import time
import random

app = Flask(__name__)

# 전역 리스트에 데이터를 저장
generated_data = []

def generate_data():
    """ 1초마다 랜덤한 JSON 데이터를 생성 """
    global generated_data
    while True:
        data = {
            "user_id": random.randint(1, 100),
            "action": random.choice(["click", "view", "purchase"]),
            "amount": round(random.uniform(1.0, 100.0), 2),
            "timestamp": int(time.time())
        }
        print("generate data", data)
        if len(generated_data) >= 100:  # 최근 100개 데이터만 유지
            generated_data.pop(0)
        generated_data.append(data)
        time.sleep(1)

# 백그라운드 스레드 실행
thread = threading.Thread(target=generate_data, daemon=True)
thread.start()

@app.route('/data', methods=['GET'])
def get_data():
    """ 저장된 데이터를 반환하는 API """
    return jsonify(generated_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

