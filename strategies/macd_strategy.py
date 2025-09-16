def macd_cross_signals(df):
    df["Prev_diff"] = (df["MACD"] - df["Signal"]).shift(1)
    df["Curr_diff"] = df["MACD"] - df["Signal"]

    df["GoldenCross"] = (df["Prev_diff"] <= 0) & (df["Curr_diff"] > 0)
    df["DeadCross"] = (df["Prev_diff"] >= 0) & (df["Curr_diff"] < 0)

    signals = df[(df["GoldenCross"]) | (df["DeadCross"])]
    return signals[["Close", "MACD", "Signal", "GoldenCross", "DeadCross"]]