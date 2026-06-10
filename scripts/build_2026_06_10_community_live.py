#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from pathlib import Path


SITE_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
SOURCE_JSON = WORKSPACE_ROOT / "output/ubo-live-2026-06-10/2026-06-10_一燈UBO直播_copy.json"
EVENT_SLUG = "2026-06-10-community-live-network-hub"
EVENT_DIR = SITE_ROOT / "events" / EVENT_SLUG
TRANSCRIPT_DIR = SITE_ROOT / "transcripts" / EVENT_SLUG

PAGE_TITLE = "還沒有很厲害的時候，人脈怎麼經營"
PAGE_DESCRIPTION = "一燈在 UBO 社群晨間直播，從市場驗證、主揪角色、小群文化到借力專家，拆解還沒有很厲害時該怎麼經營人脈。"
TRANSCRIPT_NOTE = (
    "完整逐字稿依本機 Whisper large-v3-turbo 轉錄結果整理，已移除開場閒聊與結尾未完句，"
    "並修正常見錯詞。未做 speaker diarization，本頁以一燈為主要講者保守呈現。"
)
SUMMARY_ONE_LINER = (
    "這場直播把「做內容、做社群、做人脈」串成同一條線：先用市場驗證找到會回應的人，"
    "再用主揪與小群文化把流量變信任，最後才讓信任變成能導流、能合作、能成交的私域。"
)

START_CUTOFF_MS = 29_890
END_CUTOFF_MS = 2_540_000

REPLACEMENTS = {
    "正媒體": "自媒體",
    "一次媒體": "自媒體",
    "為修": "微修",
    "低層洛基": "底層邏輯",
    "雨球": "羽球",
    "主究": "主揪",
    "主鳩": "主揪",
    "阻糾": "主揪",
    "私慾": "私域",
    "Line App": "Line @",
    "Line app": "Line @",
    "寶石捷": "保時捷",
    "以毒不回": "已讀不回",
    "亂費": "浪費",
    "措施了一個": "錯失了一個",
    "School": "school",
    "school的": "school 的",
    "脆上面": "脆上面",
}

SUMMARY_HIGHLIGHTS = [
    "熱門主題不一定要從零發明；先找已被市場驗證的題目，再用自己的故事與觀點重新詮釋。",
    "AI Landing Page 不是只做漂亮畫面，而是把對方的價值、痛點與服務講得更清楚。",
    "願意承擔場地、時間、規則與邀請這些麻煩事的人，往往比最會炫耀的人更容易累積信任。",
    "小群組不是人越多越好；要有門檻、文化與參與規則，才能留下真正會互動的人。",
    "你不一定要自己是專家；只要能找到對的專家幫人解題，信任很多時候仍會回到你身上。",
    "私域不只是在做短影音後把人導進 Line @；社區主委、球場主揪、讀書會或媽媽群也都能是私域。",
    "最小市場調查可以從限時動態開始：沒人喊 +1 的題目，就先不要硬做。",
]

ACTION_CHECKLIST = [
    "先從你自己真的會持續投入的興趣或目標出發，例如健身、羽球、讀書會、喝水打卡或媽媽社群。",
    "在成立群組前先做最小市場調查，看看限時動態、貼文或現有朋友裡有沒有人真的願意回應。",
    "定下簡單但明確的參與規則，像是每月出現一次、固定回報、固定打卡，讓文化先成形。",
    "有人提問時，就算你不是專家，也先幫他找到答案；這種問題解決的回路就是信任累積。",
    "不要急著一開始就賣東西，先確認這個群體真正的需求與痛點，再決定能不能自然導到服務或合作。",
]

