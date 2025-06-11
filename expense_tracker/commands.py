import click
from flask.cli import with_appcontext
from .utils.recurring_processor import process_recurring_transactions
# db is not directly used here, but process_recurring_transactions uses it from its own imports.

@click.command(name='process-recurring')
@with_appcontext
def process_recurring_command():
    """
    Processes all due recurring transactions for all users
    and creates corresponding transaction entries.
    """
    click.echo("Starting recurring transaction processing for all users...")
    try:
        # Call the main processing function without a specific user_id
        # to process rules for all users.
        processed_count = process_recurring_transactions()

        if processed_count > 0:
            click.echo(f"Successfully processed occurrences for {processed_count} recurring transaction rule instance(s).")
        else:
            click.echo("No recurring transactions were due or processed.")

    except Exception as e:
        # Log the full exception for debugging if possible
        # For CLI, click.echo is fine for user feedback
        click.echo(f"An error occurred during recurring transaction processing: {str(e)}", err=True)
        # Potentially re-raise or exit with error code if needed for scripting
        # raise e # Uncomment if you want the command to exit with non-zero on error

# If you plan to have more commands, you can create an init_app function:
# def init_app(app):
#     app.cli.add_command(process_recurring_command)
#     # app.cli.add_command(another_command)
