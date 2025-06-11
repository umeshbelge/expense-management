from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from datetime import datetime, date # Import date for date comparisons

from ..forms import RecurringTransactionRuleForm
from ..models import RecurringTransactionRule, Category
from ..extensions import db
from ..utils.recurring_processor import calculate_first_occurrence # Import the new helper

recurring_bp = Blueprint('recurring', __name__, url_prefix='/recurring')

# The old placeholder calculate_next_occurrence is now replaced by
# determine_actual_next_occurrence in recurring_processor.py and calculate_first_occurrence for setup.

@recurring_bp.route('/')
@login_required
def list_rules():
    rules = RecurringTransactionRule.query.filter_by(user_id=current_user.id).order_by(RecurringTransactionRule.next_occurrence_date).all()
    return render_template('recurring/list_recurring.html', rules=rules, title="Recurring Transactions")

@recurring_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_rule():
    form = RecurringTransactionRuleForm()
    if form.validate_on_submit():
        initial_next_occurrence = calculate_first_occurrence(
            start_date=form.start_date.data,
            frequency=form.frequency.data,
            interval=form.interval.data,
            day_of_week_int=form.day_of_week.data if form.day_of_week.data != '' else None,
            day_of_month=form.day_of_month.data
        )

        rule = RecurringTransactionRule(
            user_id=current_user.id,
            description=form.description.data,
            amount=form.amount.data,
            type=form.type.data,
            category_id=form.category.data.id,
            payment_mode=form.payment_mode.data,
            frequency=form.frequency.data,
            interval=form.interval.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            day_of_week=form.day_of_week.data if form.day_of_week.data != '' else None, # Store None if not applicable
            day_of_month=form.day_of_month.data,
            next_occurrence_date=initial_next_occurrence # Set based on calculation
        )
        db.session.add(rule)
        db.session.commit()
        flash('New recurring transaction rule added successfully!', 'success')
        return redirect(url_for('recurring.list_rules'))

    # Set default for day_of_week if not provided by GET (e.g. initial form load)
    if request.method == 'GET' and form.day_of_week.data is None:
        form.day_of_week.data = ''


    return render_template('recurring/add_recurring.html', form=form, title="Add Recurring Rule")

@recurring_bp.route('/<int:rule_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_rule(rule_id):
    rule = RecurringTransactionRule.query.get_or_404(rule_id)
    if rule.user_id != current_user.id:
        abort(403)

    form = RecurringTransactionRuleForm(obj=rule)
    if request.method == 'GET' and rule.day_of_week is None: # Handle None for day_of_week from db
         form.day_of_week.data = ''


    if form.validate_on_submit():
        rule.description = form.description.data
        rule.amount = form.amount.data
        rule.type = form.type.data
        rule.category_id = form.category.data.id
        rule.payment_mode = form.payment_mode.data
        rule.frequency = form.frequency.data
        rule.interval = form.interval.data

        new_start_date = form.start_date.data
        # If start date or critical frequency parameters change, recalculate next_occurrence
        # If start date or any frequency parameters change, recalculate next_occurrence
        # This ensures the next_occurrence_date is correctly set if the rule's timing logic changes.
        if rule.start_date != new_start_date or \
           rule.frequency != form.frequency.data or \
           rule.interval != form.interval.data or \
           (rule.day_of_week != (form.day_of_week.data if form.day_of_week.data != '' else None)) or \
           (rule.day_of_month != form.day_of_month.data):
            rule.next_occurrence_date = calculate_first_occurrence(
                start_date=new_start_date, # Use the new start_date for calculation
                frequency=form.frequency.data,
                interval=form.interval.data,
                day_of_week_int=form.day_of_week.data if form.day_of_week.data != '' else None,
                day_of_month=form.day_of_month.data
            )

        rule.start_date = new_start_date # Assign new start_date to the rule
        rule.end_date = form.end_date.data
        rule.day_of_week = form.day_of_week.data if form.day_of_week.data != '' else None
        rule.day_of_month = form.day_of_month.data

        db.session.commit()
        flash('Recurring transaction rule updated successfully!', 'success')
        return redirect(url_for('recurring.list_rules'))

    return render_template('recurring/edit_recurring.html', form=form, rule=rule, title="Edit Recurring Rule")

@recurring_bp.route('/<int:rule_id>/delete', methods=['POST'])
@login_required
def delete_rule(rule_id):
    rule = RecurringTransactionRule.query.get_or_404(rule_id)
    if rule.user_id != current_user.id:
        abort(403)

    db.session.delete(rule)
    db.session.commit()
    flash('Recurring transaction rule deleted successfully!', 'success')
    return redirect(url_for('recurring.list_rules'))
