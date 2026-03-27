# CAIA Navigator

CAIA Navigator is a local prototype for cancer navigation workflow support. It combines a lightweight Python server with a browser-based UI for managing a patient queue, importing CSV files, classifying barriers, and previewing simple rule-based risk signals.

This is a prototype application for demonstration and workflow exploration. It is not a production clinical system and should not be used for medical decision-making.

## What It Does

- Maintains a local patient queue backed by `patients.json`
- Supports add, edit, single delete, and batch delete
- Imports CSV files into the queue
- Detects unchanged duplicate rows and skips them
- Detects Patient ID conflicts and lets the user choose how to resolve them
- Prevents duplicate Patient IDs during manual entry
- Generates simple rule-based predictions for:
  - overall delay risk
  - delay sub-risk
  - disengagement sub-risk
  - access sub-risk
- Suggests:
  - primary barrier
  - secondary barrier
  - queue priority
  - intervention package

## App Architecture

This project runs as a local file-backed web app:

- `caia_navigator_server.py` provides the local HTTP server and API
- `caia_navigator_file_app.html` provides the browser UI
- `patients.json` stores the current local dataset
- `start_caia_navigator.bat` launches the app on Windows

The app is intentionally simple:
- no database
- no authentication
- no multi-user synchronization
- no external dependencies beyond Python standard library

## Main Files

Core files:

- `start_caia_navigator.bat`
- `caia_navigator_server.py`
- `caia_navigator_file_app.html`
- `patients.json`
- `README.md`

Example CSV files:

- `caia_navigator_example_import.csv`
- `caia_navigator_example_high_risk.csv`
- `caia_navigator_example_mixed_queue.csv`
- `caia_navigator_example_access_barriers.csv`
- `caia_navigator_example_low_risk.csv`

Other local/demo files in this folder are optional and not required to run the main file-backed app.

## Requirements

- Windows
- Python 3
- A local browser such as Chrome or Edge

At least one of the following must work in Command Prompt:

```bat
C:\Users\hanyi\anaconda3\python.exe
```

or

```bat
py -3
```

or

```bat
python
```

## Run The App

### Option 1: Double-click the launcher

Run:

```bat
start_caia_navigator.bat
```

This will:
- try to find a usable Python executable
- start the local server
- open the app in your default browser

### Option 2: Run from Command Prompt

Open Command Prompt in the project folder and run one of:

```bat
C:\Users\hanyi\anaconda3\python.exe -u caia_navigator_server.py
```

or

```bat
py -3 -u caia_navigator_server.py
```

or

```bat
python -u caia_navigator_server.py
```

Then open:

```text
http://127.0.0.1:8000/
```

Important:

- Do not close the server window while using the app
- The app writes local data into `patients.json`
- Runtime output is written to `server.log`

## Typical Workflow

1. Start the app.
2. Open the `Patient Queue` page to review current records.
3. Use `Data Entry` to add or edit a patient.
4. Use the prediction panel to preview risk and barrier logic.
5. Import CSV files when you want to load a larger queue.
6. Use queue filtering, selection, and batch delete to manage the worklist.

## CSV Import Behavior

The CSV importer supports:

- importing new patients
- updating existing patients
- skipping unchanged duplicate rows
- conflict review for reused Patient IDs with different patient details

### Duplicate Handling

If a CSV row has the same Patient ID and the same normalized data as an existing record:

- the row is skipped automatically

If a CSV row has the same Patient ID but different patient data:

- the app opens a conflict modal
- the user can choose one of:
  - overwrite the existing patient
  - generate a new Patient ID
  - skip that incoming row

### Manual Entry Protection

The `Patient ID` field in the form includes:

- real-time duplicate detection
- save blocking when the ID already exists
- a `Generate ID` button for the next available `PT-xxxx`

## CSV Template Expectations

The importer expects these fields:

- `id`
- `name`
- `age`
- `gender`
- `language`
- `payer`
- `cancerType`
- `stage`
- `daysSinceFinding`
- `primaryBarrier`
- `secondaryBarrier`
- `priority`
- `socialRisk`
- `missedVisits`
- `insuranceDelayDays`
- `referralComplete`
- `transportationRisk`
- `languageBarrier`
- `notes`

Each row represents one patient.

## Risk Logic

The prediction system is intentionally transparent and rule-based. It is not a trained machine learning model.

The current UI estimates:

- overall delay risk
- delay risk
- disengagement risk
- access risk

These estimates are based on fields such as:

- `daysSinceFinding`
- `referralComplete`
- `insuranceDelayDays`
- `missedVisits`
- `transportationRisk`
- `languageBarrier`
- `language`
- `socialRisk`
- `stage`

The UI then suggests:

- queue priority
- likely primary barrier
- likely secondary barrier
- recommended intervention package

## Local Data Storage

The app stores queue data locally in:

```text
patients.json
```

This means:

- imported data persists between sessions
- edits persist between sessions
- deletes persist between sessions

It also means:

- this is best for single-user local use
- concurrent editing by multiple users is not supported

## Limitations

- Windows-first launcher
- file-based persistence only
- no user accounts
- no audit trail
- no database locking
- no production deployment hardening
- no clinical validation

## Recommended GitHub Upload Set

If you want a minimal upload set for the working local app, include:

- `start_caia_navigator.bat`
- `caia_navigator_server.py`
- `caia_navigator_file_app.html`
- `patients.json`
- `README.md`

If you also want demo content for testing imports, include the example CSV files as well.

## Disclaimer

This repository contains a workflow and UI prototype only.

- It is not a medical device
- It is not clinically validated
- It is not intended for diagnosis or treatment decisions
