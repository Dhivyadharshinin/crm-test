import json

from vendorservice.data.request.subtaxrequest import SubTaxRequest
from vendorservice.data.request.taxraterequest import TaxRateResquest
from vendorservice.data.request.taxrequest import TaxRequest
from masterservice.service.subtaxservice import SubTaxService
from masterservice.service.taxrateservice import TaxRateService
from masterservice.service.taxservice import TaxMasterService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from vendorservice.data.request.paymoderequest import PaymodeRequest

from masterservice.service.paymodeservice import PaymodeService

from masterservice.service.counrtyservice import CountryService
from masterservice.data.request.countryrequest import CountryRequest
from masterservice.data.request.districtrequest import DistrictRequest
from masterservice.data.request.staterequest import StateRequest
from masterservice.service.districtservice import DistrictService
from masterservice.service.stateservice import StateService
from masterservice.data.request.pincoderequest import PincodeResquest
from masterservice.service.cityservice import CityService
from masterservice.service.pincodeservice import PincodeService
from masterservice.data.request.uomrequest import UomRequest
from masterservice.service.uomservice import UomService

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def paymode(request):
    if request.method == 'POST':
        scope = request.scope
        paymode_service = PaymodeService(scope)
        paymode_obj = json.loads(request.body)
        pay_obj = PaymodeRequest(paymode_obj)
        employee_id = request.employee_id
        resp_obj = paymode_service.create_paymode(pay_obj, employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
       return fetch_paymode_list(request)

def fetch_paymode_list(request):
        scope = request.scope
        paymode_service = PaymodeService(scope)
        employee_id = request.employee_id
        resp_obj = paymode_service.fetch_paymode_list(scope)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_paymode(request, paymode_id):
    if request.method == 'GET':
        scope = request.scope
        paymode_service = PaymodeService(scope)
        employee_id =request.employee_id
        resp_obj = paymode_service.fetchpaymode(paymode_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
         return delete_paymode(request, paymode_id)
def delete_paymode(request, paymode_id):
    scope = request.scope
    paymode_service = PaymodeService(scope)
    employee_id = request.employee_id
    resp_obj = paymode_service.delete_paymode(paymode_id, employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

# @csrf_exempt
# @api_view(['GET', 'POST'])
# @authentication_classes([VysfinAuthentication])
# @permission_classes([IsAuthenticated, VysfinPermission])
# def bank(request):
#     if request.method == 'POST':
#         bank_service = BankService()
#         bank_data = json.loads(request.body)
#         user_id = request.user.id
#         bank_obj = BankRequest(bank_data)
#         resp_obj = bank_service.create_bank(bank_obj, user_id)
#         response = HttpResponse(resp_obj.get(), content_type="application/json")
#         return response
#     elif request.method == 'GET':
#         return fetch_bank_list(request)
#
#
# def fetch_bank_list(request):
#     bank_service = BankService()
#     user_id = request.user.id
#     resp_obj = bank_service.fetch_bank_list(user_id)
#     response = HttpResponse(resp_obj.get(), content_type="application/json")
#     return response
#
# @csrf_exempt
# @api_view(['GET', 'DELETE'])
# @authentication_classes([VysfinAuthentication])
# @permission_classes([IsAuthenticated, VysfinPermission])
# def fetch_bank(request,bank_id):
#     if request.method == 'GET':
#         bank_service = BankService()
#         user_id = request.user.id
#         resp_obj = bank_service.fetch_bank(bank_id,user_id)
#         response = HttpResponse(resp_obj.get(), content_type="application/json")
#         return response
#     elif request.method == 'DELETE':
#         return delete_bank(request,bank_id)
#
# @csrf_exempt
# def delete_bank(request,bank_id):
#     bank_service = BankService()
#     resp_obj = bank_service.delete_bank(bank_id)
#     response = HttpResponse(resp_obj.get(), content_type="application/json")
#     return response


# tax - create , insert , update , delete

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def tax(request):
    if request.method == 'POST':
        scope = request.scope
        tax_service = TaxMasterService(scope)
        tax_data = json.loads(request.body)
        tax_obj = TaxRequest(tax_data)
        employee_id = request.employee_id
        resp_obj = tax_service.create_tax(tax_obj, employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_tax_list(request)


def fetch_tax_list(request):
    user_id = request.user.id
    scope = request.scope
    tax_service = TaxMasterService(scope)
    resp_obj = tax_service.fetch_tax_list(user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


def delete_tax(request, tax_id):
    scope = request.scope
    tax_service = TaxMasterService(scope)
    employee_id = request.employee_id
    resp_obj = tax_service.delete_tax(tax_id, employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_tax(request, tax_id):
    if request.method == 'GET':
        scope = request.scope
        tax_service = TaxMasterService(scope)
        employee_id = request.employee_id
        resp_obj = tax_service.fetch_tax(tax_id, employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_tax(request, tax_id)


# subtax - create , insert , update , delete

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def subtax(request):
    if request.method == 'POST':
        scope = request.scope
        subtax_service = SubTaxService(scope)
        employee_id = request.employee_id
        subtax_data = json.loads(request.body)
        subtax_obj = SubTaxRequest(subtax_data)
        resp_obj = subtax_service.create_subtax(subtax_obj, employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_subtax_list(request)


def fetch_subtax_list(request):
    scope = request.scope
    subtax_service = SubTaxService(scope)
    employee_id = request.employee_id
    resp_obj = subtax_service.fetch_subtax_list(employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


def delete_subtax(request, subtax_id):
    scope = request.scope
    subtax_service = SubTaxService(scope)
    employee_id = request.employee_id
    resp_obj = subtax_service.delete_subtax(subtax_id, employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_subtax(request, subtax_id):
    if request.method == 'GET':
        scope = request.scope
        subtax_service = SubTaxService(scope)
        employee_id = request.employee_id
        resp_obj = subtax_service.fetch_subtax(subtax_id, employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_subtax(request, subtax_id)


# taxratemaster - create , insert , update , delete

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def taxrate(request):
    if request.method == 'POST':
        scope = request.scope
        taxrate_service = TaxRateService(scope)
        employee_id = request.employee_id
        taxrate_data = json.loads(request.body)
        taxrate_obj = TaxRateResquest(taxrate_data)
        resp_obj = taxrate_service.create_taxrate(taxrate_obj, employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_taxrate_list(request)


def fetch_taxrate_list(request):
    scope = request.scope
    taxrate_service = TaxRateService(scope)
    employee_id = request.employee_id
    resp_obj = taxrate_service.fetch_taxrate_list(employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


def delete_taxrate(request, taxrate_id):
    scope = request.scope
    taxrate_service = TaxRateService(scope)
    employee_id = request.employee_id
    resp_obj = taxrate_service.delete_taxrate(taxrate_id, employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_taxrate(request, taxrate_id):
    if request.method == 'GET':
        scope = request.scope
        taxrate_service = TaxRateService(scope)
        employee_id = request.employee_id
        resp_obj = taxrate_service.fetch_taxrate(taxrate_id, employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_taxrate(request, taxrate_id)
