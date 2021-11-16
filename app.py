
from flask import (Flask, url_for, render_template, request, redirect)
import random 
import bcrypt
import cs304dbi as dbi

app = Flask(__name__)
app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

@app.route('/', methods=['GET','POST'])
def login():
    conn = dbi.connect()
    if request.method == "GET":
        print("yo")
        return render_template('login.html')
    elif request.method == 'POST':
        print("hii")
        if request.form['submit'] == 'Sign In':
            email = request.form['email']
            inputPass = request.form['password']
            print(email,inputPass)
            #find password from db 
            truePass, user_type = getPassword(conn,email)
            if inputPass == truePass:
                print("true")
                if user_type == "student":
                    return redirect(url_for('welcome_student'))
                elif user_type == "referrer":
                    return redirect(url_for('welcome_referrer'))
                else:
                    return redirect(url_for('welcome_admin'))
            else:
                print("false")
                flash("Account not found or incorrect password. Please try again or register.")
        elif request.form['submit'] == 'Sign Up':
            return redirect(url_for('base_registration'))
    
@app.route('/base_registration',methods=['GET', 'POST'])
def base_registration():
    conn = dbi.connect()
    # hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    # storedPass = hashed.decode('utf-8')
    return render_template('baseRegForm.html')

@app.route('/main_search')
def main_search():
    conn = dbi.connect()
    return render_template('mainSearch.html')

@app.route('/welcome_student')
def welcome_student():
    conn = dbi.connect()
    return render_template('welcome_student.html')

@app.route('/welcome_referrer')
def welcome_referrer():
    conn = dbi.connect()
    return render_template('welcome_referrer.html')

@app.route('/welcome_admin')
def welcome_admin():
    conn = dbi.connect()
    return render_template('welcome_admin.html')

@app.route('/profile_referrer')
def profile_referrer():
    conn = dbi.connect()
    return render_template('profile_referrer.html')

@app.route('/profile_student')
def profile_student():
    conn = dbi.connect()
    return render_template('profile_student.html')

@app.before_first_request
def startup():
    dbi.cache_cnf()
    dbi.use('referral_db')

if __name__ == '__main__':
    import os
    uid = os.getuid()
    app.debug = True
    app.run('0.0.0.0',uid)