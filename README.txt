Abracadata Demo

How to run on another Windows computer:

1. Make sure Python 3 is installed.
   One of these commands must work in Command Prompt:
   %USERPROFILE%\anaconda3\python.exe
   py -3
   python
   python3

2. Keep all files together in the same folder.
   Required files:
   start_caia_navigator.bat
   caia_navigator_server.py
   caia_navigator_file_app.html
   patients.json

3. Start the app.
   Option A:
   Double-click start_caia_navigator.bat

   Option B:
   Open Command Prompt in this folder and run:
   %USERPROFILE%\anaconda3\python.exe -u caia_navigator_server.py
   or
   py -3 -u caia_navigator_server.py
   or
   python -u caia_navigator_server.py

4. Open the app in a browser:
   http://127.0.0.1:8000/

Important:
- Do not close the server Command Prompt window while using the app.
- Data is saved locally in patients.json.
- Logs are written to server.log.

CSV examples included:
- caia_navigator_example_import.csv
- caia_navigator_example_high_risk.csv
- caia_navigator_example_mixed_queue.csv
- caia_navigator_example_access_barriers.csv
- caia_navigator_example_low_risk.csv
