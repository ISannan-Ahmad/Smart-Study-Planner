from pydantic import BaseModel
from typing import List

class StudyTask(BaseModel):
    task: str
    description: str
    scheduled_date: str
    duration: str
