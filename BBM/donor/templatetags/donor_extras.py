from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divisibleby(value, arg):
    """Divides the value by the argument"""
    try:
        return int(value) / int(arg)
    except (ValueError, TypeError):
        return 0
