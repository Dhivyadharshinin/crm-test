import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from userservice.service.employeeservice import EmployeeService
from vendorservice.service.venodrcontactservice import VendorContactService
from vendorservice.data.request.vendorcontactrequest import ContactRequest
from masterservice.service.contacttypeservice import ContactTypeService
from masterservice.service.designationservice import DesignationService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
#vendor_id
def vendorcontact(request,vendor_id):
    if request.method == 'POST':
        scope = request.scope
        contact_service = VendorContactService(scope)
        employee_id = request.employee_id
        contact_data = json.loads(request.body)
        contact_obj = ContactRequest(contact_data)
        resp_obj = contact_service.create_vendorcontact(vendor_id,contact_obj,employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_vendorcontact_list(request,vendor_id)


def fetch_vendorcontact_list(request,vendor_id):
    scope = request.scope
    contact_service = VendorContactService(scope)
    employee_id = request.employee_id
    resp_obj = contact_service.fetch_vendorcontact_list(vendor_id,employee_id)
    contact_service = ContactTypeService(scope)
    x = resp_obj.data

    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_vendorcontact(request,vendor_id, contact_id):
    if request.method == 'GET':
        scope = request.scope
        contact_service = VendorContactService(scope)
        employee_id = request.employee_id
        resp_obj = contact_service.fetch_vendorcontact(vendor_id,employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_vendorcontact(request,vendor_id,contact_id)

def delete_vendorcontact(request,vendor_id,contact_id):
    scope = request.scope
    contact_service = VendorContactService(scope)
    employee_id = request.employee_id
    resp_obj = contact_service.delete_vendorcontact(vendor_id,contact_id,employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
