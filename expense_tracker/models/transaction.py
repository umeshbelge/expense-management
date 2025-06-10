from ..extensions import db # Changed from ..app import db
from datetime import datetime
from sqlalchemy.types import Numeric # For precision with currency

class Transaction(db.Model):
    __tablename__ = 'transaction' # Explicitly setting table name

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(Numeric(10, 2), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # "income" or "expense"
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    description = db.Column(db.String(200), nullable=True)
    payment_mode = db.Column(db.String(50), nullable=True) # e.g., 'Cash', 'Credit Card', 'Online'

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # user relationship will be backref'd from User model
    # category relationship is backref'd as 'category_ref' from Category model

    def __repr__(self):
        return f'<Transaction {self.id} - {self.type} - {self.amount}>'
