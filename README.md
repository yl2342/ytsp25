# Yale Trading Simulation Platform (YTSP) 

A full-stack web application for Yale students to simulate stock investments, manage financial portfolios, and interact with a community of peers.

--- 
<div align="center">
  <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
    <div style="width: 48%;">
      <img src="app/static/img/main_demo1.png" alt="Yale Trading Platform - Main Page" width="100%" style="height: auto;" />
      <p><strong>Yale Trading Platform - Main Page</strong></p>
    </div>
    <div style="width: 48%;">
      <img src="app/static/img/main_demo2.png" alt="Yale Trading Platform - Stock Details" width="100%" style="height: auto;" />
      <p><strong>Yale Trading Platform - Stock Details</strong></p>
    </div>
  </div>
  
  <div style="display: flex; justify-content: space-between;">
    <div style="width: 48%;">
      <img src="app/static/img/main_demo3.png" alt="Yale Trading Platform - AI Assist Trading" width="100%" style="height: auto;" />
      <p><strong>Yale Trading Platform - AI Assist Trading</strong></p>
    </div>
    <div style="width: 48%;">
      <img src="app/static/img/main_demo4.png" alt="Yale Trading Platform - Social" width="100%" style="height: auto;" />
      <p><strong>Yale Trading Platform - Social</strong></p>
    </div>
  </div>
</div>

--- 

## Project Status

**Current Version: Beta Version II**

This is the beta version of the platform with core trading functionality and AI-assisted features. The application is fully functional with user authentication, trading capabilities, portfolio management, augmented social features, and AI trading advice.

### Roadmap

* **March 28 2024**: MVP Release with core trading, portfolio management, and social features ✅
* **April 9**: Alpha Version: Enhanced UI/UX and expanded community feature (like/dislike posts) ✅
* **April 18 2024**: Beta Version: Implement Yale CAS authentication, polish UI/UX with avator added, add enhanced interactive price trend chart over different time intervals ✅
* **April 23 2024**: Beta Version II : Add AI-Assisted Trading Advice integration (structured prompt for gemini-2.0-flash grounding by real-time google search)✅
* **May 3 2024**: Final Version:  Finalize UI/UX design, comprehensive testing, documentation, and deployment

