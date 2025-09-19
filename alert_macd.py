# alert_macd.py
import time
import pyupbit
import pandas as pd
from datetime import datetime

# ===== MACD 계산 함수 =====
def calc_macd(df, short=12, long=26, signal=9):
    short_ema = df["close"].ewm(span=short).mean()
    long_ema = df["close"].ewm(span=long).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal).mean()
    return macd, signal_line

# ===== 시그널 체크 함수 =====
def check_signal(interval="minute60"):
    df = pyupbit.get_ohlcv("XRP", interval=interval, count=200)

    macd, signal_line = calc_macd(df)
    hist = macd - signal_line
    df["MACD"] = macd
    df["Signal"] = signal_line
    df["Hist"] = hist
    df["MA5"] = df["close"].rolling(5).mean()

    prev, curr = df.iloc[-2], df.iloc[-1]

    # 1) 파랑→핑크 전환
    if prev["Hist"] < 0 and curr["Hist"] > 0:
        print(f"[{interval}] 🔔 XRP MACD 골든크로스 (파랑→핑크 전환)")

    # 2) 핑크 상태 + 5MA 하락 전환
    elif curr["Hist"] > 0 and curr["MA5"] < prev["MA5"]:
        print(f"[{interval}] ⚠️ XRP 고점 경고 (핑크인데 5MA 하락)")

# ===== 가동 시간 제어 (자정~04:55는 휴식) =====
def is_active_time():
    now = datetime.now()
    # 00:00 <= 시각 < 05:00 은 휴식
    if 0 <= now.hour < 5:
        # 단, 04:55 이후면 작동 시작
        if now.hour == 4 and now.minute >= 55:
            return True
        return False
    return True

# ===== 정각 체크 =====
def is_on_the_hour():
    now = datetime.now()
    return now.minute == 0

# ===== 메인 루프 =====
if __name__ == "__main__":
    print("🚀 XRP MACD 알림 봇 시작")
    while True:
        try:
            if is_active_time() and is_on_the_hour():
                check_signal("minute60")   # 60분봉
            time.sleep(60)   # 1분마다 확인
        except Exception as e:
            print("에러:", e)
            time.sleep(60)