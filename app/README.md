# Yale Trading Simulation Platform - Application Structure

This directory contains the core application code for the Yale Trading Simulation Platform.

## Directory Structure

### `__init__.py`
- Application factory pattern
- Flask application configuration
- Blueprint registration
- Extension initialization

### `/api/`
API endpoints for external services integration.

- Stock data retrieval
- Market information
- External integrations

### `/controllers/`
Route handlers organized by feature.

- **`auth.py`**: Authentication routes (login, logout, registration)
- **`main.py`**: Core application routes (home, about, etc.)
- **`social.py`**: Social feature routes (following, feed, posts)
- **`trading.py`**: Trading functionality routes (buy, sell, portfolio)

### `/models/`
Database models using SQLAlchemy ORM.

- **`user.py`**: User account and profile models
- **`stock.py`**: Stock data and portfolio models
- **`social.py`**: Social interaction models (follows, posts)

### `/static/`
Static assets for the application.

- **`/css/`**: Stylesheets
- **`/js/`**: JavaScript files
- **`/img/`**: Images and icons
- **`/vendor/`**: Third-party libraries

### `/templates/`
Jinja2 templates organized by feature.

- **`/auth/`**: Authentication templates
- **`/main/`**: Core page templates
- **`/social/`**: Social feature templates
- **`/trading/`**: Trading functionality templates
- **`layout.html`**: Base template with common structure

### `/utils/`
Utility functions and helpers.

- Date/time formatting
- Financial calculations
- Security utilities
- General helper functions

### `forms.py`
Form definitions using WTForms.

- Login/registration forms
- Trading forms
- User profile forms
- Search forms

## Application Flow

1. Request enters through a controller route
2. Controller validates input (forms)
3. Controller interacts with models to retrieve/modify data
4. Controller renders a template with the data
5. Response returned to user

## Development Guidelines

### Adding a New Feature

1. **Models**: Add necessary database models
2. **Forms**: Create form classes for user input
3. **Controllers**: Add route handlers
4. **Templates**: Create templates for the feature
5. **Static Assets**: Add any required CSS/JS
6. **Testing**: Write tests for the new functionality

### Code Style

- Follow PEP 8 for Python code
- Use consistent naming conventions
- Comment complex sections of code
- Write docstrings for functions and classes

### Security Best Practices

- Use CSRF protection for all forms
- Validate all user input
- Escape output to prevent XSS
- Use secure password handling
- Implement proper access controls

## Extending the Application

### Adding a New Model

1. Create a new file in `models/` or extend an existing one
2. Define your SQLAlchemy model class
3. Add relationships to other models as needed
4. Run migrations to update the database schema

### Adding a New Controller

1. Create a new file in `controllers/` or extend an existing one
2. Define a Blueprint for the feature
3. Add route handlers
4. Register the Blueprint in `__init__.py`

### Adding a New Template

1. Create a new file in `templates/` in the appropriate subdirectory
2. Extend from the base layout template
3. Define blocks for content and scripts
4. Include any required forms or components

## Troubleshooting

- Check the Flask error logs
- Verify database connection
- Ensure all dependencies are installed
- Check for syntax errors in templates
- Verify route definitions and URL mappings

---

For more detailed documentation on specific components, please refer to comments in the respective files. 