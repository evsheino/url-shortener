from django.test import TestCase, Client
from urlshortener.models import ShortUrl

class ShortUrlModelTests(TestCase):
    def test_encode_generates_correctly(self):
        self.assertEquals('ec', ShortUrl.encode(250))
        self.assertEquals('fsr', ShortUrl.encode(20353))
        self.assertEquals('k4U8YJ', ShortUrl.encode(9999999999))

    def test_decode_works(self):
        self.assertEquals(250, ShortUrl.decode('ec'))
        self.assertEquals(20353, ShortUrl.decode('fsr'))
        self.assertEquals(9999999999, ShortUrl.decode('k4U8YJ'))


class ShortUrlManagerTests(TestCase):
    def test_get_by_url_code_works(self):
        s = ShortUrl(real_url="http://www.google.com")
        s.save()
        self.assertEquals(ShortUrl.objects.get_by_code('b'), s)


class ShortUrlViewTests(TestCase):
    def test_get_redirects_to_appropriate_url(self):
        url = "http://www.google.com"
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

    def test_get_returns_404_when_no_parameter_given(self):
        client = Client()
        response = client.get('/get')

        self.assertEquals(404, response.status_code)

    def test_shorten_creates_new_shorturl(self):
        url = "http://www.something.com"
        client = Client()
        response = client.post('/shorten', { 'link': url })
        short = response.content.decode("utf-8")

        url_obj = ShortUrl.objects.get_by_code(short)
        self.assertEquals(url, url_obj.real_url)

    def test_shorten_accepted_schemes(self):
        schemes = ["http://", "https://", "ftp://", "ftps://"]
        url = "www.something.com"
        client = Client()
        for scheme in schemes:
            full_url = scheme + url
            response = client.post('/shorten', { 'link': full_url })
            short = response.content.decode("utf-8")

            url_obj = ShortUrl.objects.get_by_code(short)
            self.assertEquals(full_url, url_obj.real_url)

    def test_shorten_returns_400_when_scheme_not_acceptable(self):
        url = "foo://www.something.com"
        client = Client()
        response = client.post('/shorten', { 'link': url })

        self.assertEquals(400, response.status_code)

    def test_shorten_fixes_url_when_not_fully_qualified(self):
        urls = ["www.something.com", "something.com", "something.com:80"]
        client = Client()
        for url in urls:
            response = client.post('/shorten', { 'link': url })
            short = response.content.decode("utf-8")

            url_obj = ShortUrl.objects.get_by_code(short)
            self.assertEquals("http://" + url, url_obj.real_url)

    def test_shorten_returns_400_if_no_link_given(self):
        client = Client()
        response = client.post('/shorten')
        self.assertEquals(400, response.status_code)

    def test_shorten_returns_400_if_link_is_an_empty_string(self):
        client = Client()
        response = client.post('/shorten', { 'link': '' })
        self.assertEquals(400, response.status_code)
