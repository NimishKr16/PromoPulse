from flask import Flask, render_template, request, redirect, url_for, session
import hashlib
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = 'promopulse-123-$%^-mad2-proj*'  # Change this to a strong secret key

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///promopulse.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ! ---------------- MODELS ----------------#

# * --- Admin Table --- #
class Admin(db.Model):
    __tablename__ = 'admin'
    AdminID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(50), nullable=False)
    Password = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"<{self.Username} | {self.Password} | {self.Email}>"


# ! ---------------- ROUTES ----------------#
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True,port=5500)
