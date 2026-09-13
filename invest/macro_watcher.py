#!/usr/bin/env python3
"""
CRFX 投資工具 — 宏觀監視 + 金美元背馳檢測
產生 invest/macro-report.md，每日/按需運行。

用 yfinance 撈數據，唔需要 API key。
"""

import datetime
from pathlib import Path

import yfinance as yf  # type: ignore[import-untyped]

HERE = Path(__file__).resolve().parent
OUT = HERE / "macro-report.md"


# ---------- helpers ----------

def rsi(closes, period=14):
    if len(closes) < period + 1:
        return None
    gains, losses = [], []
    for i in range(1, len(closes)):
        d = closes[i] - closes[i - 1]
        gains.append(max(d, 0.0))
        losses.append(max(-d, 0.0))
    avg_g = sum(gains[:period]) / period
    avg_l = sum(losses[:period]) / period
    if avg_l == 0:
        return 100.0
    for i in range(period, len(gains)):
        avg_g = (avg_g * (period - 1) + gains[i]) / period
        avg_l = (avg_l * (period - 1) + losses[i]) / period
    return round(100 - 100 / (1 + avg_g / avg_l), 1)


def sma(lst, n):
    if len(lst) < n:
        return None
    return round(sum(lst[-n:]) / n, 2)


def pct_chg(lst):
    if len(lst) < 2:
        return None
    return round((lst[-1] - lst[-2]) / lst[-2] * 100, 2)


def range_pos(lst):
    if len(lst) < 2:
        return 50
    hi, lo = max(lst), min(lst)
    if hi == lo:
        return 50
    return round((lst[-1] - lo) / (hi - lo) * 100, 0)


def fetch(ticker, window="90d"):
    try:
        h = yf.Ticker(ticker).history(period=window)
        if h.empty:
            return None
        closes = [float(c) for c in h["Close"]]
        return closes
    except Exception:
        return None


# ---------- main ----------

