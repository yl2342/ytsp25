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