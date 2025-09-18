# run_loop.py
# 매 60초마다 업비트 XRP 데이터를 갱신하고
# MACD+SMA200 복합전략의 최신 Entry/Exit 신호를 콘솔로 알림 (드라이런)

import time
import os
from fetch_upbit import main as fetch_prices
from backtest import load_price_data, calc_macd, calc_sma
from strategies.macd_strategy import macd_with_ma_filter

TICKER = "KRW-XRP"
INTERVAL_SEC = 60
STATE_FILE = "reports/last_signal.txt"  # 마지막 알림 상태 저장

def read_last_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

def write_last_state(s):
    os.makedirs("reports", exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(s)

def check_signal():
    # 1) 최신 데이터 갱신
    fetch_prices()  # data/price.csv 업데이트

    # 2) 지표 계산
    df = load_price_data("data/price.csv")
    df = calc_macd(df)
    df = calc_sma(df, 200)

    # 3) 복합전략 신호
    combo = macd_with_ma_filter(df)
    last = combo.tail(1).iloc[0]

    # 4) 상태 변화가 있을 때만 알림
    state = "NONE"
    if last["Entry"]:
        state = "ENTRY"
    elif last["Exit"]:
        state = "EXIT"

    prev = read_last_state()
    if state and state != prev:
        price = float(last["Close"])
        print(f"[{TICKER}] {state} 신호 - 종가: {price:,.0f}")
        write_last_state(state)
    else:
        print(f"[{TICKER}] 변화 없음 (유지)")

def main():
    print("=== DRYRUN 루프 시작 (Ctrl+C 로 종료) ===")
    while True:
        try:
            check_signal()
        except Exception as e:
            print("ERROR:", e)
        time.sleep(INTERVAL_SEC)

if __name__ == "__main__":
    main()