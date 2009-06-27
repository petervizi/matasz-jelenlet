import re
import sys
sys.path.insert(0, 'GChartWrapper.zip')

from django.http import *
from django.core.urlresolvers import reverse
from django.template import Context, loader
from django.utils.translation import ugettext as _
from django.utils import simplejson
from django.core import serializers

from jelenlet.models import *

from google.appengine.ext import db
from google.appengine.api import memcache

from datetime import datetime, timedelta, date
from GChartWrapper import *
import math

from tz import utc, cest
import logging

from operator import itemgetter

def get_online_users():
    data = memcache.get('online_users')
    if data is None:
        data = UserNumber.all().order('-time').get()
        if data is None:
            logging.debug('nincs data')
            data = 0
        elif data.number < 0:
            data = 0
        else:
            data = data.number
        memcache.set('online_users', data, 120)
    logging.info('kiadjuk %d', data)
    return data

def get_online_peak():
    data = memcache.get('online_peak')
    if data is None:
        data = UserNumber.all().order('-number').get()
        if data is None:
            data = 1
        else:
            try:
                data = int(data.number)
            except:
                data = 1
        if data <= 0:
            data = 1
        memcache.set('online_peak', data, 120)
    return data


def index(request):
    t = loader.get_template("index.html")
    today = datetime.now()
    c = Context({
            'title': _("Welcome"),
            'today': '%d-%02d-%02d' % (today.year, today.month, today.day),
            })
    return HttpResponse(t.render(c))

def list(request, list_from=0):
    if request.method == 'GET':
        if not list_from:
            list_from = 1
        else:
            list_from = int(list_from)
        sessions = Session.all()
        sessions.order('-login')
        t = loader.get_template("list.html")
        title = _('List')
    else:
        name = request.POST['name']
        list_from = int(request.POST['page'])
        sessions = Session.all().filter('user = ', name).order('-login')
        t = loader.get_template('ajaxlist.html')
        title = name

    count = math.ceil(sessions.count() / 10.)+1    
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
            'from': list_from,
            'next': next,
            'prev': list_from - 1,
            'count': int(count) - 1,
            'range': prange,
            'sessions': thesessions,
            'title': title,
            })
    return HttpResponse(t.render(c))

def login(request):
    if request.method == 'POST':
        logging.info('login')
        #dsession = db.GqlQuery("SELECT * FROM Session WHERE user = :1 AND logout < :2",
        #                       request.POST['user'], 0)
        #dsession = dsession.get()        
        #if dsession:
        #    logging.info("dangling")
        #    dsession.logout = datetime.now()            
        #    dsession.put()
        session = Session()
        session.user = request.POST['user']
        session.put()
        logging.info("user %s" % session.user)
        n = UserNumber.all().order('-time').get()
        logging.info('UserNumber %s' % n)
        if (n is None) or (n.number is None):
            logging.info('UserNumber was None')
            n = 0
        else:
            logging.info('UserNumber was %d', n.number)
            n = n.number
        userno = UserNumber()
        try:
            userno.number = int(n) + 1
        except:
            logging.info('Number was not a number!')
            userno.number = 1
        logging.info('New UserNumber %d' % userno.number)
        userno.put()
        duser = CUser.all().filter('name = ', request.POST['user'])
        duser = duser.get()
        if not duser:
            logging.info('Creating new user.')
            duser = CUser()
            duser.name = request.POST['user']
            duser.online_time = 0
        duser.lastlogin = datetime.now()
        duser.online = True
        duser.put()
        return HttpResponseRedirect(reverse('jelenlet.views.index'))
    else:
        raise Http404

def logout(request):
    if request.method == 'POST':
        logging.info('logout')
        session_q = Session.all()
        session_q.filter('user = ', request.POST['user'])
        session_q.order('-login')
        session = session_q.get()
        logging.info('User %s' % session.user)
        userno = UserNumber()
        n = UserNumber.all().order('-time').get()
        if n is None:
            logging.info('UserNumber was None')
            n = 0
        else:
            logging.info('UserNumber was %d' % n.number)
            n = n.number
        if session:
            session.logout = datetime.now()
            logging.info('there was a session, closing')
        else:
            loggin.debug('creating new session')
            session = Session()
            session.user = request.POST['user']
            session.logout = session.login
        session.put()
        duser = CUser.all().filter('name = ', request.POST['user']).get()
        if not duser:
            logging.info('creating new user')
            duser = CUser()
            duser.name = request.POST['user']
            duser.lastlogin = datetime.now()
            duser.online_time = 0
            duser.online = True
        if duser.online:
            logging.info('user was online')
            try:
                userno.number = n - 1
                if userno.number < 0:
                    userno.number = 0
            except:
                logging.info('could not decrease number')
                userno.number = 0
        duser.online = False
        logging.info("New UserNumber %d" % userno.number)
        userno.put()            
        delta = duser.lastlogin - datetime.now()
        duser.online_time = duser.online_time + delta.seconds
        duser.put()
        return HttpResponseRedirect(reverse('jelenlet.views.index'))
    else:
        raise Http404

