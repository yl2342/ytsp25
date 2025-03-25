"""
Entry point for the Yale Trading Simulation Platform application.
This script creates and runs the Flask application.
"""
from app import create_app

# Create the application using the factory function
app = create_app()

if __name__ == "__main__":
    # Run the application in debug mode when executed directly
    app.run(debug=True) 