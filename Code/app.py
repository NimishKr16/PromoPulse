from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps

app = Flask(__name__)

app.secret_key = 'promopulse-123-$%^-mad2-proj*'  # Change this to a strong secret key

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///promopulse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ! ---------------- MODELS ---------------- #

# * --- Admin Table --- #
class Admin(db.Model):
    __tablename__ = 'admin'
    
    AdminID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(50), nullable=False)
    Password = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"<{self.Username} | {self.Password} | {self.Email}>"


# * --- User Table --- #
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Password = db.Column(db.String(256), nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)
    Role = db.Column(db.String(20), nullable=False)
    
    # Relationships
    sponsor = db.relationship('Sponsor', uselist=False, backref='user')
    influencer = db.relationship('Influencer', uselist=False, backref='user')
    
    
# * --- Sponsor Table --- #
class Sponsor(db.Model):
    __tablename__ = 'sponsors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(50), nullable=False)
    budget = db.Column(db.Float, nullable=False)
    
# * --- Influencer Table --- #
class Influencer(db.Model):
    __tablename__ = 'influencers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    profile_name = db.Column(db.String(100), nullable=False)
    niche = db.Column(db.String(50), nullable=False)
    reach = db.Column(db.Float, nullable=False)


# ------------ WRAPPER FUNCTIONS -------------
def role_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or 'id' not in session or 'role' not in session:
            return redirect(url_for('login', message='Please Login First'))
        return f(*args, **kwargs)
    return decorated_function


# ! ---------------- ROUTES ---------------- #
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    message = request.args.get('message')
    return render_template('login.html',message=message)

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/temp')
def temp():
    return render_template('tempform.html')


@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')
        session.pop('id')
        session.pop('role')
    
        print("=== LOGGED OUT ===")
    return redirect(url_for('login',message='LOG OUT Successful!'))

# * ---------------- AUTHENTICATION ---------------- #

# REGISTER
@app.route('/registerUser', methods=['POST'])
def registerUser():
    if request.method == 'POST':
        name = request.form.get('name')
        role = request.form.get('role')
        pwd = request.form.get('pwd')
        email = request.form.get('email')
        industry = request.form.get('industry')
        
        existing_user = User.query.filter_by(Email=email).first()
        if existing_user:
            return render_template('signup.html',msg=True)

        hashed_password = generate_password_hash(pwd, method='pbkdf2:sha256', salt_length=16)
        new_user = User(Name=name, Password=hashed_password, Email=email, Role=role)
        db.session.add(new_user)
        db.session.commit()
        print("==== NEW USER COMMIT ==== ")
        
        if role == 'sponsor':
            company_name = name
            new_sponsor = Sponsor(user_id=new_user.id, 
                                  company_name=company_name,
                                  industry=industry,
                                  budget = 0)
            db.session.add(new_sponsor)
            db.session.commit()
            print("==== NEW SPONSOR COMMIT ==== ")
        
        if role == 'influencer':
            company_name = name
            new_influencer = Influencer(user_id=new_user.id, 
                                  profile_name=company_name,
                                  niche=industry,
                                  reach = 0)
            db.session.add(new_influencer)
            db.session.commit()
            print("==== NEW INFLUENCER COMMIT ==== ")

    return redirect(url_for('login'))

# LOGIN
@app.route('/userLogin', methods = ['POST'])
def userLogin():
    print(request.method)
    if request.method == 'POST':
        email = request.form.get('email')
        pwd = request.form.get('pwd')
        print(email,pwd)
        user = User.query.filter_by(Email=email.lower()).first()
        if user:
            is_password_correct = check_password_hash(user.Password, pwd)
            if is_password_correct:
                role = user.Role
                id = user.id
                name = (user.Name)
                # print(name)
                session['user'] = name
                session['id'] = id
                session['role'] = role
                print(f' ===== {role} log in =====')
                return redirect(url_for(role,id=id,name=name))

            else:
                return render_template('login.html', message='Incorrect password entered!')
        else:
            return render_template('login.html',message='Account with this email doesn\'t exist!')
        
    return render_template('login.html')
    

# * ------------ USER VIEW ROUTES ------------ #

@app.route('/sponsor/<int:id>/<string:name>')
@role_login_required
def sponsor(id,name):
    return render_template('sponsor.html',id=id,name=name)


@app.route('/influencer/<int:id>/<string:name>')
@role_login_required
def influencer(id,name):
    return render_template('influencer.html',id=id,name=name)




# * ------------ ADMIN ROUTES ------------ #

@app.route('/admin')
def admin_login_page():
    return render_template('admin-login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        print(email,password)
        admin = Admin.query.filter_by(Email=email).first()
        if admin and password == admin.Password:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return "<h1>Invalid uname or pwd</h1>"


def isAdminLogin():
    return 'admin' in session and session['admin'] == True


@app.route('/admin/dashboard')
def admin_dashboard():
    if(isAdminLogin()):
        return render_template('admin-dash.html')
    else:
        return "<h1>Must be logged in as Admin</h1>"


# ''' RUN APP.PY '''

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True,port=5500)


# sample sponsor : email: dotnkey@gmail.com ; pwd : nimish0305

