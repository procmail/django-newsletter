from django.db import models


class Purchase(models.Model):
	product = models.ForeignKey('product.Product')
	customer = models.ForeignKey('customer.Customer')
	purchase_date = models.DateField(auto_now_add=True)
	transaction_id = models.CharField(max_length=500)
	invoice_id = models.CharField(max_length=500)
	payment_status = models.CharField(max_length=100)
	country = models.CharField(max_length=200)
	discount_code = models.CharField(max_length=500)
	currency = models.CharField(max_length=10)
	amount = models.CharField(max_length=100)

	def __unicode__(self):
	    return self.product.name
