from django.db import models
from django.utils.translation import ugettext_lazy as _

# from newsletter.models import Subscription  # importing this causes an Internal Server Error, caused by a circular import


class Customer(models.Model):
	# This is not a django user, but a Subscription
	user = models.ForeignKey(
	    "Subscription", blank=True, null=True, verbose_name=_('user')
	)
	# purchases = models.ManyToManyField(Purchase)

	def __unicode__(self):
	    return self.user.name
