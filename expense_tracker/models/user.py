from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db # Changed from ..app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Relationship to Transaction model
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    # categories relationship can be added later if categories become more user-specific
    # categories = db.relationship('Category', backref='user', lazy=True)
    recurring_rules = db.relationship(
        'RecurringTransactionRule',
        backref='user_ref',  # Using user_ref to avoid conflict with Transaction.user
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<User {self.username}>'
