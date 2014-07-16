from django.contrib import admin
from .models import Customer


class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'number_of_products'
    )

    """ List extensions """
    def number_of_products(self, obj):
    	return len(obj.products.all())


admin.site.register(Customer, CustomerAdmin)
