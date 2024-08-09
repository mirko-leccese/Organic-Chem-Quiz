# Organic-Chem-Quiz

This repository is a simple project demonstrating the use of the **Flask Framework** for web application development in Python. Specifically, we have created a quiz game focused on Organic Chemistry. The game involves asking the user to identify a molecule based on its molecular structure. 

Here’s how the game works:
- The user can click on the *Customize* link in the sidebar on the left to adjust the number of questions and the number of options displayed.
- On the Homepage, the user should enter a username to log the results.
- By clicking *Let's Play*, the game begins.

After playing, results are logged into an SQL table, which can be viewed directly from the app by clicking on **Scoreboard**.

![GIF](https://github.com/mirko-leccese/Organic-Chem-Quiz/blob/main/game-show.gif)

## Setup
Before running the web app, you need to create a database file to store user information and game results. The app handles database operations internally using `sqlite3`. On the first run, simply execute the `init_db.py` script located in the `database` folder:

```shell
python init_db.py
```

## Run
To run the application, you can use either of the following methods:

```shell
export FLASK_APP=QUIZ
export FLASK_ENV=development
flask run
```

or directly,

```shell
python app.py
```
