import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine


#connecting to engine
DB_URL= "postgresql://niranjanprakash:bagon1234@localhost:5432/stock_data"
engine = create_engine(DB_URL)


#loading DB from postgres
@st.cache_data

def load_data(query):
    return pd.read_sql(query,engine)

#streamlit app
st.title("\U0001F4C8 Stock Market Dashboard")


#getting market data
market_data_query = "SELECT * FROM market_data"
market_data = load_data(market_data_query)

#getting quarterly stmnt
income_data_query = "SELECT * FROM filtered_income_statements"
income_data = load_data(income_data_query)

#refresh for updated data

#if st.button('Fetch Latest Data'):
   # response = requests.post(flask_api_url, json ={ 
   #        "tickers": ["AAPL", "GOOG"],
   #     "start_date": "2023-01-01",
   #    "end_date": "2023-12-31"
    #})
   #if response.status_code == 200:
    #    st.success("Data fetched successfully!")
    #else:
    #    st.error("Failed to fetch data")

#filters
st.sidebar.header("Filters")
tickers= st.sidebar.multiselect("Select Stocks", market_data['ticker'].unique())
date_range = st.sidebar.multiselect("Select Date Range", [])
metrics = st.sidebar.multiselect("Select Metrics", income_data.columns[2:])

if tickers:
    filtered_market_data = market_data[market_data['ticker'].isin(tickers)]
else:
    filtered_market_data = market_data

if len(date_range)==2:
    start_date, end_date = date_range
    filtered_market_data = filtered_market_data[
        (filtered_market_data['datetime_'] >= pd.Timestamp(start_date)) &
        (filtered_market_data['datetime_'] <= pd.Timestamp(end_date))
    ]


if tickers:
    filtered_income_data = income_data[income_data['ticker'].isin(tickers)]
else:
    filtered_income_data = income_data

if metrics:
    filtered_income_data = filtered_income_data[['ticker', 'datetime_']+ metrics]


#Layout and graphs

st.header("Market Overview")
col1, col2 = st.columns(2)

with col1: 
    st.subheader("Stock Price Trends")
    fig= px.line(filtered_market_data, x="datetime_", y="close", color= 'ticker', title= "Stock Price Trend")
    st.plotly_chart(fig)

with col2:
    st.subheader("Daily Returns")
    fig = px.line(filtered_market_data, x="datetime_", y="close", color= 'ticker', title= "Daily Returns")
    st.plotly_chart(fig)

#second rows
st.header("Market Data")
st.write("Filtered Market Data:")
st.dataframe(filtered_market_data)

st.header("Quarterly Financials")
st.write("Filtered Quarterly Financial Statement:")
st.dataframe(filtered_income_data)

#Metric graph

if metrics: 
    st.header("Quarterly Metrics")
    for metric in metrics: 
        st.subheader(f"{metric} Over Time")
        fig = px.line(filtered_income_data, x="datetime_",y= metric, color='ticker', title="f{metric] Over Time}")
        st.plotly_chart(fig)
