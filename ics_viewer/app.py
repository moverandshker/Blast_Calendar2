from flask import Flask, request, jsonify, render_template
import requests
from icalendar import Calendar
import logging
from datetime import datetime, date, timedelta
import pytz
from dotenv import load_dotenv
import os
from dateutil import rrule
from dateutil.relativedelta import relativedelta
import calendar

# Load environment variables from .env file
load_dotenv()

# Configure basic logging
logging.basicConfig(level=logging.INFO)

# --- Constants ---
# Consider moving to a config file later if needed
REQUEST_TIMEOUT = 10 # seconds
TARGET_TIMEZONE = pytz.timezone('America/Denver') # Example: Use your local timezone
UTC = pytz.utc
DATE_FORMAT = "%a, %b %d, %Y %I:%M %p %Z" # Example format: Mon, Jan 21, 2024 02:30 PM MST
RECURRENCE_LIMIT_DAYS = 90 # Expand recurring events X days into the future

# Get default URL from environment
ICS_DEFAULT_URL = os.getenv('ICS_DEFAULT_URL', '') # Provide empty default if not set

# --- Flask App Initialization ---
app = Flask(__name__)

# --- Helper Functions ---
def fetch_ics_data(url):
    """Fetches ICS data from a URL, checking Content-Type."""
    logging.info(f"Attempting to fetch ICS data from: {url}")
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        # Check Content-Type header
        content_type = response.headers.get('Content-Type', '').lower()
        if 'text/calendar' not in content_type:
             err_msg = f"Expected 'text/calendar' content type, but received '{content_type}'. Is the URL correct?"
             logging.error(err_msg)
             return None, err_msg # Return None content and the error

        logging.info(f"Successfully fetched ICS data (Content-Type: {content_type}).")
        return response.text, None # Return content and no error

    except requests.exceptions.Timeout:
        err_msg = f"Timeout error (>{REQUEST_TIMEOUT}s) when fetching ICS from {url}"
        logging.error(err_msg)
        return None, err_msg
    except requests.exceptions.RequestException as e:
        err_msg = f"Error fetching ICS from {url}: {e}"
        logging.error(err_msg)
        return None, err_msg

