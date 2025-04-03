# ICS Viewer Clone - Development Plan (Simplified - No Tailwind)

**Goal:** Create a web application hosted on a Raspberry Pi that fetches an ICS feed from a URL, parses it, and displays the events with basic styling, robust error handling, proper timezone management, and support for recurring events.

**Technology Stack:**

*   **Backend:** Python, Flask
*   **ICS Parsing:** `icalendar` library
*   **HTTP Requests:** `requests` library
*   **Timezones:** `pytz` library
*   **Date/Time Utilities:** `python-dateutil` (for recurrence)
*   **Frontend Styling:** Basic CSS (no frameworks initially)
*   **WSGI Server:** Waitress (for deployment)
*   **Deployment:** Raspberry Pi (using GitHub & systemd eventually)

**Development Phases:**

1.  **Phase 1: Project Setup & Core Backend (Status: Mostly Complete)**
    *   **Location:** `c:\Users\hendr\Documents\BlastCalendar3\ics_viewer`
    *   **Environment:** Python virtual environment (`venv`) with `Flask`, `requests`, `icalendar`, `pytz`, `python-dateutil` installed. (`requirements.txt` exists).
    *   **Core App:** `app.py` exists with basic routes (`/`, `/view`), helper functions (`fetch_ics_data`, `parse_ics_content`), and renders `templates/index.html`.

2.  **Phase 2: Basic Frontend Cleanup & Minimal Styling**
    *   Clean `index.html`: Remove any framework-specific CSS links.
    *   Create `static/css/style.css` and link it in `index.html`.
    *   Add minimal CSS rules to `style.css` for basic readability.
    *   Remove Node.js related files (`package.json`, `package-lock.json`) and `node_modules` directory.

3.  **Phase 3: Enhancements (Core Logic)**
    *   **Robust Error Handling (Refinement):** Ensure errors from fetching/parsing are clearly displayed in the HTML template.
    *   **Date/Time Handling & Timezones:**
        *   Define a target timezone (e.g., start with `'America/Denver'`).
        *   Modify `app.py` to convert event `dtstart`/`dtend` times to this target timezone using `pytz`. Handle both timezone-aware and naive datetimes.
        *   Format dates/times nicely in `index.html` using Python's `strftime`.
    *   **Recurring Events (RRULE):**
        *   Modify `app.py`'s parsing logic.
        *   When a `VEVENT` with an `RRULE` is found, use `dateutil.rrule` to generate occurrences within a specified future timeframe (e.g., next 30 days).
        *   Add these generated occurrences to the list of events passed to the template. Indicate they are instances of a recurring event.

4.  **Phase 4: Deployment Preparation**
    *   Install `waitress`: `pip install waitress` and update `requirements.txt`.
    *   Finalize `app.py`: Remove `debug=True` from `app.run()` (or comment out the block).
    *   Test locally using `waitress-serve --host 127.0.0.1 --port 5000 app:app`.
    *   Prepare files for GitHub (e.g., create/update `.gitignore` to include `venv/`).

5.  **Phase 5: Testing, GitHub & RPi Deployment**
    *   Thorough local testing of all features.
    *   Push code to GitHub repository.
    *   Clone onto Raspberry Pi.
    *   Set up environment & install dependencies on Pi.
    *   Run using Waitress on the Pi (`waitress-serve --host 0.0.0.0 --port 5000 app:app`).
    *   (Optional) Set up systemd service on Pi.
