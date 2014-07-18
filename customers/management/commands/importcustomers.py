import csv
from optparse import make_option
import sys

from django.core.management.base import BaseCommand, CommandError
from customers.models import Customer
from products.models import Product
from newsletter.models import Subscription, Newsletter


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
        try:
            newsletter = Newsletter.objects.get(pk=newsletter_id)
        except:
            print "Error: the newsletter ID of %s isn't found" % newsletter_id
            sys.exit()
        with open(options['filename']) as f:
            reader = csv.reader(f, delimiter="\t")
            data_list = list(reader)
            # First line contains:
            # Payment Date (MST)    Processed by E-j (MST)  Transaction ID  Payment Processor   E-j Internal Txn ID Payment Status  First Name  Last Name   Payer E-mail    Billing Info    Payer Phone Card Last 4 Card Type   Payer IP    Passed Custom Param.    Discount Codes  Invoice Shipping Info   Shipping Phone  Shipping    Tax eBay Auction Buyer ID   Affiliate E-mail    Affiliate Name  Affiliate ID    Affiliate Share (common for txn)    Currency    Item Name   Variations/Variants Item Number SKU Quantity    Amount  Affiliate Share (per item)  Download Info   Key/Code (if any)   eBay Auction ID Buyer Country
            first_name_col = data_list[0].index('First Name')
            last_name_col = data_list[0].index('Last Name')
            email_col = data_list[0].index('Payer E-mail')
            item_name_col = data_list[0].index('Item Name')

            lines_scanned = 0
            new_customers_added = 0
            new_subscriptions_added = 0
            new_products_added = 0

            for index, sale_line in enumerate(data_list):
                sys.stdout.write("Processing line %d of %d (%d%%). C/S/P: %d/%d/%d \r" % (index, len(data_list), self.percentage(index, len(data_list)), new_customers_added, new_subscriptions_added, new_products_added) )
                sys.stdout.flush()
                if sale_line[email_col] == "Payer E-mail" and sale_line[item_name_col] == "Item Name":
                    continue
                lines_scanned += 1
                name = sale_line[first_name_col] + " " + sale_line[last_name_col]
                # ignore portions of a string that it can't convert to utf-8
                name = name.decode('utf-8', 'ignore').strip().title()
                email = sale_line[email_col].strip().lower()
                subscription_user, subcription_created = Subscription.objects.get_or_create(
                    email_field=email,
                    newsletter=newsletter,
                     defaults={
                     'name_field': name,
                     'subscribed': True,
                     'email_field': email
                     })
                # subscription_user.save()
                if subcription_created:
                    new_subscriptions_added += 1

                product_name = sale_line[item_name_col].strip().title()
                product, product_created = Product.objects.get_or_create(
                    name=product_name
                    )
                if product_created:
                    new_products_added += 1

                customer_user, customer_created = Customer.objects.get_or_create(
                    user=subscription_user
                    )
                if customer_created:
                    new_customers_added += 1
                customer_user.products.add(product)
                customer_user.save()

            sys.stdout.write("Total number of lines scanned = %d\nNew customers added = %d\nNew subscriptions added = %d\nNew products added = %d\n" % (lines_scanned - 1, new_customers_added, new_subscriptions_added, new_products_added))


