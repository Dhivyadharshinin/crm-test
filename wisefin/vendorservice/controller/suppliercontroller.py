import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from userservice.service.employeeservice import EmployeeService
from vendorservice.service.clientservice import ContractorService, ClientService
from vendorservice.service.supplierservice import AddressService , ContactService
from vendorservice.service.profileservice import ProfileService
from vendorservice.data.request.supplierrequest import AddressRequest , ContactRequest,ProfileRequest,ClientRequest,ContractRequest

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
# from validationservice.controller.vendorvalidation import VendorValidation
from utilityservice.data.response.nwisefinpage import NWisefinPage
from masterservice.service.cityservice import CityService
from masterservice.service.stateservice import StateService
from masterservice.service.districtservice import DistrictService
from masterservice.service.pincodeservice import PincodeService
from vendorservice.service.vendorservice import VendorService
from vendorservice.models import Vendor
from django.db import transaction
from vendorservice.util.vendorutil import VendorStatusUtil

# supplier address - create , insert , update , delete
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def address(request):
    if request.method == 'POST':
        scope = request.scope
        address_service = AddressService(scope)
        address_data = json.loads(request.body)
        address_obj=AddressRequest(address_data)
        employee_id = request.employee_id
        resp_obj = address_service.create_address(address_obj,employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_address_list(request)

def fetch_address_list(request):
    scope = request.scope
    address_service = AddressService(scope)
    employee_id = request.employee_id
    resp_obj = address_service.fetch_address_list(employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
def delete_address(request,address_id):
    scope = request.scope
    address_service = AddressService(scope)
    employee_id = request.employee_id
    resp_obj = address_service.delete_address(address_id,employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_address(request, address_id):
    if request.method == 'GET':
        scope = request.scope
        address_service = AddressService(scope)
        employee_id = request.employee_id
        resp_obj = address_service.fetch_address(address_id,employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_address(request,address_id)



# supplier contact - create , insert , update , delete
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def contact(request):
    if request.method == 'POST':
        scope = request.scope
        contact_service = ContactService(scope)
        contact_data = json.loads(request.body)
        employee_id = request.employee_id
        contact_obj = ContactRequest(contact_data)
        resp_obj = contact_service.create_contact(contact_obj,employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_contact_list(request)

def fetch_contact_list(request):
    scope = request.scope
    contact_service = ContactService(scope)
    employee_id = request.employee_id
    resp_obj = contact_service.fetch_contact_list(employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
def delete_contact(request,contact_id):
    scope = request.scope
    contact_service = ContactService(scope)
    employee_id = request.employee_id
    resp_obj = contact_service.delete_contact(contact_id,employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_contact(request, contact_id):
    if request.method == 'GET':
        scope = request.scope
        contact_service = ContactService(scope)
        employee_id = request.employee_id
        resp_obj = contact_service.fetch_contact(contact_id,employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_contact(request,contact_id)


# supplier basic profile - create , insert , update , delete

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def profile(request,vendor_id):
    if request.method == 'POST':
        scope = request.scope
        profile_service = ProfileService(scope)
        employee_id = request.employee_id
        vendor_id=int(vendor_id)
        profile_data = json.loads(request.body)
        profile_obj = ProfileRequest(profile_data)
        resp_obj = profile_service.create_profile(profile_obj,vendor_id,employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_profile_list(request)

def fetch_profile_list(request):
    scope = request.scope
    profile_service = ProfileService(scope)
    employee_id = request.employee_id
    resp_obj = profile_service.fetch_profile_list(employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
def delete_profile(request,profile_id):
    scope = request.scope
    profile_service = ProfileService(scope)
    employee_id = request.employee_id
    resp_obj = profile_service.delete_profile(profile_id,employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_profile(request, profile_id,vendor_id):
    if request.method == 'GET':
        scope = request.scope
        profile_service = ProfileService(scope)
        employee_id = request.employee_id
        vendor_id = int(vendor_id)
        resp_obj = profile_service.fetch_profile(profile_id,employee_id,vendor_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_profile(request,profile_id)

#supplier contract - create , insert , update , delete
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def contractor(request,vendor_id):
    if request.method == 'POST':
        scope = request.scope
        contractor_service = ContractorService(scope)
        # vendorvalidation=VendorValidation()    # commented for purpose
        employee_id = request.employee_id
        vendor_id = int(vendor_id)
        contractor_data = json.loads(request.body)

        contractor_obj = ContractRequest(contractor_data)
        # vendorcontract_validation=vendorvalidation.vendorcontract_validation(contractor_obj)   # commented for purpose
        vendor_service=VendorService(scope)
        mod_status=vendor_service.get_modification_status(vendor_id)
        if mod_status:
            resp_obj = contractor_service.contractor_modification(contractor_obj, vendor_id, employee_id)
        else:
            resp_obj = contractor_service.create_contractor(contractor_obj, vendor_id, employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_contractor_list(request,vendor_id)

def fetch_contractor_list(request,vendor_id):
    scope = request.scope
    contractor_service = ContractorService(scope)
    employee_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)

    resp_obj = contractor_service.fetch_contractor_list(request, vys_page, employee_id, vendor_id)
    vendor_service = VendorService(scope)
    x = resp_obj.data
    for i in x:
        vendor_id = i.vendor_id
        vendor_status = vendor_service.get_vendor_status(vendor_id)
        i.q_modify = False
        if (i.created_by == employee_id):
            if (vendor_status == 0 or vendor_status == 1):
                i.q_modify = True

    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
def delete_contractor(request,contractor_id,vendor_id):
    scope = request.scope
    contractor_service = ContractorService(scope)
    employee_id = request.employee_id
    vendor_service = VendorService(scope)
    mod_status = vendor_service.get_modification_status(vendor_id)
    if mod_status is True:
        resp_obj = contractor_service.modification_delete_contractor(contractor_id, vendor_id,employee_id)
    else:
        resp_obj = contractor_service.delete_contractor(contractor_id,vendor_id,employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_contractor(request, contractor_id,vendor_id):
    if request.method == 'GET':
        scope = request.scope
        contractor_service = ContractorService(scope)
        employee_id = request.employee_id
        vendor_id = int(vendor_id)
        resp_obj = contractor_service.fetch_contractor(contractor_id,employee_id,vendor_id)

        vendor_service = VendorService(scope)
        vendor_id = resp_obj.vendor_id
        vendor_status = vendor_service.get_vendor_status(vendor_id)
        resp_obj.q_modify = False
        if (resp_obj.created_by == employee_id):
            if (vendor_status == 0 or vendor_status == 1):
                resp_obj.q_modify = True
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_contractor(request,contractor_id,vendor_id)

# supplier client - create , insert , update , delete
@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def client(request,vendor_id):
    if request.method == 'POST':
        scope = request.scope
        client_service = ClientService(scope)
        address_service = AddressService(scope)
        employee_id = request.employee_id
        vendor_id = int(vendor_id)
        client_data = json.loads(request.body)
        client_json=client_data
        client_obj = ClientRequest(client_data)

        address = client_data.get("address")
        address_obj = AddressRequest(address)

        vendor_service = VendorService(scope)
        mod_status = vendor_service.get_modification_status(vendor_id)
        if mod_status:
            add_id = address_service.modification_create_address(address_obj, employee_id,vendor_id)
            resp_obj = client_service.client_modification(client_obj,employee_id,vendor_id,add_id)
        else:
            add_id = address_service.create_address(address_obj, employee_id,vendor_id)
            resp_obj = client_service.create_client(client_obj,client_json,employee_id,vendor_id,add_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_client_list(request,vendor_id)


def fetch_client_list(request,vendor_id):
    employee_id = request.employee_id
    scope = request.scope
    client_service = ClientService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = client_service.fetch_client_list(request, vys_page, employee_id,vendor_id)

    # monesh
    address_service = AddressService(scope)
    state_service = StateService(scope)
    city_service = CityService(scope)
    district_service = DistrictService(scope)
    pincode_service = PincodeService(scope)
    x = resp_obj.data
    for i in x:
        add_id = i.address_id
        address = address_service.fetch_address(add_id, employee_id)
        i.address_id = address

    y=resp_obj.data
    for i in y:
        pincode_id = i.address_id.pincode_id
        pincode = pincode_service.fetch_pincode(pincode_id, employee_id)
        i.address_id.pincode_id = pincode
        city_id = i.address_id.city_id
        city = city_service.fetch_city(city_id, employee_id)
        i.address_id.city_id = city
        district_id = i.address_id.district_id
        district = district_service.fetchdistrict(district_id)
        i.address_id.district_id = district
        state_id = i.address_id.state_id
        state = state_service.fetchstate(state_id)
        i.address_id.state_id = state

    vendor_service = VendorService(scope)
    x = resp_obj.data
    for i in x:
        vendor_id = i.vendor_id
        vendor_status = vendor_service.get_vendor_status(vendor_id)
        i.q_modify = False
        if (i.created_by == employee_id):
            if (vendor_status == 0 or vendor_status == 1):
                i.q_modify = True

    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
def delete_client(request,client_id,vendor_id):
    scope = request.scope
    client_service = ClientService(scope)
    employee_id = request.employee_id
    vendor_service = VendorService(scope)
    mod_status = vendor_service.get_modification_status(vendor_id)
    if mod_status is True:
        resp_obj = client_service.modification_delete_client(client_id, employee_id, vendor_id)
    else:
        resp_obj = client_service.delete_client(client_id,vendor_id, employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")

    return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_client(request,vendor_id, client_id):
    if request.method == 'GET':
        scope = request.scope
        client_service = ClientService(scope)
        address_service = AddressService(scope)
        state_service = StateService(scope)
        city_service = CityService(scope)
        district_service = DistrictService(scope)
        pincode_service = PincodeService(scope)
        employee_id = request.employee_id
        vendor_id = int(vendor_id)
        resp_obj = client_service.fetch_client(client_id)
        add_id = resp_obj.address_id
        address = address_service.fetch_address(add_id, employee_id)
        resp_obj.address_id = address

        city_id = resp_obj.address_id.city_id
        city = city_service.fetch_city(city_id, employee_id)
        resp_obj.address_id.city_id = city
        state_id = resp_obj.address_id.state_id
        state = state_service.fetchstate(state_id)
        resp_obj.address_id.state_id = state
        district_id = resp_obj.address_id.district_id
        district = district_service.fetchdistrict(district_id)
        resp_obj.address_id.district_id = district
        pincode_id = resp_obj.address_id.pincode_id
        pincode = pincode_service.fetch_pincode(pincode_id, employee_id)
        resp_obj.address_id.pincode_id = pincode

        vendor_service = VendorService(scope)
        vendor_id = resp_obj.vendor_id
        vendor_status = vendor_service.get_vendor_status(vendor_id)
        resp_obj.q_modify = False
        if (resp_obj.created_by == employee_id):
            if (vendor_status == 0 or vendor_status == 1):
                resp_obj.q_modify = True

        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':

        return delete_client(request,client_id,vendor_id)
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_supplier_using_code(request):
    scope = request.scope
    sup_serv=ContactService(scope)
    employee_id = request.employee_id
    sup_code=request.GET.get('supplier_code')
    page = request.GET.get('page', 1)
    page = int(page)
    assetmaster_resp = sup_serv.fetch_supplier_code(sup_code)
    response = HttpResponse(assetmaster_resp.get(), content_type='application/json')
    return response


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_supplier_using_code(request,supplier_code):
    scope = request.scope
    sup_serv=ContactService(scope)
    employee_id = request.employee_id
    sup_code=supplier_code
    page = request.GET.get('page', 1)
    page = int(page)
    assetmaster_resp = sup_serv.fetch_supplier_code(sup_code)
    response = HttpResponse(assetmaster_resp, content_type='application/json')
    return response
