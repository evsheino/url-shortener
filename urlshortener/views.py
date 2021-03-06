from django.shortcuts import redirect, get_object_or_404
from django.http import Http404, HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from urlshortener.models import ShortUrl

@require_GET
def get(request, code):
    """
    Redirect to a previously stored url based on the short url id given.
    
    Returns a 404 error if no matching url is found for the given id.
    """

    try:
        url_obj = ShortUrl.objects.get_by_code(code)
    except ShortUrl.DoesNotExist:
        raise Http404("No matching URL")

    return redirect(url_obj.real_url, permanent=True)

@csrf_exempt
@require_POST
def shorten(request):
    """
    Saves the url given as parameter 'link' and returns its
    encoded id as plain text.

    Returns a 400 error if the 'link' parameter is omitted or
    is blank, or the URL scheme (protocol) is not allowed.
    """

    real_url = request.POST.get('link', None)
    url_obj = ShortUrl(real_url=real_url)
    try:
        url_obj.full_clean()
        url_obj.save()
    except ValidationError as e:
        return HttpResponse(e.messages, status=400)

    return HttpResponse(url_obj.url_code, content_type="text/plain")
