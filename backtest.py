import pandas as pd

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

if __name__ == "__main__":
    try:
        df = load_price_data()
        df = calc_macd(df)
        print(df.tail(10)[["Close", "MACD", "Signal", "Hist"]])
    except FileNotFoundError:
        print("⚠️ data/price.csv 파일이 없습니다. 먼저 CSV 데이터를 넣어주세요.")