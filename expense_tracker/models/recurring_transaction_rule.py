from ..extensions import db
from datetime import datetime # Though not directly used for column defaults here, good to have for model context

class RecurringTransactionRule(db.Model):
    __tablename__ = 'recurring_transaction_rule'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True) # Added index
    description = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # "income" or "expense"
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False, index=True) # Added index
    payment_mode = db.Column(db.String(50), nullable=True)

    frequency = db.Column(db.String(20), nullable=False)  # e.g., "daily", "weekly", "monthly", "yearly"
    interval = db.Column(db.Integer, nullable=False, default=1) # e.g., every 1 month, every 2 weeks

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True) # Rule becomes inactive after this date

    next_occurrence_date = db.Column(db.Date, nullable=False, index=True) # Important for scheduling/processing

    # Specifics for frequencies
    day_of_week = db.Column(db.Integer, nullable=True)  # For weekly: 0=Monday, 6=Sunday
    day_of_month = db.Column(db.Integer, nullable=True) # For monthly/yearly: 1-31. Can also store negative for "last day", etc.
                                                       # Or special values like "last" (-1), "2nd_last" (-2) if we want to get fancy.
                                                       # For yearly, this could be day of year, or use month + day_of_month.
                                                       # For simplicity, let's assume for 'monthly', it's the day number.
                                                       # For 'yearly', it might be month and day_of_month.

    # Relationships
    category = db.relationship('Category') # No backref needed here unless Category needs to see rules.
    # user_ref will be defined by backref in User model

    def __repr__(self):
        return f'<RecurringTransactionRule {self.id} - "{self.description}" for user {self.user_id}>'
