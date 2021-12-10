from flask import (Flask, url_for, render_template, request, redirect, flash, session, send_from_directory, jsonify)
import sys, os, random, io 
import bcrypt
import cs304dbi as dbi
from datetime import timedelta
from werkzeug.utils import secure_filename
import login_handler, search_handler, user_reg, update, job_handler, message_center, refer_handler
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

#Login page deal with old user login
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

#logout route, pop all the sessions
@app.route('/logout/')
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

@app.route('/base_registration/',methods=['GET', 'POST'])
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
        return render_template('profile_referrer.html', uid = uid, dic={})
    else:
        dic = {}
        name = user_reg.retrieve_user(conn, uid)
        dic['company'] = request.form.get('company')
        dic['position'] = request.form.get('position')
        emailPrefer = request.form.get('contactEmail')
        # if email format is invalid
        if not user_reg.check_valid_email(conn, emailPrefer):
            flash('Incorrect email format. Please re-enter.')
            return render_template('profile_referrer.html', dic=dic, uid=uid)
        dic['emailPrefer'] = emailPrefer
        dic['linkedin'] = request.form.get('linkedIn')
        dic['phoneNumber'] = request.form.get('phnum')
        dic['otherContact'] = request.form.get('otherContact')
        user_reg.insert_referrer_profile(conn,uid,name,dic['company'],dic['position'],
    dic['emailPrefer'],dic['otherContact'],dic['linkedin'], dic['phoneNumber'])
        session['logged_in'] = True
        return redirect(url_for('welcome_referrer', uid=uid))

@app.route('/profile_student/<int:uid>', methods=['GET', 'POST'])
def profile_student(uid):
    ''' This is our profile page for student. ''' 
    conn = dbi.connect()
    if request.method == 'GET':
        return render_template('profile_student.html', msg="", uid=uid, dic={})
    else:
        try:
            dic = {}
            # get parameters from the form
            dic['major'] = request.form.get('major')
            dic['minor'] = request.form.get('minor')
            dic['preferredLocation'] = request.form.get('prefLoc')
            dic['description'] = request.form.get('description')
            name = user_reg.retrieve_user(conn, uid)
            f = request.files['resume']
            # if the format of file is not allowed
            if not user_reg.allowed_file(f.filename):
                flash('Incorrect file format. Only support txt, doc, or pdf.')
                return render_template('profile_student.html', is_update= False, uid=uid, dic=dic)
            else:
                # get the file and save the file
                user_filename = f.filename
                ext = user_filename.split('.')[-1]
                filename = secure_filename('{}.{}'.format(uid,ext))
                pathname = os.path.join(app.config['UPLOADS'],filename)
                f.save(pathname)
                # insert the student into the database
                user_reg.insert_student_profile(conn,uid,name,dic['major'],
                    dic['minor'],filename,dic['preferredLocation'],dic['description'])
                # store user info in session
                session['logged_in'] = True
                return redirect(url_for('welcome_student', uid=uid))
        except Exception as err:
            flash('Upload failed {why}'.format(why=err))
            #although we can retrieve user's input (which is a better way to implement), we'll give students a blank form for now 
            return render_template('profile_student.html', is_update= False, uid = uid, dic={})

