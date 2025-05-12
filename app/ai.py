import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel('gemini-pro')

def generate_study_tasks_prompt(subjects):
    prompt = "Create a study plan with tasks for the following subjects and topics:\n\n"
    for subject in subjects:
        prompt += f"Subject: {subject.name} (Exam: {subject.exam_date})\n"
        for topic in subject.topics:
            prompt += f"- {topic.name} (Difficulty: {topic.difficulty})\n"
        prompt += "\n"
    prompt += "Give each task a title and description.\n"
    return prompt


def generate_study_tasks(subjects):
    prompt = generate_study_tasks_prompt(subjects)
    response = model.generate_content(prompt)
    return response.text
