import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from userservice.service.employeeservice import EmployeeService
from vendorservice.data.request.directorrequest import DirectorRequest
from vendorservice.service.directorservice import DirectorService
from nwisefin.settings import logger
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def director(request, vendor_id):
    if request.method == 'POST':
        employee_id = request.employee_id
        scope = request.scope
        bulk = request.GET.get('bulk', False)
        director_service = DirectorService(scope)
        director_json = json.loads(request.body)
        director_obj = DirectorRequest(director_json)
        director_obj.set_vendor_id(vendor_id)
        resp_obj = director_service.create_director(vendor_id, director_obj, employee_id, bulk)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_director_list(request, vendor_id)


def fetch_director_list(request, vendor_id):
    employee_id = request.employee_id
    scope = request.scope
    director_service = DirectorService(scope)
    resp_obj = director_service.fetch_director_list(vendor_id, employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_director(request, vendor_id, director_id):
    if request.method == 'GET':
        employee_id = request.employee_id
        scope = request.scope
        director_service = DirectorService(scope)
        logger.info(str(vendor_id))
        logger.info(str(director_id))
        resp_obj = director_service.fetch_director(vendor_id, director_id, employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_director(request, vendor_id, director_id)


def delete_director(request, vendor_id, director_id):
    employee_id = request.employee_id
    scope = request.scope
    director_service = DirectorService(scope)
    resp_obj = director_service.delete_director(vendor_id, director_id, employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
    pass
