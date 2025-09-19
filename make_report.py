# make_report.py
# reports/daily_summary.csv 를 읽어
# 1) 날짜별 종가 라인차트
# 2) 일일 변동(종가-시가) 막대 차트
# 를 reports/ 아래 PNG로 저장

import os
import csv
from datetime import datetime
import matplotlib.pyplot as plt

SUMMARY_CSV = "reports/daily_summary.csv"

def read_summary(path=SUMMARY_CSV):
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path}가 없습니다. run_loop.py가 하루 이상 돌아간 뒤에 생성됩니다.")
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            # date,ticker,open,high,low,close,entry_count,exit_count
            rows.append({
                "date": datetime.strptime(r["date"], "%Y-%m-%d"),
                "ticker": r["ticker"],
                "open": float(r["open"]),
                "high": float(r["high"]),
                "low": float(r["low"]),
                "close": float(r["close"]),
                "entry_count": int(r["entry_count"]),
                "exit_count": int(r["exit_count"]),
            })
    rows.sort(key=lambda x: x["date"])
    return rows

def save_price_curve(rows, out_path="reports/summary_price_curve.png"):
    dates  = [r["date"]  for r in rows]
    closes = [r["close"] for r in rows]

    plt.figure()
    plt.plot(dates, closes, label="Close")
    plt.title("Daily Close")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"✅ 저장: {out_path}")

def save_change_bars(rows, out_path="reports/summary_change_bars.png"):
    dates   = [r["date"] for r in rows]
    changes = [r["close"] - r["open"] for r in rows]

    plt.figure()
    plt.bar(dates, changes, label="Close - Open")
    plt.title("Daily Change (Close - Open)")
    plt.xlabel("Date")
    plt.ylabel("Change")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"✅ 저장: {out_path}")

if __name__ == "__main__":
    rows = read_summary()
    if len(rows) < 1:
        raise RuntimeError("daily_summary.csv에 데이터가 없습니다.")
    save_price_curve(rows)
    save_change_bars(rows)