def parse_ics_content(ics_string):
    """Parses event details from an ICS string, converting times to target timezone and handling recurrence."""

    if not ics_string:
        return None, "No ICS content provided for parsing."

    events = []
    error_message = None
    try:
        # Define time range for recurrence expansion
        now_local = datetime.now(TARGET_TIMEZONE)
        future_limit_local = now_local + timedelta(days=RECURRENCE_LIMIT_DAYS)

        # Attempt to parse the ICS string
        cal = Calendar.from_ical(ics_string)

        # Walk through components (Events, Todos, etc.)
        for component in cal.walk('VEVENT'):
            summary = component.get('summary')
            dtstart_obj = component.get('dtstart').dt if component.get('dtstart') else None
            dtend_obj = component.get('dtend').dt if component.get('dtend') else None

            # --- Original Timezone Handling --- (Needed for RRULE start)
            dtstart_orig_tz = None
            dtstart_naive = False
            if isinstance(dtstart_obj, datetime):
                 dtstart_orig_tz = dtstart_obj.tzinfo
                 if not dtstart_orig_tz:
                      dtstart_naive = True
                      # We will assume naive times are UTC when localizing for RRULE
            # Note: date objects have no tzinfo

            # --- RRULE Handling ---
            if component.get('RRULE'):
                try:
                    rules = rrule.rrulestr(component.get('RRULE').to_ical().decode('utf-8'), dtstart=dtstart_obj)
                    duration = None
                    if isinstance(dtstart_obj, datetime) and isinstance(dtend_obj, datetime):
                        duration = dtend_obj - dtstart_obj
                    elif isinstance(dtstart_obj, date) and isinstance(dtend_obj, date):
                         duration = dtend_obj - dtstart_obj # Duration in days for date objects

                    # Generate occurrences within the time window
                    # Need to provide datetime objects with correct tz context for .between()
                    start_dt_for_rrule = dtstart_obj
                    if dtstart_naive and isinstance(start_dt_for_rrule, datetime):
                         start_dt_for_rrule = UTC.localize(start_dt_for_rrule) # Assume naive are UTC for rule generation

                    # Ensure comparison datetimes have tzinfo if start_dt_for_rrule does
                    compare_start = now_local
                    compare_end = future_limit_local
                    if start_dt_for_rrule.tzinfo:
                         if not compare_start.tzinfo:
                              compare_start = TARGET_TIMEZONE.localize(compare_start.replace(tzinfo=None))
                         if not compare_end.tzinfo:
                              compare_end = TARGET_TIMEZONE.localize(compare_end.replace(tzinfo=None))
                         # Convert compare times to the start_dt's timezone for correct comparison by rrule
                         compare_start = compare_start.astimezone(start_dt_for_rrule.tzinfo)
                         compare_end = compare_end.astimezone(start_dt_for_rrule.tzinfo)
                    else: # start_dt_for_rrule is naive (likely a date object)
                         compare_start = compare_start.replace(tzinfo=None)
                         compare_end = compare_end.replace(tzinfo=None)


                    for occ_start in rules.between(compare_start, compare_end, inc=True):
                        # Convert occurrence start time to target timezone
                        start_localized = None
                        if isinstance(occ_start, datetime):
                            if occ_start.tzinfo:
                                start_localized = occ_start.astimezone(TARGET_TIMEZONE)
                            else: # If rrule returns naive, assume UTC like original naive
                                start_localized = UTC.localize(occ_start).astimezone(TARGET_TIMEZONE)
                        elif isinstance(occ_start, date):
                            start_localized = occ_start # Keep as date object

                        # Calculate end time based on duration
                        end_localized = None
                        if duration is not None and start_localized is not None:
                             end_localized = start_localized + duration

                        event = {
                            'summary': f"{summary} (Recurring)",
                            'start': start_localized,
                            'end': end_localized,
                            'recurring': True # Flag for potential future use
                        }
                        events.append(event)
                    logging.info(f"Expanded recurring event '{summary}' starting {dtstart_obj}")

                except Exception as rule_error:
                     logging.error(f"Could not parse RRULE for event '{summary}' starting {dtstart_obj}: {rule_error}")
                     # Optionally add a placeholder event indicating the failure?

            else:
                # --- Single Event Timezone Conversion (as before) ---
                start_localized = None
                if isinstance(dtstart_obj, datetime):
                    if dtstart_obj.tzinfo:
                        start_localized = dtstart_obj.astimezone(TARGET_TIMEZONE)
                    else: # Naive datetime, assume UTC (common default for ICS naive times)
                        start_localized = UTC.localize(dtstart_obj).astimezone(TARGET_TIMEZONE)
                elif isinstance(dtstart_obj, date): # Handle date objects (maybe all-day events)
                     # Represent as start of the day in target timezone?
                     # Or just pass the date object itself?
                     # For now, let's store it as is, format later if needed
                     start_localized = dtstart_obj

                end_localized = None
                if isinstance(dtend_obj, datetime):
                    if dtend_obj.tzinfo:
                        end_localized = dtend_obj.astimezone(TARGET_TIMEZONE)
                    else: # Naive datetime, assume UTC
                        end_localized = UTC.localize(dtend_obj).astimezone(TARGET_TIMEZONE)
                elif isinstance(dtend_obj, date):
                     end_localized = dtend_obj
                # --- End Single Event Timezone Conversion ---

                event = {
                    'summary': summary,
                    'start': start_localized,
                    'end': end_localized,
                    'recurring': False
                }
                # Basic check to ensure we have at least a summary or start time
                if event['summary'] or event['start']:
                    events.append(event)
        logging.info(f"Parsed {len(events)} events from ICS data.")
    except ValueError as e:
        error_message = f"Failed to parse ICS data. It might be invalid or corrupted. Error: {e}"
        logging.error(error_message)
    except Exception as e: # Catch other potential parsing errors
        error_message = f"An unexpected error occurred during ICS parsing: {e}"
        logging.error(error_message)

    # Return events list (might be empty) and error message (if any)
    return events, error_message

# --- Routes ---
@app.route('/')
def index():
    """Renders the main page with the default ICS URL in the form."""
    # Pass the default URL to pre-fill the form
    return render_template('index.html', ics_url=ICS_DEFAULT_URL)

