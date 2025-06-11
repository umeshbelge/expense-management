from ..extensions import db
from ..extensions import db # Already there
from ..models import Transaction, RecurringTransactionRule # Already there
from datetime import datetime, date # Already there
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY, MO, TU, WE, TH, FR, SA, SU # Already there
from dateutil.relativedelta import relativedelta # Add this import

# Helper to map integer day_of_week (0=Mon) to dateutil constants
WEEKDAY_MAP = [MO, TU, WE, TH, FR, SA, SU]

def determine_actual_next_occurrence(current_processing_date, frequency, interval, day_of_week_int=None, day_of_month=None, original_start_date=None):
    """
    Calculates the next occurrence date *after* current_processing_date.
    original_start_date is used to anchor monthly/yearly rules if day_of_month is not set,
    or to determine the very first day for weekly rules if not already on correct day.
    """
    if not original_start_date: # Should ideally always be passed for context
        original_start_date = current_processing_date

    if frequency == 'daily':
        return current_processing_date + relativedelta(days=interval)

    elif frequency == 'weekly':
        # The next occurrence will be 'interval' weeks from the current_processing_date,
        # maintaining the day of the week.
        # If day_of_week_int is specified, it means the rule *must* fall on that day.
        # The initial next_occurrence_date (set at rule creation) should already be on this correct day.
        # So, subsequent calculations just add weeks.
        return current_processing_date + relativedelta(weeks=interval)

    elif frequency == 'monthly':
        next_date = current_processing_date + relativedelta(months=interval)
        target_day = day_of_month if day_of_month else original_start_date.day
        try:
            next_date = next_date.replace(day=target_day)
        except ValueError: # Day is out of range for next_date's month (e.g. 31st for Feb)
            # Go to last day of that month
            next_month_start = (next_date.replace(day=1) + relativedelta(months=1))
            next_date = next_month_start - relativedelta(days=1)
        return next_date

    elif frequency == 'yearly':
        next_date = current_processing_date + relativedelta(years=interval)
        target_day = day_of_month if day_of_month else original_start_date.day
        target_month = original_start_date.month # Assuming yearly keeps the same month as start_date
        try:
            next_date = next_date.replace(month=target_month, day=target_day)
        except ValueError: # Day is out of range for target month (e.g. Feb 29 on non-leap year)
            next_month_start = (next_date.replace(month=target_month, day=1) + relativedelta(months=1))
            next_date = next_month_start - relativedelta(days=1)
        return next_date

    return current_processing_date # Fallback, should not happen

def process_recurring_transactions(user_id=None):
    """
    Processes due recurring transactions and creates actual Transaction records.
    Updates the next_occurrence_date for processed rules.
    """
    today = datetime.utcnow().date()

    query = RecurringTransactionRule.query.filter(RecurringTransactionRule.next_occurrence_date <= today)
    if user_id:
        query = query.filter(RecurringTransactionRule.user_id == user_id)

    rules_due = query.all()
    processed_count = 0

    for rule in rules_due:
        # Loop to process all occurrences up to 'today' if a rule is very overdue
        while rule.next_occurrence_date <= today:
            if rule.end_date and rule.next_occurrence_date > rule.end_date:
                # Rule has finished, mark next_occurrence_date far in future or handle differently
                # For now, just break and it won't be picked up again if end_date is past.
                # Or set next_occurrence_date to None or a very future date if rule is truly complete.
                # Let's assume if end_date is past, the rule is effectively inactive.
                # A cleanup job might be better for this.
                break

            # Create the actual transaction
            new_transaction = Transaction(
                user_id=rule.user_id,
                amount=rule.amount,
                type=rule.type,
                category_id=rule.category_id,
                date=rule.next_occurrence_date, # Transaction date is the due date
                description=f"(Recurring) {rule.description}", # Prepend to indicate it's from a rule
                payment_mode=rule.payment_mode
            )
            db.session.add(new_transaction)

            # Calculate the next occurrence date for this rule
            new_next_occurrence = determine_actual_next_occurrence(
                current_processing_date=rule.next_occurrence_date,
                frequency=rule.frequency,
                interval=rule.interval,
                day_of_week_int=rule.day_of_week,
                day_of_month=rule.day_of_month,
                original_start_date=rule.start_date # Pass original start_date for context
            )
            rule.next_occurrence_date = new_next_occurrence

            # Check again if the new next_occurrence_date has passed the end_date
            if rule.end_date and rule.next_occurrence_date > rule.end_date:
                 # If so, we might not want to add the rule back for update if it's truly finished.
                 # Or, we update it, and it just won't generate more transactions.
                 # For simplicity, we update it. The initial check in the outer loop handles termination.
                 pass


            db.session.add(rule) # Add rule to session to update its next_occurrence_date
            processed_count += 1

            # If the rule was processed and its new next_occurrence_date is still <= today (e.g. daily rule, server down for days)
            # the outer while loop `rule.next_occurrence_date <= today` will ensure it's processed again.
            if rule.next_occurrence_date > today : # if the new date is in future, break from inner while
                break


    if processed_count > 0:
        try:
            db.session.commit()
            print(f"Successfully processed {processed_count} recurring transactions.")
        except Exception as e:
            db.session.rollback()
            print(f"Error during commit of recurring transactions: {e}")
            return 0 # Indicate error or no processing

    return processed_count

# Helper for initial next_occurrence_date calculation (when rule is created/edited)
def calculate_first_occurrence(start_date, frequency, interval, day_of_week_int=None, day_of_month=None):
    """
    Calculates the very first occurrence date based on the rule's parameters,
    ensuring it's on or after the provided start_date.
    """
    # dateutil.rrule is powerful for this.
    # freq mapping:
    freq_map = {'daily': DAILY, 'weekly': WEEKLY, 'monthly': MONTHLY, 'yearly': YEARLY}

    if frequency not in freq_map:
        return start_date # Fallback or raise error

    rrule_freq = freq_map[frequency]

    # Common parameters for rrule
    rrule_params = {
        'freq': rrule_freq,
        'dtstart': datetime.combine(start_date, datetime.min.time()), # rrule needs datetime
        'interval': interval,
        'count': 1 # We only need the first occurrence
    }

    if frequency == 'weekly':
        if day_of_week_int is not None: # 0=Mon, 1=Tue...
            rrule_params['byweekday'] = [WEEKDAY_MAP[day_of_week_int]]
    elif frequency == 'monthly':
        if day_of_month:
            # Handle potential negative day_of_month (e.g., -1 for last day) if desired
            # For now, assume positive day_of_month
            rrule_params['bymonthday'] = [day_of_month]
    elif frequency == 'yearly':
        # For yearly, rrule needs bymonth if bymonthday is used without bysetpos
        # If only day_of_month is given, assume it's for the month of start_date
        rrule_params['bymonth'] = start_date.month
        if day_of_month:
            rrule_params['bymonthday'] = [day_of_month]

    try:
        first_date = rrule(**rrule_params)[0].date()
        return first_date
    except Exception as e:
        # Fallback or logging if rrule fails (e.g., invalid day_of_month for a month)
        print(f"Error calculating first occurrence with rrule: {e}. Defaulting to start_date.")
        return start_date
```
This is a more complex file. I've added `determine_actual_next_occurrence` (renamed from `calculate_next_occurrence` in the prompt for clarity, as it calculates the one *after* processing) and `calculate_first_occurrence`.
The `process_recurring_transactions` function now has a loop to catch up on overdue transactions.
I need to import `relativedelta` in this file.
