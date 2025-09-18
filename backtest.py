import pandas as pd
import matplotlib.pyplot as plt

# CSV 예시 파일: data/price.csv
# 형식: Date,Open,High,Low,Close,Volume (Date는 YYYY-MM-DD)

def load_price_data(filepath="data/price.csv"):
    df = pd.read_csv(filepath, parse_dates=["Date"])
    df.sort_values("Date", inplace=True)
    df.set_index("Date", inplace=True)
    return df

def calc_macd(df, short=12, long=26, signal=9):
    df["EMA12"] = df["Close"].ewm(span=short, adjust=False).mean()
    df["EMA26"] = df["Close"].ewm(span=long, adjust=False).mean()
    df["MACD"] = df["EMA12"] - df["EMA26"]
    df["Signal"] = df["MACD"].ewm(span=signal, adjust=False).mean()
    df["Hist"] = df["MACD"] - df["Signal"]
    return df

def calc_sma(df, window=200):
    df[f"SMA{window}"] = df["Close"].rolling(window=window, min_periods=1).mean()
    return df

if __name__ == "__main__":
    try:
        from strategies.macd_strategy import macd_cross_signals, macd_with_ma_filter
        import os
        import matplotlib.pyplot as plt

        df = load_price_data()
        df = calc_macd(df)
        df = calc_sma(df, 200)

        # 1) 크로스 신호 추출
        signals = macd_cross_signals(df)

        # 2) reports 폴더 생성
        os.makedirs("reports", exist_ok=True)

        # 3) CSV 저장
        out_path = "reports/signals.csv"
        signals.to_csv(out_path, encoding="utf-8")
        print(f"\n✅ CSV 저장 완료: {out_path}")

        # 4) 차트 저장
        golden_idx = signals.index[signals["GoldenCross"] == True]
        dead_idx   = signals.index[signals["DeadCross"]   == True]

        plt.figure()
        plt.plot(df.index, df["Close"], label="Close")
        plt.scatter(golden_idx, df.loc[golden_idx, "Close"], marker="^", label="GoldenCross")
        plt.scatter(dead_idx,   df.loc[dead_idx,   "Close"], marker="v", label="DeadCross")
        plt.title("Price with MACD Cross Signals")
        plt.legend()
        plt.tight_layout()
        plt.savefig("reports/price_with_signals.png", dpi=150)
        plt.close()

        plt.figure()
        plt.plot(df.index, df["MACD"],   label="MACD")
        plt.plot(df.index, df["Signal"], label="Signal")
        plt.bar(df.index, df["Hist"], label="Hist")
        plt.title("MACD / Signal / Histogram")
        plt.legend()
        plt.tight_layout()
        plt.savefig("reports/macd_panel.png", dpi=150)
        plt.close()

        print("✅ 차트 저장 완료: reports/price_with_signals.png, reports/macd_panel.png")

    except FileNotFoundError:
        print("⚠️ data/price.csv 파일이 없습니다. 먼저 CSV 데이터를 넣어주세요.")