
from flask import (Flask, url_for, render_template, request, redirect)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('baseRegForm.html')

@app.route('/main_search')
def main_search():
    return render_template('mainSearch.html')

@app.route('/welcome_student')
def welcome_student():
    return render_template('welcome_student.html')

@app.route('/welcome_referrer')
def welcome_referrer():
    return render_template('welcome_referrer.html')

@app.route('/profile_referrer')
def profile_referrer():
    return render_template('profile_referrer.html')

@app.route('/profile_student')
def profile_student():
    return render_template('profile_student.html')


@app.route('/welcome_admin')
def welcome_admin():
    return render_template('welcome_admin.html')

if __name__ == '__main__':
    import os
    uid = os.getuid()
    app.debug = True
    app.run('0.0.0.0',uid)