def nickchange(request):
    if request.method == 'POST':
        oldn = request.POST['old']
        newn = request.POST['new']
        ouser = CUser.all().filter('name = ', oldn)
        ouser = ouser.get()
        if not ouser:
            ouser = CUser()
            ouser.name = newn
            ouser.lastlogin = datetime.now()
            ouser.online_time = 0
        else:
            ouser.name = newn
        ouser.online = True
        ouser.put()
        session = Session.all().filter('user = ', oldn)
        session = session.get()
        if session:
            session.user = newn
        else:
            session = Session()
            session.user = newn
        session.put()
        return HttpResponseRedirect(reverse('jelenlet.views.index'))
    else:
        raise Http404

def user(request, name):
    today = date.today()
    user = CUser.all().filter('name = ', name).get()    

    c = Context({
            'user': user,
            'title': name,
            'timestat1_prev': today - timedelta(days = 7),
            'timestat2_prev': today - timedelta(days = 30),
            })
    t = loader.get_template("user.html")
    return HttpResponse(t.render(c))

def create_weekly_graph(query):
    '''Return an url to the graph'''
    today = date.today()
    data = [0]*7
    axes = ''
    for day in xrange(1, 8):        
        dfrom = query - timedelta(days=(day))
        dto = query - timedelta(days=(7 + day))
        ol = UserNumber.all().filter('time <= ', dfrom).filter('time > ', dto).fetch(100)
        numbers = [f.number for f in ol]
        numbers = filter(lambda x: x != None, numbers)
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
    G.title(_('Week view'))
    G.size((300,200))
    G.axes.range(1, '0,%d,1' % max(data))
    G.grid(100./7,10)
    return G.url

def week(request, year, month, day):
    today = datetime.now()
    try:
        query = datetime(int(year), int(month), int(day))
    except:
        return HttpResponseBadRequest()
    if today - query > timedelta(days=7):
        ws = WeeklyStat.all().filter('day = ', query).get()
        if not ws:
            ws = WeeklyStat()
            ws.day = query
            ws.url = create_weekly_graph(query)
            ws.put()
        url = ws.url
    else:
        url = create_weekly_graph(query)
    return HttpResponseRedirect(url)

def timestat(request, duration, user, fyear, fmonth, fday):
    now = datetime(int(fyear), int(fmonth), int(fday))
    max_dur = 86400.
    if duration == 'week':
        day_r = 7
        caption = _('Week view')
        xlabel = "%a"
        jscriptfn = 'dload_timestat1'
    elif duration == 'month':
        day_r = 30
        caption = _('Month view')
        xlabel = "%d"
        jscriptfn = 'dload_timestat2'
    data = [0]*day_r
    axes = ''
    for day in xrange(1,day_r + 1):        
        dfrom = now - timedelta(days=(day + 1))
        dto = now - timedelta(days=(day))
        ol = Session.all().filter('user = ', user).filter('login > ', dfrom).filter('login < ', dto).fetch(100)
        sum = 0
        for o in ol:
            try:
                if o.logout > dto:
                    o.logout = dto
                sum += (o.logout - o.login).seconds
            except:
                pass         
        data[day_r-day] = sum/max_dur*100.
        axes = "%s|" % dfrom.strftime(xlabel) + axes

    G = Sparkline(data, encoding='text')
    G.axes.type('xy')
    G.axes.label(0, axes)
    G.color('0077CC')
    G.size(200,40)
    G.marker('B', 'E6F2FA',0,0,0)
    G.line(1,0,0)
    G.title(caption)
    G.size((300,200))
    #G.axes.range(1, '0,%d,1' % 1)
    G.axes.range(0, (0,1,0.1))
    G.axes.range(1, (0,day_r))
    G.grid(100./day_r, 100)
    if request.method == 'POST':
        next = now + timedelta(days=day_r)
        if next > datetime.now():
            next = None
        else:
            next = next.strftime("%Y-%m-%d")
        data = Context({
            'url': G.url,
            'prev': (now - timedelta(days=day_r)).strftime("%Y-%m-%d"),
            'next': next,
            'duration': duration,
            'title': user,
            'jscriptfn': jscriptfn,
        })
        return HttpResponse(loader.get_template("timestat.html").render(data))
    else:
        return HttpResponseRedirect(G.url)
    
def hit(request):
    if request.method == 'POST':
        h = Hit()
        h.name = request.POST['user'].strip()
        h.where = request.POST['where'].lower()
        try:
            h.dmg = int(request.POST['dmg'])
        except:
            return HttpResponse("%s nem szam" % 
                                request.POST['dmg'].strip())
        h.time = datetime.now()
        h.put()
        return HttpResponse("Utesed elmentve: %s %d." %
                            (capitalize(h.where), h.dmg))
    else:
        raise Http404

DATEREG = re.compile("(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})")
def getdatefromstring(string):
    '''Return a datetime from a string: 2009-01-01'''
    m = DATEREG.match(string)
    if m:
        year = int(m.group('year'))
        month = int(m.group('month'))
        day = int(m.group('day'))        
        dd = datetime(year, month, day)
    else:
        dd = datetime.today()
    return dd


