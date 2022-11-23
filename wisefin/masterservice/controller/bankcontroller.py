import io
import json
from datetime import datetime

import pandas as pd
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from nwisefin.settings import logger
from masterservice.util.masterutil import dictdefault
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from masterservice.data.request.bankrequest import BankRequest
from masterservice.service.bankservice import BankService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.service.employeeservice import EmployeeService
from masterservice.models import Bank
from utilityservice.data.response.nwisefinlist import NWisefinList

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def bank(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        bank_service = BankService(scope)
        bank_data = json.loads(request.body)
        # user_id = request.user.id
        bank_obj = BankRequest(bank_data)
        # emp_service = EmployeeService(scope)
        # empid = emp_service.get_empid_from_userid(user_id)
        resp_obj = bank_service.create_bank(bank_obj, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_bank_list(request)


def fetch_bank_list(request):
    scope = request.scope
    bank_service = BankService(scope)
    user_id = request.employee_id
    page = request.GET.get('page', 1)
    query = request.GET.get('query', None)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = bank_service.fetch_bank_list(vys_page,query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_bank(request,bank_id):
    if request.method == 'GET':
        scope = request.scope
        emp_id = request.employee_id
        bank_service = BankService(scope)
        # user_id = request.user.id
        resp_obj = bank_service.fetch_bank(bank_id,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_bank(request,bank_id)


@csrf_exempt
def delete_bank(request,bank_id):
    scope = request.scope
    emp_id = request.employee_id
    bank_service = BankService(scope)
    # user_id = request.user.id
    resp_obj = bank_service.delete_bank(bank_id,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def bank_search(request):
    scope = request.scope
    bank_service = BankService(scope)
    query = request.GET.get('query')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = bank_service.fetch_bank_search(query,vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def bank_mtom(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        bank_service = BankService(scope)
        bank_data = json.loads(request.body)
        user_id = request.employee_id
        action = request.GET.get('action')
        bank_obj = BankRequest(bank_data)
        # emp_service = EmployeeService(scope)
        # empid = emp_service.get_empid_from_userid(user_id)
        resp_obj = bank_service.create_bank_mtom(bank_obj, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

#micro to micro New
#Get bank
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_bankone(request,bank_id):
    bank = Bank.objects.get(id=bank_id)
    bank_data = {"id": bank.id, "code": bank.code, "name": bank.name}
    bank_dic = json.dumps(bank_data, indent=4)
    return HttpResponse(bank_dic, content_type='application/json')
#bank getlist
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_banklist(request):
    bank_ids = json.loads(request.body)
    bank_id2 = bank_ids['bank_id']
    obj = Bank.objects.filter(id__in=bank_id2).values('id', 'name','code')
    bank_list_data = NWisefinList()
    for i in obj:
        data = {"id": i['id'], "name": i['name'],"code": i['code']}
        bank_list_data.append(data)
    return HttpResponse(bank_list_data.get(), content_type='application/json')

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_bank_download(request):
    scope = request.scope
    bank_service = BankService(scope)
    user_id = request.user.id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    bank_resp = bank_service.fetch_bank_list_download(request)
    data = json.loads(json.dumps(bank_resp.__dict__, default=dictdefault))['data']
    df = pd.DataFrame(data)
    df.rename(columns={'id': "S.No",'code':"Code",'name':"Name"},inplace=True)
    BytesIO = io.BytesIO()
    BytesIO.name = 'EXCEL-DOWNLOAD-(' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ').xlsx'
    writer = pd.ExcelWriter(BytesIO, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False, startcol=0, startrow=5)
    worksheet = writer.sheets['Sheet1']
    workbook = writer.book
    header_format = workbook.add_format()
    header_format.set_align('center')
    header_format.set_bold()
    worksheet.write_string(2, 2, 'Bank Master Excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="Bank Master.xlsx"'
    logger.info("Bank_Download Data:"+str(datetime.now()))
    return response