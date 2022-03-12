# Kanban_162

This is a Kanban app that allows the user to keep track of their tasks by categorizing them either into "To Do", "Doing" or "Done". These tasks can later be updated or deleted if the user chooses to do so. The user's tasks are protected by user authentication (email + password), but woe unto them if they forget their password (the app does not support password recovery, yet). The app is built on the Flask micro-framework, using SQLAlchemy database models to store the user and task information. The styling is CSS only. Feel free to clone the repo and play around with the app!


### Getting the app running

1. Clone the repo to your local machine!
2. Open your terminal and cd to the location of the cloned repo.
3. In the clone's root directory, input:

#### macOS
```python3
python3.6 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3.6 app.py
```

#### Windows
```python3
python3.6 -m venv venv
venv\Scripts\activate.bat
pip3 install -r requirements.txt
python3.6 app.py
```

#### Git Bash
```python3
python3.6 -m venv venv
venv/Scripts/activate.bat
pip3 install -r requirements.txt
python3.6 app.py
```

4. Once you run the commands, the app will spool up and give you a link in the terminal (usually: http://127.0.0.1:5000/).
5. Paste the link into your favorite browser (Google Chrome is recommended) and voila! You now have a task management system. Enjoy!

As a side note, the app also features 15 inbuilt tests to confirm that all the routes are operational. You can run them by using the following command:

```python3
python3.6 -m unittest discover test
```
