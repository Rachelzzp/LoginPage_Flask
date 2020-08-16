from functools import wraps
from flask import Flask,request,render_template,redirect,url_for,flash,session

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_,or_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = '\xc9ixnRb\xe40\xd4\xa5\x7f\x03\xd0y6\x01\x1f\x96\xeao+\x8a\x9f\xe4'
db = SQLAlchemy(app)


############################################
# Database
############################################

# ORM
class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(80),unique=True)
    password = db.Column(db.String(80))
    email = db.Column(db.String(120),unique=True)

    def __repr__(self):
        return '<User %r>' % self.username


# create table and insert data into database
@app.before_first_request
def create_db():
    db.drop_all()  # delete the former and create a new table each time
    db.create_all()

    admin = User(username='admin',password='root',email='admin@example.com')
    db.session.add(admin)

    guestes = [User(username='guest1',password='guest1',email='guest1@example.com'),
               User(username='guest2',password='guest2',email='guest2@example.com'),
               User(username='guest3',password='guest3',email='guest3@example.com'),
               User(username='guest4',password='guest4',email='guest4@example.com')]
    db.session.add_all(guestes)
    db.session.commit()


############################################
# Decor
############################################

# Validation for login（validate username and password）
def valid_login(username,password):
    user = User.query.filter(and_(User.username == username,User.password == password)).first()
    if user:
        return True
    else:
        return False


# Validation for registration（validate username and email）
def valid_regist(username,email):
    user = User.query.filter(or_(User.username == username,User.email == email)).first()
    if user:
        return False
    else:
        return True


# Login
def login_required(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        # if g.user:
        if session.get('username'):
            return func(*args,**kwargs)
        else:
            return redirect(url_for('login',next=request.url))

    return wrapper


############################################
# Router
############################################

# 1.homepage
@app.route('/home')
def home():
    return render_template('home.html',username=session.get('username'))


# 2.login
@app.route('/login',methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'],request.form['password']):
            flash("Login successfully！")
            session['username'] = request.form.get('username')
            return redirect(url_for('home'))
        else:
            error = 'Wrong username or password！'

    return render_template('login.html',error=error)

# 3.logout
@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect(url_for('home'))


# 4.registration
@app.route('/regist',methods=['GET','POST'])
def regist():
    error = None
    if request.method == 'POST':
        if request.form['password1'] != request.form['password2']:
            error = 'Password unmatched！'
        elif valid_regist(request.form['username'],request.form['email']):
            user = User(username=request.form['username'],password=request.form['password1'],
                        email=request.form['email'])
            db.session.add(user)
            db.session.commit()

            flash("Register successfully！")
            return redirect(url_for('login'))
        else:
            error = 'This username or password has been registered！'

    return render_template('regist.html',error=error)


# 5.person profile
@app.route('/panel')
@login_required
def panel():
    username = session.get('username')
    user = User.query.filter(User.username == username).first()
    return render_template("panel.html",user=user)

# 6. subscribe
@app.route('/subscribe',methods=['GET','POST'])
def subscribe():
    error = None
    if request.method == 'POST':
        if valid_regist(request.form['username'],request.form['email']):
            flash("Subscribe successfully！")
            return redirect(url_for('home'))
        else:
            error = 'Wrong username or email！'

    return render_template('subscribe.html', error=error)


if __name__ == '__main__':
    app.run(debug=True)
