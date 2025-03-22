from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return value

@register.filter(name='abs')
def abs_filter(value):
    """Return the absolute value of a number."""
    try:
        return abs(int(value))
    except (ValueError, TypeError):
        return value
