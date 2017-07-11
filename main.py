from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from hashutils import make_pw_hash, check_pw_hash


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:insecure@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'SUPER_SECRET_SQUIRREL_KEY'


class BlogPost(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    blog_text = db.Column(db.String(1024))
    blog_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blog_title, blog_text, owner, blog_date=None):
        self.blog_title = blog_title
        self.blog_text = blog_text
        self.owner = owner
        if blog_date is None:
            blog_date = datetime.utcnow()
        self.blog_date = blog_date

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('BlogPost', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)


@app.before_request
def require_login():

    allowed_routes = ['login', 'signup']

    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')



@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['email'] = email
            flash("Logged in")
            return redirect('/')
        else:
            flash("User password incorrect, or user does not exist.", 'error')   

    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        pw_error = ''
        verify_pw_error = ''
        username_error = ''

        if len(password) < 3:
            pw_error = "Password must be greater than 3 characters."
        elif password != verify:
            verify_pw_error = "Passwords must match."
            pw_error = "Passwords must match."
        else:
            pass        

        if not pw_error and not verify_pw_error and not username_error:
            pass
        else:
            return "<h1>Error!</h1>"             

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')

        else:
            return "<h1>Duplicate user</h1>"


    return render_template('signup.html', 
        username_error=username_error, 
        pw_error=pw_error, 
        verify_pw_error=verify_pw_error, 
        username=username)


@app.route('/logout')
def logout():

    del session['email']
    return redirect('/')


@app.route('/blog', methods=['GET', 'POST'])
def index():
    blogs = BlogPost.query.all()

    if 'id' in request.args:
        blog_id = request.args['id']
        blog_post = BlogPost.query.get(blog_id)
        return render_template('post.html', blog=blog_post)

    return render_template('blog.html', blogs=blogs)


@app.route('/newpost', methods=['GET', 'POST'])
def add_blog():
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_text = request.form['blog_text']

        title_error = ''
        text_error = ''

        if blog_title == "":
            title_error = "Please enter a title."
        if blog_text == "":
            text_error = "Please enter blog text."    
        
        if not title_error and not text_error:
            owner = User.query.filter_by(email=session['email']).first()
            new_blog = BlogPost(blog_title, blog_text, owner)
            db.session.add(new_blog)
            db.session.commit()
            id_param = new_blog.id

            return redirect('/blog?id={0}'.format(id_param))

        else:
            return render_template('newpost.html', 
            title_error=title_error,
            text_error=text_error, 
            blog_text=blog_text, 
            blog_title=blog_title)    

    else:
        return render_template('newpost.html')


if __name__ == '__main__':
    app.run()  