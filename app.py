import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go

# Page configuration
st.set_page_config(layout="wide")
st.title("📈 Simple Stock Market Data Viewer")

# Sidebar inputs
st.sidebar.header("User Input")
ticker_symbol = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL)", "AAPL").upper()

today = datetime.now()
start_date_default = today - timedelta(days=365)

start_date = st.sidebar.date_input("Start Date", start_date_default)
end_date = st.sidebar.date_input("End Date", today)

if start_date > end_date:
    st.sidebar.error("Error: End date must fall after start date.")

# Fetch stock data
@st.cache_data
def get_stock_data(ticker, start, end):
    try:
        data = yf.download(ticker, start=start, end=end)
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Main logic
if st.sidebar.button("Fetch Data"):
    if ticker_symbol:
        stock_data = get_stock_data(ticker_symbol, start_date, end_date)

        if not stock_data.empty:
            st.subheader(f"📊 Historical Data for {ticker_symbol}")
            st.dataframe(stock_data)

            # Closing price chart
            st.subheader("📈 Closing Price")
            st.line_chart(stock_data['Close'])

            # Volume chart
            st.subheader("📦 Volume")
            st.bar_chart(stock_data['Volume'])

            # SMA chart
            st.subheader("🧮 Simple Moving Average (SMA)")
            sma_period = st.slider("Select SMA Period (days)", 10, 100, 20)
            stock_data['SMA'] = stock_data['Close'].rolling(window=sma_period).mean()
            st.line_chart(stock_data[['Close', 'SMA']])

            # Candlestick chart
            st.subheader("🕯️ Candlestick Chart")
            fig = go.Figure(data=[go.Candlestick(
                x=stock_data.index,
                open=stock_data['Open'],
                high=stock_data['High'],
                low=stock_data['Low'],
                close=stock_data['Close']
            )])
            fig.update_layout(xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

            # Download CSV
            st.subheader("📥 Download Data")
            csv = stock_data.to_csv().encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"{ticker_symbol}_data.csv",
                mime='text/csv'
            )
        else:
            st.warning("No data fetched. Please try a different ticker or date range.")
    else:
        st.warning("Please enter a stock ticker symbol to fetch data.")

st.sidebar.markdown("---")
st.sidebar.markdown("Built with ❤️ using Streamlit and yfinance")