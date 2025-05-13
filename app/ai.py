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
    prompt = (
        "You are an intelligent study planner. Based on the following subjects, topics, and daily available study hours, "
        "generate a JSON-formatted study plan that spans from today up to each subject's exam date.\n\n"

        "Guidelines:\n"
        f"- Schedule tasks daily within the user's available study time window: {start_time} to {end_time}.\n"
        "- Use the exam dates to plan backwards from today.\n"
        "- For complex or lengthy topics, break them into multiple sessions on different days.\n"
        "- Add revision sessions close to the exam date for each subject.\n"
        "- Multiple subjects can be scheduled on the same day, as long as they fit within the study window.\n\n"

        "Return a flat JSON array of tasks. Each task should include:\n"
        "- task: Title of the task\n"
        "- description: Brief detail of what to do\n"
        "- scheduled_date: Date in YYYY-MM-DD format\n"
        "- duration: Estimated duration in hours (e.g., '2 hours')\n"
        "- DO NOT include any 'break' field or value.\n\n"

        "Here are the subjects and topics:\n"
    )

    for subject in subjects:
        prompt += f"\nSubject: {subject.name} (Exam Date: {subject.exam_date})\n"
        for topic in subject.topics:
            prompt += f"- {topic.name} (Difficulty: {topic.difficulty})\n"

    prompt += "\nReturn ONLY a valid JSON array as explained above. Do not return day_1, day_2, etc. and also return all the tasks from today to the exam date of each subject so that each topic and subject is covered and if there is time left in the exam date and the subject is complete so you need to add revisions instead of studying and also add atleast 1 rivision for each subject right before exam like 1 day before exam so that students can revise what they studied"

    return prompt

def generate_study_tasks(subjects, start_time, end_time):
    prompt = generate_study_tasks_prompt(start_time, end_time, subjects)
    response = model.generate_content(prompt)

    # Assuming the response is in JSON format
    try:
        # Directly parse the JSON response into a list of StudyTask objects
        study_schedule = [StudyTask.model_validate(task) for task in json.loads(response.text)]
        return study_schedule
    except json.JSONDecodeError:
        print("Error parsing response:", response.text)
        return None
    except Exception as e:
        print(f"Error in parsing the response to StudyTask format: {e}")
        return None