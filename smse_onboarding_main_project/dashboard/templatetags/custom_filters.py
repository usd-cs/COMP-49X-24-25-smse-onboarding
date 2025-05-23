from django import template

register = template.Library()

@register.filter
def absolute(value):
    """Return the absolute value"""
    return abs(value)

@register.filter
def completed_tasks(tasks):
    """Return only completed tasks"""
    return [task for task in tasks if task.is_completed_by_faculty]

@register.filter
def upcoming_tasks(tasks):
    """Return only upcoming (not completed) tasks"""
    return [task for task in tasks if not task.is_completed_by_faculty]
