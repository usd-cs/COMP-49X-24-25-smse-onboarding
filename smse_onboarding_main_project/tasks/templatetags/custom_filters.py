from django import template

register = template.Library()

@register.filter
def ends_with(value, arg):
    return value.endswith(arg)

@register.filter
def absolute(value):
    """Returns the absolute value"""
    try:
        return abs(int(value))
    except (ValueError, TypeError):
        return value