@app.route('/update_profile/', methods=['GET','POST'])
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
            return render_template("profile_student.html", is_update= True, uid = session_uid, dic=dic)
        #render the template with information from the referrer database
        elif session_account_type == "Referrer":
            dic = update.retrieve_referrer_profile(conn,session_uid)
            return render_template('profile_referrer.html', is_update= True, uid = session_uid, dic=dic)
    else:
        #update the profile
        if session_account_type == "Student":
            try:
                # get parameters from the form
                dic = {}
                dic['major'] = request.form.get('major')
                dic['minor'] = request.form.get('minor')
                dic['preferredLocation'] = request.form.get('prefLoc')
                dic['description'] = request.form.get('description')
                f = request.files['resume']
                if not user_reg.allowed_file(f.filename):
                    flash('Incorrect file format. Only support txt, doc, or pdf.')
                    return render_template('profile_student.html', is_update= True, uid = session_uid, dic = dic)
                else:
                    user_filename = f.filename
                    ext = user_filename.split('.')[-1]
                    filename = secure_filename('{}.{}'.format(session_uid,ext))
                    pathname = os.path.join(app.config['UPLOADS'],filename)
                    f.save(pathname)
                    update.update_student_profile(conn,session_uid,dic['major'],dic['minor'],
                    filename,dic['preferredLocation'],dic['description'])
                    return redirect(url_for('welcome_student', uid=session_uid))
            except Exception as err:
                flash('Upload failed {why}'.format(why=err))
                #although we can retrieve user's input (which is a better way to implement), we'll give students a blank form for now 
                return render_template('profile_student.html', is_update= True, uid = session_uid) #redirect to page they are on and they can get a new blank form             #re-render the page filling in all information that they just sent us 
        elif session_account_type == "Referrer":
            dic = {}
            dic['company'] = request.form.get('company')
            dic['position'] = request.form.get('position')
            emailPrefer = request.form.get('contactEmail')
            if not user_reg.check_valid_email(conn, emailPrefer):
                flash('Incorrect email format. Please re-enter.')
                return render_template('profile_referrer.html', is_update = True, uid=session_uid, dic=dic)
            dic['linkedin'] = request.form.get('linkedIn')
            dic['phoneNumber'] = request.form.get('phnum')
            dic['otherContact'] = request.form.get('otherContact')
            # if email format is invalid
            dic['emailPrefer'] = emailPrefer
            update.update_referrer_profile(conn,session_uid,dic['company'],dic['position'],
                dic['emailPrefer'],dic['otherContact'],dic['linkedin'], dic['phoneNumber'])
            return redirect(url_for('welcome_referrer', uid=session_uid))

@app.route('/welcome_student/<int:uid>' ,methods=['GET'])
def welcome_student(uid):
    '''This method is used for student dashboard'''
    if not session['logged_in']:
        return redirect(url_for('logout')) 
    conn = dbi.connect()
    pid = job_handler.retrieve_pid(conn, uid)
    if not pid:
        msg = 'No active referral application'
        return render_template('welcome_student.html', msg=msg)
    positions = job_handler.retrieve_applied_positions(conn, uid)
    return render_template('welcome_student.html', positions=positions)

@app.route('/welcome_referrer/<int:uid>',methods=['GET'])
def welcome_referrer(uid):
    ''' This method is used for referrer dashboard'''
    if not session['logged_in']:
        return redirect(url_for('logout')) 
    conn = dbi.connect()
    results = job_handler.retrieve_applied_student(conn, uid)
    if not results:
        msg = 'No student applied'
        return render_template('welcome_referrer.html', msg=msg)
    return render_template('welcome_referrer.html',uid=uid,results = results)

@app.route('/welcome_admin/<int:uid>')
def welcome_admin(uid):
    ''' This method is used for admin dashboard'''
    if not session['logged_in']:
        return redirect(url_for('logout'))
    conn = dbi.connect()
    return render_template('welcome_admin.html')

@app.route('/dashboard/', methods=['GET'])
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
    ''' This method is for our main search '''
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

@app.route('/position_detail/<int:pid>', methods=['GET'])
def position_detail(pid):
    ''' This method is for position detail page '''
    if not session['logged_in']:
        return redirect(url_for('logout')) 
    conn = dbi.connect()
    position = job_handler.retrieve_position(conn, pid)
    referrer_contact = job_handler.retrieve_referrer_contact(conn, position['rid'])
    session['jobInfo'] = [position['pid'], position['rid']]
    return render_template('position_detail.html', position=position, 
                            ask="True", referrer_contact=referrer_contact)

@app.route('/dashboard_position_detail/<int:pid>', methods=['GET'])
def dashboard_position_detail(pid):
    ''' This method is for position detail page'''
    if not session['logged_in']:
        return redirect(url_for('logout')) 
    conn = dbi.connect()
    position = job_handler.retrieve_position(conn, pid)
    referrer_contact = job_handler.retrieve_referrer_contact(conn, position['rid'])
    session['jobInfo'] = [position['pid'], position['rid']]
    session_uid = session['uid']
    return render_template('position_detail.html', position=position, 
                            dashboard="True", uid = session_uid, referrer_contact=referrer_contact)

