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

## User roles and workflow

On the first launch, create the administrator account using a username and password (minimum 8 characters). There are no hardcoded default passwords.

1. Log in as **Admin** and choose **Create Staff Account**. Provide a staff username and temporary password.
2. Click **Switch Account**, then log in as **Staff**. Submit a report (e.g., PC-01 and 'Monitor has no display'). Staff can view their own reports and current statuses, but cannot change statuses or delete reports.
3. Click **Switch Account**, log in as **Admin**, and review all submitted reports. Choose **Mark In Progress** when investigating the issue. When it is fixed, choose **Mark Resolved** and record what was done. Admin can reopen or delete reports if necessary.
4. Click **Switch Account** and log in as Staff to see the updated status of their reports.

Report IDs and dates are assigned automatically. Both roles can search reports and filter by status. Summary counts reflect reports visible to the logged-in user.

## Local storage and limitations

- `reports.json` contains issue reports. `users.json` contains account details and salted password hashes. Neither file is committed to Git.
- The program is **offline and single-computer**. Staff and Admin accounts are intended to take turns using the same computer and local files. The app does **not** synchronize reports across computers or support remote staff submissions.
- Accounts are suitable for classroom demonstration, not a production security boundary against someone with direct access to the local JSON files. Back up both JSON files together when migrating to another computer.

The application starts with no reports. `reports.json` is created on the first successful save and is ignored by Git.

## Tests

Run `python -m unittest discover -s tests -v` to check report creation, validation, search, status updates, deletion, and saving/loading.

## Data storage

Reports are held in a Python dictionary while the application runs and saved to a local JSON file whenever they change. This is designed for a single offline computer, not multiple concurrent users.

## Project scope

A functional prototype built with standard-library Python and Tkinter. Local login with role-specific screens, but no server, third-party dependencies, or SQL database.
