import pandas as pd
from sqlalchemy import create_engine

engine= create_engine("postgresql://niranjanprakash:bagon1234@localhost:5432/stock_data")
conn= engine.connect()
query= "SELECT * FROM market_data"
market_data =pd.read_sql(query,conn)

tickers = ["aapl", "msft","pltr",'tsla', 'zm','amc', 'intc' ] # stocks which are in portfolio

def data_transformation(market_data):
    transformed_data= []
    for ticker in tickers:
        close_col=f"close_{ticker}"

        if close_col in market_data.columns:
            ticker_data = market_data[['datetime_', close_col]].copy()
            print(f"processing ticker: {ticker}")
            print(ticker_data.head())  #checking ticker data\

            ticker_data.rename(columns={close_col: 'close'}, inplace=True)
            ticker_data.set_index('datetime_', inplace=True)

            ticker_data['daily_return'] = ticker_data['close'].pct_change()  # daily return
            ticker_data['sma_20_days'] = ticker_data['close'].rolling(window=20).mean()  # 20-day SMA
            ticker_data['volatility_20_days'] = ticker_data['close'].pct_change().rolling(window=20).std()

            ticker_data.reset_index(inplace=True)
            ticker_data['ticker'] = ticker
            cols = ['datetime_'] + [col for col in ticker_data.columns if col != 'datetime_']
            ticker_data = ticker_data[cols]
            transformed_data.append(ticker_data)
    print(transformed_data)
    final_transformed_data = pd.concat(transformed_data)
    final_transformed_data.to_sql("transformed_market_data", engine, if_exists='replace', index=False)
    print("Transformed data stored in PostgreSQL!")

