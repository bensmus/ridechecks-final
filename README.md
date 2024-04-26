# What is this?

This application serves amusement park administrators, enabling them to generate ride check schedules. These schedules assign mechanics to inspect amusement park rides before opening hours. The application runs locally on the administrator's computer (which must have Python installed). Upon schedule generation, it opens in the default web browser, allowing administrators to download (ctrl-s) or print (ctrl-p) the schedule. Here's a sample schedule:

<img width="1916" alt="ridechecks_blurred" src="https://github.com/bensmus/ridechecks-final/assets/37351071/7e44cd93-c044-40ff-8440-2c70b7fe5f91">

The mechanic names are blurred for privacy. 'R.C.' stands for ride closed, and 'P.C.' stands for park closed.

The schedule constraints assumed by the application are:

- There is a certain 'time till opening' during which the workers have to check their assigned rides. 
- Each worker has a certain set of rides that they can be assigned (have been trained on).
- Each ride takes a certain amount of time to check.
- All of the rides that are open on a given day have to be checked.

The application needs to be set up (described below) and can then be run with Python.

# Setting up the application

*Note: The application is optimized for Windows computers. The UI may appear less polished on Mac or Linux due to default PySide6 widgets on those systems.*

*Note: The steps below assume a Windows computer with git and at least python3.10 installed, and are given for PowerShell.*

1. Clone the repository
2. Optional but recommended: create a virtual environment `python -m venv venv` and activate it `./venv/Scripts/activate.ps1`
   (ensures that python libraries don't conflict with other python libraries on your computer)
3. Run `pip install -r requirements.txt`, which installs all requirements (libraries that the application depends on)

# Using the application

Run `python ridechecks_app.py` to launch the application.

The GUI has four tabs: 'Weekly Info', 'Worker Permissions', 'Rides', and 'Generate'.

![image](https://github.com/bensmus/ridechecks-final/assets/37351071/f0f8f77c-8ecd-41e4-bc90-1caeb39da68e)

In the image above, the UI is opened to the 'Weekly Info' tab. Here's an explanation of the UI. Since the time till opening is 0 for Monday and Tuesday, this means that no ridechecks will be scheduled for those days. On each day fom Wednesday to Sunday, there are 4 hours till opening. For Wednesday, "Jay" and "Steve" are absent, and "Coaster track" is closed.

In the most common scenario, the administrator tweaks some week-specific information in this tab, and then goes to the 'Generate' tab and clicks generate.

To add and remove workers, as well as change which rides workers are trained to check, use the 'Worker Permissions tab'.

To add and remove rides, use the 'Rides' tab.
