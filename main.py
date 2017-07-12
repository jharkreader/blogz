from flask import Flask, request, redirect, render_template, session, flash
from datetime import datetime
from hashutils import make_pw_hash, check_pw_hash
from app import app, db
from models import User, BlogPost

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
            return redirect('/newpost')
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