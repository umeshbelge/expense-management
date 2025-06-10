from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, TextAreaField
from wtforms.fields import DecimalField # Corrected import for DecimalField
from wtforms.fields import DateField # Corrected import for DateField
from wtforms.validators import DataRequired, Optional, Length
from wtforms_sqlalchemy.fields import QuerySelectField
from ..models import Category
from datetime import datetime

def category_query():
    # For now, allow all categories (global and user-specific if they exist)
    # Later, this could be filtered by current_user.id for user-specific categories + global
    return Category.query.order_by(Category.name).all()

class TransactionForm(FlaskForm):
    amount = DecimalField('Amount', validators=[DataRequired()], places=2)
    type = SelectField('Type', choices=[('income', 'Income'), ('expense', 'Expense')], validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()], default=datetime.utcnow)
    description = TextAreaField('Description', validators=[Optional(), Length(max=200)])
    payment_mode = StringField('Payment Mode', validators=[Optional(), Length(max=50)])
    category = QuerySelectField('Category',
                                query_factory=category_query,
                                get_label='name',
                                allow_blank=False, # Consider allow_blank=True with text "Choose..." if preferred
                                validators=[DataRequired()])
    submit = SubmitField('Add Transaction')
