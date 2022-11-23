import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from masterservice.service.addressservice import AddressService
from masterservice.data.request.addressrequest import AddressRequest

from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
#master_id
def address(request,address_id):
    if request.method == 'POST':
        user_id = request.employee_id
        scope = request.scope
        address_service = AddressService(scope)
        address_data = json.loads(request.body)
        address_obj=AddressRequest(address_data)
        resp_obj = address_service.create_address( address_obj, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_address_list(request,address_id)


def fetch_address_list(request, address_id):
    user_id = request.employee_id
    scope = request.scope
    address_service = AddressService(scope)
    resp_obj = address_service.fetch_address_list(user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_address(request, address_id):
    if request.method == 'GET':
        user_id = request.employee_id
        scope = request.scope
        address_service = AddressService(scope)
        resp_obj = address_service.fetch_address(address_id, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_address(request,address_id)


def delete_address(request, address_id):
    user_id = request.employee_id
    scope = request.scope
    address_service = AddressService(scope)
    resp_obj = address_service.delete_address(address_id, user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

