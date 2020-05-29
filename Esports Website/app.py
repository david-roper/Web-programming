#Assignment 2+3 flask file, contains all the routes for the html files + password database set up
#by David Roper 40131739

import sqlite3
import csv
from flask import Flask, url_for, render_template,flash,redirect
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
app = Flask(__name__, static_url_path='/static')


app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY']='key'

#setting up database and login manager
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#classes for forms and users
class User1(UserMixin):
    def __init__(self, username):
        self.id = username

class User(db.Model):
    id = db.Column(db.INTEGER,primary_key =True)
    username = db.Column(db.String(40),unique=True, nullable = False) #for user name
    email = db.Column(db.String(80), unique=True, nullable=False) #for email
    password = db.Column(db.String(40),nullable =False)

    def __repr__(self):
        return f"User('self.username','self.email')"




class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=5, max=25)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=5, max=25)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class WinnerForm(FlaskForm):
    gamename = StringField('Game Name:',validators=[DataRequired()])
    teamname = StringField('Team Name:',validators=[DataRequired()])
    submit = SubmitField('Add')

#app routes
@app.route('/')
def index():
    return render_template("base 2.html")

@app.route('/Team')
def Team():
   return render_template("Team.html")

@app.route('/Tournament')
def Tournament():
    return render_template("Tournament.html")

@app.route('/Contact')
def Contact():
    return render_template("Contact.html")

@app.route('/Disc')
def Disc():
    return render_template("Disc.html")

@app.route('/ex2')
def ex():
    data = ['a','b','c','d']
    return render_template("ex2.html",d=data)


#app route for dynamic tables of winners
@app.route('/table')
def table():
    columns = ['Game', 'Player/Team']
    df = pd.read_csv('data/tabledata.csv', names=columns)
    winners_table = df;
    str = """{% extends "Base.html" %}{% block navbar %}
      <nav class="navbar navbar-default">
      <div style="background-color: maroon" class="container-fluid">
        <ul class="nav navbar-nav">
          <li class="active"><a href="/">Back to Home Page</a></li>
          <li><a href="{{ url_for('Team') }}">Join a Team</a></li>
          <li><a href="/Tournament">Tournament sign up</a></li>
          <li><a href="/Contact">Contact</a></li>
          <li><a href="/Disc">Discussion</a></li>
        <li><a href="/login">Login</a></li>
        <li><a href="/register">Register</a></li>

        </ul>
      </div>
    </nav>
    {% endblock %}
    <head><style>
           table{
               align: center;
           } </style></head><body> {% block content %}""" + winners_table.to_html(index = False) + """</body> {% endblock %}"""
    with open('templates/winners_table.html', 'w') as html_file:
        html_file.write(str)
    return render_template("winners_table.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        new_user = User(username=form.username.data,email=form.email.data,password=form.password.data)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('index'))
    else:
        flash("input error!")
        return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
            user = User.query.filter_by(username = form.username.data).first()
            if user:
                if user.password == form.password.data:
                    login_user(User1(form.username.data))
                    return redirect(url_for('index'))
            else:
                return "<h1><a href=""/login"">Invalid username/password click here to try again</a></h1>"

    else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@login_manager.user_loader
def load_user(user_id):
    return User1(user_id)

#show when user is logged in
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

#protected html page
@app.route('/protected')
@login_required
def protected():
    return render_template('protected.html')

@app.route("/addwinner",methods=['GET', 'POST'])
def addwinner():
    form = WinnerForm()
    if form.validate_on_submit():

        with open('data/tabledata.csv','a') as f:
            writer = csv.writer(f)
            writer.writerow([form.gamename.data,form.teamname.data])
    flash("A winner has been added!")
    return render_template('addwinner.html',form=form)


@app.route("/coords")
def writelist():
    #writes dynamic list of coordinators to the html page
    str1="""{% extends "Base.html" %}{% block navbar %}
      <nav class="navbar navbar-default">
      <div style="background-color: maroon" class="container-fluid">
        <ul class="nav navbar-nav">
          <li><a href="/">Home Page</a></li>
          <li><a href="{{ url_for('Team') }}">Join a Team</a></li>
          <li><a href="/Tournament">Tournament sign up</a></li>
          <li class="active"><a href="/Contact">Back to contact page</a></li>
        {% if current_user.is_authenticated %}
                <li><a href="/logout">Logout</a></li>
        {% else %}
                <li class><a href="/login">Login</a></li>
        {% endif %}
        <li><a href="/register">Register</a></li>

        </ul>
      </div>
    </nav>
    {% endblock %}
    <head></head><body> {% block content %}<h2>List of Coordinators</h2><ul>"""
    with open('data/club_coords') as f:
        for line in f:
            str1 = str1+"<li><a href =""mailto:abc@gmail.com"">"+line+ "</a></li>"
    str1 = str1 + "</ul>{% endblock %}"
    with open('templates/coords.html','w') as h:
        h.write(str1)

    return render_template('coords.html')






if __name__ == '__main__':
    app.run()
