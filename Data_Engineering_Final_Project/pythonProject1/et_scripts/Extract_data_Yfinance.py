import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine

def fetch_market_data(tickers, start_date, end_date):
    market_data = yf.download(tickers, start=start_date, end=end_date, timeout= 30)  # timeperiod for data collection
    market_data.reset_index(inplace=True)
    market_data.rename(columns={"Date": "datetime"}, inplace=True)  # Datetime index added as a column
    market_data.columns =["_".join(map(str,col)).lower() if isinstance(col, tuple) else col
                          for col in market_data.columns]
    market_data_long = market_data.melt(id_vars=["datetime_"],var_name="ticker_column", value_name=["close"])
    market_data_long["ticker"]= market_data_long['ticker_column'].apply(lambda x: x.split('_')[-1].upper())
    market_data_long.drop(columns="ticker_column",inplace=True)
    return market_data_long


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
    transformed_data= []
    tickers = ["aapl", "msft","pltr",'tsla', 'zm','amc', 'intc' ] # stocks which are in portfolio

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

def store_to_postgres(data, table_name, db_url):
    engine = create_engine(db_url)
    print(type(data))
    data.to_sql(name=table_name, con=engine, if_exists='replace')
    print("Data stored in PostgreSQL!")
