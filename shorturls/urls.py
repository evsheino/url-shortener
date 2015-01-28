from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^get/(\w)$', 'urlshortener.views.get', name='get'),
    url(r'^shorten$', 'urlshortener.views.shorten', name='shorten'),
)
