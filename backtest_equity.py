# backtest_equity.py
# MACD+SMA200 Entry/Exit 신호로 가상 매매 → 누적 수익률/잔고곡선 계산

import os
import matplotlib.pyplot as plt
import pandas as pd
from backtest import load_price_data, calc_macd, calc_sma
from strategies.macd_strategy import macd_with_ma_filter

DATA_PATH = "data/price.csv"
OUT_EQUITY = "reports/equity_curve.png"

INIT_CASH = 1_000_000  # 초기자본 (원)

def run_backtest():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"{DATA_PATH} 없음")

    # 1) 데이터 불러오기
    df = load_price_data(DATA_PATH)
    df = calc_macd(df)
    df = calc_sma(df, 200)

    # 2) 전략 신호 계산
    signals = macd_with_ma_filter(df)

    # 3) 포지션/잔고 계산
    cash = INIT_CASH
    coin = 0
    equity_list = []

    position = None
    entry_price = 0

    for date, row in signals.iterrows():
        price = row["Close"]

        # 매수 신호 (Entry)
        if row["Entry"] and position is None:
            coin = cash / price
            cash = 0
            position = "LONG"
            entry_price = price

        # 매도 신호 (Exit)
        elif row["Exit"] and position == "LONG":
            cash = coin * price
            coin = 0
            position = None

        # 현재 평가금액
        equity = cash + coin * price
        equity_list.append({"Date": date, "Equity": equity})

    equity_df = pd.DataFrame(equity_list).set_index("Date")

    # 4) 성과 지표 계산
    total_return = equity_df["Equity"].iloc[-1] / INIT_CASH - 1
    equity_df["Peak"] = equity_df["Equity"].cummax()
    equity_df["Drawdown"] = equity_df["Equity"] / equity_df["Peak"] - 1
    mdd = equity_df["Drawdown"].min()

    print("=== 백테스트 결과 ===")
    print(f"초기 자본: {INIT_CASH:,.0f}원")
    print(f"최종 자본: {equity_df['Equity'].iloc[-1]:,.0f}원")
    print(f"총 수익률: {total_return*100:.2f}%")
    print(f"최대 낙폭(MDD): {mdd*100:.2f}%")

    # 5) Equity Curve 차트 저장
    plt.figure()
    plt.plot(equity_df.index, equity_df["Equity"], label="Equity")
    plt.fill_between(equity_df.index, 
                     equity_df["Equity"], 
                     equity_df["Peak"], 
                     color="red", alpha=0.3, label="Drawdown")
    plt.title("Equity Curve (MACD + SMA200)")
    plt.xlabel("Date")
    plt.ylabel("Equity (원)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_EQUITY, dpi=150)
    plt.close()
    print(f"✅ Equity Curve 저장: {OUT_EQUITY}")

if __name__ == "__main__":
    run_backtest()
