# run_loop.py
# 매 60초마다 업비트 XRP 데이터를 갱신하고
# MACD+SMA200 복합전략의 최신 Entry/Exit 신호를 콘솔로 알림 + 로그 저장 + 일일 요약

import time
import os
from datetime import datetime, timedelta
from fetch_upbit import main as fetch_prices
from backtest import load_price_data, calc_macd, calc_sma
from strategies.macd_strategy import macd_with_ma_filter

TICKER = "KRW-XRP"
INTERVAL_SEC = 60

# 로그/요약 경로
LOG_DIR = "reports/logs"
DAILY_SUMMARY_CSV = "reports/daily_summary.csv"
STATE_FILE = "reports/last_state.txt"      # 마지막 알림 상태 (ENTRY/EXIT/NONE)
LAST_DAY_FILE = "reports/last_day.txt"     # 마지막으로 요약 처리한 날짜(YYYY-MM-DD)

def ensure_dirs():
    os.makedirs("reports", exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)

def now_kr():
    # 간단히 로컬 시간을 한국시간처럼 사용 (PC 시간대 기준)
    # 필요하면 timezone 라이브러리로 Asia/Seoul 명시 가능
    return datetime.now()

def log_path_for(date_obj):
    return os.path.join(LOG_DIR, f"signals_{date_obj.strftime('%Y-%m-%d')}.csv")

def read_text(path, default=""):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return default

def write_text(path, text):
    ensure_dirs()
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def append_log_row(ts, price, state):
    """하루 단위 로그 파일에 한 줄 추가"""
    ensure_dirs()
    log_path = log_path_for(ts)
    header_needed = not os.path.exists(log_path)
    with open(log_path, "a", encoding="utf-8") as f:
        if header_needed:
            f.write("timestamp,ticker,price,state\n")
        f.write(f"{ts.strftime('%Y-%m-%d %H:%M:%S')},{TICKER},{price},{state}\n")

def summarize_day(day_str):
    """해당 날짜의 로그를 읽어 일일 요약(ENTRY/EXIT 횟수, 시가/종가, 고가/저가) 생성"""
    path = os.path.join(LOG_DIR, f"signals_{day_str}.csv")
    if not os.path.exists(path):
        return None  # 로그가 없으면 요약 불가

    # 간단 파서(표준 라이브러리만 사용)
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    if len(lines) <= 1:
        return None  # 데이터 없음
    for line in lines[1:]:
        ts, ticker, price, state = line.split(",")
        rows.append((ts, ticker, float(price), state))

    if not rows:
        return None

    prices = [r[2] for r in rows]
    open_price = rows[0][2]
    close_price = rows[-1][2]
    high_price = max(prices)
    low_price = min(prices)
    entry_cnt = sum(1 for r in rows if r[3] == "ENTRY")
    exit_cnt  = sum(1 for r in rows if r[3] == "EXIT")

    # 요약 CSV에 추가(헤더 자동)
    header_needed = not os.path.exists(DAILY_SUMMARY_CSV)
    with open(DAILY_SUMMARY_CSV, "a", encoding="utf-8") as f:
        if header_needed:
            f.write("date,ticker,open,high,low,close,entry_count,exit_count\n")
        f.write(f"{day_str},{TICKER},{open_price},{high_price},{low_price},{close_price},{entry_cnt},{exit_cnt}\n")
    return {
        "date": day_str,
        "open": open_price,
        "high": high_price,
        "low": low_price,
        "close": close_price,
        "entry_count": entry_cnt,
        "exit_count": exit_cnt
    }

def check_signal_once():
    # 1) 최신 데이터 갱신
    fetch_prices()  # data/price.csv 업데이트

    # 2) 지표 계산
    df = load_price_data("data/price.csv")
    df = calc_macd(df)
    df = calc_sma(df, 200)

    # 3) 복합전략 신호
    combo = macd_with_ma_filter(df)
    last = combo.tail(1).iloc[0]

    # 4) 상태 판정
    state = "NONE"
    if last["Entry"]:
        state = "ENTRY"
    elif last["Exit"]:
        state = "EXIT"

    price = float(last["Close"])
    ts = now_kr()

    # 5) 로그 남기기 (매 루프 한 줄씩 기록)
    append_log_row(ts, price, state)

    # 6) 변화 있을 때만 콘솔 알림
    prev_state = read_text(STATE_FILE, default="")
    if state != prev_state:
        if state == "NONE":
            print(f"[{TICKER}] 변화 없음")
        else:
            print(f"[{TICKER}] {state} 신호 - 종가: {price:,.0f}  ({ts.strftime('%Y-%m-%d %H:%M:%S')})")
        write_text(STATE_FILE, state)
    else:
        print(f"[{TICKER}] 유지 - {state} (가격 {price:,.0f})")

    # 7) 날짜 바뀌면 어제자 요약 생성
    today_str = ts.strftime("%Y-%m-%d")
    last_day_done = read_text(LAST_DAY_FILE, default="")
    # 날짜가 바뀌었고, 아직 어제자 요약을 안 했다면 요약 실행
    if last_day_done != today_str:
        # 어제 날짜
        yday_str = (ts - timedelta(days=1)).strftime("%Y-%m-%d")
        summary = summarize_day(yday_str)
        if summary:
            print(f"[요약] {yday_str} → open:{summary['open']:.0f} high:{summary['high']:.0f} low:{summary['low']:.0f} close:{summary['close']:.0f} (ENTRY:{summary['entry_count']} / EXIT:{summary['exit_count']})")
        write_text(LAST_DAY_FILE, today_str)

def main():
    ensure_dirs()
    print("=== DRYRUN 루프 시작 (Ctrl+C 로 종료) ===")
    while True:
        try:
            check_signal_once()
        except Exception as e:
            print("ERROR:", e)
        time.sleep(INTERVAL_SEC)

if __name__ == "__main__":
    main()
