import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from pypfopt import EfficientFrontier, risk_models, expected_returns

st.title("📈 AI-Powered Portfolio Optimizer")

# Selecting the stocks to choose from
tickers = st.multiselect(
    "Choose your stocks:",
    ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'SPY', 'QQQ'],
    default=['AAPL', 'MSFT', 'SPY']
)

if tickers:
    # Get stock data
    raw_data = yf.download(tickers, start="2020-01-01")
    # st.write("Raw data columns:", raw_data.columns)   # Debugging this

    # Safely extract 'Close' column
    if isinstance(raw_data.columns, pd.MultiIndex):
        if "Close" in raw_data.columns.levels[0]:
            data = raw_data["Close"]
        else:
            st.error(
                "Could not find 'Close' in downloaded data. Please try different tickers.")
            st.stop()
    else:
        if "Close" in raw_data.columns:
            data = raw_data[["Close"]]
            data.columns = tickers
        else:
            st.error(
                "Could not find 'Close' in downloaded data. Please try different tickers.")
            st.stop()

    # Show price chart
    st.subheader("📉 Historical Price Data")
    st.line_chart(data)

    # Run optimizer
    st.subheader("📊 Optimized Portfolio")
    mu = expected_returns.mean_historical_return(data)
    S = risk_models.sample_cov(data)
    ef = EfficientFrontier(mu, S)
    weights = ef.max_sharpe()
    cleaned_weights = ef.clean_weights()
    st.write("✅ Recommended Allocation:")
    st.write(cleaned_weights)

    # Pie Chart of Allocations
    st.subheader("📊 Allocation Breakdown")

    # Filter out zero allocations
    non_zero_allocations = {ticker: weight for ticker,
                            weight in cleaned_weights.items() if weight > 0}

    # Create Pie Chart
    fig, ax = plt.subplots()
    ax.pie(non_zero_allocations.values(),
           labels=non_zero_allocations.keys(), autopct="%1.1f%%", startangle=90)
    ax.axis("equal")  # Equal aspect ratio ensures the pie chart is circular

    st.pyplot(fig)

    # 💰 Investment Calculator
    st.subheader("💵 Investment Breakdown")

    # Let user input how much they want to invest
    total_investment = st.number_input(
        "Enter your total investment amount:", min_value=0.0, value=100000.0, step=1000.0)

    # Calculate actual ₹ or $ amount for each stock
    investment_allocation = {ticker: round(
        weight * total_investment, 2) for ticker, weight in cleaned_weights.items() if weight > 0}

    # Show as a table
    st.write("Based on your optimized allocation:")
    st.table(investment_allocation)

    # 📈 Portfolio Metrics
    st.subheader("📈 Portfolio Performance Metrics")

    # Calculate performance
    expected_annual_return = ef.portfolio_performance()[0]  # return
    annual_volatility = ef.portfolio_performance()[1]       # volatility
    sharpe_ratio = ef.portfolio_performance()[2]            # sharpe

    # Show results with formatting
    st.metric("Expected Annual Return", f"{expected_annual_return*100:.2f}%")
    st.metric("Annual Volatility (Risk)", f"{annual_volatility*100:.2f}%")
    st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")