SECTIONS = [
    {
        "id": "section-01",
        "start_sec": 30,
        "title": "回作業、找市場：從老二哲學到 AI Landing Page",
        "tag": "市場驗證",
        "summary": "開場先回應社群成員前幾天的心得與作業。一燈強調，真正聰明的做法不是每次都從零發明題目，而是善用市場已經驗證過的需求，再用自己的觀點、故事與案例重新講一次。這也延伸到蝦皮電商驗證與 AI Landing Page：先找有需求的人，再把價值講清楚。",
        "highlights": [
            "熱門主題早就有市場需求，重點不是搶著當第一個，而是重新詮釋。",
            "做生意與做自媒體都一樣：先看搜尋量、競爭度與既有市場，再決定切入。",
            "AI Landing Page 的價值不只在畫面，而是在幫客戶把痛點講到他也能看懂。 ",
        ],
    },
    {
        "id": "section-02",
        "start_sec": 366,
        "title": "租場地不是小事：主揪其實是在累積人脈",
        "tag": "主揪角色",
        "summary": "一位朋友租籃球場的經驗，讓一燈把主題拉到「主揪」這件事。球場要抽籤、要找人、要扛責任，看起來麻煩，但也正因為如此，願意承擔這些麻煩的人，會自然變成別人要找資源時先想到的中間點。",
        "highlights": [
            "人脈不一定來自你很厲害，也可以來自你願意處理別人懶得處理的麻煩。",
            "主揪不是最會說的人，而是能把場地、時間與參與者安排好的人。",
            "只要你成為大家想到的那個節點，信任就會慢慢堆在你身上。",
        ],
    },
    {
        "id": "section-03",
        "start_sec": 630,
        "title": "人脈不是炫耀，而是成為能解題的中間人",
        "tag": "信任樞紐",
        "summary": "這段直播把人脈的本質講得很直白：不是曬車、曬收入、曬資源，而是讓別人覺得你可靠，知道有問題可以來找你。就算你自己不是專家，只要你能幫對方找到答案、找到人、把事情接起來，信任仍會回到你身上。",
        "highlights": [
            "真正的信任，常常從「我幫你問問看」這種小事開始。",
            "別人來問問題，是建立信任最好的機會，不要急著把他打發回網路或 AI。",
            "你解決的是「找到正確答案」這個問題，信任就會累積在你身上。",
        ],
    },
    {
        "id": "section-04",
        "start_sec": 904,
        "title": "小群比大群有力：門檻、文化與小組長會自己長出來",
        "tag": "群組經營",
        "summary": "一燈把健身群、打卡群與直播群拿來做例子，說明群組不是越大越有用。真正有向心力的小群，要有人數門檻、參與規則與文化，否則只會養出已讀不回與不參與的氛圍。當文化建立起來後，群裡甚至會自然長出願意幫你管理的人。",
        "highlights": [
            "十到十五人的小群，往往比上百人的鬆散群更容易產生向心力。",
            "沒有參與規則的群，最後很容易被幽靈人口拖垮文化。",
            "當群內有人開始主動複製你的做法，他其實就在變成下一個小組長。",
        ],
    },
    {
        "id": "section-05",
        "start_sec": 1444,
        "title": "主揪像班長：願意承擔的人，最容易變成人脈節點",
        "tag": "承擔責任",
        "summary": "從球場主揪、讀書會、AI 共學，到小時候的班長，一燈用一連串生活化例子說明：主揪往往不是最厲害的人，而是最願意負責的人。誰願意多扛一點場地、時間、規則與協調，誰就更容易接觸到資訊、資源與關鍵人物。",
        "highlights": [
            "主揪的核心不是專業壓制，而是承擔責任與穩定執行。",
            "班長不是最有權力的人，卻常常是整個班唯一對得上老師與行政的人。",
            "出社會之後，這種班長型角色其實到處都是，只是很多人沒有意識到。",
        ],
    },
    {
        "id": "section-06",
        "start_sec": 1818,
        "title": "興趣群、媽媽群、工作坊：舒服的私域比硬撐商會更有力量",
        "tag": "私域場景",
        "summary": "這段把私域從抽象名詞拉回生活。喝水群、打卡群、占星工作坊、媽媽社群，甚至社區主委，都是可能的人脈樞紐。相較於硬撐獅子會或商會會長這種高成本角色，從自己比較舒服、也真的做得久的場景出發，往往更容易累積長期信任。",
        "highlights": [
            "不是每個人都適合靠商會累積人脈，成本、酒局與捐款壓力都很高。",
            "如果你的興趣本身就能形成群體，那個群體就可能是你的私域入口。",
            "社區主委、育兒群、工作坊發起人，都是生活裡常見但被低估的人脈樞紐。",
        ],
    },
    {
        "id": "section-07",
        "start_sec": 2147,
        "title": "借力專家、回到需求，再用 +1 驗證要不要做",
        "tag": "借力與驗證",
        "summary": "收尾則把整套邏輯收得很完整：你不一定要自己變成超級專家，但你可以借力真正的專家來服務群體；前提是你真的站在對方的需求出發，而不是只想硬賣。最後，再把這件事拉回市場驗證：你想做什麼群，就先用 IG 或社群最小樣本測一下，有人喊 +1 再做。",
        "highlights": [
            "借力不是包裝自己，而是先把問題解掉，再把對的人接進來。",
            "再好的導流，也要先站在群體需求與舒服度上來設計。",
            "限時動態、貼文與 +1 回應，就是最便宜的市場調查工具。",
        ],
    },
]


