from datetime import datetime, timezone

from werkzeug.security import generate_password_hash, check_password_hash

from database import db


def utcnow():
    # Modern replacement for the deprecated datetime.utcnow(); kept naive to
    # match the (timezone-less) DateTime columns used across the schema.
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        # Serializer omits the password hash: sensitive data never leaves the API.
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at),
        }

    def set_password(self, pwd):
        # Adaptive hashing (werkzeug pbkdf2) instead of fast, insecure md5.
        self.password = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self.password, pwd)

    def is_admin(self):
        return self.role == 'admin'
