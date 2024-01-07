from django import template

register = template.Library()

@register.filter
def queryset_pagination_counter(value, arg):
    return value.start_index() + int(arg)
