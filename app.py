
from flask import (Flask, url_for, render_template, request, redirect, flash)
import random 
import bcrypt
import cs304dbi as dbi
import login_handler, search_handler, user_reg

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
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        if request.form['submit'] == 'Sign In':
            email = request.form['email']
            inputPass = request.form['password']
            #find password from db 
            stored, user_type = login_handler.getPassword (conn,email)

            hashedInput = bcrypt.hashpw(inputPass.encode('utf-8'), stored.encode('utf-8'))
            hashedInputPass = hashedInput.decode('utf-8')
            
            if hashedInputPass == stored:
                if user_type == 'Student':
                    return redirect(url_for('welcome_student'))
                elif user_type == 'Referrer':
                    return redirect(url_for('welcome_referrer'))
                else:
                    return redirect(url_for('welcome_admin'))
            else:
                flash("Account not found or incorrect password. Please try again or register.")
                return render_template('login.html')
        elif request.form['submit'] == 'Sign Up':
            return redirect(url_for('base_registration'))
    
@app.route('/base_registration',methods=['GET', 'POST'])
def base_registration():
    conn = dbi.connect()
    if request.method == 'GET':
        return render_template('baseRegForm.html')
    else:
        name = request.form.get('name')
        password = request.form.get('password')
        email = request.form.get('email')
        year = request.form.get('classyear')
        accountType = request.form.get('accountType')
        hashed = bcrypt.hashpw(password.encode('utf-8'),
                    bcrypt.gensalt())
        stored_password = hashed.decode('utf-8')
        user_reg.insert_user_db(conn,name,email,stored_password,year,accountType)
        uid = user_reg.user_id(conn,email)
        if accountType ==  "Student":
            return redirect(url_for("welcome_student",uid = uid))
        elif accountType ==  "Referrer":
            return redirect(url_for("welcome_referrer",uid = uid))
        
@app.route('/welcome_student/<int:uid>')
def welcome_student(uid):
    conn = dbi.connect()
    return render_template('welcome_student.html')

@app.route('/welcome_referrer/<int:uid>')
def welcome_referrer(uid):
    conn = dbi.connect()
    return render_template('welcome_referrer.html')

@app.route('/welcome_admin/<int:uid>')
def welcome_admin(uid):
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

@app.route('/mainSearch/', methods=['GET', 'POST'])
def mainSearch():
    conn = dbi.connect()

    if request.method == 'GET':
        return render_template('mainSearch.html')
    else:
        query = request.form['query']
        search_by = request.form['search_by']
        print('You submitted {} and {}'.format(query, search_by))
        if search_by == 'position':
            results = search_handler.searchByPosition(conn, query)            
        elif search_by == 'referrer':
            results = search_handler.searchByReferrer(conn, query)
        else:
            results = search_handler.searchByPosition(conn, query)
        
        print(results)
        return render_template('search.html', results=results)

@app.route('/position_detail')
def position_detail():
    conn = dbi.connect()
    return render_template('position_detail.html')

@app.before_first_request
def startup():
    dbi.cache_cnf()
    dbi.use('referral_db')

if __name__ == '__main__':
    import os
    uid = os.getuid()
    app.debug = True
    app.run('0.0.0.0',uid)