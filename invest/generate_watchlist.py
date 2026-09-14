#!/usr/bin/env python3
# 生成 watchlist.html — 純增長版投資觀察名單
import json, os

# 讀 JSON
with open('/shared/invest/watchlist_technical.json', encoding='utf-8') as f:
    tech = json.load(f)
with open('/shared/invest/backtest-pointintime-2023.json', encoding='utf-8') as f:
    bt = json.load(f)

# 建立回測 lookup（合併 strict + relaxed，去重）
seen = set()
bt_lookup = {}
for item in bt.get('strict', []) + bt.get('relaxed', []):
    t = item['ticker']
    if t not in seen:
        seen.add(t)
        bt_lookup[t] = item

bench = bt.get('bench', 0)

def generate_clues(t):
    clues = []
    price = t['price']
    ma50 = t['ma50']
    ma200 = t['ma200']
    rsi = t['rsi']
    macd_hist = t['macd']['histogram']
    vol_ratio = t['volume']['ratio_20d']

    if rsi > 70:
        clues.append('RSI>70 超買 → 警惕回調')
    if rsi < 30 and price > ma200:
        clues.append('RSI<30 超賣 + 價格喺 MA200 上方 → 觀察低吸')
    if macd_hist > 0:
        clues.append('MACD 柱狀轉正 → 多頭動能')
    if vol_ratio > 1.2:
        clues.append(f'放量 ({vol_ratio:.2f}x) → 波動放大，注意方向')
    if not clues:
        return '常規觀察'
    return ' | '.join(clues)

def clue_parts_html(clues_str):
    parts = clues_str.split(' | ')
    out = []
    for p in parts:
        cls = ''
        if '超買' in p:
            cls = 'warn'
        elif '超賣' in p:
            cls = 'good'
        elif '多頭' in p:
            cls = 'good'
        elif '放量' in p:
            cls = 'warn'
        if cls:
            out.append(f'<span class="{cls}">{p}</span>')
        else:
            out.append(f'<span>{p}</span>')
    return '\n'.join(out)

# 合併 31 隻股票數據（按回報降序）
combined = []
for t in tech:
    ticker = t['ticker']
    if ticker in bt_lookup:
        bt_item = bt_lookup[ticker]
        combined.append({
            'ticker': ticker,
            'name': t['name'],
            'ret3y': bt_item['ret3y'],
            'eps_g': bt_item['eps_g'],
            'margin': bt_item['margin'],
            'mcap': bt_item['mcap'],
            'tech': t,
        })
combined.sort(key=lambda x: x['ret3y'], reverse=True)

# ── CSS（沿用 invest/index.html 風格） ──
css = '''
  :root {
    --bg: #0d1117;
    --fg: #e6edf3;
    --muted: #8b949e;
    --accent: #58a6ff;
    --card: #161b22;
    --border: #30363d;
    --warn: #f0883e;
    --good: #3fb950;
    --tag-bg: rgba(88,166,255,0.12);
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    background: var(--bg);
    color: var(--fg);
    padding: 1.5rem;
    line-height: 1.6;
  }
  .container { max-width: 1100px; margin: 0 auto; }
  header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
  }
  h1 { font-size: 1.5rem; margin: 0; font-weight: 600; }
  .subtitle { color: var(--muted); font-size: 0.9rem; margin-top: 0.25rem; }
  .header-right { display: flex; gap: 0.75rem; align-items: center; }
  .header-info {
    color: var(--muted);
    font-size: 0.8rem;
    background: var(--card);
    padding: 0.35rem 0.7rem;
    border-radius: 6px;
    border: 1px solid var(--border);
  }
  .card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.25rem;
    margin-bottom: 1.25rem;
    page-break-inside: avoid;
  }
  .card h3 {
    margin: 0 0 0.75rem 0;
    font-size: 1.05rem;
    font-weight: 600;
  }
  .card .desc { color: var(--muted); font-size: 0.85rem; margin: 0 0 0.75rem 0; }
  .section-meta {
    color: var(--muted);
    font-size: 0.85rem;
    background: rgba(139,148,158,0.08);
    border-left: 3px solid var(--accent);
    padding: 0.6rem 0.9rem;
    margin: 0.75rem 0;
    border-radius: 0 6px 6px 0;
  }
  .section-meta strong { color: var(--fg); }
  .table-wrap {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
  }
  th, td {
    text-align: left;
    padding: 0.55rem 0.6rem;
    border-bottom: 1px solid var(--border);
    vertical-align: top;
  }
  th {
    color: var(--muted);
    font-weight: 600;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    background: rgba(139,148,158,0.05);
    white-space: nowrap;
  }
  tr:last-child td { border-bottom: none; }
  .ticker { font-weight: 600; color: var(--accent); }
  .good { color: var(--good); }
  .warn { color: var(--warn); }
  .muted { color: var(--muted); }
  .pos { color: var(--good); }
  .neg { color: var(--warn); }
  .clues { font-size: 0.82rem; color: var(--muted); }
  .clues span { display: block; margin-bottom: 0.2rem; }
  .footer {
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
    color: var(--muted);
    font-size: 0.8rem;
    text-align: center;
  }
  @media (max-width: 700px) {
    body { padding: 1rem; }
    table { font-size: 0.8rem; }
    th, td { padding: 0.4rem 0.4rem; }
  }
'''

