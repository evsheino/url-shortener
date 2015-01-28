from django.db import models
import string

ALPHABET = string.ascii_letters + string.digits
BASE = len(ALPHABET)

class ShortUrl(models.Model):
    """
    An object that represents a shortened url
    """

    real_url = models.CharField(max_length=200)
    url_code = models.CharField(max_length=20)

    def save(self, *args, **kwargs):
        """
        Override the save method in order to set the url_code attribute
        based on the model object's id
        """

        # Save first so that an id is assigned
        super(ShortUrl, self).save(*args, **kwargs)

        if not self.url_code:
            self._generate_url_code()
            super(ShortUrl, self).save(*args, **kwargs)

    def _generate_url_code(self):
        """
        Set the url_code attribute by generating a string based
        on the id of this object.
        """

        digits = []

        number = self.id
        while number > 0:
            digits.append(number % BASE)
            number //= BASE

        digits.reverse()
        self.url_code = ''.join([ALPHABET[x] for x in digits])
