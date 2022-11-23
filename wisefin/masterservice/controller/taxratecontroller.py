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
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from masterservice.data.request.taxraterequest import TaxRateResquest
from masterservice.service.taxrateservice import TaxRateService
from masterservice.service.subtaxservice import SubTaxService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.service.employeeservice import EmployeeService

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def taxrate(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        taxrate_service = TaxRateService(scope)
        # user_id = request.employee_id
        taxrate_data = json.loads(request.body)
        taxrate_obj = TaxRateResquest(taxrate_data)
        # emp_service = EmployeeService(scope)
        # empid = emp_service.get_empid_from_userid(user_id)
        resp_obj = taxrate_service.create_taxrate(taxrate_obj, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_taxrate_list(request)


def fetch_taxrate_list(request):
    scope = request.scope
    taxrate_service = TaxRateService(scope)
    user_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = taxrate_service.fetch_taxrate_list(vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


def delete_taxrate(request, taxrate_id):
    scope = request.scope
    emp_id = request.employee_id
    taxrate_service = TaxRateService(scope)
    # user_id = request.employee_id
    resp_obj = taxrate_service.delete_taxrate(taxrate_id, emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_taxrate(request, taxrate_id):
    if request.method == 'GET':
        scope = request.scope
        emp_id = request.employee_id
        taxrate_service = TaxRateService(scope)
        # user_id = request.employee_id
        resp_obj = taxrate_service.fetch_taxrate(taxrate_id, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_taxrate(request, taxrate_id)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def taxrate_search(request):
    scope = request.scope
    taxrate_service = TaxRateService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query',None)
    name = request.GET.get('name',None)
    subtax_id = request.GET.get('subtax_id',None)
    resp_obj = taxrate_service.fetch_taxrate_search(vys_page,query,subtax_id,name)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def taxrate_mtom(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        taxrate_service = TaxRateService(scope)
        action = request.GET.get('action')
        # user_id = request.employee_id
        taxrate_data = json.loads(request.body)
        taxrate_obj = TaxRateResquest(taxrate_data)
        emp_service = EmployeeService(scope)
        resp_obj = taxrate_service.create_taxrate_mtom(taxrate_obj,action, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def taxrate_inactive(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        taxrate_service = TaxRateService(scope)
        # user_id = request.employee_id
        taxrate_data = json.loads(request.body)
        # emp_service = EmployeeService(scope)
        # empid = emp_service.get_empid_from_userid(user_id)
        resp_obj = taxrate_service.inactive_taxrate(taxrate_data, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


#subtax getlist
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_taxratelist(request):
    subtax_ids = json.loads(request.body)
    subtax_id2 = subtax_ids['subtax_id']
    from masterservice.models.mastermodels import TaxRate
    obj = TaxRate.objects.filter(subtax_id__in=subtax_id2).values('id', 'subtax_id','code','name','rate')
    taxrate_list_data = NWisefinList()
    for i in obj:
        data = {"id": i['id'], "subtax_id": i['subtax_id'],"code": i['code'],"name":i['name'],"rate":i['rate']}
        taxrate_list_data.append(data)
    return HttpResponse(taxrate_list_data.get(), content_type='application/json')

@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def taxrate_active_inactive(request):
    if request.method == 'POST':
        scope=request.scope
        taxrate_service = TaxRateService(scope)
        user_id = request.employee_id
        taxrate_data = json.loads(request.body)
        taxrate_obj = TaxRateResquest(taxrate_data)
        emp_service = EmployeeService(scope)
        empid = emp_service.get_empid_from_userid(user_id)
        resp_obj = taxrate_service.taxrate_active_inactive(request,taxrate_obj,empid)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_tax_rate_download(request):
    scope = request.scope
    taxrate_service = TaxRateService(scope)
    user_id = request.user.id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    tax_rate = taxrate_service.fetch_taxrate_list_download(request)
    data = json.loads(json.dumps(tax_rate.__dict__, default=dictdefault))['data']
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
    worksheet.write_string(2, 2, 'Taxrate master excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="Taxrate master.xlsx"'
    logger.info("Tax_rate_Download Data:"+str(datetime.now()))
    return response

