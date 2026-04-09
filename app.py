import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import feedparser
from datetime import datetime
import time

st.set_page_config(
    page_title="ZSE Portfolio Optimizer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  DESIGN SYSTEM
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&family=Playfair+Display:wght@600;700&display=swap');

:root {
    --ice-gray:  #F0F4F8;
    --heather:   #B8C2D0;
    --greyish:   #A8B2C0;
    --fossil:    #8E9AAB;
    --trout:     #6C7A8E;
    --iron:      #4E5B6E;
    --abalone:   #D9E0E8;
    --thunder:   #3A4556;
    --mink:      #5D6A7A;
    --white:     #FFFFFF;
    --success:   #3A7D5B;
    --danger:    #8B3A3A;
}

html, body, .stApp, [data-testid="stAppViewContainer"] {
    background-color: var(--ice-gray) !important;
    color: var(--thunder) !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stHeader"] { background-color: var(--ice-gray) !important; }

[data-testid="stSidebar"] {
    background-color: var(--thunder) !important;
    border-right: 1px solid var(--iron) !important;
}
[data-testid="stSidebar"] * {
    color: var(--abalone) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important;
}
[data-testid="stSidebar"] .stRadio > label {
    color: var(--heather) !important;
    font-size: 0.62rem !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
[data-testid="stSidebar"] .stRadio label {
    display: block;
    padding: 0.5rem 0.8rem;
    border-radius: 6px;
    margin-bottom: 2px;
    transition: background 0.15s;
    color: var(--heather) !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.08) !important;
    color: var(--white) !important;
}

h1 {
    font-family: 'Playfair Display', serif !important;
    color: var(--thunder) !important;
    font-size: 1.9rem !important;
    font-weight: 700 !important;
}
h2 {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--iron) !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    border-bottom: 1px solid var(--abalone);
    padding-bottom: 0.35rem;
    margin-top: 1.6rem !important;
}
h3 {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--mink) !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
}

.page-header {
    background: var(--white);
    border: 1px solid var(--abalone);
    border-radius: 10px;
    padding: 1.1rem 1.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.page-header-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--thunder);
    margin: 0;
}
.page-tag {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    color: var(--trout);
    background: var(--abalone);
    border: 1px solid var(--heather);
    padding: 3px 10px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.card {
    background: var(--white);
    border: 1px solid var(--abalone);
    border-radius: 10px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1rem;
}
.card-accent {
    background: var(--white);
    border: 1px solid var(--heather);
    border-left: 4px solid var(--iron);
    border-radius: 10px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1rem;
}

/* ── HOME user role cards ── */
.role-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin: 1.4rem 0;
}
.role-card {
    background: var(--white);
    border: 1px solid var(--abalone);
    border-radius: 12px;
    padding: 1.4rem 1.2rem 1.2rem;
    text-align: center;
    transition: border-color 0.2s, box-shadow 0.2s;
    cursor: default;
}
.role-card:hover {
    border-color: var(--trout);
    box-shadow: 0 4px 16px rgba(78,91,110,0.10);
}
.role-icon {
    font-size: 2rem;
    margin-bottom: 0.6rem;
    display: block;
}
.role-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.92rem;
    font-weight: 600;
    color: var(--thunder);
    margin-bottom: 0.5rem;
}
.role-desc {
    font-size: 0.76rem;
    color: var(--trout);
    line-height: 1.6;
}
.role-link {
    font-family: 'DM Mono', monospace;
    font-size: 0.63rem;
    color: var(--iron);
    background: var(--abalone);
    border: 1px solid var(--heather);
    border-radius: 20px;
    padding: 2px 10px;
    display: inline-block;
    margin-top: 0.6rem;
    letter-spacing: 0.05em;
}

/* ── logo mark ── */
.logo-mark {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 1.8rem;
}
.logo-icon {
    width: 54px;
    height: 54px;
    background: var(--iron);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.logo-text-main {
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--thunder);
    letter-spacing: -0.02em;
    line-height: 1;
}
.logo-text-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.63rem;
    color: var(--fossil);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 4px;
}

.welcome-banner {
    background: var(--white);
    border: 1px solid var(--abalone);
    border-radius: 12px;
    padding: 1.4rem 1.8rem;
    margin-bottom: 1.6rem;
}
.welcome-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: var(--iron);
    margin-bottom: 0.4rem;
}
.welcome-body {
    font-size: 0.86rem;
    color: var(--trout);
    line-height: 1.75;
    max-width: 620px;
}

