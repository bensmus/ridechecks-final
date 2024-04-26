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

The majority of the code is making the UI in PySide6. 
The application uses a YAML file (state.yaml) to save its state, so that it reopens its state from the YAML file when it is closed.
