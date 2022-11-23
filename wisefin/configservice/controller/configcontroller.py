import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from configservice.service.configservice import ConfigService


@csrf_exempt
def schema(request):
    if request.method == 'POST':
        return post_schema(request)
    elif request.method == 'GET':
        return fetch_schema(request)
    elif request.method == 'DELETE':
        return delete_schema(request)


def post_schema(request):
    schema_json = json.loads(request.body)
    service = ConfigService()
    resp_obj = service.post_schema(schema_json)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


def fetch_schema(request):
    scope = request.scope
    service = ConfigService()
    resp_obj = service.fetch_schema()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


def delete_schema(request):
    scope = request.scope
    service = ConfigService()
    id = request.GET.get('id', None)
    resp_obj = service.delete_schema(id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
def configure(request):
    config_json = json.loads(request.body)
    app_id = config_json['application_id']
    entity_id = config_json['entity_id']
    schema_id = config_json['schema_id']
    scope = request.scope
    service = ConfigService()
    resp_obj = service.reserve(app_id, entity_id, schema_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
def test(request):
    scope = request.scope
    service = ConfigService()
    resp_obj = service.set_config(request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
