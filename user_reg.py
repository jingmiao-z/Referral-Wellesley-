import cs304dbi as dbi
def insert_user_db(conn,name,email,password,year,account_type):
    '''insert a new user into database, the password here is after salt'''
    try: 
        curs = dbi.dict_cursor(conn)
        sql = '''INSERT INTO user (name, email, password,
        classYear,type) VALUES (%s,%s,%s,%s,%s);'''
        curs.execute(sql,[name,email,password,year,account_type])
        conn.commit()
    except Exception as err:
        print('something went wrong', repr(err))

def user_id(conn,email):
    '''return user's id as a int given email'''
    curs = dbi.dict_cursor(conn)
    sql = "select uid from user where email = %s"
    curs.execute(sql,[email])
    return int(curs.fetchone()["uid"])

def insert_student_profile(conn,sid,name,major,minor,
    file,preferredLocation,description):
    '''insert a new student into database'''
    curs = dbi.dict_cursor(conn)
    sql = '''INSERT INTO student (sid, name, major, minor,file,
    preferredLocation,description) VALUES (%s,%s,%s,%s,%s,%s,%s);'''   
    curs.execute(sql,[sid,name,major,minor,file,preferredLocation,description])
    conn.commit() 

def insert_referrer_profile(conn,rid,name,company,position,
    emailPrefer,otherContact,linkedin,phoneNumber):
    '''insert a new student into database'''
    curs = dbi.dict_cursor(conn)
    sql = '''INSERT INTO student (sid, name, major, minor,file,
    preferredLocation,description) VALUES (%s,%s,%s,%s,%s,%s,%s);'''    
    curs.execute(sql,[sid,name,major,minor,file,preferredLocation,description])
    conn.commit()


def insert_admin_profile(conn,aid):
    sql = '''INSERT INTO admin (aid, name, major, minor,file,
    preferredLocation,description) VALUES (%s,%s,%s,%s,%s,%s,%s);'''    
    curs.execute(sql,[sid,name,major,minor,file,preferredLocation,description])



