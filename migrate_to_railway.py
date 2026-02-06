"""
Migrate data from local SQLite to Railway PostgreSQL
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import User, Message, OnlineUser, Base

# Local SQLite database
local_engine = create_engine('sqlite:///chatapp.db')
LocalSession = sessionmaker(bind=local_engine)

# Railway PostgreSQL database
railway_db_url = os.getenv('DATABASE_URL')
if not railway_db_url:
    print("❌ Error: DATABASE_URL environment variable not set!")
    print("\nTo get your DATABASE_URL:")
    print("1. Go to Railway dashboard")
    print("2. Click on PostgreSQL database")
    print("3. Go to 'Connect' tab")
    print("4. Copy the DATABASE_URL")
    print("\nThen run:")
    print('set DATABASE_URL=your_database_url')
    print('python migrate_to_railway.py')
    exit(1)

# Fix postgres:// to postgresql:// if needed (Railway uses postgres:// but SQLAlchemy needs postgresql://)
if railway_db_url.startswith('postgres://'):
    railway_db_url = railway_db_url.replace('postgres://', 'postgresql://', 1)

railway_engine = create_engine(railway_db_url)
RailwaySession = sessionmaker(bind=railway_engine)

print("🚀 Starting migration to Railway...")
print(f"📍 Local: SQLite (chatapp.db)")
print(f"📍 Remote: PostgreSQL (Railway)")

# Create tables in Railway if they don't exist
Base.metadata.create_all(railway_engine)
print("✅ Tables created/verified in Railway database")

# Migrate users
local_session = LocalSession()
railway_session = RailwaySession()

try:
    # Get all users from local database
    local_users = local_session.query(User).all()
    print(f"\n📋 Found {len(local_users)} users in local database")
    
    migrated_count = 0
    skipped_count = 0
    
    for user in local_users:
        # Check if user already exists in Railway
        existing = railway_session.query(User).filter_by(username=user.username).first()
        
        if existing:
            print(f"⏭️  Skipped: {user.username} (already exists)")
            skipped_count += 1
            continue
        
        # Create new user in Railway
        new_user = User(
            username=user.username,
            password=user.password,
            plain_password=user.plain_password,
            is_admin=user.is_admin,
            is_banned=user.is_banned
        )
        railway_session.add(new_user)
        print(f"✅ Migrated: {user.username} {'(admin)' if user.is_admin else ''}")
        migrated_count += 1
    
    railway_session.commit()
    print(f"\n🎉 Migration completed!")
    print(f"   ✅ Migrated: {migrated_count} users")
    print(f"   ⏭️  Skipped: {skipped_count} users (already existed)")
    
except Exception as e:
    print(f"\n❌ Error during migration: {e}")
    railway_session.rollback()
    raise
finally:
    local_session.close()
    railway_session.close()

print("\n✅ Done! Your users are now on Railway.")
print("🚀 You can now login with your existing accounts in the app!")
