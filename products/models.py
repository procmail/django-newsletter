from django.db import models


class Product(models.Model):
	name = models.CharField(max_length=500)
	price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
	file = models.FileField(upload_to='/', null=True, blank=True)

	def __unicode__(self):
	    return self.name

