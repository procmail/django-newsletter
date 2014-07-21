from django.contrib import admin
from django.db.models import Count

from purchase.models import Purchase


class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        'get_product_name', 'get_price', 'amount', 'purchase_date', 'transaction_id', 'invoice_id', 'payment_status', 'currency', 'discount_code', 'country',
    )

    search_fields = (
        'transaction_id', 'invoice_id', 'discount_code',
    )

    list_filter = ('payment_status',)

    """ List extensions """
    def get_product_name(self, obj):
    	return obj.product.name

    def get_price(self, obj):
    	if obj.product.price is None:
    		return "Unset"
    	else:
    		return obj.product.price

admin.site.register(Purchase, PurchaseAdmin)
