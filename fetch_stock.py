import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import traceback
from datetime import datetime, timedelta

def get_stock_data(symbol, period='1mo'):
    """
    Fetch stock data for the given symbol and period.
    Includes robust error handling and fallback mechanisms.
    """
    try:
        # Clean the symbol and add .NS extension for NSE stocks if needed
        if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
            symbol = f"{symbol}.NS"
        
        # Try to download the data
        data = yf.download(symbol, period=period)
        
        # Check if we got valid data
        if data is None or data.empty:
            # Try with BSE extension instead
            if symbol.endswith('.NS'):
                bse_symbol = symbol.replace('.NS', '.BO')
                data = yf.download(bse_symbol, period=period)
                if data is not None and not data.empty:
                    return data, bse_symbol
        
        # Verify we have required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        if data is not None and not data.empty:
            for col in required_columns:
                if col not in data.columns:
                    st.warning(f"Missing required column: {col}")
                    return None, symbol
            
            # Log success
            st.markdown(f"<div style='display:none'>Successfully fetched {len(data)} data points for {symbol}</div>", unsafe_allow_html=True)
            return data, symbol
        else:
            st.warning(f"No data returned for {symbol}. The symbol may be invalid or data unavailable.")
            return None, symbol
            
    except Exception as e:
        st.error(f"Error fetching stock data: {str(e)}")
        st.markdown(f"<details><summary>Technical Details</summary>{traceback.format_exc()}</details>", unsafe_allow_html=True)
        return None, symbol

def get_current_price(symbol):
    """
    Get the current market price for a stock symbol.
    Returns a numerical value or 'N/A' if unavailable.
    """
    try:
        # Add .NS extension if needed
        if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
            symbol = f"{symbol}.NS"
        
        # Fetch the ticker info
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Try to get current price
        price = info.get('regularMarketPrice')
        
        if price is None:
            # Try alternative price fields
            price = info.get('currentPrice') or info.get('previousClose')
            
            # If still no price, try BSE
            if price is None and symbol.endswith('.NS'):
                bse_symbol = symbol.replace('.NS', '.BO')
                bse_ticker = yf.Ticker(bse_symbol)
                price = bse_ticker.info.get('regularMarketPrice') or bse_ticker.info.get('currentPrice')
        
        return price if price is not None else 'N/A'
        
    except Exception as e:
        st.markdown(f"<div style='display:none'>Error getting price: {str(e)}</div>", unsafe_allow_html=True)
        return 'N/A'

def get_stock_info(symbol):
    """
    Get detailed information about a stock including financials and company info.
    """
    try:
        if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
            symbol = f"{symbol}.NS"
        
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Extract relevant info
        company_info = {
            'Company Name': info.get('longName', 'N/A'),
            'Sector': info.get('sector', 'N/A'),
            'Industry': info.get('industry', 'N/A'),
            'Market Cap': info.get('marketCap', 'N/A'),
            'P/E Ratio': info.get('trailingPE', 'N/A'),
            '52 Week High': info.get('fiftyTwoWeekHigh', 'N/A'),
            '52 Week Low': info.get('fiftyTwoWeekLow', 'N/A'),
            'Dividend Yield': info.get('dividendYield', 'N/A'),
            'Avg Volume': info.get('averageVolume', 'N/A'),
            'Beta': info.get('beta', 'N/A')
        }
        
        # Clean up any None values
        for key, value in company_info.items():
            if value is None:
                company_info[key] = 'N/A'
            elif isinstance(value, (int, float)) and key != 'Beta':
                if key == 'Market Cap':
                    if value >= 1e9:
                        company_info[key] = f"₹{value/1e9:.2f}B"
                    else:
                        company_info[key] = f"₹{value/1e6:.2f}M"
                elif key == 'Dividend Yield' and value != 'N/A':
                    company_info[key] = f"{value*100:.2f}%"
                elif value != 'N/A':
                    company_info[key] = f"{value:,.2f}"
        
        return company_info
    
    except Exception as e:
        st.warning(f"Could not fetch detailed info for {symbol}: {str(e)}")
        return {}

