from django import template

register = template.Library()

@register.filter
def currency(value):
    try:
        return "${:,.2f}".format(value)
    except(ValueError, TypeError):
        return value