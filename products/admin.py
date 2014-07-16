from django.contrib import admin
from .models import Product
from customers.models import Customer


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

    def number_of_purchases(self, obj):
    	return len(obj.customer_set.all())


admin.site.register(Product, ProductAdmin)
