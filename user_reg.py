
import cs304dbi as dbi
import re

# credit to: https://www.mygreatlearning.com/blog/regular-expression-in-python/
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc'}

def insert_user_db(conn,name,email,password,year,account_type):
    '''Insert a new user into database, the password here is after salt'''
    try: 
        curs = dbi.dict_cursor(conn)
        sql = '''INSERT INTO user (name, email, password,
        classYear,type) VALUES (%s,%s,%s,%s,%s)'''
        curs.execute(sql,[name,email,password,year,account_type])
        conn.commit()
    except Exception as err:
        print('something went wrong', repr(err))
        
def insert_student_profile (conn,sid,name,major,minor,
    file,preferredLocation,description):
    '''Insert a new student into database'''
    try: 
        curs = dbi.dict_cursor(conn)
        sql = '''INSERT INTO student (sid, name, major, minor, file,
        preferredLocation,description) VALUES (%s,%s,%s,%s,%s,%s,%s)'''   
        curs.execute(sql,[sid,name,major,minor,file,preferredLocation,description])
        conn.commit()
    except Exception as err:
        print('something went wrong', repr(err))

def insert_referrer_profile(conn,rid,name,company,position,
    emailPrefer,otherContact,linkedin,phoneNumber):
    '''Insert a new referrer into database'''
    try: 
        curs = dbi.dict_cursor(conn)
        sql = '''INSERT INTO referrer (rid,name,company,position,emailPrefer,
            otherContact,linkedin,phoneNumber) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'''
        curs.execute(sql,[rid,name,company,position,
        emailPrefer,otherContact,linkedin,phoneNumber])
        conn.commit()
    except Exception as err:
        print('something went wrong', repr(err))

def retrieve_user(conn, uid):
    ''' Retrieve user name from user table with provided uid '''
    curs = dbi.dict_cursor(conn)
    sql = '''select name from user where uid = %s'''
    curs.execute(sql,[uid])
    return curs.fetchone()["name"]

def allowed_file(filename):
    ''' Determine whether the file is allowed '''
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def retrieve_uid(conn, email):
    ''' Retrieve uid from user table with provided email, if not exist, return None '''
    curs = dbi.dict_cursor(conn)
    sql = '''select uid from user where email = %s'''
    curs.execute(sql,[email])
    dic = curs.fetchone()
    if dic != None:
        return dic["uid"]
    else:
        return dic

def check_email(conn,email):
    '''Check if email already in db, return true if it exists'''
    curs = dbi.dict_cursor(conn)
    sql = '''select email from user where email = %s'''
    curs.execute(sql,[email])
    return curs.fetchone() != None
    
def check_valid_email(conn, email):
    ''' Check if email is in valid format '''
    if(re.fullmatch(regex, email)):
        return True
    else:
        print("Invalid Email")
        return False