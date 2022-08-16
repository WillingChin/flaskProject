import os
from functools import wraps
from flask import Flask, render_template, send_file, request, session, redirect, url_for, send_from_directory
from flask_wtf.csrf import CSRFProtect, CSRFError


from charts import *

import logging
import logging.config
import sys


'''
@Title Router controller
@Project ：Crime data analysis
@File    ：app.py
@Author  ：XChen202
@Date    ：7/15/2022 9:42 AM
@evn python3.7
'''


# hot run
# https://pyquestions.com/auto-reloading-python-flask-app-upon-code-changes
from user_database import *

app = Flask(__name__)
csrf = CSRFProtect(app)

logging.basicConfig(
    level=logging.DEBUG,
    # format="%(asctime)s [%(levelname)s] %(message)s",
    # example for website: https://blog.csdn.net/cxx654/article/details/110167330
    format="%(asctime)s - %(levelname)s - %(process)d - %(thread)d - %(filename)s - %(funcName)s - %(lineno)d - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logging.debug('Flask running success.');

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400

@app.after_request
def apply_caching(response):
    #XSS
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "0"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Type"] = "text/html; charset=utf-8"

    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
    )

    response.set_cookie('username', 'flask', secure=True, httponly=True, samesite='Lax')
    return response

if os.getenv("FLASK_WEB_APP_KEY") != None:
    app.secret_key = os.environ['FLASK_WEB_APP_KEY']

# login validation(every page)
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if request.method == "POST":
            return f(*args, **kwargs)
        """login session"""
        if 'logged_in' in session and session["logged_in"] == True:
            logging.info(session['username'] + " entry main page.")
            return redirect(url_for('main'))
        else:
            pass
        return render_template('login.html')
    return wrap
# end login_required

# login validation(validation session state)
def main_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        """login session"""
        if 'logged_in' in session and session["logged_in"] == True:
            logging.info(session['username'] + " entry main page.")
            return f(*args, **kwargs)
        else:
            pass
        return render_template('login.html')
    return wrap
# end main_required

@app.route('/main')
@main_required
def main():
    """Entry point; the view for the main page"""
    types = get_chart_type_data(code='chart_type')
    crimes = get_chart_type_data(code='crime_type')
    return render_template('main.html', chart_type_data=types, crime_type=crimes, chart_file=None)
# end main

@app.route('/logout',  methods=["GET", "POST"])
def logout():
    try:
        logging.info("logout")
        error = ''
        session['logged_in'] = False
        session['username'] = None
        return render_template('login.html', error=error)
    except Exception as e:
        logging.warning(e)
# end login


#GET -> login.html POST -> main.html
@app.route('/',  methods=["GET", "POST"])
@app.route("/login",  methods=["GET", "POST"])
@login_required
def login():
    """The view for the login page"""
    try:
        error = ''
        if request.method == "POST":
            attempted_username = request.form['username']
            attempted_password = request.form['password']
            # save user information with session
            if attempted_username == 'admin' and attempted_password == os.environ['USER_PASSWORD']:
                session['logged_in'] = True
                session['username'] = request.form['username']
                logging.info(session['username'] + " login success.")
                return redirect(url_for('main', ))
            else:
                logging.info('Invalid credentials. Please, try again.')
                error = 'Invalid credentials. Please, try again.'
        # GET logic
        return render_template('login.html', error=error)
    except Exception as e:
        logging.warning(e)
        return render_template('login.html', error=str(e))
# end login


@app.route('/chart_plot_image',  methods=["GET"])
def chart_plot_image():
    chart_type = request.values.get("chart_type")
    if chart_type == None or chart_type == "":
        selected = get_chart_type_selected_data("chart_type", 1);
        if selected == None or len(selected) == 0 :
            logging.info(" dict code chart_type is empty!");
            return;
        chart_type = selected[0].item_value;

    args = request.args
    webData = getWebData(args);
    img = None;


    if chart_type == "pie":
        img = get_pie_chart_iamge(webData)
    elif chart_type == "line":
        img = get_line_chart_iamge(webData)
    elif chart_type == "bar":
        img = get_bar_chart_iamge(webData)
    return send_file(img, mimetype='image/png', cache_timeout=0)


# test route
@app.route('/test')
def hello_world():  # put application's code here
    logging.info('frist')
    return 'Hello World!'
# end hello_world


if __name__ == '__main__':
    app.debug = True
    app.run()


