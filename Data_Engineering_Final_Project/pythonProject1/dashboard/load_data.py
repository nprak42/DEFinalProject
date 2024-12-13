import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import sys
import os
import requests
from Extract_data_Yfinance import fetch_market_data,fetch_quarterly_income_statement, store_to_postgres, data_transformation

DB_URL = "postgresql://nprak42:bagon1234@stockdata.cl8ewyo6cf3z.us-east-2.rds.amazonaws.com:5432/stock_data"

# Title for dashboard
st.title("Financial Data Dashboard")
st.write("""
This dashboard allows you to fetch and visualize market data and quarterly income statements for selected tickers.
""")

# Input for Market Data
st.header("Fetch Market Data")
tickers_input = st.text_input("Enter Tickers for Market Data (comma separated):", "AAPL,MSFT,TSLA")
start_date = st.date_input("Start Date", pd.to_datetime("2023-01-01"))
end_date = st.date_input("End Date", pd.to_datetime("2023-12-31"))

if st.button("Fetch Market Data"):
    tickers = tickers_input.split(",")
    st.write(f"Fetching data for tickers: {tickers}")
    try:
        # Fetch market data and store in database
        market_data = fetch_market_data(tickers, start_date, end_date)
        store_to_postgres(market_data, "market_data", DB_URL)

        # Fetch updated market data from database
        engine = create_engine(DB_URL)
        market_data_db = pd.read_sql("SELECT * FROM market_data", engine)

        # Display fetched data
        st.subheader("Fetched Market Data")
        st.dataframe(market_data_db)

        # Create line plots for each ticker
        st.subheader("Market Data Visualization")
        for ticker in tickers:
            ticker_data = market_data_db[market_data_db['ticker'] == ticker]
            if not ticker_data.empty:
                fig = px.line(
                    ticker_data, x='datetime_', y='close', title=f"{ticker} Close Prices"
                )
                st.plotly_chart(fig)
            else:
                st.warning(f"No data available for {ticker}.")
    except Exception as e:
        st.error(f"Error fetching market data: {e}")

# Streamlit form for fetching and displaying quarterly income statements
st.header("Fetch Quarterly Income Statements")
tickers_income_input = st.text_input("Enter Tickers for Income Statement (comma separated):", "AAPL,MSFT,TSLA")
quarters_to_keep = st.text_input("Enter Quarters to Keep (comma separated, e.g., 'Q1 2023, Q2 2023')", "Q1 2023, Q2 2023")

if st.button("Fetch Income Statements"):
    tickers = tickers_income_input.split(",")
    quarters = quarters_to_keep.split(",")
    try:
        # Fetch income statements and store in database
        income_statements = fetch_quarterly_income_statement(tickers, quarters)
        store_to_postgres(income_statements, "filtered_income_statements", DB_URL)

        # Fetch income statements from database
        engine = create_engine(DB_URL)
        income_statements_db = pd.read_sql("SELECT * FROM filtered_income_statements", engine)

        # Display the income statements
        st.subheader("Fetched Quarterly Income Statements")
        st.dataframe(income_statements_db)
    except Exception as e:
        st.error(f"Error fetching income statements: {e}")

# Streamlit form for fetching and displaying transformed data
st.header("View Transformed Market Data")

if st.button("View Transformed Data"):
    try:
        # Fetch the transformed data from the database
        engine = create_engine(DB_URL)
        transformed_data = pd.read_sql("SELECT * FROM transformed_market_data", engine)
        
        st.subheader("Transformed Market Data")
        st.dataframe(transformed_data)
    except Exception as e:
        st.error(f"Error fetching transformed data: {e}")