@app.route('/view') # Using GET for simplicity in phase 1/2
def view_ics():
    """Fetches, parses ICS data, structures for month view, and renders the template."""
    ics_url = request.args.get('url', default=ICS_DEFAULT_URL)
    error = None
    events_by_date = {}

    try:
        # Get target year and month from query params, default to current month
        current_dt = datetime.now(TARGET_TIMEZONE)
        target_year = request.args.get('year', default=current_dt.year, type=int)
        target_month = request.args.get('month', default=current_dt.month, type=int)

        # Validate month and create the first day of the target month date object
        first_day_target_month = date(target_year, target_month, 1)
        month_name = first_day_target_month.strftime("%B")

        # Calculate previous and next month/year
        prev_month_date = first_day_target_month - relativedelta(months=1)
        next_month_date = first_day_target_month + relativedelta(months=1)
        prev_year = prev_month_date.year
        prev_month = prev_month_date.month
        next_year = next_month_date.year
        next_month = next_month_date.month

    except (ValueError, TypeError) as e:
        # Handle invalid year/month input
        error = f"Invalid year or month specified: {e}"
        # Set defaults so template doesn't crash, but show error
        target_year = current_dt.year
        target_month = current_dt.month
        month_name = current_dt.strftime("%B")
        # Set dummy prev/next if error occurred during calculation
        prev_year, prev_month, next_year, next_month = (None, None, None, None)
        month_calendar_weeks = [] # Ensure calendar doesn't render
        return render_template(
            'index.html',
            error=error, ics_url=ics_url, month_name=month_name,
            target_year=target_year, target_month=target_month,
            prev_year=prev_year, prev_month=prev_month,
            next_year=next_year, next_month=next_month,
            month_calendar_weeks=month_calendar_weeks,
            events_by_date=events_by_date, date=date
        )


    # Only fetch and parse if URL is provided and no date error occurred
    if not error and ics_url:
        ics_content, fetch_error = fetch_ics_data(ics_url)

        if fetch_error:
            error = fetch_error
        elif ics_content:
            parsed_events, parse_error = parse_ics_content(ics_content)
            if parse_error:
                error = parse_error
                # We might still want to display the empty list if parse_error occurred
                events = []
            else:
                events = parsed_events

                # Filter events for the target month and structure them by date
                first_day_of_month = date(target_year, target_month, 1)
                # Find the first day of the *next* month
                if target_month == 12:
                     first_day_of_next_month = date(target_year + 1, 1, 1)
                else:
                     first_day_of_next_month = date(target_year, target_month + 1, 1)

                for event in events:
                     event_start_dt = event['start'] # This is localized datetime or date object
                     event_date = None
                     if isinstance(event_start_dt, datetime):
                          event_date = event_start_dt.date()
                     elif isinstance(event_start_dt, date):
                          event_date = event_start_dt

                     # Check if the event date falls within the target month
                     if event_date and event_date >= first_day_of_month and event_date < first_day_of_next_month:
                          # Format event times for display
                          start_str = None
                          end_str = None
                          if isinstance(event['start'], datetime):
                               start_str = event['start'].strftime(DATE_FORMAT)
                          elif isinstance(event['start'], date):
                               start_str = "All day"

                          if isinstance(event['end'], datetime):
                               # Optional: Format end time if needed, maybe just show start?
                               # end_str = event['end'].strftime(DATE_FORMAT)
                               pass
                          elif isinstance(event['end'], date):
                               # Optional: Indicate end date for multi-day all-day events?
                               pass

                          # Add formatted event to the dictionary for its date
                          formatted_event = {
                               'summary': event['summary'],
                               'start_str': start_str,
                               # 'end_str': end_str, # Add back if needed
                               'recurring': event.get('recurring', False)
                          }
                          if event_date not in events_by_date:
                               events_by_date[event_date] = []
                          events_by_date[event_date].append(formatted_event)

    # Get the calendar structure for the month
    calendar.setfirstweekday(calendar.SUNDAY) # Ensure weeks start on Sunday
    month_calendar_weeks = calendar.monthcalendar(target_year, target_month)

    # Pass calendar structure and events to the template
    return render_template(
        'index.html',
        error=error,
        ics_url=ics_url,
        month_name=month_name,
        target_year=target_year,
        target_month=target_month,
        prev_year=prev_year, 
        prev_month=prev_month,
        next_year=next_year,
        next_month=next_month,
        month_calendar_weeks=month_calendar_weeks,
        events_by_date=events_by_date,
        date=date # Pass the date constructor to the template
    )

# --- Main Execution ---
if __name__ == '__main__':
    # Host 0.0.0.0 makes it accessible on the network
    # Debug=True is helpful for development, REMOVE for production
    app.run(host='0.0.0.0', port=5000, debug=True)