# ── 頁首 ──
header = f'''
<!DOCTYPE html>
<html lang="zh-HK">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>投資觀察名單 | CRFX</title>
<style>{css}</style>
</head>
<body>
<div class="container">
  <header>
    <div>
      <h1>{{'📊 純增長版投資觀察名單'}}</h1>
      <div class="subtitle">31 隻股票 · 回測 + 技術綜合清單 · 觀察用</div>
    </div>
    <div class="header-right">
      <span class="header-info">數據更新：2026-09-13</span>
    </div>
  </header>

  <div class="section-meta">
    <strong>篩選條件：</strong>EPS 增長 >15% + 淨利率 >15% + 市值 >50B &nbsp;|&nbsp;
    <strong>回測基準：</strong>2023-09-03 → 2026-09-13 · SPY 同期 +69.4% &nbsp;|&nbsp;
    <strong>統計：</strong>正回報 25 隻（81%）· 跑贏 SPY 11 隻 · 平均回報 +77.3% · 中位數 +48.9%
  </div>
'''

# ── 表一：回測表現 + 基本面 ──
table1_rows = []
for item in combined:
    ticker = item['ticker']
    name = item['name']
    ret = item['ret3y']
    eps_g = item['eps_g']
    margin = item['margin']
    mcap = item['mcap']

    ret_str = f"{ret*100:+.1f}%"
    ret_cls = 'pos' if ret > 0 else 'neg'
    beat_spy = ret > bench
    beat_str = f"✓ (+{(ret-bench)*100:.1f}%)" if beat_spy else f"✗ ({(ret-bench)*100:.1f}%)"
    beat_cls = 'good' if beat_spy else 'muted'
    eps_str = f"{eps_g*100:.1f}%"
    margin_str = f"{margin*100:.1f}%"
    mcap_str = f"${mcap/1e9:.1f}B"

    table1_rows.append(f'''
            <tr>
              <td><span class="ticker">{ticker}</span></td>
              <td>{name}</td>
              <td class="{ret_cls}">{ret_str}</td>
              <td class="{beat_cls}">{beat_str}</td>
              <td>{eps_str}</td>
              <td>{margin_str}</td>
              <td>{mcap_str}</td>
            </tr>''')

table1 = f'''
  <div class="card">
    <h3>一、回測表現 + 基本面（2023-09-03 → 2026-09-13）</h3>
    <div class="desc">按 3 年回報降序排列，包含 EPS 增長、淨利率、市值等基本面指標。</div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>股票</th>
            <th>名稱</th>
            <th>3年回報</th>
            <th>跑贏 SPY</th>
            <th>EPS 增長</th>
            <th>淨利率</th>
            <th>市值</th>
          </tr>
        </thead>
        <tbody>
          {''.join(table1_rows)}
        </tbody>
      </table>
    </div>
  </div>
'''

