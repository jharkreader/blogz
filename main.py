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

    def __repr__(self):
        return self.username    


@app.before_request
def require_login():

    allowed_routes = ['login', 'signup', 'list_blogs', 'index']

    if request.endpoint not in allowed_routes and 'username' not in session and '/static/' not in request.path:
        return redirect('/login')



@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            flash("Logged in")
            return redirect('/blog')
        elif user and not check_pw_hash(password, user.pw_hash):
            flash("User password incorrect.", 'error')
        else:
            flash("User does not exist.", 'error')       

    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()

        if len(username) < 3:            
            flash("Username must be greater than 3 characters")
        elif existing_user:
            flash("Username is already in use.")
        elif len(password) < 3:
            flash("Password must be greater than 3 characters.")
        elif password != verify:
            flash("Passwords must match.")
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

    return render_template('signup.html')


@app.route('/logout')
def logout():

    del session['username']
    return redirect('/blog')


@app.route('/blog', methods=['GET', 'POST'])
def list_blogs():
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
            owner = User.query.filter_by(username=session['username']).first()
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

@app.route('/', methods=['GET'])
def index():

    users = User.query.all()

    if 'user' in request.args:
        username = request.args['user']
        owner = User.query.filter_by(username=username).first()
        user_blogs = BlogPost.query.filter_by(owner=owner).all()

        return render_template('singleuser.html', user_blogs=user_blogs)

    return render_template('index.html', users=users)

if __name__ == '__main__':
    app.run()  