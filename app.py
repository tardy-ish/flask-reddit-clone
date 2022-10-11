from datetime import datetime
from flask import Flask, flash, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from config import DevelopmentConfig

from helper_functions import db_table, salt_password, uname_check

app = Flask(__name__)

app.config.from_object(DevelopmentConfig)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100),nullable=False, unique=True)
    email = db.Column(db.String(120),nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self,username,email,password) -> None:
        self.username = username
        self.email = email
        self.password = password


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods =['GET', 'POST'])
def signup():
    form_data = {
        'username':"",
        'email':"",
        'password':"",
        'conf_pass':""
    }
    if request.method == 'POST':
        #we add shit to our database now
        _username = request.form['username'].strip()
        _email = request.form['email'].strip()
        _password = request.form['password'].strip() #salt the password and hash it
        conf_pass = request.form['conf_pass'].strip()
        
        form_data = {
            'username':_username,
            'email':_email,
            'password':_password,
            'conf_pass':conf_pass
        }

        if not (len(_username) and len(_email) and len(_password) and len(conf_pass)):
            flash("Fields can't be empty","warning")
            return render_template('auth/reg.html', form_data = form_data)

        _user_db = db_table(User)

        if _password != conf_pass:
            flash("Passwords don't match!","warning")
            form_data = {
                'username':_username,
                'email':_email,
                'password':"",
                'conf_pass':""
            }
            return render_template('auth/reg.html', form_data = form_data)

        if _user_db({'email':_email}).count():
            flash("Email is already registered","warning")
            form_data = {
                'username':_username,
                'email':"",
                'password':"",
                'conf_pass':""
            }
            return render_template('auth/reg.html', form_data = form_data)
        
        if uname_check(_username):
            flash("Not a legal username, pick a different one","warning")
            form_data = {
                'username':_username,
                'email':_email,
                'password':"",
                'conf_pass':""
            }
            return render_template('auth/reg.html', form_data = form_data)

        if _user_db({'username':_username}).count():
            flash("Username is already taken","warning")
            form_data = {
                'username':_username,
                'email':_email,
                'password':"",
                'conf_pass':""
            }
            return render_template('auth/reg.html', form_data = form_data)

        salted_pass = salt_password(_password)
        hashed_pass = bcrypt.generate_password_hash(salted_pass).decode("utf-8")

        try:
            new_user = User(
                username = _username,
                email = _email,
                password = hashed_pass
            )
            db.session.add(new_user)
            db.session.commit()
            print("Data Added successfully")
        except Exception as e:
            print("There was an error creating your account")
            print(e)
        return redirect("/")


    return render_template('auth/reg.html', form_data = form_data)

@app.route('/login',methods = ['GET','POST'])
def login():
    form_data = {
        'username':"",
        'password':""
    }
    if request.method == 'POST':
        #we add shit to our database now
        _username = request.form['username'].strip()
        _password = request.form['password'].strip() #salt the password and check password hash
        
        _user_db = db_table(User)
        _user = _user_db({'username':_username}).first()
        if not _user:
            flash("This username is not registered with us","warning")
            form_data = {
                'username':"",
                'password':""
            }
            return render_template('auth/signin.html', form_data = form_data)

        salted_pass = salt_password(_password)    

        if not bcrypt.check_password_hash(_user.password,salted_pass):
            flash("Username or Password wrong","warning")
            form_data = {
                'username':_username,
                'password':""
            }
            return render_template('auth/signin.html', form_data = form_data)
        
        print("Logged in successfully")

    return render_template('auth/signin.html', form_data = form_data)

if __name__ == '__main__':
    app.run()