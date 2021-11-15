
from flask import (Flask, url_for, render_template, request, redirect)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('mainSearch.html')

if __name__ == '__main__':
    import os
    uid = os.getuid()
    app.debug = True
    app.run('0.0.0.0',uid)