from typing import List
from . import db
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref 
from datetime import date, datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String(150), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(db.String(150), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String(256), nullable=False)
    
    # Relationships
    study_plans: Mapped[List["StudyPlan"]] = relationship(
        "StudyPlan", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    personal_tasks: Mapped[List["PersonalTask"]] = relationship(
        "PersonalTask", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )


class StudyPlan(db.Model):
    __tablename__ = 'study_plans'
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('users.id'))
    name: Mapped[str] = mapped_column(db.String(100), nullable=False, default="My Study Plan")
    start_time: Mapped[str] = mapped_column(db.String(10))
    end_time: Mapped[str] = mapped_column(db.String(10))
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
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
    duration_minutes: Mapped[int] = mapped_column(db.Integer)
    scheduled_date: Mapped[date] = mapped_column(db.Date)
    priority: Mapped[int] = mapped_column(db.Integer, default=2)  # 1=High, 2=Medium, 3=Low
    is_ai_generated: Mapped[bool] = mapped_column(db.Boolean, default=True)
    
    plan: Mapped["StudyPlan"] = relationship(back_populates="tasks")

class PersonalTask(db.Model):
    __tablename__ = 'personal_tasks'
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('users.id'))
    title: Mapped[str] = mapped_column(db.String(120))
    description: Mapped[str] = mapped_column(db.String(300))
    is_done: Mapped[bool] = mapped_column(db.Boolean, default=False)
    due_date: Mapped[date] = mapped_column(db.Date)
    priority: Mapped[int] = mapped_column(db.Integer, default=2)  # 1=High, 2=Medium, 3=Low
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    user: Mapped["User"] = relationship("User", back_populates="personal_tasks")