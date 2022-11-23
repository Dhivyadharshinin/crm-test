import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from vendorservice.service.vendoraddressservice import VendorAddressService
from vendorservice.data.request.vendoraddressrequest import AddressRequest
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from masterservice.service.stateservice import StateService
from masterservice.service.districtservice import DistrictService
from masterservice.service.cityservice import CityService
from masterservice.service.pincodeservice import PincodeService
from vendorservice.models.vendormodels import VendorRelAddress

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
#vendor_id
def vendoraddress(request,vendor_id):
    if request.method == 'POST':
        employee_id = request.employee_id
        scope = request.scope
        vendoraddress_service = VendorAddressService(scope)
        vendoraddress_obj = json.loads(request.body)
        vendoraddress_obj=AddressRequest(vendoraddress_obj)
        resp_obj = vendoraddress_service.create_vendoraddress( vendoraddress_obj,vendor_id, employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_vendoraddress_list(request,vendor_id)


def fetch_vendoraddress_list(request, vendor_id):
    employee_id = request.employee_id
    scope = request.scope
    vendoraddress_service = VendorAddressService(scope)
    resp_obj = vendoraddress_service.fetch_vendoraddress_list(vendor_id, employee_id)
    state_service = StateService(scope)
    city_service = CityService(scope)
    district_service = DistrictService(scope)
    pincode_service = PincodeService(scope)
    x = resp_obj.data
    for i in x:
        city_id = i.city_id
        city = city_service.fetch_city(city_id, employee_id)
        i.city_id = city
        district_id = i.district_id
        district = district_service.fetchdistrict(district_id)
        i.district_id = district
        pincode_id = i.pincode_id
        pincode = pincode_service.fetch_pincode(pincode_id,employee_id)
        i.pincode_id = pincode
        state_id = i.state_id
        state = state_service.fetchstate(state_id)
        i.state_id = state

    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_vendoraddress(request, vendor_id, address_id):
    if request.method == 'GET':
        emp_id = request.employee_id
        scope = request.scope
        vendoraddress_service = VendorAddressService(scope)
        resp_obj = vendoraddress_service.fetch_vendoraddress(vendor_id, emp_id)
        state_service = StateService(scope)
        city_service = CityService(scope)
        district_service = DistrictService(scope)
        pincode_service = PincodeService(scope)
        x = resp_obj.data
        for i in x:
            city_id = i.city_id
            city = city_service.fetch_city(city_id, emp_id)
            i.city_id = city
            district_id = i.district_id
            district = district_service.fetchdistrict(district_id)
            i.district_id = district
            pincode_id = i.pincode_id
            pincode = pincode_service.fetch_pincode(pincode_id,emp_id)
            i.pincode_id = pincode
            state_id = i.state_id
            state = state_service.fetchstate(state_id)
            i.state_id = state

        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_vendoraddress(request, vendor_id,address_id)


def delete_vendoraddress(request, vendor_id, address_id):
    employee_id = request.employee_id
    scope = request.scope
    vendoraddress_service = VendorAddressService(scope)
    resp_obj = vendoraddress_service.delete_vendoraddress(vendor_id, address_id, employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

# #microtomicro
# @csrf_exempt
# @api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def fetch_vendoraddress(request, address_id):
#     vendoraddresss = VendorRelAddress.objects.get(id=address_id)
#     vendoraddress_data = {"id": vendoraddresss.id,
#                            "line1": vendoraddresss.line1,
#                            "line2": vendoraddresss.line2,
#                            "line3": vendoraddresss.line3,
#                            "pincode_id": vendoraddresss.pincode_id,
#                            "city_id": vendoraddresss.city_id,
#                            "state_id": vendoraddresss.state_id}
#     venaddress_dic = json.dumps(vendoraddress_data, indent=4)
#     return HttpResponse(venaddress_dic, content_type='application/json')
#
