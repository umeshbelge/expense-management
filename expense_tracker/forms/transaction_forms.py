from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, TextAreaField
from wtforms.fields import DecimalField # Corrected import for DecimalField
from wtforms.fields import DateField # Corrected import for DateField
from wtforms.validators import DataRequired, Optional, Length
from wtforms_sqlalchemy.fields import QuerySelectField
from ..models import Category
from datetime import datetime
from flask_login import current_user # Import current_user
from sqlalchemy import or_ # Import or_

def category_query():
    if current_user.is_authenticated:
        # Show user's own categories and global (user_id is None) categories
        return Category.query.filter(
            or_(Category.user_id == current_user.id, Category.user_id.is_(None))
        ).order_by(Category.name).all()
    else:
        # For unauthenticated users (should ideally not happen if form is on a protected page)
        # or as a fallback, show only global categories
        return Category.query.filter(Category.user_id.is_(None)).order_by(Category.name).all()

# Query for the filter form - needs to be separate as it has different blank_text logic.
def category_query_for_filter():
    if current_user.is_authenticated:
        return Category.query.filter(
            or_(Category.user_id == current_user.id, Category.user_id.is_(None))
        ).order_by(Category.name).all()
    return Category.query.filter(Category.user_id.is_(None)).order_by(Category.name).all()

class TransactionForm(FlaskForm):
    amount = DecimalField('Amount', validators=[DataRequired()], places=2)
    type = SelectField('Type', choices=[('income', 'Income'), ('expense', 'Expense')], validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()], default=datetime.utcnow)
    description = TextAreaField('Description', validators=[Optional(), Length(max=200)])
    payment_mode = StringField('Payment Mode', validators=[Optional(), Length(max=50)])
    category = QuerySelectField('Category',
                                query_factory=category_query,
                                get_label='name',
                                allow_blank=False,
                                validators=[DataRequired()])
    submit = SubmitField('Add Transaction')

class TransactionFilterForm(FlaskForm):
    category = QuerySelectField('Category',
                                query_factory=category_query_for_filter,
                                get_label='name',
                                allow_blank=True,
                                blank_text='-- All Categories --')
    type = SelectField('Type',
                       choices=[('', '-- All Types --'), ('income', 'Income'), ('expense', 'Expense')],
                       default='')
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Filter')
