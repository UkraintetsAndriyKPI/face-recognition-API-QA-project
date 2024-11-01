from app import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    image = db.Column(db.String(256), nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'
