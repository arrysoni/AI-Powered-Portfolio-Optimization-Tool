📈 AI-Powered Portfolio Optimization Tool
🔍 Overview
This Streamlit-based web app allows users to build custom stock portfolios, fetch real-time adjusted close prices, and receive optimized investment recommendations using Modern Portfolio Theory.

Leveraging the powerful PyPortfolioOpt library and real-time data from Polygon.io, this tool computes optimal allocations to maximize the Sharpe Ratio, while offering:

Custom stock selection

Adjustable risk exposure

Date range configuration

Real-time visualizations and analytics

Downloadable CSV and PDF reports

Equal-weighted portfolio comparison

🚀 Live Demo
🌐 Click here to use the live app

Replace the URL with your deployed app link.

📊 Features
Feature	Description
🔎 Ticker Input	Enter any number of stock tickers (comma-separated)
📆 Date Range	Select a custom range for backtesting performance
🎯 Risk Control	Adjust maximum weight per stock to reflect your risk appetite
📈 Price Visualization	Line chart of historical adjusted close prices
💼 Optimized Weights	Max Sharpe ratio portfolio using mean-variance optimization
🥧 Portfolio Pie Chart	See your optimized allocations visually
📥 CSV & PDF Downloads	Export weights and metrics with one click
🔁 Equal-Weighted Comparison	Compare against a naïve equal-weighted strategy

📂 Project Structure
bash
Copy
Edit
├── portfolio_app.py         # Main Streamlit app
├── requirements.txt         # All required dependencies
├── runtime.txt
├── .streamlit               # UI customization
   ├── config.toml
├── README.md                # You're here!
🛠️ Setup Instructions
🔸 1. Clone the Repository
bash
Copy
Edit
git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
cd YOUR-REPO-NAME
🔸 2. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
🔸 3. Run Locally
bash
Copy
Edit
streamlit run portfolio_app.py
🔐 Polygon.io API Key Setup
Replace the value of api_key in portfolio_app.py with your own:

python
Copy
Edit
api_key = "YOUR_POLYGON_API_KEY"
Or better, store it using st.secrets["api_key"] if deploying securely on Streamlit Cloud.

📦 Requirements
All dependencies are listed in requirements.txt, but key libraries include:

streamlit

PyPortfolioOpt

matplotlib, pandas, requests, fpdf

🧠 Methodology
The optimization is powered by Modern Portfolio Theory, where:

Expected return is calculated using historical mean returns

Risk is modeled using sample covariance of asset returns

Sharpe Ratio is maximized using convex optimization

Constraints allow bounding stock allocations (e.g., max 60%)

📄 License
MIT License. Free for personal and commercial use. Attribution appreciated.

🙌 Acknowledgments
Polygon.io for market data APIs

PyPortfolioOpt by Robert Martin

Streamlit for fast deployment

