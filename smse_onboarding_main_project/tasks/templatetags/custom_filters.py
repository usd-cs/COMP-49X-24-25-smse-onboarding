from django import template

register = template.Library()

@register.filter
def ends_with(value, arg):
    return value.endswith(arg)
