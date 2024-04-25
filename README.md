# What is this?

This is an application made for an amusement park that allows them to assign mechanics (workers) to check amusement park rides before the park opens. 
There is a certain 'time till opening' during which the workers have to check their assigned rides. 
Each worker has a certain set of rides that they can check, and some rides take longer than others: 
these are the main constraints of the problem. 

The application is where the amusement park administrator can input the mechanic and ride availability, 
and then generate, view, and save the mechanic schedule in their browser.
The application needs to be set up (described below) and can then be run with Python.

# Setting up the application

*Note: The application is optimized for Windows computers. The UI may appear less polished on Mac or Linux due to default PySide6 widgets on those systems.*

*Note: The steps below assume a Windows computer with git and at least python3.10 installed, and are given for PowerShell.*

1. Clone the repository
2. Optional but recommended: create a virtual environment `python -m venv venv` and activate it `./venv/Scripts/activate.ps1`
   (ensures that python libraries don't conflict with other python libraries on your computer)
3. Run `pip install -r requirements.txt`, which installs all requirements (libraries that the application depends on)

# Using the application: tab by tab

Run `python ridechecks_app.py` to launch the application.

The GUI has four tabs: 'Weekly Info', 'Worker Permissions', 'Rides', and 'Generate'.

![image](https://github.com/bensmus/ridechecks-final/assets/37351071/f0f8f77c-8ecd-41e4-bc90-1caeb39da68e)

## Weekly Info

*Tab for editing problem state*

Edit available time, worker availablity, and ride status for each day.

In the image above, the UI is opened to the 'Weekly Info' tab. Here's an explanation of the UI. Since the time till opening is 0 for Monday and Tuesday, this means that no ridechecks will be scheduled for those days. On each day fom Wednesday to Sunday, there are 4 hours till opening. For Wednesday, "Jay" and "Steve" are absent, and "Coaster track" is closed.

## Worker Permissions

*Tab for editing problem state*

Edit which workers are trained on which ride by clicking checkboxes.

Also add and remove workers.

## Rides

*Tab for editing problem state*

Add and remove rides.

## Generate

*Tab for getting the mechanic schedule*

Click on generate. You may have to wait for 30 seconds for the mechanic schedule to be generated.
The mechanic schedule will open up in your default browser once generation is complete. You can then save the schedule by ctrl-s.

# Technical details

## CSP

The type of problem that this application solves is a CSP (Constraint Satisfaction Problem).
This type of problem is well known, so Python modules exist for it, and the
[python-constraint](https://github.com/python-constraint/python-constraint) module was used in the core logic.

After trying multiple CSP algorithms provided by python-constraint, 
[min-conflict search](https://en.wikipedia.org/wiki/Min-conflicts_algorithm) is the fastest for this problem.
This algorithm also comes with the bonus of different results for the same inputs (it is a randomized algorithm). 
This is beneficial since we want to avoid repeatedly assigning the same workers to check the same rides.

## Other details

The vast majority of the code is making the UI in PySide6. 
The application uses a YAML file (state.yaml) to save its state, so that it reopens its state from the YAML file when it is closed.