# ── 表二：技術 + 成交量 + Target Price ──
table2_rows = []
for t in tech:
    ticker = t['ticker']
    price = t['price']
    r52 = t['range_52w']
    ma50 = t['ma50']
    ma200 = t['ma200']
    rsi = t['rsi']
    macd_hist = t['macd']['histogram']
    vol_ratio = t['volume']['ratio_20d']
    tgt = t['targets']

    price_str = f"${price:.2f}"
    range_str = f"${r52['low']:.2f}–${r52['high']:.2f}"

    ma50_dir = "上" if price > ma50 else "下"
    ma50_str = f"${ma50:.2f} ({ma50_dir})"
    ma50_cls = 'good' if price > ma50 else 'muted'

    ma200_dir = "上" if price > ma200 else "下"
    ma200_str = f"${ma200:.2f} ({ma200_dir})"
    ma200_cls = 'good' if price > ma200 else 'muted'

    rsi_str = f"{rsi:.0f}"
    rsi_cls = 'good' if rsi < 30 else ('warn' if rsi > 70 else '')

    macd_str = f"{macd_hist:+.2f}"
    macd_cls = 'good' if macd_hist > 0 else 'muted'

    vol_str = f"{vol_ratio:.2f}x"
    vol_cls = 'warn' if vol_ratio > 1.2 else ''

    supp_str = f"${tgt['support']:.2f}"
    base_str = f"${tgt['base']:.2f}"
    resid_str = f"${tgt['resistance']:.2f}"

    clues_str = generate_clues(t)
    clues_html = clue_parts_html(clues_str)

    table2_rows.append(f'''
            <tr>
              <td><span class="ticker">{ticker}</span></td>
              <td>{price_str}</td>
              <td class="muted">{range_str}</td>
              <td class="{ma50_cls}">{ma50_str}</td>
              <td class="{ma200_cls}">{ma200_str}</td>
              <td class="{rsi_cls}">{rsi_str}</td>
              <td class="{macd_cls}">{macd_str}</td>
              <td class="{vol_cls}">{vol_str}</td>
              <td style="color:var(--good);">{supp_str}</td>
              <td class="muted">{base_str}</td>
              <td style="color:var(--warn);">{resid_str}</td>
              <td class="clues">{clues_html}</td>
            </tr>''')

table2 = f'''
  <div class="card">
    <h3>二、技術 + 成交量 + Target Price（2026-09-13）</h3>
    <div class="desc">即時技術指標、成交量相對均線倍數、52週高低三等分 Target Price 參考位置。</div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>股票</th>
            <th>股價</th>
            <th>52週</th>
            <th>MA50</th>
            <th>MA200</th>
            <th>RSI</th>
            <th>MACD 柱</th>
            <th>成交量<br>(20日倍)</th>
            <th>Support</th>
            <th>Base</th>
            <th>Resistance</th>
            <th>簡易線索</th>
          </tr>
        </thead>
        <tbody>
          {''.join(table2_rows)}
        </tbody>
      </table>
    </div>
  </div>
'''

# ── 使用說明 ──
usage = '''
  <div class="card">
    <h3>三、點樣用呢個清單</h3>
    <div class="desc">參考流程，幫手快速篩選值得深入研究嘅股票。</div>
    <div style="font-size:0.9rem;">
      <div style="margin-bottom:0.75rem;">
        <strong>1. 先看回報 + 跑贏 SPY</strong>：
        篩選出歷史表現較強、基本面穩健嘅股。
      </div>
      <div style="margin-bottom:0.75rem;">
        <strong>2. 再看技術位置</strong>：
        <ul style="margin:0.25rem 0 0 1.2rem;">
          <li>股價喺 MA200 上方 + RSI&lt;30：可能係回調做多機會。</li>
          <li>股價喺 MA50/MA200 下方 + RSI&gt;70：超買警惕，唔適合追高。</li>
          <li>MACD 柱狀轉正：動能剛轉強，留意確認。</li>
        </ul>
      </div>
      <div style="margin-bottom:0.75rem;">
        <strong>3. Target Price 作為參考</strong>：
        Support 附近考慮觀察，Resistance 附近 caution。
      </div>
      <div>
        <strong>4. 成交量放大</strong>（20日倍 &gt;1.2x）：
        代表市場注意，配合方向用。
      </div>
    </div>
    <div class="section-meta" style="margin-top:1rem;">
      <strong>備註：</strong>技術數據係基於 yfinance 歷史數據， target price 係 52週高低三等分簡化位置，唔係嚴謹的技術分析目標。用作觀察清單，唔係投資建議。
    </div>
  </div>

  <div class="footer">
    <p>投資觀察名單 · 僅供參考，唔係投資建議 · 執行決定由 Samuel 自己做</p>
  </div>
</div>
</body>
</html>
'''

# 組合 + 寫入
html = header.replace('{{' , '').replace('}}' , '') + table1 + table2 + usage

output_path = '/opt/data/games/crfx-arcade/invest/watchlist.html'
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"HTML 寫入：{output_path}")
print(f"文件大小：{len(html)} 字節")
print("完成")
