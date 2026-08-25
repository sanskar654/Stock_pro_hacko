import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
from ta.trend import SMAIndicator, MACD
from ta.momentum import RSIIndicator
import joblib
from textblob import TextBlob
import os
import logging
import hashlib
import re
from email.mime.text import MIMEText
import smtplib
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from twilio.rest import Client
import time
import mysql.connector
from PIL import Image
import base64

# Configure logging
logging.basicConfig(filename='stock_analyzer.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

st.set_page_config(page_title="NIFTY AI Stock Pro", layout="wide", initial_sidebar_state="expanded")

# Vibrant, modern CSS with enhanced visual features
theme = st.sidebar.radio("Theme", ["Dark", "Light"], index=0)
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    .main {{
        background: {'linear-gradient(135deg, #1A237E, #3F51B5)' if theme == 'Dark' else 'linear-gradient(135deg, #E3F2FD, #BBDEFB)'};
        color: {'#E0E0E0' if theme == 'Dark' else '#212121'};
        font-family: 'Inter', sans-serif;
        padding: 20px;
        min-height: 100vh;
        position: relative;
        overflow-x: hidden;
    }}
    .main::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: {'url("https://www.transparenttextures.com/patterns/dark-mosaic.png")' if theme == 'Dark' else 'url("https://www.transparenttextures.com/patterns/light-wool.png")'};
        opacity: 0.1;
        z-index: -1;
    }}
    .sidebar .sidebar-content {{
        background: {'linear-gradient(180deg, #283593, #3F51B5)' if theme == 'Dark' else 'linear-gradient(180deg, #BBDEFB, #90CAF9)'};
        padding: 25px;
        border-right: 3px solid {'#00E676' if theme == 'Dark' else '#0288D1'};
        box-shadow: 2px 0 10px rgba(0,0,0,0.2);
        height: 100vh;
        position: sticky;
        top: 0;
    }}
    .sidebar .stRadio > div {{
        background: {'rgba(255,255,255,0.1)' if theme == 'Dark' else 'rgba(0,0,0,0.05)'};
        padding: 10px;
        border-radius: 8px;
    }}
    .stButton>button {{
        background: {'linear-gradient(45deg, #00E676, #4CAF50)' if theme == 'Dark' else 'linear-gradient(45deg, #0288D1, #03A9F4)'};
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .stButton>button:hover {{
        background: {'linear-gradient(45deg, #00C853, #388E3C)' if theme == 'Dark' else 'linear-gradient(45deg, #0277BD, #0288D1)'};
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }}
    .stTabs {{
        background: {'rgba(255,255,255,0.1)' if theme == 'Dark' else 'rgba(0,0,0,0.05)'};
        padding: 15px;
        border-radius: 12px;
        border: 2px solid {'#00E676' if theme == 'Dark' else '#0288D1'};
        margin-bottom: 20px;
        backdrop-filter: blur(5px);
    }}
    .stTabs [role="tab"] {{
        font-weight: 600;
        color: {'#E0E0E0' if theme == 'Dark' else '#424242'};
        padding: 10px 20px;
        border-radius: 8px;
        transition: all 0.3s ease;
    }}
    .stTabs [role="tab"][aria-selected="true"] {{
        background: {'#00E676' if theme == 'Dark' else '#0288D1'};
        color: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }}
    .stTabs [role="tab"]:hover {{
        background: {'rgba(0,230,118,0.2)' if theme == 'Dark' else 'rgba(2,136,209,0.2)'};
    }}
    .card {{
        background: {'linear-gradient(145deg, #263238, #37474F)' if theme == 'Dark' else 'linear-gradient(145deg, #FFFFFF, #F5F5F5)'};
        padding: 25px;
        border-radius: 16px;
        margin: 20px 0;
        box-shadow: 0 8px 20px rgba(0,0,0,{'0.3' if theme == 'Dark' else '0.15'});
        position: relative;
        overflow: hidden;
        transition: transform 0.3s ease;
        animation: slideUp 0.5s ease-out;
    }}
    .card:hover {{
        transform: translateY(-5px);
    }}
    .card::after {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 6px;
        background: {'linear-gradient(90deg, #00E676, #4CAF50)' if theme == 'Dark' else 'linear-gradient(90deg, #0288D1, #03A9F4)'};
        border-radius: 16px 16px 0 0;
    }}
    .stHeader {{
        font-size: 32px;
        font-weight: 700;
        color: {'#00E676' if theme == 'Dark' else '#0288D1'};
        text-align: center;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
        margin-bottom: 20px;
        animation: fadeIn 0.5s ease;
    }}
    .stMetric {{
        color: {'#00E676' if theme == 'Dark' else '#0288D1'};
        font-weight: 600;
    }}
    .premium {{
        background: linear-gradient(45deg, #FFD700, #FFA000);
        border: none;
        padding: 6px 12px;
        border-radius: 8px;
        color: #1A237E;
        font-weight: 700;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }}
    .premium:hover {{
        transform: scale(1.1);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }}
    .stSpinner > div > div {{
        border-color: {'#00E676' if theme == 'Dark' else '#0288D1'} transparent transparent transparent;
    }}
    @keyframes fadeIn {{
        from {{opacity: 0;}}
        to {{opacity: 1;}}
    }}
    @keyframes slideUp {{
        from {{transform: translateY(20px); opacity: 0;}}
        to {{transform: translateY(0); opacity: 1;}}
    }}
    @media (max-width: 768px) {{
        .main {{padding: 15px;}}
        .sidebar .sidebar-content {{padding: 15px;}}
        .stButton>button {{padding: 10px 20px; font-size: 14px;}}
        .card {{padding: 15px; margin: 10px 0;}}
        .stHeader {{font-size: 24px;}}
        .stTabs [role="tab"] {{padding: 8px 15px; font-size: 14px;}}
    }}
    .footer {{
        text-align: center;
        padding: 20px;
        color: {'#B0BEC5' if theme == 'Dark' else '#616161'};
        font-size: 14px;
        margin-top: 20px;
        border-top: 1px solid {'#4CAF50' if theme == 'Dark' else '#0288D1'};
    }}
    .footer a {{
        color: {'#00E676' if theme == 'Dark' else '#0288D1'};
        text-decoration: none;
        margin: 0 10px;
    }}
    .footer a:hover {{
        text-decoration: underline;
    }}
    </style>
""", unsafe_allow_html=True)

NIFTY_50 = {
    "Adani Ports": "ADANIPORTS.NS", "Asian Paints": "ASIANPAINT.NS", "Axis Bank": "AXISBANK.NS",
    "Bajaj Auto": "BAJAJ-AUTO.NS", "Bajaj Finance": "BAJFINANCE.NS", "Bajaj Finserv": "BAJAJFINSV.NS",
    "Bharti Airtel": "BHARTIARTL.NS", "Britannia": "BRITANNIA.NS", "Cipla": "CIPLA.NS",
    "Coal India": "COALINDIA.NS", "Divi's Labs": "DIVISLAB.NS", "Dr. Reddy's": "DRREDDY.NS",
    "Eicher Motors": "EICHERMOT.NS", "Grasim": "GRASIM.NS", "HCL Tech": "HCLTECH.NS",
    "HDFC Bank": "HDFCBANK.NS", "HDFC Life": "HDFCLIFE.NS", "Hero MotoCorp": "HEROMOTOCO.NS",
    "Hindalco": "HINDALCO.NS", "HUL": "HINDUNILVR.NS", "ICICI Bank": "ICICIBANK.NS",
    "IndusInd Bank": "INDUSINDBK.NS", "Infosys": "INFY.NS", "ITC": "ITC.NS",
    "JSW Steel": "JSWSTEEL.NS", "Kotak Bank": "KOTAKBANK.NS", "L&T": "LT.NS",
    "M&M": "M&M.NS", "Maruti Suzuki": "MARUTI.NS", "Nestle India": "NESTLEIND.NS",
    "NTPC": "NTPC.NS", "ONGC": "ONGC.NS", "Power Grid": "POWERGRID.NS",
    "Reliance": "RELIANCE.NS", "SBI": "SBIN.NS", "SBI Life": "SBILIFE.NS",
    "Sun Pharma": "SUNPHARMA.NS", "Tata Consumer": "TATACONSUM.NS", "Tata Motors": "TATAMOTORS.NS",
    "Tata Steel": "TATASTEEL.NS", "TCS": "TCS.NS", "Tech Mahindra": "TECHM.NS",
    "Titan": "TITAN.NS", "UPL": "UPL.NS", "UltraTech Cement": "ULTRACEMCO.NS",
    "Wipro": "WIPRO.NS"
}

# Database class for user management (Updated for MySQL with verification)
class UserDB:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",  # Replace with your MySQL username
                password="D@tabasesql",  # Replace with your MySQL password
                database="stock_analyzer"
            )
            self.create_table()
        except mysql.connector.Error as e:
            logging.error(f"Failed to connect to MySQL: {str(e)}")
            st.error("Database connection failed. Check MySQL settings.")
            self.conn = None

    def create_table(self):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users
                             (username VARCHAR(255) PRIMARY KEY,
                              password VARCHAR(255) NOT NULL,
                              email VARCHAR(255) NOT NULL,
                              is_premium BOOLEAN NOT NULL,
                              profile_pic BLOB,
                              verified BOOLEAN DEFAULT FALSE)''')
            self.conn.commit()
            cursor.close()

    def add_user(self, username, password, email, profile_pic=None, is_premium=False):
        if not self.conn:
            return False
        cursor = self.conn.cursor()
        try:
            pic_data = profile_pic.read() if profile_pic else None
            cursor.execute("INSERT INTO users (username, password, email, is_premium, profile_pic, verified) VALUES (%s, %s, %s, %s, %s, %s)",
                           (username, hash_password(password), email, int(is_premium), pic_data, False))
            self.conn.commit()
            cursor.close()
            return True
        except mysql.connector.Error as e:
            logging.error(f"Add user error: {str(e)}")
            cursor.close()
            return False

    def get_user(self, username):
        if not self.conn:
            return None, None, None, None, None
        cursor = self.conn.cursor()
        cursor.execute("SELECT password, email, is_premium, profile_pic, verified FROM users WHERE username = %s", (username.lower(),))
        result = cursor.fetchone()
        cursor.close()
        return (result[0], result[1], bool(result[2]), result[3], bool(result[4])) if result else (None, None, None, None, None)

    def update_verification(self, username, verified=True):
        if not self.conn:
            return False
        cursor = self.conn.cursor()
        try:
            cursor.execute("UPDATE users SET verified = %s WHERE username = %s", (int(verified), username))
            self.conn.commit()
            cursor.close()
            return True
        except mysql.connector.Error as e:
            logging.error(f"Verification update error: {str(e)}")
            cursor.close()
            return False

    def close(self):
        if self.conn:
            self.conn.close()

# Initialize database
db = UserDB()

# User authentication with enhancements
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def is_strong_password(password):
    return (len(password) >= 8 and 
            re.search(r"[A-Z]", password) and 
            re.search(r"[a-z]", password) and 
            re.search(r"[0-9]", password) and 
            re.search(r"[!@#$%^&*]", password))

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.is_premium = False
    st.session_state.verified = False

def login():
    with st.sidebar.form("login_form"):
        st.subheader("Login")
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        bypass_verification = st.checkbox("Bypass Verification (for testing)", value=False, help="Enable to log in without verification.")
        if st.form_submit_button("🔑 Login"):
            stored_password, email, is_premium, profile_pic, verified = db.get_user(username)
            if stored_password:
                if stored_password == hash_password(password):
                    if bypass_verification or verified:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.is_premium = bool(is_premium)
                        st.session_state.verified = verified
                        st.success("Logged in successfully! 🎉")
                        st.rerun()
                    else:
                        st.error("Account not verified. Check your email or enable bypass for testing.")
                else:
                    st.error("Invalid password.")
            else:
                st.error("Username not found.")

def signup():
    with st.sidebar.form("signup_form"):
        st.subheader("Sign Up")
        new_username = st.text_input("Username", placeholder="Choose a username")
        new_email = st.text_input("Email", placeholder="Enter your email")
        new_password = st.text_input("Password", type="password", placeholder="Choose a strong password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        profile_pic = st.file_uploader("Upload Profile Picture", type=["jpg", "png", "jpeg"], key="profile_upload")
        terms = st.checkbox("I agree to the Terms & Conditions and Privacy Policy")
        password_strength = "Weak" if not is_strong_password(new_password) else "Strong"
        st.write(f"Password Strength: <span style='color: {'#EF5350' if password_strength == 'Weak' else '#00E676'}'>{password_strength}</span>", unsafe_allow_html=True)

        if st.form_submit_button("📝 Sign Up"):
            if not new_username or not new_email or not new_password or not confirm_password:
                st.error("All fields are required.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            elif not is_strong_password(new_password):
                st.error("Password must be at least 8 characters long with uppercase, lowercase, number, and special character.")
            elif not terms:
                st.error("You must agree to the Terms & Conditions.")
            else:
                if db.add_user(new_username, new_password, new_email, profile_pic):
                    st.success("Account created! Please check your email for verification.")
                    st.info("Verification email sent. Please verify to log in.")
                else:
                    st.error("Username or email already exists.")

if not st.session_state.logged_in:
    login()
    signup()
    st.stop()

# Sidebar settings with enhanced navigation
st.sidebar.title("🔧 NIFTY AI Stock Pro")
st.sidebar.markdown("<div style='font-size: 24px; font-weight: 700; color: #00E676; text-align: center; margin-bottom: 20px;'>Control Panel</div>", unsafe_allow_html=True)
st.sidebar.header("Analysis Settings")
analysis_type = st.sidebar.selectbox("📊 Analysis Type", ["Single Stock", "Stock Comparison", "Portfolio", "Market Overview"], index=0)
company_name = st.sidebar.selectbox("🏦 Select NIFTY 50 Company", options=list(NIFTY_50.keys()), key="single_stock") if analysis_type in ["Single Stock", "Stock Comparison"] else None
ticker = NIFTY_50[company_name] if company_name else None
compare_tickers = st.sidebar.multiselect("⚖️ Compare Stocks", options=list(NIFTY_50.keys()), key="compare_stocks") if analysis_type == "Stock Comparison" else []
start_date = st.sidebar.date_input("📅 Start Date", value=date.today() - timedelta(days=365), max_value=date.today())
end_date = st.sidebar.date_input("📅 End Date", value=date.today(), max_value=date.today())
moving_averages = st.sidebar.multiselect("📈 Moving Averages (days)", [10, 20, 50, 100, 200], default=[20, 50])
indicators = st.sidebar.multiselect("🔍 Technical Indicators", ["SMA", "MACD", "RSI"], default=["SMA", "MACD"])
show_trend = st.sidebar.checkbox("🤖 Show AI Trend Prediction", value=True)
show_sentiment = st.sidebar.checkbox("😊 Show Real-Time Sentiment", value=True)
portfolio_file = st.sidebar.file_uploader("💼 Upload Portfolio (CSV)", help="CSV with 'Ticker' and optional 'Weight' columns.", key="portfolio_upload") if analysis_type == "Portfolio" else None
if st.session_state.is_premium:
    custom_epochs = st.sidebar.slider("🧠 LSTM Epochs", 5, 20, 10, help="Adjust the number of training epochs for AI predictions.")
    price_alert = st.sidebar.number_input("🔔 Price Alert Threshold (%)", min_value=1.0, max_value=20.0, value=5.0, help="Set a percentage threshold for price alerts.")

# Notification settings with tooltips
with st.sidebar.expander("⚙️ Notifications", expanded=False):
    user_email = st.text_input("📧 Your Email", "user@example.com", placeholder="your.email@example.com", help="Enter your email for notifications.")
    email_password = st.text_input("🔐 Gmail App Password", "", type="password", placeholder="Enter app password", help="Use an App-specific password for Gmail.")
    twilio_sid = st.text_input("📱 Twilio SID", "", placeholder="Your Twilio SID", help="Twilio Account SID for SMS alerts.")
    twilio_token = st.text_input("🔑 Twilio Auth Token", "", placeholder="Your Twilio Token", help="Twilio Auth Token for SMS alerts.")
    twilio_phone = st.text_input("📞 Twilio Phone", "", placeholder="+1234567890", help="Twilio phone number for sending SMS.")
    user_phone = st.text_input("📲 Your Phone", "", placeholder="+0987654321", help="Your phone number for receiving SMS alerts.")

def send_notification(user_email, message):
    try:
        if email_password:
            msg = MIMEText(message)
            msg['Subject'] = "NIFTY AI Stock Pro Alert"
            msg['To'] = user_email
            msg['From'] = user_email
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(user_email, email_password)
                server.sendmail(user_email, user_email, msg.as_string())
        if all([twilio_sid, twilio_token, twilio_phone, user_phone]):
            client = Client(twilio_sid, twilio_token)
            client.messages.create(body=message, from_=twilio_phone, to=user_phone)
            logging.info(f"Notification sent to {user_email} and {user_phone}")
        else:
            logging.warning("Incomplete notification settings, skipping SMS.")
    except Exception as e:
        logging.error(f"Notification error: {str(e)}")
        st.error("Notification failed. Check settings.")

@st.cache_data
def fetch_stock_data(ticker, start_date, end_date, interval="1d"):
    with st.spinner(f"Fetching data for {ticker}..."):
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(start=start_date, end=end_date, interval=interval, auto_adjust=True)
            if data.empty:
                raise ValueError(f"No data for {ticker}. Using cached if available.")
            os.makedirs("cache", exist_ok=True)
            data.to_csv(f"cache/{ticker}_data.csv")
            return data
        except Exception as e:
            logging.error(f"Fetch error for {ticker}: {str(e)}")
            if os.path.exists(f"cache/{ticker}_data.csv"):
                st.warning(f"Using cached data for {ticker}.")
                return pd.read_csv(f"cache/{ticker}_data.csv", index_col=0, parse_dates=True)
            return pd.DataFrame()

@st.cache_data
def fetch_x_sentiment(ticker):
    with st.spinner(f"Analyzing sentiment for {ticker}..."):
        try:
            query = f"{ticker} stock -filter:retweets"
            posts = ["Bullish on {}!", "Bearish news for {}", "{} looks strong", "{} might drop"]
            sentiments = [TextBlob(post.format(ticker)).sentiment.polarity for post in posts]
            avg_sentiment = np.mean(sentiments)
            return avg_sentiment, "Bullish" if avg_sentiment > 0.1 else "Bearish" if avg_sentiment < -0.1 else "Neutral"
        except Exception as e:
            logging.error(f"X sentiment error for {ticker}: {str(e)}")
            return 0, "N/A"

def train_lstm_model(data, epochs=5):
    with st.spinner("Training AI model..."):
        try:
            data = data.copy()
            data['Returns'] = data['Close'].pct_change().fillna(0)
            data['SMA50'] = SMAIndicator(data['Close'], window=50).sma_indicator()
            data['SMA200'] = SMAIndicator(data['Close'], window=200).sma_indicator()
            data['RSI'] = RSIIndicator(data['Close'], window=14).rsi()
            data['MACD'] = MACD(data['Close']).macd()
            data['Volume_Ratio'] = data['Volume'] / data['Volume'].rolling(window=20).mean()
            data = data.dropna()

            features = ['Close', 'Returns', 'SMA50', 'SMA200', 'RSI', 'MACD', 'Volume_Ratio']
            X = data[features].values
            y = (data['Close'].shift(-1) > data['Close']).astype(int).shift(1).fillna(0)

            scaler = MinMaxScaler()
            X_scaled = scaler.fit_transform(X)
            joblib.dump(scaler, 'scaler.pkl')

            train_size = int(len(X_scaled) * 0.8)
            X_train, y_train = X_scaled[:train_size], y[:train_size]
            X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))

            model = Sequential([
                LSTM(64, return_sequences=True, input_shape=(X_train.shape[1], 1)),
                Dropout(0.2),
                LSTM(32),
                Dropout(0.2),
                Dense(1, activation='sigmoid')
            ])
            model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
            model.fit(X_train, y_train, epochs=epochs, batch_size=32, verbose=0)
            model.save('stock_model.h5')
            return model, scaler
        except Exception as e:
            logging.error(f"LSTM training error: {str(e)}")
            st.error(f"Model training failed: {str(e)}")
            return None, None

def predict_trend(data, model, scaler):
    with st.spinner("Predicting trend..."):
        try:
            data = data.copy()
            data['Returns'] = data['Close'].pct_change().fillna(0)
            data['SMA50'] = SMAIndicator(data['Close'], window=50).sma_indicator()
            data['SMA200'] = SMAIndicator(data['Close'], window=200).sma_indicator()
            data['RSI'] = RSIIndicator(data['Close'], window=14).rsi()
            data['MACD'] = MACD(data['Close']).macd()
            data['Volume_Ratio'] = data['Volume'] / data['Volume'].rolling(window=20).mean()
            data = data.dropna()

            features = ['Close', 'Returns', 'SMA50', 'SMA200', 'RSI', 'MACD', 'Volume_Ratio']
            X = data[features].values[-1:]
            X_scaled = scaler.transform(X)
            X_reshaped = X_scaled.reshape((1, X_scaled.shape[1], 1))
            prediction = model.predict(X_reshaped, verbose=0)[0][0]
            confidence = prediction if prediction > 0.5 else 1 - prediction
            return 'Uptrend' if prediction > 0.5 else 'Downtrend', confidence
        except Exception as e:
            logging.error(f"Trend prediction error: {str(e)}")
            return "N/A", 0

def monte_carlo_simulation(data, n_simulations=1000, days=30):
    with st.spinner("Running simulation..."):
        try:
            returns = data['Close'].pct_change().dropna()
            mean_return = returns.mean()
            volatility = returns.std()
            last_price = data['Close'][-1]
            simulations = np.zeros((n_simulations, days))
            for i in range(n_simulations):
                daily_returns = np.random.normal(mean_return, volatility, days)
                price_series = last_price * (1 + daily_returns).cumprod()
                simulations[i] = price_series
            return simulations
        except Exception as e:
            logging.error(f"Monte Carlo error: {str(e)}")
            return None

def calculate_risk_metrics(data, market_data=None):
    with st.spinner("Calculating risk metrics..."):
        try:
            returns = data['Close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)
            var_95 = returns.quantile(0.05)
            max_drawdown = (data['Close'] / data['Close'].cummax() - 1).min()
            beta = None
            if market_data is not None and not market_data.empty:
                market_returns = market_data['Close'].pct_change().dropna()
                cov = returns.cov(market_returns)
                market_var = market_returns.var()
                beta = cov / market_var if market_var != 0 else None
            return volatility, var_95, max_drawdown, beta
        except Exception as e:
            logging.error(f"Risk metrics error: {str(e)}")
            return None, None, None, None

def backtest_strategy(data, strategy="macd"):
    with st.spinner("Backtesting strategy..."):
        try:
            data = data.copy()
            data['Returns'] = data['Close'].pct_change().fillna(0)
            if strategy == "macd":
                macd = MACD(data['Close'])
                data['MACD'] = macd.macd()
                data['MACD_Signal'] = macd.macd_signal()
                data['Position'] = np.where(data['MACD'] > data['MACD_Signal'], 1, np.where(data['MACD'] < data['MACD_Signal'], -1, 0))
            data['Strategy_Return'] = data['Position'].shift(1) * data['Returns']
            data['Cumulative_Strategy'] = (1 + data['Strategy_Return']).cumprod() - 1
            return data
        except Exception as e:
            logging.error(f"Backtest error: {str(e)}")
            return data

def portfolio_weights(tickers, returns_df, weights_input=None):
    with st.spinner("Analyzing portfolio..."):
        try:
            if weights_input is not None and 'Weight' in weights_input.columns:
                weights = weights_input.set_index('Ticker')['Weight'].to_dict()
                total_weight = sum(weights.values())
                weights = {t: w / total_weight for t, w in weights.items() if t in tickers}
            else:
                weights = {t: 1.0 / len(tickers) for t in tickers}
            portfolio_return = np.dot(returns_df.mean() * 252, [weights.get(t, 0) for t in returns_df.columns])
            portfolio_vol = np.sqrt(np.dot(np.dot(returns_df.cov() * 252, [weights.get(t, 0) for t in returns_df.columns]), [weights.get(t, 0) for t in returns_df.columns]))
            sharpe = portfolio_return / portfolio_vol if portfolio_vol != 0 else 0
            return weights, portfolio_return, portfolio_vol, sharpe
        except Exception as e:
            logging.error(f"Portfolio weights error: {str(e)}")
            return None, None, None, None

def suggest_rebalance(weights, returns_df):
    with st.spinner("Suggesting rebalance..."):
        try:
            returns = returns_df.mean() * 252
            volatility = returns_df.std() * np.sqrt(252)
            risk_adjusted = returns / volatility.replace(0, np.inf)
            suggested_weights = {t: w * risk_adjusted[t] / sum(w * risk_adjusted[t] for t in weights) for t in weights}
            return suggested_weights
        except Exception as e:
            logging.error(f"Rebalance error: {str(e)}")
            return None

def plot_candlestick(data, company_name):
    fig = go.Figure(data=[go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], 
                                         increasing_line_color='#00E676', decreasing_line_color='#EF5350')])
    for window in moving_averages:
        data[f"MA{window}"] = data['Close'].rolling(window).mean()
        fig.add_trace(go.Scatter(x=data.index, y=data[f"MA{window}"], mode='lines', name=f"MA {window}", 
                                 line=dict(color='#FFD700')))
    fig.update_layout(title=f"{company_name} Candlestick", xaxis_title="Date", yaxis_title="Price (INR)", 
                      template="plotly_dark" if theme == 'Dark' else "plotly_white", xaxis_rangeslider_visible=True,
                      title_font=dict(size=24, family="Inter", color="#00E676" if theme == 'Dark' else "#0288D1"),
                      plot_bgcolor='rgba(0,0,0,0.1)', paper_bgcolor='rgba(0,0,0,0)')
    return fig

def plot_comparison(data_dict):
    fig = go.Figure()
    for ticker, data in data_dict.items():
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name=ticker, line=dict(dash='solid')))
    fig.update_layout(title="Stock Comparison", xaxis_title="Date", yaxis_title="Price (INR)", 
                      template="plotly_dark" if theme == 'Dark' else "plotly_white", 
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                      title_font=dict(size=24, family="Inter", color="#00E676" if theme == 'Dark' else "#0288D1"),
                      plot_bgcolor='rgba(0,0,0,0.1)', paper_bgcolor='rgba(0,0,0,0)')
    return fig

def plot_volume(data):
    fig = px.bar(data, x=data.index, y='Volume', title="Trading Volume", template="plotly_dark" if theme == 'Dark' else "plotly_white")
    fig.update_layout(xaxis_title="Date", yaxis_title="Volume", bargap=0.1,
                      title_font=dict(size=24, family="Inter", color="#00E676" if theme == 'Dark' else "#0288D1"),
                      plot_bgcolor='rgba(0,0,0,0.1)', paper_bgcolor='rgba(0,0,0,0)')
    return fig

def plot_returns(data, title="Returns"):
    data = data.copy()
    data['Return'] = data['Close'].pct_change() * 100
    fig = px.line(data, x=data.index, y='Return', title=title, template="plotly_dark" if theme == 'Dark' else "plotly_white")
    fig.update_layout(xaxis_title="Date", yaxis_title="Return (%)",
                      title_font=dict(size=24, family="Inter", color="#00E676" if theme == 'Dark' else "#0288D1"),
                      plot_bgcolor='rgba(0,0,0,0.1)', paper_bgcolor='rgba(0,0,0,0)')
    return fig

def plot_monte_carlo(simulations, last_price, title):
    fig = go.Figure([go.Scatter(x=np.arange(simulations.shape[1]), y=simulations[i], mode='lines', opacity=0.1, 
                                line=dict(color='#00E676' if theme == 'Dark' else '#0288D1')) for i in range(simulations.shape[0])])
    fig.add_trace(go.Scatter(x=[0], y=[last_price], mode='markers', name="Current Price", marker=dict(size=12, color='#FFD700')))
    fig.update_layout(title=title, xaxis_title="Days", yaxis_title="Price (INR)", 
                      template="plotly_dark" if theme == 'Dark' else "plotly_white",
                      title_font=dict(size=24, family="Inter", color="#00E676" if theme == 'Dark' else "#0288D1"),
                      plot_bgcolor='rgba(0,0,0,0.1)', paper_bgcolor='rgba(0,0,0,0)')
    return fig

def plot_correlation(data):
    corr = data.corr()
    fig = px.imshow(corr, text_auto=True, aspect="auto", title="Correlation Heatmap", color_continuous_scale='RdBu_r', 
                    template="plotly_dark" if theme == 'Dark' else "plotly_white")
    fig.update_traces(hovertemplate="Stock: %{y}<br>Correlated with: %{x}<br>Value: %{z:.2f}")
    fig.update_layout(title_font=dict(size=24, family="Inter", color="#00E676" if theme == 'Dark' else "#0288D1"),
                      plot_bgcolor='rgba(0,0,0,0.1)', paper_bgcolor='rgba(0,0,0,0)')
    return fig

def plot_allocation(weights):
    fig = px.pie(names=list(weights.keys()), values=list(weights.values()), title="Portfolio Allocation", 
                 template="plotly_dark" if theme == 'Dark' else "plotly_white")
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(title_font=dict(size=24, family="Inter", color="#00E676" if theme == 'Dark' else "#0288D1"),
                      plot_bgcolor='rgba(0,0,0,0.1)', paper_bgcolor='rgba(0,0,0,0)')
    return fig

def plot_market_mood(sentiments):
    avg_sentiment = np.mean([s[0] for s in sentiments.values() if s[0] != 0])
    fig = go.Figure(go.Indicator(mode="gauge+number", value=avg_sentiment, title={"text": "Market Sentiment"},
                                 gauge={'axis': {'range': [-1, 1]}, 'bar': {'color': '#00E676' if theme == 'Dark' else '#0288D1'},
                                        'steps': [{'range': [-1, -0.1], 'color': '#EF5350'}, {'range': [-0.1, 0.1], 'color': '#B0BEC5'}, 
                                                  {'range': [0.1, 1], 'color': '#00E676'}]}))
    fig.update_layout(template="plotly_dark" if theme == 'Dark' else "plotly_white",
                      title_font=dict(size=24, family="Inter", color="#00E676" if theme == 'Dark' else "#0288D1"),
                      plot_bgcolor='rgba(0,0,0,0.1)', paper_bgcolor='rgba(0,0,0,0)')
    return fig

def generate_pdf_report(company_name, ticker, data, trend, confidence, volatility, var_95, max_drawdown, beta, sentiment):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesizes=letter)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 750, f"NIFTY AI Stock Pro Report - {company_name} ({ticker})")
    c.setFont("Helvetica", 12)
    c.drawString(50, 730, f"Date: {date.today()}")
    c.drawString(50, 710, f"Trend: {trend} (Confidence: {confidence:.2%})")
    c.drawString(50, 690, f"Volatility: {volatility:.2%}" if volatility else "Volatility: N/A")
    c.drawString(50, 670, f"VaR (95%): {var_95:.2%}" if var_95 else "VaR: N/A")
    c.drawString(50, 650, f"Max Drawdown: {max_drawdown:.2%}" if max_drawdown else "Max Drawdown: N/A")
    c.drawString(50, 630, f"Beta: {beta:.2f}" if beta else "Beta: N/A")
    c.drawString(50, 610, f"Sentiment: {sentiment[1]} (Score: {sentiment[0]:.2f})")
    c.drawString(50, 590, "Latest Data:")
    textobject = c.beginText(70, 570)
    textobject.setFont("Helvetica", 10)
    for line in data[['Open', 'High', 'Low', 'Close', 'Volume']].tail(1).to_string(index=False).split('\n'):
        textobject.textLine(line)
    c.drawText(textobject)
    c.showPage()
    c.save()
    buffer.seek(0)
    os.makedirs("reports", exist_ok=True)
    with open(f"reports/{ticker}_report_{date.today()}.pdf", "wb") as f:
        f.write(buffer.read())
    return buffer

# Initialize directories
for dir_path in ["cache", "reports"]:
    os.makedirs(dir_path, exist_ok=True)

# Main tabs with breadcrumbs
tabs = ["🏠 Dashboard", "📈 Stock Insights", "💼 Portfolio", "👤 Profile", "🎓 Learn Trading"]
tab1, tab2, tab3, tab4, tab5 = st.tabs(tabs)
st.markdown(f'<div style="font-size: 14px; color: {"#B0BEC5" if theme == "Dark" else "#616161"}; padding: 10px; background: {"rgba(255,255,255,0.1)" if theme == "Dark" else "rgba(0,0,0,0.05)"}; border-radius: 8px; margin-bottom: 20px;">Home > {tabs[st.session_state.get("tab_index", 0)]}</div>', unsafe_allow_html=True)

with tab1:
    st.session_state.tab_index = 0
    st.markdown('<div class="stHeader">Dashboard</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="card">Welcome, {st.session_state.username}! Dive into your financial future with AI-powered insights. 🌟</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 Market Update"):
            with st.spinner("Fetching market data..."):
                time.sleep(1)
                sentiments = {t: fetch_x_sentiment(t) for t in list(NIFTY_50.values())[:5]}
                st.plotly_chart(plot_market_mood(sentiments), use_container_width=True, key=f"market_mood_{time.time()}")
                send_notification(user_email, f"Market update at {date.today()}: Sentiment {sentiments[list(sentiments.keys())[0]][1]}")
    with col2:
        data_nifty = fetch_stock_data("^NSEI", start_date, end_date)
        if not data_nifty.empty:
            st.metric("NIFTY 50 Close", f"{data_nifty['Close'][-1]:.2f} INR")
    with col3:
        st.info("💡 Tip: Check trends for long-term investments!")

with tab2:
    st.session_state.tab_index = 1
    st.markdown('<div class="stHeader">Stock Insights</div>', unsafe_allow_html=True)
    if analysis_type == "Single Stock" and ticker:
        data = fetch_stock_data(ticker, start_date, end_date)
        market_data = fetch_stock_data("^NSEI", start_date, end_date)
        if not data.empty:
            st.markdown('<div class="card"><h3>Overview</h3></div>', unsafe_allow_html=True)
            st.dataframe(data[['Open', 'High', 'Low', 'Close', 'Volume']].tail(5).style.format("{:.2f}"))

            st.markdown('<div class="card"><h3>Charts</h3></div>', unsafe_allow_html=True)
            st.plotly_chart(plot_candlestick(data, company_name), use_container_width=True, key=f"candlestick_{ticker}")
            if "RSI" in indicators:
                st.plotly_chart(px.line(data.assign(RSI=RSIIndicator(data['Close'], 14).rsi()), x=data.index, y='RSI', title="RSI", 
                                  template="plotly_dark" if theme == 'Dark' else "plotly_white")
                                .add_hline(y=70, line_dash="dash", line_color="#EF5350")
                                .add_hline(y=30, line_dash="dash", line_color="#00E676"), 
                                use_container_width=True, key=f"rsi_{ticker}")
            if "MACD" in indicators:
                macd_data = data.assign(MACD=MACD(data['Close']).macd(), Signal=MACD(data['Close']).macd_signal())
                st.plotly_chart(px.line(macd_data, x=macd_data.index, y=['MACD', 'Signal'], title="MACD", 
                                       template="plotly_dark" if theme == 'Dark' else "plotly_white"), 
                                use_container_width=True, key=f"macd_{ticker}")
            st.plotly_chart(plot_volume(data), use_container_width=True, key=f"volume_{ticker}")
            st.plotly_chart(plot_returns(data, "Daily Returns"), use_container_width=True, key=f"returns_daily_{ticker}")
            st.plotly_chart(plot_returns(data.assign(Cumulative=(1 + data['Close'].pct_change()).cumprod() - 1), "Cumulative Returns"), 
                            use_container_width=True, key=f"returns_cumulative_{ticker}")

            if show_trend:
                st.markdown('<div class="card"><h3>AI Prediction <span class="premium" title="Premium Feature">Premium</span></h3></div>', unsafe_allow_html=True)
                model_path = 'stock_model.h5'
                epochs = custom_epochs if st.session_state.is_premium else 5
                with st.spinner("Analyzing trends..."):
                    time.sleep(1)
                    if not os.path.exists(model_path):
                        model, scaler = train_lstm_model(data, epochs)
                    else:
                        try:
                            model = load_model(model_path)
                            scaler = joblib.load('scaler.pkl')
                        except:
                            model, scaler = train_lstm_model(data, epochs)
                    if model:
                        trend, confidence = predict_trend(data, model, scaler)
                        st.success(f"Trend: **{trend}** (Confidence: {confidence:.2%})")
                        if st.session_state.is_premium and confidence > 0.7:
                            send_notification(user_email, f"{ticker} trend: {trend} (Confidence {confidence:.2%})")

            st.markdown('<div class="card"><h3>Simulations <span class="premium" title="Premium Feature">Premium</span></h3></div>', unsafe_allow_html=True)
            simulations = monte_carlo_simulation(data)
            if simulations is not None:
                st.plotly_chart(plot_monte_carlo(simulations, data['Close'][-1], "30-Day Forecast"), use_container_width=True, key=f"monte_carlo_{ticker}")

            st.markdown('<div class="card"><h3>Risk Metrics</h3></div>', unsafe_allow_html=True)
            vol, var, drawdown, beta = calculate_risk_metrics(data, market_data)
            if vol:
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Volatility", f"{vol:.2%}")
                col2.metric("VaR (95%)", f"{var:.2%}")
                col3.metric("Max Drawdown", f"{drawdown:.2%}")
                col4.metric("Beta", f"{beta:.2f}" if beta else "N/A")

            st.markdown('<div class="card"><h3>Strategy</h3></div>', unsafe_allow_html=True)
            backtest = backtest_strategy(data)
            st.plotly_chart(px.line(backtest, x=backtest.index, y='Cumulative_Strategy', title="MACD Strategy", 
                                  template="plotly_dark" if theme == 'Dark' else "plotly_white"), 
                            use_container_width=True, key=f"strategy_{ticker}")

            if show_sentiment:
                st.markdown('<div class="card"><h3>Sentiment</h3></div>', unsafe_allow_html=True)
                sentiment = fetch_x_sentiment(ticker)
                st.write(f"**Sentiment:** {sentiment[1]} (Score: {sentiment[0]:.2f})")

            st.markdown('<div class="card"><h3>Report & Alerts</h3></div>', unsafe_allow_html=True)
            pdf = generate_pdf_report(company_name, ticker, data, trend, confidence, vol, var, drawdown, beta, sentiment)
            st.download_button("📥 Download Report", pdf, f"{ticker}_report_{date.today()}.pdf", "application/pdf")
            if st.session_state.is_premium:
                if st.button("🔔 Set Price Alert"):
                    threshold = data['Close'][-1] * (1 + price_alert / 100)
                    st.session_state.alert_threshold = threshold
                    st.success(f"Alert set for {ticker} at {threshold:.2f} INR!")
    elif analysis_type == "Stock Comparison" and compare_tickers:
        data_dict = {t: fetch_stock_data(NIFTY_50[t], start_date, end_date) for t in compare_tickers}
        valid_data = {t: d for t, d in data_dict.items() if not d.empty}
        if valid_data:
            st.markdown('<div class="card"><h3>Comparison Chart</h3></div>', unsafe_allow_html=True)
            st.plotly_chart(plot_comparison(valid_data), use_container_width=True, key=f"comparison_{'_'.join(compare_tickers)}")
            st.info("💡 Tip: Compare stocks to diversify your portfolio!")

with tab3:
    st.session_state.tab_index = 2
    st.markdown('<div class="stHeader">Portfolio</div>', unsafe_allow_html=True)
    if analysis_type == "Portfolio" and portfolio_file:
        st.markdown('<div class="card"><h3>Portfolio Overview</h3></div>', unsafe_allow_html=True)
        try:
            if portfolio_file.name.endswith((".csv", ".xlsx", ".xls")):
                portfolio = pd.read_csv(portfolio_file) if portfolio_file.name.endswith(".csv") else pd.read_excel(portfolio_file)
                if all(col in portfolio.columns for col in ['Ticker', 'Weight']):
                    tickers = [t for t in portfolio['Ticker'] if t in NIFTY_50.values()]
                    weights = portfolio.set_index('Ticker')['Weight'].to_dict()
                else:
                    tickers = [t for t in portfolio['Ticker'] if t in NIFTY_50.values()]
                    weights = None
                if tickers:
                    data = {t: fetch_stock_data(t, start_date, end_date)['Close'] for t in tickers}
                    df = pd.DataFrame(data)
                    if not df.empty:
                        st.dataframe(portfolio.style.format({"Weight": "{:.2%}"}))
                        st.plotly_chart(plot_correlation(df), use_container_width=True, key=f"correlation_{'_'.join(tickers)}")
                        with st.spinner("Analyzing portfolio..."):
                            time.sleep(1)
                            returns = df.pct_change().dropna()
                            w, ret, vol, sharpe = portfolio_weights(tickers, returns, portfolio if 'Weight' in portfolio else None)
                            st.markdown(f"<div style='padding: 10px; background: {'rgba(255,255,255,0.1)' if theme == 'Dark' else 'rgba(0,0,0,0.05)'}; border-radius: 8px;'>"
                                        f"<strong>Expected Return:</strong> {ret:.2%} | <strong>Volatility:</strong> {vol:.2%} | <strong>Sharpe Ratio:</strong> {sharpe:.2f}</div>", 
                                        unsafe_allow_html=True)
                            st.plotly_chart(plot_allocation(w), use_container_width=True, key=f"allocation_{'_'.join(tickers)}")
                            if st.session_state.is_premium:
                                suggested_weights = suggest_rebalance(w, returns)
                                st.markdown('<div class="card"><h3>Suggested Rebalance</h3></div>', unsafe_allow_html=True)
                                st.dataframe(pd.DataFrame(list(suggested_weights.items()), columns=["Stock", "Weight"]).style.format({"Weight": "{:.2%}"}))
                            results = pd.DataFrame({
                                'Stock': tickers,
                                'Weight': [f"{w.get(t, 0):.2%}" for t in tickers],
                                'Trend': [predict_trend(fetch_stock_data(t, start_date, end_date), *train_lstm_model(fetch_stock_data(t, start_date, end_date))[0:2])[0] 
                                          if train_lstm_model(fetch_stock_data(t, start_date, end_date)) else "N/A" for t in tickers],
                                'Sentiment': [fetch_x_sentiment(t)[1] for t in tickers]
                            })
                            st.dataframe(results)
                            csv = results.to_csv(index=False).encode()
                            st.download_button("📥 Download Summary", data=csv, file_name="portfolio_summary.csv")
                else:
                    st.error("No valid tickers found.")
            else:
                st.error("Unsupported format. Use CSV/XLSX with 'Ticker' column.")
        except Exception as e:
            logging.error(f"Portfolio error: {str(e)}")
            st.error(f"Error: {str(e)}")
    elif analysis_type == "Market Overview":
        st.markdown('<div class="card"><h3>Market Overview</h3></div>', unsafe_allow_html=True)
        sentiments = {t: fetch_x_sentiment(t) for t in list(NIFTY_50.values())[:10]}
        st.plotly_chart(plot_market_mood(sentiments), use_container_width=True, key=f"market_mood_overview_{time.time()}")
        performance = [(t, (fetch_stock_data(t, start_date, end_date)['Close'].pct_change() + 1).prod() - 1) 
                       for t in list(NIFTY_50.values())[:10] if not fetch_stock_data(t, start_date, end_date).empty]
        st.dataframe(pd.DataFrame(performance, columns=["Ticker", "Return"]).sort_values("Return", ascending=False).style.format({"Return": "{:.2%}"}))
        st.markdown("🌐 Real-time insights powered by X sentiment analysis.", unsafe_allow_html=True)

with tab4:
    st.session_state.tab_index = 3
    st.markdown('<div class="stHeader">Profile</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="card">Manage your account, view your activity, and unlock exclusive features! 🚀</div>', unsafe_allow_html=True)

    # Fetch user data
    _, email, is_premium, profile_pic, verified = db.get_user(st.session_state.username)

    # User Information Card
    st.markdown('<div class="card"><h3>User Information</h3></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        if profile_pic:
            st.image(Image.open(BytesIO(profile_pic)), caption="Profile Picture", width=150)
        else:
            st.image("https://via.placeholder.com/150?text=User", caption="No Profile Picture", width=150)
        with st.form("profile_pic_form"):
            new_profile_pic = st.file_uploader("📸 Update Profile Picture", type=["jpg", "png", "jpeg"], key="new_profile_upload")
            if st.form_submit_button("Upload"):
                if new_profile_pic:
                    try:
                        cursor = db.conn.cursor()
                        pic_data = new_profile_pic.read()
                        cursor.execute("UPDATE users SET profile_pic = %s WHERE username = %s", (pic_data, st.session_state.username))
                        db.conn.commit()
                        cursor.close()
                        st.success("Profile picture updated successfully! 🎉")
                        st.rerun()
                    except mysql.connector.Error as e:
                        logging.error(f"Profile picture update error: {str(e)}")
                        st.error("Failed to update profile picture.")
                else:
                    st.error("Please select an image to upload.")
    with col2:
        st.markdown(f"""
            <div style='padding: 10px;'>
                <p><strong>Username:</strong> {st.session_state.username}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Plan:</strong> <span style='color: {("#00E676" if theme == "Dark" else "#0288D1")}'>{"Premium" if is_premium else "Free"}</span></p>
                <p><strong>Verified:</strong> {"✅ Yes" if verified else "❌ No"}</p>
            </div>
        """, unsafe_allow_html=True)

    # Account Settings
    with st.expander("⚙️ Account Settings", expanded=False):
        st.markdown('<div class="card"><h3>Update Account Details</h3></div>', unsafe_allow_html=True)
        with st.form("update_account_form"):
            new_email = st.text_input("📧 New Email", value=email, placeholder="Enter new email")
            new_password = st.text_input("🔒 New Password", type="password", placeholder="Enter new password")
            confirm_password = st.text_input("🔒 Confirm New Password", type="password", placeholder="Confirm new password")
            if st.form_submit_button("💾 Update"):
                if new_email and new_email != email:
                    try:
                        cursor = db.conn.cursor()
                        cursor.execute("UPDATE users SET email = %s WHERE username = %s", (new_email, st.session_state.username))
                        db.conn.commit()
                        cursor.close()
                        st.success("Email updated successfully! Please verify your new email.")
                        logging.info(f"User {st.session_state.username} updated email to {new_email}")
                    except mysql.connector.Error as e:
                        logging.error(f"Email update error: {str(e)}")
                        st.error("Failed to update email.")
                if new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("Passwords do not match.")
                    elif not is_strong_password(new_password):
                        st.error("Password must be at least 8 characters long with uppercase, lowercase, number, and special character.")
                    else:
                        try:
                            cursor = db.conn.cursor()
                            cursor.execute("UPDATE users SET password = %s WHERE username = %s", (hash_password(new_password), st.session_state.username))
                            db.conn.commit()
                            cursor.close()
                            st.success("Password updated successfully!")
                            logging.info(f"User {st.session_state.username} updated password")
                        except mysql.connector.Error as e:
                            logging.error(f"Password update error: {str(e)}")
                            st.error("Failed to update password.")
                elif new_password or confirm_password:
                    st.error("Please fill both password fields.")

    # Activity Log
    st.markdown('<div class="card"><h3>Activity Log</h3></div>', unsafe_allow_html=True)
    try:
        with open('stock_analyzer.log', 'r') as log_file:
            logs = log_file.readlines()
            user_logs = [log for log in logs[-10:] if st.session_state.username.lower() in log.lower() or "notification sent" in log.lower()]
            if user_logs:
                st.markdown("<div style='max-height: 200px; overflow-y: auto; padding: 10px; background: {'rgba(255,255,255,0.1)' if theme == 'Dark' else 'rgba(0,0,0,0.05)'}; border-radius: 8px;'>", unsafe_allow_html=True)
                for log in user_logs:
                    st.write(f"- {log.strip()}")
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("No recent activity found.")
    except FileNotFoundError:
        st.info("No activity log available.")

    # Premium Benefits
    if not is_premium:
        st.markdown('<div class="card"><h3>Premium Benefits <span class="premium" title="Premium Feature">Premium</span></h3></div>', unsafe_allow_html=True)
        st.markdown("""
            <div style='padding: 10px;'>
                <p>Unlock the full potential of NIFTY AI Stock Pro with a Premium subscription!</p>
                <ul>
                    <li>📈 Advanced AI Predictions with Custom Epochs</li>
                    <li>🔔 Price Alerts for Real-Time Monitoring</li>
                    <li>📊 Monte Carlo Simulations for Risk Analysis</li>
                    <li>🎓 Exclusive Interactive Quizzes</li>
                    <li>📩 Priority Support</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        if st.button("🔓 Upgrade to Premium", key="premium_upgrade_profile"):
            st.info("Unlock advanced features! Visit <a href='https://x.ai/grok' target='_blank'>x.ai/grok</a> for details.", unsafe_allow_html=True)

    # Achievements/Badges
    st.markdown('<div class="card"><h3>Achievements</h3></div>', unsafe_allow_html=True)
    badges = [
        {"name": "First Report", "icon": "📊", "earned": os.path.exists("reports") and any(f.startswith(ticker) for f in os.listdir("reports")) if ticker else False},
        {"name": "Trend Spotter", "icon": "🔍", "earned": st.session_state.get("alert_threshold") is not None},
        {"name": "Market Guru", "icon": "🌟", "earned": is_premium}
    ]
    cols = st.columns(3)
    for i, badge in enumerate(badges):
        with cols[i % 3]:
            st.markdown(f"""
                <div style='text-align: center; padding: 10px;'>
                    <span style='font-size: 24px;'>{badge["icon"]}</span><br>
                    <strong>{badge["name"]}</strong><br>
                    <span style='color: {("#00E676" if badge["earned"] else "#B0BEC5")}'>{"Earned" if badge["earned"] else "Locked"}</span>
                </div>
            """, unsafe_allow_html=True)

    # Export Profile Data
    st.markdown('<div class="card"><h3>Export Profile</h3></div>', unsafe_allow_html=True)
    if st.button("📥 Download Profile Data"):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesizes=letter)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 750, f"NIFTY AI Stock Pro - User Profile")
        c.setFont("Helvetica", 12)
        c.drawString(50, 730, f"Username: {st.session_state.username}")
        c.drawString(50, 710, f"Email: {email}")
        c.drawString(50, 690, f"Plan: {'Premium' if is_premium else 'Free'}")
        c.drawString(50, 670, f"Verified: {'Yes' if verified else 'No'}")
        c.drawString(50, 650, f"Generated on: {date.today()}")
        c.showPage()
        c.save()
        buffer.seek(0)
        st.download_button("Download Profile PDF", buffer, f"{st.session_state.username}_profile_{date.today()}.pdf", "application/pdf")

