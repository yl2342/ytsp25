#!/usr/bin/env python3
"""
Database management utility for the Yale Trading Simulation Platform.
Provides tools for verification, migration, maintenance, and seeding of the database.
"""
import os
import sys
import argparse
import random
from datetime import datetime, timedelta
import zoneinfo

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
        import subprocess
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

def seed_database():
    """Seed the database with sample data."""
    from app.models.user import User
    from app.models.stock import StockHolding, Transaction
    from app.models.social import TradingPost, Comment, PostInteraction
    
    app = create_app()
    
    with app.app_context():
        print("Seeding database with sample data...")
        
        # Create admin user
        print("Creating users...")
        admin = User(
            net_id='admin',
            first_name='Admin',
            last_name='User'
        )
        admin.balance = 100000.00  # $100,000 starting balance
        admin.avatar_id = random.randint(1, 10)  # Randomly assign avatar from available options
        
        # Create seed users with "SEED" as last name
        seed_users = []
        
        # List of common first names
        first_names = ['Emma', 'James', 'Sophia', 'Michael', 'Olivia', 
                       'William', 'Ava', 'Alexander', 'Isabella', 'Daniel', 
                       'Mia', 'Matthew', 'Charlotte', 'Ethan', 'Amelia']
        
        # Create 15 seed users (for a total of 16 users including admin)
        for i in range(15):
            # Randomly select a first name
            first_name = first_names[i % len(first_names)]
            
            # Create a net_id pattern like "fs123" where f=first initial, s=S for SEED
            net_id = f"{first_name[0].lower()}s{random.randint(100, 999)}"
            
            # Create the user
            seed_user = User(
                net_id=net_id,
                first_name=first_name,
                last_name='SEED'  # All have SEED as last name for identification
            )
            
            # Set a random balance between $40,000 and $120,000
            seed_user.balance = random.uniform(40000.00, 120000.00)
            
            # Assign a random avatar ID (1-9) to each seed user
            seed_user.avatar_id = random.randint(1, 9)
            
            seed_users.append(seed_user)
        
        # Set created_at dates to be staggered
        now = datetime.now(zoneinfo.ZoneInfo("America/New_York"))
        
        # Admin user
        admin.created_at_edt = now - timedelta(days=60)
        
        # Seed users - staggered creation between 7 and 55 days ago
        for user in seed_users:
            user.created_at_edt = now - timedelta(days=random.randint(7, 55))
        
        # Last login times
        # Admin user
        admin.last_login_edt = now - timedelta(hours=1)
        
        # Seed users - last login between 1 hour and 5 days ago
        for user in seed_users:
            login_hours_ago = random.randint(1, 120)  # Between 1 hour and 5 days (120 hours)
            user.last_login_edt = now - timedelta(hours=login_hours_ago)
        
        # Combine all users
        all_users = [admin] + seed_users
        
        # Add all users to the database
        db.session.add_all(all_users)
        db.session.commit()
        
        # Create sample stock holdings
        print("Creating stock holdings...")
        stocks = [
            {'ticker': 'AAPL', 'company_name': 'Apple Inc.', 'price': 184.27},
            {'ticker': 'MSFT', 'company_name': 'Microsoft Corporation', 'price': 428.52},
            {'ticker': 'GOOGL', 'company_name': 'Alphabet Inc.', 'price': 153.39},
            {'ticker': 'AMZN', 'company_name': 'Amazon.com, Inc.', 'price': 177.23},
            {'ticker': 'NVDA', 'company_name': 'NVIDIA Corporation', 'price': 902.50},
            {'ticker': 'META', 'company_name': 'Meta Platforms, Inc.', 'price': 475.80},
            {'ticker': 'TSLA', 'company_name': 'Tesla, Inc.', 'price': 168.19},
            {'ticker': 'BAC', 'company_name': 'Bank of America Corporation', 'price': 39.76},
            {'ticker': 'JPM', 'company_name': 'JPMorgan Chase & Co.', 'price': 198.73},
            {'ticker': 'V', 'company_name': 'Visa Inc.', 'price': 271.40},
            {'ticker': 'WMT', 'company_name': 'Walmart Inc.', 'price': 78.65},
            {'ticker': 'PG', 'company_name': 'Procter & Gamble Co.', 'price': 167.30},
            {'ticker': 'DIS', 'company_name': 'The Walt Disney Company', 'price': 113.45},
            {'ticker': 'KO', 'company_name': 'The Coca-Cola Company', 'price': 62.74},
            {'ticker': 'NFLX', 'company_name': 'Netflix, Inc.', 'price': 648.92}
        ]
        
        # Each user buys some stocks
        for user in all_users:
            # Select 4-8 random stocks for each user
            user_stocks = random.sample(stocks, random.randint(4, 8))
            
            for stock in user_stocks:
                # Decide quantity (between 5 and 80 shares)
                quantity = random.randint(5, 80)
                price = stock['price'] * (1 - random.uniform(0.05, 0.15))  # Bought at historical price (5-15% lower)
                
                # Create holding
                holding = StockHolding(
                    user_id=user.id,
                    ticker=stock['ticker'],
                    company_name=stock['company_name'],
                    quantity=quantity,
                    buy_price=price
                )
                holding.current_price = stock['price']  # Current price
                db.session.add(holding)
                
                # Create transaction record
                transaction = Transaction(
                    user_id=user.id,
                    ticker=stock['ticker'],
                    quantity=quantity,
                    price=price,
                    transaction_type='buy'
                )
                
                # Set transaction date to be between user creation and now
                days_since_created = (now - user.created_at_edt).days
                if days_since_created > 0:
                    transaction_days_ago = random.randint(1, days_since_created)
                else:
                    transaction_days_ago = 1
                transaction.created_at_edt = now - timedelta(days=transaction_days_ago)
                
                db.session.add(transaction)
                
                # SEED users have higher chance of creating a trading post (80% vs 50% for admin)
                post_chance = 0.8 if user.last_name == 'SEED' else 0.5
                
                # Maybe create a trading post about this purchase
                if random.random() < post_chance:
                    # Different content based on user type
                    if user.last_name == 'SEED':
                        content_options = [
                            f"As a seed investor, I see great potential in {stock['company_name']}. Adding {quantity} shares at ${price:.2f}.",
                            f"My seed portfolio now includes {quantity} shares of {stock['ticker']} at ${price:.2f}. Expecting great returns!",
                            f"Just added {stock['ticker']} to my seed investments. {quantity} shares at ${price:.2f}.",
                        ]
                    else:
                        content_options = [
                            f"I believe {stock['company_name']} has great potential for growth. Adding {quantity} shares to my portfolio at ${price:.2f}.",
                            f"Just invested in {quantity} shares of {stock['ticker']} at ${price:.2f}. Thoughts?",
                            f"Added {stock['ticker']} to my portfolio: {quantity} shares at ${price:.2f}.",
                        ]
                    
                    content = random.choice(content_options)
                    
                    # Create the trading post
                    post = TradingPost(
                        user_id=user.id,
                        title=f"Just bought {stock['ticker']}!",
                        content=content,
                        transaction_id=transaction.id,
                        is_public=True
                    )
                    
                    # Set post date to be shortly after transaction
                    post.created_at = transaction.created_at_edt + timedelta(minutes=random.randint(5, 60))
                    
                    db.session.add(post)
                    
                    # Add some likes/dislikes to the post
                    potential_likers = [u for u in all_users if u.id != user.id]
                    num_likes = random.randint(0, min(7, len(potential_likers)))
                    
                    if num_likes > 0:
                        likers = random.sample(potential_likers, num_likes)
                        for liker in likers:
                            interaction = PostInteraction(
                                post_id=post.id,
                                user_id=liker.id,
                                interaction_type='like' if random.random() < 0.8 else 'dislike'
                            )
                            db.session.add(interaction)
                    
                    # Add some comments
                    potential_commenters = [u for u in all_users if u.id != user.id]
                    num_comments = random.randint(0, min(5, len(potential_commenters)))
                    
                    if num_comments > 0:
                        commenters = random.sample(potential_commenters, num_comments)
                        
                        buy_comments = [
                            f"Good choice! I'm also bullish on {stock['ticker']}.",
                            f"What's your price target for {stock['ticker']}?",
                            f"Nice entry point! I bought some at ${stock['price'] * 1.1:.2f} last month.",
                            f"What made you decide to invest in {stock['company_name']}?",
                            f"I've had {stock['ticker']} for a while, solid stock!",
                            f"Interesting choice, I'm watching this one closely.",
                        ]
                        
                        for commenter in commenters:
                            comment = Comment(
                                post_id=post.id,
                                user_id=commenter.id,
                                content=random.choice(buy_comments)
                            )
                            comment.created_at = post.created_at + timedelta(hours=random.randint(1, 24))
                            db.session.add(comment)
            
            # Maybe sell some of the stock
            if random.random() < 0.4:  # 40% chance to sell some stock
                # Select a stock to sell from this user's holdings
                holdings = [h for h in db.session.query(StockHolding).filter_by(user_id=user.id).all()]
                
                if holdings:
                    holding = random.choice(holdings)
                    
                    # Sell between 30% and 80% of holdings
                    if holding.quantity > 1:
                        sell_quantity = random.randint(max(1, int(holding.quantity * 0.3)), 
                                                       max(1, int(holding.quantity * 0.8)))
                        
                        # Calculate sell price (0-15% higher than buy price)
                        sell_price = holding.buy_price * (1 + random.uniform(0, 0.15))
                        
                        # Create transaction
                        sell_transaction = Transaction(
                            user_id=user.id,
                            ticker=holding.ticker,
                            quantity=sell_quantity,
                            price=sell_price,
                            transaction_type='sell'
                        )
                        
                        # Set sell date to be after buy date
                        days_since_bought = (now - transaction.created_at_edt).days
                        if days_since_bought > 1:
                            sell_days_ago = random.randint(1, days_since_bought)
                            sell_transaction.created_at_edt = now - timedelta(days=sell_days_ago)
                        else:
                            sell_transaction.created_at_edt = now - timedelta(hours=random.randint(1, 12))
                        
                        db.session.add(sell_transaction)
                        
                        # Maybe create a post about the sale (60% chance)
                        if random.random() < 0.6:
                            sell_post = TradingPost(
                                user_id=user.id,
                                title=f"Sold some {holding.ticker}",
                                content=f"Just sold {sell_quantity} shares of {holding.ticker} at ${sell_price:.2f}. " +
                                        random.choice([
                                            f"Taking some profits!",
                                            f"Rebalancing my portfolio.",
                                            f"Moving into different sectors.",
                                            f"Locking in gains!",
                                            f"Needed some liquidity for a new opportunity."
                                        ]),
                                transaction_id=sell_transaction.id,
                                is_public=True
                            )
                            
                            # Set post date to be shortly after transaction
                            sell_post.created_at = sell_transaction.created_at_edt + timedelta(minutes=random.randint(5, 60))
                            
                            db.session.add(sell_post)
                            
                            # Add interactions and comments similar to buy posts
                            pot_interactors = [u for u in all_users if u.id != user.id]
                            num_interactors = random.randint(0, min(5, len(pot_interactors)))
                            
                            if num_interactors > 0:
                                interactors = random.sample(pot_interactors, num_interactors)
                                for interactor in interactors:
                                    interaction = PostInteraction(
                                        post_id=sell_post.id,
                                        user_id=interactor.id,
                                        interaction_type='like' if random.random() < 0.7 else 'dislike'
                                    )
                                    db.session.add(interaction)
                            
                            # Maybe add comments
                            pot_commenters = [u for u in all_users if u.id != user.id]
                            num_coms = random.randint(0, min(3, len(pot_commenters)))
                            
                            if num_coms > 0:
                                commenters = random.sample(pot_commenters, num_coms)
                                
                                sell_comments = [
                                    f"Good move taking profits on {holding.ticker}!",
                                    f"Do you think {holding.ticker} still has room to grow?",
                                    f"What are you planning to buy with these profits?",
                                    f"I'm still holding my {holding.ticker} shares for now.",
                                    f"Smart timing on the sale!",
                                    f"Are you planning to buy back in if it dips?"
                                ]
                                
                                for commenter in commenters:
                                    comment = Comment(
                                        post_id=sell_post.id,
                                        user_id=commenter.id,
                                        content=random.choice(sell_comments)
                                    )
                                    comment.created_at = sell_post.created_at + timedelta(hours=random.randint(1, 24))
                                    db.session.add(comment)
                            
                        # Update holding quantity
                        holding.quantity -= sell_quantity
                        
                        # Add to user balance
                        user.balance += sell_quantity * sell_price
        
        # Commit all changes
        db.session.commit()
        
        # Print summary of seed users
        print("\nCreated the following users:")
        print(f"- Admin User (net_id: admin)")
        print("\nCreated the following SEED users:")
        for user in seed_users:
            print(f"- {user.first_name} SEED (net_id: {user.net_id})")
            
        # Print statistics
        post_count = db.session.query(TradingPost).count()
        comment_count = db.session.query(Comment).count()
        transaction_count = db.session.query(Transaction).count()
        holding_count = db.session.query(StockHolding).count()
        
        print(f"\nSeed data statistics:")
        print(f"- {len(all_users)} users created")
        print(f"- {post_count} posts created")
        print(f"- {comment_count} comments created")
        print(f"- {transaction_count} transactions created")
        print(f"- {holding_count} stock holdings created")
        
        print("\nNOTE: Users are created without passwords since the application uses Yale CAS authentication.")
        print("To use these accounts, manually update your session data or register with these NetIDs via the Yale CAS test interface.")
        
        return True

