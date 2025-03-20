# Yale Trading Simulation Platform (YTSP)

A Robinhood-like full-stack web application for Yale students to simulate stock investments, manage financial portfolios, and interact with a community of peers.

## Features

### User Management
- Registration/login with Yale student ID and password
- Deposit/withdraw simulated funds

### Trading Features
- Search stocks by symbol/ticker
- View company information and stock trends
- Buy/sell stocks with real-time pricing
- Portfolio tracking and performance monitoring

### Social Features
- Follow other Yale students
- View public trading activities of people you follow
- Interact with trading posts through comments and reactions
- Public/private settings for your trading activities

## Tech Stack
- Backend: Python with Flask framework
- Database: SQLite (development) / PostgreSQL (production)
- API: Integration with financial data providers
- Authentication: Flask-Login with secure password handling

## Setup Instructions

1. Clone the repository
```
git clone [repository-url]
cd [repository-name]
```

2. Set up a virtual environment
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```
pip install -r requirements.txt
```

4. Set up environment variables
```
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database
```
flask db init
flask db migrate
flask db upgrade
```

6. Run the application
```
flask run
```

7. Access the application at http://localhost:5000

## Development

This is an MVP focused on backend functionality. Future iterations will improve the frontend/UI.

## Testing

Run tests with:
```
pytest
```

## Setting Up Stock Trading Functionality

The application uses Yahoo Finance (yfinance) for retrieving stock data, which doesn't require an API key. This means you can search for and trade stocks without any additional configuration.

### Searching for Stocks

1. Enter a ticker symbol (e.g., AAPL, MSFT) or company name in the search field
2. Click "Search" to retrieve stock information
3. You can then view stock details and place trades

### Supported Features

- Real-time stock quotes
- Historical price data
- Company information and financials
- Buy and sell functionality
- Portfolio tracking

### Common Stock Tickers

The search functionality works best with well-known stock tickers such as:
- AAPL (Apple)
- MSFT (Microsoft)
- GOOGL (Alphabet/Google)
- AMZN (Amazon)
- META (Meta/Facebook)
- TSLA (Tesla)
- NVDA (NVIDIA)
- And many more

### Troubleshooting

If you're having issues with stock data:
1. Try searching for a well-known ticker symbol like AAPL or MSFT
2. Ensure you're connected to the internet
3. Check the application logs for any errors
4. Restart the application if issues persist 