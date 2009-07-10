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
    day = db.DateTimeProperty()
    url = db.StringProperty()

class CUser(BaseModel):
    name = db.StringProperty()
    lastlogin = db.DateTimeProperty()
    online = db.BooleanProperty()
    online_time = db.IntegerProperty()
    
class Hit(BaseModel):
    name = db.StringProperty()
    time = db.DateTimeProperty()
    where = db.StringProperty()
    dmg = db.IntegerProperty()

class GraphCache(BaseModel):
    url = db.StringProperty()
    graph = db.BlobProperty()

class Member(BaseModel):
    name = db.StringProperty()
    id = db.IntegerProperty()
    avatar = db.StringProperty()
