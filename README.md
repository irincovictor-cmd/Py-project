# Computer Laboratory Issue Reporting System

A simple offline desktop application for recording and monitoring computer laboratory issues.

## Requirements

- Python 3.10 or later
- Tkinter (included in typical Python installations on Windows)
- No external packages or database required

## Run

1. Clone the repository.
2. Open the project folder in Visual Studio Code.
3. Run `python main.py` (or `py main.py` on Windows).

## Features

- Create reports with a computer number and issue description.
- Automatically assign a report ID and date.
- Search by report ID, computer number, issue or status.
- View all reports, or filter by pending/resolved status.
- Change a report's status between Pending and Resolved.
- Delete a selected report after confirmation.
- View summary counts for total, pending, and resolved reports.
- Save records locally in `reports.json` automatically.

The application starts with no reports. `reports.json` is created on the first successful save and is ignored by Git.

## Tests

Run `python -m unittest discover -s tests -v` to check report creation, validation, search, status updates, deletion, and saving/loading.

## Data storage

Reports are held in a Python dictionary while the application runs and saved to a local JSON file whenever they change. This is designed for a single offline computer, not multiple concurrent users.

## Project scope

A functional prototype built with standard-library Python and Tkinter. No login, server, third-party dependencies, or SQL database.
