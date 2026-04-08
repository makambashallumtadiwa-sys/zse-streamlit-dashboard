import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import feedparser
from datetime import datetime

st.set_page_config(
    page_title="ZSE · Portfolio Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  DESIGN SYSTEM  — dark terminal + gold accent
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500&display=swap');

/* ── tokens ── */
:root {
    --bg:        #0D0F12;
    --bg2:       #13161B;
    --bg3:       #1A1E25;
    --border:    #252A33;
    --border2:   #2E3540;
    --gold:      #C9A84C;
    --gold-dim:  #7A6130;
    --gold-glow: rgba(201,168,76,0.12);
    --text:      #E8EAF0;
    --text2:     #8A95A3;
    --text3:     #4E5968;
    --green:     #3DBA7F;
    --red:       #E05252;
    --blue:      #4A9EE8;
    --font-head: 'Syne', sans-serif;
    --font-body: 'Inter', sans-serif;
    --font-mono: 'IBM Plex Mono', monospace;
}

/* ── base reset ── */
html, body, .stApp, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
}

[data-testid="stHeader"] { background: var(--bg) !important; }

/* ── sidebar ── */
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text2) !important; font-family: var(--font-mono) !important; font-size: 0.78rem !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: var(--text3) !important; font-size: 0.7rem !important; letter-spacing: 0.08em; text-transform: uppercase; }

/* ── sidebar radio as nav pills ── */
[data-testid="stSidebar"] .stRadio label {
    display: block;
    padding: 0.55rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.15s;
    color: var(--text2) !important;
    letter-spacing: 0.03em;
}
[data-testid="stSidebar"] .stRadio label:hover { background: var(--bg3) !important; color: var(--text) !important; }
[data-testid="stSidebar"] .stRadio [aria-checked="true"] + label,
[data-testid="stSidebar"] .stRadio input:checked + div { color: var(--gold) !important; }

/* ── headings ── */
h1, h2, h3, .main-title {
    font-family: var(--font-head) !important;
    color: var(--text) !important;
    letter-spacing: -0.02em;
}
h1 { font-size: 2rem !important; font-weight: 800 !important; }
h2 { font-size: 1.3rem !important; font-weight: 700 !important; border-bottom: 1px solid var(--border); padding-bottom: 0.4rem; margin-top: 1.8rem !important; }
h3 { font-size: 1rem !important; font-weight: 600 !important; color: var(--text2) !important; }

/* ── cards ── */
.card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}
.card-gold {
    background: var(--bg2);
    border: 1px solid var(--gold-dim);
    border-radius: 6px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    box-shadow: inset 0 0 40px var(--gold-glow);
}

/* ── KPI tiles ── */
.kpi-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 12px; margin: 1rem 0; }
.kpi {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1rem 1.2rem;
    position: relative;
    overflow: hidden;
}
.kpi::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: var(--gold);
}
.kpi-label { font-family: var(--font-mono); font-size: 0.65rem; color: var(--text3); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.3rem; }
.kpi-value { font-family: var(--font-head); font-size: 1.8rem; font-weight: 800; color: var(--gold); line-height: 1; }
.kpi-sub   { font-size: 0.72rem; color: var(--text2); margin-top: 0.25rem; font-family: var(--font-mono); }

/* ── status badges ── */
.badge { display: inline-block; padding: 2px 8px; border-radius: 3px; font-family: var(--font-mono); font-size: 0.68rem; font-weight: 500; letter-spacing: 0.05em; }
.badge-green { background: rgba(61,186,127,0.15); color: var(--green); border: 1px solid rgba(61,186,127,0.3); }
.badge-red   { background: rgba(224,82,82,0.15);  color: var(--red);   border: 1px solid rgba(224,82,82,0.3); }
.badge-gold  { background: var(--gold-glow);       color: var(--gold);  border: 1px solid var(--gold-dim); }
.badge-blue  { background: rgba(74,158,232,0.12);  color: var(--blue);  border: 1px solid rgba(74,158,232,0.3); }

/* ── ticker label ── */
.ticker { font-family: var(--font-mono); font-size: 0.75rem; background: var(--bg3); border: 1px solid var(--border2); padding: 2px 7px; border-radius: 3px; color: var(--gold); }

/* ── news card ── */
.news-item {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-left: 3px solid var(--gold-dim);
    border-radius: 4px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.7rem;
}
.news-headline { font-family: var(--font-head); font-size: 0.9rem; font-weight: 600; color: var(--text); margin-bottom: 0.3rem; }
.news-meta { font-family: var(--font-mono); font-size: 0.65rem; color: var(--text3); margin-bottom: 0.4rem; }
.news-body { font-size: 0.82rem; color: var(--text2); line-height: 1.6; }

