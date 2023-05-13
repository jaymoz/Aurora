from django import template
from app.models import *

register = template.Library()

@register.filter
def cart_total_price(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, ordered=False)
        if qs.exists():
            return qs[0].get_total()
    return 0