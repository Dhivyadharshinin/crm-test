import io
from datetime import datetime

import pandas as pd
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from nwisefin.settings import logger
from masterservice.controller.codegencontroller import dictdefault
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from masterservice.data.request.taxrequest import TaxRequest
from masterservice.service.taxservice import TaxMasterService
import json
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.service.employeeservice import EmployeeService


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def tax(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        tax_service = TaxMasterService(scope)
        tax_data = json.loads(request.body)
        tax_obj = TaxRequest(tax_data)
        # user_id = request.employee_id
        # emp_service = EmployeeService(scope)
        # empid = emp_service.get_empid_from_userid(user_id)
        resp_obj = tax_service.create_tax(tax_obj, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_tax_list(request)


def fetch_tax_list(request):
    user_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    scope = request.scope
    tax_service = TaxMasterService(scope)
    resp_obj = tax_service.fetch_tax_list(vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def delete_tax(request, tax_id):
    scope = request.scope
    emp_id = request.employee_id
    tax_service = TaxMasterService(scope)
    # user_id = request.employee_id
    resp_obj = tax_service.delete_tax(tax_id, emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_tax(request, tax_id):
    if request.method == 'GET':
        scope = request.scope
        emp_id = request.employee_id
        tax_service = TaxMasterService(scope)
        # user_id = request.employee_id
        resp_obj = tax_service.fetch_tax(tax_id, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_tax(request, tax_id)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def tax_search(request):
    query = request.GET.get('query')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    scope = request.scope
    tax_service = TaxMasterService(scope)
    resp_obj = tax_service.fetch_tax_search(query,vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def tax_mtom(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        tax_service = TaxMasterService(scope)
        tax_data = json.loads(request.body)
        action = request.GET.get('action')
        tax_obj = TaxRequest(tax_data)
        # user_id = request.employee_id
        # emp_service = EmployeeService(scope)
        # empid = emp_service.get_empid_from_userid(user_id)
        resp_obj = tax_service.create_tax_mtom(tax_obj, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def newtaxsummary(request):
    if request.method=='GET':
        page = request.GET.get('page', 1)
        page = int(page)
        scope =request.scope
        vys_page = NWisefinPage(page, 10)
        tax_service=TaxMasterService(scope)
        resp_obj=tax_service.new_tax_summmary(request,vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def taxname(request):
    if request.method=='GET':
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        scope = request.scope
        tax_service = TaxMasterService(scope)
        resp_obj = tax_service.taxname_get(request, vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def subtaxname(request,tax_id):
    if request.method == 'GET':
        print(tax_id)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        scope = request.scope
        tax_service = TaxMasterService(scope)
        resp_obj = tax_service.subtaxname(request, vys_page,tax_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def taxratename(request,subtax_id):
    if request.method == 'GET':
        print(subtax_id)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        scope = request.scope
        tax_service = TaxMasterService(scope)
        resp_obj = tax_service.taxratename(request, vys_page,subtax_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_tax_download(request):
    scope = request.scope
    tax_service = TaxMasterService(scope)
    user_id = request.user.id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    tax_resp = tax_service.fetch_tax_list_download(request)
    data = json.loads(tax_resp.get())
    # data = json.loads(json.dumps(tax_resp.__dict__, default=dictdefault))['data']
    df = pd.DataFrame.from_dict(data['data'])
    df = df.reindex(columns=['id','code','name','glno','payable','receivable'])
    df.rename(columns={'id': 'Id', 'code': 'Code','name':'Name', 'glno': 'Glno','payable': 'Payable','receivable':'Receivable'},
               inplace=True)
    BytesIO = io.BytesIO()
    BytesIO.name = 'EXCEL-DOWNLOAD-(' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ').xlsx'
    writer = pd.ExcelWriter(BytesIO, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False, startcol=0, startrow=5)
    worksheet = writer.sheets['Sheet1']
    workbook = writer.book
    header_format = workbook.add_format()
    header_format.set_align('center')
    header_format.set_bold()
    worksheet.write_string(2, 3, 'Tax master excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="Tax master.xlsx"'
    logger.info("Tax_master_Download Data:"+str(datetime.now()))
    return response
