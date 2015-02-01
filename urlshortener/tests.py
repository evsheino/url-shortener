from django.test import TestCase, Client
from urlshortener.models import ShortUrl

class ShortUrlModelTests(TestCase):
    def test_generate_url_code_generates_correctly(self):
        self.assertEquals('ec', ShortUrl.generate_url_code(250))
        self.assertEquals('fsr', ShortUrl.generate_url_code(20353))
        self.assertEquals('k4U8YJ', ShortUrl.generate_url_code(9999999999))

    def test_save_instance_generates_correctly_for_first_object(self):
        s = ShortUrl(real_url="http://www.google.com")
        s.id = 1
        s.save()
        self.assertEquals('b', s.url_code)

    def test_save_instance_generates_url_code(self):
        s = ShortUrl(real_url="http://www.google.com")
        s.id = 2
        s.save()
        self.assertEquals('c', s.url_code)

        s = ShortUrl(real_url="http://www.google.com")
        s.id = 3
        s.save()
        self.assertEquals('d', s.url_code)


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

    def test_shorten_creates_new_shorturl(self):
        url = "http://www.something.com"
        client = Client()
        response = client.post('/shorten', { 'link': url })
        short = response.content

        url_obj = ShortUrl.objects.get(url_code=short)
        self.assertEquals(url, url_obj.real_url)

    def test_shorten_accepted_schemes(self):
        schemes = ["http://", "https://", "ftp://"]
        url = "www.something.com"
        client = Client()
        for scheme in schemes:
            full_url = scheme + url
            response = client.post('/shorten', { 'link': full_url })
            short = response.content

            url_obj = ShortUrl.objects.get(url_code=short)
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
            short = response.content

            url_obj = ShortUrl.objects.get(url_code=short)
            self.assertEquals("http://" + url, url_obj.real_url)

    def test_shorten_returns_400_if_no_link_given(self):
        client = Client()
        response = client.post('/shorten')
        self.assertEquals(400, response.status_code)

    def test_shorten_returns_400_if_link_is_an_empty_string(self):
        client = Client()
        response = client.post('/shorten', { 'link': '' })
        self.assertEquals(400, response.status_code)
