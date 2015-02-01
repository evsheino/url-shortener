from django.db import models, transaction
from django.core.exceptions import ValidationError
from urllib.parse import urlsplit, urlunsplit
import string

# The symbols used in the shortened url id.
ALPHABET = string.ascii_letters + string.digits
BASE = len(ALPHABET)

class ShortUrlManager(models.Manager):
    def get_by_code(self, code):
        return self.get(id=ShortUrl.decode(code))
            

class ShortUrl(models.Model):
    """
    An object that represents a shortened URL.
    """

    real_url = models.CharField(max_length=200)

    objects = ShortUrlManager()

    @property
    def url_code(self):
        """
        The short id for the URL.
        """

        try:
            return self.encode(self.id)
        except TypeError:
            # No id assigned to the instance yet.
            return None

    @staticmethod
    def encode(key):
        """
        Encode the given number (the ShortUrl object's id) with the set of symbols 
        specified in 'ALPHABET' to be used as the short id of the URL.
        """

        digits = []

        while key > 0:
            digits.append(key % BASE)
            key //= BASE

        digits.reverse()
        return ''.join([ALPHABET[x] for x in digits])

    @staticmethod
    def decode(code):
        """
        Decode a shortened url id.
        """

        # E.g. 'cLs' maps to our base 62 alphabet as [2, 37, 18]
        # -> 2 * 62**2 + 37 * 62**1 + 18 * 62**0 = 10000
        return sum([ALPHABET.index(char)*BASE**i for i, char in enumerate(code[::-1])])

    def clean(self):
        """
        Validate the URL and make sure it's handled as an absolute URL.
        """
        
        if not self.real_url:
            raise ValidationError("URL is required")

        parsed = urlsplit(self.real_url, scheme='http')

        if not parsed.scheme in ['http', 'https', 'ftp', 'ftps']:
            # These are the only schemes that Django will redirect by default
            # so allow those only for now.
            raise ValidationError("URL scheme not supported")

        self.real_url = urlunsplit(parsed)
        if parsed.netloc == '':
            # The given URL didn't include the leading '//' so it was basically parsed
            # as a relative URL. Because of this, putting it back together will introduce
            # an extra slash - get rid of it.
            self.real_url = self.real_url.replace('///', '//', 1)