def hits(request, page):
    if request.method == 'GET':
        t = loader.get_template("hits.html")
        hits = Hit.all().order("-time")
        count = math.ceil(Hit.all().count() / 10.)+1
        title =  _('Hits')
        format = 'html'
    else:
        t = loader.get_template("ajaxhits.html")
        name = request.POST.get('name', '')
        page = request.POST.get('page', 0)
        time = str(request.POST.get('time', ''))
        if time:
            time = getdatefromstring(time)
        where = str(request.POST.get('where', ''))
        format = request.POST.get('format', 'html')
        logging.info("format %s" % format)
        # Here comes the bot's request
        hits = Hit.all()
        if name:
            hits.filter('name = ', name)
            logging.info("name %s", name)
        if where:
            hits.filter('where = ', where)
            logging.info("where %s", where)
        if time:
            logging.info("time %s" % time)
            max = time + timedelta(days = 1)
            hits.filter("time > ", time)
            hits.filter("time < ", max)
        hits.order('-time')
        count = math.ceil(Hit.all().filter('name =', name).count() / 10.)+1
        title = name
    if page:
        try:
            page = int(page)
        except:
            page = 1
    else:
        page = 1
    logging.info("page %d" % page)

    if page + 1 < count:
        next = page + 1
    else:
        next = 0
    prange = xrange(page - 3, page + 4)
    prange = [p for p in prange if p > 0 and p < count]
    hits = hits.fetch(10, (page-1)*10)
    logging.info("len(hits) %d" % len(hits))
    if format == 'html':
        for hit in hits:
            hit.time = hit.time.replace(tzinfo=utc).astimezone(cest)
        c = Context({
                'from': page,
                'next': next,
                'prev': page - 1,
                'count': int(count) - 1,
                'range': prange,
                'title': title,
                'hits': hits
                })
        return HttpResponse(t.render(c))
    elif format == 'json':
        sum = 0
        data = {}
        for hit in hits:
            hit.where = hit.where.capitalize()
            sum += hit.dmg
            if hit.where in data:
                if hit.time.strftime("%Y-%m-%d") in data[hit.where]:
                    data[hit.where][hit.time.strftime("%Y-%m-%d")] += hit.dmg
                else:
                    data[hit.where][hit.time.strftime("%Y-%m-%d")] = hit.dmg
            else:
                data[hit.where] = {}
                data[hit.where][hit.time.strftime("%Y-%m-%d")] = hit.dmg            
        try:
            value = {
                'err': False,
                'sum': sum,
                'data': data,
                }
            data = simplejson.dumps(value, indent=4)
            return HttpResponse(data, mimetype="text/json")
        except Exception, e:
            return HttpResponse("itt a bibi %s" % e)
    else:
        pass

def userno(request):
    return HttpResponse("userno: %d" % get_online_users())
#    q = UserNumber.all()
#    r = q.fetch(400)
#    db.delete(r)

def capitalize(text):
    words = text.split(' ')
    words = [word.capitalize() for word in words]
    return ' '.join(words)

def base_stats(request):
    data = {
        'online_percent': "%f%%" % (100.-100*float(get_online_users())/get_online_peak()),
        'online_users': get_online_users(),
        'online_peak': get_online_peak(),
        }
    data = simplejson.dumps(data, indent=4)
    return HttpResponse(data, mimetype="text/json")

def f9(seq):
    # Not order preserving
    return {}.fromkeys(seq).keys()

def activeusers(request, duration, year, month, day, hfrom, hto):
    try:
        dfrom = datetime(int(year), int(month), int(day), int(hfrom))
        dto = datetime(int(year), int(month), int(day), int(hto))
        delta = (dto - dfrom).seconds
    except:
        return HttpResponseBadRequest()
    if duration == 'week':
        day_range = 7
    elif duration == 'month':
        day_range = 30
    else:
        return HttpResponseBadRequest()
    maxd = delta * day_range
    stat = {}
    for i in xrange(1, 1+day_range):
        dfrom = dfrom - timedelta(days=1)
        dto = dto - timedelta(days=1)
        sessions1 = Session.all(keys_only=True).filter('login < ', dto).filter('login > ', dfrom).fetch(100)
        sessions2 = Session.all(keys_only=True).filter('logout < ', dto).filter('logout > ', dfrom).fetch(100)
        sessions1.extend(sessions2)
        sessions1 = f9(sessions1)
        sessions = Session.get(sessions1)
        for session in sessions:
            if session.login < dfrom:
                session.login = dfrom
            if session.logout and session.logout > dto:
                session.logout = dto
            else:
                session.logout = session.login
            if session.user in stat:
                stat[session.user] += (session.logout - session.login).seconds
            else:
                stat[session.user] = (session.logout - session.login).seconds
    stat = sorted(stat.iteritems(), key=itemgetter(1), reverse = True)
    #stat = sorted(stat.iteritems(), key=lambda (k,v):(v,k), reverse=True)
    c = Context({'sorted': stat,
                 'maxd': maxd})
    return HttpResponse(loader.get_template("activeusers.html").render(c))

def activity(request):
    c = Context({})
    return HttpResponse(loader.get_template('activity.html').render(c))

