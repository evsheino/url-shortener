from django.test import TestCase, Client
from urlshortener.models import ShortUrl

class ShortUrlMethodTests(TestCase):
    def test_generate_url_code_generates_correctly_for_first_object(self):
        s = ShortUrl(real_url="http://www.google.com")
        s.id = 1
        s._generate_url_code()
        self.assertEquals('b', s.url_code)

    def test_generate_url_code_generates_correctly(self):
        s = ShortUrl(real_url="http://www.google.com")
        s.id = 250
        s._generate_url_code()
        self.assertEquals('ec', s.url_code)

    def test_generate_url_code_raises_exception_if_object_has_no_id(self):
        s = ShortUrl(real_url="http://www.google.com")
        self.assertRaises(ValueError, s._generate_url_code)
        self.assertEquals('', s.url_code)

    def test_save_generates_url_code(self):
        s = ShortUrl(real_url="http://www.google.com")
        s.save()
        self.assertEquals('b', s.url_code)

        s = ShortUrl(real_url="http://www.google.com")
        s.save()
        self.assertEquals('c', s.url_code)

class ShortUrlViewTests(TestCase):
    def test_get_redirects_to_appropriate_url(self):
        url = "google.com"
        s = ShortUrl(real_url=url)
        s.save()

        client = Client()
        response = client.get('/get/' + s.url_code)

        self.assertEquals(301, response.status_code)
        self.assertEqual(url, response.url)

    def test_get_returns_404_when_url_not_found(self):
        client = Client()
        response = client.get('/get/ab2')

        self.assertEquals(404, response.status_code)

    def test_shorten_creates_new_shorturl(self):
        url = "http://www.something.com"
        client = Client()
        response = client.post('/shorten', { 'link': url })
        short = response.content

        url_obj = ShortUrl.objects.get(url_code=short)
        self.assertEquals(url, url_obj.real_url)

    def test_shorten_returns_400_if_no_link_given(self):
        url = "http://www.something.com"
        client = Client()
        response = client.post('/shorten')
        self.assertEquals(400, response.status_code)

    def test_shorten_returns_400_if_link_is_an_empty_string(self):
        url = "http://www.something.com"
        client = Client()
        response = client.post('/shorten', { 'link': '' })
        self.assertEquals(400, response.status_code)
