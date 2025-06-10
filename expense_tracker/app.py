import os
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
# from config import Config # Removed direct import at module level
# Import all models to ensure they are registered with SQLAlchemy metadata for Alembic
from .models import User, Category, Transaction
from .extensions import db, migrate, login_manager # Import extensions

# db = SQLAlchemy() # Moved to extensions.py
# migrate = Migrate() # Moved to extensions.py
# login_manager = LoginManager() # Moved to extensions.py
login_manager.login_view = 'auth.login' # Configure login_manager here or in create_app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

import os # Ensure os is imported
def create_app(config_identifier="config.Config"): # Default to string path "config.Config"
    # Calculate project root (assuming app.py is in expense_tracker subfolder)
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    instance_path = os.path.join(project_root, 'instance')

    app = Flask(__name__, instance_path=instance_path, instance_relative_config=False) # instance_relative_config=False as path is absolute

    if config_identifier:
        if isinstance(config_identifier, str):
            # If it's a string, Flask will try to import it.
            # This requires 'config.py' to be in PYTHONPATH.
            try:
                app.config.from_object(config_identifier)
            except (ImportError, ModuleNotFoundError) as e:
                print(f"Failed to load config from string '{config_identifier}': {e}")
                # Fallback to a very basic config if string import fails
                app.config.update(SECRET_KEY='fallback_secret_key', SQLALCHEMY_DATABASE_URI='sqlite:///./instance/fallback.db')
        else:
            # If it's an object (e.g., Config class itself), load directly.
            app.config.from_object(config_identifier)
    else:
        print("Warning: create_app called with no config_identifier. Using fallback config.")
        # Fallback to a very basic config if nothing is provided
        app.config.update(SECRET_KEY='fallback_secret_key_none', SQLALCHEMY_DATABASE_URI='sqlite:///./instance/fallback_none.db')

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Create the instance folder if it doesn't exist
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # with app.app_context():
    #     db.create_all() # Let Flask-Migrate handle table creation

    # Seed initial data
    from .utils.data_seeding import seed_initial_categories
    with app.app_context():
        # seed_initial_categories will now check if the 'category' table exists.
        seed_initial_categories()

    # Register blueprints here
    from .routes import auth_bp, main_bp # Corrected import
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp, url_prefix='/') # Main blueprint can be at root

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('main.dashboard'))
        return redirect(url_for('auth.login'))

    return app

if __name__ == '__main__':
    # This allows running app.py directly, if config.py is in the same dir or PYTHONPATH
    try:
        # Try to import the Config class directly for direct execution
        from config import Config as DirectRunConfigObject
        app_instance = create_app(DirectRunConfigObject) # Pass the actual class
    except ImportError:
        print("Could not import 'config.Config' when running app.py directly. Using default string identifier.")
        # Falls back to create_app("config.Config") which requires config.py in PYTHONPATH
        app_instance = create_app()
    app_instance.run(debug=True)
