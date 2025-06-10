from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_ # For OR conditions in filter

from ..forms import CategoryForm
from ..models import Category
from ..extensions import db

category_bp = Blueprint('category', __name__, url_prefix='/category')

@category_bp.route('/', methods=['GET', 'POST']) # Changed to '/' as blueprint has prefix
@login_required
def manage_categories():
    form = CategoryForm()
    if form.validate_on_submit():
        category_name = form.name.data
        # Case-insensitive check for duplicates (user's own or global)
        existing_category = Category.query.filter(
            Category.name.ilike(category_name),
            or_(Category.user_id == current_user.id, Category.user_id.is_(None))
        ).first()

        if existing_category:
            if existing_category.user_id is None and current_user.is_authenticated:
                 flash(f'A global category named "{existing_category.name}" already exists. You can use it directly.', 'info')
            elif existing_category.user_id == current_user.id:
                 flash(f'You already have a category named "{existing_category.name}".', 'warning')
            else: # Should not happen with the query logic but as a fallback
                 flash(f'Category "{category_name}" already exists.', 'warning')
        else:
            new_category = Category(name=category_name, user_id=current_user.id)
            db.session.add(new_category)
            db.session.commit()
            flash(f'Category "{category_name}" added successfully!', 'success')
        return redirect(url_for('category.manage_categories'))

    predefined_categories = Category.query.filter_by(user_id=None).order_by(Category.name).all()
    user_categories = Category.query.filter_by(user_id=current_user.id).order_by(Category.name).all()

    return render_template('categories.html',
                           title='Manage Categories',
                           form=form,
                           predefined_categories=predefined_categories,
                           user_categories=user_categories)
