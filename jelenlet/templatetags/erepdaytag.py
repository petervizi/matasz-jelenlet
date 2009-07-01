from django import template
from datetime import date
from jelenlet.tz import utc, erep, erepstart

erepstart_d = date(erepstart.year, erepstart.month, erepstart.day)
register = template.Library()
@register.filter
def erepday(date):
    '''date is a date in erep timezone'''
    diff = date - erepstart_d
    return diff.days

erepday.is_safe = True
    
