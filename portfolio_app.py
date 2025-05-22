import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import date
from pypfopt import EfficientFrontier, risk_models, expected_returns
from fpdf import FPDF
import tempfile
import os

st.set_page_config(page_title="AI-Powered Portfolio Optimization Tool")
st.title("📈 AI-Powered Portfolio Optimization Tool")

# --- User input for tickers ---
st.sidebar.header("🧠 Customize Your Portfolio")
user_input = st.sidebar.text_input(
    "Enter stock tickers (comma-separated)", value="AAPL, MSFT, TSLA")
tickers = [ticker.strip().upper()
           for ticker in user_input.split(",") if ticker.strip()]

if not tickers:
    st.warning("Please enter at least one valid stock ticker.")
    st.stop()

# --- Custom date range selection ---
st.sidebar.subheader("📆 Select Date Range")
start_date = st.sidebar.date_input("Start Date", date(2023, 6, 1))
end_date = st.sidebar.date_input("End Date", date(2024, 6, 1))

if start_date >= end_date:
    st.warning("⚠️ End date must be after start date.")
    st.stop()

# --- Max weight slider ---
st.sidebar.subheader("🎯 Risk Control")
max_weight = st.sidebar.slider(
    "Max weight per stock", 0.2, 1.0, 0.6, step=0.05)

api_key = os.getenv("POLYGON_API_KEY")
price_data = pd.DataFrame()


@st.cache_data(ttl=3600)
def get_historical_data(ticker, start_date, end_date):
    start = pd.to_datetime(start_date).strftime("%Y-%m-%d")
    end = pd.to_datetime(end_date).strftime("%Y-%m-%d")
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start}/{end}?adjusted=true&sort=asc&limit=5000&apiKey={api_key}"
    response = requests.get(url)
    data = response.json()
    if "results" in data:
        df = pd.DataFrame(data["results"])
        df["date"] = pd.to_datetime(df["t"], unit="ms")
        df.set_index("date", inplace=True)
        return df[["c"]].rename(columns={"c": ticker})
    else:
        st.warning(f"⚠️ No data for {ticker}: {data}")
        return None


# --- Fetch data ---
with st.spinner("Fetching stock data..."):
    for ticker in tickers:
        st.write(f"📡 Fetching: `{ticker}`")
        df = get_historical_data(ticker, start_date, end_date)
        if df is not None:
            price_data = pd.concat([price_data, df], axis=1)
        time.sleep(15)

price_data.dropna(how="any", inplace=True)

if not price_data.empty:
    st.subheader("📊 Adjusted Close Prices")
    st.dataframe(price_data.head())

    fig, ax = plt.subplots(figsize=(12, 6))
    for ticker in price_data.columns:
        ax.plot(price_data.index, price_data[ticker], label=ticker)
    ax.set_title("Adjusted Close Prices Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD)")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # --- Portfolio Optimization ---
    st.subheader("📌 Optimized Portfolio Allocation (Max Sharpe Ratio)")
    returns = price_data.pct_change().dropna()
    mu = expected_returns.mean_historical_return(price_data)
    S = risk_models.sample_cov(price_data)

    ef = EfficientFrontier(mu, S, weight_bounds=(0.05, max_weight))
    weights = ef.max_sharpe()
    cleaned_weights = ef.clean_weights()

    st.write("### 💼 Suggested Weights")
    st.json(cleaned_weights)

    # --- Pie Chart ---
    non_zero_weights = {k: v for k, v in cleaned_weights.items() if v > 0}
    fig2, ax2 = plt.subplots()
    ax2.pie(non_zero_weights.values(),
            labels=non_zero_weights.keys(), autopct='%1.1f%%')
    ax2.axis("equal")
    st.pyplot(fig2)

    # --- Portfolio Performance ---
    expected_return, volatility, sharpe = ef.portfolio_performance()
    st.write("### 📈 Portfolio Performance")
    st.metric("Expected Annual Return", f"{expected_return*100:.2f}%")
    st.metric("Annual Volatility", f"{volatility*100:.2f}%")
    st.metric("Sharpe Ratio", f"{sharpe:.2f}")

    # --- CSV Download ---
    weights_df = pd.DataFrame.from_dict(
        cleaned_weights, orient="index", columns=["Weight"])
    weights_df["Weight"] = (weights_df["Weight"] * 100).round(2)
    weights_df.index.name = "Ticker"

    perf_df = pd.DataFrame({
        "Expected Annual Return (%)": [round(expected_return * 100, 2)],
        "Annual Volatility (%)": [round(volatility * 100, 2)],
        "Sharpe Ratio": [round(sharpe, 2)]
    })

    csv_data = pd.concat([weights_df, perf_df.T])
    csv = csv_data.to_csv().encode('utf-8')
    st.download_button("📥 Download Portfolio CSV", data=csv,
                       file_name="portfolio_summary.csv", mime="text/csv")

    # --- Equal-Weighted Comparison ---
    st.subheader("🆚 Equal-Weighted Portfolio Comparison")
    equal_weights = {ticker: 1/len(price_data.columns)
                     for ticker in price_data.columns}
    eq_return = sum(mu[t] * equal_weights[t] for t in equal_weights)
    eq_volatility = (pd.Series(equal_weights).T @ S @
                     pd.Series(equal_weights)) ** 0.5
    eq_sharpe = eq_return / eq_volatility

    st.metric("Equal-Weighted Expected Return", f"{eq_return*100:.2f}%")
    st.metric("Equal-Weighted Volatility", f"{eq_volatility*100:.2f}%")
    st.metric("Equal-Weighted Sharpe Ratio", f"{eq_sharpe:.2f}")

else:
    st.error("❌ No data could be fetched. Please check the tickers or date range.")

# --- One-step PDF Download Button ---
with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", size=12)
    pdf.cell(200, 10, txt="Portfolio Optimization Summary", ln=True, align="C")

    # Portfolio Weights
    pdf.ln(10)
    pdf.set_font("Times", size=10)
    pdf.cell(200, 10, txt="Suggested Weights:", ln=True)
    for ticker, weight in cleaned_weights.items():
        pdf.cell(200, 8, txt=f"{ticker}: {round(weight * 100, 2)}%", ln=True)

    # Performance Metrics
    pdf.ln(10)
    pdf.set_font("Times", size=10)
    pdf.cell(
        200, 10, txt=f"Expected Annual Return: {expected_return*100:.2f}%", ln=True)
    pdf.cell(200, 10, txt=f"Annual Volatility: {volatility*100:.2f}%", ln=True)
    pdf.cell(200, 10, txt=f"Sharpe Ratio: {sharpe:.2f}", ln=True)

    # Save PDF and offer immediate download
    pdf.output(tmpfile.name)

    with open(tmpfile.name, "rb") as f:
        st.download_button(
            "📥 Download PDF", f, file_name="portfolio_summary.pdf", mime="application/pdf")

    os.remove(tmpfile.name)

    st.markdown("---")
    st.caption("Built by Aarya Soni | Powered by Polygon.io + PyPortfolioOpt")
