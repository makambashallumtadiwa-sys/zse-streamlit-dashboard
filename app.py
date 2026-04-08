import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import feedparser
from datetime import datetime
import re
import os  # Add this line

st.set_page_config(page_title="ZSE PORTFOLIO OPTIMIZER", layout="wide")

# ---------------------------
# Custom CSS with your color palette
# ---------------------------
st.markdown("""
<style>
    :root {
        --ice-gray: #F0F4F8;
        --heather: #B8C2D0;
        --greyish: #A8B2C0;
        --fossil: #8E9AAB;
        --trout: #6C7A8E;
        --iron: #4E5B6E;
        --abalone: #D9E0E8;
        --thunder: #3A4556;
        --mink: #5D6A7A;
    }
    body, .stApp {
        background-color: var(--ice-gray);
    }
    .main-header {
        color: var(--thunder);
        font-size: 2.8rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .logo {
        font-size: 4rem;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .tagline {
        color: var(--trout);
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    .card {
        background-color: white;
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 1.2rem;
        border-left: 4px solid var(--iron);
    }
    .metric-card {
        background-color: var(--abalone);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    .explanation-card {
        background-color: white;
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1rem;
        border: 1px solid var(--heather);
    }
    .stButton>button {
        background-color: var(--iron);
        color: white;
        border-radius: 8px;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: var(--thunder);
    }
    hr {
        margin: 1rem 0;
        border-color: var(--heather);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Helper functions
# ---------------------------
@st.cache_data
def load_csv(file, parse_dates=None):
    try:
        return pd.read_csv(file, parse_dates=parse_dates)
    except FileNotFoundError:
        st.warning(f"File not found: {file}")
        return pd.DataFrame()

def wide_to_long(df, id_vars='Date', value_name='price'):
    if df.empty:
        return df
    return df.melt(id_vars=id_vars, var_name='ticker', value_name=value_name)

def fetch_rss_feed(url):
    """Fetch RSS feed, keep only articles from 2025+ and about the 9 companies."""
    try:
        feed = feedparser.parse(url)
        entries = []
        keywords = [
            'AFDIS', 'African Distillers', 'BAT', 'British American Tobacco', 'CAFCA', 'Cafca',
            'CBZ', 'CBZ Holdings', 'DLTA', 'Delta', 'DZL', 'Dairibord', 'ECO', 'Econet',
            'OKZ', 'OK Zimbabwe', 'SEED', 'Seed Co'
        ]
        for entry in feed.entries[:40]:
            pub_date = entry.get('published', '')
            year = 0
            try:
                dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z')
                year = dt.year
            except:
                match = re.search(r'(\d{4})', pub_date)
                year = int(match.group(1)) if match else 0
            if year < 2025:
                continue
            title = entry.title.lower()
            summary = entry.get('summary', '').lower()
            if any(keyword.lower() in title or keyword.lower() in summary for keyword in keywords):
                entries.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': pub_date,
                    'summary': entry.get('summary', '')[:350] + '...' if len(entry.get('summary', '')) > 350 else entry.get('summary', '')
                })
        return entries
    except Exception as e:
        st.error(f"RSS feed error: {e}")
        return []

# ---------------------------
# Load default data
# ---------------------------
@st.cache_data
def load_default_data():
    news_df = load_csv("news_sentiment_clean.csv", parse_dates=['date'])
    prices_wide = load_csv("prices_9stocks.csv", parse_dates=['Date'])
    prices_long = wide_to_long(prices_wide) if not prices_wide.empty else pd.DataFrame()
    fund_df = load_csv("fundamentals_9stocks.csv")
    if not fund_df.empty:
        fund_df.rename(columns={
            'pb_ratio': 'P/B', 'roi': 'ROE', 'net_margin': 'Net Margin',
            'div_yield': 'Dividend Yield', 'market_cap_zig_millions': 'Market Cap (ZiG mn)',
            'pe_ratio': 'P/E'
        }, inplace=True)
    forecast_df = load_csv("forecasts_9stocks.csv", parse_dates=['date'])
    return news_df, prices_long, fund_df, forecast_df

# Initialize session state
if 'news_df' not in st.session_state:
    news_df, prices_long, fund_df, forecast_df = load_default_data()
    st.session_state.news_df = news_df
    st.session_state.prices_long = prices_long
    st.session_state.fund_df = fund_df
    st.session_state.forecast_df = forecast_df
else:
    news_df = st.session_state.news_df
    prices_long = st.session_state.prices_long
    fund_df = st.session_state.fund_df
    forecast_df = st.session_state.forecast_df

API_URL = "https://zse-ai-backend.onrender.com/api/optimize"

def get_portfolio_data(tau, risk, date):
    payload = {"tau": tau, "risk_aversion": risk, "selected_date": date}
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return None

# ---------------------------
# Sidebar navigation (new order: Home, User Guide, then others)
# ---------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "🏠 Home",
    "📘 User Guide",
    "📊 Market Intelligence",
    "⚙️ Portfolio Optimizer",
    "📈 Stock Analysis",
    "📰 Live News Feed"
])

# ---------------------------
# Page 0: Home (Cover page with logo, name, user personas – NO RESULTS)
# ---------------------------
if page == "🏠 Home":
    st.markdown('<div class="logo">📈📊💰</div>', unsafe_allow_html=True)
    st.markdown('<div class="main-header">ZSE PORTFOLIO OPTIMIZER</div>', unsafe_allow_html=True)
    st.markdown('<div class="tagline">AI‑Driven Black‑Litterman Optimization for Zimbabwe Stock Exchange</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: var(--abalone); padding: 1rem; border-radius: 12px; margin-bottom: 2rem; text-align: center;">
        <p>Welcome to the AI‑powered portfolio optimization system. Use the sidebar to explore sentiment analysis,
        run portfolio optimisation, analyse individual stocks, and follow live news.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Who can benefit from this system?")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="card">
            <h3>📈 Investors</h3>
            <p>See how AI sentiment forecasts translate into portfolio recommendations. Understand which stocks are overweight or underweight and why.</p>
            <p><strong>➡️ Start on <em>Market Intelligence</em> to gauge overall sentiment, then go to <em>Portfolio Optimizer</em> for the AI‑BL weights.</strong></p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
            <h3>📊 Analysts</h3>
            <p>Drill into individual stocks: fundamentals, AI signals, price vs sentiment correlation, and forecast accuracy. Validate the CNN‑LSTM predictions.</p>
            <p><strong>➡️ Use <em>Stock Analysis</em> to explore any ticker in depth.</strong></p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="card">
            <h3>🏦 Portfolio Managers</h3>
            <p>Adjust τ (confidence in AI) and δ (risk aversion) to see how the optimal portfolio changes. The sensitivity analysis shows how weights shift with τ.</p>
            <p><strong>➡️ Go to <em>Portfolio Optimizer</em> and run the τ sensitivity chart.</strong></p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
            <h3>📰 Stockbrokers & Advisors</h3>
            <p>Stay ahead with live news feeds filtered for the 9 ZSE companies. Explain to clients why sentiment drives our recommendations.</p>
            <p><strong>➡️ Check <em>Live News Feed</em> for the latest updates from 2025 onwards.</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("📌 About the system"):
        st.markdown("""
        - **Sentiment**: Domain‑adapted BERT fine‑tuned on 8,465 Zimbabwean news articles (81.4% accuracy).  
        - **Forecasts**: CNN‑LSTM trained on historical prices and sentiment scores.  
        - **Optimisation**: Black‑Litterman Bayesian fusion (market equilibrium + AI views).  
        - **Backtest (2023‑2024)**: AI‑BL portfolio outperformed equal‑weight by 20.4% and preserved 76.6% of USD value during currency collapse.  
        - **Live backend**: API deployed on Render returns weights in real time.
        """)

# ---------------------------
# Page 1: User Guide (now second)
# ---------------------------
elif page == "📘 User Guide":
    st.header("User Guide")
    st.markdown("""
    <div class="card">
        <h3>📊 Market Intelligence</h3>
        <p>Select a date, view sentiment gauges, bar chart, sentiment change, and expand news articles. You can upload your own CSV to replace the news data.</p>
    </div>
    <div class="card">
        <h3>⚙️ Portfolio Optimizer</h3>
        <p>Adjust τ (AI confidence) and δ (risk aversion), then run optimization. The τ sensitivity chart shows how weights shift with AI confidence. The currency simulator shows wealth preservation during hyperinflation.</p>
    </div>
    <div class="card">
        <h3>📈 Stock Analysis</h3>
        <p>Select a stock and date to see fundamentals, AI signals, price vs sentiment chart, and forecast vs actual returns.</p>
    </div>
    <div class="card">
        <h3>📰 Live News Feed</h3>
        <p>Fetches RSS news, keeps only articles from 2025 onwards that mention any of the 9 companies. You can provide a custom RSS URL.</p>
    </div>
    <div class="card">
        <h3>💾 Upload Your Own Data</h3>
        <p>On the Market Intelligence page, upload a new news CSV. The dashboard will immediately use it for sentiment analysis.</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------
# Page 2: Market Intelligence (unchanged)
# ---------------------------
elif page == "📊 Market Intelligence":
    st.header("Market Intelligence")
    
    uploaded_file = st.file_uploader("Upload new news CSV (optional)", type=["csv"])
    if uploaded_file is not None:
        try:
            new_news = pd.read_csv(uploaded_file, parse_dates=['date'])
            st.session_state.news_df = new_news
            news_df = new_news
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Articles in uploaded data", len(new_news))
            with col2:
                st.metric("Date range", f"{new_news['date'].min().date()} to {new_news['date'].max().date()}")
            st.success("News data updated! All charts now reflect the new data.")
        except Exception as e:
            st.error(f"Error loading file: {e}")
    
    if news_df.empty:
        st.error("No news data available. Please upload a CSV file.")
        st.stop()
    
    all_dates = sorted(news_df["date"].unique())
    selected_date = st.selectbox("Select a date (only dates with news)", all_dates)
    daily_news = news_df[news_df["date"] == selected_date]
    
    if not daily_news.empty:
        avg_sentiment = daily_news["sentiment_score"].mean()
        max_sent = daily_news["sentiment_score"].max()
        min_sent = daily_news["sentiment_score"].min()
        sentiment_vol = (max_sent - min_sent) / 2
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Average Sentiment", f"{avg_sentiment:.3f}")
            norm = (avg_sentiment + 1) / 2
            st.progress(norm)
        with col2:
            st.metric("Sentiment Volatility", f"{sentiment_vol:.3f}")
        
        daily_avg_ticker = daily_news.groupby("ticker")["sentiment_score"].mean().reset_index()
        fig_bar = px.bar(daily_avg_ticker, x="ticker", y="sentiment_score", title="Sentiment by Stock")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("No sentiment data for selected date.")
    
    sentiment_over_time = news_df.groupby("date")["sentiment_score"].mean().reset_index()
    fig_line = px.line(sentiment_over_time, x="date", y="sentiment_score", title="Market Sentiment Trend")
    st.plotly_chart(fig_line, use_container_width=True)
    
    st.subheader("Sentiment Change (vs previous date with news)")
    prev_dates = [d for d in all_dates if d < selected_date]
    if prev_dates:
        prev_date = max(prev_dates)
        current_sent = news_df[news_df["date"] == selected_date].groupby("ticker")["sentiment_score"].mean().reset_index()
        prev_sent = news_df[news_df["date"] == prev_date].groupby("ticker")["sentiment_score"].mean().reset_index()
        merged = current_sent.merge(prev_sent, on="ticker", suffixes=("_current", "_prev"))
        merged["change"] = merged["sentiment_score_current"] - merged["sentiment_score_prev"]
        merged["trend"] = merged["change"].apply(
            lambda x: "▲ Strongly Improving" if x > 0.05 else ("▲ Improving" if x > 0 else ("▼ Strongly Declining" if x < -0.05 else ("▼ Declining" if x < 0 else "● Stable")))
        )
        st.dataframe(merged[["ticker", "sentiment_score_current", "sentiment_score_prev", "change", "trend"]])
    else:
        st.info("No previous date available for comparison.")
    
    st.subheader(f"News Articles on {selected_date.date()}")
    news_today = news_df[news_df["date"] == selected_date]
    if not news_today.empty:
        for _, row in news_today.iterrows():
            with st.expander(f"{row['headline']} ({row['source']})"):
                st.write(row["content"])
                st.caption(f"Sentiment: {row.get('sentiment_label', 'N/A')} | Score: {row.get('sentiment_score', 'N/A'):.3f} | Confidence: {row.get('confidence', 'N/A')}")
    else:
        st.info("No news articles for this date.")

# ---------------------------
# Page 3: Portfolio Optimizer (unchanged, but ensure no accidental results on Home)
# ---------------------------
elif page == "⚙️ Portfolio Optimizer":
    st.header("Portfolio Optimizer")
    
    if not forecast_df.empty:
        available_dates = sorted(forecast_df['date'].dt.strftime('%Y-%m-%d').unique())
        selected_date = st.selectbox(
            "Select optimization date", 
            available_dates,
            index=len(available_dates)//2 if available_dates else 0
        )
    else:
        selected_date = "2023-06-15"
        st.warning("Forecast data not available, using default date.")
    
    tau = st.sidebar.slider("τ (AI Confidence)", 0.01, 0.10, 0.025, 0.005)
    risk = st.sidebar.slider("δ (Risk Aversion)", 1.0, 5.0, 2.5, 0.1)
    
    if st.button("Run Optimization", type="primary"):
        with st.spinner("Calling Black‑Litterman API..."):
            data = get_portfolio_data(tau, risk, selected_date)
        
        if data:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("Portfolio Allocation")
                df_weights = pd.DataFrame({
                    "Ticker": data["tickers"],
                    "Weight %": data["weights_percent"],
                    "Posterior Return": data["posterior_returns"],
                    "AI View": data["ai_views"],
                    "Equilibrium Return": data["equilibrium_returns"]
                }).sort_values("Weight %", ascending=False)
                fig = px.bar(df_weights, x="Ticker", y="Weight %", title=f"Optimal Weights (τ={tau:.3f}, δ={risk:.1f})")
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
                st.subheader("Weights Table")
                st.dataframe(df_weights)
                
                st.subheader("📋 Explain a Stock's Weight")
                explain_ticker = st.selectbox("Select a ticker to see why it is overweight or underweight", df_weights["Ticker"].tolist())
                if explain_ticker:
                    row = df_weights[df_weights["Ticker"] == explain_ticker].iloc[0]
                    eq_weight_pct = 100 / len(df_weights)
                    diff = row["Weight %"] - eq_weight_pct
                    status = "OVERWEIGHT" if diff > 0 else "UNDERWEIGHT"
                    st.markdown(f"""
                    <div class="explanation-card">
                        <strong>{explain_ticker}</strong><br>
                        Weight: {row['Weight %']:.2f}% (Benchmark: {eq_weight_pct:.2f}%)<br>
                        AI View: {row['AI View']:.2%}<br>
                        Equilibrium Return: {row['Equilibrium Return']:.2%}<br>
                        Posterior Return: {row['Posterior Return']:.2%}<br>
                        <span style="color: {'green' if diff>0 else 'red'}">{status} by {abs(diff):.2f}%</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.subheader("τ Sensitivity Analysis")
                st.caption("How portfolio weights change as AI confidence (τ) increases")
                if st.button("Run Sensitivity Analysis", key="sens_btn"):
                    tau_values = [0.01, 0.025, 0.05, 0.075, 0.10]
                    sensitivity_results = []
                    progress = st.progress(0)
                    for i, t in enumerate(tau_values):
                        res = get_portfolio_data(t, risk, selected_date)
                        if res:
                            for ticker, w in zip(res['tickers'], res['weights_percent']):
                                sensitivity_results.append({'tau': t, 'ticker': ticker, 'weight': w})
                        progress.progress((i+1)/len(tau_values))
                    if sensitivity_results:
                        sens_df = pd.DataFrame(sensitivity_results)
                        fig_sens = px.line(sens_df, x='tau', y='weight', color='ticker', markers=True,
                                           title='Portfolio Weights vs AI Confidence (τ)',
                                           labels={'tau': 'AI Confidence (τ)', 'weight': 'Weight (%)'})
                        eq_weight_pct = 100 / len(df_weights)
                        fig_sens.add_hline(y=eq_weight_pct, line_dash="dash", line_color="gray",
                                           annotation_text=f"Equal Weight ({eq_weight_pct:.2f}%)")
                        fig_sens.update_layout(xaxis_tickformat='.3f')
                        st.plotly_chart(fig_sens, use_container_width=True)
                        st.caption("As τ increases, the portfolio tilts more toward AI views and away from market equilibrium.")
                
                st.subheader("Currency Crisis Wealth Simulator")
                st.caption("Simulate how different portfolios preserve wealth during currency devaluation")
                initial_usd = st.number_input("Initial Investment (USD)", min_value=100, max_value=100000, value=1000, step=100)
                colA, colB, colC = st.columns(3)
                with colA:
                    ai_bl_final = initial_usd * 0.766
                    st.markdown(f'<div class="metric-card"><h4>AI-BL Portfolio</h4><h2>${ai_bl_final:,.2f}</h2><p>76.6% preserved</p><p style="color:green">Best performer</p></div>', unsafe_allow_html=True)
                with colB:
                    eq_final = initial_usd * 0.636
                    st.markdown(f'<div class="metric-card"><h4>Equal-Weight Portfolio</h4><h2>${eq_final:,.2f}</h2><p>63.6% preserved</p><p style="color:orange">Moderate loss</p></div>', unsafe_allow_html=True)
                with colC:
                    mkt_final = initial_usd * 0.000009
                    st.markdown(f'<div class="metric-card"><h4>Market-Cap Portfolio</h4><h2>${mkt_final:,.4f}</h2><p>0.0009% preserved</p><p style="color:red">Near total loss</p></div>', unsafe_allow_html=True)
            
            with col2:
                st.subheader("Portfolio Metrics")
                st.metric("Expected Daily Return", f"{data['portfolio_return']:.4%}")
                st.metric("Daily Volatility", f"{data['portfolio_volatility']:.4%}")
                st.metric("Sharpe Ratio", f"{data['sharpe_ratio']:.2f}")
    
    with st.expander("🔍 How the Black-Litterman model works here"):
        st.markdown("""
        **Step 1 – Market Equilibrium Prior (Π)**  
        The model starts from market-cap weights as the collective market wisdom.
        
        **Step 2 – AI Views (Q)**  
        CNN-LSTM forecasts (trained on DA-BERT sentiment and prices) become the views.
        
        **Step 3 – Bayesian Fusion**  
        τ controls the weight given to AI views: low τ stays close to market, high τ tilts toward AI.
        
        **Step 4 – Optimization**  
        Posterior returns are fed into a mean-variance optimizer (long-only, max Sharpe ratio).
        """)
        st.latex(r"E[R] = \left[(\tau\Sigma)^{-1} + P^\top\Omega^{-1}P\right]^{-1}\left[(\tau\Sigma)^{-1}\Pi + P^\top\Omega^{-1}Q\right]")

# ---------------------------
# Page 4: Stock Analysis (unchanged)
# ---------------------------
elif page == "📈 Stock Analysis":
    st.header("Stock Analysis")
    if news_df.empty:
        st.error("No news data available.")
        st.stop()
    all_tickers = sorted(news_df["ticker"].unique())
    selected_ticker = st.selectbox("Select Stock", all_tickers)
    all_dates = sorted(news_df["date"].unique())
    selected_date = st.selectbox("Select Date", all_dates)
    
    st.subheader("Fundamentals")
    if fund_df is not None and not fund_df.empty:
        fund = fund_df[fund_df["ticker"] == selected_ticker]
        if not fund.empty:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("P/B Ratio", f"{fund['P/B'].values[0]:.2f}" if 'P/B' in fund else "N/A")
                st.metric("ROE", f"{fund['ROE'].values[0]:.1%}" if 'ROE' in fund else "N/A")
            with col2:
                st.metric("Net Margin", f"{fund['Net Margin'].values[0]:.1%}" if 'Net Margin' in fund else "N/A")
                st.metric("Dividend Yield", f"{fund['Dividend Yield'].values[0]:.1%}" if 'Dividend Yield' in fund else "N/A")
            with col3:
                st.metric("Market Cap (ZiG mn)", f"{fund['Market Cap (ZiG mn)'].values[0]:,.0f}" if 'Market Cap (ZiG mn)' in fund else "N/A")
            with col4:
                st.metric("P/E Ratio", f"{fund['P/E'].values[0]:.2f}" if 'P/E' in fund else "N/A")
        else:
            st.info("No fundamentals for this ticker.")
    else:
        st.info("Fundamentals file not loaded.")
    
    st.subheader("AI Signals")
    news_sent = news_df[(news_df["ticker"] == selected_ticker) & (news_df["date"] == selected_date)]
    sentiment_score = news_sent["sentiment_score"].iloc[0] if not news_sent.empty else None
    sentiment_label = news_sent["sentiment_label"].iloc[0] if not news_sent.empty else "N/A"
    if forecast_df is not None and not forecast_df.empty:
        forecast = forecast_df[(forecast_df["ticker"] == selected_ticker) & (forecast_df["date"] == selected_date)]
        ai_view = forecast["predicted_return"].iloc[0] if not forecast.empty else None
    else:
        ai_view = None
    api_data = get_portfolio_data(0.025, 2.5, selected_date.strftime("%Y-%m-%d"))
    if api_data:
        try:
            idx = api_data["tickers"].index(selected_ticker)
            ai_bl_weight = api_data["weights_percent"][idx]
            eq_weight = 100 / len(api_data["tickers"])
            vs_eq = ai_bl_weight - eq_weight
        except ValueError:
            ai_bl_weight = None
            vs_eq = None
    else:
        ai_bl_weight = None
        vs_eq = None
    
    colA, colB, colC = st.columns(3)
    with colA:
        st.metric("Sentiment Score", f"{sentiment_score:.3f}" if sentiment_score is not None else "N/A")
        st.caption(f"Label: {sentiment_label}")
    with colB:
        st.metric("AI View (Predicted Return)", f"{ai_view:.2%}" if ai_view else "N/A")
    with colC:
        if ai_bl_weight is not None:
            st.metric("AI-BL Weight", f"{ai_bl_weight:.2f}%")
            st.metric("vs Equal Weight", f"{vs_eq:+.2f}%")
        else:
            st.metric("AI-BL Weight", "N/A")
    
    st.subheader("Price & Sentiment Over Time")
    if prices_long is not None and not prices_long.empty:
        stock_prices = prices_long[prices_long["ticker"] == selected_ticker].copy()
        stock_sentiment = news_df[news_df["ticker"] == selected_ticker].copy()
        if not stock_prices.empty and not stock_sentiment.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=stock_prices["Date"], y=stock_prices["price"], name="Price", yaxis="y1"))
            fig.add_trace(go.Scatter(x=stock_sentiment["date"], y=stock_sentiment["sentiment_score"], name="Sentiment", yaxis="y2"))
            fig.update_layout(
                title="Price and Sentiment",
                yaxis=dict(title="Price (ZiG)", side="left"),
                yaxis2=dict(title="Sentiment", overlaying="y", side="right", range=[-1,1])
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Insufficient price or sentiment data for this ticker.")
    else:
        st.warning("Price data not available.")
    
    st.subheader("AI Forecast vs Actual Returns")
    if forecast_df is not None and not forecast_df.empty:
        stock_forecasts = forecast_df[forecast_df["ticker"] == selected_ticker].copy()
        if not stock_forecasts.empty:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=stock_forecasts["date"], y=stock_forecasts["predicted_return"], name="Predicted", mode="lines+markers"))
            fig2.add_trace(go.Scatter(x=stock_forecasts["date"], y=stock_forecasts["actual_return"], name="Actual", mode="lines+markers"))
            fig2.update_layout(title="Forecast vs Actual Returns", xaxis_title="Date", yaxis_title="Return")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No forecast data for this ticker.")
    else:
        st.info("Forecast file not loaded.")

# ---------------------------
# Page 5: Live News Feed (unchanged)
# ---------------------------
elif page == "📰 Live News Feed":
    st.header("Live News Feed")
    st.markdown("Latest financial news from Zimbabwe, **filtered for the 9 companies** and **only articles from 2025 onwards**.")
    
    rss_url = "https://www.herald.co.zw/feed/"
    with st.spinner("Fetching latest news..."):
        entries = fetch_rss_feed(rss_url)
    
    if entries:
        for entry in entries:
            with st.container():
                st.markdown(f"### [{entry['title']}]({entry['link']})")
                st.caption(f"Published: {entry['published']}")
                st.write(entry['summary'])
                st.divider()
    else:
        st.warning("No relevant news from 2025 onwards found for the 9 companies. Try another RSS feed.")
    
    st.subheader("Custom RSS Feed")
    custom_url = st.text_input("Enter a custom RSS feed URL", value="https://www.herald.co.zw/feed/")
    if st.button("Fetch Custom Feed"):
        with st.spinner("Fetching..."):
            custom_entries = fetch_rss_feed(custom_url)
            if custom_entries:
                for entry in custom_entries:
                    st.markdown(f"### [{entry['title']}]({entry['link']})")
                    st.caption(f"Published: {entry['published']}")
                    st.write(entry['summary'])
                    st.divider()
            else:
                st.error("No relevant entries from 2025 onwards found.")


# At the very end of the file, add these lines
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8501))
    st.run(port=port)