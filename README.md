# CRFX Arcade

自己做起嚟嘅小遊戲，全部放喺同一個網址。

- 冇廣告、冇追蹤、冇內購
- 每隻遊戲都係**單一 HTML 檔**，零依賴，離線玩到
- 冇 build step —— 掉個資料夾入去就出到街

---

## 結構

```
crfx-arcade/
├── index.html          ← 遊戲機大廳（自動讀 games.js 生成卡片）
├── games.js            ← 遊戲清單（唯一需要改嘅檔）
├── README.md
└── games/
    └── bubble-rush/    ← 遊戲 1
        ├── index.html
        └── preview-orientation.html
```

---

## 點加一隻新遊戲

```
① 開個資料夾         games/<遊戲 id>/
② 放入去              index.html（入口檔一定要叫呢個名）
③ 喺 games.js 加一筆
④ 完 —— 冇 build、冇 npm、冇編譯
```

### 例子

```js
{
  id:       "my-game",
  title:    "My Game",
  title_zh: "我嘅遊戲",
  tagline:  "一句話介紹。",
  path:     "games/my-game/index.html",
  accent:   "#ffd93d",        // 卡片主色
  emoji:    "🎮",             // 冇縮圖時顯示
  players:  "1人",
  minutes:  "5分鐘",
  orientation: "both",
  status:   "playable",       // playable | wip | soon
  tags:     ["益智"],
  added:    "2026-09-12",
}
```

### GDevelop 都放得入

GDevelop export HTML5 → 掉個資料夾入 `games/` → 加一筆就得。
即係兩條 track（自己寫 / GDevelop）最後都收埋喺同一個大廳。

---

## 為何用 `games.js` 而唔係 `games.json`

`<script src>` 喺 `file://` 之下照跑，但 `fetch()` 會被 CORS 擋。

用 `.js` 嘅話，**雙擊 `index.html` 就開到**，唔使起 server —— 方便本地測試同埋派俾人。

---

## 本地測試

```bash
cd crfx-arcade
python3 -m http.server 8000
# 開 http://localhost:8000
```

或者直接雙擊 `index.html`。

---

## 部署

靜態網站，任何 static host 都得：

| Host | 自訂 domain | 私人 repo | 免費額度 |
|------|------------|----------|---------|
| Cloudflare Pages | ✅ | ✅ | 無限流量 |
| GitHub Pages | ✅ | ❌（要 public 或 Pro）| 100GB/月 |
| Netlify | ✅ | ✅ | 100GB/月 |

---

## 之後會加

- 帳號 / 班級代碼（老師開班 → 出一個碼 → 小朋友入碼歸班）
- 排行榜
- 每日挑戰（全世界同一 seed）
- 遊戲內積分（append-only ledger）

詳見 Jira `CRFXPJ-28`（Epic）。
