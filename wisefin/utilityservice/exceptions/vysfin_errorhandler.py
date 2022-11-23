import json

from django.http import HttpResponse


def handler404(request, exception):
    resp = dict()
    resp['Message'] = "Resource Not Found"
    response = HttpResponse(json.dumps(resp), content_type="application/json", status=404)
    return response


def handler500(request):
    resp = dict()
    resp['Message'] = "Invalid Request"
    response = HttpResponse(json.dumps(resp), content_type="application/json", status=500)
    return response