---

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
- [Team](#team)
- [License](#license)

---

## Features

### User Management
- **Authentication**: Secure registration and login system using Yale netid and Yale CAS
- **Profile Management**: Customize your trading profile and privacy settings for your trading posts
- **Fund Management**: Deposit and withdraw simulated funds with transaction history

### Trading Features
- **Stock Search**: Find companies by ticker symbol (e.g., AAPL, MSFT)
- **Real-time Data**: View current stock prices powered by Yahoo Finance API
- **Historical Data**: View historical stock prices over different time intervals
- **Company Information**: Access detailed company profiles, financial statistics
- **Portfolio Management**:
  - Buy and sell stocks with (nearly) real-time pricing
  - Track your holdings with performance metrics
  - View historical trades and portfolio growth
  - Analyze investment distribution and sector exposure
  
### Social Features
- **User Network**: Follow other Yale students to build your investment network
- **Activity Feed**: View trading activities on the social feed platform or shared by the people you follow
- **Trading Posts**: Share insights about your trades with custom messages
- **Engagement**: Comment on trading posts, like or dislike posts
- **Interactive Reactions**: Like/dislike trading posts with visual feedback and counter updates
- **Privacy Control**: Set trading activities as public or private

### AI-Assisted Trading Advice
- **Personalized Analysis**: Get AI-generated advice tailored to your specific trading situation
- **Context-Aware Recommendations**: The system analyzes your:
  - Current holdings and portfolio composition
  - Trading history and patterns
  - Stock's current performance metrics
  - Recent market trends and news
- **Interactive Workflow**:
  1. Click "Need AI assist for this trade?" when placing an order
  2. Generate and review the prompt for your AI assistant (customizable)
  3. Confirm to send the prompt to your AI assistant 
  4. Review detailed AI trading advice response with markdown formatting
  5. View source references used by the AI for its analysis
  6. Choose to confirm and display the advice on your trading submission page
- **Grounded Analysis**: Model (Gemini-2.0-Flash) uses Google Search in real-time to provide up-to-date information about:
  - Recent stock news and developments
  - Market conditions and trends
  - Company-specific information
- **Comprehensive Advice**: Receive structured guidance including:
  - Analysis of your trading patterns and preferences
  - Specific recommendations for your proposed trade
  - Alternative trading strategies to consider
  - Potential risks and opportunities

---

## Tech Stack

### Backend
- **Framework**: Python Flask with Blueprints architecture
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy for database management
- **Authentication**: Flask-Login with secure password handling via Flask-Bcrypt and Yale CAS
- **Forms**: WTForms with CSRF protection
- **AI Integration**: Google Generative AI (Gemini) with search grounding capabilities

### Frontend
- **Templates**: Jinja2 template engine
- **CSS Framework**: Bootstrap 5 for responsive design
- **JavaScript**: Vanilla JS with HTMX for dynamic content
- **Charts**: Chart.js for financial data visualization
- **Markdown Rendering**: Marked.js for formatting AI responses

### APIs & Services
- **Stock Data**: Integration with nearly-real-time Yahoo Finance API
- **Historical Data**: Time-series financial information
- **Company Information**: Company profiles and key statistics
- **AI Services**: Google Gemini 2.0 Flash API with Google Search grounding

---

## Project Structure

```
ytsp/
├── app/                    # Main application package
│   ├── api/                # API endpoints
│   │   ├── stock_api.py    # Stock data endpoints
│   │   ├── user_api.py     # User data endpoints
│   │   └── ai_api.py       # AI assistance endpoints
│   ├── controllers/        # Route handlers
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
├── db_tools/               # Database management utilities
│   ├── backup_db.sh        # Database backup script
│   └── db_manager.py       # All-in-one database management utility
├── backups/                # Directory for database backups
├── venv/                   # Virtual environment
├── .env                    # Environment variables (includes GEMINI_API_KEY)
├── .env.example            # Example environment file
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point
└── README.md               # This file
```

---

## Server Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Git
- PostgreSQL 12 or higher
- Internet connection for API access
- Google Gemini API key (for AI-assisted trading features)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yale-cpsc-419-25sp/project-project-group-24
cd project-project-group-24
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
- Google gemini api key is required for AI-assisted features
- To get the key, please visit https://aistudio.google.com/app/apikey
- Note the rate limit for the free tier gemini-2.0-flash API call
  - RPM (requests per minute) is 15
  - TPM (tokens per minute) is 1,000,000
  - RPD (requests per day) is 1,500
```bash
cp .env.example .env
# Edit .env with your configuration
# Be sure to include your GEMINI_API_KEY for AI-assisted features
# Be sure to set DATABASE_URL for PostgreSQL
```

5. **Start the PostgreSQL service**
```bash
# This step is REQUIRED before any database operations
# macOS: 
brew services start postgresql
# Ubuntu: 
sudo systemctl start postgresql
# Windows (with PostgreSQL installed):
# Open Services application and start PostgreSQL service
```

6. **Set up the database**

```bash
# Install PostgreSQL if not already installed
# macOS: brew install postgresql
# Ubuntu: sudo apt install postgresql postgresql-contrib

# Create database and user
createdb ytsp
psql postgres -c "CREATE USER ytsp_server WITH PASSWORD 'secure_password';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE ytsp TO ytsp_server;"

# Or using psql directly
psql postgres
> CREATE DATABASE ytsp;
> CREATE USER ytsp_server WITH PASSWORD 'secure_password';
> GRANT ALL PRIVILEGES ON DATABASE ytsp TO ytsp_server;
> \q

# Update your .env file with PostgreSQL connection string
# DATABASE_URL=postgresql://ytsp_server:secure_password@localhost:5432/ytsp
```

7. **Initialize the database**
```bash
# Initialize Flask migrations (only needed once for a new project)
flask db init

# Apply migrations
flask db upgrade
# OR use the database manager
python db_tools/db_manager.py --migrate

# Verify database connection
python db_tools/db_manager.py --verify
```

8. **Populate with sample data (optional)**
```bash
# After database migrations have been applied
python db_tools/db_manager.py --seed
# OR reset and seed in one command
python db_tools/db_manager.py --reset-seed
```

9. **Run the application**
```bash
flask run
# or
python run.py
```

10. **Access the application at http://localhost:5000**

### Verifying Your Setup

To ensure everything is working correctly:

1. **Check database connection and information**:
```bash
python db_tools/db_manager.py --all
```

2. **Access the application** and verify you can:
   - Register a new user
   - Log in
   - View stocks
   - Make transactions
   - Access social features

---

## Client User Guide

### Registration and Login
1. Navigate to the homepage
2. Click "Register" and complete the form with your Yale credentials
3. Log in with your credentials (you can not log in without registering first)

### Managing Your Portfolio
1. After logging in, you'll be directed to your dashboard
2. New users will be granted 1,000 virtual dollars to start with
3. To add funds: Go to "Account" → "Deposit Funds"
4. To buy stocks:
   - Use the search bar to find a stock by ticker symbol
   - Click on the stock to view details
   - Enter the quantity and click "Buy" (You can only trade whole shares)
5. To sell stocks:
   - Go to "Portfolio" → "Holdings"
   - Find the stock you want to sell
   - Enter the quantity and click "Sell"
6. To view performance:
   - Visit your portfolio dashboard for an overview
   - Click on individual holdings for detailed performance

### Using AI-Assisted Trading
1. Search for a stock and navigate to its detail page
2. Enter the quantity you wish to buy/sell
3. Click the "Need AI assist for this trade?" button
4. In the modal window, click "Generate and review your prompt first"
5. Review the generated prompt (which includes your portfolio data and trade details)
6. Edit the prompt if desired - it's fully customizable!
7. Click "Confirm my prompt for AI advice" like you send your prompt to your other AI friends (eg. chatgpt)
8. Review the AI's detailed analysis and recommendations in the new window
9. Click "Confirm" to add the AI advice to your trading page, or "Close" to dismissss it
10. If confirmed, the AI advice will appear on your stock detail page for reference
11. Submit your trade if you want to proceed with the trade

### Social Features
1. To follow other users:
   - Search for users by their netid in the "Social" tab
   - Visit their profile and click "Follow"
2. To share a trade:
   - Complete a buy/sell transaction
   - Choose add a comment to your trade and make it public
3. To engage with posts:
   - Browse the "Social Feed" to see posts from users you follow
   - Comment on posts
   - Like or dislike posts by clicking the thumbs up/down buttons
   - Click again on a liked/disliked post to remove your reaction

---

## Development Guidelines

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

---

## Database Utilities

YTSP provides a single all-in-one database management utility located in `db_tools/db_manager.py`:

```bash
# Verify database connection (default if no arguments provided)
python db_tools/db_manager.py --verify

# Get database information
python db_tools/db_manager.py --info

# Test model operations
python db_tools/db_manager.py --test

# Run all verification checks
python db_tools/db_manager.py --all

# Database migrations (alternative to flask db upgrade)
python db_tools/db_manager.py --migrate

# PostgreSQL maintenance
python db_tools/db_manager.py --vacuum --analyze

# Database reset and seed operations
python db_tools/db_manager.py --reset        # Drop and recreate all tables
python db_tools/db_manager.py --seed         # Populate with sample data
python db_tools/db_manager.py --reset-seed   # Reset and seed in one operation
python db_tools/db_manager.py --reset-seed -y # Skip confirmation prompts
```

For database backups and restores:

```bash
# Create a timestamped backup of your PostgreSQL database
./db_tools/backup_db.sh

# Restore from a backup file
psql -U ytsp_server -d ytsp < ./backups/ytsp_backup_YYYYMMDD_HHMMSS.sql
```

The backup script:
- Automatically extracts database connection information from your `.env` file
- Creates timestamped SQL dump files in the `backups/` directory
- Works with PostgreSQL databases
- Provides detailed feedback on backup size and success status

To restore a database:
- Use the standard PostgreSQL `psql` command as shown above
- Replace the filename with your actual backup file's name
- Make sure the target database exists before restoring
- The restore will replace all data in the target database

4. **Database Reset**
   - Use the reset script which will recreate all tables: `python db_tools/db_manager.py --reset`
   - Reset and seed in one operation: `python db_tools/db_manager.py --reset-seed`

---

## Troubleshooting

### Common Issues

#### API Connection Problems
If stock data isn't loading:
1. Check your internet connection
2. Verify that the Yahoo Finance API is accessible
3. Try searching for a popular ticker (AAPL, MSFT)
4. Check application logs for errors

#### AI Feature Issues
If the AI trading assistant isn't working:
1. Ensure your GEMINI_API_KEY is correctly set in your .env file
2. Check your internet connection as the AI uses Google Search for grounding
3. Check the current rate limit of free tier gemini-2.0-flash API and see if you have reached the limit
4. Try with a simpler prompt if context window size exceeds the model's limit
5. Check application logs for API errors

#### Database Errors
If you encounter database issues:

1. **PostgreSQL Service Issues**
   - Make sure PostgreSQL service is running:
     - macOS: `brew services list` to check, `brew services start postgresql` to start
     - Ubuntu: `sudo systemctl status postgresql` to check, `sudo systemctl start postgresql` to start
   - If you see "Connection refused" errors, this is usually because the PostgreSQL service isn't running

2. **Migration Issues**
   - Ensure migrations are up to date: `flask db upgrade`
   - If there are conflicts: `flask db stamp head` then `flask db migrate`
   - Alternative: Use the database manager: `python db_tools/db_manager.py --migrate`

3. **Connection Issues**
   - Connection errors: Check that PostgreSQL service is running
   - Permission issues: Verify user has proper permissions on database
   - Use the verification tool: `python db_tools/db_manager.py --verify`

4. **Database Reset**
   - Use the reset script which will recreate all tables: `python db_tools/db_manager.py --reset`
   - Reset and seed in one operation: `python db_tools/db_manager.py --reset-seed`

5. **Performance Issues**
   - Slow queries may indicate missing indexes
   - Run maintenance: `python db_tools/db_manager.py --vacuum --analyze`

#### Authentication Problems
If you can't log in:
1. Make sure you are Yale affliated and have a valid netid. (This app is not open to the public yet)
2. Verify your credentials for Yale CAS

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request
   
---

## Team

### Project Authors
- Yuntian Liu, PhD student in Biomedical informatics and data science department at Yale University
- Karen Dorantes, Undergrad Student in Computer Science at Yale University
- David Rodriguez, Undergrad Student in Computer Science at Yale University

---

## License

This project is licensed under the MIT License 

---

© 2025 Yale University CPSC 519 Project Team No. 24. All rights reserved.