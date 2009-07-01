from datetime import datetime, timedelta, date

from django.utils.translation import ugettext as _
from GChartWrapper import *

from models import *

def timestat_graph(duration, user, fyear, fmonth, fday):
    '''Returns graph object'''
    now = datetime(fyear, fmonth, fday)
    max_dur = 864.
    if duration == 'week':
        day_r = 7
        caption = _('Week view')
        xlabel = "%a"
    elif duration == 'month':
        day_r = 30
        caption = _('Month view')
        xlabel = "%d"
    data = [0]*day_r
    axes = [0]*day_r
    for day in xrange(0,day_r):
        dfrom = now - timedelta(days=(day + 1))
        dto = now - timedelta(days=(day))
        #ol = Session.all().filter('user = ', user).filter('login > ', dfrom).filter('login < ', dto).fetch(100)
        kl = Session.all(keys_only = True).filter('user = ', user).filter('logout > ', dfrom)
        nl = Session.all(keys_only = True).filter('user =', user).filter('login < ', dto)
        kl = set(kl.fetch(kl.count()))
        nl = set(nl.fetch(nl.count()))
        ol = Session.get(nl.intersection(kl))
        sum = 0
        for o in ol:
            try:
                if o.logout > dto:
                    o.logout = dto
                if o.login < dfrom:
                    o.login = dfrom
                sum += (o.logout - o.login).seconds
            except:
                pass
        data[day_r-day-1] = sum/max_dur
        #logging.info("sum %f" % (sum/max_dur))
                
        axes[day_r-day-1] = dfrom.strftime(xlabel)

    axes = "|".join(axes)

    G = Sparkline(data, encoding='text')
    # G.scale(min(data), max(data))
    G.axes.type('xy')
    G.axes.label(0, axes)
    G.color('0077CC')
    G.size(200,40)
    G.marker('B', 'E6F2FA',0,0,0)
    G.line(1,0,0)
    G.title(caption)
    G.size((670,200))
    #G.axes.range(0, (min(data), max(data), 1))
    G.axes.range(1, (0,day_r))
    md = max(data)
    #G.axes.label(1, None, "%.1f" % md)
    G.grid(100./(day_r-1), int(md))

    return G

def activity_graph(user, year, month, day):
    dto = date(year, month, day)
    dfrom = dto - timedelta(days=7)
            #logging.info("%s %s < %s" % (user, dfrom, dto))
    sessions_less = Session.all(keys_only=True).filter("user = ", user).filter("logout > ", dfrom)
    sessions_more = Session.all(keys_only=True).filter("user = ", user).filter("login < ", dto)
    set1 = set(sessions_less.fetch(sessions_less.count()))
    set2 = set(sessions_more.fetch(sessions_more.count()))
    common = set1.intersection(set2)
            #logging.info("%s %s -> %s" % (len(set1), len(set2), len(common)))
    data = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    axes = range(24)
    axes = "|".join(["%d" % a for a in axes])
    for s in Session.get(common):
        ds = s.login.hour
        data[ds] += 1

    G = Line(data, encoding='text')
    G.scale(min(data), max(data))
    G.axes.type('xy')
    G.axes.label(0, axes)
    G.color('0077CC')
    G.marker('B', 'E6F2FA',0,0,0)
    G.line(1,0,0)
    G.title(_('Logins during last week'))
    G.size((670,200))
    G.axes.range(0, '0,23,1')
    G.axes.range(1, '0,%d,1' % max(data))
    G.axes.label(1, None, max(data))
    G.grid(100.0/23.0,50)
    return G

def week_graph(year, month, day):
    today = date.today()
    query = datetime(year, month, day)
    data = [0]*7
    axes = [0]*7
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
        #axes = "%s|" % dfrom.strftime("%a") + axes
        axes[6-day] = dfrom.strftime("%a")
    axes = "|".join(axes)

    G = Sparkline(data, encoding='text')
    G.scale(min(data), max(data))
    G.axes.type('xy')
    G.axes.label(0, axes)
    G.color('0077CC')
    G.size(200,40)
    G.marker('B', 'E6F2FA',0,0,0)
    G.line(1,0,0)
    G.title(_('Week view'))
    G.size((670,200))
    G.axes.range(1, '%d,%d,1' % (min(data), max(data)))
    G.grid(100./6,10)
    return G



