import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

from pypfopt import EfficientFrontier, risk_models, expected_returns

st.title("AI-Powered Portfolio Optimization Tool")

# --- User input for tickers ---
tickers_input = st.text_input(
    "Enter stock tickers separated by commas (e.g., AAPL, MSFT, TSLA)", "AAPL, MSFT, TSLA")
tickers = [ticker.strip().upper() for ticker in tickers_input.split(',')]

# --- Fetch Adjusted Close Data using period ---
if tickers:
    try:
        st.write("Fetching 1 year of data...")
        raw_data = yf.download(
            tickers, period='1y', group_by='ticker', threads=False, progress=False)

        if raw_data.empty or "Adj Close" not in raw_data:
            st.warning("No valid stock data found. Please check the tickers.")
        else:
            price_data = raw_data.loc[:, ("Adj Close", slice(None))]
            price_data.columns = price_data.columns.droplevel(0)
            price_data = price_data.dropna(how="all")

            st.subheader("Historical Adjusted Close Prices")
            st.line_chart(price_data)

            # --- Calculate returns and risk ---
            returns = price_data.pct_change().dropna()
            mu = expected_returns.mean_historical_return(price_data)
            S = risk_models.sample_cov(price_data)

            # --- Portfolio Optimization ---
            ef = EfficientFrontier(mu, S)
            weights = ef.max_sharpe()
            cleaned_weights = ef.clean_weights()

            st.subheader("Recommended Portfolio Allocation")
            st.write(cleaned_weights)

            # --- Plot Pie Chart ---
            fig, ax = plt.subplots()
            ax.pie(cleaned_weights.values(),
                   labels=cleaned_weights.keys(), autopct='%1.1f%%')
            ax.axis("equal")
            st.pyplot(fig)

            # --- Display Portfolio Performance ---
            expected_annual_return, annual_volatility, sharpe_ratio = ef.portfolio_performance()

            st.subheader("Portfolio Performance")
            st.write(
                f"Expected annual return: {expected_annual_return*100:.2f}%")
            st.write(f"Annual volatility: {annual_volatility*100:.2f}%")
            st.write(f"Sharpe Ratio: {sharpe_ratio:.2f}")

    except Exception as e:
        st.error(f"Error fetching or processing data: {e}")
