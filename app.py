from datetime import datetime
from flask import Flask, flash, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from config import DevelopmentConfig

from helper_functions import exist_in_db, salt_password, uname_check

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
        'email':""
    }
    if request.method == 'POST':
        #we add shit to our database now
        _username = request.form['username'].strip()
        _email = request.form['email'].strip()
        _password = request.form['password'].strip() #salt the password and hash it
        conf_pass = request.form['conf_pass'].strip()
        
        if _password != conf_pass:
            flash("Passwords don't match!","warning")
            form_data['username'] = _username
            form_data['email'] = _email
            return render_template('auth/reg.html', form_data = form_data)
        
        if exist_in_db(User,'email',_email):
            flash("Email is already registered","warning")
            form_data['username'] = _username
            form_data['email'] = ""
            return render_template('auth/reg.html', form_data = form_data)
        
        if uname_check(_username):
            flash("Not a legal username, pick a different one","warning")
            form_data['username'] = ""
            form_data['email'] = _email
            return render_template('auth/reg.html', form_data = form_data)

        if exist_in_db(User,'username',_username):
            flash("Username is already taken","warning")
            form_data['username'] = ""
            form_data['email'] = _email
            return render_template('auth/reg.html', form_data = form_data)

        salted_pass = salt_password(_password)
        hashed_pass = bcrypt.generate_password_hash(salted_pass)

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
    return render_template('auth/signin.html')

if __name__ == '__main__':
    app.run()