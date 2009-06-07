from appengine_django.models import BaseModel
from google.appengine.ext import db

class Session(BaseModel):
    user = db.StringProperty()
    login =  db.DateTimeProperty(auto_now_add=True)
    logout = db.DateTimeProperty()

class UserNumber(BaseModel):
    time = db.DateTimeProperty(auto_now_add=True)
    number = db.IntegerProperty()

class WeeklyStat(BaseModel):
    week = db.IntegerProperty()
    url = db.StringProperty()
