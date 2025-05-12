from . import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

class StudyPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    start_time = db.Column(db.String(10))
    end_time = db.Column(db.String(10))
    subjects = db.relationship('Subject', backref='plan', cascade="all, delete-orphan")

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    exam_date = db.Column(db.String(10))
    plan_id = db.Column(db.Integer, db.ForeignKey('study_plan.id'))
    topics = db.relationship('Topic', backref='subject', cascade="all, delete-orphan")

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    difficulty = db.Column(db.String(20))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
