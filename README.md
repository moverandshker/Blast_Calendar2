# Blast Calendar ICS Viewer

Blast Calendar is a simple web application built with Flask that allows users to view events from an iCalendar (.ics) feed URL in a monthly calendar format.

## Features

*   **ICS Feed Display:** Enter the URL of an `.ics` feed to fetch and display events.
*   **Monthly Calendar View:** Events are displayed in a traditional month-at-a-glance calendar layout.
*   **Month Navigation:** Use "Previous" and "Next" buttons to navigate between months.
*   **Event Tooltips:** Hover over an event in the calendar to see its summary and start time.
*   **Responsive Header/Form:** The URL input form and header are hidden once a calendar is successfully loaded.
*   **Default URL:** Can be configured via an environment variable for convenience.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/moverandshker/Blast_Calendar2.git
    cd Blast_Calendar3
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # On Windows
    python -m venv .venv
    .venv\Scripts\activate

    # On macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r ics_viewer/requirements.txt
    ```

4.  **Configure Environment Variables:**
    *   Create a file named `.env` in the `ics_viewer` directory (`ics_viewer/.env`).
    *   Add the following line to `.env`, optionally setting a default ICS feed URL:
        ```plaintext
        ICS_DEFAULT_URL=https://www.example.com/path/to/your/calendar.ics
        ```
        *Note: If `ICS_DEFAULT_URL` is not set, the input field will be empty.* 

## Running the Application

1.  Make sure your virtual environment is activated.
2.  Navigate to the `ics_viewer` directory:
    ```bash
    cd ics_viewer
    ```
3.  Run the Flask development server:
    ```bash
    python app.py
    ```
    *The application will typically be available at `http://127.0.0.1:5000`.* 

4.  Open the URL in your web browser.
5.  Enter an ICS feed URL into the input box and click "View Events".

## Dependencies

The main dependencies are listed in `ics_viewer/requirements.txt` and include:

*   Flask
*   requests
*   icalendar
*   python-dateutil
*   pytz
*   python-dotenv

## Project Structure

```
BlastCalendar3/
├── .venv/                  # Virtual environment files (ignored by Git)
├── .gitignore              # Specifies intentionally untracked files
├── .windsurfrules          # Cascade rules (ignore)
├── ics_viewer/             # Main application directory
│   ├── .env                # Environment variables (ignored by Git)
│   ├── .gitignore          # Gitignore specific to app directory
│   ├── app.py              # Flask application logic
│   ├── requirements.txt    # Python package dependencies
│   ├── static/
│   │   └── css/
│   │       └── style.css   # CSS styles
│   └── templates/
│       └── index.html      # HTML template for the calendar view
└── README.md               # This file
```
