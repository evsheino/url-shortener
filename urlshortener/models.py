from django.db import models
from django.core.exceptions import ValidationError
from urllib.parse import urlsplit, urlunsplit
import string

ALPHABET = string.ascii_letters + string.digits
BASE = len(ALPHABET)

class ShortUrl(models.Model):
    """
    An object that represents a shortened url
    """

    real_url = models.CharField(max_length=200)
    # Allowing url_code to be blank because the url_code is based
    # on the object's id which is not available before the object
    # has been saved for the first time.
    url_code = models.CharField(max_length=20, blank=True)

    @staticmethod
    def generate_url_code(key):
        """
        Generate a short code for a URL from a number (the ShortUrl object's id).
        """

        digits = []

        while key > 0:
            digits.append(key % BASE)
            key //= BASE

        digits.reverse()
        return ''.join([ALPHABET[x] for x in digits])

    def save(self, *args, **kwargs):
        """
        Override the save method in order to set the url_code attribute
        based on the model object's id
        """

        # Save first so that an id is assigned
        super(ShortUrl, self).save(*args, **kwargs)

        if not self.url_code:
            self.url_code = self.generate_url_code(self.id)
            super(ShortUrl, self).save(*args, **kwargs)

    def clean(self):
        """
        Validate the URL and make sure it's handled as an absolute URL.
        """
        
        if not self.real_url:
            raise ValidationError("URL is required")

        parsed = urlsplit(self.real_url, scheme='http')

        if not parsed.scheme in ['http', 'https', 'ftp']:
            # These are the only schemes that Django will redirect by default and they
            # should suffice.
            raise ValidationError("URL scheme not supported")

        self.real_url = urlunsplit(parsed)
        if parsed.netloc == '':
            # The given URL didn't include the leading '//' so it was basically parsed
            # as a relative URL. Because of this, putting it back together will introduce
            # an extra slash - get rid of it.
            self.real_url = self.real_url.replace('///', '//', 1)

