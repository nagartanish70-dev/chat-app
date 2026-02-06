"""
Migration script to move data from JSON files to SQL database
Run this once to migrate your existing data
"""

import json
import sys
from database import SessionLocal, init_db, User, Message, OnlineUser
from datetime import datetime
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def migrate_users(db):
    print("📋 Migrating users...")
    try:
        with open("./users.json", "r") as f:
            users_data = json.load(f)
        
        user_map = {}  # Map username to user_id
        
        for username, user_info in users_data.items():
            # Check if user already exists
            existing_user = db.query(User).filter(User.username == username).first()
            if existing_user:
                print(f"   ⚠️  User '{username}' already exists, skipping...")
                user_map[username] = existing_user.id
                continue
            
            user = User(
                username=username,
                password=user_info.get("password", hash_password("password123")),
                plain_password=user_info.get("plain_password", "password123"),
                is_admin=user_info.get("admin", False),
                is_banned=False
            )
            db.add(user)
            db.flush()  # Get the ID
            user_map[username] = user.id
            print(f"   ✅ Migrated user: {username}")
        
        db.commit()
        print(f"✅ Migrated {len(users_data)} users")
        return user_map
    
    except FileNotFoundError:
        print("⚠️  users.json not found, skipping user migration")
        return {}
    except Exception as e:
        print(f"❌ Error migrating users: {e}")
        db.rollback()
        return {}

def migrate_messages(db, user_map):
    print("\n📋 Migrating messages...")
    try:
        with open("./messages.json", "r") as f:
            messages_data = json.load(f)
        
        migrated = 0
        for msg_data in messages_data:
            from_username = msg_data.get("from_user")
            to_username = msg_data.get("to_user")
            
            # Skip if users don't exist in map
            if from_username not in user_map or to_username not in user_map:
                print(f"   ⚠️  Skipping message from {from_username} to {to_username} (users not found)")
                continue
            
            # Check if message already exists
            msg_id = msg_data.get("id", str(datetime.utcnow().timestamp()))
            existing_msg = db.query(Message).filter(Message.id == msg_id).first()
            if existing_msg:
                continue
            
            message = Message(
                id=msg_id,
                from_user_id=user_map[from_username],
                to_user_id=user_map[to_username],
                message=msg_data.get("message", ""),
                file_url=msg_data.get("file_url"),
                file_name=msg_data.get("file_name"),
                file_type=msg_data.get("file_type"),
                timestamp=datetime.fromisoformat(msg_data.get("timestamp", datetime.utcnow().isoformat())),
                edited=msg_data.get("edited", False),
                deleted_for_sender=msg_data.get("deleted_for", {}).get(from_username, False),
                deleted_for_receiver=msg_data.get("deleted_for", {}).get(to_username, False),
                deleted_for_everyone=msg_data.get("deleted_for_everyone", False)
            )
            db.add(message)
            migrated += 1
        
        db.commit()
        print(f"✅ Migrated {migrated} messages")
    
    except FileNotFoundError:
        print("⚠️  messages.json not found, skipping message migration")
    except Exception as e:
        print(f"❌ Error migrating messages: {e}")
        db.rollback()

def migrate_banned_users(db, user_map):
    print("\n📋 Migrating banned users...")
    try:
        with open("./banned_users.json", "r") as f:
            banned_users = json.load(f)
        
        for username in banned_users:
            if username in user_map:
                user = db.query(User).filter(User.id == user_map[username]).first()
                if user:
                    user.is_banned = True
                    print(f"   ✅ Banned user: {username}")
        
        db.commit()
        print(f"✅ Migrated {len(banned_users)} banned users")
    
    except FileNotFoundError:
        print("⚠️  banned_users.json not found, skipping banned users migration")
    except Exception as e:
        print(f"❌ Error migrating banned users: {e}")
        db.rollback()

def main():
    print("=" * 60)
    print("🚀 Starting JSON to SQL Database Migration")
    print("=" * 60)
    
    # Initialize database
    print("\n📦 Initializing database...")
    init_db()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Migrate users first (needed for foreign keys)
        user_map = migrate_users(db)
        
        if not user_map:
            print("\n⚠️  No users migrated. Creating default admin user...")
            admin = User(
                username="admin",
                password=hash_password("admin"),
                plain_password="admin",
                is_admin=True
            )
            db.add(admin)
            db.commit()
            print("✅ Default admin user created (username: admin, password: admin)")
        
        # Migrate messages
        migrate_messages(db, user_map)
        
        # Migrate banned users
        migrate_banned_users(db, user_map)
        
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        print("\n📝 Next steps:")
        print("1. Test the application with the new database")
        print("2. Backup your JSON files")
        print("3. Update your deployment configuration")
        print("\n⚠️  Remember to set DATABASE_URL environment variable for PostgreSQL")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