def main():
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    assets = {
        "金期貨 (GC=F)":       ("GC=F",     "金 — XAU/USD 期貨"),
        "金ETF (GLD)":         ("GLD",     "金上場基金"),
        "銀期貨 (SLV)":        ("SLV",     "銀 — XAG/USD"),
        "美元指數 (DXY)":      ("DX-Y.NYB","美元指數"),
        "S&P 500 (SPY)":       ("SPY",     "美股基準"),
        "NASDAQ 100 (QQQ)":    ("QQQ",     "科技主導指數"),
        "10年期美債 (^TNX)":   ("^TNX",    "長期利率（%）"),
        "長期美債 ETF (TLT)":  ("TLT",     "長期美債 ETF"),
        "比特幣 (BTC-USD)":    ("BTC-USD", "比特幣美金價"),
        "VIX 恐慌指數 (^VIX)": ("^VIX",    "股市波動率指數"),
    }

    out = [f"# 宏觀一覽 — {ts}", ""]

    data = {}
    for label, (sym, desc) in assets.items():
        closes = fetch(sym, "90d")
        if closes is None:
            out.append(f"## {label}")
            out.append(f"_無數據（{desc}）_")
            out.append("")
            continue
        data[label] = {"sym": sym, "desc": desc, "closes": closes}

    # 金 & 美元要喺度先算背馺
    gold = data.get("金期貨 (GC=F)")
    dollar = data.get("美元指數 (DXY)")

    if gold and dollar:
        # 聯合為同一天
        g = gold["closes"]
        d = dollar["closes"]
        ml = min(len(g), len(d))
        g, d = g[-ml:], d[-ml:]
        # 簡易 rolling correlation (90 日)
        if len(g) >= 20:
            import statistics
            corr_30 = None
            corr_90 = None
            if len(g) >= 30:
                shorter = min(len(g), 30)
                corr_30 = _corr(g[-shorter:], d[-shorter:])
            if len(g) >= 90:
                corr_90 = _corr(g, d)
        else:
            corr_30 = corr_90 = None

        # 背馺檢測
        g_rsi = rsi(g)
        d_rsi = rsi(d)
        divergence = ""
        if g_rsi and d_rsi:
            # 金新高但美元也新高，且 RSI 背離
            g_hi = max(g[-10:])
            g_lo = min(g[-10:])
            g_at_top = g[-1] >= g_hi * 0.995
            d_at_top = d[-1] >= max(d[-10:]) * 0.995
            if g_at_top and d_at_top and g_rsi < 65 and d_rsi > 45:
                divergence += "⚠️ **背離訊號**：金創近期高位，但 RSI 未跟上（動量相對較弱）。美元同時偏強，常見金後半段回調。”\n\n"
            # 金 USD 正常情況：金 UP + 美元 DOWN = 正常
        out.append(f"## 金 vs 美元背離檢測\n")
        out.append(f"- 金 RSI(14): **{g_rsi}**（過買/過賣閥值 75/25）\n")
        out.append(f"- 美元指數 RSI(14): **{d_rsi}**\n")
        out.append(f"- 30日相關係數: {corr_30 if corr_30 else '不足資料'}\n")
        out.append(f"- 90日相關係數: {corr_90 if corr_90 else '不足資料'}\n")
        out.append(f"- 背景：金與美元 normally 冇正相關（甚至負）。若兩者一齊上升，代表有額外購買力推動金（央行買入、避險等）。\n")
        out.append(f"- 訊號：{divergence if divergence else '無明顯背離'}\n")
        out.append("")

    # 逐 asset 寫
    for label, info in data.items():
        c = info["closes"]
        price = c[-1]
        chg = pct_chg(c)
        sma20 = sma(c, 20)
        sma50 = sma(c, 50)
        r = rsi(c)
        rp = range_pos(c)

        # 推算趨勢
        trend = "中性"
        if sma20 and sma50:
            if price > sma20 > sma50:
                trend = "偏多"
            elif price < sma20 < sma50:
                trend = "偏跌"

        flags = []
        if r is not None:
            if r >= 75:
                flags.append("RSI 偏高（>75）")
            elif r <= 25:
                flags.append("RSI 偏低（<25）")
        if sma20 and price < sma20:
            flags.append("跌穿 SMA20")
        if sma20 and price > sma20:
            flags.append("站上 SMA20")
        if rp >= 85:
            flags.append("近3月高位")
        elif rp <= 15:
            flags.append("近3月低位")

        unit = ""
        if label.startswith("10年"):
            unit = " %"
        elif "金" in label:
            unit = " $/oz"
        elif "美元" in label:
            unit = ""
        else:
            unit = " $"

        out.append(f"## {label}")
        out.append(f"{info['desc']}\n")
        out.append(f"| 價格 | 1日 | RSI(14) | SMA20 | SMA50 | 半年位置 | 趨勢 | 訊號 |")
        out.append(f"|------|-----|---------|-------|-------|----------|------|------|")
        flag_txt = ", ".join(flags) if flags else "—"
        out.append(
            f"| {price:.2f}{unit} | {chg:+.2f}% | {r} | {sma20} | {sma50} | {rp}% | {trend} | {flag_txt} |"
        )
        out.append("")

    # 金季節性小貼士（簡單）
    month = datetime.date.today().month
    seasonal_note = ""
    if month in (9, 10):
        seasonal_note = (
            "\n## 季節性提示（金）\n"
            f"現時 {month} 月。歷史數據顯示 8 月下旬至 9 月係金價上升時期之一（8月下旬→9月持續上升至年底）。"
            "但每年受宏觀因素影響，季節性僅供參考。\n"
        )
    elif month == 12:
        seasonal_note = (
            "\n## 季節性提示（金）\n"
            "現時 12 月。歷史研究指 12 月中至 2 月底係金最強上漲季節之一。"
            "過往 12 月中常係可靠入場點。\n"
        )
    elif month == 3:
        seasonal_note = (
            "\n## 季節性提示（金）\n"
            "現時 3 月。歷史顯示 3 月係金最平值月（cheapest month），部分年份係低吸機會。\n"
        )
    if seasonal_note:
        out.append(seasonal_note)

    out.append(f"_產生時間：{ts}_")
    OUT.write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out))


def _corr(a, b):
    """簡易 Pearson correlation."""
    n = len(a)
    ma = sum(a) / n
    mb = sum(b) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = sum((x - ma) ** 2 for x in a) ** 0.5
    db = sum((y - mb) ** 2 for y in b) ** 0.5
    if da == 0 or db == 0:
        return None
    return round(num / (da * db), 3)


if __name__ == "__main__":
    main()
