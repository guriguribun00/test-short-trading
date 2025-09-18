def macd_cross_signals(df):
    df["Prev_diff"] = (df["MACD"] - df["Signal"]).shift(1)
    df["Curr_diff"] = df["MACD"] - df["Signal"]

    df["GoldenCross"] = (df["Prev_diff"] <= 0) & (df["Curr_diff"] > 0)
    df["DeadCross"] = (df["Prev_diff"] >= 0) & (df["Curr_diff"] < 0)

    signals = df[(df["GoldenCross"]) | (df["DeadCross"])]
    return signals[["Close", "MACD", "Signal", "GoldenCross", "DeadCross"]]

def macd_with_ma_filter(df, ma_col="SMA200"):
    """
    룰:
       - 진입: MACD 골든크로스 AND 종가가 200일선 위
       - 청산: MACD 데드크로스
       - 반환: 기존 컬럼 + Entry(매수신호), Exit(매도신호)
    """
    out = df.copy()
    out["Prev_diff"] = (out["MACD"] - out["Signal"]).shift(1)
    out["Curr_diff"] = out["MACD"] - out["Signal"]

    out["GoldenCross"] = (out["Prev_diff"] <= 0) & (out["Curr_diff"] > 0)
    out["DeadCross"] = (out["Prev_diff"] >= 0) & (out["Curr_diff"] < 0)
    
    #200일선 필터
    above_ma = out["Close"] > out[ma_col]
    
    out["Entry"] = out["GoldenCross"] & above_ma
    out["Exit"] = out["DeadCross"]

    cols = ["Close", "MACD", "Signal", ma_col, "GoldenCross", "DeadCross", "Entry", "Exit"]
    return out[cols]