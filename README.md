# Yale Trading Simulation Platform (YTSP)

A Robinhood-like full-stack web application for Yale students to simulate stock investments, manage financial portfolios, and interact with a community of peers.

![Yale Trading Platform](https://via.placeholder.com/800x400?text=Yale+Trading+Platform)

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [User Guide](#user-guide)
- [Development Guidelines](#development-guidelines)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

### User Management
- **Authentication**: Secure registration and login system with Yale NetID integration
- **Profile Management**: Customize your trading profile and privacy settings
- **Fund Management**: Deposit and withdraw simulated funds with transaction history
- **Account Settings**: Update personal information and security preferences

### Trading Features
- **Stock Search**: Find companies by ticker symbol (e.g., AAPL, MSFT) or company name
- **Real-time Data**: View current stock prices, trends, and historical performance
- **Company Information**: Access detailed company profiles, financial statistics, and news
- **Portfolio Management**:
  - Buy and sell stocks with real-time pricing
  - Track your holdings with performance metrics
  - View historical trades and portfolio growth
  - Analyze investment distribution and sector exposure

### Social Features
- **User Network**: Follow other Yale students to build your investment network
- **Activity Feed**: View trading activities of people you follow
- **Trading Posts**: Share insights about your trades with custom messages
- **Engagement**: Like, dislike, and comment on trading posts
- **Privacy Control**: Set trading activities as public or private
- **Leaderboards**: Compare performance with peers (coming soon)

## Tech Stack

### Backend
- **Framework**: Python Flask with Blueprints architecture
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: SQLAlchemy for database management
- **Authentication**: Flask-Login with secure password handling
- **Forms**: WTForms with CSRF protection

### Frontend
- **Templates**: Jinja2 template engine
- **CSS Framework**: Bootstrap 5 for responsive design
- **JavaScript**: Vanilla JS with HTMX for dynamic content
- **Charts**: Chart.js for financial data visualization

### APIs & Services
- **Stock Data**: Integration with Yahoo Finance (yfinance)
- **Historical Data**: Time-series financial information
- **Company Information**: Company profiles and key statistics

## Project Structure

```
ytsp/
├── app/                    # Main application package
│   ├── api/                # API endpoints
│   │   ├── auth.py         # Authentication routes
│   │   ├── main.py         # Main site routes
│   │   ├── social.py       # Social feature routes
│   │   └── trading.py      # Trading functionality routes
│   ├── models/             # Database models
│   │   ├── user.py         # User model
│   │   ├── stock.py        # Stock and portfolio models
│   │   └── social.py       # Social interaction models
│   ├── static/             # Static assets (CSS, JS, images)
│   ├── templates/          # HTML templates
│   └── utils/              # Utility functions
├── migrations/             # Database migrations
├── tests/                  # Test suite
├── venv/                   # Virtual environment
├── .env                    # Environment variables
├── .env.example            # Example environment file
├── app.db                  # SQLite database
├── requirements.txt        # Python dependencies
├── reset_db.py             # Database reset utility
├── run.py                  # Application entry point
└── README.md               # This file
```

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Git
- Internet connection for API access

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yale-cpsc519/trading-platform.git
cd trading-platform
```

2. **Set up a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize the database**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. **Populate with sample data (optional)**
```bash
python reset_db.py
```

7. **Run the application**
```bash
flask run
# or
python run.py
```

8. **Access the application at http://localhost:5000**

## User Guide

### Registration and Login
1. Navigate to the homepage
2. Click "Register" and complete the form with your Yale credentials
3. Verify your email if required
4. Log in with your credentials

### Managing Your Portfolio
1. After logging in, you'll be directed to your dashboard
2. To add funds: Go to "Account" → "Deposit Funds"
3. To buy stocks:
   - Use the search bar to find a stock by ticker or name
   - Click on the stock to view details
   - Enter the quantity and click "Buy"
4. To sell stocks:
   - Go to "Portfolio" → "Holdings"
   - Find the stock you want to sell
   - Enter the quantity and click "Sell"
5. To view performance:
   - Visit your portfolio dashboard for an overview
   - Click on individual holdings for detailed performance

### Social Features
1. To follow other users:
   - Search for users in the "Social" tab
   - Visit their profile and click "Follow"
2. To share a trade:
   - Complete a buy/sell transaction
   - Choose to make it public and add a comment
3. To engage with posts:
   - Browse the "Social Feed" to see posts from users you follow
   - Like, dislike, or comment on posts
4. To manage privacy:
   - Go to "Settings" → "Privacy"
   - Configure which activities are visible to followers

## Development Guidelines

### Coding Standards
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Document functions and classes with docstrings
- Maintain separation of concerns between models, views, and controllers

### Database Migrations
When changing models:
```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

### Adding New Features
1. Create/modify model classes in `app/models/`
2. Update controllers in `app/controllers/`
3. Create/modify templates in `app/templates/`
4. Add static assets in `app/static/`
5. Run tests to ensure functionality

## Testing

### Running Tests
```bash
pytest
# For specific tests
pytest tests/test_trading.py
# With coverage
pytest --cov=app tests/
```

### Testing Accounts
- **Admin User**: admin@yale.edu / password123
- **Test User**: test@yale.edu / password123

## Troubleshooting

### Common Issues

#### API Connection Problems
If stock data isn't loading:
1. Check your internet connection
2. Verify that the Yahoo Finance API is accessible
3. Try searching for a popular ticker (AAPL, MSFT)
4. Check application logs for errors

#### Database Errors
If you encounter database issues:
1. Ensure migrations are up to date: `flask db upgrade`
2. If database is corrupted, reset it: `python reset_db.py`

#### Authentication Problems
If you can't log in:
1. Verify your credentials
2. Reset your password through the login page
3. Check if your account is locked (after multiple failed attempts)

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

© 2023 Yale University CPSC 519 Project Team 