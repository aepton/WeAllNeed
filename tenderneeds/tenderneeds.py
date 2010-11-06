from django.http import HttpResponse

def current_datetime(request):
    html = "<html><body>Hello world.</body></html>"
    return HttpResponse(html)