import logging

logger = logging.getLogger(__name__)

from django import forms

from django.core.exceptions import ValidationError

from django.core.validators import validate_email

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from .models import Newsletter, Blacklist
from .admin_forms import check_name, check_email


def check_if_email_is_already_blacklisted(newsletter, email):
    # returns the email if the user isn't already blacklisted.
    if newsletter:
        qs = Blacklist.objects.filter(
            newsletter_id=newsletter.id,
            email_field__exact=email)
    else:
        qs = Blacklist.objects.filter(
            email_field__exact=email)

    if qs.count():
        return None

    return email


def blacklist_parse_csv(myfile, newsletter, ignore_errors=False):
    from newsletter.addressimport.csv_util import UnicodeReader
    import codecs
    import csv

    # Detect encoding
    from chardet.universaldetector import UniversalDetector

    detector = UniversalDetector()

    for line in myfile.readlines():
        detector.feed(line)
        if detector.done:
            break

    detector.close()
    charset = detector.result['encoding']

    # Reset the file index
    myfile.seek(0)

    # Attempt to detect the dialect
    encodedfile = codecs.EncodedFile(myfile, charset)
    dialect = csv.Sniffer().sniff(encodedfile.read(1024))

    # Reset the file index
    myfile.seek(0)

    logger.info('Detected encoding %s and dialect %s for CSV file',
                charset, dialect)

    myreader = UnicodeReader(myfile, dialect=dialect, encoding=charset)

    firstrow = myreader.next()

    # Find name column
    colnum = 0
    namecol = None
    for column in firstrow:
        if "name" in column.lower() or ugettext("name") in column.lower():
            namecol = colnum

            if "display" in column.lower() or \
                    ugettext("display") in column.lower():
                break

        colnum += 1

    if namecol is None:
        raise forms.ValidationError(_(
            "Name column not found. The name of this column should be "
            "either 'name' or '%s'.") % ugettext("name")
        )

    logger.debug("Name column found: '%s'", firstrow[namecol])

    # Find email column
    colnum = 0
    mailcol = None
    for column in firstrow:
        if 'email' in column.lower() or \
                'e-mail' in column.lower() or \
                ugettext("e-mail") in column.lower():

            mailcol = colnum

            break

        colnum += 1

    if mailcol is None:
        raise forms.ValidationError(_(
            "E-mail column not found. The name of this column should be "
            "either 'email', 'e-mail' or '%(email)s'.") %
            {'email': ugettext("e-mail")}
        )

    logger.debug("E-mail column found: '%s'", firstrow[mailcol])

    if namecol == mailcol:
        raise forms.ValidationError(
            _(
                "Could not properly determine the proper columns in the "
                "CSV-file. There should be a field called 'name' or "
                "'%(name)s' and one called 'e-mail' or '%(e-mail)s'."
            ) % {
                "name": _("name"),
                "e-mail": _("e-mail")
            }
        )

    logger.debug('Extracting data.')

    addresses = {}
    for row in myreader:
        if not max(namecol, mailcol) < len(row):
            logger.warn("Column count does not match for row number %d",
                        myreader.line_num, extra=dict(data={'row': row}))

            if ignore_errors:
                # Skip this record
                continue
            else:
                raise forms.ValidationError(_(
                    "Row with content '%(row)s' does not contain a name and "
                    "email field.") % {'row': row}
                )

        name = check_name(row[namecol], ignore_errors)
        email = check_email(row[mailcol], ignore_errors)

        logger.debug("Going to add %s <%s>", name, email)

        try:
            validate_email(email)
            addr = check_if_email_is_already_blacklisted(newsletter, email)
        except ValidationError:
            if ignore_errors:
                logger.warn(
                    "Entry '%s' at line %d does not contain a valid "
                    "e-mail address.",
                    name, myreader.line_num, extra=dict(data={'row': row}))
            else:
                raise forms.ValidationError(_(
                    "Entry '%s' does not contain a valid "
                    "e-mail address.") % name
                )

        if addr:
            if email in addresses:
                logger.warn(
                    "Entry '%s' at line %d contains a "
                    "duplicate entry for '%s'",
                    name, myreader.line_num, email,
                    extra=dict(data={'row': row}))

                if not ignore_errors:
                    raise forms.ValidationError(_(
                        "The address file contains duplicate entries "
                        "for '%s'.") % email)

            addresses.update({addr: name})
        else:
            logger.warn(
                "Entry '%s' at line %d is already subscribed to "
                "with email '%s'",
                name, myreader.line_num, email, extra=dict(data={'row': row}))

            if not ignore_errors:
                raise forms.ValidationError(
                    _("Some entries are already subscribed to."))

    return addresses


class BlacklistImportForm(forms.Form):

    def clean(self):
        # If there are validation errors earlier on, don't bother.
        if not ('address_file' in self.cleaned_data and
                'ignore_errors' in self.cleaned_data):
            return self.cleaned_data

        ignore_errors = self.cleaned_data['ignore_errors']
        newsletter = self.cleaned_data['newsletter']

        myfield = self.base_fields['address_file']
        myvalue = myfield.widget.value_from_datadict(
            self.data, self.files, self.add_prefix('address_file'))

        content_type = myvalue.content_type
        allowed_types = ('text/plain', 'application/octet-stream',
                         'text/vcard', 'text/directory', 'text/x-vcard',
                         'application/vnd.ms-excel',
                         'text/comma-separated-values', 'text/csv',
                         'application/csv', 'application/excel',
                         'application/vnd.msexcel', 'text/anytext')
        if content_type not in allowed_types:
            raise forms.ValidationError(_(
                "File type '%s' was not recognized.") % content_type)

        self.addresses = []

        ext = myvalue.name.rsplit('.', 1)[-1].lower()
        if ext == 'csv':
            self.addresses = blacklist_parse_csv(
                myvalue.file, newsletter, ignore_errors)

        else:
            raise forms.ValidationError(
                _("File extention '%s' was not recognized.") % ext)

        if len(self.addresses) == 0:
            raise forms.ValidationError(
                _("No entries could found in this file."))

        return self.cleaned_data

    def get_addresses(self):
        if hasattr(self, 'addresses'):
            logger.debug('Getting addresses: %s', self.addresses)
            return self.addresses
        else:
            return {}

    def get_newsletter(self):
        if self.cleaned_data['newsletter']:
            return self.cleaned_data['newsletter'].id
        else:
            return None

    newsletter = forms.ModelChoiceField(
        label=_("Newsletter"),
        queryset=Newsletter.objects.all(),
        initial=Newsletter.get_default_id(),
        required=False)
    address_file = forms.FileField(label=_("Address file"))
    ignore_errors = forms.BooleanField(
        label=_("Ignore non-fatal errors"),
        initial=False, required=False)


class BlacklistAdminForm(forms.ModelForm):

    class Meta:
        model = Blacklist

    def clean_email_field(self):
        data = self.cleaned_data['email_field']
        if self.cleaned_data['user'] and data:
            raise forms.ValidationError(_(
                'If a user has been selected this field '
                'should remain empty.'))
        return data

    def clean_name_field(self):
        data = self.cleaned_data['name_field']
        if self.cleaned_data['user'] and data:
            raise forms.ValidationError(_(
                'If a user has been selected '
                'this field should remain empty.'))
        return data

    def clean(self):
        cleaned_data = super(BlacklistAdminForm, self).clean()
        if not (cleaned_data.get('user', None) or
                cleaned_data.get('email_field', None)):

            raise forms.ValidationError(_(
                'Either a user must be selected or an email address must '
                'be specified.')
            )
        return cleaned_data
