from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Retrieves an item from a dictionary or list using its key/index.
    """
    try:
        return dictionary[key]
    except (KeyError, IndexError, TypeError):
        return None
