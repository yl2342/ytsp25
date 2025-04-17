# Yale Trading Simulation Platform - Application Structure

This directory contains the core application code for the Yale Trading Simulation Platform (YTSP). This document provides an overview of the application architecture, component responsibilities, and design patterns.

## Project Status

**Current Version: Alpha Version**

This is the initial version of the platform with core trading functionality. The application is fully functional with user authentication, trading capabilities, portfolio management, and social features.

### Upcoming Features

* **Enhanced UI/UX**: Improved design and user experience
* **Advanced Portfolio Analytics**: More detailed performance metrics and visualizations
* **Enhanced Social Features**: Expanded community functionality including likes/dislikes and sharing
* **AI-Assisted Trading Advice**: Integration with LLM reasoning models to provide personalized trading insights and recommendations

## Architecture Overview

The application follows a Model-View-Controller (MVC) pattern with Flask Blueprints for modular organization:

- **Models**: Database schema definitions using SQLAlchemy ORM
- **Views**: Jinja2 templates (in `templates/`)
- **Controllers**: Route handlers organized into blueprints

## Directory Structure

```
app/
├── __init__.py          # Application factory and configuration
├── forms.py             # WTForms form definitions
├── api/                 # API endpoints for data retrieval
├── controllers/         # Route handlers organized by feature
├── models/              # Database models
├── static/              # Static assets (CSS, JS, images)
├── templates/           # Jinja2 HTML templates
└── utils/               # Helper functions and utilities
```

## Components

### Models (`app/models/`)

Database models using SQLAlchemy:

- **User** (`user.py`): User accounts, authentication, and relationships
- **Stock** (`stock.py`): Stock holdings, transactions, and cash movements
- **Social** (`social.py`): Trading posts, comments, and social interactions

### Controllers (`app/controllers/`)

Route handlers divided by feature area:

- **Auth** (`auth.py`): User registration, login, profile management
- **Main** (`main.py`): Home page, dashboard, and general navigation
- **Trading** (`trading.py`): Stock search, buy/sell operations, portfolio management
- **Social** (`social.py`): Social feed, posts, comments, and user following

### API (`app/api/`)

External data access endpoints for stock data retrieval

### Templates (`app/templates/`)

Jinja2 templates are organized by controller/feature to maintain separation of concerns.

### Utils (`app/utils/`)

Helper functions and services:

- **stock_utils.py**: Functions for fetching and processing stock data
- **trading_utils.py**: Utilities for executing trades and managing portfolios

## Planned AI Integration

In future iterations, we will integrate large language models (LLMs) to provide AI-assisted trading advice:

### LLM Reasoning Models

- **Trade Analysis**: AI evaluation of potential trades based on market conditions, historical data, and user portfolio
- **Risk Assessment**: Intelligent risk analysis for each transaction
- **Market Insights**: AI-generated explanations of market trends and events
- **Learning System**: Personalized advice that improves based on user preferences and trading history

### Implementation Plan

1. Create a new `ai_utils.py` module for AI-related functionality
2. Add API endpoints for requesting trading advice
3. Develop UI components to display AI insights within the trading workflow
4. Implement feedback mechanisms to improve advice quality

### Technical Approach

- Integration with LLM providers' APIs
- Context-aware prompting with user portfolio data and market conditions
- Hybrid system combining traditional analysis with AI reasoning
- Feedback loop for continuous improvement

## Authentication Flow

1. User registers with email and password
2. Password is hashed and stored using Bcrypt via Flask-Bcrypt
3. Flask-Login manages user sessions and authorization
4. Protected routes enforce login_required decorator

## Data Flow

1. User initiates actions through controller routes
2. Controllers validate input using WTForms
3. Business logic is executed (often with help from utils)
4. Database is updated via SQLAlchemy models
5. Responses are returned (templates or JSON)


---

For more detailed documentation on specific components, please refer to comments in the respective files. 