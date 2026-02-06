from database import *
from sqlalchemy.orm import Session

engine = create_engine('postgresql://postgres:CcValDIiQMMZZQOuIppHNzjeWTcEiXva@tramway.proxy.rlwy.net:54487/railway')
session = Session(engine)

# Promote superadmin
admin = session.query(User).filter_by(username='superadmin').first()
if admin:
    admin.is_admin = True
    session.commit()
    print('✅ Superadmin promoted successfully')
    print(f'Username: {admin.username}')
    print(f'Is Admin: {admin.is_admin}')
else:
    print('❌ Superadmin user not found')

session.close()
