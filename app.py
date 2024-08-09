# Basic imports
import pandas as pd 
import numpy as np 
import random
import sqlite3
from datetime import datetime

# Flask imports
from flask import Flask, render_template, request, redirect, url_for, session

# utils import
from libs.utils import Utils

# Reading the dataset with molecules, set the main db
df_orgmol = pd.read_csv('./orgmolecules_dataset.csv', sep=",").reset_index()
db_path = "database/database.db"

app = Flask(__name__)
# Needed for session management
app.secret_key = 'supersecretkey'  

@app.route('/', methods=['GET', 'POST'])
def login():
    '''
    Homepage of the web app. The user should log in inserting a username. If username does not exist,
    we create a new user in the users table.
    '''
    if request.method == 'POST':
        username = request.form['username'].strip()
        # if username, check if user already exists in the users table 
        if username:
            connection = Utils.get_db_connection(db_path)
            user = connection.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

            # otherwise create a new user
            if user is None:
                connection.execute("INSERT INTO users (username) VALUES (?)", (username,))
                connection.commit()
                user = connection.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            
            connection.close()
            
            # setting session parameters
            session['user_id'] = user['userid']
            session['username'] = user['username']
            session['count'] = 0
            session['correct'] = 0

            return redirect(url_for('playgame'))
        
    return render_template('index.html')

@app.route('/playgame')
def playgame():
    '''
    Game main page. Here, we pick a random molecule and define the set of possible options
    '''
    # Redirect to Login if user not in session
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Select a random molecule
    random_molecule = np.random.choice(df_orgmol["IUPAC"])

    # Prepare the options (correct one + random incorrect ones)
    num_options = session.get("num_options", 4) - 1

    random_options = list(np.random.choice(df_orgmol[df_orgmol["IUPAC"]!=random_molecule]["IUPAC"], num_options))
    options = random_options + [random_molecule]

    # Shuffling options
    random.shuffle(options)

    # Extracting img url of the random molecule chosen
    molecule_url = df_orgmol.loc[df_orgmol["IUPAC"] == random_molecule, "image_url"].values[0]

    return render_template('playgame.html', molecule_url=molecule_url, options=options, correct_answer=random_molecule)

@app.route('/check_answer', methods=['POST'])
def check_answer():
    '''
    Method to check whether the selected options is the right one
    '''
    selected_molecule = request.form['selected_molecule']
    question_molecule = request.form['question_molecule']
    correct_answer = request.form['correct_answer']

    # Adding the session count (which counts the number of questions)
    session['count'] = session.get('count', 0) + 1

    # if the answer is correct, updating the correct counter
    if selected_molecule == correct_answer:
        session['correct'] = session.get('correct', 0) + 1

    # setting number of questions
    num_questions = session.get("num_questions", 10)

    # return results if sessions counts match the number of questions defined
    if session['count'] >= num_questions:
        return redirect(url_for('results'))

    return redirect(url_for('playgame'))

@app.route('/results')
def results():
    '''
    Result page. We get the number of questions and the correct answers and create a new record in the results table.
    '''
    # Define session parameters
    correct = session.get('correct', 0)
    count = session.get('count', 0)
    ratio = round(correct/count*100, 2)
    playdate = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")

    # Get the db connection
    connection = Utils.get_db_connection(db_path)

    # Insert results into results table
    connection.execute("INSERT INTO results (userid, playdate, correct, questions, ratio) VALUES (?,?,?,?,?)", (session["user_id"], playdate, correct, count, ratio))
    connection.commit()
    connection.close()

    return render_template('results.html', correct=correct, count=count)

@app.route('/reset')
def reset():
    '''
    Method to reset session info when the user press Play Again at the end of each play. The username is not reset. This method just
    resets counters. 
    '''
    session.pop('count', None)
    session.pop('correct', None)
    return redirect(url_for('playgame'))

@app.route('/logout')
def logout():
    '''
    Method to log out the user when he/she press Log Out at the end of each play.
    '''
    session.clear()
    return redirect(url_for('login'))

@app.route('/scoreboard')
def scoreboard():
    '''
    Scoreboard page. We fetch all data from results table and generate the Scoreboard page
    '''
    # Get database connection
    connection = Utils.get_db_connection(db_path)

    results = connection.execute("""
        SELECT users.username, results.playdate, results.correct, results.questions, results.ratio 
        FROM results 
        JOIN users ON results.userid = users.userid 
        ORDER BY results.ratio DESC
    """).fetchall()

    connection.close()
    
    return render_template('scoreboard.html', results=results)

@app.route('/customize', methods=['GET', 'POST'])
def customize():
    '''
    Customize page. In this page, the user can customize the number of questions and options to display during the game.
    '''
    if request.method == 'POST':
        # get values from forms
        num_questions = request.form['num_questions']
        num_options = request.form['num_options']

        # setting session parameters 
        session["num_questions"] = int(num_questions)
        session["num_options"] = int(num_options)

        return redirect(url_for('login'))
        
    return render_template('customize.html')

if __name__ == '__main__':
    app.run(debug=True)