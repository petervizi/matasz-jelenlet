import sys
sys.path.insert(0, 'django.zip')

import os
import time
from datetime import datetime, tzinfo, timedelta
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
import django.forms.fields

memcache.set("online_users", 0)

class CEST(tzinfo):
    """CET timezone with DST"""
    def utcoffset(self, dt):
        return timedelta(hours=1) + self.dst(dt)
    def dst(self, dt):
        return timedelta(hours=1)
    def tzname(self, dt):
        return "CEST"

class UTC(tzinfo):
    """UTC timezone"""
    def utcoffset(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return timedelta(0)

cest = CEST()
utc = UTC()

class Session(db.Model):
    user = db.StringProperty()
    login =  db.DateTimeProperty(auto_now_add=True)
    logout = db.DateTimeProperty()

class UserNumber(db.Model):
    time = db.DateTimeProperty(auto_now_add=True)
    number = db.IntegerProperty()

q = db.GqlQuery("SELECT * FROM UserNumber ORDER BY number DESC")
m = q.get()
if m:
    memcache.set("online_peak", m.number)
else:
    memcache.set("online_peak", 1)

class MainPage(webapp.RequestHandler):
  def get(self):
      template_values = {
          'online_percent': memcache.get("online_users")/memcache.get("online_peak"),
          'online_users': memcache.get("online_users"),
          }
      path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
      self.response.out.write(template.render(path, template_values))

class LoginPage(webapp.RequestHandler):
    def get(self):
        self.redirect('/')

    def post(self):
        session = Session()
        session.user = self.request.get('user')
        memcache.incr("online_users")
        n = memcache.get("online_users")
        userno = UserNumber()
        userno.number = n
        if n > memcache.get("online_peak"):
            memcache.set("online_peak", n)
        session.put()

class LogoutPage(webapp.RequestHandler):
    def get(self):
        self.redirect('/')

    def post(self):
        session_q = Session.all()
        session_q.filter('user = ', self.request.get('user'))
        session_q.order('-login')
        sessions = session_q.get()
        
        if len(sessions) == 1:
            session = sessions[0]
            memcache.decr("online_users")
        else:
            session = Session()
            session.user = self.request.get('user')

        session.logout = datetime.now()       
        session.put()

class ListPage(webapp.RequestHandler):
    def get(self):
        sessions_q = Session.all().order('-login')
        sessions = sessions_q.fetch(10)
        for session in sessions:
            session.login = session.login.replace(tzinfo=utc).astimezone(cest)
            if session.logout:
                session.logout = session.logout.replace(tzinfo=utc).astimezone(cest)
        template_values = {
            'sessions': sessions,
            'online_percent': memcache.get("online_users")/memcache.get("online_peak"),
            'online_users': memcache.get("online_users")
            }
        path = os.path.join(os.path.dirname(__file__), 'templates/list.html')
        self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/login/%d', LoginPage),
                                      ('/logout', LogoutPage),
                                      ('/list', ListPage)
                                      ],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
