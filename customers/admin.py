from django.contrib import admin
from django.db.models import Count

from .models import Customer


class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'number_of_products'
    )
    search_fields = (
        'user__email_field', 'user__name_field',
    )

    """ List extensions """
    def queryset(self, request):
        qs = super(CustomerAdmin, self).queryset(request)
        qs = qs.annotate(Count('products'))
        return qs

    def number_of_products(self, obj):
    	return obj.products.count()
    number_of_products.admin_order_field = 'products__count'


admin.site.register(Customer, CustomerAdmin)
