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

## Running on Raspberry Pi (Auto-start on Boot)

To make the ICS Viewer automatically start when your Raspberry Pi boots, you can create a systemd service file. These instructions assume your project is located at `/home/pi/BlastCalendar3` and you are using the standard `pi` user.

1.  **Create the systemd service file:**

    Use a text editor (like `nano`) to create a new service file:
    ```bash
    sudo nano /etc/systemd/system/blastcalendar.service
    ```

2.  **Add the following content** to the file. Adjust paths if your project location or Python version differs:

    ```ini
    [Unit]
    Description=Blast Calendar ICS Viewer Flask App
    After=network.target

    [Service]
    User=pi
    WorkingDirectory=/home/pi/BlastCalendar3/ics_viewer
    ExecStart=/home/pi/BlastCalendar3/.venv/bin/python /home/pi/BlastCalendar3/ics_viewer/app.py
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```

    *   `Description`: A brief description of the service.
    *   `After=network.target`: Ensures the network is up before starting.
    *   `User=pi`: Runs the service as the `pi` user.
    *   `WorkingDirectory`: Sets the correct directory so Flask can find templates and static files.
    *   `ExecStart`: The full command to run the application using the Python interpreter *inside* the virtual environment.
    *   `Restart=always`: Automatically restarts the service if it crashes.

3.  **Save and close** the editor (in `nano`, press `Ctrl+X`, then `Y`, then `Enter`).

4.  **Enable the service** (so it starts on boot):

    ```bash
    sudo systemctl enable blastcalendar.service
    ```

5.  **Start the service** immediately (optional, otherwise it starts on next reboot):

    ```bash
    sudo systemctl start blastcalendar.service
    ```

6.  **Check the status** (optional):

    ```bash
    sudo systemctl status blastcalendar.service
    ```

Now, the Blast Calendar viewer should start automatically whenever the Raspberry Pi boots up.
