from django.db import models
from products.models import Product
from newsletter.models import Subscription, Submission, Blacklist
from django.utils.translation import ugettext_lazy as _


class Customer(models.Model):
	user = models.ForeignKey(
	    Subscription, blank=True, null=True, verbose_name=_('user')
	)
	products = models.ManyToManyField(Product)

	def __unicode__(self):
	    return self.user.name

