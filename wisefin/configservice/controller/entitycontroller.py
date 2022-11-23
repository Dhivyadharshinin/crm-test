import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from configservice.data.request.entityrequest import EntityRequest
from configservice.service.entityservice import EntityService


@csrf_exempt
def entity(request):
    if request.method == 'POST':
        return post_entity(request)
    if request.method == 'GET':
        return fetch_entity(request)
    if request.method == 'DELETE':
        return delete_entity(request)


def post_entity(request):
    entity_json = json.loads(request.body)
    entity_req = EntityRequest(entity_json)
    service = EntityService()
    resp_obj = service.post(entity_req)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


def fetch_entity(request):
    service = EntityService()
    id = request.GET.get('id', None)
    if id is None:
        resp_obj = service.fetch_entity_list()
    else:
        resp_obj = service.fetch_entity(id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


def delete_entity(request):
    service = EntityService()
    id = request.GET.get('id', None)
    resp_obj = service.delete_entity(id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def entity_search(request):
    name = request.GET.get('query', None)
    entity_service = EntityService()
    resp_data = entity_service.search_entity(name)
    response = HttpResponse(resp_data.get(), content_type="application/json")
    return response
