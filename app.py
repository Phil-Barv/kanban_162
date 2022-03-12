from flask import Flask, redirect, url_for, render_template, flash, request, abort
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from flask_bcrypt import Bcrypt
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, EmailField
from wtforms.validators import InputRequired, Length, Email 
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import logging
 
app = Flask(__name__)
app.secret_key = "VerySecretKey" #change before deployment
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_BINDS'] = {'tasks_db': 'sqlite:///tasks.sqlite3' }
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #removes modifications to database warnings

#Initialize the database
db = SQLAlchemy(app) 
db.init_app(app)

#Initialize Bycrypt
bcrypt = Bcrypt(app)

#set up login management
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
    
#create login decorator
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

#create forms
class SignUpForm(FlaskForm):
    user = StringField('user', 
                    validators=[InputRequired(), Length(min=4, max=20)], 
                    render_kw={'placeholder':'Username'})

    email = EmailField('email', 
                    validators=[InputRequired(), Length(min=10, max=100), 
                    Email(message="Invalid Email!",check_deliverability=True)], 
                    render_kw={'placeholder':'Email'})

    password = PasswordField('password', 
                    validators=[InputRequired(), Length(min=4,max=100)], 
                    render_kw={'placeholder':'Password'})

    submit = SubmitField('Sign Up')


    def validate_email(self, email):
        existing_user_email = Users.query.filter_by(email=email.data).first()
        if existing_user_email:
            flash("That email already exists! Try a different one.", "info")
            

class LoginForm(FlaskForm):
    email = EmailField('email', 
                        validators=[InputRequired(), Length(min=10, max=100), 
                        Email(message="Invalid Email!",check_deliverability=True)], 
                        render_kw={'placeholder':'Email'})

    password = PasswordField('password', 
                        validators=[InputRequired(), Length(min=4,max=100)], 
                        render_kw={'placeholder':'Password'})

    submit = SubmitField('Sign In')


class TaskForm(FlaskForm):
    types = SelectField(label='Task Type', 
                        choices=[('To Do','To Do'), ('Doing','Doing'), ('Done','Done')], 
                        render_kw={'placeholder':'Enter task label'})

    title = StringField(label='Task Label', 
                        validators=[InputRequired(), Length(min=4, max=20)], 
                        render_kw={'placeholder':'Enter task label'})

    description = TextAreaField(label='Description', 
                        validators=[InputRequired(), Length(min=4, max=100)], 
                        render_kw={'placeholder':'Enter your task description'})

    submit = SubmitField('Submit')


#create db model for tasks
class Tasks(db.Model):
    #details of each task as a column in the db
    id = db.Column(db.Integer, primary_key=True)
    types = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    #create relational to tasks
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


#Create db model for users
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    tasks_list = db.relationship('Tasks', backref='task_owner')


#define default views
view1 = {"title": "Username", "t_link": "home", "function": "Log Out", "f_link": "logout", "dialog":"Are you sure you want to log out?" }
view2 = {"title": "Sign Up", "t_link": "signup", "function": "Log In", "f_link": "login", "dialog":"Please enter your credentials below!" }
view3 = {"title": "Take me back", "t_link": "home", "function": "Home", "f_link": "home", "dialog":"You are going to be redirected!" }


#create routes
#error handlers
logger = logging.getLogger('errors')
logger.setLevel(logging.ERROR)
handler = logging.FileHandler('errors.log')
formatter = logging.Formatter('%(asctime)s: %(levelname)s:  %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

@app.errorhandler(404)
def not_found(e):
    #for deployment we might not want to log 404s, 500s are more important
    logger.error(f"Route: {request.url}, Error: {e}")
    error = {"error":"404", "description": "Page Not Found!"}
    return render_template('errors.html', view=view3, error=error)

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Route: {request.url}, Error: {e}")
    error = {"error":"500", "description": "Internal Server Error :("}
    return render_template('errors.html', view=view3, error=error)



#signup user
@app.route("/signup/", methods=["POST", "GET"])
def signup():

    form = SignUpForm()
    
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()

        if user is None:
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            new_user = Users(user=form.user.data,password=hashed_password,email=form.email.data)

            try:
                db.session.add(new_user)
                db.session.commit()
                flash("Your account has been added, Sign In!", "info")
                return redirect(url_for('login'))

            except:
                abort(500)

    return render_template("signup.html", form=form, view=view2)


#login user
@app.route("/login/", methods=["POST", "GET"])
@app.route("/", methods=["POST", "GET"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash(f"Oops, you put the wrong password, {form.email.data}. Try again.", "info") 
        else:
            flash(f"{form.email.data}, please create an account!", "info")
    
    return render_template("login.html", form=form, view=view2)


#home page 
@app.route("/home/", methods=["POST", "GET"])
@login_required
def home():

    #calculate today and yesterday for task timestamp formatting
    today = datetime.utcnow().date()
    yesterday = today - timedelta(hours=24)

    try:
        task_list = Tasks.query.filter_by(user_id=current_user.id).order_by(desc(Tasks.date_created))

    except:
        task_list = [] #no tasks displayed

    view1["title"] = str(current_user.user).capitalize()

    return render_template('home.html', 
                            task_list=task_list, 
                            today=today, 
                            yesterday=yesterday, 
                            view=view1)


#add a new task 
@app.route("/new/", methods=["POST", "GET"])
@login_required
def new():

    form = TaskForm()

    if form.validate_on_submit and request.method=="POST":

        task_list = Tasks(
                        types=form.types.data, title=form.title.data, 
                        description=form.description.data, 
                        task_owner=current_user)

        #push to database
        try:
            db.session.add(task_list)
            db.session.commit()
            return redirect(url_for('home'))

        except:
            #raise error
            abort(500)

    else:   
        return render_template("new.html", view=view1, form=form)


#update existing task 
@app.route("/update/<int:id>", methods=["POST", "GET"])
@login_required
def update(id):

    update = Tasks.query.get_or_404(current_user.id)

    if request.method == "POST":
        update.types = request.form["entry_type"]
        update.title = request.form["entry_title"]
        update.description = request.form["entry_description"]
        
        #push change to database
        try:
            db.session.commit()
            return redirect(url_for("home"))

        except:
            abort(500)
    
    else:   
        return render_template("update.html", update = Tasks.query.get_or_404(id), view=view1)


#delete existing task
@app.route("/delete/<int:id>", methods=["POST", "GET"])
def delete(id):

    delete = Tasks.query.get_or_404(int(id))
    #push change to database
    try:
        db.session.delete(delete)
        db.session.commit()
        return redirect(url_for('home'))

    except:
        abort(500)


#logout user
@app.route("/logout/", methods=["POST", "GET"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out!", "warning")
    return redirect(url_for('login'))


#run app 
if __name__ == "__main__":
    db.create_all()
    app.run(debug=True) #include debug=True argument to detect changes made