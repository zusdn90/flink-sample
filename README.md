## 실시간 데이터 처리 예제 (Flask + PyFlink)
- 이 예제에서는 Flask 애플리케이션을 이용해 실시간 데이터를 생성하고, PyFlink를 사용하여 해당 데이터를 처리하는 구조를 구현합니다.

## 시스템 구성도
- [ Flask (data-producer) ]  --->  [ PyFlink Job ]  --->  [ 결과 출력 ]

1.Flask 서버 (data-producer)
  - 1초마다 랜덤 데이터를 생성하여 /data API로 제공
  - Docker 컨테이너로 실행됨

2.PyFlink Job (flink-job)
  - HTTP Source를 사용하여 Flask API에서 데이터를 가져옴
  - JSON 데이터를 파싱하여 user_id, action, amount, timestamp 추출
  - 특정 행동(click, view, purchase)을 카운팅하여 실시간 분석 수행
  - 결과를 콘솔에 출력

## 실행 결과 예시
- 실시간 데이터가 아래와 같이 처리됩니다.

(click, 10)
(view, 7)
(purchase, 3)
(click, 15)
(view, 10)
