# fetch_upbit.py
# KRW-BTC 일봉 시세를 가져와 data/price.csv 로 저장
# columns: Date,Open,High,Low,Close,Volume

import pyupbit
import pandas as pd
import os

TICKER = "KRW-XRP"    # 필요하면 KRW-ETH 등으로 바꿔도 됨
COUNT  = 200          # 최근 200일

def main():
    os.makedirs("data", exist_ok=True)
    df = pyupbit.get_ohlcv(ticker=TICKER, interval="day", count=COUNT)
    # Upbit df: index=Datetime, columns=['open','high','low','close','volume','value']
    df = df.rename(columns={
        "open":"Open", "high":"High", "low":"Low", "close":"Close", "volume":"Volume"
    })
    df["Date"] = pd.to_datetime(df.index.date)  # YYYY-MM-DD
    out = df[["Date","Open","High","Low","Close","Volume"]].sort_values("Date")
    out.to_csv("data/price.csv", index=False, encoding="utf-8")
    print(f"✅ 저장 완료: data/price.csv  (티커: {TICKER}, 행수: {len(out)})")

if __name__ == "__main__":
    main()