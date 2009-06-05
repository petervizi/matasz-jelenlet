import os
from datetime import datetime
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template

class Session(db.Model):
    user = db.StringProperty()
    login =  db.DateTimeProperty(auto_now_add=True)
    logout = db.DateTimeProperty()

class MainPage(webapp.RequestHandler):
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
    self.response.out.write(template.render(path, {}))

class LoginPage(webapp.RequestHandler):
    def get(self):
        self.redirect('/')

    def post(self):
        session = Session()
        session.user = self.request.get('user')
        session.put()

class LogoutPage(webapp.RequestHandler):
    def get(self):
        self.redirect('/')

    def post(self):
        session_q = Session.all()
        session_q.filter('user = ', self.request.get('user'))
        session_q.order('-login')
        sessions = session_q.fetch(1)
        
        if len(sessions) == 1:
            session = sessions[0]
        else:
            session = Session()
            session.user = self.request.get('user')

        session.logout = datetime.now()       
        session.put()

class ListPage(webapp.RequestHandler):
    def get(self):
        sessions_q = Session.all().order('-login')
        sessions = sessions_q.fetch(10)
        template_values = {
            'sessions': sessions}
        path = os.path.join(os.path.dirname(__file__), 'templates/list.html')
        self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/login', LoginPage),
                                      ('/logout', LogoutPage),
                                      ('/list', ListPage)
                                      ],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
