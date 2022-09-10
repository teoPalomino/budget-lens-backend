# Budget Lens Backend
This repository is insteded for the Capstone team to manage the backend servers of the BudgetLens Application.

## Getting Started
 First, make sure you have Python3 installed on your local machine. I'd suggest using Python version `3.10` to avoid any version conflicts. You also need to install _pipenv_ to create a python virtual environment to avoid dependency collisions. In a terminal window, run the following command: ` pip install pipenv` then, use the following steps: <br>

 1. Inside the project root, where you can find the files _pipfile_ and _pipfile.lock_, run the command `pipenv shell` to start the virtual environment.
 2. Run the command `pipenv install` to install all python packages and dependencies needed for the project. This command installs all the packages from _pipfile.lock_.
 3. Run the command `python manage.py runserver` which will run the server.
 4. Check the page rendered by the project in your browser at `http://127.0.0.1:8000/`. This port will be use as our backend server for now until the project will be deployed online.

 ## Updating Database Models
 Whenever the database models are update or a new Django Models class is created you need to run `python manage.py makemigrations` and then `python manage.py migrate`. the _makemigrations_ checks for migrations and the _migrate_ makes the migrations and updates the database.

 ## Adding new Python Packages
 Normally, python users are used to the _pip_ command for installing dependencies, but use instead _pipenv_. This updated the _pipfile_ and _pipfile.lock_ files as well as installing the new package.
