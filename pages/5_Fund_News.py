import streamlit as st
import requests
import json
from datetime import datetime, timedelta, timezone
from config import mutual_funds

# pages/9_Fund_News.py  (renamed file)
from utils.sidebar_style import render_sidebar
render_sidebar("news")
# ─────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Taurus – Fund News",
    page_icon="🐂",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Styling (matches app.py exactly)
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
    color: #e8e2d5;
}

.stApp {
    background-color: #080b0f;
    background-image:
        radial-gradient(ellipse 80% 60% at 15% 20%,  rgba(0, 245, 212, 0.07) 0%, transparent 65%),
        radial-gradient(ellipse 60% 80% at 85% 75%,  rgba(0, 180, 245, 0.06) 0%, transparent 60%),
        radial-gradient(ellipse 50% 40% at 50% 100%, rgba(0, 245, 212, 0.04) 0%, transparent 55%);
    background-attachment: fixed;
    min-height: 100vh;
    position: relative;
}

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 70% 55% at 8% 18%,  rgba(0,245,212,0.06) 0%, transparent 60%),
        radial-gradient(ellipse 55% 70% at 88% 72%, rgba(0,140,255,0.05) 0%, transparent 55%);
    z-index: 0;
    pointer-events: none;
    animation: taurus-pulse 8s ease-in-out infinite;
}

.stApp::after {
    content: "";
    position: fixed;
    inset: 0;
    background-image: radial-gradient(circle, rgba(0,245,212,0.16) 1px, transparent 1px);
    background-size: 38px 38px;
    z-index: 0;
    pointer-events: none;
    opacity: 0.45;
}

@keyframes taurus-pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.55; }
}

.stApp > * { position: relative; z-index: 1; }

[data-testid="stSidebar"] {
    background: linear-gradient(160deg, rgba(2,22,44,0.97) 0%, rgba(1,14,28,0.98) 100%) !important;
    border-right: 1px solid rgba(0,245,212,0.1) !important;
    box-shadow: 4px 0 32px rgba(0,0,0,0.5) !important;
    backdrop-filter: blur(12px);
}

#MainMenu, footer { visibility: hidden; }


.block-container {
    padding-top: 2rem !important;
    max-width: 1100px !important;
}

/* ── News cards ── */
.news-card {
    background: rgba(8,14,20,0.78);
    border: 1px solid rgba(0,245,212,0.15);
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 10px;
    transition: border-color 0.2s;
}
.news-card:hover {
    border-color: rgba(0,245,212,0.4);
}
.news-headline {
    font-family: 'Syne', sans-serif;
    font-size: 14px;
    font-weight: 600;
    color: #dff5f0;
    line-height: 1.45;
    margin-bottom: 6px;
}
.news-headline a {
    color: #dff5f0;
    text-decoration: none;
}
.news-headline a:hover { color: #00f5d4; }
.news-meta {
    font-size: 11px;
    color: rgba(255,255,255,0.35);
    letter-spacing: 0.04em;
}
.news-desc {
    font-size: 12px;
    color: rgba(255,255,255,0.5);
    margin-top: 6px;
    line-height: 1.5;
}

/* ── Sentiment badges ── */
.badge {
    display: inline-block;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-left: 8px;
    vertical-align: middle;
}
.badge-positive {
    background: rgba(0,245,160,0.15);
    border: 1px solid rgba(0,245,160,0.4);
    color: #00f5a0;
}
.badge-negative {
    background: rgba(255,107,107,0.15);
    border: 1px solid rgba(255,107,107,0.4);
    color: #ff6b6b;
}
.badge-neutral {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.2);
    color: rgba(255,255,255,0.55);
}

