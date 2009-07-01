from django import template
from django.utils.translation import gettext_lazy as _

register = template.Library()

def do_hash(h, key):
    if key in h:
        return h[key]
    else:
        return None

register.tag('hash', do_hash)
