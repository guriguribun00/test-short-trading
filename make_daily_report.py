# make_daily_report.py
# daily_summary.csv + 생성된 차트들을 한 장의 리포트 PNG/PDF로 합치기

import os
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

SUMMARY_CSV = "reports/daily_summary.csv"
PRICE_CURVE = "reports/summary_price_curve.png"
CHANGE_BARS = "reports/summary_change_bars.png"
COMBO_CHART = "reports/price_with_combo.png"   # 있으면 썸네일로 넣음(선택)
OUT_PNG     = "reports/daily_report.png"
OUT_PDF     = "reports/daily_report.pdf"

def read_summary_rows(path=SUMMARY_CSV):
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path}가 없습니다. run_loop.py가 하루 이상 돌아간 뒤 생성됩니다.")
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append({
                "date": datetime.strptime(row["date"], "%Y-%m-%d"),
                "ticker": row["ticker"],
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "entry_count": int(row["entry_count"]),
                "exit_count": int(row["exit_count"]),
            })
    rows.sort(key=lambda x: x["date"])
    return rows

def latest_summary(rows):
    return rows[-1] if rows else None

def build_report():
    rows = read_summary_rows()
    last = latest_summary(rows)
    if not last:
        raise RuntimeError("daily_summary.csv에 데이터가 없습니다.")

    # 리포트 캔버스 레이아웃
    fig = plt.figure(figsize=(11.7, 8.3), dpi=150)  # A4 가로 비슷한 비율
    gs = gridspec.GridSpec(3, 4, figure=fig, wspace=0.5, hspace=0.6)

    # (1) 헤더 / 요약 박스
    ax1 = fig.add_subplot(gs[0, :])
    ax1.axis("off")
    title = f"Daily Report - {last['ticker']}  ({last['date'].strftime('%Y-%m-%d')})"
    stats = (
        f"Open: {last['open']:.0f}   High: {last['high']:.0f}   "
        f"Low: {last['low']:.0f}   Close: {last['close']:.0f}   "
        f"Change: {last['close']-last['open']:+.0f}\n"
        f"ENTRY: {last['entry_count']}   EXIT: {last['exit_count']}"
    )
    ax1.text(0.01, 0.72, title, fontsize=16, weight="bold", va="top")
    ax1.text(0.01, 0.35, stats, fontsize=12, va="top")

    # (2) 좌측 큰 패널: 종가 추이
    ax2 = fig.add_subplot(gs[1:, :2])
    if os.path.exists(PRICE_CURVE):
        img = plt.imread(PRICE_CURVE)
        ax2.imshow(img)
        ax2.axis("off")
        ax2.set_title("Daily Close Curve", pad=6)
    else:
        ax2.text(0.5, 0.5, "summary_price_curve.png 없음", ha="center", va="center")
        ax2.axis("off")

    # (3) 우측 상단: 일일 변동 막대
    ax3 = fig.add_subplot(gs[1, 2:])
    if os.path.exists(CHANGE_BARS):
        img = plt.imread(CHANGE_BARS)
        ax3.imshow(img)
        ax3.axis("off")
        ax3.set_title("Daily Change (Close - Open)", pad=6)
    else:
        ax3.text(0.5, 0.5, "summary_change_bars.png 없음", ha="center", va="center")
        ax3.axis("off")

    # (4) 우측 하단: 콤보 차트 썸네일(선택)
    ax4 = fig.add_subplot(gs[2, 2:])
    if os.path.exists(COMBO_CHART):
        img = plt.imread(COMBO_CHART)
        ax4.imshow(img)
        ax4.axis("off")
        ax4.set_title("Price + SMA200 with MACD Entries/Exits", pad=6)
    else:
        ax4.text(0.5, 0.5, "price_with_combo.png 없음(선택)", ha="center", va="center")
        ax4.axis("off")

    # 저장
    os.makedirs("reports", exist_ok=True)
    fig.suptitle("", y=0.99)  # 기본 여백 조절
    plt.tight_layout()
    fig.savefig(OUT_PNG)
    fig.savefig(OUT_PDF)
    plt.close(fig)

    print(f"✅ 리포트 저장: {OUT_PNG}")
    print(f"✅ 리포트 저장: {OUT_PDF}")

if __name__ == "__main__":
    build_report()
