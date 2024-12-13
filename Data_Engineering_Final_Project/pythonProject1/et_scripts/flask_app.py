from flask import Flask, request, jsonify
from et_scripts.Extract_data_Yfinance import fetch_market_data, fetch_quarterly_income_statement, store_to_postgres, data_transformation
import pandas as pd
import logging
import os
import yfinance as yf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

DB_URL = "postgresql://niranjanprakash:bagon1234@localhost:5432/stock_data"

@app.route('/fetch_market_data', methods=['POST'])
def fetch_and_store_market_data():
    data = request.json
    tickers = data.get("tickers")
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    if not tickers or not start_date or not end_date:
        return jsonify({"error": "Missing parameters"}), 400
    
    try:
        market_data = fetch_market_data(tickers, start_date, end_date)
        logger.info(f"fetched market data for {len(tickers)} tickers.")
        store_to_postgres(market_data,"market_data", DB_URL )
        
        data_transformation(market_data)
        logger.info("Data transformation completed and stored")
        return jsonify({"message": "Market data fetched, transformed and stored"}), 200
    except Exception as e: 
        logger.error(f"Error")
        return jsonify({"error":str(e)}), 500


@app.route('/fetch_quarterly_income_statement', methods=['POST'])
def fetch_and_store_quarterly_income_statement():
    data = request.json
    tickers = data.get("tickers")
    quarterly_to_keep = data.get("quarterly_to_keep")
    if not tickers or not quarterly_to_keep:
        return jsonify({"error": "Missing parameters"}), 400

    try:
        income_statements= fetch_quarterly_income_statement(tickers, quarterly_to_keep)
        store_to_postgres(income_statements, "filtered_income_statements", DB_URL )
        return jsonify({"message": "Quarterly income stored."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5432)