/* ── section label (mono overline) ── */
.overline { font-family: var(--font-mono); font-size: 0.65rem; color: var(--gold); text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 0.4rem; }

/* ── table ── */
.stDataFrame, [data-testid="stDataFrameResizable"] {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
}

/* ── inputs ── */
.stSelectbox > div > div,
.stDateInput > div > div,
.stNumberInput > div > div { background: var(--bg3) !important; border: 1px solid var(--border2) !important; color: var(--text) !important; border-radius: 4px !important; }
.stSlider .stSlider { accent-color: var(--gold) !important; }

/* ── button ── */
.stButton > button {
    background: transparent !important;
    border: 1px solid var(--gold-dim) !important;
    color: var(--gold) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.05em !important;
    border-radius: 4px !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: var(--gold-glow) !important;
    border-color: var(--gold) !important;
}

/* ── file uploader ── */
[data-testid="stFileUploader"] {
    background: var(--bg3) !important;
    border: 1px dashed var(--border2) !important;
    border-radius: 6px !important;
}

/* ── metric overrides ── */
[data-testid="stMetricValue"] { font-family: var(--font-head) !important; font-size: 1.6rem !important; color: var(--gold) !important; font-weight: 800 !important; }
[data-testid="stMetricLabel"] { font-family: var(--font-mono) !important; font-size: 0.65rem !important; color: var(--text3) !important; text-transform: uppercase !important; letter-spacing: 0.1em !important; }
[data-testid="stMetricDelta"] { font-family: var(--font-mono) !important; font-size: 0.75rem !important; }

/* ── progress bar ── */
.stProgress > div > div { background: var(--gold) !important; }

/* ── divider ── */
hr { border-color: var(--border) !important; }

/* ── expander ── */
.streamlit-expanderHeader {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    font-family: var(--font-mono) !important;
    font-size: 0.8rem !important;
    color: var(--text2) !important;
}

/* ── scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }

/* ── plotly chart background override ── */
.js-plotly-plot .plotly { background: transparent !important; }

/* ── page header bar ── */
.page-header {
    display: flex; align-items: baseline; gap: 12px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.8rem; margin-bottom: 1.4rem;
}
.page-header h1 { margin: 0 !important; padding: 0 !important; font-size: 1.5rem !important; }
.page-header .page-tag {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    color: var(--text3);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    background: var(--bg3);
    border: 1px solid var(--border);
    padding: 2px 8px;
    border-radius: 3px;
}

/* ── sidebar logo area ── */
.sidebar-logo {
    font-family: var(--font-head);
    font-size: 1.1rem;
    font-weight: 800;
    color: var(--gold) !important;
    letter-spacing: -0.02em;
    padding: 0.5rem 0 1.2rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1rem;
}
.sidebar-logo span { color: var(--text3) !important; font-weight: 400; font-size: 0.7rem; display: block; letter-spacing: 0.05em; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PLOTLY THEME  (dark, matches the app)
# ─────────────────────────────────────────────
PLOT_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#13161B",
    font=dict(family="IBM Plex Mono, monospace", color="#8A95A3", size=11),
    xaxis=dict(gridcolor="#1A1E25", linecolor="#252A33", tickcolor="#252A33"),
    yaxis=dict(gridcolor="#1A1E25", linecolor="#252A33", tickcolor="#252A33"),
    colorway=["#C9A84C", "#4A9EE8", "#3DBA7F", "#E05252", "#A67CE0", "#5DCAA5"],
    hoverlabel=dict(bgcolor="#1A1E25", bordercolor="#252A33", font_color="#E8EAF0"),
    margin=dict(l=12, r=12, t=36, b=12),
)


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
        "AFDIS","African Distillers","BAT","British American Tobacco","CAFCA","Cafca",
        "CBZ","Delta","DZL","Dairibord","ECO","Econet","OKZ","OK Zimbabwe","SEED","Seed Co"
    ]
    try:
        feed = feedparser.parse(url)
        entries = []
        for entry in feed.entries[:30]:
            title   = entry.title.lower()
            summary = entry.get("summary","").lower()
            if any(k.lower() in title or k.lower() in summary for k in keywords):
                entries.append({
                    "title":     entry.title,
                    "link":      entry.link,
                    "published": entry.get("published","—"),
                    "summary":   (entry.get("summary","")[:280] + "…") if len(entry.get("summary","")) > 280 else entry.get("summary","")
                })
        return entries
    except Exception as e:
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
            "div_yield":"Dividend Yield","market_cap_zig_millions":"Market Cap (ZiG mn)","pe_ratio":"P/E"
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

API_URL = "https://zse-ai-backend.onrender.com/api/optimize"