@app.route('/ask_for_refer/', methods=['GET', 'POST'])
def ask_for_refer():
    ''' This method is for when student want to ask for a referral '''
    if not session['logged_in']:
        return redirect(url_for('logout')) 
    conn = dbi.connect()
    session_uid = session['uid']
    pid = session['jobInfo'][0]
    rid = session['jobInfo'][1]
    if request.method == 'GET':
        return render_template('askForRefer.html', pid = pid)
    else:
        if refer_handler.check_duplicate_request(conn, rid, session_uid, pid):
            flash("You already submitted a request of referral for this position. You cannot submit twice.")
            return redirect(url_for('mainSearch'))
        else: 
            try: 
                whyCompany = request.form['whyCompany']
                whyPosition = request.form['whyPosition']
                refer_handler.ask_for_refer(conn, rid, session_uid, pid, whyCompany, whyPosition)
                flash("Successfully submit a request for an referral. Please go to your dashboard for status update.")
                session.pop('jobInfo')
                return redirect(url_for('mainSearch'))
            except Exception as err:
                flash("something went wrong", repr(err))
                session.pop('jobInfo')
                return redirect(url_for('position_detail', pid=pid))

@app.route('/jobs/', methods=['GET', 'POST'])
def jobs():
    '''This route is used for referrer submitting jobs that they can refer students'''
    if not session['logged_in']:
        return redirect(url_for('logout')) 
    conn = dbi.connect()
    if request.method == 'GET':
        return render_template('jobSubmit.html')
    else:
        rid = session.get('uid')
        company = request.form.get("company")
        pos_name = request.form.get("pos_name")
        referrer_name = job_handler.name(conn,rid)
        postionLocation = request.form.get("location")
        materialNeeded = request.form.get("materialNeeded")
        submitDeadline = request.form.get("submitDeadline")
        job_handler.storeJob(conn,rid,company,pos_name,referrer_name,postionLocation,
            materialNeeded,submitDeadline)
        session_uid = session['uid']
        return redirect(url_for('welcome_referrer',uid = session_uid))

@app.route('/student_detail/<int:sid>/<int:pid>', methods=['GET','POST'])
def student_detail(sid,pid):
    ''' This method is for student detail page '''
    if not session['logged_in']:
        return redirect(url_for('logout')) 
    conn = dbi.connect()
    session_uid = session['uid']
    if request.method == 'GET':
        dic = job_handler.student_detail(conn, sid)
        return render_template('student_detail.html',dic=dic, uid = session_uid,pid=pid,sid= sid )
    else:
        status = request.form.get('action')
        rid = session_uid
        job_handler.change_status(conn,status,rid,sid,pid)
        return redirect(url_for('welcome_referrer', uid=session_uid))

#NOT IMPLEMENTED YET, SEE BETA VERSION
@app.route('/messageCenter/', methods=['GET'])
def messageCenter():
    '''Route for message Center, not implemented yet. DO NOT GRADE'''
    if not session['logged_in']:
        return redirect(url_for('logout'))
    conn = dbi.connect()
    announcements = message_center.retrieve_announcement(conn)
    print(announcements)
    if not announcements:
        return jsonify({'empty': True, 'emptymsg': "No Notifications"})
    return jsonify({'empty': False, 'message': announcements})

@app.route('/keywords/<keyword>/<search_by>', methods=['GET'])
def keywords(keyword, search_by):
    '''Route used for Ajax - autofill keywords when student search for positions to apply'''
    if not session['logged_in']:
        return redirect(url_for('logout'))
    conn = dbi.connect()
    if request.method == 'GET':
        if search_by == 'position':
            keywordLists = search_handler.get_matched_position_names(conn, keyword)
        #if the user select search by referrer
        elif search_by == 'referrer':
            keywordLists = search_handler.get_matched_referrer_names(conn, keyword)
        #if the user select search by company
        else:
            keywordLists = search_handler.get_matched_company_names(conn, keyword)
        return jsonify({'search_by': search_by, 'keywords': keywordLists})

@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    ''' This method get file and allows the referrer to 
    download student's resume file'''
    upload_file = os.path.join(app.root_path, app.config['UPLOADS'])
    return send_from_directory(directory=upload_file, path=filename)

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


