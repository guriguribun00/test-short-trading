# backtest_equity.py
# MACD+SMA200 Entry/Exit + 수수료/슬리피지 + 퍼센트 손절 / 익절 → 잔고곡선

import os
import matplotlib.pyplot as plt
import pandas as pd
from backtest import load_price_data, calc_macd, calc_sma
from strategies.macd_strategy import macd_with_ma_filter

DATA_PATH   = "data/price.csv"
OUT_EQUITY  = "reports/equity_curve.png"
INIT_CASH   = 1_000_000     # 초기 자본(원)

# ===== 현실 계수 =====
FEE  = 0.0005   # 업비트 수수료 0.05% (매수/매도 각각)
SLIP = 0.0005   # 슬리피지 0.05% (원하면 0으로)

# ==== 퍼센트 손절/익절 (원하는 대로 바꾸세요) ====
STOP_PCT = 0.03   # -3% 손절
TAKE_PCT = 0.06   # +6% 익절

def run_backtest():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"{DATA_PATH} 없음")

    # 1) 데이터 & 지표
    df = load_price_data(DATA_PATH)   # columns: Date, Open, High, Low, Close, Volume
    df = calc_macd(df)
    df = calc_sma(df, 200)

    # 2) 신호 (MACD + SMA200 필터)
    sig = macd_with_ma_filter(df)     # index 가 날짜로 동일해야 함

    # 3) 포지션/잔고
    cash = INIT_CASH
    coin = 0.0
    position = None
    entry_price = None

    equity_rows = []

    for dt, row in sig.iterrows():
        px_close = float(row["Close"])
        px_high  = float(df.loc[dt, "High"])
        px_low   = float(df.loc[dt, "Low"])

        # === 매수 ===
        if row["Entry"] and position is None:
            buy_price = px * (1 + FEE + SLIP)    # 체결가(비용 반영)
            coin = cash / buy_price              # 살 수 있는 수량
            cash = 0.0
            position = "LONG"
            entry_price = buy_price
        # === 보유 중일 때 손절/일절/신호 청산 체크 ===
        elif position == "LONG":
            stop_lvl = entry_price * (1 - STOP_PCT)
            takc_lvl = entry_price * (1 + TAKE_PCT)

            exited = False

            # 1) 보수적으로: 같은 봉에서 둘 다 맞으면 '손절' 우선
            if px_low <= stop_lvl:
                sell_price = stop_lvl * (1 - FEE - SLIP)   # 손절 체결가에 비용 반영
                cash = coin * sell_price
                coin = 0.0
                position = None
                entry_price = None
                exited  = True

            elif px_high >= take_lvl:
                sell_price = take_lvl * (1 - FEE - SLIP)   # 익절 체결가에 비용 반영
                cash = coin * sell_price
                coin = 0.0
                position = None
                entry_price = None
                exited = True

            # 2) 퍼센트 조건이 걸리지 않았을 때만 MACD Exit 신호로 청산
            if (not extied) and row["Exit"]:
                sell_price = px_close * (1 - FEE - SLIP)
                cash = coin * sell_price
                coin = 0.0
                position = None
                entry_price = None
        
        # 평가자산
        equity = cash + coin * px_close
        equity_rows.append({"Date": dt, "Equity": equity})

    equity_df = pd.DataFrame(equity_rows).set_index("Date")

    # 4) 성과지표
    total_return = equity_df["Equity"].iloc[-1] / INIT_CASH - 1
    equity_df["Peak"] = equity_df["Equity"].cummax()
    equity_df["Drawdown"] = equity_df["Equity"] / equity_df["Peak"] - 1
    mdd = float(equity_df["Drawdown"].min())

    print("=== 백테스트 결과 (수수료/슬리피지 반영) ===")
    print(f"초기 자본 : {INIT_CASH:,.0f}원")
    print(f"최종 자본 : {equity_df['Equity'].iloc[-1]:,.0f}원")
    print(f"총 수익률 : {total_return*100:.2f}%")
    print(f"최대 낙폭 : {mdd*100:.2f}%")
    print(f"(적용) 수수료 {FEE*100:.3f}% | 슬리피지 {SLIP*100:.3f}%")

    # 5) 잔고곡선 저장
    os.makedirs("reports", exist_ok=True)
    plt.figure()
    plt.plot(equity_df.index, equity_df["Equity"], label="Equity")
    # 드로우다운 영역(피크 대비 하락 분)
    plt.fill_between(
        equity_df.index,
        equity_df["Equity"],
        equity_df["Peak"],
        where=(equity_df["Equity"] < equity_df["Peak"]),
        alpha=0.25,
        label="Drawdown"
    )
    plt.title("Equity Curve (MACD + SMA200, fee/slippage applied)")
    plt.xlabel("Date")
    plt.ylabel("Equity (KRW)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_EQUITY, dpi=150)
    plt.close()
    print(f"✅ Equity Curve 저장: {OUT_EQUITY}")

if __name__ == "__main__":
    run_backtest()
