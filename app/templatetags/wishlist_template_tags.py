from django import template
from app.models import *

register = template.Library()

@register.filter
def wishlist_item_count(user):
    if user.is_authenticated:
        qs = Wishlist.objects.filter(user=user)
        if qs.exists():
            return qs[0].items.count()
    return 0