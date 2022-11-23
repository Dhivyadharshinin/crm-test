import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from userservice.service.employeeservice import EmployeeService
from vendorservice.data.request.supplierrequest import ProfileRequest
from vendorservice.service.profileservice import ProfileService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
#vendor_id
def profile(request,vendor_id):
    if request.method == 'POST':
        employee_id = request.employee_id
        scope = request.scope
        profile_service = ProfileService(scope)
        pro_obj = json.loads(request.body)
        profile_obj=ProfileRequest(pro_obj)
        resp_obj = profile_service.create_profile(profile_obj,vendor_id,employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_profile_list(request,vendor_id)


def fetch_profile_list(request, vendor_id):
    employee_id = request.employee_id
    scope = request.scope
    profile_service = ProfileService(scope)
    resp_obj = profile_service.fetch_profile_list(vendor_id, employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_profile(request, vendor_id, profile_id):
    if request.method == 'GET':
        employee_id = request.employee_id
        scope = request.scope
        profile_service = ProfileService(scope)
        resp_obj = profile_service.fetch_profile(vendor_id, profile_id, employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_profile(request, vendor_id, profile_id)


def delete_profile(request, vendor_id,profile_id):
    employee_id = request.employee_id
    scope = request.scope
    profile_service = ProfileService(scope)
    resp_obj = profile_service.delete_profile(vendor_id, profile_id, employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

