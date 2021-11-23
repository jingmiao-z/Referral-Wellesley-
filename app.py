from flask import (Flask, url_for, render_template, request, redirect, flash, session, send_from_directory)
import sys, os, random, io 
import bcrypt
import cs304dbi as dbi
from datetime import timedelta
from werkzeug.utils import secure_filename
import login_handler, search_handler, user_reg, update
app = Flask(__name__)
app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                           '0123456789'))
                           for i in range(20) ])
# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True
# new for file upload
app.config['UPLOADS'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1*1024*1024 # 1 MB

#Login page deal with 
@app.route('/', methods=['GET','POST'])
def login():
    ''' This is our main login page.'''
    conn = dbi.connect()
    # get values from cookies
    session_uid = session.get('uid')
    session_email = session.get('email')
    session_account_type = session.get('account_type')

    if not session_email:
        # case 1: first visit
        if request.method == 'GET':
            return render_template('login.html')
        # case 2: user submitted a form with their name
        elif request.method == 'POST':
            # if user clicked sign in button
            if request.form['submit'] == 'Sign In':
                email = request.form['email']
                inputPass = request.form['password']
                # check if email exists
                if user_reg.check_email(conn,email):
                    # find password from db 
                    stored, user_type = login_handler.getPassword (conn,email)
                    # hash the input password
                    hashedInput = bcrypt.hashpw(inputPass.encode('utf-8'), stored.encode('utf-8'))
                    hashedInputPass = hashedInput.decode('utf-8')
                    uid = int(user_reg.retrieve_uid(conn, email))
                    # if hashed input pass is equal to the stored password
                    if uid and hashedInputPass == stored:
                        session['uid'] = uid 
                        session['email']  = email
                        session['account_type'] = user_type
                        session['logged_in'] = True
                        if user_type == 'Student':
                            return redirect(url_for('welcome_student', uid=uid))
                        elif user_type == 'Referrer':
                            return redirect(url_for('welcome_referrer', uid=uid))
                        else:
                            return redirect(url_for('welcome_admin', uid=uid))
                    else:
                        flash("Incorrect password. Please try again.")
                        return render_template('login.html')
                else:
                    flash("Account not found. Please register.")
                    return render_template('login.html')
            else:
                return redirect(url_for('base_registration'))
    else:
        # case 3: a regular visit ？
        if request.method == "GET":
            if session_account_type == 'Student':
                return redirect(url_for('welcome_student', uid=session_uid))
            elif session_account_type == 'Referrer':
                return redirect(url_for('welcome_referrer', uid=session_uid))
            else:
                return redirect(url_for('welcome_admin', uid=session_uid))

@app.route('/logout')
def logout():
    ''' This is a function for logout '''
    if session['logged_in']:
        session.pop('uid')
        session.pop('email')
        session.pop('account_type')
        session['logged_in'] = False
        flash('You are logged out.')
        return redirect(url_for('login'))
    else:
        flash('You are not logged in. Please login.')
        return redirect(url_for('login'))

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
        # if email format is invalid
        if not user_reg.check_valid_email(conn, email):
            msg = 'Incorrect email format. Please re-enter.'
            return render_template('baseRegForm.html', msg=msg)
        # if email already exist, cannot re-register 
        if user_reg.check_email(conn,email):
            flash('Email exists, please sign in instead')
            return redirect(url_for("login"))
        year = request.form.get('classyear')
        accountType = request.form.get('accountType')
        # hash the password
        hashed = bcrypt.hashpw(password.encode('utf-8'),
                    bcrypt.gensalt())
        stored_password = hashed.decode('utf-8')
        # insert a new user into the database
        user_reg.insert_user_db(conn,name,email,stored_password,year,accountType)
        # retrieve the user's uid from the database
        uid = int(user_reg.retrieve_uid(conn,email))
        # determine what page to be redirected
        if accountType ==  "Student":
            session['uid'] = uid 
            session['email']  = email
            session['account_type'] = accountType
            return redirect(url_for("profile_student", uid = uid))
        elif accountType ==  "Referrer":
            session['uid'] = uid 
            session['email']  = email
            session['account_type'] = accountType
            return redirect(url_for("profile_referrer", uid = uid))
    
@app.route('/profile_referrer/<int:uid>', methods=['GET', 'POST'])
def profile_referrer(uid):
    ''' This is our profile page for referrer. ''' 
    conn = dbi.connect()
    if request.method == 'GET':
        return render_template('profile_referrer.html', company="", 
                    position="",emailPrefer="", otherContact="", 
                    linkedin="", phoneNumber="")
    else:
        name = user_reg.retrieve_user(conn, uid)
        company = request.form.get('company')
        position = request.form.get('position')
        emailPrefer = request.form.get('contactEmail')
        # if email format is invalid
        if not user_reg.check_valid_email(conn, emailPrefer):
            flash('Incorrect email format. Please re-enter.')
            return render_template('profile_referrer.html')
        linkedin = request.form.get('linkedIn')
        phoneNumber = request.form.get('phnum')
        otherContact = request.form.get('otherContact')
        user_reg.insert_referrer_profile(conn,uid,name,company,position,
    emailPrefer,otherContact,linkedin,phoneNumber)
        session['logged_in'] = True
        return redirect(url_for('welcome_referrer', uid=uid))

@app.route('/profile_student/<int:uid>', methods=['GET', 'POST'])
def profile_student(uid):
    ''' This is our profile page for student. ''' 
    conn = dbi.connect()
    if request.method == 'GET':
        return render_template('profile_student.html', msg="", uid=uid, major ="", 
                    minor="", loc ="", des="", resume="")
    else:
        try:
            # get parameters from the form
            major = request.form.get('major')
            minor = request.form.get('minor')
            prefLoc = request.form.get('prefLoc')
            description = request.form.get('description')
            name = user_reg.retrieve_user(conn, uid)
            f = request.files['resume']
            # if the format of file is not allowed
            if not user_reg.allowed_file(f.filename):
                flash('Incorrect file format. Only support txt, doc, or pdf.')
                return render_template('profile_student.html', uid=uid, major ="", 
                    minor="", loc ="", des="", resume="")
            else:
                # get the file and save the file
                user_filename = f.filename
                ext = user_filename.split('.')[-1]
                filename = secure_filename('{}.{}'.format(uid,ext))
                pathname = os.path.join(app.config['UPLOADS'],filename)
                f.save(pathname)
                # insert the student into the database
                user_reg.insert_student_profile(conn,uid,name,major,minor,filename,prefLoc,description)
                # store user info in session
                session['logged_in'] = True
                return redirect(url_for('welcome_student', uid=uid))
        except Exception as err:
            flash('Upload failed {why}'.format(why=err))
            return render_template('profile_student.html', uid=uid, major ="", 
                    minor="", loc ="", des="", resume="")

@app.route('/update_profile', methods=['GET','POST'])
def update_profile():
    ''' This method is for profile update'''
    if not session['logged_in']:
        return redirect(url_for('logout'))
    conn = dbi.connect()
    session_account_type = session['account_type']
    session_uid = session['uid']
    session_email = session['email']
    if request.method == 'GET': 
        #render the template with information from the student database
        if session_account_type == "Student":
            dic = update.retrieve_student_profile(conn,session_uid)
            major = dic['major']
            minor = dic['minor']
            resume = dic['file']
            # file = send_from_directory(app.config['UPLOADS'], resume)
            loc = dic['preferredLocation']
            des = dic['description']
            uploadMsg = "You already uploaded " + resume
            return render_template("profile_student.html", major = major, 
                    minor = minor, loc = loc, des= des, resume=resume, uploadMsg=uploadMsg)
        #render the template with information from the referrer database
        elif session_account_type == "Referrer":
            dic = update.retrieve_referrer_profile(conn,session_uid)
            company = dic['company']
            position = dic['position']
            emailPrefer = dic['emailPrefer']
            otherContact = dic['otherContact']
            linkedin = dic['linkedin']
            phoneNumber = dic['phoneNumber']
            return render_template('profile_referrer.html', company=company, 
                    position=position,emailPrefer=emailPrefer, otherContact=otherContact, 
                    linkedin=linkedin, phoneNumber=phoneNumber)
    else:
        #update the profile
        if session_account_type == "Student":
            try:
                # get parameters from the form
                major = request.form.get('major')
                minor = request.form.get('minor')
                prefLoc = request.form.get('prefLoc')
                description = request.form.get('description')
                name = user_reg.retrieve_user(conn, session_uid)
                f = request.files['resume']
                if not user_reg.allowed_file(f.filename):
                    flash('Incorrect file format. Only support txt, doc, or pdf.')
                    return render_template('profile_student.html', major = major, 
                    minor = minor, loc = prefLoc, des= description, resume="")
                else:
                    user_filename = f.filename
                    ext = user_filename.split('.')[-1]
                    filename = secure_filename('{}.{}'.format(session_uid,ext))
                    pathname = os.path.join(app.config['UPLOADS'],filename)
                    f.save(pathname)
                    # send_file(returned_file, )
                    # return send_file(io.BytesIO(returned_file.data))

                    update.update_student_profile(conn,session_uid,major,minor,filename,prefLoc,description)
                    return redirect(url_for('welcome_student', uid=session_uid))
            except Exception as err:
                flash('Upload failed {why}'.format(why=err))
                return 'incorrect' #redirect to page they are on and they can get a new blank form 
            #re-render the page filling in all information that they just sent us 
        elif session_account_type == "Referrer":
            name = user_reg.retrieve_user(conn, session_uid)
            company = request.form.get('company')
            position = request.form.get('position')
            emailPrefer = request.form.get('contactEmail')
            linkedin = request.form.get('linkedIn')
            phoneNumber = request.form.get('phnum')
            otherContact = request.form.get('otherContact')
            # if email format is invalid
            if not user_reg.check_valid_email(conn, emailPrefer):
                flash('Incorrect email format. Please re-enter.')
                return render_template('profile_referrer.html', company=company, 
                    position=position, emailPrefer="", otherContact=otherContact, 
                    linkedin=linkedin, phoneNumber=phoneNumber)
            update.update_referrer_profile(conn,session_uid,company,position,
        emailPrefer,otherContact,linkedin,phoneNumber)
            return redirect(url_for('welcome_referrer', uid=session_uid))

#QQQ: haven't implemented this yet
#  is this get only? Not sure since students can only check but not post anything right? 
@app.route('/welcome_student/<int:uid>' ,methods=['GET', 'POST'])
def welcome_student(uid):
    if not session['logged_in']:
        return redirect(url_for('logout')) 
    conn = dbi.connect()
    return render_template('welcome_student.html', uid=uid)

@app.route('/welcome_referrer/<int:uid>',methods=['GET','Post'])
def welcome_referrer(uid):
    if not session['logged_in']:
        return redirect(url_for('logout')) 
    conn = dbi.connect()
    return render_template('welcome_referrer.html',uid=uid)

@app.route('/welcome_admin/<int:uid>')
def welcome_admin(uid):
    if not session['logged_in']:
        return redirect(url_for('logout')) 
    conn = dbi.connect()
    return render_template('welcome_admin.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    ''' This method is for redirecting to dashboard'''
    if not session['logged_in']:
        return redirect(url_for('logout')) 
    conn = dbi.connect()
    session_account_type = session['account_type']
    session_uid = session['uid']
    if session_account_type == "Student":
        return redirect(url_for('welcome_student', uid=session_uid))
    elif session_account_type == "Referrer":
        return redirect(url_for('welcome_referrer', uid=session_uid))
    
@app.route('/mainSearch/', methods=['GET', 'POST'])
def mainSearch():
    ''' This method is for our main search'''
    if not session['logged_in']:
        return redirect(url_for('logout')) 
    conn = dbi.connect()

    if request.method == 'GET':
        return render_template('mainSearch.html')
    else:
        query = request.form['query']
        search_by = request.form['search_by']
        print('You submitted {} and {}'.format(query, search_by))
        #if the user select search by position
        if search_by == 'position':
            results = search_handler.searchByPosition(conn, query)   
        #if the user select search by referrer
        elif search_by == 'referrer':
            results = search_handler.searchByReferrer(conn, query)
        #if the user select search by company
        else:
            results = search_handler.searchByCompany(conn, query)
        #if there is no result in the database
        if not results:
            desc = 'No results'
            msg = 'Please search another keywords.'
            return render_template('search.html', msg=msg, desc=desc)
        return render_template('search.html', results=results)

@app.route('/position_detail')
def position_detail():
    if not session['logged_in']:
        return redirect(url_for('logout')) 
    conn = dbi.connect()
    return render_template('position_detail.html')

@app.before_first_request
def startup():
    dbi.cache_cnf()
    dbi.use('referral_db')
    session['logged_in'] = False

if __name__ == '__main__':
    import os
    uid = os.getuid()
    app.debug = True
    app.run('0.0.0.0',uid)