def get_portfolio_data(tau, risk, date):
    try:
        r = requests.post(API_URL, json={"tau": tau, "risk_aversion": risk, "selected_date": date}, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"API error — {e}")
        return None


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        ZSE · INTELLIGENCE
        <span>Zimbabwe Stock Exchange · AI Portfolio System</span>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "NAVIGATE",
        ["Home", "Market Intelligence", "Portfolio Optimizer", "Stock Analysis", "Live News", "User Guide"],
        label_visibility="visible"
    )

    st.markdown("---")
    st.markdown("""
    <div style='font-family:var(--font-mono);font-size:0.62rem;color:#4E5968;line-height:1.8'>
    DA-BERT Accuracy &nbsp; <span style='color:#C9A84C'>81.4%</span><br>
    Sharpe Ratio &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <span style='color:#C9A84C'>0.79</span><br>
    USD Preserved &nbsp;&nbsp;&nbsp;&nbsp; <span style='color:#3DBA7F'>76.6%</span><br>
    Outperformance &nbsp;&nbsp; <span style='color:#3DBA7F'>+20.4%</span><br>
    Test Period &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <span style='color:#8A95A3'>2023–2024</span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE 0  —  HOME
# ─────────────────────────────────────────────
if page == "Home":

    st.markdown("""
    <div style='padding: 2.5rem 0 1rem'>
        <div style='font-family:var(--font-mono);font-size:0.65rem;color:#C9A84C;
                    letter-spacing:0.2em;text-transform:uppercase;margin-bottom:0.6rem'>
            Zimbabwe Stock Exchange · AI Portfolio Intelligence
        </div>
        <h1 style='font-family:Syne,sans-serif;font-size:3rem;font-weight:800;
                   color:#E8EAF0;letter-spacing:-0.03em;line-height:1.1;margin:0'>
            Sentiment-Driven<br>
            <span style='color:#C9A84C'>Portfolio Optimization</span>
        </h1>
        <p style='color:#8A95A3;font-size:0.95rem;margin-top:1rem;max-width:560px;line-height:1.7'>
            Domain-adapted BERT sentiment analysis · CNN-LSTM return forecasting ·
            Black-Litterman Bayesian fusion — applied to the ZSE frontier market.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # KPI row
    st.markdown("""
    <div class='kpi-grid'>
        <div class='kpi'>
            <div class='kpi-label'>Outperformance</div>
            <div class='kpi-value'>+20.4%</div>
            <div class='kpi-sub'>vs equal-weight benchmark</div>
        </div>
        <div class='kpi'>
            <div class='kpi-label'>USD Wealth Preserved</div>
            <div class='kpi-value'>76.6%</div>
            <div class='kpi-sub'>during ZWL→ZiG collapse</div>
        </div>
        <div class='kpi'>
            <div class='kpi-label'>Sharpe Ratio</div>
            <div class='kpi-value'>0.79</div>
            <div class='kpi-sub'>AI-BL portfolio · β = 0.084</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Feature grid
    col1, col2, col3 = st.columns(3)
    features = [
        ("01", "Market Intelligence", "DA-BERT sentiment scores from Zimbabwean financial news. Upload new data and watch the system adapt."),
        ("02", "Portfolio Optimizer", "Adjust τ (AI confidence) and δ (risk aversion). The Black-Litterman API returns live optimal weights."),
        ("03", "Stock Deep Dive", "Fundamentals, AI signals, price-sentiment correlation, CNN-LSTM forecast vs actual."),
        ("04", "τ Sensitivity", "See how portfolio weights shift as you increase trust in AI views over market equilibrium."),
        ("05", "Currency Simulator", "Model wealth preservation across portfolios during hyperinflationary currency collapse."),
        ("06", "Live News Feed", "RSS-filtered headlines from The Herald and custom sources, matched to your 9 holdings."),
    ]
    for i, (num, title, desc) in enumerate(features):
        with [col1, col2, col3][i % 3]:
            st.markdown(f"""
            <div class='card' style='min-height:130px'>
                <div style='font-family:var(--font-mono);font-size:0.6rem;
                            color:#4E5968;margin-bottom:0.5rem'>{num}</div>
                <div style='font-family:Syne,sans-serif;font-size:0.9rem;
                            font-weight:700;color:#E8EAF0;margin-bottom:0.4rem'>{title}</div>
                <div style='font-size:0.78rem;color:#8A95A3;line-height:1.6'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='font-family:var(--font-mono);font-size:0.65rem;color:#4E5968;text-align:center;padding:0.5rem 0'>
        Research · Harare Institute of Technology · Department of Financial Engineering · 2026
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE 1  —  MARKET INTELLIGENCE
# ─────────────────────────────────────────────
elif page == "Market Intelligence":

    st.markdown("""
    <div class='page-header'>
        <h1>Market Intelligence</h1>
        <span class='page-tag'>DA-BERT Sentiment</span>
    </div>
    """, unsafe_allow_html=True)

    # Upload
    uploaded = st.file_uploader("Upload news CSV to override default data", type=["csv"])
    if uploaded:
        try:
            new_df = pd.read_csv(uploaded, parse_dates=["date"])
            st.session_state.news_df = new_df
            news_df = new_df
            col_a, col_b = st.columns(2)
            col_a.metric("Articles loaded", len(new_df))
            col_b.metric("Date range", f"{new_df['date'].min().date()} → {new_df['date'].max().date()}")
            st.success("Dataset updated — all visuals below reflect your upload.")
        except Exception as e:
            st.error(f"Could not parse file — {e}")

    if news_df.empty:
        st.warning("No news data found. Upload a CSV above.")
        st.stop()

    all_dates = sorted(news_df["date"].unique())
    selected_date = st.selectbox("Trading date", all_dates)
    daily = news_df[news_df["date"] == selected_date]

    if not daily.empty:
        avg_s = daily["sentiment_score"].mean()
        vol_s = (daily["sentiment_score"].max() - daily["sentiment_score"].min()) / 2

        c1, c2, c3 = st.columns(3)
        c1.metric("Average Sentiment", f"{avg_s:.3f}")
        c2.metric("Sentiment Spread", f"{vol_s:.3f}")
        pct_pos = (daily["sentiment_score"] > 0.1).mean() * 100
        c3.metric("% Positive Articles", f"{pct_pos:.0f}%")

        # Sentiment bar
        ticker_avg = daily.groupby("ticker")["sentiment_score"].mean().reset_index()
        ticker_avg["color"] = ticker_avg["sentiment_score"].apply(
            lambda x: "#3DBA7F" if x > 0.1 else ("#E05252" if x < -0.1 else "#C9A84C")
        )
        fig_bar = go.Figure(go.Bar(
            x=ticker_avg["ticker"], y=ticker_avg["sentiment_score"],
            marker_color=ticker_avg["color"],
            text=ticker_avg["sentiment_score"].round(3),
            textposition="outside", textfont=dict(family="IBM Plex Mono", size=10, color="#8A95A3")
        ))
        fig_bar.update_layout(
            title=dict(text="Sentiment Score by Stock", font=dict(family="Syne", size=14, color="#E8EAF0")),
            showlegend=False, **PLOT_THEME
        )
        fig_bar.add_hline(y=0, line_color="#252A33", line_width=1)
        st.plotly_chart(fig_bar, use_container_width=True)

    # Sentiment trend line
    trend = news_df.groupby("date")["sentiment_score"].mean().reset_index()
    fig_line = go.Figure(go.Scatter(
        x=trend["date"], y=trend["sentiment_score"],
        mode="lines", line=dict(color="#C9A84C", width=1.5),
        fill="tozeroy", fillcolor="rgba(201,168,76,0.07)"
    ))
    fig_line.update_layout(
        title=dict(text="Market Sentiment Trend", font=dict(family="Syne", size=14, color="#E8EAF0")),
        **PLOT_THEME
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # Change table
    prev_dates = [d for d in all_dates if d < selected_date]
    if prev_dates:
        prev_date = max(prev_dates)
        curr_s = news_df[news_df["date"] == selected_date].groupby("ticker")["sentiment_score"].mean().reset_index()
        prev_s = news_df[news_df["date"] == prev_date].groupby("ticker")["sentiment_score"].mean().reset_index()
        merged = curr_s.merge(prev_s, on="ticker", suffixes=("_now", "_prev"))
        merged["Δ"] = merged["sentiment_score_now"] - merged["sentiment_score_prev"]
        merged["Signal"] = merged["Δ"].apply(
            lambda x: "▲ Improving" if x > 0.05 else ("▲ Slight ↑" if x > 0 else ("▼ Declining" if x < -0.05 else "▼ Slight ↓"))
        )
        st.markdown("<h2>Sentiment Change</h2>", unsafe_allow_html=True)
        st.dataframe(merged.rename(columns={"ticker":"Ticker","sentiment_score_now":"Now","sentiment_score_prev":"Prev"})[["Ticker","Now","Prev","Δ","Signal"]], use_container_width=True)

    # News articles
    st.markdown(f"<h2>News Articles — {selected_date.date()}</h2>", unsafe_allow_html=True)
    news_today = news_df[news_df["date"] == selected_date]
    if not news_today.empty:
        for _, row in news_today.iterrows():
            label_color = "badge-green" if row.get("sentiment_label","") == "positive" else ("badge-red" if row.get("sentiment_label","") == "negative" else "badge-gold")
            st.markdown(f"""
            <div class='news-item'>
                <div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.3rem'>
                    <span class='ticker'>{row.get("ticker","—")}</span>
                    <span class='badge {label_color}'>{row.get("sentiment_label","neutral").upper()} · {row.get("sentiment_score",0):.3f}</span>
                </div>
                <div class='news-headline'>{row.get("headline","No headline")}</div>
                <div class='news-meta'>{str(row.get("source","")).upper()} · {str(row.get("date",""))[:10]}</div>
                <div class='news-body'>{row.get("content","")}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No articles for this date.")


# ─────────────────────────────────────────────
#  PAGE 2  —  PORTFOLIO OPTIMIZER
# ─────────────────────────────────────────────
elif page == "Portfolio Optimizer":

    st.markdown("""
    <div class='page-header'>
        <h1>Portfolio Optimizer</h1>
        <span class='page-tag'>Black-Litterman · Live API</span>
    </div>
    """, unsafe_allow_html=True)

    # Parameters
    col_p1, col_p2, col_p3 = st.columns([2, 2, 1])
    with col_p1:
        tau  = st.slider("τ — AI Confidence (higher = more trust in AI views)", 0.01, 0.10, 0.025, 0.005, format="%.3f")
    with col_p2:
        risk = st.slider("δ — Risk Aversion (higher = more conservative)", 1.0, 5.0, 2.5, 0.1, format="%.1f")
    with col_p3:
        if not forecast_df.empty:
            avail = sorted(forecast_df["date"].dt.strftime("%Y-%m-%d").unique())
            sel_date = st.selectbox("Date", avail, index=len(avail)//2)
        else:
            sel_date = "2023-06-15"

    run = st.button("Run Black-Litterman Optimization →")

    if run:
        with st.spinner("Calling optimization API…"):
            data = get_portfolio_data(tau, risk, sel_date)

        if data:
            left, right = st.columns([3, 1])

            with left:
                # Weights chart
                df_w = pd.DataFrame({
                    "Ticker":   data["tickers"],
                    "Weight %": [round(w, 3) for w in data["weights_percent"]],
                    "AI View":  [round(v, 4) for v in data["ai_views"]],
                    "Equilibrium": [round(e, 4) for e in data["equilibrium_returns"]],
                    "Posterior":   [round(p, 4) for p in data["posterior_returns"]],
                }).sort_values("Weight %", ascending=False)

                EQ = 100 / len(df_w)
                df_w["vs_eq"] = (df_w["Weight %"] - EQ).round(3)
                df_w["Status"] = df_w["vs_eq"].apply(lambda x: "OVERWEIGHT" if x > 0 else "UNDERWEIGHT")
                colors = ["#3DBA7F" if x > 0 else "#E05252" for x in df_w["vs_eq"]]

                fig_w = go.Figure(go.Bar(
                    x=df_w["Ticker"], y=df_w["Weight %"],
                    marker_color=colors,
                    text=df_w["Weight %"].apply(lambda x: f"{x:.1f}%"),
                    textposition="outside",
                    textfont=dict(family="IBM Plex Mono", size=10, color="#8A95A3")
                ))
                fig_w.add_hline(y=EQ, line_dash="dot", line_color="#C9A84C",
                                annotation_text=f"Equal weight {EQ:.2f}%",
                                annotation_font=dict(color="#C9A84C", size=10))
                fig_w.update_layout(
                    title=dict(text=f"Optimal Weights  ·  τ={tau:.3f}  ·  δ={risk:.1f}",
                               font=dict(family="Syne", size=14, color="#E8EAF0")),
                    showlegend=False, **PLOT_THEME
                )
                st.plotly_chart(fig_w, use_container_width=True)

                # Overweight table
                st.markdown("<h2>Allocation Breakdown</h2>", unsafe_allow_html=True)
                df_w["Explanation"] = df_w.apply(
                    lambda r: f"AI view {r['AI View']:.2%} vs equilibrium {r['Equilibrium']:.2%} → posterior {r['Posterior']:.2%}",
                    axis=1
                )
                st.dataframe(df_w[["Ticker","Weight %","vs_eq","Status","Explanation"]], use_container_width=True)

                # τ Sensitivity
                with st.expander("τ Sensitivity — how weights change with AI confidence"):
                    tau_vals = [0.01, 0.025, 0.05, 0.075, 0.10]
                    sens = []
                    prog = st.progress(0)
                    for i, t in enumerate(tau_vals):
                        r = get_portfolio_data(t, risk, sel_date)
                        if r:
                            for tick, w in zip(r["tickers"], r["weights_percent"]):
                                sens.append({"τ": t, "Ticker": tick, "Weight %": round(w, 3)})
                        prog.progress((i+1)/len(tau_vals))
                    if sens:
                        sf = pd.DataFrame(sens)
                        fig_s = px.line(sf, x="τ", y="Weight %", color="Ticker",
                                        title="Portfolio Weights vs AI Confidence (τ)")
                        fig_s.add_hline(y=EQ, line_dash="dot", line_color="#C9A84C",
                                        annotation_text="Equal weight")
                        fig_s.update_layout(**PLOT_THEME)
                        st.plotly_chart(fig_s, use_container_width=True)
                        st.caption("Steeper lines = stocks where AI views diverge more from market equilibrium.")

                # BL math
                with st.expander("Black-Litterman formula"):
                    st.latex(r"E[R] = \left[(\tau\Sigma)^{-1} + P^\top\Omega^{-1}P\right]^{-1}\left[(\tau\Sigma)^{-1}\Pi + P^\top\Omega^{-1}Q\right]")
                    st.markdown("""
                    <div style='font-family:var(--font-mono);font-size:0.72rem;color:#8A95A3;line-height:2'>
                    Π &nbsp;= market equilibrium returns (CAPM reverse-optimisation)<br>
                    Q &nbsp;= CNN-LSTM return forecasts (AI views)<br>
                    Σ &nbsp;= historical covariance matrix<br>
                    Ω &nbsp;= diagonal view uncertainty (validation forecast errors)<br>
                    τ &nbsp;= confidence scalar (your slider above)<br>
                    P &nbsp;= identity matrix (absolute views, one per asset)
                    </div>
                    """, unsafe_allow_html=True)

            with right:
                st.markdown("<h2>Metrics</h2>", unsafe_allow_html=True)
                st.metric("Expected Return", f"{data['portfolio_return']:.4%}")
                st.metric("Daily Volatility",  f"{data['portfolio_volatility']:.4%}")
                st.metric("Sharpe Ratio",       f"{data['sharpe_ratio']:.2f}")

                st.markdown("---")
                st.markdown("<h2>Backtest</h2>", unsafe_allow_html=True)
                st.metric("AI-BL Final Wealth",    "25.84 ZiG", "+20.4% vs EW")
                st.metric("Equal-Weight Wealth",   "21.47 ZiG")
                st.metric("Market-Cap Wealth",     "0.0003 ZiG", "-99.99%")

                st.markdown("---")
                st.markdown("<h2>USD Preservation</h2>", unsafe_allow_html=True)
                inv = st.number_input("Initial USD", min_value=100, max_value=100000, value=1000, step=100)
                st.markdown(f"""
                <div style='margin-top:0.8rem'>
                    <div style='font-family:var(--font-mono);font-size:0.65rem;color:#4E5968;margin-bottom:0.3rem'>AI-BL</div>
                    <div style='font-family:Syne,sans-serif;font-size:1.4rem;font-weight:800;color:#3DBA7F'>${inv*0.766:,.2f}</div>
                    <div style='font-size:0.72rem;color:#8A95A3;margin-bottom:0.8rem'>76.6% preserved</div>
                    <div style='font-family:var(--font-mono);font-size:0.65rem;color:#4E5968;margin-bottom:0.3rem'>Equal-Weight</div>
                    <div style='font-family:Syne,sans-serif;font-size:1.4rem;font-weight:800;color:#C9A84C'>${inv*0.636:,.2f}</div>
                    <div style='font-size:0.72rem;color:#8A95A3;margin-bottom:0.8rem'>63.6% preserved</div>
                    <div style='font-family:var(--font-mono);font-size:0.65rem;color:#4E5968;margin-bottom:0.3rem'>Market-Cap</div>
                    <div style='font-family:Syne,sans-serif;font-size:1.4rem;font-weight:800;color:#E05252'>${inv*0.000009:,.4f}</div>
                    <div style='font-size:0.72rem;color:#8A95A3'>0.0009% preserved</div>
                </div>
                """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE 3  —  STOCK ANALYSIS
# ─────────────────────────────────────────────
elif page == "Stock Analysis":

    st.markdown("""
    <div class='page-header'>
        <h1>Stock Analysis</h1>
        <span class='page-tag'>Fundamentals · AI Signals · Forecasts</span>
    </div>
    """, unsafe_allow_html=True)

    if news_df.empty:
        st.warning("No news data loaded.")
        st.stop()

    col_sel1, col_sel2 = st.columns(2)
    selected_ticker = col_sel1.selectbox("Stock", sorted(news_df["ticker"].unique()))
    all_dates        = sorted(news_df["date"].unique())
    selected_date    = col_sel2.selectbox("Date", all_dates)

    # Fundamentals
    st.markdown("<h2>Fundamentals</h2>", unsafe_allow_html=True)
    if fund_df is not None and not fund_df.empty:
        fund = fund_df[fund_df["ticker"] == selected_ticker]
        if not fund.empty:
            f = fund.iloc[0]
            cols = st.columns(6)
            fields = [("P/B","P/B"),("ROE","ROE"),("Net Margin","Net Margin"),
                      ("Dividend Yield","Dividend Yield"),("Market Cap (ZiG mn)","Market Cap (ZiG mn)"),("P/E","P/E")]
            for col, (label, key) in zip(cols, fields):
                val = f.get(key, "N/A")
                if isinstance(val, float):
                    if key in ("ROE","Net Margin","Dividend Yield"):
                        val = f"{val:.1%}"
                    else:
                        val = f"{val:,.2f}"
                col.metric(label, val)
        else:
            st.info("No fundamentals for this ticker.")

    # AI Signals
    st.markdown("<h2>AI Signals</h2>", unsafe_allow_html=True)
    news_s = news_df[(news_df["ticker"] == selected_ticker) & (news_df["date"] == selected_date)]
    sent_score = news_s["sentiment_score"].iloc[0] if not news_s.empty else None
    sent_label = news_s["sentiment_label"].iloc[0]  if not news_s.empty else "N/A"

    fc = pd.DataFrame()
    if forecast_df is not None and not forecast_df.empty:
        fc = forecast_df[(forecast_df["ticker"] == selected_ticker) & (forecast_df["date"] == selected_date)]
    ai_view = fc["predicted_return"].iloc[0] if not fc.empty else None

    api_d = get_portfolio_data(0.025, 2.5, selected_date.strftime("%Y-%m-%d"))
    ai_bl_w = vs_eq = None
    if api_d:
        try:
            idx     = api_d["tickers"].index(selected_ticker)
            ai_bl_w = api_d["weights_percent"][idx]
            vs_eq   = ai_bl_w - 100 / len(api_d["tickers"])
        except ValueError:
            pass

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sentiment Score", f"{sent_score:.3f}" if sent_score is not None else "N/A", sent_label)
    c2.metric("AI View (CNN-LSTM)", f"{ai_view:.2%}" if ai_view else "N/A")
    c3.metric("AI-BL Weight",   f"{ai_bl_w:.2f}%" if ai_bl_w else "N/A")
    c4.metric("vs Equal Weight", f"{vs_eq:+.2f}%" if vs_eq is not None else "N/A")

    # Price & Sentiment
    st.markdown("<h2>Price & Sentiment</h2>", unsafe_allow_html=True)
    if prices_long is not None and not prices_long.empty:
        sp = prices_long[prices_long["ticker"] == selected_ticker]
        ss = news_df[news_df["ticker"]   == selected_ticker]
        if not sp.empty and not ss.empty:
            fig_ps = go.Figure()
            fig_ps.add_trace(go.Scatter(x=sp["Date"], y=sp["price"],
                                        name="Price", line=dict(color="#C9A84C", width=1.5)))
            fig_ps.add_trace(go.Scatter(x=ss["date"], y=ss["sentiment_score"],
                                        name="Sentiment", yaxis="y2",
                                        line=dict(color="#4A9EE8", width=1, dash="dot")))
            fig_ps.update_layout(
                title=dict(text=f"{selected_ticker} — Price vs Sentiment",
                           font=dict(family="Syne", size=14, color="#E8EAF0")),
                yaxis =dict(title="Price (ZiG)"),
                yaxis2=dict(title="Sentiment", overlaying="y", side="right", range=[-1, 1]),
                **PLOT_THEME
            )
            st.plotly_chart(fig_ps, use_container_width=True)

    # Forecast vs Actual
    st.markdown("<h2>CNN-LSTM Forecast vs Actual</h2>", unsafe_allow_html=True)
    if forecast_df is not None and not forecast_df.empty:
        sf = forecast_df[forecast_df["ticker"] == selected_ticker]
        if not sf.empty:
            fig_f = go.Figure()
            fig_f.add_trace(go.Scatter(x=sf["date"], y=sf["predicted_return"],
                                       name="Predicted", line=dict(color="#C9A84C", width=1.5)))
            fig_f.add_trace(go.Scatter(x=sf["date"], y=sf["actual_return"],
                                       name="Actual", line=dict(color="#4A9EE8", width=1)))
            fig_f.update_layout(
                title=dict(text="Forecast vs Actual Returns",
                           font=dict(family="Syne", size=14, color="#E8EAF0")),
                **PLOT_THEME
            )
            st.plotly_chart(fig_f, use_container_width=True)
            st.caption("Directional accuracy: 34.47% — typical for highly volatile frontier markets.")


# ─────────────────────────────────────────────
#  PAGE 4  —  LIVE NEWS
# ─────────────────────────────────────────────
elif page == "Live News":

    st.markdown("""
    <div class='page-header'>
        <h1>Live News Feed</h1>
        <span class='page-tag'>RSS · Filtered for 9 Holdings</span>
    </div>
    """, unsafe_allow_html=True)

    rss_url = st.text_input("RSS feed URL", value="https://www.herald.co.zw/feed/")

    if st.button("Fetch News"):
        with st.spinner("Fetching…"):
            entries = fetch_rss_feed(rss_url)

        if entries:
            st.markdown(f"<div class='badge badge-gold'>{len(entries)} relevant articles found</div><br><br>", unsafe_allow_html=True)
            for e in entries:
                st.markdown(f"""
                <div class='news-item'>
                    <div class='news-headline'><a href='{e["link"]}' style='color:#E8EAF0;text-decoration:none'>{e["title"]}</a></div>
                    <div class='news-meta'>{e["published"]}</div>
                    <div class='news-body'>{e["summary"]}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No relevant articles found for the 9 holdings. The feed may not contain recent ZSE news.")

    st.markdown("---")
    st.markdown("""
    <div style='font-family:var(--font-mono);font-size:0.72rem;color:#4E5968;line-height:1.8'>
    Filtered keywords: AFDIS · African Distillers · BAT · British American Tobacco ·
    CAFCA · CBZ · Delta · Dairibord · Econet · OK Zimbabwe · Seed Co
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  PAGE 5  —  USER GUIDE
# ─────────────────────────────────────────────
elif page == "User Guide":

    st.markdown("""
    <div class='page-header'>
        <h1>User Guide</h1>
        <span class='page-tag'>How to use this system</span>
    </div>
    """, unsafe_allow_html=True)

    pages_guide = [
        ("Market Intelligence", "DA-BERT Sentiment",
         "Upload a news CSV or use the default dataset. Select a trading date to see sentiment scores per stock, the market-wide sentiment trend, and individual news articles with their DA-BERT labels and scores. The change table compares today's sentiment to the previous news date."),
        ("Portfolio Optimizer", "Black-Litterman · Live API",
         "Adjust τ (AI confidence: 0.01 = near-market-equilibrium, 0.10 = high AI trust) and δ (risk aversion). Click Run Optimization to call the live backend API. Optimal weights are returned, explained, and visualised. The τ Sensitivity panel shows how weights shift across the full τ range, proving the system is genuinely dynamic."),
        ("Stock Analysis", "Fundamentals · AI Signals",
         "Select a stock and date. See fundamentals (P/B, ROE, Net Margin, Dividend Yield, Market Cap, P/E), AI signals (sentiment score, CNN-LSTM predicted return, AI-BL weight vs equal weight), and two charts: price vs sentiment over time, and CNN-LSTM forecast vs actual returns."),
        ("Live News", "RSS · Filtered",
         "Enter any RSS feed URL (default: The Herald). The system filters articles to only show those mentioning the 9 portfolio companies by ticker or company name. This demonstrates the news pipeline that feeds the DA-BERT sentiment model."),
        ("Upload Your Data", "CSV Override",
         "On the Market Intelligence page, upload your own news CSV. The system immediately adapts — all sentiment charts, trend lines, and news panels update to reflect your data. Required columns: date, ticker, headline, content, sentiment_score, sentiment_label, source, confidence."),
    ]

    for title, tag, desc in pages_guide:
        st.markdown(f"""
        <div class='card-gold' style='margin-bottom:1rem'>
            <div style='display:flex;align-items:center;gap:10px;margin-bottom:0.6rem'>
                <span style='font-family:Syne,sans-serif;font-size:1rem;font-weight:700;color:#E8EAF0'>{title}</span>
                <span class='badge badge-gold'>{tag}</span>
            </div>
            <p style='font-size:0.82rem;color:#8A95A3;line-height:1.7;margin:0'>{desc}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='font-family:var(--font-mono);font-size:0.65rem;color:#4E5968;line-height:2'>
    DA-BERT fine-tuned on 8,465 Zimbabwean news articles · accuracy 81.4% · F1 0.79<br>
    CNN-LSTM directional accuracy 34.47% (frontier market baseline) · MAE 5.88%<br>
    Black-Litterman posterior: τΣ prior + Ω view uncertainty · long-only constraint · max Sharpe<br>
    Backend deployed on Render · FastAPI · data sources: ZSE, The Herald, NewsDay, Zimbabwe Independent
    </div>
    """, unsafe_allow_html=True)