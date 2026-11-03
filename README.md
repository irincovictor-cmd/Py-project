# Computer Laboratory Issue Reporting System

A simple offline desktop application for recording and monitoring computer laboratory issues.

## Requirements

- Python 3.10 or later
- Tkinter (included in typical Python installations on Windows)
- No external packages or database required

## Setup on a new Windows computer

1. Install Python 3.10 or newer from https://www.python.org/downloads/windows/ (enable **Add Python to PATH** if offered). Python includes the Tkinter GUI library in standard Windows installations.
2. Install Git from https://git-scm.com/downloads/win to use the clone commands. Install Visual Studio Code from https://code.visualstudio.com/ if you want to edit the project (optional for running it).
3. Open PowerShell and run:

   ```powershell
   git clone https://github.com/irincovictor-cmd/Py-project.git
   cd Py-project
   python --version
   python -m tkinter
   python -m pip install -r requirements.txt
   python main.py
   ```

   The Tkinter check should open a small window; close that window before running the application. The requirements command succeeds without installing extra modules because this project only uses the Python standard library.

4. If `python` is not recognized, try `py` instead, for example `py -m tkinter` and `py main.py`.
5. To run the automated tests **from the Py-project folder**, use `python -m unittest discover -s tests -v`.

If you do not have Git installed, download the repository ZIP from GitHub, extract it, open PowerShell in the extracted project folder, and run `python main.py`.

`requirements.txt` lists no external packages. It does not install Python itself, Tkinter separately, Git, or VS Code. Those applications need to be installed separately where required.

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
