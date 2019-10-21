from flask import Flask, render_template, request, session, flash, redirect, url_for
import os
import random

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker
from functools import wraps
from sqlalchemy import and_


app = Flask(__name__)
app.secret_key = os.urandom(24)

ENV = 'prod'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = ''
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:hamza@localhost/postgres'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

count = []
people = []

class carttable(db.Model):
    __tablename__ = 'carttable'
    id = db.Column(db.Integer, primary_key = True)
    quantity = db.Column(db.String(50))    
    infillQuantity = db.Column(db.String(50))
    color = db.Column(db.String(50))
    filename = db.Column(db.String(100))
    session = db.Column(db.String(50))

    def __init__(self, quantity, infillQuantity, color, filename, session):

        self.quantity = quantity
        self.infillQuantity = infillQuantity
        self.color = color
        self.filename = filename
        self.session = session

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    email = db.Column(db.String(100))

    def __init__(self, username, password, email):
        self.username = username 
        self.password =  password
        self.email = email

class Bill(db.Model):
    __tablename__ = 'bill'
    id = db.Column(db.Integer, primary_key= True)
    email = db.Column(db.String(50))
    product = db.Column(db.String(100))

    def __init__(self, email, product): 
        self.email = email
        self.product = product
    
class Finalamount(db.Model):
    __tablename__ = 'finalamount'
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(50))
    totalAmount = db.Column(db.String(50))

    def __init__(self, email, totalAmount):
        self.email = email
        self.totalAmount = totalAmount

class Checkout(db.Model):
    __tablename__ = 'checkout'
    id = db.Column(db.Integer, primary_key= True)
    username = db.Column(db.String(50))
    company = db.Column(db.String(50))
    address = db.Column(db.String(100))
    town = db.Column(db.String(50))
    zipcode = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(100))
    checkoutAmount = db.Column(db.String(100))


    def __init__(self, username, company, address, town, zipcode, phone, email, checkoutAmount):
        self.username = username
        self.company = company
        self.address = address
        self.town = town
        self.zipcode = zipcode
        self.phone = phone
        self.email = email
        self.checkoutAmount = checkoutAmount

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Login required to add item to cart')
            return redirect(url_for('login'))
    return wrap

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/productDetails")
def productDetails():
   return render_template("product-details.html")

@app.route("/cart")
def cart():
    if 'user_id' in session: 
        items =  carttable.query.filter_by(session = session["user_id"]).all()
    else: 
        items =  None
    return render_template("cart.html", items=items)

@app.route("/checkout")
def checkout():
   
    return render_template("checkout.html")




@app.route("/addtocart", methods=["POST", "GET"])
@login_required
def addtocart():

    quantity = request.form.get("quantity")
    infillQuantity  = request.form.get("infillQuantity")
    color = request.form['color1']
    target = os.path.join(APP_ROOT, 'static/')
    fileext = "none"
    for file in request.files.getlist("file"):
        print(file)
        filename =  str(len(count)) + "_" + (file.filename) 
        fileext = str(len(count)) + "_" + str(file.filename)
        count.append("1")
        destination='/'.join([target, filename])
        print(destination)
        file.save(destination)

    file = request.files['file']
    

    print(quantity, infillQuantity, color)
    print(session)
    data = carttable(quantity, infillQuantity, color, fileext, session["user_id"])
    db.session.add(data)
    db.session.commit()   
    flash("Added to cart")
    return redirect(url_for("cart"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        if not request.form.get("email"):
            return render_template("login.html", message="Please Enter email")
        elif not request.form.get("password"):
            return render_template("login.html", message="Please Enter Password")
        
        email =  request.form.get("email")
        password = request.form.get("password")
        User = Users.query.filter(and_(Users.email == request.form.get("email"), Users.password ==  request.form.get("password"))).first()

        if User is not None: 
            session['logged_in'] = True
            session["user_id"] = request.form.get("email")
            return redirect(url_for("index")) 
        else: 
            return render_template("login.html", message="Invalid email or password")
    else:
        return render_template("login.html")

@app.route("/register",  methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("register.html", message="Please Enter Username")
        elif not request.form.get("password"):
            return render_template("register.html", message="Please Enter Password")
        elif not request.form.get("email"):
            return render_template("register.html", message="Please enter email")   
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password") 

        user = Users.query.filter_by(email=email).first()
        if user is not None: 
            return render_template("register.html", message="User already exists")   
        
        new_user = Users(username, password, email)
        db.session.add(new_user)
        db.session.commit()
        flash("Email successfully registered")

        return redirect(url_for('login'))
    else: 
        return render_template("register.html")

@app.route("/addToCheckout", methods=['POST'])
def addToCheckout():
    amount = request.form.get("fname")
    items =  carttable.query.filter_by(session = session["user_id"]).all()
    for item in items: 
        temp = Bill.query.filter(and_(Bill.product == item.filename, Bill.email == session["user_id"] )).first()

        if temp is None: 
       
            data = Bill(session["user_id"], item.filename)
            db.session.add(data)
            db.session.commit()   
            data = Finalamount(session["user_id"], amount)
            db.session.add(data)
            db.session.commit()
            
        else: 
            return render_template("cart.html", message="Already finalised, complete finalised details") 
    return redirect(url_for('checkout'))
     

@app.route("/emptyCart", methods=['POST'])
def emptyCart():
    itemInCart = carttable.query.filter_by(session=session["user_id"]).first()
    if itemInCart is not None:      
        carttable.query.filter_by(session=session["user_id"]).delete()
        db.session.commit()
        return render_template("cart.html", message="Cart Emptied")
    else: 
        return render_template("cart.html", message="Cart already empty")