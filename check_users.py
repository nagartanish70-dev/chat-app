from database import *
from sqlalchemy.orm import Session

engine = create_engine('postgresql://postgres:CcValDIiQMMZZQOuIppHNzjeWTcEiXva@tramway.proxy.rlwy.net:54487/railway')
session = Session(engine)

users = session.query(User).all()
print('\n📋 All Users in Production Database:')
print('='*70)
for u in users:
    print(f'Username: {u.username:15} | is_admin: {str(u.is_admin):5} | is_banned: {u.is_banned}')

session.close()
