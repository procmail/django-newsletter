from django.contrib import admin
from django.db.models import Count

from .models import Product


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
        qs = qs.annotate(Count('customer'))
        return qs

    def number_of_purchases(self, obj):
    	return obj.customer_set.count()
    number_of_purchases.admin_order_field = 'customer__count'


admin.site.register(Product, ProductAdmin)