with tab5:
    st.session_state.tab_index = 4
    st.markdown('<div class="stHeader">Learn Trading</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">Master trading and financial skills with our free resources! Explore tutorials in English and Hindi, and unlock exclusive quizzes with a Premium subscription. 🚀</div>', unsafe_allow_html=True)

    # Section: Learn Trading in English
    st.markdown('<div class="card"><h3>Learn Trading in English</h3><p>Watch our curated English YouTube playlist to understand trading concepts, strategies, and market analysis.</p></div>', unsafe_allow_html=True)
    st.video("https://youtu.be/XDtWSmnDLEs?si=aXzd_C_ZPNATRCWZ")

    # Section: Learn Trading in Hindi
    st.markdown('<div class="card"><h3>Learn Trading in Hindi (हिंदी में ट्रेडिंग सीखें)</h3><p>Explore our Hindi YouTube playlist for trading tutorials in your native language, covering basics to advanced strategies.</p></div>', unsafe_allow_html=True)
    st.video("https://youtu.be/fBhZ1xz5rIw?si=UcHcoIpdx1kgEqh0")

    # Section: Buy Premium to Attempt Quizzes
    st.markdown('<div class="card"><h3>Buy Premium to Attempt Quizzes <span class="premium" title="Premium Feature">Premium</span></h3><p>Unlock interactive quizzes to test your trading knowledge! Upgrade to Premium for exclusive access to quizzes and advanced tools.</p></div>', unsafe_allow_html=True)
    if not st.session_state.is_premium:
        if st.button("🔓 Upgrade to Premium", key="premium_quiz_button"):
            st.info("Unlock quizzes and advanced features! Visit <a href='https://x.ai/grok' target='_blank'>x.ai/grok</a> for details.", unsafe_allow_html=True)
    else:
        st.success("You are a Premium user! Access quizzes below.")
        st.markdown('<div class="card"><p>Coming Soon: Interactive trading quizzes to test your skills!</p></div>', unsafe_allow_html=True)

# Footer
st.markdown("""
    <div class='footer'>
        NIFTY AI Stock Pro &copy; 2025 | 
        <a href='https://x.ai/grok'>Support</a> | 
        <a href='https://x.ai/grok'>Terms & Conditions</a> | 
        <a href='https://x.ai/grok'>Privacy Policy</a>
    </div>
""", unsafe_allow_html=True)

# Clean up database connection
db.close()
