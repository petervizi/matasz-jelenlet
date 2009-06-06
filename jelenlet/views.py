from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import Context, loader
from jelenlet.models import Session, UserNumber

from google.appengine.ext import db
from google.appengine.api import memcache

from datetime import datetime
import math

from tz import utc, cest

q = db.GqlQuery("SELECT * FROM UserNumber ORDER BY number DESC")
m = q.get()
if m:
    memcache.set("online_peak", m.number)
else:
    memcache.set("online_peak", 1)
memcache.set("online_users", 0)

def index(request):
    t = loader.get_template("index.html")
    c = Context({
            'online_percent': memcache.get("online_users")/memcache.get("online_peak"),
            'online_users': memcache.get("online_users"),
            })
    return HttpResponse(t.render(c))

def list(request, list_from=0):
    if not list_from:
        list_from = 1
    else:
        list_from = int(list_from)
    sessions = Session.all()
    sessions.order('-login')
    
    t = loader.get_template("list.html")
    count = math.ceil(Session.all().count() / 10.)+1
    next = 0
    if list_from + 1 < count:
        next = list_from + 1

    thesessions = sessions.fetch(10, (list_from - 1)*10)
    for session in thesessions:
        session.login = session.login.replace(tzinfo=utc).astimezone(cest)
        if session.logout:
            session.logout = session.logout.replace(tzinfo=utc).astimezone(cest)
            session.duration = session.logout - session.login

    c = Context({
            'online_percent': memcache.get("online_users")/memcache.get("online_peak"),
            'online_users': memcache.get("online_users"),
            'from': list_from,
            'next': next,
            'prev': list_from - 1,
            'count': range(1, count),
            'sessions': thesessions
            })
    return HttpResponse(t.render(c))

def login(request):
    if request.method == 'POST':
        session = Session()
        session.user = request.POST['user']
        session.put()
        memcache.incr("online_users")
        n = memcache.get("online_users")
        userno = UserNumber()
        userno.number = n
        if n > memcache.get("online_peak"):
            memcache.set("online_peak", n)
        userno.put()
    return HttpResponseRedirect(reverse('jelenlet.views.index'))

def logout(request):
    if request.method == 'POST':
        session_q = Session.all()
        session_q.filter('user = ', request.POST['user'])
        session_q.order('-login')
        session = session_q.get()
        if session:
            session.logout = datetime.now()
            memcache.decr("online_users")
        else:
            session = Session()
            session.user = request.POST['user']
            session.logout = session.login
        session.put()
    return HttpResponseRedirect(reverse('jelenlet.views.index'))
