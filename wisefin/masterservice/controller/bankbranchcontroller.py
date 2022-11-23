import io
import json
from datetime import datetime

import pandas as pd
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from masterservice.util.masterutil import dictdefault
from nwisefin.settings import logger
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from masterservice.data.request.bankbranchrequest import BankBranchRequest
from masterservice.service.bankbranchservice import BankBranchService
from masterservice.service.addressservice import AddressService
from masterservice.data.request.addressrequest import AddressRequest
from masterservice.service.bankservice import BankService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.service.employeeservice import EmployeeService
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def bankbranch(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        bankbranch_service = BankBranchService(scope)
        bankbranch_data = json.loads(request.body)
        # user_id = request.user.id
        # emp_service = EmployeeService(scope)
        # empid = emp_service.get_empid_from_userid(user_id)
        bankbranch_obj = BankBranchRequest(bankbranch_data)
        address_service = AddressService(scope)
        address = bankbranch_data.get("address_id")
        address_obj = AddressRequest(address)
        if bankbranch_obj.id is not None:
            address_id = bankbranch_service.get_addressid_bankbranch(bankbranch_obj.id)
            address_obj.id = address_id
        add_id = address_service.create_address(address_obj, emp_id)

        resp_obj = bankbranch_service.create_bankbranch(bankbranch_obj, add_id, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
# @csrf_exempt
# @api_view(['GET', 'POST'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def bankbranch(request):
#     if request.method == 'POST':
#         bankbranch_service = BankBranchService()
#         bankbranch_data = json.loads(request.body)
#         user_id = request.employee_id
#         emp_service = EmployeeService()
#         empid = emp_service.get_empid_from_userid(user_id)
#         bankbranch_obj = BankBranchRequest(bankbranch_data)
#
#         address_service = AddressService()
#         # address = bankbranch_data.get_add_id("id")
#         # print(address)
#         # address = bankbranch_data.get("address_id")
#         # address_obj = AddressRequest(address)
#         address_obj1 = AddressRequest(bankbranch_data)
#         # new_address = address_obj.get_addresss_id()
#         address_obj = address_obj1.get_addresss_id()
#         if bankbranch_obj.id is not None:
#             address_id=bankbranch_service.get_addressid_bankbranch(bankbranch_obj.id)
#             address_obj.id =address_id
#
#         add_id = address_service.create_address(address_obj, user_id)
#
#         resp_obj = bankbranch_service.create_bankbranch(bankbranch_obj,add_id, empid)
#         response = HttpResponse(resp_obj.get(), content_type="application/json")
#         return response
    elif request.method == 'GET':
        return fetch_bankbranch_list(request)


def fetch_bankbranch_list(request):
    scope = request.scope
    bankbranch_service = BankBranchService(scope)
    user_id = request.user.id
    page = request.GET.get('page', 1)
    query = request.GET.get('query', None)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = bankbranch_service.fetch_bankbranch_list(vys_page, query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_bankbranch(request, bankbranch_id):
    if request.method == 'GET':
        scope = request.scope
        emp_id = request.employee_id
        bankbranch_service = BankBranchService(scope)
        # user_id = request.user.id
        resp_obj = bankbranch_service.fetch_bankbranch(bankbranch_id, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_bankbranch(request, bankbranch_id)


@csrf_exempt
def delete_bankbranch(request, bankbranch_id):
    scope = request.scope
    emp_id = request.employee_id
    bankbranch_service = BankBranchService(scope)
    # user_id = request.user.id
    resp_obj = bankbranch_service.delete_bankbranch(bankbranch_id, emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def bankbranch_search(request):
    scope = request.scope
    bankbranch_service = BankBranchService(scope)
    query = request.GET.get('query')
    bank_id = request.GET.get('bank_id')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = bankbranch_service.fetch_bankbranch_search(query, bank_id, vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ifsc_bankbranch(request):
    if request.method == 'GET':
        scope = request.scope
        bankbranch_service = BankBranchService(scope)
        query = request.GET.get('query')
        bank_id = request.GET.get('bank_id')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = bankbranch_service.search_ifsc(bank_id, query, vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def bankbranch_mtom(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        bankbranch_service = BankBranchService(scope)
        bankbranch_data = json.loads(request.body)
        # user_id = request.user.id
        # emp_service = EmployeeService(scope)
        # empid = emp_service.get_empid_from_userid(user_id)
        bankbranch_obj = BankBranchRequest(bankbranch_data)
        address = bankbranch_service.address_details_get(bankbranch_data['address_id'])
        address_service = AddressService(scope)
        # address = bankbranch_data.get("address_id")
        address_obj = AddressRequest(address)
        if bankbranch_obj.id is not None:
            address_id = bankbranch_service.get_addressid_bankbranch(bankbranch_obj.id)
            address_obj.id = address_id

        add_id = address_service.create_address(address_obj, emp_id)

        resp_obj = bankbranch_service.create_bankbranch_mtom(bankbranch_obj, add_id, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
# @csrf_exempt
# @api_view(['GET', 'POST'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def bankbranch_new(request):
#     if request.method == 'POST':
#         bankbranch_service = BankBranchService()
#         bankbranch_data = json.loads(request.body)
#         user_id = request.employee_id
#         emp_service = EmployeeService()
#         empid = emp_service.get_empid_from_userid(user_id)
#         bankbranch_obj = BankBranchRequest(bankbranch_data)
#         address_service = AddressService()
#         address_details = bankbranch_data.get("address")
#         print(address_details)
#         address_obj1 = AddressRequest(address_details)
#         add_id = address_service.create_address(address_obj1, user_id)
#         resp_obj = bankbranch_service.create_bankbranch(bankbranch_obj,add_id, empid)
#         print(resp_obj.get())
#         response = HttpResponse(resp_obj.get(), content_type="application/json")
#         return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def bankbranch_summary(request,bank_id):
    print(bank_id)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    scope = request.scope
    bank_service = BankBranchService(scope)
    resp_obj = bank_service.bank_branch_summary(request, bank_id, vys_page)
    return HttpResponse(resp_obj.get(), content_type='application/json')


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_bank_branch_download(request):
    scope = request.scope
    bankbranch_service = BankBranchService(scope)
    user_id = request.user.id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    bank_br_resp = bankbranch_service.fetch_bankbranch_list_download(request)
    data = json.loads(json.dumps(bank_br_resp.__dict__, default=dictdefault))['data']
    df = pd.DataFrame(data)
    BytesIO = io.BytesIO()
    BytesIO.name = 'EXCEL-DOWNLOAD-(' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ').xlsx'
    writer = pd.ExcelWriter(BytesIO, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False, startcol=0, startrow=5)
    worksheet = writer.sheets['Sheet1']
    workbook = writer.book
    header_format = workbook.add_format()
    header_format.set_align('center')
    header_format.set_bold()
    worksheet.write_string(2, 2, 'Bank Branch master excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="Bank Branch master.xlsx"'
    logger.info("Bank_branch_Download Data:"+str(datetime.now()))
    return response
