from flask import Flask, render_template, request,session
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

with open('config.json','r') as c:
    params = json.load(c)["params"]
    

local_server = True
app = Flask(__name__)
app.secret_key = 'super-secret-key'

app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-password']
)
mail = Mail(app)

if (local_server):
 app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
 app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(30), nullable=True)
    tagline = db.Column(db.String(100), nullable=True)


@app.route("/")
def home():
    posts = Posts.query.filter_by().all()[0:params['no_of_posts_on_home']]
   
    return render_template('index.html', params=params, posts=posts)


@app.route("/dashboard", methods=['GET','POST'])
def login():
    
    if 'user' in session and session['user'] == params['admin_user'] :
        return render_template('dashboard.html', params=params)
        

    if request.method=='POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if(username==params["admin_user"] and userpass == params["admin_password"]):
            #set the session variable
            session['user'] = username
            return render_template('dashboard.html', params=params)
    
    else:
        return render_template('login.html',params=params)

@app.route("/post/<string:post_slug>", methods=['GET']) 
def post_route(post_slug):
     post = Posts.query.filter_by(slug=post_slug).first()
     return render_template('post.html', params=params, post=post)

@app.route("/about")
def about():
    return render_template('about.html',params=params)


@app.route("/contact", methods = ['GET', 'POST'],)
def contact():
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, phone_num = phone, msg = message, date= datetime.now(),email = email )
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from Blog', sender=email, 
                                                   recipients= [params["gmail-user"]],
                                                   body=message + "\n" + phone)
    else:
     return render_template('contact.html',params=params)


app.run(debug=True)
