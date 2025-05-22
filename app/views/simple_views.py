from app.models import User, StudyPlan, StudyTask, PersonalTask, Subject, Topic
from app import db
from datetime import datetime, timedelta

def get_user_study_progress(user_id):
    """Calculate and return user study progress statistics"""
    
    # Get all tasks (study + personal)
    study_tasks = db.session.query(
        db.func.count(StudyTask.id).label('total_study_tasks'),
        db.func.sum(db.case((StudyTask.is_done == True, 1), else_=0)).label('completed_study_tasks')
    ).join(StudyPlan).filter(
        StudyPlan.user_id == user_id
    ).first()

    personal_tasks = db.session.query(
        db.func.count(PersonalTask.id).label('total_personal_tasks'),
        db.func.sum(db.case((PersonalTask.is_done == True, 1), else_=0)).label('completed_personal_tasks')
    ).filter(
        PersonalTask.user_id == user_id
    ).first()

    # Get study plans count
    total_plans = StudyPlan.query.filter_by(user_id=user_id).count()

    # Calculate percentages
    total_tasks = (study_tasks.total_study_tasks or 0) + (personal_tasks.total_personal_tasks or 0)
    completed_tasks = (study_tasks.completed_study_tasks or 0) + (personal_tasks.completed_personal_tasks or 0)
    
    completion_percentage = 0
    if total_tasks > 0:
        completion_percentage = round((completed_tasks / total_tasks) * 100, 1)

    return {
        'total_plans': total_plans,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'completion_percentage': completion_percentage,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')
    }

def get_upcoming_exams(user_id):
    """Get all upcoming exams for a user"""
    exams = db.session.query(
        Subject.name.label('subject_name'),
        Subject.exam_date,
        StudyPlan.name.label('plan_name'),
        (Subject.exam_date - datetime.now().date()).label('days_remaining')
    ).join(StudyPlan).filter(
        StudyPlan.user_id == user_id,
        Subject.exam_date >= datetime.now().date()
    ).order_by(
        'days_remaining'
    ).all()

    return [{
        'subject_name': exam.subject_name,
        'exam_date': exam.exam_date.strftime('%Y-%m-%d'),
        'plan_name': exam.plan_name,
        'days_remaining': exam.days_remaining
    } for exam in exams]

def get_task_timeline(user_id, days=30):
    """Get task completion timeline for the last N days"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    timeline = db.session.query(
        db.func.date(StudyTask.scheduled_date).label('date'),
        db.func.count().label('total_tasks'),
        db.func.sum(db.case((StudyTask.is_done == True, 1), else_=0)).label('completed_tasks')
    ).join(StudyPlan).filter(
        StudyPlan.user_id == user_id,
        StudyTask.scheduled_date.between(start_date, end_date)
    ).group_by(
        db.func.date(StudyTask.scheduled_date)
    ).order_by(
        'date'
    ).all()

    return [{
        'date': item.date.strftime('%Y-%m-%d'),
        'total_tasks': item.total_tasks,
        'completed_tasks': item.completed_tasks,
        'completion_rate': round((item.completed_tasks / item.total_tasks) * 100, 1) if item.total_tasks else 0
    } for item in timeline]

def get_subject_difficulty(user_id):
    """Get difficulty distribution across subjects"""
    difficulty_data = db.session.query(
        Subject.name.label('subject_name'),
        Topic.difficulty,
        db.func.count().label('topic_count')
    ).join(StudyPlan).join(Topic).filter(
        StudyPlan.user_id == user_id
    ).group_by(
        Subject.name, Topic.difficulty
    ).all()

    # Organize by subject
    subjects = {}
    for item in difficulty_data:
        if item.subject_name not in subjects:
            subjects[item.subject_name] = []
        subjects[item.subject_name].append({
            'difficulty': item.difficulty,
            'count': item.topic_count
        })

    # Calculate percentages
    result = []
    for subject, difficulties in subjects.items():
        total = sum(d['count'] for d in difficulties)
        result.append({
            'subject_name': subject,
            'difficulties': [{
                'difficulty': d['difficulty'],
                'count': d['count'],
                'percentage': round((d['count'] / total) * 100, 1)
            } for d in difficulties]
        })

    return result

def get_overdue_tasks(user_id):
    """Get all overdue personal tasks"""
    tasks = PersonalTask.query.filter(
        PersonalTask.user_id == user_id,
        PersonalTask.due_date < datetime.now().date(),
        PersonalTask.is_done == False
    ).order_by(
        PersonalTask.due_date,
        PersonalTask.priority
    ).all()

    return [{
        'id': task.id,
        'title': task.title,
        'due_date': task.due_date.strftime('%Y-%m-%d'),
        'days_overdue': (datetime.now().date() - task.due_date).days,
        'priority': task.priority,
        'priority_text': ['High', 'Medium', 'Low'][task.priority - 1]
    } for task in tasks]














