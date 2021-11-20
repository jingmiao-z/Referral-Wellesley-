
from flask import (Flask, url_for, render_template, request, redirect, flash, session, make_response)
import random 
import bcrypt
import cs304dbi as dbi
from datetime import timedelta
import login_handler, search_handler, user_reg

app = Flask(__name__)
app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                           '0123456789'))
                           for i in range(20) ])
app.permanent_session_lifetime = timedelta(seconds=5)

@app.route('/', methods=['GET','POST'])
def login():
    session.permanent = True
    conn = dbi.connect()
    # get email and password from cookies
    cookie_email = request.cookies.get('email')
    cookie_password = request.cookies.get('password')
    cookie_account_type = request.cookies.get('account_type')
    # no cookie set
    if not cookie_email and not cookie_password:
        # case 1: first visit
        if request.method == 'GET':
            return render_template('login.html', cookies=request.cookies)
        # case 2: user submitted a form with their name
        elif request.method == 'POST':
            # if user clicked sign in button
            if request.form['submit'] == 'Sign In':
                email = request.form['email']
                inputPass = request.form['password']
                # find password from db 
                stored, user_type = login_handler.getPassword (conn,email)
                # hash the input password
                hashedInput = bcrypt.hashpw(inputPass.encode('utf-8'), stored.encode('utf-8'))
                hashedInputPass = hashedInput.decode('utf-8')
                # if hashed input pass is equal to the stored password
                if hashedInputPass == stored:
                    if user_type == 'Student':
                        resp = make_response(
                            render_template('welcome_student.html',
                            cookies=request.cookies))
                        # return redirect(url_for('welcome_student'))
                    elif user_type == 'Referrer':
                        resp = make_response(
                            render_template('welcome_referrer.html',
                            cookies=request.cookies))
                        # return redirect(url_for('welcome_referrer'))
                    else:
                        resp = make_response(
                            render_template('welcome_admin.html',
                            cookies=request.cookies))
                        # return redirect(url_for('welcome_admin'))
                    # store cookie to response
                    resp.set_cookie('email', email)
                    resp.set_cookie('password', hashedInputPass)
                    resp.set_cookie('account_type', user_type)
                    return resp
                else:
                    flash("Account not found or incorrect password. Please try again or register.")
                    return render_template('login.html', cookies=request.cookies)
            elif request.form['submit'] == 'Sign Up':
                return redirect(url_for('base_registration'))
    # cookie is set
    else:
        # case 3: a regular visit
        if request.method == "GET":
            if account_type == 'Student':
                resp = make_response(
                    render_template('welcome_student.html',
                    cookies=request.cookies))
            elif account_type == 'Referrer':
                resp = make_response(
                    render_template('welcome_referrer.html',
                    cookies=request.cookies))
            else:
                resp = make_response(
                    render_template('welcome_admin.html',
                    cookies=request.cookies))
        # case 4: time out
        else:
            # message
            resp = make_response(
                    render_template('login.html',
                    cookies=request.cookies))
            resp.set_cookie('email', '', expires=0)
            resp.set_cookie('password', '', expires=0)
            resp.set_cookie('account_type', '', expires=0)
        return resp
    
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
            results = search_handler.searchByCompany(conn, query)
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