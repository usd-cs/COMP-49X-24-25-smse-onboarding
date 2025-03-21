from django import template

register = template.Library()

@register.filter
def absolute(value):
    """Return the absolute value"""
    return abs(value)
