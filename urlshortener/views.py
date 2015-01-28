from django.shortcuts import redirect, get_object_or_404
from django.http import Http404
from django.views.decorators.http import require_GET, require_POST

from urlshortener import ShortUrl

@require_GET
def get(request):
    code = request.GET.get('id', None)
    get_object_or_404(url_obj = ShortUrl.objects.get(url_code=code))

    redirect(url_obj.real_url, permanent=True)

@require_POST
def shorten(request):
    real_url = request.POST.get('link', None)

