import yfinance as yf
df = yf.download(["AAPL", "MSFT", "TSLA"], period="1y", threads=False)
print(df.head())
