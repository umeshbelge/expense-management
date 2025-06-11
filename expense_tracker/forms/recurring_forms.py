from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, IntegerField
from wtforms.fields import DecimalField, DateField
from wtforms.validators import DataRequired, Optional, Length, NumberRange
from wtforms_sqlalchemy.fields import QuerySelectField
from ..models import Category # Assuming Category model is in ..models
from flask_login import current_user # To filter categories
from sqlalchemy import or_ # For OR condition in query

# Using the existing category query function from transaction_forms for consistency
# If it needs to be different, a new one can be defined here.
# For now, let's assume it can be shared or adapted.
# from .transaction_forms import category_query # This would create a circular import if category_query uses current_user

# Define category_query specifically for this form to avoid import issues
# and ensure it's tailored if needed.
def category_query_for_recurring():
    if current_user.is_authenticated:
        return Category.query.filter(
            or_(Category.user_id == current_user.id, Category.user_id.is_(None))
        ).order_by(Category.name).all()
    # Fallback for theoretical case where form is used by unauthenticated user
    return Category.query.filter(Category.user_id.is_(None)).order_by(Category.name).all()


FREQUENCIES = [('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('yearly', 'Yearly')]
DAYS_OF_WEEK = [(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'),
                (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')]

class RecurringTransactionRuleForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired(), Length(max=150)])
    amount = DecimalField('Amount', validators=[DataRequired()], places=2)
    type = SelectField('Type', choices=[('income', 'Income'), ('expense', 'Expense')], validators=[DataRequired()])
    category = QuerySelectField('Category',
                                query_factory=category_query_for_recurring,
                                get_label='name',
                                allow_blank=False,
                                validators=[DataRequired()])
    payment_mode = StringField('Payment Mode', validators=[Optional(), Length(max=50)])

    frequency = SelectField('Frequency', choices=FREQUENCIES, validators=[DataRequired()])
    interval = IntegerField('Interval (e.g., every 1 week, every 2 months)', default=1, validators=[DataRequired(), NumberRange(min=1)])

    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date (Optional)', format='%Y-%m-%d', validators=[Optional()])

    # Conditional validators for day_of_week and day_of_month might be needed in the route
    # or by overriding validate() if we want form-level validation based on frequency.
    # For now, making them optional and handling logic in route/model.
    day_of_week = SelectField('Day of Week (for weekly frequency)',
                              choices=[('', '-- Not Applicable --')] + DAYS_OF_WEEK,
                              validators=[Optional()],
                              coerce=int, # Important to coerce to int, or handle string value
                              default='') # Default to empty string for "-- Not Applicable --"

    day_of_month = IntegerField('Day of Month (1-31, for monthly/yearly frequency)',
                               validators=[Optional(), NumberRange(min=1, max=31)])

    submit = SubmitField('Save Rule')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        if self.start_date.data and self.end_date.data and self.end_date.data < self.start_date.data:
            self.end_date.errors.append('End date cannot be before start date.')
            return False

        if self.frequency.data == 'weekly':
            if self.day_of_week.data is None or self.day_of_week.data == '': # Check for empty string from default
                self.day_of_week.errors.append('Day of week is required for weekly frequency.')
                return False
        elif self.frequency.data in ['monthly', 'yearly']:
            if not self.day_of_month.data:
                self.day_of_month.errors.append('Day of month is required for monthly or yearly frequency.')
                return False
        return True
