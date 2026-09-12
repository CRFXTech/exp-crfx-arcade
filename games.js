/* ============================================================
   CRFX Arcade — game manifest
   ------------------------------------------------------------
   This is a .js file and not .json ON PURPOSE:
   <script src> works over file:// , fetch() does not.
   So the hub opens correctly when you just double-click it.

   TO ADD A GAME (works for Bubble Rush, GDevelop exports, anything):
     1. drop it in  games/<id>/index.html
     2. add an entry below
     3. done — no build step
   ============================================================ */

window.GAMES = [
  {
    id:       "bubble-rush",
    title:    "Bubble Rush",
    title_zh: "泡泡衝刺",
    tagline:  "按住上升，放開下墜。穿過空隙、收集星星、避開尖刺。",
    tagline_en: "Hold to rise, release to fall. Thread the gaps.",
    path:     "games/bubble-rush/index.html",
    thumb:    null,                       // null = 用自動生成嘅縮圖
    accent:   "#5ce1e6",
    emoji:    "🫧",
    players:  "1人",
    minutes:  "1-3分鐘",
    orientation: "landscape",
    status:   "playable",                 // playable | wip | soon
    tags:     ["街機", "單鍵操作", "小朋友", "高分挑戰"],
    added:    "2026-09-11",
  },
  {
    id:       "cat-planet",
    title:    "貓咪星球",
    title_zh: "貓咪星球",
    tagline:  "8×8 格放 8 隻貓，行、列、鄰近全唔得撞。",
    tagline_en: "Place 8 cats on an 8x8 grid — no same row, column, or adjacent.",
    path:     "games/cat-planet/index.html",
    thumb:    null,
    accent:   "#FFB7C5",
    emoji:    "🐱",
    players:  "1人",
    minutes:  "3-5分鐘",
    orientation: "both",
    status:   "playable",
    tags:     ["解謎", "小朋友", "休閒", "貓咪", "邏輯"],
  },

/* ---- 下面係樣板，加新遊戲照抄 ---- */
  // {
  //   id:       "my-gdevelop-game",
  //   title:    "My Game",
  //   title_zh: "我嘅遊戲",
  //   tagline:  "一句話介紹。",
  //   path:     "games/my-gdevelop-game/index.html",
  //   accent:   "#ffd93d",
  //   emoji:    "🎮",
  //   players:  "1人",
  //   minutes:  "5分鐘",
  //   orientation: "both",
  //   status:   "wip",
  //   tags:     ["益智"],
  //   added:    "2026-09-12",
  // },
];
