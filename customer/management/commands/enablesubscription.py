from optparse import make_option
import sys

from django.core.management.base import BaseCommand, CommandError

from customer.models import Customer
from product.models import Product
from purchase.models import Purchase

from newsletter.models import Subscription, Newsletter

"""
Sets all the subscriptions in the newsletter to Unsubscribe, then reads for a text file (contains 1 email address per line) and enables each email's subscription one by one.
"""
class Command(BaseCommand):
    help = 'Imports customer from the e-junkie sales export file'
    args = '<customer_data_file1 customer_data_file2 ...>'

    option_list = BaseCommand.option_list + (
        make_option(
            '-n',
            '--newsletter',
            action='store',
            dest='newsletter',
            default=1,
            help='Specify the newsletter ID with which to associated the subscription users to'
            ),
        make_option(
            '-f',
            '--filename',
            action='store',
            dest='filename',
            default="",
            help='Specify file to read the subscription information from'
            ),
        )

    def percentage(self, part, whole):
      return 100 * float(part)/float(whole)

    def handle(self, *args, **options):
        newsletter_id = options['newsletter']

        Subscription.objects.update(subscribed=False)
        Subscription.objects.update(unsubscribed=True)

        try:
            newsletter = Newsletter.objects.get(pk=newsletter_id)
        except Exception, e:
            print "Error: the newsletter ID of %s isn't found" % newsletter_id
            print str(e)
            sys.exit()
        with open(options['filename'], 'rU') as f:
            reader = f.readlines()

            subscriptions_enabled = 0
            for index, email in enumerate(reader):
                email = email.strip().lower()
                sys.stdout.write("Processing line %d of %d (%d%%). \r" % (index, len(reader), self.percentage(index, len(reader)) ))
                sys.stdout.flush()

                try:
                    subscription = Subscription.objects.get(email_field=email)
                    subscription.subscribed = True
                    subscription.unsubscribed = False
                    subscription.save()
                    subscriptions_enabled += 1
                except Exception, e:
                    print "Error: can't enable subscription for %s" % email
                    print str(e)

            sys.stdout.write("Total number of subscriptions enabled = %d\n" % subscriptions_enabled)


