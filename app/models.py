from . import db
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String(150), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(db.String(150), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String(256), nullable=False)
    study_plans: Mapped[list["StudyPlan"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class StudyPlan(db.Model):
    __tablename__ = 'study_plans'
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('users.id'))
    start_time: Mapped[str] = mapped_column(db.String(10))
    end_time: Mapped[str] = mapped_column(db.String(10))
    
    user: Mapped["User"] = relationship(back_populates="study_plans")
    subjects: Mapped[list["Subject"]] = relationship(back_populates="plan", cascade="all, delete-orphan")
    tasks: Mapped[list["StudyTask"]] = relationship(back_populates="plan", cascade="all, delete-orphan")


class Subject(db.Model):
    __tablename__ = 'subjects'
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(120))
    exam_date: Mapped[date] = mapped_column(db.Date)
    plan_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('study_plans.id'))
    
    plan: Mapped["StudyPlan"] = relationship(back_populates="subjects")
    topics: Mapped[list["Topic"]] = relationship(back_populates="subject", cascade="all, delete-orphan")

class Topic(db.Model):
    __tablename__ = 'topics'
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(120))
    difficulty: Mapped[str] = mapped_column(db.String(20))
    subject_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('subjects.id'))
    
    subject: Mapped["Subject"] = relationship(back_populates="topics")

class StudyTask(db.Model):
    __tablename__ = 'study_tasks'

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    plan_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('study_plans.id'))
    title: Mapped[str] = mapped_column(db.String(120))
    description: Mapped[str] = mapped_column(db.String(300))
    is_done: Mapped[bool] = mapped_column(db.Boolean, default=False)
    duration_minutes: Mapped[int] = mapped_column(db.Integer)  # e.g., 120 = 2 hours
    scheduled_date: Mapped[date] = mapped_column(db.Date)  # <-- NEW FIELD

    plan: Mapped["StudyPlan"] = relationship(back_populates="tasks")