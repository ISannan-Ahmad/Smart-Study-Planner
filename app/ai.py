import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
from .schemas import StudyTask
from pydantic import parse_obj_as
from typing import List

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel('gemini-1.5-flash')

def generate_study_tasks_prompt(start_time, end_time, subjects):
    prompt = f"""
You are an intelligent study planner. Based on the following subjects, topics, and daily available study hours,
generate a JSON-formatted study plan that spans from today up to each subject's exam date.

Guidelines:
- Schedule tasks daily within the user's available study time window: {start_time} to {end_time}.
- Use the exam dates to plan backwards from today.
- For complex or lengthy topics, break them into multiple sessions on different days.
- Add revision sessions close to the exam date for each subject.
- Multiple subjects can be scheduled on the same day, as long as they fit within the study window.

Return a flat JSON array of tasks. Each task should include:
- task: Title of the task
- description: Brief detail of what to do
- scheduled_date: Date in YYYY-MM-DD format
- duration: Estimated duration in hours (e.g., "2 hours")
- DO NOT include any 'break' field or value.

Here are the subjects and topics:
"""

    for subject in subjects:
        prompt += f"\nSubject: {subject.name} (Exam Date: {subject.exam_date})\n"
        for topic in subject.topics:
            prompt += f"- {topic.name} (Difficulty: {topic.difficulty})\n"

    prompt += """           
                Return ONLY a valid JSON array as e xplained above. Do not return day_1, day_2, etc.
                Return all the tasks from today to the exam date of each subject so that each topic and subject is covered.
                If there is time left until the exam date and the subject is complete, add revisions instead of new study.
                Also add at least one revision for each subject one day before its exam. Make sure that the tasks date that you assign are from today's date for example today is 2025-5-21 and if i create a task today so the task should start from 2025-5-21 to the date of exam for example exam is on 2025-5-29 so you should manage all the tasks between these dates

                Here's an example of how you should format the response:

                [
                {
                    "task": "Study Linked List",
                    "description": "Review the basic concepts of linked list",
                    "scheduled_date": "2025-05-14",
                    "duration": "2 hours"
                },
                {
                    "task": "Study Integration - Session 1",
                    "description": "Understand basic integration rules",
                    "scheduled_date": "2025-05-14",
                    "duration": "3 hours"
                },
                {
                    "task": "Revise Linked List",
                    "description": "Quick recap of linked list before the exam",
                    "scheduled_date": "2025-05-20",
                    "duration": "1 hour"
                }
                ]
            """

    return prompt

def clean_response_text(raw_text: str) -> str:
    """
    Cleans the raw Gemini response text by removing Markdown code block markers like ```json
    """
    raw_text = raw_text.strip()
    if raw_text.startswith("```json"):
        raw_text = raw_text[len("```json"):].strip()
    elif raw_text.startswith("```"):
        raw_text = raw_text[len("```"):].strip()
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3].strip()
    return raw_text


def generate_study_tasks(subjects, start_time, end_time) -> List[StudyTask] | None:
    prompt = generate_study_tasks_prompt(start_time, end_time, subjects)
    response = model.generate_content(prompt)

    try:
        raw_text = clean_response_text(response.text)
        data = json.loads(raw_text)  # safely load JSON string into Python object
        tasks = [StudyTask.model_validate(item) for item in data]  # use updated Pydantic v2 method
        return tasks

    except json.JSONDecodeError as e:
        print("JSON parsing error:", e)
        print("Raw response:\n", response.text)
    except Exception as e:
        print("Validation error:", e)

    return None