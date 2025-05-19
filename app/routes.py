from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import json
from pydantic import ValidationError
from .models import db, StudyPlan, Subject, Topic, StudyTask, PersonalTask
from collections import defaultdict
import re
from app.ai import generate_study_tasks
from collections import defaultdict


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
    # Get all study plans
    study_plans = StudyPlan.query.filter_by(user_id=current_user.id)\
                               .order_by(StudyPlan.updated_at.desc())\
                               .all()
    
    # Get all tasks across all plans
    all_tasks = StudyTask.query.join(StudyPlan)\
                             .filter(StudyPlan.user_id == current_user.id)\
                             .all()
    ai_tasks = [t for t in all_tasks if t.is_ai_generated]
    personal_tasks = PersonalTask.query.filter_by(user_id=current_user.id).all()
    
    # Calculate stats
    stats = {
        'total_plans': len(study_plans),
        'total_tasks': len(all_tasks) + len(personal_tasks),
        'total_ai_tasks': len(ai_tasks),
        'completed_ai_tasks': len([t for t in ai_tasks if t.is_done]),
        'total_personal_tasks': len(personal_tasks),
        'completed_personal_tasks': len([t for t in personal_tasks if t.is_done]),
        'last_updated': max(plan.updated_at for plan in study_plans) if study_plans else datetime.now(),
        'completion_rate': round(
            len([t for t in all_tasks if t.is_done]) / len(all_tasks) * 100 if all_tasks else 0,
            1
        ),
        'active_plan_name': study_plans[0].name if study_plans else "No active plan"
    }
    
    # Get active plan (most recently updated)
    active_plan = study_plans[0] if study_plans else None
    
    # Ensure subjects and subject_hours are always defined
    subjects = study_plans[0].subjects if study_plans else []
    subject_hours = []
    
    for subject in subjects:
        subject_tasks = [t for t in all_tasks if t.title.startswith(subject.name)]
        total_hours = sum(t.duration_minutes for t in subject_tasks) / 60
        subject_hours.append(round(total_hours, 2))
    
    return render_template('dashboard.html',
                         study_plans=study_plans,
                         study_plan=study_plans[0] if study_plans else None,
                         subjects=subjects,
                         subject_hours=subject_hours,
                         stats=stats,
                         now=datetime.now())


def parse_duration_to_minutes(duration_str):
    # Converts strings like "2 hours", "1.5 hours" into minutes
    match = re.match(r"(\d+(\.\d+)?)\s*hours?", duration_str.lower())
    if match:
        hours = float(match.group(1))
        return int(hours * 60)
    return 0


def group_tasks_by_day(tasks):
    grouped = defaultdict(list)
    for task in tasks:
        grouped[task.scheduled_date].append(task)
    return grouped


@main.route('/plan', methods=['GET', 'POST'])
@login_required
def plan():
    if request.method == 'POST':
        start_time = request.form.get('daily_start_time')
        end_time = request.form.get('daily_end_time')
        plan_name = request.form.get('plan_name')
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
            name=plan_name,
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

        if tasks_data:
            grouped_tasks = group_tasks_by_day(tasks_data)

            for day, tasks in grouped_tasks.items():
                for task_data in tasks:
                    scheduled_date = datetime.strptime(task_data.scheduled_date, "%Y-%m-%d").date()
                    duration_minutes = parse_duration_to_minutes(task_data.duration)

                    task = StudyTask(
                        title=task_data.task,
                        description=task_data.description,
                        scheduled_date=scheduled_date,
                        duration_minutes=duration_minutes,
                        plan_id=study_plan.id
                    )
                    db.session.add(task)

            db.session.commit()

            return redirect(url_for('main.dashboard'))

    return render_template('planform.html')


@main.route('/complete_task/<int:task_id>', methods=['POST'])
@login_required
def complete_task(task_id):
    task = StudyTask.query.get_or_404(task_id)
    task.is_done = not task.is_done  # Toggle completion status
    db.session.commit()
    
    # Get the filter from the form submission
    current_filter = request.form.get('current_plan_filter', 'all')
    
    # Redirect back with the filter preserved
    return redirect(url_for('main.ai_dashboard', plan_filter=current_filter))


@main.context_processor
def inject_now():
    return {'now': datetime.now}


@main.route('/tasks/personal')
@login_required
def personal_tasks():
    personal_tasks = PersonalTask.query.filter_by(user_id=current_user.id)\
                                     .order_by(PersonalTask.due_date)\
                                     .all()
    
    # Calculate completion percentage
    completed_count = sum(1 for task in personal_tasks if task.is_done)
    completion_percentage = round(completed_count / len(personal_tasks) * 100, 1) if personal_tasks else 0
    
    return render_template('personal_tasks.html', 
                         tasks=personal_tasks, 
                         completion_percentage=completion_percentage,
                         completed_count=completed_count)


@main.route('/tasks/personal/add', methods=['POST'])
@login_required
def add_personal_task():
    due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d').date() if request.form['due_date'] else None
    
    task = PersonalTask(
        title=request.form['title'],
        description=request.form['description'],
        due_date=due_date,
        user_id=current_user.id,
        priority=request.form['priority']
    )
    
    db.session.add(task)
    db.session.commit()
    flash('Personal task added successfully!', 'success')
    return redirect(url_for('main.personal_tasks'))


@main.route('/tasks/personal/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_personal_task(task_id):
    task = PersonalTask.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    task.is_done = not task.is_done
    db.session.commit()
    return redirect(url_for('main.personal_tasks'))


# Personal Task Routes
@main.route('/tasks/personal/<int:task_id>/update', methods=['POST'])
@login_required
def update_personal_task(task_id):
    task = PersonalTask.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    
    task.title = request.form['title']
    task.description = request.form['description']
    task.due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d').date() if request.form['due_date'] else None
    task.priority = int(request.form['priority'])
    task.updated_at = datetime.now()
    
    db.session.commit()
    flash('Task updated successfully!', 'success')
    return redirect(url_for('main.personal_tasks'))


@main.route('/tasks/personal/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_personal_task(task_id):
    task = PersonalTask.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('main.personal_tasks'))


@main.route('/ai_dashboard')
@login_required
def ai_dashboard():
    plan_filter = request.args.get('plan_filter', 'all')
    
    # Get plan IDs for current user first
    plan_ids = [p.id for p in current_user.study_plans]
    
    # Get tasks for these plans
    query = StudyTask.query.filter(
        StudyTask.plan_id.in_(plan_ids),
        StudyTask.is_ai_generated == True
    )
    
    # Apply plan filter if specified
    if plan_filter != 'all':
        query = query.filter(StudyTask.plan_id == int(plan_filter))
    
    ai_tasks = query.order_by(StudyTask.scheduled_date).all()
    
    stats = {
        'total_ai_tasks': len(ai_tasks),
        'completed_ai_tasks': sum(1 for t in ai_tasks if t.is_done)
    }
    print(ai_tasks)

    return render_template('ai_dashboard.html',
                         study_plans=current_user.study_plans,
                         ai_tasks=ai_tasks,
                         stats=stats,
                         current_filter=plan_filter)