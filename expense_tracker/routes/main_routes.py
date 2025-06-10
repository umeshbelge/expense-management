from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from datetime import datetime
from decimal import Decimal # Import Decimal for calculations

from ..forms import TransactionForm
from ..models import Transaction
from ..extensions import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()

    total_income = Decimal(0.0)
    total_expenses = Decimal(0.0)

    for t in transactions:
        if t.type == 'income':
            total_income += t.amount
        elif t.type == 'expense':
            total_expenses += t.amount

    current_balance = total_income - total_expenses

    return render_template(
        'dashboard.html',
        title='Dashboard',
        transactions=transactions,
        total_income=total_income,
        total_expenses=total_expenses,
        current_balance=current_balance
    )

from ..forms import TransactionForm, TransactionFilterForm # Added TransactionFilterForm

@main_bp.route('/transactions', methods=['GET'])
@login_required
def view_transactions():
    # Initialize the form, populating it from request.args for GET requests
    filter_form = TransactionFilterForm(request.args, meta={'csrf': False})

    query = Transaction.query.filter_by(user_id=current_user.id)

    # It's better to check if the form field has data rather than directly from request.args
    # QuerySelectField will have data as a Category object if selected, or None if blank is allowed and chosen.
    # SelectField will have data as the choice value (e.g., 'income', 'expense') or empty string if default/blank.

    if filter_form.category.data: # filter_form.category.data will be the Category object
        query = query.filter(Transaction.category_id == filter_form.category.data.id)

    if filter_form.type.data: # filter_form.type.data will be 'income' or 'expense'
        query = query.filter(Transaction.type == filter_form.type.data)

    transactions = query.order_by(Transaction.date.desc()).all()

    return render_template('transactions.html',
                           title='Transaction History',
                           transactions=transactions,
                           filter_form=filter_form)

@main_bp.route('/transaction/<int:transaction_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.user_id != current_user.id:
        from flask import abort
        from flask import abort, request # Added request
        abort(403) # Forbidden

    form = TransactionForm(obj=transaction)
    if request.method == 'GET':
        # Ensure the category field is correctly populated on GET.
        # obj=transaction should ideally handle this if transaction.category (field name)
        # or transaction.category_ref (relationship name) provides the Category object.
        # Explicitly setting helps if there's ambiguity or name mismatch.
        form.category.data = transaction.category_ref

    if form.validate_on_submit():
        transaction.amount = form.amount.data
        transaction.type = form.type.data
        transaction.date = form.date.data
        transaction.description = form.description.data
        transaction.payment_mode = form.payment_mode.data
        transaction.category_id = form.category.data.id # form.category.data is the selected Category object

        db.session.commit()
        flash('Transaction updated successfully!', 'success')
        return redirect(url_for('main.view_transactions'))

    return render_template('edit_transaction.html', title='Edit Transaction', form=form, transaction_id=transaction.id)

@main_bp.route('/transaction/<int:transaction_id>/delete', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.user_id != current_user.id:
        abort(403) # Forbidden

    db.session.delete(transaction)
    db.session.commit()
    flash('Transaction deleted successfully!', 'success')
    return redirect(url_for('main.view_transactions'))

@main_bp.route('/transaction/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    form = TransactionForm()
    if form.validate_on_submit():
        new_transaction = Transaction(
            amount=form.amount.data,
            type=form.type.data,
            date=form.date.data,
            description=form.description.data,
            payment_mode=form.payment_mode.data,
            category_id=form.category.data.id, # category.data will be the Category object
            user_id=current_user.id
        )
        db.session.add(new_transaction)
        db.session.commit()
        flash('Transaction added successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('add_transaction.html', title='Add Transaction', form=form)
