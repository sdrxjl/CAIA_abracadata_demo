# Webapp Navigator

CAIA Navigator is a local prototype for cancer navigation workflow support. It lets you manage a patient queue, import CSV data, classify barriers, and preview simple rule-based risk predictions for delay, disengagement, and access risk.

This project is designed as a lightweight local app:
- Python serves the app and local API
- The browser provides the UI
- Data is stored in a local `patients.json` file

## Core Files

These are the main files to upload:

- `start_caia_navigator.bat`
- `caia_navigator_server.py`
- `caia_navigator_file_app.html`
- `patients.json`
- `README.md`

Optional sample CSV files are also included for testing imports.

## Features

- Patient queue with filtering and sorting
- Add, edit, and delete patient records
- Batch delete from the queue
- CSV import with duplicate detection
- CSV conflict review when the same Patient ID belongs to different patient data
- Rule-based prediction preview for:
  - overall delay risk
  - delay sub-risk
  - disengagement sub-risk
  - access sub-risk
- Suggested barrier classification and intervention package
- Local persistence to `patients.json`

## Requirements

- Windows
- Python 3

One of these must work in Command Prompt:

```bat
%USERPROFILE%\anaconda3\python.exe
```

or

```bat
py -3
```

or

```bat
python
```

## Run Locally

### Option 1: Double-click

Double-click:

```bat
start_caia_navigator.bat
```

### Option 2: Command Prompt

Open Command Prompt in the project folder and run:

```bat
%USERPROFILE%\anaconda3\python.exe -u caia_navigator_server.py
```

or

```bat
py -3 -u caia_navigator_server.py
```

Then open:

```text
http://127.0.0.1:8000/
```

Important:
- Do not close the server window while using the app.
- Data is saved locally in `patients.json`.
- Runtime logs are written to `server.log`.

## CSV Import Behavior

The CSV importer supports:

- normal import for new patients
- skipping unchanged duplicates
- conflict detection when the same `id` has different patient details

If a CSV row reuses an existing Patient ID but the data differs, the app opens a conflict modal and lets you choose:

- overwrite the existing patient
- generate a new Patient ID
- skip that row

## Patient ID Rules

- Manual entry checks whether a Patient ID already exists
- Duplicate IDs are blocked during form save
- The UI includes a `Generate ID` button for creating the next available `PT-xxxx` value

## Sample CSV Files

Example files included in this project:

- `caia_navigator_example_import.csv`
- `caia_navigator_example_high_risk.csv`
- `caia_navigator_example_mixed_queue.csv`
- `caia_navigator_example_access_barriers.csv`
- `caia_navigator_example_low_risk.csv`

## Notes

This is a prototype, not a production clinical system.

- Risk logic is rule-based, not a trained medical model
- Data storage is file-based
- Multi-user concurrent editing is not supported
- This should not be used for clinical decision-making
