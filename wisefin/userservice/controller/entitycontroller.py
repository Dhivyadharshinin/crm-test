import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.service.entityservice import EntityService
from userservice.data.request.entityrequest import EntityRequest


# @csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_entity(request):
    if request.method == 'POST':
        scope=request.scope
        entity_service = EntityService(scope)
        entity_data = json.loads(request.body)
        user_id = request.user.id
        entity_obj = EntityRequest(entity_data)
        resp_obj = entity_service.create_entity(entity_obj, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_entity_list(request)


def fetch_entity_list(request):
    scope=request.scope
    entity_service = EntityService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    user_id = request.user.id
    resp_obj = entity_service.fetch_entity_list(request,vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def entity_activate_inactivate(request):
    if request.method == 'POST':
        scope=request.scope
        entity_service = EntityService(scope)
        entity_obj = json.loads(request.body)
        ent_obj = EntityRequest(entity_obj)
        resp_obj = entity_service.entity_activate_inactivate(request,ent_obj)
        # print(resp_obj.get())
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
