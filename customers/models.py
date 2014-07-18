from django.db import models
from django.utils.translation import ugettext_lazy as _

from products.models import Product
from newsletter.models import Subscription, Submission, Blacklist


class Customer(models.Model):
	# This is not a django user, but a Subscription
	user = models.ForeignKey(
	    Subscription, blank=True, null=True, verbose_name=_('user')
	)
	products = models.ManyToManyField(Product)

	def __unicode__(self):
	    return self.user.name

