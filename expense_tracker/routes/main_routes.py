from flask import Blueprint, render_template, redirect, url_for, flash
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

@main_bp.route('/transactions', methods=['GET'])
@login_required
def view_transactions():
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    return render_template('transactions.html', title='Transaction History', transactions=transactions)

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