def create_stock_chart(data, symbol):
    """
    LEGACY METHOD: Create an interactive candlestick chart for the given stock data.
    This method is kept for backward compatibility.
    Now redirects to the TradingView chart.
    """
    st.info("Using TradingView charts for enhanced visualization")
    return embed_tradingview_chart(symbol)

def embed_tradingview_chart(symbol):
    """
    Embed TradingView chart directly in Streamlit
    """
    try:
        # First check if the stock exists
        data, verified_symbol = get_stock_data(symbol, period='1d')
        
        if data is not None and not data.empty:
            # Format symbol for TradingView
            if verified_symbol.endswith('.NS'):
                tv_symbol = f"NSE:{verified_symbol.replace('.NS', '')}"
            elif verified_symbol.endswith('.BO'):
                tv_symbol = f"BSE:{verified_symbol.replace('.BO', '')}"
            else:
                tv_symbol = f"NSE:{verified_symbol}"  # Default to NSE
            
            # Display stock information
            st.markdown(f"## {verified_symbol} Stock Chart")
            
            # Display current price
            current_price = get_current_price(verified_symbol)
            if current_price != 'N/A' and isinstance(current_price, (int, float)):
                st.metric("Current Price", f"₹{current_price:.2f}")
            elif current_price != 'N/A':
                st.metric("Current Price", f"{current_price}")
            
            # Create TradingView Widget HTML
            tradingview_widget = f"""
            <!-- TradingView Widget BEGIN -->
            <div class="tradingview-widget-container">
              <div id="tradingview_chart"></div>
              <div class="tradingview-widget-copyright">
                <a href="https://www.tradingview.com/symbols/{tv_symbol}/" rel="noopener" target="_blank">
                <span class="blue-text">{tv_symbol} Chart</span></a> by TradingView
              </div>
              <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
              <script type="text/javascript">
              new TradingView.widget(
              {{
              "width": 980,
              "height": 610,
              "symbol": "{tv_symbol}",
              "interval": "D",
              "timezone": "Asia/Kolkata",
              "theme": "light",
              "style": "1",
              "locale": "en",
              "toolbar_bg": "#f1f3f6",
              "enable_publishing": false,
              "hide_top_toolbar": false,
              "hide_legend": false,
              "save_image": false,
              "container_id": "tradingview_chart",
              "studies": [
                "MASimple@tv-basicstudies",
                "RSI@tv-basicstudies",
                "Volume@tv-basicstudies"
              ]
            }}
              );
              </script>
            </div>
            <!-- TradingView Widget END -->
            """
            
            # Embed the TradingView chart
            st.components.v1.html(tradingview_widget, width=1000, height=650, scrolling=False)
            
            # Display stock info in an expander
            with st.expander("Company Information"):
                stock_info = get_stock_info(verified_symbol)
                if stock_info:
                    col1, col2 = st.columns(2)
                    
                    # Distribute info between two columns
                    info_items = list(stock_info.items())
                    midpoint = len(info_items) // 2
                    
                    with col1:
                        for key, value in info_items[:midpoint]:
                            st.markdown(f"**{key}**: {value}")
                    
                    with col2:
                        for key, value in info_items[midpoint:]:
                            st.markdown(f"**{key}**: {value}")
                else:
                    st.warning("Detailed company information not available.")
            
            return True
        else:
            st.error(f"Could not find stock data for {symbol}. Please check the symbol and try again.")
            return False
            
    except Exception as e:
        st.error(f"Error displaying TradingView chart: {str(e)}")
        st.markdown(f"<details><summary>Technical Details</summary>{traceback.format_exc()}</details>", unsafe_allow_html=True)
        return False

def display_stock_chart(symbol, period='1y'):
    """
    Main function to display stock chart - this is the primary function
    other modules should call to display a chart.
    
    Now using TradingView charts for better visualization.
    """
    return embed_tradingview_chart(symbol)