"""
Create admin user with admin privileges
"""
import os
from database import User, get_db, init_db
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Railway database URL
DATABASE_URL = "postgresql://postgres:CcValDIiQMMZZQOuIppHNzjeWTcEiXva@tramway.proxy.rlwy.net:54487/railway"

engine = create_engine(DATABASE_URL)
session = Session(engine)

# Delete old admin if exists
old_admin = session.query(User).filter_by(username='admin').first()
if old_admin:
    session.delete(old_admin)
    session.commit()
    print("🗑️  Deleted old admin user")

# Create new admin with admin=True
admin = User(
    username='admin',
    password='admin',
    plain_password='admin',
    is_admin=True,
    is_banned=False
)
session.add(admin)
session.commit()
print("✅ Created admin user with admin privileges")

# Verify
admin_check = session.query(User).filter_by(username='admin').first()
print(f"📋 Verification: username={admin_check.username}, is_admin={admin_check.is_admin}")

session.close()
