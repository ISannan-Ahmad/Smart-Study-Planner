from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from datetime import datetime
import json
from .models import db, StudyPlan, Subject, Topic, StudyTask
from collections import defaultdict
import re
from app.ai import generate_study_tasks


main = Blueprint('main', __name__)


@main.route('/')
def home():
    return render_template('home.html')


@main.route('/about')
def about():
    return render_template('about.html')


@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


def parse_duration_to_minutes(duration_str):
    # Converts strings like "2 hours", "1.5 hours" into minutes
    match = re.match(r"(\d+(\.\d+)?)\s*hours?", duration_str.lower())
    if match:
        hours = float(match.group(1))
        return int(hours * 60)
    return 0


@main.route('/plan', methods=['GET', 'POST'])
@login_required
def plan():
    if request.method == 'POST':
        start_time = request.form.get('daily_start_time')
        end_time = request.form.get('daily_end_time')

        subjects = defaultdict(lambda: {"topics": {}})

        for key in request.form:
            subject_match = re.match(r'subjects\[(\d+)\]\[(name|exam_date)\]', key)
            if subject_match:
                subj_idx, field = subject_match.groups()
                subjects[subj_idx][field] = request.form[key]
                continue

            topic_match = re.match(r'subjects\[(\d+)\]\[topics\]\[(\d+)\]\[(name|difficulty)\]', key)
            if topic_match:
                subj_idx, topic_idx, field = topic_match.groups()
                if 'topics' not in subjects[subj_idx]:
                    subjects[subj_idx]['topics'] = {}
                if topic_idx not in subjects[subj_idx]['topics']:
                    subjects[subj_idx]['topics'][topic_idx] = {}
                subjects[subj_idx]['topics'][topic_idx][field] = request.form[key]

        study_plan = StudyPlan(
            user_id=current_user.id,
            start_time=start_time,
            end_time=end_time
        )
        db.session.add(study_plan)

        for subject_data in subjects.values():
            subject = Subject(
                name=subject_data['name'],
                exam_date=datetime.strptime(subject_data['exam_date'], '%Y-%m-%d').date(),
                plan=study_plan
            )
            db.session.add(subject)

            for topic_data in subject_data['topics'].values():
                topic = Topic(
                    name=topic_data['name'],
                    difficulty=topic_data['difficulty'],
                    subject=subject
                )
                db.session.add(topic)

        db.session.commit()

        db.session.refresh(study_plan)
        tasks_data = generate_study_tasks(subjects=study_plan.subjects, start_time=study_plan.start_time, end_time=study_plan.end_time)

                
        for day, tasks in tasks_data.items():
            for task_data in tasks:
                scheduled_date = datetime.strptime(task_data["scheduled_date"], "%Y-%m-%d").date()
                duration_minutes = parse_duration_to_minutes(task_data["duration"])

                task = StudyTask(
                    title=task_data["task"],
                    description=task_data["description"],
                    scheduled_date=scheduled_date,
                    duration_minutes=duration_minutes,
                    plan_id=study_plan.id
                )
                db.session.add(task)

        db.session.commit()

        return redirect(url_for('main.dashboard'))

    return render_template('planform.html')