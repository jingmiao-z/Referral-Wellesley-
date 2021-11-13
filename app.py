from flask import (Flask, url_for, render_template, request, redirect, flash)
# import referral_db as dbi
import random 
app = Flask(__name__)

app.secret_key = 'your secret here'
# replace that with a random key
app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

#student search bar 
@app.route('/search')
def search():
    # conn = dbi.connect()
    return render_template('search_bar.html')


# @app.before_first_request
# def startup():
#     dbi.cache_cnf()
#     dbi.use('referral_db')

if __name__ == '__main__':
    import os
    uid = os.getuid()
    app.debug = True
    app.run('0.0.0.0',uid)