def ts_from_seconds(total_seconds: int) -> str:
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def row_id(seconds: int) -> str:
    return f"t-{seconds:06d}"


def clean_text(text: str) -> str:
    text = text.strip()
    for source, target in REPLACEMENTS.items():
        text = text.replace(source, target)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s*([,，。！？；：])\s*", r"\1", text)
    return text.strip()


def sentence_join(parts: list[str]) -> str:
    out: list[str] = []
    for part in parts:
        if not part:
            continue
        piece = clean_text(part)
        if not piece:
            continue
        if out and not re.search(r"[，。！？；：]$", out[-1]):
            out[-1] += "。"
        out.append(piece)
    return "".join(out).strip("。") + "。"


def load_segments() -> list[dict[str, object]]:
    data = json.loads(SOURCE_JSON.read_text())
    raw_segments = data["transcription"]
    segments: list[dict[str, object]] = []
    for item in raw_segments:
        start_ms = int(item["offsets"]["from"])
        end_ms = int(item["offsets"]["to"])
        if start_ms < START_CUTOFF_MS or end_ms > END_CUTOFF_MS:
            continue
        text = clean_text(str(item["text"]))
        if not text:
            continue
        segments.append(
            {
                "start_ms": start_ms,
                "end_ms": end_ms,
                "start_sec": start_ms // 1000,
                "end_sec": max(start_ms // 1000, end_ms // 1000),
                "text": text,
            }
        )
    return segments


def merge_segments(segments: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    current: list[dict[str, object]] = []
    char_count = 0

    def flush() -> None:
        nonlocal current, char_count
        if not current:
            return
        start_sec = int(current[0]["start_sec"])
        end_sec = int(current[-1]["end_sec"])
        rows.append(
            {
                "id": row_id(start_sec),
                "time": ts_from_seconds(start_sec),
                "speaker": "一燈",
                "start_sec": start_sec,
                "end_sec": end_sec,
                "text": sentence_join([str(item["text"]) for item in current]),
            }
        )
        current = []
        char_count = 0

    for segment in segments:
        if current:
            gap_ms = int(segment["start_ms"]) - int(current[-1]["end_ms"])
            span_sec = int(segment["end_sec"]) - int(current[0]["start_sec"])
            if gap_ms > 2500 or char_count > 160 or span_sec > 38:
                flush()
        current.append(segment)
        char_count += len(str(segment["text"]))
    flush()
    return rows


def assign_section_anchors(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    anchored: list[dict[str, object]] = []
    for section in SECTIONS:
        anchor = next(
            (row for row in rows if int(row["start_sec"]) >= int(section["start_sec"])),
            rows[-1],
        )
        anchored.append({**section, "anchor_id": str(anchor["id"]), "anchor_time": str(anchor["time"])})
    return anchored


def section_for_row(start_sec: int) -> dict[str, object]:
    current = SECTIONS[0]
    for section in SECTIONS:
        if int(section["start_sec"]) <= start_sec:
            current = section
    return current


def render_event_page(sections: list[dict[str, object]]) -> str:
    toc_items = "\n".join(
        f'<a class="toc-link toc-level-3" href="../../transcripts/{EVENT_SLUG}/#{html.escape(str(section["anchor_id"]))}">{html.escape(str(section["anchor_time"]))}｜{html.escape(str(section["title"]))}</a>'
        for section in sections
    )
    guide_items = "\n".join(
        f'<li><a href="../../transcripts/{EVENT_SLUG}/#{html.escape(str(section["anchor_id"]))}"><strong>{html.escape(str(section["anchor_time"]))}｜{html.escape(str(section["title"]))}</strong></a>：{html.escape(str(section["summary"]))}</li>'
        for section in sections
    )
    key_points = "\n".join(
        f"<li>{html.escape(item)}</li>" for item in SUMMARY_HIGHLIGHTS
    )
    action_points = "\n".join(
        f"<li>{html.escape(item)}</li>" for item in ACTION_CHECKLIST
    )
    quotes = [
        "真正聰明的人不是什麼都自己試錯。",
        "租場地，也是一個不錯的累積人脈的方式。",
        "人脈不是靠炫耀來的，而是你承擔了某一些角色、累積信任來的。",
        "主揪通常不是那個最厲害的人，但主揪是最願意承擔責任的人。",
        "你不一定要把自己包裝成一個超厲害專家的角色。",
        "私域不是只有做自媒體短影音，然後導到你的 Line @ 才叫私域。",
        "300 個人裡面一個都沒有 +1，那你就先不要做了。",
    ]
    quote_items = "\n".join(
        f"<p><strong>一燈：</strong>「{html.escape(item)}」</p>" for item in quotes
    )
    section_cards = "\n".join(
        f"""
        <section class="insight-card">
          <p class="insight-tag">{html.escape(str(section["tag"]))}</p>
          <h3>{html.escape(str(section["title"]))}</h3>
          <p>{html.escape(str(section["summary"]))}</p>
        </section>
        """.strip()
        for section in sections[:4]
    )
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(PAGE_TITLE)}｜UBO</title>
  <meta name="description" content="{html.escape(PAGE_DESCRIPTION)}">
  <link rel="stylesheet" href="../../event-page.css">
  <style>
    .home-button {{ position: fixed; top: 14px; left: 14px; z-index: 10; display: inline-flex; align-items: center; min-height: 38px; padding: 8px 12px; border: 1px solid var(--line); border-radius: 6px; background: var(--paper); color: var(--ink); font-weight: 800; text-decoration: none; box-shadow: 0 8px 20px rgba(0,0,0,.08); }}
    .toc-list {{ grid-template-columns: 1fr; }}
    .toc-level-3 {{ padding-left: 0; }}
    .path-flow {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; margin: 20px 0 18px; counter-reset: path; }}
    .path-step {{ position: relative; min-height: 150px; padding: 18px 16px; border: 1px solid var(--line); border-radius: 8px; background: linear-gradient(180deg, #fffdf8 0%, #f3efe5 100%); box-shadow: inset 0 1px 0 rgba(255,255,255,.8); }}
    .path-step::before {{ counter-increment: path; content: counter(path); display: inline-grid; place-items: center; width: 28px; height: 28px; margin-bottom: 18px; border-radius: 50%; background: var(--accent); color: #fffdf8; font-size: 13px; font-weight: 900; }}
    .path-step:not(:last-child)::after {{ content: "→"; position: absolute; top: 22px; right: -14px; z-index: 2; color: var(--accent-2); font-weight: 900; font-size: 22px; }}
    .path-step h3 {{ margin: 0 0 8px; color: var(--heading); font-size: 22px; }}
    .path-step p {{ margin: 0; color: var(--muted); line-height: 1.55; }}
    .path-note {{ margin: 0 0 24px; color: var(--muted); }}
    .insight-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; margin: 18px 0 10px; }}
    .insight-card {{ padding: 16px; border: 1px solid var(--line); border-radius: 8px; background: #fffaf2; }}
    .insight-card h3 {{ margin-top: 0; }}
    .insight-tag {{ margin: 0 0 8px; color: var(--accent-2); font-size: 13px; font-weight: 800; text-transform: uppercase; letter-spacing: .04em; }}
    @media (max-width: 820px) {{ .path-flow {{ grid-template-columns: 1fr; }} .path-step {{ min-height: auto; }} .path-step:not(:last-child)::after {{ content: "↓"; top: auto; right: 18px; bottom: -22px; }} .insight-grid {{ grid-template-columns: 1fr; }} }}
    @media (max-width: 680px) {{ .home-button {{ position: sticky; top: 8px; margin: 8px 0 0 12px; }} }}
  </style>
</head>
<body>
  <a class="home-button" href="../../">回首頁</a>
  <header class="hero">
    <div class="hero-inner">
      <p class="eyebrow">2026-06-10 · UBO 社群直播 · 早上場</p>
      <h1>{html.escape(PAGE_TITLE)}</h1>
      <p class="summary">{html.escape(PAGE_DESCRIPTION)}</p>
    </div>
  </header>
  <nav class="toc-wrap" aria-label="頁面目錄">
    <p class="toc-title">章節導讀</p>
    <div class="toc-list">
      {toc_items}
    </div>
  </nav>
  <main>
    <article>
      <h1>{html.escape(PAGE_TITLE)}</h1>
      <blockquote>本頁是整理版；完整逐字稿已整理成時間軸與章節錨點。章節導讀可直接跳到完整逐字稿對應段落。</blockquote>

      <h2 id="一句話總結">一句話總結</h2>
      <p>{html.escape(SUMMARY_ONE_LINER)}</p>

      <h2 id="章節導讀">章節導讀</h2>
      <ul>
        {guide_items}
      </ul>

      <h2 id="重點摘錄">重點摘錄</h2>
      <ul>
        {key_points}
      </ul>

      <h2 id="主揪路徑">主揪變信任的路徑</h2>
      <div class="path-flow" aria-label="流量到私域的主揪路徑">
        <section class="path-step">
          <h3>驗證</h3>
          <p>先找已經有人回應的主題，不要從零憑空幻想需求。</p>
        </section>
        <section class="path-step">
          <h3>主揪</h3>
          <p>願意承擔場地、時間、規則與協調，成為大家想到的節點。</p>
        </section>
        <section class="path-step">
          <h3>信任</h3>
          <p>持續幫人解決問題，就算是借力專家，信任也會慢慢回到你身上。</p>
        </section>
        <section class="path-step">
          <h3>私域</h3>
          <p>把小群文化與穩定互動累積起來，最後才有合作、導流與成交的基礎。</p>
        </section>
      </div>
      <p class="path-note">一燈這場直播最實用的提醒是：真正能變成資產的，不只是表面的流量，而是你能不能把人聚起來、把問題接起來，再把信任留在自己身上。</p>

      <h2 id="直播脈絡">直播脈絡</h2>
      <div class="insight-grid">
        {section_cards}
      </div>

      <h2 id="可直接帶走的做法">可直接帶走的做法</h2>
      <ul>
        {action_points}
      </ul>

      <h2 id="簡短逐字稿">簡短逐字稿</h2>
      {quote_items}

      <p><a class="button primary" href="../../transcripts/{EVENT_SLUG}/">查看完整逐字稿</a></p>
    </article>
  </main>
  <footer class="footer">UBO / 一燈內容總站</footer>
</body>
</html>
"""


def render_transcript_page(rows: list[dict[str, object]], sections: list[dict[str, object]]) -> str:
    toc_items = "\n".join(
        f'<a href="#{html.escape(str(section["anchor_id"]))}">{html.escape(str(section["anchor_time"]))}｜{html.escape(str(section["title"]))}</a>'
        for section in sections
    )
    transcript_rows = "\n".join(
        f'<section class="transcript-row" id="{html.escape(str(row["id"]))}"><time>{html.escape(str(row["time"]))}</time><strong class="speaker">{html.escape(str(row["speaker"]))}</strong><p>{html.escape(str(row["text"]))}</p></section>'
        for row in rows
    )
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(PAGE_TITLE)}完整逐字稿</title>
  <meta name="description" content="{html.escape(PAGE_DESCRIPTION)}">
  <link rel="stylesheet" href="../../styles.css">
  <style>
    html {{ scroll-behavior: smooth; }}
    .home-button {{ position: fixed; top: 14px; left: 14px; z-index: 10; display: inline-flex; align-items: center; min-height: 38px; padding: 8px 12px; border: 1px solid var(--line); border-radius: 6px; background: var(--paper); color: var(--ink); font-weight: 800; text-decoration: none; box-shadow: 0 8px 20px rgba(0,0,0,.08); }}
    .article {{ max-width: 980px; padding: 64px 0 72px; }}
    .article h1 {{ font-size: clamp(34px, 5vw, 62px); }}
    .article h2 {{ margin-top: 38px; color: var(--red); }}
    .article p, .article li {{ color: var(--ink); }}
    .note {{ padding: 16px 18px; border: 1px solid var(--line); border-radius: 8px; background: var(--soft-gold); color: #614615; }}
    .transcript-toc {{ margin: 28px 0 34px; padding: 18px; border: 1px solid var(--line); border-radius: 8px; background: #fffdf8; }}
    .transcript-toc h2 {{ margin-top: 0; }}
    .toc-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }}
    .toc-grid a {{ display: block; padding: 10px 12px; border: 1px solid var(--line); border-radius: 6px; color: var(--ink); text-decoration: none; background: var(--paper); font-weight: 800; }}
    .toc-grid a:hover, .toc-grid a.is-active {{ border-color: var(--red); color: var(--red); background: #fff4ed; }}
    .transcript-row {{ display: grid; grid-template-columns: 92px 86px 1fr; gap: 16px; padding: 14px 0; border-top: 1px solid var(--line); scroll-margin-top: 76px; }}
    .transcript-row:target, .transcript-row.is-current {{ border-color: var(--red); outline: 2px solid rgba(171, 65, 43, .26); outline-offset: 4px; background: #fff8ef; }}
    .transcript-row time {{ color: var(--green); font-weight: 900; }}
    .speaker {{ color: var(--red); font-weight: 900; }}
    .transcript-row p {{ margin: 0; }}
    .reader-tools {{ position: fixed; right: 18px; bottom: 18px; z-index: 12; display: grid; gap: 8px; width: min(360px, calc(100vw - 36px)); }}
    .current-marker, .back-to-toc {{ border: 1px solid var(--line); border-radius: 8px; background: var(--paper); box-shadow: 0 10px 28px rgba(0,0,0,.12); }}
    .current-marker {{ padding: 10px 12px; color: var(--ink); font-size: 14px; line-height: 1.45; }}
    .current-marker strong {{ display: block; color: var(--red); font-size: 13px; }}
    .back-to-toc {{ display: inline-flex; justify-content: center; padding: 10px 12px; color: var(--ink); font-weight: 900; text-decoration: none; }}
    .back-to-toc:hover {{ color: var(--red); border-color: var(--red); }}
    @media (max-width: 720px) {{ .home-button {{ position: sticky; top: 8px; margin: 8px 0 0 12px; }} .article {{ padding-top: 28px; }} .toc-grid {{ grid-template-columns: 1fr; }} .transcript-row {{ grid-template-columns: 1fr; gap: 4px; }} .reader-tools {{ right: 10px; bottom: 10px; width: calc(100vw - 20px); }} }}
  </style>
</head>
<body>
  <a class="home-button" href="../../">回首頁</a>
  <main class="shell article" id="transcript-top">
    <p class="kicker">UBO / 一燈內容總站</p>
    <h1>{html.escape(PAGE_TITLE)}完整逐字稿</h1>
    <p class="lead">2026-06-10 早上 UBO 社群直播，本機 Whisper 轉錄後整理為逐字稿時間軸。</p>
    <p class="note">{html.escape(TRANSCRIPT_NOTE)}</p>
    <nav class="transcript-toc" id="transcript-toc" aria-label="逐字稿目錄">
      <h2>逐字稿目錄</h2>
      <div class="toc-grid">
        {toc_items}
      </div>
    </nav>
    <h2 id="transcript-body">逐字稿</h2>
    {transcript_rows}
  </main>
  <div class="reader-tools" aria-label="閱讀輔助">
    <div class="current-marker" id="current-marker" aria-live="polite">
      <strong>目前段落</strong>
      <span>{html.escape(str(sections[0]["anchor_time"]))}｜{html.escape(str(sections[0]["title"]))}</span>
    </div>
    <a class="back-to-toc" href="#transcript-toc">回逐字稿目錄</a>
  </div>
  <script>
    (() => {{
      const rows = Array.from(document.querySelectorAll('.transcript-row'));
      const tocLinks = Array.from(document.querySelectorAll('.toc-grid a'));
      const markerText = document.querySelector('#current-marker span');
      const chapters = tocLinks
        .map((link) => {{
          const target = document.querySelector(link.getAttribute('href'));
          return target ? {{ link, target, title: link.textContent.trim() }} : null;
        }})
        .filter(Boolean);

      function chapterFor(row) {{
        let current = chapters[0];
        for (const chapter of chapters) {{
          if (chapter.target.offsetTop <= row.offsetTop + 2) current = chapter;
        }}
        return current;
      }}

      function setCurrent(row) {{
        if (!row) return;
        rows.forEach((item) => item.classList.toggle('is-current', item === row));
        const chapter = chapterFor(row);
        tocLinks.forEach((link) => link.classList.toggle('is-active', chapter && link === chapter.link));
        const time = row.querySelector('time')?.textContent.trim() || '';
        const speaker = row.querySelector('.speaker')?.textContent.trim() || '';
        markerText.textContent = `${{time}}｜${{speaker}}｜${{chapter ? chapter.title.replace(/^[^｜]+｜/, '') : '逐字稿'}}`;
      }}

      const observer = new IntersectionObserver((entries) => {{
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible[0]) setCurrent(visible[0].target);
      }}, {{ rootMargin: '-18% 0px -70% 0px', threshold: [0, 0.2, 0.6] }});

      rows.forEach((row) => observer.observe(row));
      window.addEventListener('hashchange', () => setCurrent(document.querySelector(location.hash)));
      setCurrent(document.querySelector(location.hash) || rows[0]);
    }})();
  </script>
</body>
</html>
"""


def main() -> None:
    EVENT_DIR.mkdir(parents=True, exist_ok=True)
    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)

    segments = load_segments()
    rows = merge_segments(segments)
    sections = assign_section_anchors(rows)

    (EVENT_DIR / "index.html").write_text(render_event_page(sections))
    (TRANSCRIPT_DIR / "index.html").write_text(render_transcript_page(rows, sections))


if __name__ == "__main__":
    main()
