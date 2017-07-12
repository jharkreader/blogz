from hashutils import make_pw_hash
from app import db
from datetime import datetime


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
