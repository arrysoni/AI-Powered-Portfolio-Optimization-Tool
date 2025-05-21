import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from pypfopt import EfficientFrontier, risk_models, expected_returns

# App title
st.title("📈 AI-Powered Portfolio Optimizer")

# Sidebar inputs
st.sidebar.header("User Input")
ticker = st.sidebar.text_input("Enter Ticker Symbol", value="AAPL")
start = st.sidebar.date_input("Start Date", value=pd.to_datetime("2020-01-01"))
end = st.sidebar.date_input("End Date", value=pd.to_datetime("today"))

# Download stock data
raw_data = yf.download(ticker, start=start, end=end)

# Display the raw data to inspect structure
st.write("Raw data preview:")
st.write(raw_data.head())

# Check for 'Close' column safely
if ("Close", ticker) in raw_data.columns:
    data = raw_data[("Close", ticker)]
else:
    st.error(
        f"'Close' data not found for {ticker}. Available coluSmns: {raw_data.columns.tolist()}")
    st.stop()


# Calculate expected returns and sample covariance
returns = raw_data[["Adj Close"]].pct_change().dropna()
mu = expected_returns.mean_historical_return(returns)
S = risk_models.sample_cov(returns)

# Portfolio Optimization
ef = EfficientFrontier(mu, S)
weights = ef.max_sharpe()
cleaned_weights = ef.clean_weights()
st.subheader("Recommended Portfolio Allocation")
st.write(cleaned_weights)

# Plotting pie chart
fig, ax = plt.subplots()
ax.pie(cleaned_weights.values(), labels=cleaned_weights.keys(), autopct='%1.1f%%')
ax.axis("equal")
st.pyplot(fig)

# Display performance
expected_annual_return, annual_volatility, sharpe_ratio = ef.portfolio_performance()

st.subheader("Portfolio Performance")
st.write(f"Expected annual return: {expected_annual_return*100:.2f}%")
st.write(f"Annual volatility: {annual_volatility*100:.2f}%")
st.write(f"Sharpe Ratio: {sharpe_ratio:.2f}")
