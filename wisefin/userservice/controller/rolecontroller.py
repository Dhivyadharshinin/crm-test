import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from masterservice.models import *

from masterservice.models import BankBranch,Bank,TaxRate,SubTax,Tax,PayMode
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission

from userservice.data.request.rolerequest import RoleResquest
from userservice.service.roleservice import RoleService
import time
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.permissions.filter.urlpermission import UrlPermission
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
# from vendorservice.models import Vendor, VendorQueue, VendorDirector, VendorProfile, VendorAddress, VendorContact, \
#     VendorRelAddress, VendorEntity, VendorSubContractor, SupplierBranch, SupplierTax, SupplierPayment, SupplierProduct, \
#     SupplierActivity, ActivityDetail, Catelog, VendorAccessor, Vendoraudit, VendorModificationRel, VendorDocument, \
#     SupplierSubTax, VendorRelContact

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission, UrlPermission])
def role(request):
    if request.method == 'POST':
        scope = request.scope
        role_service = RoleService(scope)
        role_data = json.loads(request.body)
        user_id = request.employee_id
        role_obj = RoleResquest(role_data)
        resp_obj = role_service.create_role(role_obj, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_role_list(request)


def fetch_role_list(request):
    scope = request.scope
    role_service = RoleService(scope)
    user_id = request.employee_id
    resp_obj = role_service.fetch_role_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission,UrlPermission])
def fetch_role(request,role_id):
    if request.method == 'GET':
        t1 = time.time()
        scope = request.scope
        role_service = RoleService(scope)
        user_id = request.employee_id
        resp_obj = role_service.fetch_role(role_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        t2 = time.time()
        return response
    elif request.method == 'DELETE':
        return delete_role(request,role_id)


@csrf_exempt
def delete_role(request,role_id):
    scope = request.scope
    role_service = RoleService(scope)
    resp_obj = role_service.delete_role(role_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

#  admin

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def role_admin(request):
    if request.method == 'POST':
        scope = request.scope
        role_service = RoleService(scope)
        role_data = json.loads(request.body)
        user_id = request.employee_id
        role_obj = RoleResquest(role_data)
        resp_obj = role_service.create_role(role_obj, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_role_list(request)


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission,UrlPermission])
def fetch_role_admin(request,role_id):
    if request.method == 'GET':
        t1 = time.time()
        scope = request.scope
        role_service = RoleService(scope)
        user_id = request.employee_id
        resp_obj = role_service.fetch_role(role_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        t2 = time.time()
        return response
    elif request.method == 'DELETE':
        return delete_role(request,role_id)

#
# @csrf_exempt
# @api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def del_table(request):
#     try:
#         table_name = request.GET.get('name')
#
#         if table_name == 'Vendor':
#             Vendor.objects.all().delete()
#         if table_name == 'VendorQueue':
#             VendorQueue.objects.all().delete()
#         if table_name == 'VendorDirector':
#             VendorDirector.objects.all().delete()
#         if table_name == 'VendorProfile':
#             VendorProfile.objects.all().delete()
#         if table_name == 'VendorAddress':
#             VendorAddress.objects.all().delete()
#         if table_name == 'VendorContact':
#             VendorContact.objects.all().delete()
#         if table_name == 'VendorRelAddress':
#             VendorRelAddress.objects.all().delete()
#         if table_name == 'VendorEntity':
#             VendorEntity.objects.all().delete()
#         if table_name == 'VendorSubContractor':
#             VendorSubContractor.objects.all().delete()
#         if table_name == 'VendorRelContact':
#             VendorRelContact.objects.all().delete()
#         if table_name == 'SupplierBranch':
#             SupplierBranch.objects.all().delete()
#         if table_name == 'SupplierTax':
#             SupplierTax.objects.all().delete()
#         if table_name == 'SupplierSubTax':
#             SupplierSubTax.objects.all().delete()
#         if table_name == 'SupplierPayment':
#             SupplierPayment.objects.all().delete()
#         if table_name == 'SupplierProduct':
#             SupplierProduct.objects.all().delete()
#         if table_name == 'SupplierActivity':
#             SupplierActivity.objects.all().delete()
#         if table_name == 'ActivityDetail':
#             ActivityDetail.objects.all().delete()
#         if table_name == 'Catelog':
#             Catelog.objects.all().delete()
#         if table_name == 'VendorAccessor':
#             VendorAccessor.objects.all().delete()
#         if table_name == 'Vendoraudit':
#             Vendoraudit.objects.all().delete()
#         if table_name == 'VendorModificationRel':
#             VendorModificationRel.objects.all().delete()
#         if table_name == 'VendorDocument':
#             VendorDocument.objects.all().delete()
#         if table_name == 'BankBranch':
#             BankBranch.objects.all().delete()
#         if table_name == 'Bank':
#             Bank.objects.all().delete()
#         if table_name == 'TaxRate':
#             TaxRate.objects.all().delete()
#         if table_name == 'SubTax':
#             SubTax.objects.all().delete()
#         if table_name == 'Tax':
#             Tax.objects.all().delete()
#         if table_name == 'PayMode':
#             PayMode.objects.all().delete()
#
#         success_obj = NWisefinSuccess()
#         success_obj.set_status(SuccessStatus.SUCCESS)
#         success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
#         return HttpResponse(success_obj.get(), content_type="application/json")
#
#     except:
#         error_obj = NWisefinError()
#         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#         error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
#         return HttpResponse(error_obj.get(), content_type="application/json")