import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine

def fetch_market_data(tickers, start_date, end_date):
    # Downloading market data
    market_data = yf.download(tickers, start=start_date, end=end_date, group_by="ticker", timeout=30)
    # Resetting index and renaming date to datetime_
    market_data.reset_index(inplace=True)
    market_data.rename(columns={"Date": "datetime_"}, inplace=True)
    # cleaning up col names
    market_data.columns = [
        f"{col[1].lower()}_{col[0]}" if isinstance(col, tuple) and col[1] else col[0].lower()
        for col in market_data.columns
    ]
    # reshaping data
    if len(tickers) > 1:
        melted = pd.melt(
            market_data,
            id_vars=["datetime_"],
            var_name="metric",
            value_name="value"
        )
        # naming columns
        melted["ticker"] = melted["metric"].apply(lambda x: x.split("_")[1] if "_" in x else None)
        melted["metric"] = melted["metric"].apply(lambda x: x.split("_")[0] if "_" in x else x)
        # pivoting back
        market_data = melted.pivot(index=["datetime_", "ticker"], columns="metric", values="value").reset_index()
    return market_data

def fetch_quarterly_income_statement(tickers, quarterly_to_keep):
    income_data_master = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        try:
            income_data = stock.quarterly_income_stmt
            filtered_income_stmt = income_data.loc[
            income_data.index.intersection(quarterly_to_keep)] # keepign only columns which intersect b/w ones specified and all in statement
            filtered_income_stmt= filtered_income_stmt.T
            filtered_income_stmt["Ticker"]= ticker
            income_data_master.append(filtered_income_stmt)
        except Exception as e:
            print(f"Error in fetching income statement: {e}")

    final_quarterly_stmt = pd.concat(income_data_master,axis= 0, ignore_index=True) if income_data_master else pd.DataFrame()
    final_quarterly_stmt.columns = [ col.replace(" ", "_").lower() if isinstance(col, str) else "_".join(map(str, col)).lower() 
    for col in final_quarterly_stmt.columns ] 
    return final_quarterly_stmt

def data_transformation(market_data):
    engine = create_engine("postgresql://nprak42:bagon1234@stockdata.cl8ewyo6cf3z.us-east-2.rds.amazonaws.com:5432/stock_data")
    transformed_data = []
    tickers = ["AAPL", "MSFT", "PLTR", "TSLA", "ZM", "AMC", "INTC"]

    for ticker in tickers:
        ticker_data = market_data[market_data['ticker'] == ticker].copy()
        print(f"Processing ticker: {ticker}")
        ticker_data.set_index('datetime_', inplace=True)
        ticker_data['daily_return'] = ticker_data['close'].pct_change()  # Daily return
        ticker_data['sma_20_days'] = ticker_data['close'].rolling(window=20).mean()  # 20-day SMA
        ticker_data['volatility_20_days'] = ticker_data['close'].pct_change().rolling(window=20).std()

        # Reset index for final transformation
        ticker_data.reset_index(inplace=True)
        ticker_data['ticker'] = ticker

        # Reorder columns for better readability
        cols = ['datetime_', 'ticker'] + [col for col in ticker_data.columns if col not in ['datetime_', 'ticker']]
        ticker_data = ticker_data[cols]

        transformed_data.append(ticker_data)

    final_transformed_data = pd.concat(transformed_data)
    final_transformed_data.to_sql("transformed_market_data", con=engine, if_exists='replace', index=False)
    print("Transformed data stored in PostgreSQL!")

def store_to_postgres(data, table_name, db_url):
    engine = create_engine(db_url)
    print(type(data))
    data.to_sql(name=table_name, con=engine, if_exists='replace')
    print("Data stored in PostgreSQL!")