/* ── Sentiment summary bar ── */
.sentiment-bar-wrap {
    background: rgba(8,14,20,0.6);
    border: 1px solid rgba(0,245,212,0.12);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 16px;
}
.sentiment-bar-label {
    font-size: 11px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: rgba(0,245,212,0.6);
    margin-bottom: 10px;
}
.sbar {
    height: 8px;
    border-radius: 4px;
    display: flex;
    overflow: hidden;
    gap: 2px;
    margin-bottom: 8px;
}
.sbar-pos { background: #00f5a0; }
.sbar-neu { background: rgba(255,255,255,0.2); }
.sbar-neg { background: #ff6b6b; }
.sbar-counts {
    display: flex;
    gap: 16px;
    font-size: 11px;
}

/* ── Fund selector chips ── */
.section-label {
    font-size: 11px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #00f5d4;
    margin-bottom: 10px;
}

/* ── Overall sentiment donut-style summary ── */
.overall-card {
    background: rgba(0,245,212,0.06);
    border: 1px solid rgba(0,245,212,0.2);
    border-radius: 12px;
    padding: 18px 20px;
    text-align: center;
    margin-bottom: 16px;
}
.overall-label {
    font-size: 11px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: rgba(0,245,212,0.6);
    margin-bottom: 6px;
}
.overall-verdict {
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 800;
}
.verdict-positive { color: #00f5a0; }
.verdict-negative { color: #ff6b6b; }
.verdict-neutral  { color: rgba(255,255,255,0.6); }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Secrets
# ─────────────────────────────────────────────
NEWSAPI_KEY       = st.secrets["NEWSAPI_KEY"]
ANTHROPIC_API_KEY = st.secrets["ANTHROPIC_API_KEY"]

# ─────────────────────────────────────────────
# Fund house → search query mapping
# Extracted from config.py mutual_funds keys
# ─────────────────────────────────────────────
FUND_HOUSE_QUERIES = {
    "Mirae Asset":      "Mirae Asset mutual fund",
    "SBI Mutual Fund":  "SBI mutual fund",
    "Bandhan MF":       "Bandhan mutual fund",
    "Motilal Oswal":    "Motilal Oswal mutual fund",
    "Edelweiss MF":     "Edelweiss mutual fund",
    "Parag Parikh":     "Parag Parikh mutual fund PPFAS",
    "Nippon India":     "Nippon India mutual fund",
    "Axis MF":          "Axis mutual fund",
    "quant MF":         "quant mutual fund India",
    "HSBC MF":          "HSBC mutual fund India",
    "Kotak MF":         "Kotak mutual fund",
    "ICICI Pru":        "ICICI Prudential mutual fund",
}

# Map each fund name in config.py → fund house key above
FUND_TO_HOUSE = {
    "Mirae Asset FANG+":                              "Mirae Asset",
    "SBI Magnum Children's Benefit Fund":             "SBI Mutual Fund",
    "Bandhan Small Cap Fund":                         "Bandhan MF",
    "Motilal Oswal Midcap Fund":                      "Motilal Oswal",
    "Edelweiss Flexi Cap Fund":                       "Edelweiss MF",
    "Edelweiss Nifty Midcap150 Momentum 50 Index Fund": "Edelweiss MF",
    "Parag Parikh Flexi Cap Fund":                    "Parag Parikh",
    "Nippon India Large Cap Fund":                    "Nippon India",
    "Axis Small Cap Fund":                            "Axis MF",
    "SBI Small Cap Fund":                             "SBI Mutual Fund",
    "quant Small Cap Fund":                           "quant MF",
    "quant Mid Cap Fund":                             "quant MF",
    "HSBC Midcap Fund":                               "HSBC MF",
    "Kotak Midcap Fund":                              "Kotak MF",
    "Kotak Flexicap Fund":                            "Kotak MF",
    "ICICI Pru BHARAT 22 FOF":                        "ICICI Pru",
}

# ─────────────────────────────────────────────
# NewsAPI fetch
# ─────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)   # cache 30 min
def fetch_news(query: str, days_back: int = 7, page_size: int = 8) -> list[dict]:
    """
    Fetch recent news articles from NewsAPI.org.
    Returns list of {title, description, url, source, published_at}.
    """
    from_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%d")
    try:
        resp = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q":          query,
                "from":       from_date,
                "sortBy":     "publishedAt",
                "language":   "en",
                "pageSize":   page_size,
                "apiKey":     NEWSAPI_KEY,
            },
            timeout=10,
        )
        if resp.status_code != 200:
            return []
        articles = resp.json().get("articles", [])
        return [
            {
                "title":        a.get("title", ""),
                "description":  a.get("description", "") or "",
                "url":          a.get("url", "#"),
                "source":       a.get("source", {}).get("name", ""),
                "published_at": a.get("publishedAt", ""),
            }
            for a in articles
            if a.get("title") and "[Removed]" not in a.get("title", "")
        ]
    except Exception:
        return []


# ─────────────────────────────────────────────
# Claude sentiment scoring
# ─────────────────────────────────────────────
@st.cache_data(ttl=1800, show_spinner=False)
def score_sentiment(headlines: list[str], fund_house: str) -> list[str]:
    """
    Send headlines to Claude and get back per-headline sentiment:
    POSITIVE / NEUTRAL / NEGATIVE.
    Returns list of labels in same order as headlines.
    Falls back to NEUTRAL on any error.
    """
    if not headlines:
        return []

    numbered = "\n".join(f"{i+1}. {h}" for i, h in enumerate(headlines))
    prompt = (
        f"You are a financial sentiment analyst. "
        f"For each headline below about {fund_house}, "
        f"classify the sentiment as exactly one of: POSITIVE, NEUTRAL, or NEGATIVE "
        f"from the perspective of a retail mutual fund investor in India.\n\n"
        f"Headlines:\n{numbered}\n\n"
        f"Respond with ONLY a JSON array of strings in the same order, "
        f'e.g. ["POSITIVE","NEUTRAL","NEGATIVE"]. '
        f"No explanation, no markdown, just the JSON array."
    )

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key":         ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type":      "application/json",
            },
            json={
                "model":      "claude-sonnet-4-20250514",
                "max_tokens": 256,
                "messages":   [{"role": "user", "content": prompt}],
            },
            timeout=20,
        )
        if resp.status_code != 200:
            return ["NEUTRAL"] * len(headlines)

        text = resp.json()["content"][0]["text"].strip()
        # Strip any accidental markdown fences
        text = text.replace("```json", "").replace("```", "").strip()
        labels = json.loads(text)
        # Validate and normalise
        valid = {"POSITIVE", "NEUTRAL", "NEGATIVE"}
        return [
            l.upper() if l.upper() in valid else "NEUTRAL"
            for l in labels
        ]
    except Exception:
        return ["NEUTRAL"] * len(headlines)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def _badge(label: str) -> str:
    cls = {
        "POSITIVE": "badge-positive",
        "NEGATIVE": "badge-negative",
        "NEUTRAL":  "badge-neutral",
    }.get(label, "badge-neutral")
    icon = {"POSITIVE": "▲", "NEGATIVE": "▼", "NEUTRAL": "●"}.get(label, "●")
    return f'<span class="badge {cls}">{icon} {label}</span>'


