#!/usr/bin/env python3
"""
Database management utility for the Yale Trading Simulation Platform.
Provides tools for verification, migration, and maintenance of the database.
"""
import os
import sys
import argparse
import subprocess

# Get the absolute path to the project root directory
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

from app import create_app, db
from sqlalchemy import text
from flask_migrate import upgrade

def verify_connection():
    """Test connection to the database."""
    app = create_app()
    with app.app_context():
        try:
            # Use text() to create a proper SQL expression
            result = db.session.execute(text("SELECT 1")).scalar()
            if result == 1:
                print("✓ Database connection successful")
                
                # Check what database we're connected to
                db_version = db.session.execute(text("SELECT version()")).scalar()
                if "postgresql" in db_version.lower():
                    print(f"✓ Connected to PostgreSQL")
                    print(f"  Version: {db_version.split(',')[0]}")
                else:
                    print(f"✓ Connected to database: {db_version}")
                
                return True
            else:
                print("✗ Database test failed: unexpected result")
                return False
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False

def get_db_info():
    """Get detailed information about the database."""
    app = create_app()
    with app.app_context():
        try:
            print("\nDatabase Information:")
            print("---------------------")
            
            # Get basic connection info
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            if 'postgresql:' in db_uri:
                db_type = 'PostgreSQL'
                # Mask password in connection string for display
                parts = db_uri.split('@')
                if len(parts) > 1:
                    credentials = parts[0].split(':')
                    if len(credentials) > 2:
                        masked_uri = f"{credentials[0]}:{credentials[1]}:****@{parts[1]}"
                        print(f"Connection: {masked_uri}")
                    else:
                        print(f"Connection: PostgreSQL (connection string format not recognized)")
                else:
                    print(f"Connection: PostgreSQL (connection string format not recognized)")
            else:
                print(f"Warning: Not using PostgreSQL. Connection: {db_uri}")
            
            # Get database version
            version = db.session.execute(text("SELECT version()")).scalar()
            print(f"Version: {version}")
            
            # Get more detailed information
            # Get database size
            size = db.session.execute(text(
                "SELECT pg_size_pretty(pg_database_size(current_database()))"
            )).scalar()
            print(f"Database size: {size}")
            
            # Get table list and row counts
            print("\nTables:")
            tables = db.session.execute(text("""
                SELECT relname as table_name, n_live_tup as row_count
                FROM pg_stat_user_tables
                ORDER BY n_live_tup DESC
            """)).fetchall()
            
            for table in tables:
                print(f"  {table[0]:<20} {table[1]:>10} rows")
            
            return True
        except Exception as e:
            print(f"✗ Error getting database info: {e}")
            return False

def test_models():
    """Test basic CRUD operations on the User model."""
    from app.models.user import User
    
    app = create_app()
    with app.app_context():
        try:
            # Test user creation
            print("\nTesting model operations:")
            print("-------------------------")
            print("Testing user creation...")
            test_user = User(net_id="test123", first_name="Test", last_name="User")
            db.session.add(test_user)
            db.session.commit()
            print("✓ User created successfully!")
            
            # Test user retrieval
            print("Testing user retrieval...")
            user = User.query.filter_by(net_id="test123").first()
            if user:
                print(f"✓ Retrieved user: {user.net_id}, {user.first_name} {user.last_name}")
            else:
                print("✗ Error: User not found!")
                return False
                
            # Test user update
            print("Testing user update...")
            user.first_name = "Updated"
            db.session.commit()
            
            # Verify update
            updated_user = User.query.filter_by(net_id="test123").first()
            print(f"✓ Updated user: {updated_user.net_id}, {updated_user.first_name} {updated_user.last_name}")
            
            # Clean up - delete test user
            print("Testing user deletion...")
            db.session.delete(user)
            db.session.commit()
            
            # Verify deletion
            deleted_user = User.query.filter_by(net_id="test123").first()
            if deleted_user is None:
                print("✓ User deleted successfully!")
            else:
                print("✗ Error: User not deleted!")
                return False
                
            print("\n✓ All model operations completed successfully!")
            return True
        except Exception as e:
            print(f"✗ Error during model testing: {e}")
            return False

def run_migrations():
    """Run database migrations"""
    print("Starting database migrations...")
    
    # Create the Flask app
    app = create_app()
    
    # Get the database URL
    db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    
    # Print info (without password)
    if 'postgresql://' in db_url:
        # Hide password in displayed URL
        parts = db_url.split('@')
        if len(parts) > 1:
            user_part = parts[0].split(':')
            if len(user_part) > 1:
                obscured = f"{user_part[0]}:****@{parts[1]}"
                print(f"Database: {obscured}")
            else:
                print(f"Database: PostgreSQL (connection string format not recognized)")
        else:
            print(f"Database: PostgreSQL (connection string format not recognized)")
    else:
        print(f"Database: {db_url}")
    
    try:
        with app.app_context():
            # Check if we can connect
            result = db.session.execute(text("SELECT 1")).scalar()
            print(f"Database connection test: {'Successful' if result == 1 else 'Failed'}")
            
            # Run migrations
            print("Running database migrations...")
            upgrade()
            
            print("Database migrations completed successfully!")
            return True
    except Exception as e:
        print(f"Error during migrations: {e}")
        return False

