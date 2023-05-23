from django.shortcuts import render
from .forms import *
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import messages
import re
from django.core.exceptions import ObjectDoesNotExist
import random,string
import operator
from collections import Counter
from django.db.models import Count, Sum, DecimalField
from datetime import timedelta

def create_ref_code():
	return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

def is_valid_form(values):
	valid = True
	for field in values:
		if field == '':
			valid = False
	return valid

def get_popular_items():
    last_24_hours = timezone.now() - timedelta(hours=24)


    popular_items = OrderItem.objects.filter(
        ordered=True,
        order__ordered_date__gte=last_24_hours)[:6]

    items = [item.item for item in popular_items]
    item_counts = Counter(items)
    result = []
    for item, count in item_counts.most_common():
        images = ItemImage.objects.filter(item=item)
        image_url = images.first().imageURL if images.exists() else None
        temp = {
            'id': item.id,
            'name': item.name,
            'image': image_url,
            'quantity_sold': count,
            'price': item.price,
            'revenue': item.price * count
        }
        result.append(temp)
    return result

def get_new_arrivals():
    # Get the top 8 new arrivals based on the created_at field of the Item model
    items = Item.objects.filter(out_of_stock=False).order_by('-id')[:8]
    return items

def get_hot_sales():
    orders = Order.objects.filter(
        ordered=True,
        ordered_date__gte=timezone.now() - timezone.timedelta(days=30)
    )
    items = OrderItem.objects.filter(
        ordered=True,
        order__in=orders
    ).values('item').annotate(
        total_amount=Sum('quantity' * models.F('item__price'),
                         output_field=DecimalField())
    ).order_by('-total_amount')

    item_ids = [item['item'] for item in items[:8]]
    hot_sales = Item.objects.filter(id__in=item_ids)

    return hot_sales


def checkEmail(text):
	regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
	if(re.search(regex,text)):   
		return True
	return False 

def check_user_review(user, item):
	reviews = Review.objects.filter(user=user, item=item)
	if reviews.exists():
		return True
	return False