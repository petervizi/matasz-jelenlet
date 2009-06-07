import sys
sys.path.insert(0, 'GChartWrapper.zip')

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import Context, loader
from jelenlet.models import Session, UserNumber

from google.appengine.ext import db
from google.appengine.api import memcache

from datetime import datetime, timedelta
from GChartWrapper import *
import math

from tz import utc, cest

q = db.GqlQuery("SELECT * FROM UserNumber ORDER BY number DESC")
m = q.get()
if m:
    memcache.set("online_peak", m.number)
else:
    memcache.set("online_peak", 1)

q = db.GqlQuery("SELECT * FROM Session WHERE logout < 0")
m = q.count()
memcache.set("online_users", m)

def index(request):
    t = loader.get_template("index.html")
    c = Context({
            'online_percent': 100.-100*float(memcache.get("online_users"))/memcache.get("online_peak"),
            'online_users': memcache.get("online_users"),
            'online_peak': memcache.get("online_peak")
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

    prange = xrange(list_from - 3, list_from + 3)
    prange = [p for p in prange if p > 0 and p < count]
    c = Context({
            'online_percent': 100.-100*float(memcache.get("online_users"))/memcache.get("online_peak"),
            'online_users': memcache.get("online_users"),
            'from': list_from,
            'next': next,
            'prev': list_from - 1,
            'count': int(count) - 1,
            'range': prange,
            'sessions': thesessions,
            'title': 'Lista',
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

def user(request, name, page):
    if not page:
        page = 0
    else:
        page = int(page)
    sessions_q = Session.all().filter('user = ', name).order('-login')

    sessions = sessions_q.fetch(10, page * 10)

    sessions = sessions_q.fetch(10, page * 10)
    for session in sessions:
        session.login = session.login.replace(tzinfo=utc).astimezone(cest)
        if session.logout:
            session.logout = session.logout.replace(tzinfo=utc).astimezone(cest)
            session.duration = session.logout - session.login
        
    c = Context({
            'online_percent': 100.-100*float(memcache.get("online_users"))/memcache.get("online_peak"),
            'online_users': memcache.get("online_users"),
            'title': name,
            'sessions': sessions,
            })
    t = loader.get_template("user.html")
    return HttpResponse(t.render(c))

def week(request, page):
    if page:
        page = int(page)
    else:
        page = 0
    data = [11]*7
    axes = ''
    today = datetime.now()
    for day in xrange(1, 8):        
        dfrom = today - timedelta(days=(7*page + day))
        dto = dfrom - timedelta(days=(7*(page+1) + day))        
        ol = UserNumber.all().filter('time <= ', dfrom).filter('time > ', dto).fetch(100)
        numbers = [f.number for f in ol]
        average = sum(numbers)
        if len(numbers):
            average = average / len(numbers)
        data[6-day] = average
        axes = "%s|" % dfrom.strftime("%a") + axes

    G = Sparkline(data, encoding='text')
    G.axes.type('xy')
    G.axes.label(0, axes)
    G.color('0077CC')
    G.size(200,40)
    G.marker('B', 'E6F2FA',0,0,0)
    G.line(1,0,0)
    G.title("Week view")
    G.size((300,200))
    G.axes.range(1, '0,%d,1' % max(data))
    G.grid(100./7,10)
    return HttpResponseRedirect(G.url)