def _fmt_date(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%d %b %Y, %H:%M")
    except Exception:
        return iso


def _sentiment_bar_html(pos: int, neu: int, neg: int) -> str:
    total = pos + neu + neg or 1
    pw = pos / total * 100
    nuw = neu / total * 100
    nw = neg / total * 100
    return (
        f'<div class="sentiment-bar-wrap">'
        f'<div class="sentiment-bar-label">Sentiment breakdown — {total} articles</div>'
        f'<div class="sbar">'
        f'  <div class="sbar-pos" style="width:{pw:.0f}%"></div>'
        f'  <div class="sbar-neu" style="width:{nuw:.0f}%"></div>'
        f'  <div class="sbar-neg" style="width:{nw:.0f}%"></div>'
        f'</div>'
        f'<div class="sbar-counts">'
        f'  <span style="color:#00f5a0;">▲ {pos} positive</span>'
        f'  <span style="color:rgba(255,255,255,0.4);">● {neu} neutral</span>'
        f'  <span style="color:#ff6b6b;">▼ {neg} negative</span>'
        f'</div></div>'
    )


def _overall_verdict(pos: int, neg: int, total: int) -> tuple[str, str]:
    """Returns (verdict_text, css_class)."""
    if total == 0:
        return "No Data", "verdict-neutral"
    pos_pct = pos / total * 100
    neg_pct = neg / total * 100
    if pos_pct >= 55:
        return "Mostly Positive 📈", "verdict-positive"
    if neg_pct >= 55:
        return "Mostly Negative 📉", "verdict-negative"
    if pos_pct > neg_pct:
        return "Leaning Positive", "verdict-positive"
    if neg_pct > pos_pct:
        return "Leaning Negative", "verdict-negative"
    return "Mixed / Neutral", "verdict-neutral"


# ─────────────────────────────────────────────
# Page Header
# ─────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:4px;">
  <span style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;
    background:linear-gradient(135deg,#00f5d4 0%,#00c9ff 55%,#a78bfa 100%);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    background-clip:text;">📰 Fund News & Sentiment</span>
</div>
<div style="font-size:12px;color:rgba(255,255,255,0.4);
  letter-spacing:0.1em;text-transform:uppercase;margin-bottom:24px;">
  Recent headlines · AI-powered sentiment · Per fund house
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Controls
# ─────────────────────────────────────────────
ctrl_left, ctrl_mid, ctrl_right = st.columns([2, 1, 1])

with ctrl_left:
    st.markdown('<div class="section-label">Select Fund Houses</div>', unsafe_allow_html=True)
    # Deduplicate fund houses from the user's portfolio
    portfolio_houses = sorted(set(FUND_TO_HOUSE.values()))
    selected_houses = st.multiselect(
        "Fund houses",
        options=portfolio_houses,
        default=portfolio_houses[:4],
        label_visibility="collapsed",
    )

with ctrl_mid:
    st.markdown('<div class="section-label">Days Back</div>', unsafe_allow_html=True)
    days_back = st.select_slider(
        "Days back",
        options=[3, 7, 14, 30],
        value=7,
        label_visibility="collapsed",
    )

with ctrl_right:
    st.markdown('<div class="section-label">Articles per House</div>', unsafe_allow_html=True)
    page_size = st.select_slider(
        "Articles",
        options=[4, 6, 8, 10],
        value=6,
        label_visibility="collapsed",
    )

st.markdown("<br>", unsafe_allow_html=True)
fetch_btn = st.button(
    "📰 Fetch News & Analyse Sentiment",
    type="primary",
    use_container_width=False,
    disabled=not selected_houses,
)

if not fetch_btn:
    st.markdown(
        '<br><div style="text-align:center;opacity:0.35;padding:80px 20px;">'
        '<div style="font-size:52px;">📰</div>'
        '<div style="margin-top:14px;font-size:14px;">'
        'Select fund houses and hit Fetch</div>'
        '<div style="font-size:12px;margin-top:6px;opacity:0.7;">'
        'Headlines pulled from NewsAPI · Sentiment scored by Claude'
        '</div></div>',
        unsafe_allow_html=True,
    )
    st.stop()

# ─────────────────────────────────────────────
# Fetch + Score
# ─────────────────────────────────────────────
all_results = {}   # house → {"articles": [...], "sentiments": [...]}

progress = st.progress(0, text="Fetching news…")
for i, house in enumerate(selected_houses):
    progress.progress((i + 0.5) / len(selected_houses), text=f"Fetching news for {house}…")
    query    = FUND_HOUSE_QUERIES.get(house, house + " mutual fund India")
    articles = fetch_news(query, days_back=days_back, page_size=page_size)

    sentiments = []
    if articles:
        progress.progress((i + 0.85) / len(selected_houses), text=f"Scoring sentiment for {house}…")
        headlines  = [a["title"] for a in articles]
        sentiments = score_sentiment(tuple(headlines), house)   # tuple for cache key

    all_results[house] = {"articles": articles, "sentiments": sentiments}

progress.empty()

# ─────────────────────────────────────────────
# Overall Portfolio Sentiment Summary
# ─────────────────────────────────────────────
total_pos = total_neu = total_neg = 0
for house_data in all_results.values():
    for s in house_data["sentiments"]:
        if s == "POSITIVE":
            total_pos += 1
        elif s == "NEGATIVE":
            total_neg += 1
        else:
            total_neu += 1

total_articles = total_pos + total_neu + total_neg
verdict, verdict_cls = _overall_verdict(total_pos, total_neg, total_articles)

st.markdown(
    f'<div class="overall-card">'
    f'<div class="overall-label">Overall Portfolio Sentiment · {total_articles} articles across {len(selected_houses)} fund houses</div>'
    f'<div class="overall-verdict {verdict_cls}">{verdict}</div>'
    f'</div>',
    unsafe_allow_html=True,
)

st.markdown(
    _sentiment_bar_html(total_pos, total_neu, total_neg),
    unsafe_allow_html=True,
)

st.divider()

# ─────────────────────────────────────────────
# Per-Fund-House News Feed
# ─────────────────────────────────────────────
for house in selected_houses:
    data       = all_results[house]
    articles   = data["articles"]
    sentiments = data["sentiments"]

    # Per-house sentiment counts
    h_pos = sentiments.count("POSITIVE")
    h_neu = sentiments.count("NEUTRAL")
    h_neg = sentiments.count("NEGATIVE")
    h_verdict, h_verdict_cls = _overall_verdict(h_pos, h_neg, len(sentiments))

    # Section header
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">'
        f'<span style="font-family:\'Syne\',sans-serif;font-size:1.05rem;'
        f'font-weight:700;color:#dff5f0;">{house}</span>'
        f'<span class="overall-verdict {h_verdict_cls}" '
        f'style="font-size:13px;font-family:\'DM Mono\',monospace;">'
        f'{h_verdict}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if not articles:
        st.markdown(
            '<div style="padding:14px 18px;background:rgba(255,255,255,0.03);'
            'border:1px solid rgba(255,255,255,0.08);border-radius:10px;'
            'font-size:12px;color:rgba(255,255,255,0.35);margin-bottom:16px;">'
            'No recent articles found for this fund house.</div>',
            unsafe_allow_html=True,
        )
        continue

    # Sentiment bar for this house
    st.markdown(
        _sentiment_bar_html(h_pos, h_neu, h_neg),
        unsafe_allow_html=True,
    )

    # Article cards
    for j, (article, sentiment) in enumerate(
        zip(articles, sentiments + ["NEUTRAL"] * len(articles))
    ):
        pub = _fmt_date(article["published_at"])
        desc_html = (
            f'<div class="news-desc">{article["description"][:180]}…</div>'
            if article["description"]
            else ""
        )
        st.markdown(
            f'<div class="news-card">'
            f'  <div class="news-headline">'
            f'    <a href="{article["url"]}" target="_blank">{article["title"]}</a>'
            f'    {_badge(sentiment)}'
            f'  </div>'
            f'  {desc_html}'
            f'  <div class="news-meta">{article["source"]} &nbsp;·&nbsp; {pub}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Footer disclaimer
# ─────────────────────────────────────────────
st.markdown(
    '<div style="font-size:11px;color:rgba(255,255,255,0.2);'
    'border-top:1px solid rgba(255,255,255,0.07);padding-top:16px;margin-top:8px;">'
    '⚠️ News sourced from NewsAPI.org · Sentiment scored by Claude (Anthropic) · '
    'For informational purposes only · Not financial advice'
    '</div>',
    unsafe_allow_html=True,
)
