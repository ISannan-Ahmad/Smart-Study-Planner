import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///studyplanner.db"
    SECRET_KEY = "this_is_my_super_secret_nuclear_bomb_key"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
