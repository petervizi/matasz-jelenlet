##
# Members functionality
#

from django.http import *
from django.core.urlresolvers import reverse
from django.template import Context, loader
from django.utils.translation import ugettext as _
from django.utils import simplejson
from django.core import serializers

from jelenlet.models import *
from jelenlet.graphs import *

from google.appengine.ext import db
from google.appengine.api import memcache

from datetime import datetime, timedelta, date
from GChartWrapper import *
import math
import logging
import httplib
import xml.dom.minidom
import md5

def members(request, page):
    t = loader.get_template("members.html")
    members_per_page = 10
    if page:
        page = int(page)
    else:
        page = 0
    if 'members_per_page' in request.COOKIES:
        members_per_page = int(request.COOKIES['members_per_page'])
    logging.info('members_per_page: %d' % members_per_page)
    member_c = Member.all().count()
    count = math.ceil(member_c / members_per_page)
    next = 0
    prev = -1
    if page < count:
        next = page + 1
    if page > 0:
        prev = page - 1
    prange = xrange(page - 3, page + 4)
    prange = [p for p in prange if p > 0 and p <= count]
    members = Member.all().order('name').fetch(members_per_page, page*members_per_page)
    for member in members:
        s_url = "/v1/feeds/citizens/%d" % member.id
        conn.request("GET", s_url)
        r1 = conn.getresponse()
        if r1.status == 200:
            doc = xml.dom.minidom.parse(r1)
            member.strength = doc.getElementsByTagName('strength')[0].firstChild.data
            member.rank = doc.getElementsByTagName('military-rank')[0].firstChild.data
            member.damage = doc.getElementsByTagName('damage')[0].firstChild.data
            member.level = doc.getElementsByTagName('level')[0].firstChild.data
            member.region = doc.getElementsByTagName('region')[0].firstChild.data.lower()
            member.sex = doc.getElementsByTagName('sex')[0].firstChild.data.lower()
            member.wellness = 100.0 - float(doc.getElementsByTagName('wellness')[0].firstChild.data.lower())
    c = Context({
            'title': _('Members'),
            'members': members,
            'page': page,
            'prev': prev,
            'next': next,
            'last': int(count),
            'prange': prange,
            'members_per_page': members_per_page,
            })    
    return HttpResponse(t.render(c))

conn = httplib.HTTPConnection("api.erepublik.com")

def member_add(request):
    logging.info("method: %s" % request.method)
    if request.method == 'POST':
        name = request.POST.get('name', '').lower()
        try:
            id = int(request.POST.get('id', 0))
        except:
            id = 0
        logging.info("name %s id %d" % (name, id))
        # check if already in db
        member = Member.all().filter('name = ', name).get()
        if member:
            return HttpResponse(_("%(name)s is already member.") % {'name': name.capitalize()})
        if id:
            s_url = "/v1/feeds/citizens/%d" % id
        else:
            s_url = "/v1/feeds/citizens/%s?by_username=true" % name
        logging.info("s_url %s" % s_url)
#        if not conn:
#            logging.info("new connection")
#            conn = httplib.HTTPConnection("api.erepublik.com")
        conn.request("GET", s_url)
        r1 = conn.getresponse()
        if r1.status == 200:
            member = Member()
            member.name = name
            doc = xml.dom.minidom.parse(r1)
            id = doc.getElementsByTagName('id')
            id = int(id[len(id)-1].firstChild.data)
            member.id = id
            db = doc.getElementsByTagName('date-of-birth')[0].firstChild.data
            db = datetime.strptime(db, "%Y-%m-%d %H:%M:%S %Z")
            member.avatar = "%s/%s" % (db.strftime("%Y/%m/%d"),
                                       md5.md5("%s" % member.id).hexdigest())            
            member.put()
            return HttpResponse(_("New member %(name)s %(url)s") % {'name': name.capitalize(),
                                                                    'url': "http://www.erepublik.com/en/citizen/profile/%d" % id})
        else:
            return HttpResponse(_("Citizen %(name)s not found.") % {'name': name})
    raise Http404

def member_remove(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').lower()
        member = Member.all().filter('name = ', name).get()
        if member:
            member.delete()
            return HttpResponse(_("%(name)s removed.") % {'name': name.capitalize()})
        else:
            return HttpResponse(_("No such member."))
    else:
        raise Http404
