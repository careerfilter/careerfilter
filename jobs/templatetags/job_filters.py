from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to get an item from a dictionary using a key.
    Usage: {{ my_dict|get_item:key }}
    """
    return dictionary.get(key)

@register.filter
def get_item_by_value(dictionary, value):
    """
    Alternative: Get dictionary key by value (if needed)
    """
    for k, v in dictionary.items():
        if v == value:
            return dictionary.get(k)
    return None