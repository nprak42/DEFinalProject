# ETL Pipeline for Stock Data

## Project Overview
This project implements an ETL (Extract, Transform, Load) pipeline for financial stock data. The pipeline fetches stock data from Yahoo Finance, performs transformations, and stores the results in an Amazon RDS database using PostgreSQL. 

## Features
- **Data Extraction**: Fetch historical stock prices and quarterly income statements using the Yahoo Finance API (`yfinance`).
- **Data Transformation**: Clean and transform data using Pandas to calculate metrics like daily returns, moving averages, and volatility.
- **Data Storage**: Store raw and transformed data in an RDS PostgreSQL database.
- **Data Visualization**: Build a user-friendly Streamlit dashboard to view and analyze the data.

## Technologies Used
- **Python Libraries**:
  - `yfinance`: Fetch stock data.
  - `pandas`: Data manipulation and transformation.
  - `sqlalchemy`: Interface for interacting with the PostgreSQL database.
  - `streamlit`: Build an interactive dashboard.
  - `flask`: Backend API to fetch data for the dashboard.
- **Database**: PostgreSQL hosted on Amazon RDS.
- **Deployment**: Streamlit app serves as the frontend.

## Project Structure
```
project/
|
|-- et_scripts/
|   |-- Extract_data_Yfinance.py  # Scripts for data extraction and transformation.
|   |-- flask_app.py              # Functions for database interactions.
|   |-- requirements.txt          # requirements for docker
|
|-- dashboard/
|   |-- requirements_dashboard.txt # requirements for docker                   
|   |-- load_data.py              # Streamlit app for data visualization.
|-- requirements.txt              # Python dependencies.
|-- README.md                     # Project documentation.
```

## Setup Instructions

### Prerequisites
1. **Install Python 3.8 or higher**
2. **Install PostgreSQL** (local or Amazon RDS instance)
3. **Set up AWS credentials** (if using RDS)


## How It Works

1. **Data Extraction**:
   - Fetch historical stock data using `yfinance`.
   - Retrieve quarterly income statements for specified tickers.
2. **Data Transformation**:
   - Calculate financial metrics such as daily returns, 20-day SMA, and volatility.
   - Clean and format the data for storage.
3. **Data Storage**:
   - Save raw and transformed data to a PostgreSQL database hosted on Amazon RDS.
4. **Visualization**:
   - The Flask app provides API endpoints for fetching the data.
   - The Streamlit dashboard calls these endpoints to display the data interactively.

## Example Usage
1. Launch the Streamlit app.
2. Enter stock tickers, start date, and end date in the dashboard.
3. Fetch and view historical market data and transformed metrics.
4. Explore quarterly income statements for the selected tickers.

## Future Improvements
- Add support for more financial metrics.
- Implement user authentication for the dashboard.
- Optimize data pipeline for larger datasets.
- 
## Contact
For questions or feedback, please reach out to niranjanprak@umass.edu

