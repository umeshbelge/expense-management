from ..models import Category
from ..extensions import db

PREDEFINED_CATEGORIES = [
    "Food", "Transport", "Salary", "Bills", "Entertainment",
    "Healthcare", "Shopping", "Other Income", "Other Expense",
    "Groceries", "Utilities", "Rent/Mortgage", "Education",
    "Gifts", "Travel", "Investment"
]

def seed_initial_categories():
    """
    Seeds the database with predefined global categories if they don't already exist.
    These categories will have user_id set to None.
    """
    print("Attempting to seed initial categories...")

    # Check if the category table exists. If not, migrations probably haven't run.
    if not db.engine.dialect.has_table(db.engine.connect(), "category"):
        print("Category table does not exist. Skipping seeding. Run 'flask db upgrade' first.")
        return

    existing_category_names = {cat.name for cat in Category.query.all()}

    categories_to_add = []
    for category_name in PREDEFINED_CATEGORIES:
        if category_name not in existing_category_names:
            category = Category(name=category_name, user_id=None) # Global category
            categories_to_add.append(category)
            print(f"Queueing category: {category_name}")
        else:
            print(f"Category '{category_name}' already exists.")

    if categories_to_add:
        try:
            db.session.add_all(categories_to_add)
            db.session.commit()
            print(f"Successfully added {len(categories_to_add)} new categories.")
        except Exception as e:
            db.session.rollback()
            print(f"Error seeding categories: {e}")
    else:
        print("No new categories to seed.")

if __name__ == '__main__':
    # This part is for manual execution if needed, requires app context.
    # You would typically set up a Flask script to run this.
    # Example: flask shell
    # from expense_tracker.utils.data_seeding import seed_initial_categories
    # seed_initial_categories()
    print("To run seeding manually, use 'flask shell' and call seed_initial_categories() within app context.")
