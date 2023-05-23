from django.contrib import admin
from .models import *

def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_granted=True)

make_refund_accepted.short_description = 'Update Order To refund granted'

def order_completed(modeladmin,request,queryset):
    queryset.update(completed=True)

order_completed.short_description = 'Order Completed'

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'item',
                    'quantity',
                    'ordered'
    ]

    list_display_links = [
                'user',
                'item'

    ]

    list_filter = ['user',
                    'item',
                    'quantity',
                    'ordered'
                    ]

    search_fields = [
            'user__username',
            'item__name'

    ]

class OrderAdmin(admin.ModelAdmin):
    list_display = [ 'user',
                    'id',
                    'ordered',
                    'status',
                    'house_address',
                    'city',
                    'phone',
                    'ordered_date'

 
    ]

    list_editable = ['status']

    list_display_links = [
                'user',
                'id',

    ]

    list_filter = [
                    'ordered',
                    'status',
                    'user',
                    'ordered_date'
                    ]

    search_fields = [
            'id',
            'user__username',
            'ref_code'
    ]
    actions = [make_refund_accepted, order_completed]

admin.site.index_title = "AURORA"
admin.site.site_header = "AURORA SUPER ADMIN DASHBOARD"
admin.site.register(Category)
admin.site.register(Item)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Contact)
admin.site.register(ItemColor)
admin.site.register(Size)
admin.site.register(Brand)
admin.site.register(Address)
admin.site.register(Review)
admin.site.register(Wishlist)
admin.site.register(ItemImage)