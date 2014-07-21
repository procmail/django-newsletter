from django.contrib import admin
from django.db.models import Count

from .models import Product
from purchase.models import Purchase


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'get_price', 'number_of_purchases'
    )

    """ List extensions """
    def get_price(self, obj):
    	if obj.price is None:
    		return ""
    	else:
    		return obj.price

    def queryset(self, request):
        qs = super(ProductAdmin, self).queryset(request)
        qs = qs.annotate(Count('purchase'))
        return qs

    def number_of_purchases(self, obj):
    	return obj.purchase_set.count()
    number_of_purchases.admin_order_field = 'purchase__count'


admin.site.register(Product, ProductAdmin)
