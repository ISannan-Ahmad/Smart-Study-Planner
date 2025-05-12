from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required
from datetime import datetime
import json

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


@main.route("/plan", methods=["GET", "POST"])
def plan():
    if request.method == "POST":
        form_data = request.form.to_dict(flat=False)

        # Step 1: Extract study time range
        daily_start = request.form.get("daily_start_time")  # e.g., '18:00'
        daily_end = request.form.get("daily_end_time")      # e.g., '01:00'

        # Step 2: Reconstruct subjects
        subjects = []
        subject_indexes = set()

        # Find all unique subject indexes
        for key in form_data:
            if key.startswith("subjects["):
                idx = key.split("[")[1].split("]")[0]
                subject_indexes.add(idx)

        for idx in subject_indexes:
            name = request.form.get(f"subjects[{idx}][name]")
            exam_date = request.form.get(f"subjects[{idx}][exam_date]")

            topics = []
            topic_index = 0
            while True:
                topic_name = request.form.get(f"subjects[{idx}][topics][{topic_index}][name]")
                topic_difficulty = request.form.get(f"subjects[{idx}][topics][{topic_index}][difficulty]")
                if not topic_name:
                    break
                topics.append({
                    "name": topic_name,
                    "difficulty": topic_difficulty
                })
                topic_index += 1

            subjects.append({
                "name": name,
                "exam_date": exam_date,
                "topics": topics
            })

        # Final structured data
        user_input = {
            "daily_start_time": daily_start,
            "daily_end_time": daily_end,
            "subjects": subjects
        }

        # You can now:
        # - Send this to Gemini API
        # - Pass it to your schedule generator
        # - Render a result page
        return render_template("schedule.html", schedule=user_input)  # TEMP: just to test it

    return render_template("planform.html")