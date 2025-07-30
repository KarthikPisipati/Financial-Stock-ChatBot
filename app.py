import streamlit as st
st.set_page_config(page_title="Stock Chatbot", layout="wide")
import pandas as pd
import datetime
import threading
from fetch_stock import get_stock_data, get_current_price, create_stock_chart, embed_tradingview_chart, display_stock_chart
from news_fetcher import fetch_news
from recommender import get_stockrecommendations, get_sellrecommendations

from prediction import predict


# Load custom CSS
with open("assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize session state
for key in ['chat_history', 'live_prices', 'stop_ticker']:
    if key not in st.session_state:
        st.session_state[key] = [] if key == 'chat_history' else {} if key == 'live_prices' else False

# Title
st.title("Indian Stock Market Assistant")
st.markdown("Get stock information, charts, news, and smart recommendations.")



# ------------------------------
# ✅ LATEST NEWS
# ------------------------------
# Replace the existing news panel section with this fixed code:

# News panel at the top
st.markdown("<h3>Latest Market News</h3>", unsafe_allow_html=True)
news_items = fetch_news()

# Create a clean container for the news
st.markdown('<div class="news-panel">', unsafe_allow_html=True)

# Process each news item individually
for item in news_items:
    # Format the date properly
    try:
        # Try to parse the date if it's in ISO format
        date_obj = datetime.datetime.strptime(item['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
        formatted_date = date_obj.strftime("%b %d, %Y %H:%M")
    except:
        # If parsing fails, use as-is
        formatted_date = item['publishedAt']
    
    # Create a cleaner news item display
    st.markdown(f"""
    <div class="news-item">
        <h4><a href="{item['url']}" target="_blank">{item['title']}</a></h4>
        <p>{item.get('description', '')[:150]}{'...' if item.get('description', '') else ''}</p>
        <small>{formatted_date}</small>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Additional CSS to improve news display
st.markdown("""
<style>
.news-panel {
    background-color: black;
    padding: 15px;
    border-radius: 5px;
    margin-bottom: 20px;
    max-height: 300px;
    overflow-y: auto;
}
.news-item {
    padding: 10px;
    margin-bottom: 10px;
    border-bottom: 1px solid #ddd;
    background-color: black;
    border-radius: 4px;
}
.news-item h4 {
    color:black;
    margin-top: 0;
    margin-bottom: 8px;
}
.news-item a {
    color: #1f77b4;
    text-decoration: none;
}
.news-item a:hover {
    text-decoration: underline;
}
.news-item p {
    margin-bottom: 5px;
    color: white;
}
.news-item small {
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# ✅ LAYOUT
# ------------------------------
col1, col2 = st.columns([3, 2])

# ========== LEFT COLUMN ==========
with col1:
    st.markdown("### Stock Price Lookup")
    symbol = st.text_input("Enter stock symbol (e.g., RELIANCE, TCS)", "RELIANCE")
    time_period = st.selectbox("Select time period", ["1d", "1wk", "1mo", "3mo", "6mo", "1y"])

    if st.button("Get Stock Data"):
        with st.spinner(f"Fetching data for {symbol}..."):
            # Use the new display_stock_chart function instead of the old implementation
            display_stock_chart(symbol, time_period)

# ========== RIGHT COLUMN ==========
with col2:
    st.markdown("### Stock Chatbot")
    user_input = st.text_input("Ask me about stocks (e.g., 'Show me INFY chart', 'Should I buy RELIANCE?')")

        
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        response = ""
        lower_input = user_input.lower()
        print(f"User input: {user_input}")

        # Detect request for chart or stock data
        if "chart" in lower_input or "price" in lower_input:
            words = user_input.upper().split()
            for word in words:
                if word not in ["CHART", "PRICE", "SHOW", "ME", "FOR", "OF", "THE", "A"]:
                    potential_symbol = word.strip(".,?!")
                    with col1:
                        success = display_stock_chart(potential_symbol, "1mo")
                        if success:
                            response = f"Here's the TradingView chart for {potential_symbol}. Check the left panel."
                            break
            if not response:
                response = "Couldn't detect a valid stock symbol. Try something like 'Show RELIANCE chart'."

        # BUY / RECOMMENDATIONS
        elif any(word in lower_input for word in ["buy", "recommend", "top pick", "top stocks", "which stock"]):
            # print("Fetching recommendations...")
            recommendations = get_stockrecommendations()
            # print(f"Recommendations: {recommendations}")
            # if recommendations:
            #     response = "📈 Here are today's top BUY picks:\n\n"
            #     for rec in recommendations:
            #         response += f"- {rec['symbol']}: {rec['action']} – {rec['reason']}\n"
            st.markdown("### Today's Stock Picks")
            recommendations = get_stockrecommendations()
            print(f"Recommendations: {recommendations}")
            for i in recommendations:
                st.success(i)
            else:
                response = "No top picks found at the moment. Try again later."

        # SELL suggestions
        elif any(word in lower_input for word in ["sell", "dump", "what to avoid", "exit"]):
            recommendations = get_sellrecommendations()
            print(f"Recommendations1: {recommendations}")
            for i in recommendations:
                st.error(i)

        # Market overview
        elif any(word in lower_input for word in ["market summary", "today's trend", "market today", "what's the trend"]):
            buys = get_stockrecommendations()
            sells = get_sellrecommendations()
            response = "📊 **Market Summary Today:**\n\n"

            if buys:
                response += "**Top Gainers:**\n"
                for rec in buys:
                    response += f"- {rec['symbol']} – {rec['reason']}\n"
            else:
                response += "No gainers reported.\n"

            response += "\n"

            if sells:
                response += "**Top Losers:**\n"
                for rec in sells:
                    response += f"- {rec['symbol']} – {rec['reason']}\n"
            else:
                response += "No losers reported.\n"

        # News queries
        elif "news" in lower_input or "latest" in lower_input:
            news_items = fetch_news()
            relevant_news = []

            for item in news_items:
                title = item.get("title", "").lower()
                desc = item.get("description", "").lower()
                if any(word in title or word in desc for word in lower_input.split()):
                    relevant_news.append(item)

            if relevant_news:
                response = "🗞️ Here's the latest news related to your query:\n\n"
                for item in relevant_news[:5]:
                    response += f"- [{item['title']}]({item['url']})\n"
            else:
                response = "Couldn't find specific news. Check the top news section above. 👆"

        # Fallback: Try to match news keywords
        else:
            news_items = fetch_news()
            keywords = lower_input.split()
            matched = []

            for item in news_items:
                if any(kw in item['title'].lower() or kw in item.get('description', '').lower() for kw in keywords):
                    matched.append(item)

            if matched:
                response = "Here’s what I found related to your query:\n\n"
                for item in matched[:3]:
                    response += f"- [{item['title']}]({item['url']})\n"
            else:
                response = "I can help with stock charts, prices, top picks, and news. Try 'top picks', 'sell today', or 'market summary'."

        st.session_state.chat_history.append({"role": "assistant", "content": response})
    else:
        st.warning("No stock recommendations available today.")

st.markdown("### Predict")
stock_input = st.text_input("Type the stock symbol (e.g., RELIANCE, TCS)")
if stock_input:
    with st.spinner(f"Fetching data for {stock_input}..."):
        prediction,mae,rmse,r2 = predict(stock_input)
        st.success(f"Predicted next closing price for {stock_input}: ₹{prediction:.2f}")
        st.markdown(f"**Evaluation Metrics:**")
        st.markdown(f"- MAE: {mae:.2f}")
        st.markdown(f"- RMSE: {rmse:.2f}")
        st.markdown(f"- R²: {r2:.4f}")

        


    


    # if recommendations:
    #     st.markdown("**Top Gainers:**")
    #     st.markdown(f"{recommendations}")
        # for rec in recommendations:
        #     symbol = rec["symbol"].replace('.NS', '')
        #     action = rec["action"]
        #     reason = rec["reason"]
        #     color = "green" if action == "BUY" else "red" if action == "SELL" else "orange"

        #     st.markdown(f"""
        #     <div style="padding:10px; border-left:5px solid {color}; margin-bottom:10px; background-color:black; border-radius: 5px;">
        #         <h4>{symbol}: <span style="color:{color}">{action}</span></h4>
        #         <p>{reason}</p>
        #     </div>
        #     """, unsafe_allow_html=True)
    


# ------------------------------
# ✅ FOOTER
# ------------------------------
st.markdown("---")
st.markdown("📊 Stock data from Yahoo Finance | 🗞️ News via NewsAPI / Economic Times | 📈 Charts powered by TradingView")