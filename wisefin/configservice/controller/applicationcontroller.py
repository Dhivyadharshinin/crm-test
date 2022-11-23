import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from configservice.data.request.applicationrequest import ApplicationRequest
from configservice.data.request.entityrequest import EntityRequest
from configservice.service.applicationservice import ApplicationService
from configservice.service.entityservice import EntityService


@csrf_exempt
def application(request):
    if request.method == 'POST':
        return post_application(request)
    if request.method == 'GET':
        return fetch_application(request)
    if request.method == 'DELETE':
        return delete_application(request)


def post_application(request):
    app_json = json.loads(request.body)
    app_req = ApplicationRequest(app_json)
    service = ApplicationService()
    resp_obj = service.post(app_req)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


def fetch_application(request):
    service = ApplicationService()
    id = request.GET.get('id', None)
    if id is None:
        resp_obj = service.fetch_application_list()
    else:
        resp_obj = service.fetch_application(id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


def delete_application(request):
    service = ApplicationService()
    id = request.GET.get('id', None)
    resp_obj = service.delete_application(id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