def reset_and_seed(confirm=True):
    """Reset the database and seed it with sample data."""
    if reset_database(confirm):
        seed_database()
        print("Database reset and seeding complete!")
        print("You can now run the application with 'flask run' or 'python run.py'")
        print("\nSample user credentials:")
        print("Admin: net_id='admin' (use Yale CAS for authentication)")
        return True
    else:
        print("Database reset and seed was cancelled.")
        return False

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
    
    # Reset and seed commands
    parser.add_argument('--reset', action='store_true', help='Reset the database (drop and recreate all tables)')
    parser.add_argument('--seed', action='store_true', help='Seed the database with sample data')
    parser.add_argument('--reset-seed', action='store_true', help='Reset and seed the database in one operation')
    parser.add_argument('--setup', action='store_true', help='Set up database and user using SQL script')
    parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation prompts (use with caution)')
    
    # Convenience command
    parser.add_argument('--all', action='store_true', help='Run verification, info, and test')
    
    args = parser.parse_args()
    
    # Default to --verify if no args provided
    if not any([args.verify, args.info, args.test, args.migrate, 
                args.vacuum, args.analyze, args.reset, args.seed, 
                args.reset_seed, args.setup, args.all]):
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
        
    if args.seed:
        seed_success = seed_database()
        success = success and seed_success
        
    if args.reset_seed:
        reset_seed_success = reset_and_seed(not args.yes)
        success = success and reset_seed_success
    
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