def run_maintenance(vacuum=False, analyze=False):
    """Run database maintenance tasks (PostgreSQL only)"""
    if not any([vacuum, analyze]):
        print("No maintenance tasks specified. Use --vacuum or --analyze")
        return False
        
    print("Starting database maintenance...")
    
    # Create the Flask app
    app = create_app()
    
    with app.app_context():
        try:
            # Check if we're using PostgreSQL
            db_type = db.session.execute(text("SELECT version()")).scalar()
            if "postgresql" not in db_type.lower():
                print(f"This functionality is for PostgreSQL only. Detected: {db_type}")
                return False
                
            if vacuum:
                print("Running VACUUM...")
                db.session.execute(text("VACUUM"))
                print("VACUUM completed")
                
            if analyze:
                print("Running ANALYZE...")
                db.session.execute(text("ANALYZE"))
                print("ANALYZE completed")
                
            print("Maintenance tasks completed successfully!")
            return True
            
        except Exception as e:
            print(f"Error during maintenance: {e}")
            return False

def setup_database(confirm=True):
    """
    Set up the database by executing the setup_db.sql script.
    This will create the database, user, and set permissions.
    """
    if confirm and not confirm_deletion():
        print("Database setup cancelled.")
        return False
    
    # Get the path to the SQL setup script
    setup_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'setup_db.sql')
    
    if not os.path.exists(setup_script_path):
        print(f"Error: Setup script not found at {setup_script_path}")
        return False
    
    print("Running database setup script...")
    
    try:
        # Run the psql command to execute the script
        cmd = ['psql', 'postgres', '-f', setup_script_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error executing setup script: {result.stderr}")
            return False
        
        print("Setup script output:")
        print(result.stdout)
        print("\nDatabase and user setup completed successfully!")
        print("Remember to update your .env file with the correct database URL if needed.")
        return True
    except Exception as e:
        print(f"Error during database setup: {e}")
        return False

def confirm_deletion():
    """Confirm that the user wants to delete the database."""
    answer = input("This will DELETE the existing database and create a new one. Are you sure? (y/n): ")
    return answer.lower() == 'y'

def reset_database(confirm=True):
    """Reset the database by dropping and recreating all tables."""
    # Confirm deletion if confirm flag is True
    if confirm and not confirm_deletion():
        print("Operation cancelled.")
        return False
    
    print("Connecting to PostgreSQL database...")
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        
        print("Creating database structure...")
        db.create_all()
    
    print("Database has been reset successfully.")
    
    # Instructions for clearing browser sessions
    print("\n*** IMPORTANT: You may need to clear your browser cookies/cache ***")
    print("If you still see 'Net ID already registered' errors after reset:")
    print("1. Clear your browser cookies for this site")
    print("2. Try using incognito/private browsing mode")
    print("3. Or restart your Flask server completely\n")
    
    return True

def main():
    """Main function to parse arguments and run commands."""
    parser = argparse.ArgumentParser(description='Database Management for YTSP')
    
    # Basic verification commands
    parser.add_argument('--verify', action='store_true', help='Verify database connection')
    parser.add_argument('--info', action='store_true', help='Get database information')
    parser.add_argument('--test', action='store_true', help='Test database models')
    
    # Migration command
    parser.add_argument('--migrate', action='store_true', help='Run database migrations')
    
    # Maintenance commands (PostgreSQL only)
    parser.add_argument('--vacuum', action='store_true', help='Run VACUUM (PostgreSQL only)')
    parser.add_argument('--analyze', action='store_true', help='Run ANALYZE (PostgreSQL only)')
    
    # Reset commands
    parser.add_argument('--reset', action='store_true', help='Reset the database (drop and recreate all tables)')
    parser.add_argument('--setup', action='store_true', help='Set up database and user using SQL script')
    parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation prompts (use with caution)')
    
    # Convenience command
    parser.add_argument('--all', action='store_true', help='Run verification, info, and test')
    
    args = parser.parse_args()
    
    # Default to --verify if no args provided
    if not any([args.verify, args.info, args.test, args.migrate, 
                args.vacuum, args.analyze, args.reset, args.setup, args.all]):
        args.verify = True
    
    # If --all is specified, run all basic checks
    if args.all:
        args.verify = args.info = args.test = True
    
    success = True
    
    if args.setup:
        setup_success = setup_database(not args.yes)
        success = success and setup_success
    
    if args.verify:
        connection_success = verify_connection()
        success = success and connection_success
    
    if args.info:
        info_success = get_db_info()
        success = success and info_success
        
    if args.test:
        test_success = test_models()
        success = success and test_success
        
    if args.migrate:
        migration_success = run_migrations()
        success = success and migration_success
        
    if args.vacuum or args.analyze:
        maintenance_success = run_maintenance(
            vacuum=args.vacuum,
            analyze=args.analyze
        )
        success = success and maintenance_success
        
    if args.reset:
        reset_success = reset_database(not args.yes)
        success = success and reset_success
    
    if success:
        print("\n✓ All database operations completed successfully!")
        print("\nNote: For database backups, use the backup script:")
        print("  ./db_tools/backup_db.sh")
        return 0
    else:
        print("\n✗ Some database operations failed. See above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 