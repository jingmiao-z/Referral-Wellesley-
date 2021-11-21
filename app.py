
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
# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True
# new for file upload
app.config['UPLOADS'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1*1024*1024 # 1 MB

@app.route('/', methods=['GET','POST'])
def login():
    ''' This is our main login page.'''
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
            if cookie_account_type == 'Student':
                resp = make_response(
                    render_template('welcome_student.html',
                    cookies=request.cookies))
            elif cookie_account_type == 'Referrer':
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
    
    
#QQQ: add logic that if email duplicate, cannot register 
@app.route('/base_registration',methods=['GET', 'POST'])
def base_registration():
    ''' This is our base registration page. '''
    conn = dbi.connect()
    if request.method == 'GET':
        return render_template('baseRegForm.html')
    else:
        # get parameters from the form
        name = request.form.get('name')
        password = request.form.get('password')
        email = request.form.get('email')
        year = request.form.get('classyear')
        accountType = request.form.get('accountType')
        # hash the password
        hashed = bcrypt.hashpw(password.encode('utf-8'),
                    bcrypt.gensalt())
        stored_password = hashed.decode('utf-8')
        # insert a new user into the database
        user_reg.insert_user_db(conn,name,email,stored_password,year,accountType)
        # retrieve the user's uid from the database
        uid = user_reg.user_id(conn,email)
        # determine what page to be redirected
        if accountType ==  "Student":
            return redirect(url_for("profile_student", uid = uid))
        elif accountType ==  "Referrer":
            return redirect(url_for("profile_referrer", uid = uid))
    
@app.route('/profile_referrer/<int:uid>', methods=['GET', 'POST'])
def profile_referrer(uid):
    ''' This is our profile page for referrer. ''' 
    conn = dbi.connect()
    if request.method == 'GET':
        return render_template('profile_referrer.html', uid = uid)
    else:
        name = user_reg.retrieve_user(conn, uid)
        company = request.form.get('company')
        position = request.form.get('position')
        emailPrefer = request.form.get('contactEmail')
        linkedin = request.form.get('linkedIn')
        phoneNumber = request.form.get('phnum')
        otherContact = request.form.get('otherContact')
        user_reg.insert_referrer_profile(conn,uid,name,company,position,
    emailPrefer,otherContact,linkedin,phoneNumber)
        print("saved")
        return redirect(url_for('welcome_referrer', uid=uid))
@app.route('/profile_student/<int:uid>', methods=['GET', 'POST'])
def profile_student(uid):
    ''' This is our profile page for student. ''' 
    conn = dbi.connect()
    if request.method == 'GET':
        return render_template('profile_student.html', uid = uid)
    else:
        try:
            # get parameters from the form
            major = request.form.get('major')
            minor = request.form.get('minor')
            prefLoc = request.form.get('prefLoc')
            description = request.form.get('description')
            name = user_reg.retrieve_user(conn, uid)
            f = request.files['pic']
            user_filename = f.filename
            ext = user_filename.split('.')[-1]
            filename = secure_filename('{}.{}'.format(uid,ext))
            pathname = os.path.join(app.config['UPLOADS'],filename)
            f.save(pathname)
            user_reg.insert_student_profile(conn,uid,name,major,minor,filename,prefLoc,description)
            flash('Upload successful')
            return redirect(url_for('welcome_student', uid=uid))
        except Exception as err:
            flash('Upload failed {why}'.format(why=err))
            return render_template('profile_student.html', uid=uid)

#QQQ: is this get only? Not sure since students can only check but not post anything right? 
@app.route('/welcome_student/<int:uid>' ,methods=['GET', 'POST'])
def welcome_student(uid):
    conn = dbi.connect()
    return render_template('welcome_student.html', uid=uid)

@app.route('/welcome_referrer/<int:uid>',methods=['GET','Post'])
def welcome_referrer(uid):
    conn = dbi.connect()
    return render_template('welcome_referrer.html',uid = uid)

@app.route('/welcome_admin/<int:uid>')
def welcome_admin(uid):
    conn = dbi.connect()
    return render_template('welcome_admin.html')

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