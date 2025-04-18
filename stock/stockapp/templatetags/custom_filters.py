from django import template

register = template.Library()

@register.filter
def get_item(lst, index):
    """Returns the item at the given index in a list."""
    try:
        return lst[int(index)]
    except (IndexError, ValueError, TypeError):
        return None

@register.filter
def make_range(value):
    """Creates a range from 0 to value (non-inclusive), for loop iteration."""
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return range(0)
