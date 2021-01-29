from models import db, connect_db, User, Feedback
from app import app

db.drop_all()
db.create_all()

u1 = User.register(username="test1", password="test1",
                   first_name="tester", last_name='testerson', email="test@test.com")
u2 = User.register(username="admin", password="admin", email="admin@admin.com",
                   first_name="Administrator", last_name="Admin")
db.session.add(u1)
db.session.add(u2)
db.session.commit()
u = User.query.filter_by(username='admin').first()
u.is_admin = True
db.session.commit()
