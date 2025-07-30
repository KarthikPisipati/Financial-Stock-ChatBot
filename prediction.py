import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# STEP 1: Get Historical Stock Data
def get_stock_data(ticker, period='5y'):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period)
    return data[['Close']].dropna()

# STEP 2: Build LSTM Model
def build_model(data, lookback=60):
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data)

    X, y = [], []
    for i in range(lookback, len(scaled_data)):
        X.append(scaled_data[i-lookback:i])
        y.append(scaled_data[i])
    X, y = np.array(X), np.array(y)

    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(X.shape[1], 1)),
        LSTM(50),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X, y, epochs=20, batch_size=32, verbose=1)

    return model, scaler, lookback

# STEP 3: Predict Next Day Price
def predict_next_day(model, scaler, data, lookback):
    last_sequence = data[-lookback:]
    scaled_last = scaler.transform(last_sequence)
    X_input = np.reshape(scaled_last, (1, lookback, 1))
    pred_scaled = model.predict(X_input)
    prediction = scaler.inverse_transform(pred_scaled)
    return prediction[0][0]

# STEP 4: Evaluate the Model
def evaluate_model(model, scaler, data, lookback):
    scaled = scaler.transform(data)
    X_test, y_test = [], []

    for i in range(lookback, len(scaled)):
        X_test.append(scaled[i-lookback:i])
        y_test.append(scaled[i])

    X_test, y_test = np.array(X_test), np.array(y_test)
    preds_scaled = model.predict(X_test)
    preds = scaler.inverse_transform(preds_scaled)
    y_true = scaler.inverse_transform(y_test)

    mae = mean_absolute_error(y_true, preds)
    rmse = np.sqrt(mean_squared_error(y_true, preds))
    r2 = r2_score(y_true, preds)

    return mae, rmse, r2
    print("\n📊 Evaluation Metrics:")
    print(f"MAE  : {mae:.2f}")
    print(f"RMSE : {rmse:.2f}")
    print(f"R²   : {r2:.4f}")

# === MAIN FLOW ===
# if __name__ == "__main__":
def predict(ticker):
    ticker = ticker.upper()+".NS"
    
    print(f"\n 🔍 Fetching data for {ticker}...")
    data = get_stock_data(ticker)
    
    if data.empty:
        print(" ⚠️ No data found for the ticker. Please check the symbol.")
    else:
        print(" 📈 Training model...")
        model, scaler, lookback = build_model(data.values)
        
        print(" 🔮 Predicting next day closing price...")
        next_price = predict_next_day(model, scaler, data.values, lookback)
        
        print(f"\n📅 Predicted next closing price for {ticker}: ₹{next_price:.2f}")
        
        mae, rmse, r2 = evaluate_model(model, scaler, data.values, lookback)

        return next_price, mae, rmse, r2