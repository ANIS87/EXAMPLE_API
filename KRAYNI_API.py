
#This work is develloped by KRAYNI Anis (anis.krayni@gmail.com) 

###################################################################################
                                  #Python Libraries
###################################################################################
import os 
import sys 
import json
import numpy as np
import string
import StringIO
from PIL import Image
import requests
import sqlite3
from flask import Flask, request, jsonify, session, g, redirect, url_for, abort, render_template, flash,send_from_directory,make_response,Response,jsonify
from flask import send_file
from flask_login import login_user, logout_user, current_user, LoginManager, login_required
from flask_mail import Mail, Message
from functools import wraps
from contextlib import closing
from werkzeug.utils import secure_filename
from my_functions import resize_image, allowed_file,get_product
#data base
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from datetime import datetime
###################################################################################
                                    #Configuartion 
###################################################################################


#root configurations
UPLOAD_FOLDER = '/home/krayni/Bureau/PIXIT_SEG/API/First_API/data'
SAVE_FOLDER ='/home/krayni/Bureau/PIXIT_SEG/API/First_API/res'
DATABASE = '/tmp/my_data_base.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'krayni'
PASSWORD = 'tunisie'
NUM='1920'
MAIL_SERVER='my_name@yahoo.fr'


#data base configuration #mysql for tabels slect from ; and mongodb for documents (json format) :db.test.find
SQLALCHEMY_DATABASE_URI = \
    '{engine}://{username}:{password}@{host}:{port}/{database}'.format(
        engine='mysql',
        username='krayni',
        password='tunisie20',
        host='localhost',
        port=3306,
database='data_base_krayni')

print(SQLALCHEMY_DATABASE_URI)
# apllication configuration 

mail = Mail()
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 
app.config['SAVE_FOLDER'] = SAVE_FOLDER 
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.secret_key = os.urandom(50)

#mail
app.config['MAIL_SERVER'] = 'smtp.mail.yahoo.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'my_name@yahoo.fr',
app.config['MAIL_PASSWORD'] = 'my_password'
mail.init_app(app)

###################################################################################
                    #database
###################################################################################
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class Flower_an(db.Model):
    #drop table if exists flower_krayni;
    id = db.Column('user_id',db.Integer , primary_key=True)
    username = db.Column('username', db.String(20), index=True)    
    email = db.Column('email',db.String(50) , index=True)
    body = db.Column('body',db.String(2000),index=True)
    pub_date = db.Column(db.DateTime,default=datetime.utcnow)
    #comments = db.relationship('Comment', backref='title', lazy='dynamic')
    def __init__(self, username, email, body, pub_date=None):
        self.username = username
        self.email = email
        self.body=body
        if pub_date is None:
            pub_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        self.pub_date = pub_date
    '''
    def get_comments(self):
        return Comment.query.filter_by(post_id=flower_anis.user_id).order_by(Comment.timestamp.desc())
     '''
    def __repr__(self):
        return '<User %r>' % self.username

'''
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    post_id = db.Column(db.Integer, db.ForeignKey('flower_anis.user_id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)

'''
###################################################################################
                    #permission administartor
###################################################################################

@app.before_request
def load_users():
    if current_user.is_authenticated:
        g.user = current_user.get_id() # return username in get_id()
    else:
        g.user = None # or 'some fake value', whatever

@app.after_request
def add_header(response):
    response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0') 
    return response


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

#########################################################################################
                              #views functions
#########################################################################################
##Login
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':
        if request.form['uname'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['psw'] != app.config['PASSWORD']:
            error = 'Invalid password'
            
        else:
            session['logged_in'] = True
            print('heh',current_user.is_authenticated)
            #flash('You were logged in')
            return redirect(url_for('upload_file'))
            print(request.form['uname'])
    
        print('heh')
    
    return render_template('test.html', error=error)
#logout 
@app.route('/logout')
def logout():
    session.clear()
    session.pop('logged_in', None)
    flash('You were logged out')

    return redirect(url_for('login'))


#upload image
@app.route('/find', methods=['GET', 'POST'])
def upload_file():
 if not session.get('logged_in'):
    return redirect(url_for('login'))
 else:
    if (request.method == 'POST'):
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #functions
            get_product(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return render_template('load_file.html')


#display image and segmentation result 
@app.route('/show/<filename>')
def uploaded_file(filename): 
   if not session.get('logged_in'):
      return redirect(url_for('login'))
   else:   
       return render_template('show.html', filename=filename)



@app.route('/input/<filename>')
def send_image(filename):
 if not session.get('logged_in'):
      return redirect(url_for('login'))
 else:      
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/segmentation/<filename>')
def send_result(filename):
  if not session.get('logged_in'):
      return redirect(url_for('login'))
  else:  
     return send_from_directory(SAVE_FOLDER, filename)




#########################################################################################
                                        #Download Result
#########################################################################################

#csv
@app.route("/file")
def Download_result():
   if not session.get('logged_in'):
       return redirect(url_for('login'))   
   else:
       return render_template('share_file.html')

@app.route("/getPlotCSV")
def getPlotCSV():
    # with open("outputs/Adjacency.csv") as fp:
    #     csv = fp.read()
    csv = '1,2,3\n4,5,6\n'
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=myplot.csv"})


#PD file 

@app.route('/file-downloads/')
def file_downloads():
   if not session.get('logged_in'):
       return redirect(url_for('login'))   
   else:
	try:
		return render_template('downloads.html')
	except Exception as e:
		return str(e)


@app.route('/return-files/')
def return_files_tut():
   if not session.get('logged_in'):
       return redirect(url_for('login'))   
   else:
	try:
		return send_file('/home/krayni/Bureau/Project_Flask/MY_NEW_API/application/IEEE_paper.pdf', attachment_filename='IEEE_paper.pdf')
	except Exception as e:
		return str(e)

@app.route('/return-CV/')
def return_CV():
	try:
		return send_file('/home/krayni/Bureau/Project_Flask/MY_NEW_API/application/English_CV_KRAYNI_Anis_DATA_PIXIT.pdf', attachment_filename='English_CV_KRAYNI_Anis_DATA_PIXIT.pdf')
	except Exception as e:
		return str(e)

##########################################################################################
                                        #Commentata base
##########################################################################################

@app.route('/index')
def index():
  return render_template('index.html')

#save the data base 
@app.route('/submit_message', methods=['POST'])
def submit_message():  
  user_fl = Flower_an(request.form['who'] ,request.form['adressmail'],request.form['message'])
  db.session.add(user_fl)
  db.session.commit()
  return "Sent"


@app.route('/Read_messages')
def sohw_db():
    #communicate with the data base
    engine=create_engine(SQLALCHEMY_DATABASE_URI)
    cursor = engine.connect()
    #slect data 
    result=cursor.execute("SELECT * from flower_an")
    summary = result.fetchall()
    data = map(list, summary)
    print(data)
    
    my_data=[]
    for row in result:
       print(row['username'])
       my_data.append({row['username']:row['body']})
    cursor.close()
    return render_template('commentsFollwer.html', summary=data)
 
   
##########################################################################################
                                # Run application
#########################################################################################

if __name__ == '__main__':
   db.create_all()   
   app.run(threaded=True)
   

