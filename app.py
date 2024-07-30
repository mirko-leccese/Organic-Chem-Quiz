import pandas as pd 
import numpy as np 
import random
import sqlite3

from flask import Flask, render_template, request, redirect, url_for, session

df_orgmol = pd.read_csv('./orgmolecules_dataset.csv', sep=",").reset_index()

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for session management

correct_pairs = []


@app.route('/')
def index():

    # Select a random molecule
    random_molecule = np.random.choice(df_orgmol["IUPAC"])

    # Prepare the options (correct one + random incorrect ones)
    random_options = list(np.random.choice(df_orgmol[df_orgmol["IUPAC"]!=random_molecule]["IUPAC"], 3))
    options = random_options + [random_molecule]

    random.shuffle(options)

    # Extracting img url of the random molecule chosen
    molecule_url = df_orgmol.loc[df_orgmol["IUPAC"] == random_molecule, "image_url"].values[0]

    return render_template('index.html', molecule_url=molecule_url, options=options, correct_answer=random_molecule)

@app.route('/check_answer', methods=['POST'])
def check_answer():
    selected_word = request.form['selected_word']
    english_word = request.form['question_molecule']
    correct_word = request.form['correct_answer']

    session['count'] = session.get('count', 0) + 1

    if selected_word == correct_word:
        session['correct'] = session.get('correct', 0) + 1

    if session['count'] >= 10:
        return redirect(url_for('results'))

    return redirect(url_for('index'))

@app.route('/results')
def results():
    correct = session.get('correct', 0)
    count = session.get('count', 0)

    return render_template('results.html', correct=correct, count=count)

@app.route('/reset')
def reset():
    session.pop('count', None)
    session.pop('correct', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)