/* ── KPI tiles ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin: 1rem 0 1.6rem;
}
.kpi {
    background: var(--white);
    border: 1px solid var(--abalone);
    border-top: 3px solid var(--iron);
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
}
.kpi-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    color: var(--fossil);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.4rem;
}
.kpi-value {
    font-family: 'Playfair Display', serif;
    font-size: 1.9rem;
    font-weight: 700;
    color: var(--thunder);
    line-height: 1;
}
.kpi-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.67rem;
    color: var(--fossil);
    margin-top: 0.3rem;
}

/* ── badges ── */
.badge {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 20px;
    font-family: 'DM Mono', monospace;
    font-size: 0.63rem;
    font-weight: 500;
    letter-spacing: 0.04em;
}
.badge-positive { background:#EBF5EE; color:var(--success); border:1px solid #A8D5B5; }
.badge-negative { background:#F5EBEB; color:var(--danger);  border:1px solid #D5A8A8; }
.badge-neutral  { background:var(--abalone); color:var(--trout); border:1px solid var(--heather); }
.badge-iron     { background:var(--abalone); color:var(--iron);  border:1px solid var(--heather); }

.news-item {
    background: var(--white);
    border: 1px solid var(--abalone);
    border-left: 3px solid var(--trout);
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.8rem;
}
.news-headline {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.87rem;
    font-weight: 600;
    color: var(--thunder);
    margin-bottom: 0.25rem;
}
.news-meta {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    color: var(--fossil);
    margin-bottom: 0.35rem;
}
.news-body { font-size: 0.8rem; color: var(--trout); line-height: 1.6; }

.ticker {
    font-family: 'DM Mono', monospace;
    font-size: 0.71rem;
    background: var(--abalone);
    border: 1px solid var(--heather);
    color: var(--iron);
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 500;
}

.overline {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    color: var(--fossil);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.35rem;
}

.guide-card {
    background: var(--white);
    border: 1px solid var(--abalone);
    border-left: 4px solid var(--iron);
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}

.stSelectbox > div > div,
.stDateInput > div > div {
    background: var(--white) !important;
    border: 1px solid var(--heather) !important;
    border-radius: 6px !important;
    color: var(--thunder) !important;
}
.stButton > button {
    background: var(--iron) !important;
    color: var(--white) !important;
    border: none !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.05em !important;
    border-radius: 6px !important;
    padding: 0.55rem 1.4rem !important;
    transition: background 0.2s !important;
}
.stButton > button:hover { background: var(--thunder) !important; }
[data-testid="stFileUploader"] {
    background: var(--white) !important;
    border: 1px dashed var(--heather) !important;
    border-radius: 8px !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Playfair Display', serif !important;
    font-size: 1.5rem !important;
    color: var(--thunder) !important;
    font-weight: 700 !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.62rem !important;
    color: var(--fossil) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
[data-testid="stMetricDelta"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
}
.stDataFrame, [data-testid="stDataFrameResizable"] {
    background: var(--white) !important;
    border: 1px solid var(--abalone) !important;
    border-radius: 8px !important;
}
.stProgress > div > div { background: var(--iron) !important; }
.streamlit-expanderHeader {
    background: var(--white) !important;
    border: 1px solid var(--abalone) !important;
    border-radius: 6px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important;
    color: var(--iron) !important;
}
hr { border-color: var(--abalone) !important; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--ice-gray); }
::-webkit-scrollbar-thumb { background: var(--heather); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PLOTLY THEME HELPER
# ─────────────────────────────────────────────
def make_plot_layout(**extra):
    base = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font=dict(family="DM Mono, monospace", color="#6C7A8E", size=11),
        xaxis=dict(
            gridcolor="#D9E0E8", linecolor="#B8C2D0",
            tickcolor="#B8C2D0", tickfont=dict(color="#8E9AAB")
        ),
        yaxis=dict(
            gridcolor="#D9E0E8", linecolor="#B8C2D0",
            tickcolor="#B8C2D0", tickfont=dict(color="#8E9AAB")
        ),
        colorway=[
            "#4E5B6E","#8E9AAB","#3A7D5B","#8B3A3A","#6C7A8E","#B8C2D0"
        ],
        hoverlabel=dict(
            bgcolor="#FFFFFF", bordercolor="#B8C2D0", font_color="#3A4556"
        ),
        margin=dict(l=12, r=12, t=40, b=12),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#D9E0E8"),
    )
    base.update(extra)
    return base


# ─────────────────────────────────────────────
#  API HELPER  — retry on 429
# ─────────────────────────────────────────────
API_URL = "https://zse-ai-backend.onrender.com/api/optimize"

def get_portfolio_data(tau, risk, date, retries=2, delay=8):
    payload = {"tau": tau, "risk_aversion": risk, "selected_date": date}
    for attempt in range(retries + 1):
        try:
            resp = requests.post(API_URL, json=payload, timeout=40)
            if resp.status_code == 429:
                if attempt < retries:
                    st.warning(
                        f"Rate limit — retrying in {delay}s "
                        f"(attempt {attempt+1}/{retries})…"
                    )
                    time.sleep(delay)
                    continue
                st.error("API rate limit reached. Wait a moment and try again.")
                return None
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.Timeout:
            st.error(
                "Request timed out. The server may be starting up — "
                "please try again in 30 seconds."
            )
            return None
        except Exception as e:
            if attempt < retries:
                time.sleep(delay)
                continue
            st.error(f"API error: {e}")
            return None
    return None


# ─────────────────────────────────────────────
#  DATA HELPERS
# ─────────────────────────────────────────────
@st.cache_data
def load_csv(file, parse_dates=None):
    try:
        return pd.read_csv(file, parse_dates=parse_dates)
    except FileNotFoundError:
        return pd.DataFrame()

def wide_to_long(df, id_vars="Date", value_name="price"):
    if df.empty:
        return df
    return df.melt(id_vars=id_vars, var_name="ticker", value_name=value_name)

def fetch_rss_feed(url):
    keywords = [
        "AFDIS","African Distillers","BAT","British American Tobacco",
        "CAFCA","Cafca","CBZ","CBZ Holdings","DLTA","Delta","DZL",
        "Dairibord","ECO","Econet","OKZ","OK Zimbabwe","SEED","Seed Co"
    ]
    try:
        feed = feedparser.parse(url)
        entries = []
        for entry in feed.entries[:30]:
            title   = entry.title.lower()
            summary = entry.get("summary", "").lower()
            if any(k.lower() in title or k.lower() in summary for k in keywords):
                raw = entry.get("summary", "")
                entries.append({
                    "title":     entry.title,
                    "link":      entry.link,
                    "published": entry.get("published", "—"),
                    "summary":   (raw[:280] + "…") if len(raw) > 280 else raw,
                })
        return entries
    except Exception:
        return []


# ─────────────────────────────────────────────
#  LOAD DEFAULT DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_default_data():
    news_df     = load_csv("news_sentiment_clean.csv", parse_dates=["date"])
    prices_wide = load_csv("prices_9stocks.csv", parse_dates=["Date"])
    prices_long = wide_to_long(prices_wide) if not prices_wide.empty else pd.DataFrame()
    fund_df     = load_csv("fundamentals_9stocks.csv")
    if not fund_df.empty:
        fund_df.rename(columns={
            "pb_ratio":"P/B","roi":"ROE","net_margin":"Net Margin",
            "div_yield":"Dividend Yield",
            "market_cap_zig_millions":"Market Cap (ZiG mn)",
            "pe_ratio":"P/E",
        }, inplace=True)
    forecast_df = load_csv("forecasts_9stocks.csv", parse_dates=["date"])
    return news_df, prices_long, fund_df, forecast_df

for key, val in zip(
    ["news_df","prices_long","fund_df","forecast_df"],
    load_default_data()
):
    if key not in st.session_state:
        st.session_state[key] = val

news_df     = st.session_state.news_df
prices_long = st.session_state.prices_long
fund_df     = st.session_state.fund_df
forecast_df = st.session_state.forecast_df


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:1.2rem 0.8rem 1rem;
                border-bottom:1px solid rgba(255,255,255,0.1);
                margin-bottom:1rem'>
        <div style='font-family:Playfair Display,serif;
                    font-size:1.1rem;font-weight:700;
                    color:#F0F4F8;letter-spacing:-0.01em'>
            ZSE Portfolio
        </div>
        <div style='font-family:DM Mono,monospace;
                    font-size:0.58rem;color:#8E9AAB;
                    letter-spacing:0.1em;margin-top:3px'>
            AI · Black-Litterman · ZSE
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "NAVIGATE",
        ["🏠 Home",
         "📊 Market Intelligence",
         "⚙️ Portfolio Optimizer",
         "📈 Stock Analysis",
         "📰 Live News Feed",
         "📘 User Guide"],
        label_visibility="visible"
    )

    st.markdown("---")
    st.markdown("""
    <div style='font-family:DM Mono,monospace;font-size:0.62rem;
                color:#8E9AAB;line-height:2;padding:0.5rem 0'>
        DA-BERT Accuracy &nbsp;<span style='color:#D9E0E8'>81.4%</span><br>
        Sharpe Ratio &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style='color:#D9E0E8'>0.79</span><br>
        USD Preserved &nbsp;&nbsp;&nbsp;<span style='color:#A8D5B5'>76.6%</span><br>
        Outperformance &nbsp;<span style='color:#A8D5B5'>+20.4%</span><br>
        Test Period &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span style='color:#8E9AAB'>2023–2024</span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE 0  —  HOME  (clean, user-role focused)
# ─────────────────────────────────────────────
if page == "🏠 Home":

    # ── Logo + system name ──
    st.markdown("""
    <div class='logo-mark'>
        <div class='logo-icon'>
            <svg width="30" height="30" viewBox="0 0 30 30"
                 fill="none" xmlns="http://www.w3.org/2000/svg">
                <!-- candlestick bars -->
                <rect x="4"  y="18" width="4" height="8"  fill="#D9E0E8" rx="1"/>
                <rect x="4"  y="14" width="4" height="2"  fill="#D9E0E8" rx="0.5"/>
                <rect x="4"  y="26" width="4" height="2"  fill="#D9E0E8" rx="0.5"/>
                <rect x="13" y="10" width="4" height="12" fill="#B8C2D0" rx="1"/>
                <rect x="13" y="6"  width="4" height="2"  fill="#B8C2D0" rx="0.5"/>
                <rect x="13" y="24" width="4" height="2"  fill="#B8C2D0" rx="0.5"/>
                <rect x="22" y="4"  width="4" height="16" fill="#F0F4F8" rx="1"/>
                <rect x="22" y="2"  width="4" height="2"  fill="#F0F4F8" rx="0.5"/>
                <rect x="22" y="22" width="4" height="2"  fill="#F0F4F8" rx="0.5"/>
            </svg>
        </div>
        <div>
            <div class='logo-text-main'>ZSE Portfolio Optimizer</div>
            <div class='logo-text-sub'>Zimbabwe Stock Exchange · AI-Driven Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Welcome banner ──
    st.markdown("""
    <div class='welcome-banner'>
        <div class='welcome-title'>Welcome</div>
        <div class='welcome-body'>
            This system uses artificial intelligence to help you make
            smarter investment decisions on the Zimbabwe Stock Exchange.
            Sentiment signals from financial news, return forecasts, and
            Bayesian portfolio optimization work together to give you an
            edge — whether you are managing a portfolio, analysing a
            company, or tracking the market.
            <br><br>
            Select your role below to see how this system can work for you,
            or use the sidebar to navigate directly to any page.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── User role cards — using st.columns so Streamlit renders HTML correctly ──
    roles = [
        (
            "💼", "Investor",
            "See how each company is performing, check AI sentiment signals, "
            "and explore how much of your wealth would have been preserved "
            "during Zimbabwe's currency crisis.",
            ["→ Portfolio Optimizer", "→ Stock Analysis"],
        ),
        (
            "📊", "Stockbroker",
            "Monitor daily sentiment trends across all nine counters, track "
            "which stocks are seeing improving or declining news coverage, "
            "and stay on top of live headlines.",
            ["→ Market Intelligence", "→ Live News Feed"],
        ),
        (
            "🔬", "Analyst",
            "Run the Black-Litterman optimizer with different confidence "
            "levels, examine how AI views compare to market equilibrium, "
            "and review CNN-LSTM forecast accuracy stock by stock.",
            ["→ Portfolio Optimizer", "→ Stock Analysis"],
        ),
        (
            "🏦", "Fund Manager",
            "Upload your own news dataset and see how the sentiment model "
            "adapts. Adjust risk parameters and compare AI-driven weights "
            "against equal-weight and market-cap benchmarks.",
            ["→ Portfolio Optimizer", "→ Market Intelligence"],
        ),
    ]

    r1, r2, r3, r4 = st.columns(4, gap="small")
    for col, (icon, title, desc, links) in zip([r1, r2, r3, r4], roles):
        link_html = "".join(
            f"<div style='font-family:DM Mono,monospace;font-size:0.63rem;"
            f"color:#4E5B6E;background:#D9E0E8;border:1px solid #B8C2D0;"
            f"border-radius:20px;padding:2px 10px;display:inline-block;"
            f"margin-top:5px;margin-right:4px;letter-spacing:0.05em'>"
            f"{lnk}</div>"
            for lnk in links
        )
        col.markdown(
            f"""
            <div style='background:#FFFFFF;border:1px solid #D9E0E8;
                        border-radius:12px;padding:1.3rem 1.1rem 1.1rem;
                        height:100%;min-height:200px'>
                <div style='font-size:2rem;margin-bottom:0.5rem'>{icon}</div>
                <div style='font-family:DM Sans,sans-serif;font-size:0.92rem;
                            font-weight:600;color:#3A4556;
                            margin-bottom:0.5rem'>{title}</div>
                <div style='font-size:0.76rem;color:#6C7A8E;
                            line-height:1.65;margin-bottom:0.6rem'>{desc}</div>
                {link_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Quick start — st.columns so grid renders correctly ──
    st.markdown(
        "<div style='font-family:DM Mono,monospace;font-size:0.62rem;"
        "color:#8E9AAB;text-transform:uppercase;letter-spacing:0.1em;"
        "margin-bottom:0.7rem'>Quick Start</div>",
        unsafe_allow_html=True,
    )
    qs1, qs2, qs3 = st.columns(3, gap="medium")
    steps = [
        ("Step 1", "Market Intelligence",
         "Pick a trading date and explore what news sentiment "
         "looked like across all nine ZSE counters on that day."),
        ("Step 2", "Portfolio Optimizer",
         "Adjust the τ slider and click Run to get live "
         "AI-driven Black-Litterman portfolio weights instantly."),
        ("Step 3", "Stock Analysis",
         "Select any of the nine counters to see fundamentals, "
         "AI signals, and CNN-LSTM forecast accuracy side by side."),
    ]
    for col, (label, page_name, text) in zip([qs1, qs2, qs3], steps):
        col.markdown(
            f"""
            <div style='background:#FFFFFF;border:1px solid #D9E0E8;
                        border-radius:10px;padding:1rem 1.1rem'>
                <div style='font-family:DM Mono,monospace;font-size:0.62rem;
                            color:#4E5B6E;font-weight:500;
                            margin-bottom:0.3rem'>{label}</div>
                <div style='font-family:DM Sans,sans-serif;font-size:0.85rem;
                            font-weight:600;color:#3A4556;
                            margin-bottom:0.3rem'>{page_name}</div>
                <div style='font-size:0.78rem;color:#6C7A8E;
                            line-height:1.65'>{text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
#  PAGE 1  —  MARKET INTELLIGENCE
# ─────────────────────────────────────────────
elif page == "📊 Market Intelligence":

    st.markdown("""
    <div class='page-header'>
        <span class='page-header-title'>Market Intelligence</span>
        <span class='page-tag'>DA-BERT Sentiment</span>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Upload new news CSV to override default data (optional)",
        type=["csv"]
    )
    if uploaded is not None:
        try:
            new_df = pd.read_csv(uploaded, parse_dates=["date"])
            st.session_state.news_df = new_df
            news_df = new_df
            ca, cb = st.columns(2)
            ca.metric("Articles loaded", len(new_df))
            cb.metric(
                "Date range",
                f"{new_df['date'].min().date()} → "
                f"{new_df['date'].max().date()}"
            )
            st.success(
                "Dataset updated — all charts below now reflect "
                "your uploaded data."
            )
        except Exception as e:
            st.error(
                f"Could not parse file: {e}. "
                "Required columns: date, ticker, headline, content, "
                "sentiment_score, sentiment_label, source."
            )

    if news_df.empty:
        st.warning("No news data found. Upload a CSV above.")
        st.stop()

    all_dates     = sorted(news_df["date"].unique())
    selected_date = st.selectbox(
        "Select trading date (only dates with news shown)", all_dates
    )
    daily_news    = news_df[news_df["date"] == selected_date]

    if not daily_news.empty:
        avg_s   = daily_news["sentiment_score"].mean()
        vol_s   = (daily_news["sentiment_score"].max() -
                   daily_news["sentiment_score"].min()) / 2
        pct_pos = (daily_news["sentiment_score"] > 0.1).mean() * 100

        c1, c2, c3 = st.columns(3)
        c1.metric("Average Sentiment",   f"{avg_s:.3f}")
        c2.metric("Sentiment Spread",    f"{vol_s:.3f}")
        c3.metric("% Positive Articles", f"{pct_pos:.0f}%")
        st.progress(float((avg_s + 1) / 2))

        ticker_avg = (
            daily_news.groupby("ticker")["sentiment_score"]
            .mean().reset_index()
        )
        bar_colors = [
            "#3A7D5B" if v > 0.1 else
            ("#8B3A3A" if v < -0.1 else "#4E5B6E")
            for v in ticker_avg["sentiment_score"]
        ]
        fig_bar = go.Figure(go.Bar(
            x=ticker_avg["ticker"],
            y=ticker_avg["sentiment_score"],
            marker_color=bar_colors,
            text=ticker_avg["sentiment_score"].round(3),
            textposition="outside",
            textfont=dict(family="DM Mono", size=10, color="#6C7A8E"),
        ))
        fig_bar.add_hline(y=0, line_color="#B8C2D0", line_width=1)
        fig_bar.update_layout(
            title=dict(
                text="Sentiment Score by Stock",
                font=dict(family="DM Sans", size=14, color="#3A4556")
            ),
            showlegend=False,
            **make_plot_layout()
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("No sentiment data for selected date.")

    trend = news_df.groupby("date")["sentiment_score"].mean().reset_index()
    fig_line = go.Figure(go.Scatter(
        x=trend["date"], y=trend["sentiment_score"],
        mode="lines",
        line=dict(color="#4E5B6E", width=1.8),
        fill="tozeroy", fillcolor="rgba(78,91,110,0.08)",
    ))
    fig_line.update_layout(
        title=dict(
            text="Market Sentiment Trend",
            font=dict(family="DM Sans", size=14, color="#3A4556")
        ),
        **make_plot_layout()
    )
    st.plotly_chart(fig_line, use_container_width=True)

    prev_dates = [d for d in all_dates if d < selected_date]
    if prev_dates:
        prev_date = max(prev_dates)
        curr_s = (
            news_df[news_df["date"] == selected_date]
            .groupby("ticker")["sentiment_score"].mean().reset_index()
        )
        prev_s = (
            news_df[news_df["date"] == prev_date]
            .groupby("ticker")["sentiment_score"].mean().reset_index()
        )
        merged = curr_s.merge(prev_s, on="ticker", suffixes=("_now","_prev"))
        merged["Δ"] = (
            merged["sentiment_score_now"] -
            merged["sentiment_score_prev"]
        ).round(4)
        merged["Trend"] = merged["Δ"].apply(
            lambda x:
                "▲ Improving"  if x >  0.05 else
                "▲ Slight ↑"   if x >  0    else
                "▼ Declining"  if x < -0.05 else
                "▼ Slight ↓"
        )
        st.markdown(
            "<h2>Sentiment Change vs Previous Date</h2>",
            unsafe_allow_html=True
        )
        st.dataframe(
            merged.rename(columns={
                "ticker":"Ticker",
                "sentiment_score_now":"Current",
                "sentiment_score_prev":"Previous",
            })[["Ticker","Current","Previous","Δ","Trend"]],
            use_container_width=True,
        )
    else:
        st.info("No previous date available for comparison.")

    st.markdown(
        f"<h2>News Articles — {str(selected_date)[:10]}</h2>",
        unsafe_allow_html=True
    )
    news_today = news_df[news_df["date"] == selected_date]
    if not news_today.empty:
        for _, row in news_today.iterrows():
            lbl = str(row.get("sentiment_label","neutral")).lower()
            badge_cls = (
                "badge-positive" if lbl == "positive" else
                "badge-negative" if lbl == "negative" else
                "badge-neutral"
            )
            try:
                score_str = f"{float(row.get('sentiment_score',0)):.3f}"
            except Exception:
                score_str = str(row.get("sentiment_score",""))
            st.markdown(f"""
            <div class='news-item'>
                <div style='display:flex;justify-content:space-between;
                            align-items:flex-start;margin-bottom:0.3rem'>
                    <span class='ticker'>{row.get("ticker","—")}</span>
                    <span class='badge {badge_cls}'>
                        {lbl.upper()} · {score_str}
                    </span>
                </div>
                <div class='news-headline'>
                    {row.get("headline","No headline")}
                </div>
                <div class='news-meta'>
                    {str(row.get("source","")).upper()} ·
                    {str(row.get("date",""))[:10]}
                </div>
                <div class='news-body'>{row.get("content","")}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No articles for this date.")


# ─────────────────────────────────────────────
#  PAGE 2  —  PORTFOLIO OPTIMIZER
# ─────────────────────────────────────────────
elif page == "⚙️ Portfolio Optimizer":

    st.markdown("""
    <div class='page-header'>
        <span class='page-header-title'>Portfolio Optimizer</span>
        <span class='page-tag'>Black-Litterman · Live API</span>
    </div>
    """, unsafe_allow_html=True)

    col_p1, col_p2, col_p3 = st.columns([2, 2, 1])
    with col_p1:
        tau = st.slider(
            "τ — AI Confidence (higher = more trust in AI views)",
            0.01, 0.10, 0.025, 0.005, format="%.3f"
        )
    with col_p2:
        risk = st.slider(
            "δ — Risk Aversion (higher = more conservative)",
            1.0, 5.0, 2.5, 0.1, format="%.1f"
        )
    with col_p3:
        if forecast_df is not None and not forecast_df.empty:
            avail_dates = sorted(
                forecast_df["date"].dt.strftime("%Y-%m-%d").unique()
            )
            sel_date = st.selectbox(
                "Date", avail_dates, index=len(avail_dates) // 2
            )
        else:
            sel_date = "2023-06-15"

    run_btn = st.button("Run Black-Litterman Optimization →")

    if run_btn:
        with st.spinner("Calling Black-Litterman API…"):
            data = get_portfolio_data(tau, risk, sel_date)

        if data:
            left, right = st.columns([3, 1])

            with left:
                df_w = pd.DataFrame({
                    "Ticker":      data["tickers"],
                    "Weight %":    [round(w,3) for w in data["weights_percent"]],
                    "AI View":     [round(v,4) for v in data["ai_views"]],
                    "Equilibrium": [round(e,4) for e in data["equilibrium_returns"]],
                    "Posterior":   [round(p,4) for p in data["posterior_returns"]],
                }).sort_values("Weight %", ascending=False)

                EQ = 100 / len(df_w)
                df_w["vs_eq"]  = (df_w["Weight %"] - EQ).round(3)
                df_w["Status"] = df_w["vs_eq"].apply(
                    lambda x: "OVERWEIGHT" if x > 0 else "UNDERWEIGHT"
                )
                bar_colors = [
                    "#3A7D5B" if x > 0 else "#8B3A3A"
                    for x in df_w["vs_eq"]
                ]

                fig_w = go.Figure(go.Bar(
                    x=df_w["Ticker"], y=df_w["Weight %"],
                    marker_color=bar_colors,
                    text=df_w["Weight %"].apply(lambda x: f"{x:.1f}%"),
                    textposition="outside",
                    textfont=dict(family="DM Mono", size=10, color="#6C7A8E"),
                ))
                fig_w.add_hline(
                    y=EQ, line_dash="dot", line_color="#8E9AAB",
                    annotation_text=f"Equal weight {EQ:.2f}%",
                    annotation_font=dict(color="#8E9AAB", size=10),
                )
                fig_w.update_layout(
                    title=dict(
                        text=f"Optimal Weights  ·  τ={tau:.3f}  ·  δ={risk:.1f}",
                        font=dict(family="DM Sans", size=14, color="#3A4556")
                    ),
                    showlegend=False,
                    **make_plot_layout()
                )
                st.plotly_chart(fig_w, use_container_width=True)

                st.markdown(
                    "<h2>Allocation Breakdown</h2>",
                    unsafe_allow_html=True
                )
                df_w["Explanation"] = df_w.apply(
                    lambda r: (
                        f"AI view {r['AI View']:.2%} vs "
                        f"equilibrium {r['Equilibrium']:.2%} → "
                        f"posterior {r['Posterior']:.2%}"
                    ), axis=1
                )
                st.dataframe(
                    df_w[["Ticker","Weight %","vs_eq",
                          "Status","Explanation"]],
                    use_container_width=True,
                )

                with st.expander(
                    "τ Sensitivity — how weights change with AI confidence"
                ):
                    tau_vals = [0.01, 0.025, 0.05, 0.075, 0.10]
                    sens = []
                    prog = st.progress(0)
                    for i, t in enumerate(tau_vals):
                        r = get_portfolio_data(t, risk, sel_date)
                        if r:
                            for tick, w in zip(
                                r["tickers"], r["weights_percent"]
                            ):
                                sens.append({
                                    "τ": t, "Ticker": tick,
                                    "Weight %": round(w, 3)
                                })
                        prog.progress((i + 1) / len(tau_vals))
                        time.sleep(1)

                    if sens:
                        sf = pd.DataFrame(sens)
                        fig_s = px.line(
                            sf, x="τ", y="Weight %", color="Ticker",
                            title="Portfolio Weights vs AI Confidence (τ)",
                            color_discrete_sequence=[
                                "#4E5B6E","#8E9AAB","#3A7D5B","#8B3A3A",
                                "#6C7A8E","#B8C2D0","#3A4556",
                                "#5D6A7A","#A8B2C0"
                            ]
                        )
                        fig_s.add_hline(
                            y=EQ, line_dash="dot", line_color="#8E9AAB",
                            annotation_text="Equal weight",
                            annotation_font=dict(color="#8E9AAB", size=10),
                        )
                        fig_s.update_layout(**make_plot_layout())
                        st.plotly_chart(fig_s, use_container_width=True)
                        st.caption(
                            "Steeper lines = stocks where AI views diverge "
                            "more from market equilibrium."
                        )

                with st.expander("Black-Litterman posterior formula"):
                    st.latex(
                        r"E[R]=\left[(\tau\Sigma)^{-1}+P^\top\Omega^{-1}P"
                        r"\right]^{-1}\left[(\tau\Sigma)^{-1}\Pi+"
                        r"P^\top\Omega^{-1}Q\right]"
                    )
                    st.markdown("""
                    | Symbol | Meaning |
                    |--------|---------|
                    | Π | Market equilibrium returns (CAPM reverse-optimisation) |
                    | Q | CNN-LSTM return forecasts (AI views) |
                    | Σ | Historical covariance matrix |
                    | Ω | Diagonal view uncertainty (validation errors) |
                    | τ | Confidence scalar (your slider) |
                    | P | Identity matrix (absolute views, one per asset) |
                    """)

            with right:
                st.markdown("<h2>Metrics</h2>", unsafe_allow_html=True)
                st.metric("Expected Return",
                          f"{data['portfolio_return']:.4%}")
                st.metric("Daily Volatility",
                          f"{data['portfolio_volatility']:.4%}")
                st.metric("Sharpe Ratio",
                          f"{data['sharpe_ratio']:.2f}")

                st.markdown("---")
                st.markdown(
                    "<h2>Backtest (2023–2024)</h2>",
                    unsafe_allow_html=True
                )
                st.metric("AI-BL Final Wealth",  "25.84 ZiG", "+20.4% vs EW")
                st.metric("Equal-Weight Wealth", "21.47 ZiG")
                st.metric("Market-Cap Wealth",   "0.0003 ZiG", "-99.99%")

                st.markdown("---")
                st.markdown(
                    "<h2>USD Preservation</h2>",
                    unsafe_allow_html=True
                )
                inv = st.number_input(
                    "Initial investment (USD)",
                    min_value=100, max_value=100000,
                    value=1000, step=100
                )
                st.markdown(f"""
                <div style='margin-top:0.8rem'>
                    <div class='overline'>AI-BL Portfolio</div>
                    <div style='font-family:Playfair Display,serif;
                                font-size:1.5rem;font-weight:700;
                                color:#3A7D5B'>${inv*0.766:,.2f}</div>
                    <div style='font-size:0.72rem;color:#8E9AAB;
                                margin-bottom:0.9rem'>76.6% preserved</div>
                    <div class='overline'>Equal-Weight</div>
                    <div style='font-family:Playfair Display,serif;
                                font-size:1.5rem;font-weight:700;
                                color:#4E5B6E'>${inv*0.636:,.2f}</div>
                    <div style='font-size:0.72rem;color:#8E9AAB;
                                margin-bottom:0.9rem'>63.6% preserved</div>
                    <div class='overline'>Market-Cap</div>
                    <div style='font-family:Playfair Display,serif;
                                font-size:1.5rem;font-weight:700;
                                color:#8B3A3A'>${inv*0.000009:,.4f}</div>
                    <div style='font-size:0.72rem;color:#8E9AAB'>
                        0.0009% preserved
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE 3  —  STOCK ANALYSIS
#  AI Signals section only calls API on button
#  click to avoid rate limit on page load
# ─────────────────────────────────────────────
elif page == "📈 Stock Analysis":

    st.markdown("""
    <div class='page-header'>
        <span class='page-header-title'>Stock Analysis</span>
        <span class='page-tag'>Fundamentals · AI Signals · Forecasts</span>
    </div>
    """, unsafe_allow_html=True)

    if news_df.empty:
        st.warning("No news data loaded.")
        st.stop()

    col_s1, col_s2 = st.columns(2)
    selected_ticker  = col_s1.selectbox(
        "Select stock", sorted(news_df["ticker"].unique())
    )
    all_dates_sa     = sorted(news_df["date"].unique())
    selected_date_sa = col_s2.selectbox("Select date", all_dates_sa)

    # ── fundamentals (no API needed) ──
    st.markdown("<h2>Fundamentals</h2>", unsafe_allow_html=True)
    if fund_df is not None and not fund_df.empty:
        fund = fund_df[fund_df["ticker"] == selected_ticker]
        if not fund.empty:
            f    = fund.iloc[0]
            cols = st.columns(6)
            fields = [
                ("P/B","P/B"),("ROE","ROE"),
                ("Net Margin","Net Margin"),
                ("Dividend Yield","Dividend Yield"),
                ("Market Cap (ZiG mn)","Market Cap (ZiG mn)"),
                ("P/E","P/E"),
            ]
            for col_obj, (label, key) in zip(cols, fields):
                raw = f.get(key, "N/A")
                if isinstance(raw, float):
                    if key in ("ROE","Net Margin","Dividend Yield"):
                        display = f"{raw:.1%}"
                    elif key == "Market Cap (ZiG mn)":
                        display = f"{raw:,.0f}"
                    else:
                        display = f"{raw:.2f}"
                else:
                    display = str(raw)
                col_obj.metric(label, display)
        else:
            st.info("No fundamentals available for this ticker.")
    else:
        st.info("Fundamentals file not loaded.")

    # ── AI signals — button-triggered to avoid rate limit ──
    st.markdown("<h2>AI Signals</h2>", unsafe_allow_html=True)

    # Sentiment from CSV (no API needed)
    news_s = news_df[
        (news_df["ticker"] == selected_ticker) &
        (news_df["date"]   == selected_date_sa)
    ]
    sent_score = news_s["sentiment_score"].iloc[0] if not news_s.empty else None
    sent_label = news_s["sentiment_label"].iloc[0]  if not news_s.empty else "N/A"

    # CNN-LSTM view from CSV (no API needed)
    fc_row = pd.DataFrame()
    if forecast_df is not None and not forecast_df.empty:
        fc_row = forecast_df[
            (forecast_df["ticker"] == selected_ticker) &
            (forecast_df["date"]   == selected_date_sa)
        ]
    ai_view = fc_row["predicted_return"].iloc[0] if not fc_row.empty else None

    # Show sentiment + CNN view immediately (no API)
    c1, c2 = st.columns(2)
    c1.metric(
        "Sentiment Score",
        f"{float(sent_score):.3f}" if sent_score is not None else "N/A",
        str(sent_label),
    )
    c2.metric(
        "AI View (CNN-LSTM)",
        f"{float(ai_view):.2%}" if ai_view is not None else "N/A",
    )

    # BL weight requires API — only fetch on button click
    st.markdown("""
    <div style='font-family:DM Mono,monospace;font-size:0.72rem;
                color:#8E9AAB;margin:0.6rem 0 0.4rem'>
        Click below to load AI-BL portfolio weight for this stock
        (calls the live optimization API).
    </div>
    """, unsafe_allow_html=True)

    load_weight_btn = st.button("Load AI-BL Weight →")

    if load_weight_btn:
        date_str_sa = (
            selected_date_sa.strftime("%Y-%m-%d")
            if hasattr(selected_date_sa, "strftime")
            else str(selected_date_sa)[:10]
        )
        with st.spinner("Fetching portfolio weight…"):
            api_d = get_portfolio_data(0.025, 2.5, date_str_sa)

        ai_bl_w = vs_eq = None
        if api_d:
            try:
                idx     = api_d["tickers"].index(selected_ticker)
                ai_bl_w = api_d["weights_percent"][idx]
                vs_eq   = ai_bl_w - 100 / len(api_d["tickers"])
            except (ValueError, KeyError):
                pass

        c3, c4 = st.columns(2)
        c3.metric(
            "AI-BL Weight",
            f"{ai_bl_w:.2f}%" if ai_bl_w is not None else "N/A",
        )
        c4.metric(
            "vs Equal Weight",
            f"{vs_eq:+.2f}%" if vs_eq is not None else "N/A",
        )

        if ai_bl_w is not None:
            direction = "overweighted" if vs_eq > 0 else "underweighted"
            reason = (
                f"bullish AI view ({float(ai_view):.2%})"
                if ai_view and ai_view > 0
                else "bearish or neutral AI view"
            ) if ai_view is not None else "AI view data"
            st.markdown(f"""
            <div class='card-accent' style='margin-top:0.6rem'>
                <div style='font-size:0.8rem;color:#6C7A8E;line-height:1.7'>
                    <b style='color:#3A4556'>{selected_ticker}</b> is
                    <b style='color:#3A4556'>{direction}</b> by
                    <b style='color:#3A4556'>{abs(vs_eq):.2f}%</b>
                    relative to the equal-weight benchmark,
                    driven by {reason} combined with the
                    Black-Litterman Bayesian posterior at τ = 0.025.
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── price & sentiment chart ──
    st.markdown(
        "<h2>Price & Sentiment Over Time</h2>",
        unsafe_allow_html=True
    )
    if prices_long is not None and not prices_long.empty:
        sp = prices_long[prices_long["ticker"] == selected_ticker].copy()
        ss = news_df[news_df["ticker"] == selected_ticker].copy()
        if not sp.empty and not ss.empty:
            fig_ps = go.Figure()
            fig_ps.add_trace(go.Scatter(
                x=sp["Date"], y=sp["price"],
                name="Price",
                line=dict(color="#4E5B6E", width=1.8),
                yaxis="y",
            ))
            fig_ps.add_trace(go.Scatter(
                x=ss["date"], y=ss["sentiment_score"],
                name="Sentiment",
                line=dict(color="#8E9AAB", width=1.2, dash="dot"),
                yaxis="y2",
            ))
            fig_ps.update_layout(
                title=dict(
                    text=f"{selected_ticker} — Price vs Sentiment",
                    font=dict(family="DM Sans", size=14, color="#3A4556")
                ),
                **make_plot_layout(
                    yaxis2=dict(
                        title="Sentiment",
                        overlaying="y",
                        side="right",
                        range=[-1, 1],
                        gridcolor="#D9E0E8",
                        tickfont=dict(color="#8E9AAB"),
                    )
                )
            )
            st.plotly_chart(fig_ps, use_container_width=True)
        else:
            st.warning(
                "Insufficient price or sentiment data for this ticker."
            )
    else:
        st.warning("Price data not loaded.")

    # ── forecast vs actual ──
    st.markdown(
        "<h2>CNN-LSTM Forecast vs Actual Returns</h2>",
        unsafe_allow_html=True
    )
    if forecast_df is not None and not forecast_df.empty:
        sf = forecast_df[forecast_df["ticker"] == selected_ticker].copy()
        if not sf.empty:
            fig_f = go.Figure()
            fig_f.add_trace(go.Scatter(
                x=sf["date"], y=sf["predicted_return"],
                name="Predicted",
                line=dict(color="#4E5B6E", width=1.8),
            ))
            fig_f.add_trace(go.Scatter(
                x=sf["date"], y=sf["actual_return"],
                name="Actual",
                line=dict(color="#8E9AAB", width=1.2),
            ))
            fig_f.update_layout(
                title=dict(
                    text="CNN-LSTM Forecast vs Actual Returns",
                    font=dict(family="DM Sans", size=14, color="#3A4556")
                ),
                **make_plot_layout()
            )
            st.plotly_chart(fig_f, use_container_width=True)
            st.caption(
                "Directional accuracy: 34.47% — consistent with "
                "high-volatility frontier market literature."
            )
        else:
            st.info("No forecast data available for this ticker.")
    else:
        st.info("Forecast file not loaded.")


# ─────────────────────────────────────────────
#  PAGE 4  —  LIVE NEWS FEED
# ─────────────────────────────────────────────
elif page == "📰 Live News Feed":

    st.markdown("""
    <div class='page-header'>
        <span class='page-header-title'>Live News Feed</span>
        <span class='page-tag'>RSS · Filtered for 9 Holdings</span>
    </div>
    """, unsafe_allow_html=True)

    rss_url = st.text_input(
        "RSS feed URL",
        value="https://www.herald.co.zw/feed/"
    )

    if st.button("Fetch News"):
        with st.spinner("Fetching latest articles…"):
            entries = fetch_rss_feed(rss_url)

        if entries:
            st.markdown(
                f"<div class='badge badge-iron'>"
                f"{len(entries)} relevant articles found"
                f"</div><br><br>",
                unsafe_allow_html=True
            )
            for e in entries:
                st.markdown(f"""
                <div class='news-item'>
                    <div class='news-headline'>
                        <a href='{e["link"]}'
                           style='color:#3A4556;text-decoration:none'>
                            {e["title"]}
                        </a>
                    </div>
                    <div class='news-meta'>{e["published"]}</div>
                    <div class='news-body'>{e["summary"]}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning(
                "No relevant articles found for the 9 holdings. "
                "The feed may not contain recent ZSE-related news."
            )

    st.markdown("---")
    st.markdown("""
    <div style='font-family:DM Mono,monospace;font-size:0.62rem;
                color:#A8B2C0;line-height:1.9'>
    Filtered keywords: AFDIS · African Distillers · BAT · British American
    Tobacco · CAFCA · CBZ · Delta · Dairibord · Econet · OK Zimbabwe · Seed Co
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE 5  —  USER GUIDE
# ─────────────────────────────────────────────
elif page == "📘 User Guide":

    st.markdown("""
    <div class='page-header'>
        <span class='page-header-title'>User Guide</span>
        <span class='page-tag'>How to use this system</span>
    </div>
    """, unsafe_allow_html=True)

    guides = [
        ("📊","Market Intelligence","DA-BERT Sentiment",
         "Upload a news CSV or use the default dataset. Select a trading date "
         "to see sentiment scores per stock, the market-wide trend, and "
         "individual news articles with DA-BERT labels, scores, and confidence. "
         "The change table compares today's sentiment to the previous news date."),
        ("⚙️","Portfolio Optimizer","Black-Litterman · Live API",
         "Adjust τ (AI confidence: 0.01 = near-market-equilibrium, "
         "0.10 = high AI trust) and δ (risk aversion 1–5). Select an "
         "optimization date. Click Run Optimization to call the live FastAPI "
         "backend. Weights, explanations, and metrics are returned dynamically. "
         "The τ Sensitivity panel proves the mathematics changes with your input."),
        ("📈","Stock Analysis","Fundamentals · AI Signals",
         "Select a stock and date. Fundamentals and CNN-LSTM signals load "
         "instantly from CSV. Click Load AI-BL Weight to fetch the "
         "portfolio weight from the live API without hitting rate limits. "
         "Price vs sentiment and forecast vs actual charts load automatically."),
        ("📰","Live News Feed","RSS · Auto-filtered",
         "Enter any RSS feed URL (default: The Herald). The system filters "
         "to show only articles mentioning the 9 portfolio companies — "
         "demonstrating the news pipeline that feeds the DA-BERT model."),
        ("💾","Upload Your Data","CSV Override",
         "On the Market Intelligence page, upload your own news CSV. "
         "The system immediately adapts. Required columns: date, ticker, "
         "headline, content, sentiment_score, sentiment_label, "
         "source, confidence."),
    ]

    for icon, title, tag, desc in guides:
        st.markdown(f"""
        <div class='guide-card'>
            <div style='display:flex;align-items:center;
                        gap:10px;margin-bottom:0.6rem'>
                <span style='font-size:1.1rem'>{icon}</span>
                <span style='font-family:DM Sans,sans-serif;font-size:0.93rem;
                             font-weight:600;color:#3A4556'>{title}</span>
                <span class='badge badge-iron'>{tag}</span>
            </div>
            <p style='font-size:0.8rem;color:#6C7A8E;
                      line-height:1.75;margin:0'>{desc}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='font-family:DM Mono,monospace;font-size:0.61rem;
                color:#A8B2C0;line-height:2'>
    DA-BERT fine-tuned on 8,465 Zimbabwean news articles · accuracy 81.4% · F1 0.79<br>
    CNN-LSTM directional accuracy 34.47% · MAE 5.88% · frontier market baseline<br>
    Black-Litterman posterior: τΣ prior + Ω view uncertainty · long-only · max Sharpe<br>
    Backend: FastAPI on Render · Sources: ZSE, The Herald, NewsDay, Zimbabwe Independent
    </div>
    """, unsafe_allow_html=True)