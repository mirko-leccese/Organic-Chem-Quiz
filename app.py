import pandas as pd 
import numpy as np 
import random
import sqlite3

from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session

df_orgmol = pd.read_csv('./orgmolecules_dataset.csv', sep=",").reset_index()

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for session management

correct_pairs = []

def get_db_connection():
    connection = sqlite3.connect("database/database.db")
    connection.row_factory = sqlite3.Row 
    return connection

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        if username:
            connection = get_db_connection()
            user = connection.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

            if user is None:
                connection.execute("INSERT INTO users (username) VALUES (?)", (username,))
                connection.commit()
                user = connection.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            
            connection.close()
            
            session['user_id'] = user['userid']
            session['username'] = user['username']
            session['count'] = 0
            session['correct'] = 0

            return redirect(url_for('playgame'))
        
    return render_template('index.html')

@app.route('/playgame')
def playgame():
    # Redirect to Login if user not in session
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Select a random molecule
    random_molecule = np.random.choice(df_orgmol["IUPAC"])

    # Prepare the options (correct one + random incorrect ones)
    num_options = session.get("num_options", 4) - 1

    random_options = list(np.random.choice(df_orgmol[df_orgmol["IUPAC"]!=random_molecule]["IUPAC"], num_options))
    options = random_options + [random_molecule]

    random.shuffle(options)

    # Extracting img url of the random molecule chosen
    molecule_url = df_orgmol.loc[df_orgmol["IUPAC"] == random_molecule, "image_url"].values[0]

    return render_template('playgame.html', molecule_url=molecule_url, options=options, correct_answer=random_molecule)

@app.route('/check_answer', methods=['POST'])
def check_answer():
    selected_molecule = request.form['selected_molecule']
    question_molecule = request.form['question_molecule']
    correct_answer = request.form['correct_answer']

    session['count'] = session.get('count', 0) + 1

    if selected_molecule == correct_answer:
        session['correct'] = session.get('correct', 0) + 1

    # setting number of questions
    num_questions = session.get("num_questions", 10)

    if session['count'] >= num_questions:
        return redirect(url_for('results'))

    return redirect(url_for('playgame'))

@app.route('/results')
def results():
    correct = session.get('correct', 0)
    count = session.get('count', 0)
    ratio = round(correct/count*100, 2)
    playdate = datetime.now()
    connection = get_db_connection()

    # Insert results into results table
    connection.execute("INSERT INTO results (userid, playdate, correct, questions, ratio) VALUES (?,?,?,?,?)", (session["user_id"],playdate,correct, count, ratio))
    connection.commit()
    connection.close()

    return render_template('results.html', correct=correct, count=count)

@app.route('/reset')
def reset():
    session.pop('count', None)
    session.pop('correct', None)
    return redirect(url_for('playgame'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/scoreboard')
def scoreboard():
    connection = get_db_connection()
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
    if request.method == 'POST':
        num_questions = request.form['num_questions']
        num_options = request.form['num_options']

        session["num_questions"] = int(num_questions)
        session["num_options"] = int(num_options)

        return redirect(url_for('login'))
        
    return render_template('customize.html')

if __name__ == '__main__':
    app.run(debug=True)