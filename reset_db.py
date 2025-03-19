import os
import sys
import random
from datetime import datetime, timedelta
import zoneinfo
from flask import Flask
from flask_migrate import upgrade

# Get the absolute path to the project root directory
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Function to confirm deletion
def confirm_deletion():
    answer = input("This will DELETE the existing database and create a new one. Are you sure? (y/n): ")
    return answer.lower() == 'y'

# First, delete the old database if it exists
def reset_database():
    db_path = os.path.join(project_dir, 'instance', 'ytsp.db')
    
    if os.path.exists(db_path):
        if not confirm_deletion():
            print("Operation cancelled.")
            return False
        
        print(f"Removing existing database at {db_path}")
        os.remove(db_path)
    
    # Create the directory if it doesn't exist
    os.makedirs(os.path.join(project_dir, 'instance'), exist_ok=True)
    
    # Create a new database by importing the app and running migrations
    from app import create_app, db
    app = create_app()
    
    with app.app_context():
        print("Creating new database structure...")
        # Create all tables
        db.create_all()
    
    print("Database has been reset successfully.")
    return True

def seed_database():
    from app import create_app, db
    from app.models.user import User
    from app.models.stock import StockHolding, Transaction
    from app.models.social import TradingPost, Comment
    
    app = create_app()
    
    with app.app_context():
        print("Seeding database with sample data...")
        
        # Create sample users
        print("Creating users...")
        admin = User(
            net_id='admin',
            password='password123',
            first_name='Admin',
            last_name='User'
        )
        admin.balance = 100000.00  # $100,000 starting balance
        
        alice = User(
            net_id='acb123',
            password='password123',
            first_name='Alice',
            last_name='Brown'
        )
        alice.balance = 50000.00
        
        bob = User(
            net_id='bxs456',
            password='password123',
            first_name='Bob',
            last_name='Smith'
        )
        bob.balance = 75000.00
        
        charlie = User(
            net_id='czt789',
            password='password123',
            first_name='Charlie',
            last_name='Thompson'
        )
        charlie.balance = 60000.00
        
        # Set created_at dates to be staggered
        now = datetime.now(zoneinfo.ZoneInfo("America/New_York"))
        admin.created_at_edt = now - timedelta(days=60)
        alice.created_at_edt = now - timedelta(days=45)
        bob.created_at_edt = now - timedelta(days=30)
        charlie.created_at_edt = now - timedelta(days=15)
        
        # Last login times
        admin.last_login_edt = now - timedelta(hours=1)
        alice.last_login_edt = now - timedelta(days=1)
        bob.last_login_edt = now - timedelta(hours=12)
        charlie.last_login_edt = now - timedelta(days=3)
        
        db.session.add_all([admin, alice, bob, charlie])
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
            {'ticker': 'BRK.B', 'company_name': 'Berkshire Hathaway Inc.', 'price': 406.76},
            {'ticker': 'JPM', 'company_name': 'JPMorgan Chase & Co.', 'price': 198.73},
            {'ticker': 'V', 'company_name': 'Visa Inc.', 'price': 271.40}
        ]
        
        # Each user buys some stocks
        for user in [admin, alice, bob, charlie]:
            # Select 3-5 random stocks for each user
            user_stocks = random.sample(stocks, random.randint(3, 5))
            
            for stock in user_stocks:
                # Decide quantity (between 5 and 50 shares)
                quantity = random.randint(5, 50)
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
                
                # Maybe create a trading post about this purchase (50% chance)
                if random.choice([True, False]):
                    # Create the trading post first
                    post = TradingPost(
                        user_id=user.id,
                        title=f"Just bought {stock['ticker']}!",
                        content=f"I believe {stock['company_name']} has great potential for growth. Adding {quantity} shares to my portfolio at ${price:.2f}.",
                        ticker=stock['ticker'],
                        trade_type='buy',
                        quantity=quantity,
                        price=price,
                        is_public=True
                    )
                    post_time = user.created_at_edt + timedelta(days=random.randint(1, 10))
                    post.created_at = post_time
                    post.likes = random.randint(0, 15)
                    post.dislikes = random.randint(0, 5)
                    db.session.add(post)
                    # Flush to get the post ID
                    db.session.flush()
                    
                    # Create purchase transaction linked to the post
                    transaction = Transaction(
                        user_id=user.id,
                        ticker=stock['ticker'],
                        transaction_type='buy',
                        quantity=quantity,
                        price=price
                    )
                    transaction.timestamp = post_time - timedelta(minutes=random.randint(1, 10))
                    transaction.trading_post_id = post.id
                    db.session.add(transaction)
                    
                    # Add comments to some posts
                    if random.choice([True, False, False]):  # 33% chance
                        # Find a random user that isn't the post author
                        commenters = [u for u in [admin, alice, bob, charlie] if u.id != user.id]
                        if commenters:
                            commenter = random.choice(commenters)
                            comment = Comment(
                                post_id=post.id,
                                user_id=commenter.id,
                                content=random.choice([
                                    f"Great pick! I've been watching {stock['ticker']} for a while too.",
                                    f"What's your price target for {stock['ticker']}?",
                                    f"Bold move. I'm not convinced about {stock['ticker']} right now.",
                                    f"I like your analysis. Might add some to my portfolio too!"
                                ])
                            )
                            comment.created_at = post.created_at + timedelta(hours=random.randint(1, 24))
                            db.session.add(comment)
                else:
                    # Just create a transaction without a post
                    transaction = Transaction(
                        user_id=user.id,
                        ticker=stock['ticker'],
                        transaction_type='buy',
                        quantity=quantity,
                        price=price
                    )
                    transaction.timestamp = user.created_at_edt + timedelta(days=random.randint(1, 10))
                    db.session.add(transaction)
                
                # Deduct the amount from user's balance
                user.balance -= quantity * price
        
        # Set up follows between users
        alice.follow(bob)
        alice.follow(charlie)
        bob.follow(alice)
        charlie.follow(alice)
        charlie.follow(bob)
        
        # Commit all changes
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    if reset_database():
        seed_database()
        print("Database reset and seeding complete!")
        print("You can now run the application with 'python run.py'")
        print("\nSample user credentials:")
        print("Admin: net_id='admin', password='password123'")
        print("Alice: net_id='acb123', password='password123'")
        print("Bob:   net_id='bxs456', password='password123'")
        print("Charlie: net_id='czt789', password='password123'")
    else:
        print("Database reset was cancelled.") 