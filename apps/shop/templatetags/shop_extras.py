from django import template

import re

register = template.Library()

@register.filter
def get_class_name(value):
    return value.__class__.__name__

@register.filter
def is_trunc(value):
    return len(value) > 150

@register.filter
def add_float(value, num):
    return float(value) + float(num)

@register.filter
def replace_url(value):
    pattern = r'<img.+?>'
    match = re.search(pattern, value)
    repl = "<p class='img-note'>Click 'read more' to view images</p>"
    if match:
        value = re.sub(pattern, repl, value)
    return value

@register.filter
def capleading(value):
    return value.title()

@register.filter
def firstonly(value):
    return value.split(" ")[0]