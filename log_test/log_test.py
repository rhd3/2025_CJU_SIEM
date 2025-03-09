import time 

LOG_FILE="/var/log/forigate.log"

# 수집한 로그를 원하는 대로 처리하는 함수
def process_log(log_data):
    if "attack" in log_data or "blocked" in log_data:
        print("[Warring! 경고 로그 감지]", log_data.strip())


# 실시간으로 로그 파일을 감시하여 새로운 로그가 추가되면 처리
def monitor_log():
    with open(LOG_FILE, "r") as flie:
        flie.seek(0, 2)     # 파일 끝으로 이동
        while True:
            line = flie.readline()
            if not line:
                time.sleep(0.1)
                continue
            process_log(line)

if __name__=="__main__":
    monitor_log()
