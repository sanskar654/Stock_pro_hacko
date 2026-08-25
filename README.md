NIFTY AI Stock Pro 📈

Empowering Indian investors with AI-driven stock analysis and financial education.

NIFTY AI Stock Pro is a web application designed to make stock market investing accessible, data-driven, and educational for Indian users, focusing on the NIFTY 50 index. Built with Streamlit, MySQL, and AI-powered analytics, it offers real-time stock insights, portfolio management, and multilingual tutorials to boost financial literacy.

Project Overview

India’s financial literacy rate is only 27%, and many face barriers to stock market participation, especially in Tier 2/3 cities and rural areas. NIFTY AI Stock Pro addresses these challenges by providing:

AI-Powered Insights: Leverage LSTM models for trend predictions and Monte Carlo simulations for risk analysis.

User-Friendly Interface: A modern, responsive Streamlit UI with Dark/Light themes and interactive charts.

Financial Education: Free tutorials to empower users with trading knowledge.

Portfolio Optimization: Tools to analyze and rebalance portfolios for better returns.

Secure User Management: MySQL-backed user authentication with secure password hashing using bcrypt.

Societal Impact

Financial Inclusion: Makes investing approachable for non-urban and non-English-speaking users.

Literacy Boost: Multilingual resources bridge knowledge gaps.

Risk Reduction: AI-driven analytics and risk metrics help users make informed decisions.



🚀 Features

📊 Stock Analysis: Candlestick charts, technical indicators (SMA, MACD, RSI), and AI trend predictions for NIFTY 50 stocks.

💼 Portfolio Management: Upload CSV portfolios, view performance metrics (Sharpe Ratio, volatility), and get rebalancing suggestions.

🎓 Learn Trading: Free YouTube tutorials with premium interactive quizzes (coming soon).

🔔 Real-Time Alerts: Price notifications via email/SMS for premium users (mock implementation).

👤 User Profiles: Personalized accounts with profile pictures, activity logs, and achievement badges.

📥 Reports: Downloadable PDF reports summarizing stock analysis and user profiles.



📋 Prerequisites

Python 3.8+

MySQL Server (e.g., MySQL Community Server)

Git

A GitHub account and Personal Access Token (PAT) for repository access.

Optional: Gmail App Password and Twilio credentials for notifications.





🛠 Installation

Clone the Repository:


Set Up a Virtual Environment:

python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# For Windows: venv\Scripts\activate



Install Dependencies:

pip install -r requirements.txt

Configure MySQL:

Start MySQL server:

mysql.server start  # On macOS/Linux

Create a database named stock_analyzer:

CREATE DATABASE stock_analyzer;

Create a .env file in the project root:

MYSQL_USER=your_mysql_username
MYSQL_PASSWORD=your_mysql_password
MYSQL_HOST=localhost
MYSQL_DATABASE=stock_analyzer

Example:

MYSQL_USER=root
MYSQL_PASSWORD=D@tabasesql
MYSQL_HOST=localhost
MYSQL_DATABASE=stock_analyzer



Ensure .env is listed in .gitignore to avoid committing sensitive data.

Optional: Configure Notifications (for premium features):

Add Gmail and Twilio credentials to .env:

GMAIL_EMAIL=your.email@example.com
GMAIL_PASSWORD=your_gmail_app_password
TWILIO_SID=your_twilio_sid
TWILIO_TOKEN=your_twilio_token
TWILIO_PHONE=+1234567890
USER_PHONE=+0987654321

🚀 Usage





Run the Application:

streamlit run main.py

Open http://localhost:8501 in your browser.



Sign Up/Login:





Create an account with a username, email, and strong password.



Log in to access the dashboard, stock insights, portfolio tools, and learning resources.



Explore Features:





Dashboard: View market updates and NIFTY 50 trends.



Stock Insights: Analyze individual stocks or compare multiple NIFTY 50 stocks.



Portfolio: Upload a CSV with ticker symbols and weights for analysis.



Profile: Manage your account, view activity logs, and download profile data.



Learn Trading: Access free English and Hindi tutorials; premium users can attempt quizzes (coming soon).



Generate Reports:





Download PDF reports for stock analysis or user profiles from the respective tabs.

📂 Project Structure

nifty-ai-stock-pro/
├── main.py              # Main Streamlit application
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore file (excludes venv/, .env, cache/, etc.)
├── .env                # Environment variables (not committed)
├── cache/              # Cached stock data
├── reports/            # Generated PDF reports
└── README.md           # Project documentation

🤝 Contributing

Contributions are welcome! To contribute:





Fork the repository.



Create a feature branch:

git checkout -b feature/your-feature-name



Commit changes:

git commit -m "Add your feature description"



Push to your fork:

git push origin feature/your-feature-name



Open a Pull Request on GitHub.

Please follow the Code of Conduct and ensure code adheres to PEP 8 standards.

📚 Documentation

For detailed project insights, view our Google Docs documentation (replace with your actual link).


📜 License

This project is licensed under the MIT License. See LICENSE for details.



Built with Streamlit, yfinance, and TensorFlow.

Inspired by the mission to enhance financial literacy in India.

Thanks to contributors and open-source libraries.
#
