# Expense Tracker Application

## Description

A web-based application to help users track their income and expenses, manage categories, view transaction history, and set up recurring transactions.

## Features

*   User registration and login
*   Dashboard with financial summary (total income, expenses, balance) and monthly expense chart
*   Add, edit, delete, and view transactions
*   Manage predefined and custom categories (add, edit, delete)
*   Filter transaction history (by category, type, date range)
*   Define and manage recurring transaction rules
*   Manually trigger processing of recurring transactions via CLI command

## Prerequisites

*   Python 3.8+ (Python 3.7 might also work but 3.8+ is recommended)
*   pip (Python package installer)
*   Git (for cloning the repository)

## Setup and Installation

1.  **Clone the Repository:**
    If you have access to the repository, clone it to your local machine:
    ```bash
    git clone <repository_url>
    cd <repository_folder_name>
    ```
    (Replace `<repository_url>` and `<repository_folder_name>` with actual values. If you are running this in an environment where the code is already present, you can skip this step and navigate to the project's root directory.)

2.  **Create and Activate a Virtual Environment:**
    It's highly recommended to use a virtual environment to manage project dependencies.

    *   On macOS and Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    You should see `(venv)` at the beginning of your command prompt.

3.  **Install Dependencies:**
    Install all the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

The application's primary configuration is in `config.py` located at the root of the project.
*   **Secret Key:** Ensure `SECRET_KEY` is set in `config.py`. This is crucial for session security.
*   **Database:** The default configuration uses SQLite. The database file (`app.db`) will be created in an `instance` folder in your project root.

## Database Setup

The application uses Flask-Migrate to manage database schema changes.

1.  **Initialize the Migrations Folder (if it doesn't exist):**
    If you've cloned a repository that already has a `migrations` folder, you can usually skip this. If you are starting from scratch or the folder is missing:
    ```bash
    # Ensure FLASK_APP is set (see next section) before running flask db commands
    # export FLASK_APP=expense_tracker.app:create_app  (macOS/Linux)
    # set FLASK_APP=expense_tracker.app:create_app    (Windows CMD)
    # $env:FLASK_APP="expense_tracker.app:create_app" (Windows PowerShell)

    flask db init
    ```
    This command creates the `migrations` directory.

2.  **Apply Migrations:**
    To create the database tables based on the models and apply any pending schema changes:
    ```bash
    # Ensure FLASK_APP is set as described above
    flask db upgrade
    ```
    This command should be run after the initial setup and any time new migration scripts are added to the project. The initial category seeding also happens during this process if the tables are newly created.

## Running the Development Server

1.  **Set Environment Variables:**
    The application needs `FLASK_APP` to know how to load itself. For development, `FLASK_DEBUG=1` is also recommended.

    *   On macOS and Linux:
        ```bash
        export FLASK_APP=expense_tracker.app:create_app
        export FLASK_DEBUG=1
        ```
    *   On Windows (Command Prompt):
        ```bash
        set FLASK_APP=expense_tracker.app:create_app
        set FLASK_DEBUG=1
        ```
    *   On Windows (PowerShell):
        ```bash
        $env:FLASK_APP="expense_tracker.app:create_app"
        $env:FLASK_DEBUG="1"
        ```
    You can also use a `.flaskenv` file in the project root to automatically set these (see Flask documentation).

2.  **Run the Application:**
    ```bash
    flask run
    ```
    The application will typically be available at `http://127.0.0.1:5000/`. You should see output in your terminal indicating the server is running.

## Processing Recurring Transactions

Recurring transactions (like monthly rent or salary) are defined by rules but are not automatically created by the web server itself. A separate command needs to be run to process these rules and generate the actual transaction entries.

1.  **Ensure your `FLASK_APP` environment variable is set (as described in the "Running the Development Server" section).**
2.  **Run the Processor:**
    ```bash
    flask process-recurring
    ```
    This command will:
    *   Scan all recurring transaction rules.
    *   Identify rules that are due to generate a transaction.
    *   Create the corresponding transaction entries in the database.
    *   Update the `next_occurrence_date` for the processed rules.

    It's recommended to run this command periodically (e.g., daily) using a task scheduler like `cron` (on Linux/macOS) or Task Scheduler (on Windows) if you want automatic processing in a production-like environment.

## Technologies Used

*   **Backend:** Python, Flask
*   **Database ORM:** SQLAlchemy, Flask-SQLAlchemy
*   **Database Migrations:** Flask-Migrate
*   **Database (Default):** SQLite
*   **Templating:** Jinja2 (via Flask)
*   **Frontend Basics:** HTML, CSS, JavaScript
*   **Forms:** Flask-WTF, WTForms, WTForms-SQLAlchemy
*   **User Authentication:** Flask-Login
*   **Charting:** Chart.js
*   **Date/Time Utilities:** python-dateutil
*   **Command Line Interface:** Click (via Flask's CLI)
```
