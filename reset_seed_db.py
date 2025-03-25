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
        
        # Create admin user
        print("Creating users...")
        admin = User(
            net_id='admin',
            password='password123',
            first_name='Admin',
            last_name='User'
        )
        admin.balance = 100000.00  # $100,000 starting balance
        
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
                password='password123',
                first_name=first_name,
                last_name='SEED'  # All have SEED as last name for identification
            )
            
            # Set a random balance between $40,000 and $120,000
            seed_user.balance = random.uniform(40000.00, 120000.00)
            
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
            # Select 4-8 random stocks for each user (increased from 3-6)
            user_stocks = random.sample(stocks, random.randint(4, 8))
            
            for stock in user_stocks:
                # Decide quantity (between 5 and 80 shares - increased max)
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
                
                # SEED users have higher chance of creating a trading post (80% vs 50% for admin)
                post_chance = 0.8 if user.last_name == 'SEED' else 0.5
                
                # Maybe create a trading post about this purchase
                if random.random() < post_chance:
                    # Create post titles and content that reference the user is a SEED user if applicable
                    title = f"Just bought {stock['ticker']}!"
                    
                    # Different content based on user type
                    if user.last_name == 'SEED':
                        content_options = [
                            f"As a seed investor, I see great potential in {stock['company_name']}. Adding {quantity} shares at ${price:.2f}.",
                            f"My seed portfolio now includes {quantity} shares of {stock['ticker']} at ${price:.2f}. Expecting great returns!",
                            f"Just added {stock['ticker']} to my seed investments. {quantity} shares at ${price:.2f}.",
                            f"Seed strategy update: Acquired {quantity} shares of {stock['company_name']} at ${price:.2f}.",
                            f"Bullish on {stock['ticker']} for Q3! Added {quantity} shares to my seed portfolio at ${price:.2f}.",
                            f"Technical analysis shows {stock['ticker']} is undervalued. I've added {quantity} shares to my seed investments."
                        ]
                    else:
                        content_options = [
                            f"I believe {stock['company_name']} has great potential for growth. Adding {quantity} shares to my portfolio at ${price:.2f}.",
                            f"Just invested in {quantity} shares of {stock['ticker']} at ${price:.2f}. Thoughts?",
                            f"Added {stock['ticker']} to my portfolio: {quantity} shares at ${price:.2f}.",
                            f"Bullish on {stock['company_name']}! Bought {quantity} shares at ${price:.2f}."
                        ]
                    
                    content = random.choice(content_options)
                    
                    # Create the trading post
                    post = TradingPost(
                        user_id=user.id,
                        title=title,
                        content=content,
                        ticker=stock['ticker'],
                        trade_type='buy',
                        quantity=quantity,
                        price=price,
                        is_public=True
                    )
                    post_time = user.created_at_edt + timedelta(days=random.randint(1, 10))
                    post.created_at = post_time
                    
                    # SEED users get more engagement on their posts
                    if user.last_name == 'SEED':
                        post.likes = random.randint(5, 30)
                        post.dislikes = random.randint(0, 10)
                    else:
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
                    comment_chance = 0.7 if user.last_name == 'SEED' else 0.4  # Increased chances
                    if random.random() < comment_chance:
                        # Find a random user that isn't the post author
                        commenters = [u for u in all_users if u.id != user.id]
                        # Get 1-4 random commenters (increased from 1-3)
                        selected_commenters = random.sample(commenters, min(len(commenters), random.randint(1, 4)))
                        
                        for commenter in selected_commenters:
                            # Customize comments based on commenter type
                            if commenter.last_name == 'SEED':
                                seed_comments = [
                                    f"Fellow seed investor here! What's your long-term target for {stock['ticker']}?",
                                    f"Great seed investment choice! I also have {stock['ticker']} in my portfolio.",
                                    f"Seed investors unite! I've been watching {stock['ticker']} closely too.",
                                    f"As a seed investor, I'm also bullish on {stock['company_name']}. Good move!",
                                    f"What catalysts are you watching for {stock['ticker']} in the coming months?",
                                    f"I've been analyzing {stock['ticker']}'s financials too. Strong buy signal!",
                                    f"Wise choice for a seed portfolio. Their latest earnings exceeded expectations."
                                ]
                                comment_text = random.choice(seed_comments)
                            else:
                                regular_comments = [
                                    f"Great pick! I've been watching {stock['ticker']} for a while too.",
                                    f"What's your price target for {stock['ticker']}?",
                                    f"Bold move. I'm not convinced about {stock['ticker']} right now.",
                                    f"I like your analysis. Might add some to my portfolio too!"
                                ]
                                comment_text = random.choice(regular_comments)
                            
                            comment = Comment(
                                post_id=post.id,
                                user_id=commenter.id,
                                content=comment_text
                            )
                            comment.created_at = post.created_at + timedelta(hours=random.randint(1, 24))
                            db.session.add(comment)
                            
                            # 40% chance of a reply to this comment
                            if random.random() < 0.4:
                                reply_options = [
                                    f"Thanks for your feedback! I'm targeting ${stock['price'] * 1.2:.2f} in the next quarter.",
                                    f"Good point! I'm monitoring their upcoming product releases closely.",
                                    f"I appreciate your perspective. Let's compare notes after earnings!",
                                    f"Exactly my thinking. The sector is heating up!"
                                ]
                                
                                reply = Comment(
                                    post_id=post.id,
                                    user_id=user.id,  # Original poster replies
                                    content=f"@{commenter.first_name}: {random.choice(reply_options)}",  # Mentioning the user instead of using parent_comment_id
                                )
                                reply.created_at = comment.created_at + timedelta(hours=random.randint(1, 12))
                                db.session.add(reply)
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
        print("Setting up social connections...")
        
        # Create follows for SEED users - each follows 3-8 random other users
        for user in seed_users:
            # Select 3-8 random users to follow (excluding self)
            potential_follows = [u for u in all_users if u.id != user.id]
            follows_count = min(len(potential_follows), random.randint(3, 8))
            users_to_follow = random.sample(potential_follows, follows_count)
            
            for follow_user in users_to_follow:
                user.follow(follow_user)
                
                # 50% chance that the follow is reciprocal
                if random.random() < 0.5:
                    follow_user.follow(user)
        
        # Add sell transactions for some stocks (new section)
        print("Creating sell transactions...")
        for user in seed_users:
            # Get user's holdings
            holdings = [h for h in db.session.query(StockHolding).filter_by(user_id=user.id).all()]
            
            # Sell some portion of 1-3 random holdings
            if holdings:
                sell_holdings = random.sample(holdings, min(len(holdings), random.randint(1, 3)))
                
                for holding in sell_holdings:
                    # Sell between 30-70% of shares
                    sell_percent = random.uniform(0.3, 0.7)
                    sell_quantity = int(holding.quantity * sell_percent)
                    
                    if sell_quantity > 0:
                        # Current price with some randomness (±5%)
                        sell_price = holding.current_price * (1 + random.uniform(-0.05, 0.05))
                        
                        # Create sell transaction
                        sell_transaction = Transaction(
                            user_id=user.id,
                            ticker=holding.ticker,
                            transaction_type='sell',
                            quantity=sell_quantity,
                            price=sell_price
                        )
                        sell_transaction.timestamp = now - timedelta(days=random.randint(1, 15))
                        db.session.add(sell_transaction)
                        
                        # 60% chance to create a post about the sale
                        if random.random() < 0.6:
                            sell_post_title = f"Sold some {holding.ticker} shares"
                            
                            sell_content_options = [
                                f"Taking profits on {holding.ticker}. Sold {sell_quantity} shares at ${sell_price:.2f}, still bullish long-term.",
                                f"Rebalancing my seed portfolio - sold {sell_quantity} shares of {holding.ticker} at ${sell_price:.2f}.",
                                f"Decided to take some gains on {holding.ticker} (${sell_price:.2f}). Still holding {holding.quantity - sell_quantity} shares.",
                                f"Partial exit from {holding.ticker} position ({sell_quantity} shares at ${sell_price:.2f}) to fund other opportunities."
                            ]
                            
                            sell_post = TradingPost(
                                user_id=user.id,
                                title=sell_post_title,
                                content=random.choice(sell_content_options),
                                ticker=holding.ticker,
                                trade_type='sell',
                                quantity=sell_quantity,
                                price=sell_price,
                                is_public=True
                            )
                            sell_post.created_at = sell_transaction.timestamp + timedelta(minutes=random.randint(1, 10))
                            sell_post.likes = random.randint(3, 20)
                            sell_post.dislikes = random.randint(0, 8)
                            db.session.add(sell_post)
                            db.session.flush()
                            
                            # Link transaction to post
                            sell_transaction.trading_post_id = sell_post.id
                            
                            # Add some comments to sell posts too
                            if random.random() < 0.6:
                                commenters = [u for u in all_users if u.id != user.id]
                                selected_commenters = random.sample(commenters, min(len(commenters), random.randint(1, 3)))
                                
                                sell_comments = [
                                    f"Smart move taking profits. What are you eyeing next?",
                                    f"Good timing! {holding.ticker} seems a bit overvalued now.",
                                    f"I'm still holding my position, but understand the profit-taking.",
                                    f"Do you think it will pull back more? Considering adding to my position."
                                ]
                                
                                for commenter in selected_commenters:
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
        print("Database seeded successfully!")
        
        # Print summary of seed users
        print("\nCreated the following users:")
        print(f"- Admin User (net_id: admin, password: password123)")
        print("\nCreated the following SEED users:")
        for user in seed_users:
            print(f"- {user.first_name} SEED (net_id: {user.net_id}, password: password123)")
            
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

if __name__ == "__main__":
    if reset_database():
        seed_database()
        print("Database reset and seeding complete!")
        print("You can now run the application with 'python run.py'")
        print("\nSample user credentials:")
        print("Admin: net_id='admin', password='password123'")
        print("(Plus SEED users listed above)")
    else:
        print("Database reset was cancelled.") 