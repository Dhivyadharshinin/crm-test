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
from masterservice.models import SubTax
from masterservice.util.masterutil import dictdefault
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from masterservice.data.request.subtaxrequest import SubTaxRequest
from masterservice.service.subtaxservice import SubTaxService
from masterservice.service.taxservice import TaxMasterService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.service.employeeservice import EmployeeService

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def subtax(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        subtax_service = SubTaxService(scope)
        # user_id = request.employee_id
        # emp_service = EmployeeService(scope)
        # empid = emp_service.get_empid_from_userid(user_id)
        subtax_data = json.loads(request.body)
        subtax_obj = SubTaxRequest(subtax_data)
        resp_obj = subtax_service.create_subtax(subtax_obj, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_subtax_list(request)


def fetch_subtax_list(request):
    scope = request.scope
    subtax_service = SubTaxService(scope)
    user_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = subtax_service.fetch_subtax_list(vys_page)
    # tax_service = TaxMasterService()
    # x = resp_obj.data
    # for i in x:
    #     tax_id = i.tax_id
    #     tax = tax_service.fetch_tax(tax_id,user_id)
    #     i.tax_id = tax
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def delete_subtax(request, subtax_id):
    scope = request.scope
    emp_id = request.employee_id
    subtax_service = SubTaxService(scope)
    # user_id = request.employee_id
    resp_obj = subtax_service.delete_subtax(subtax_id, emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_subtax(request, subtax_id):
    if request.method == 'GET':
        scope = request.scope
        emp_id = request.employee_id
        subtax_service = SubTaxService(scope)
        # user_id = request.employee_id
        resp_obj = subtax_service.fetch_subtax(subtax_id, emp_id)
        # tax_service = TaxMasterService()
        # tax_id = resp_obj.tax_id
        # tax = tax_service.fetch_tax(tax_id, user_id)
        # resp_obj.tax_id = tax

        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_subtax(request, subtax_id)

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def subtax_search(request):
    scope = request.scope
    subtax_service = SubTaxService(scope)
    query = request.GET.get('query',None)
    tax_id =request.GET.get('tax_id',None)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = subtax_service.fetch_subtax_search(query,tax_id,vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def tds_subtax_search(request):
    scope = request.scope
    subtax_service = SubTaxService(scope)
    query = request.GET.get('query',None)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = subtax_service.subtaxtds_search(query,vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def subtax_mtom(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        subtax_service = SubTaxService(scope)
        action = request.GET.get('action')
        subtax_data = json.loads(request.body)
        subtax_obj = SubTaxRequest(subtax_data)
        resp_obj = subtax_service.create_subtax_mtom(subtax_obj,action, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

#subtax getlist
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_subtaxlist(request):
    subtax_ids = json.loads(request.body)
    subtax_id2 = subtax_ids['subtax_id']
    obj = SubTax.objects.filter(id__in=subtax_id2).values('id', 'tax_id','code','name','glno')
    subtax_list_data = NWisefinList()
    for i in obj:
        data = {"id": i['id'], "tax_id": i['tax_id'],"code": i['code'],"name":i['name'],"glno":i['glno']}
        subtax_list_data.append(data)
    return HttpResponse(subtax_list_data.get(), content_type='application/json')


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_sub_tax_download(request):
    scope = request.scope
    subtax_service = SubTaxService(scope)
    user_id = request.user.id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    sub_tax_resp = subtax_service.fetch_subtax_list_download(request)
    data = json.loads(json.dumps(sub_tax_resp.__dict__, default=dictdefault))['data']
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
    worksheet.write_string(2, 2, 'Sub Tax master excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="SubTax master.xlsx"'
    logger.info("Sub_Tax_master_Download Data:"+str(datetime.now()))
    return response
