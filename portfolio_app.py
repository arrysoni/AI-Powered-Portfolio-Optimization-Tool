import streamlit as st
import yfinance as yf
import requests
import matplotlib.pyplot as plt
import pandas as pd
from pypfopt import EfficientFrontier, expected_returns, risk_models

# ✅ Your Finnhub API key
# Replace with your real one
FINNHUB_API_KEY = "d0ma9c1r01qkesvji180d0ma9c1r01qkesvji18g"

# ✅ Search function (only keep tickers with no dot — i.e., US tickers like TSLA, AAPL)


def search_symbols(query):
    url = f"https://finnhub.io/api/v1/search?q={query}&token={FINNHUB_API_KEY}"
    res = requests.get(url)
    results = res.json().get("result", [])
    return [r["symbol"] for r in results if r["type"] == "Common Stock" and "." not in r["symbol"]]


# ✅ UI
st.title("📈 AI-Powered Portfolio Optimizer")

# Set up session state to remember selected tickers
if "selected_tickers" not in st.session_state:
    st.session_state.selected_tickers = []

search_term = st.text_input("Type a company name or ticker symbol:")

if search_term:
    matches = search_symbols(search_term)
    selected_now = st.multiselect(
        "Select stocks to include from search:", matches)
    if st.button("➕ Add to Portfolio"):
        for ticker in selected_now:
            if ticker not in st.session_state.selected_tickers:
                st.session_state.selected_tickers.append(ticker)

# Display selected tickers
if st.session_state.selected_tickers:
    st.success(
        f"📊 Current selection: {', '.join(st.session_state.selected_tickers)}")
    if st.button("🔁 Clear Selection"):
        st.session_state.selected_tickers = []

tickers = st.session_state.selected_tickers


# ✅ When tickers are selected, fetch and process data
if tickers:
    st.success(f"Fetching price data for: {', '.join(tickers)}")

    raw_data = yf.download(tickers, start="2020-01-01")

    # Check if data is valid
    if raw_data.empty:
        st.error("⚠️ No data returned from yfinance. Please try different tickers.")
        st.stop()

    # Handle single vs multi ticker
    if isinstance(raw_data.columns, pd.MultiIndex):
        data = raw_data["Close"]
    else:
        data = raw_data[["Close"]]
        data.columns = tickers

    st.subheader("📉 Historical Prices")
    st.line_chart(data)

    st.subheader("📊 Optimized Portfolio")
    mu = expected_returns.mean_historical_return(data)
    S = risk_models.sample_cov(data)
    ef = EfficientFrontier(mu, S)
    weights = ef.max_sharpe()
    cleaned_weights = ef.clean_weights()
    st.write("Recommended Allocation:", cleaned_weights)

    # 🥧 Pie chart
    non_zero_alloc = {k: v for k, v in cleaned_weights.items() if v > 0}
    fig, ax = plt.subplots()
    ax.pie(non_zero_alloc.values(),
           labels=non_zero_alloc.keys(), autopct="%1.1f%%")
    ax.axis("equal")
    st.pyplot(fig)

    # 💵 Investment breakdown
    st.subheader("💵 Investment Breakdown")
    total = st.number_input("Total amount to invest:",
                            min_value=0.0, value=100000.0, step=1000.0)
    breakdown = {k: round(v * total, 2) for k, v in non_zero_alloc.items()}
    st.table(breakdown)

    # 📈 Portfolio metrics
    st.subheader("📈 Portfolio Metrics")
    perf = ef.portfolio_performance()
    st.metric("Expected Annual Return", f"{perf[0]*100:.2f}%")
    st.metric("Annual Volatility", f"{perf[1]*100:.2f}%")
    st.metric("Sharpe Ratio", f"{perf[2]:.2f}")
