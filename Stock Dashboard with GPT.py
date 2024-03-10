import pandas as pd
import yfinance as yf
import plotly.express as px
import streamlit as st
import numpy as np
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData  # Import FundamentalData
import openai

# Set up your OpenAI GPT API key (ensure it's kept secure)
openai.api_key = "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"

st.title("Stock Dashboard")

# Sidebar input
ticker = st.sidebar.text_input("Ticker")
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")

# Validate input and handle errors
if not ticker:
    st.warning("Please enter a valid ticker symbol.")
elif start_date >= end_date:
    st.warning("End date must be after the start date.")
else:
    # Download data
    data = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'))

    # Check if data is empty
    if data.empty:
        st.warning(f"No data available for {ticker} between {start_date} and {end_date}.")
    else:
        # Plot data
        fig = px.line(data, x=data.index, y=data['Adj Close'], title=ticker)
        st.plotly_chart(fig, use_container_width=True)

        # Pricing Data Section
        st.header("Price Movement")
        data['%change'] = data['Adj Close'] / data['Adj Close'].shift(1) - 1
        data.dropna(inplace=True)
        st.write(data)  # Consider using st.dataframe(data) or st.table(data) for a more structured display
        annual_returns = data['%change'].mean() * 252 * 100
        st.write("Annual Return is", annual_returns, '%')
        stdev = np.std(data['%change']) * np.sqrt(252)
        st.write("Standard Deviation is", stdev * 100, '%')
        st.write('Risk Adj. Return is', annual_returns / stdev)

        # Fundamental Data Section
        st.header("Fundamental Data")

        # Use a secure method to retrieve your API key, such as environment variables
        key = 'YOUR_ALPHA_VANTAGE_API_KEY'  # Replace with your actual Alpha Vantage API key
        fd = FundamentalData(key, output_format='pandas')

        st.subheader('Balance Sheet')
        balance_sheet = fd.get_balance_sheet_annual(ticker)[0]
        bs = balance_sheet.T[2:]
        bs.columns = list(balance_sheet.T.iloc[0])
        st.write(bs)

        st.subheader('Income Statement')
        income_statement = fd.get_income_statement_annual(ticker)[0]
        is1 = income_statement.T[2:]
        is1.columns = list(income_statement.T.iloc[0])
        st.write(is1)

        st.subheader('Cash Flow Statement')
        cash_flow = fd.get_cash_flow_annual(ticker)[0]
        cf = cash_flow.T[2:]
        cf.columns = list(cash_flow.T.iloc[0])
        st.write(cf)

        user_input = st.text_input("Ask me anything about stocks or the market.")

        # Check if the user has entered a question
        if user_input:
            # Query ChatGPT for a response using the new method
            response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=user_input,
                max_tokens=150
            )
            st.write("ChatGPT's Response:")
            st.write(response['choices'][0]['text'])
