import io
import json
from datetime import datetime

import pandas as pd
from django.core.files.base import ContentFile
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from nwisefin.settings import logger
from masterservice.util.masterutil import dictdefault
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from masterservice.data.request.producttyperequest import  ProductypeRequest
from masterservice.service.producttypeservice import ProducttypeService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.service.employeeservice import EmployeeService



@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_producttype(request):
    if request.method == 'POST':
        producttype_obj=json.loads(request.body)
        scope=request.scope
        print(producttype_obj)
        user_id = request.employee_id
        protypeobj=ProductypeRequest(producttype_obj)
        producttype_service=ProducttypeService(scope)
        resp_obj=producttype_service.create_producttype(protypeobj, user_id)
        response=HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_pdttype_list(request)

def fetch_pdttype_list(request):
    scope = request.scope
    producttype_service=ProducttypeService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj=producttype_service.pdttype_list(vys_page)
    response=HttpResponse(resp_obj.get(), content_type='application/json')
    return response


@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_producttype(request,producttype_id):
    if request.method == 'GET':
        scope=request.scope
        producttype_service = ProducttypeService(scope)
        resp_obj = producttype_service.fetch_producttype(producttype_id)
        resp_obj = HttpResponse(resp_obj.get(), content_type="application/json")
        return resp_obj
    elif request.method == 'DELETE':
        return delete_producttype(request, producttype_id)

def delete_producttype(request, producttype_id):
    scope = request.scope
    producttype_service = ProducttypeService(scope)
    user_id = request.employee_id
    resp_obj = producttype_service.delete_producttype(producttype_id,user_id)
    resp_obj = HttpResponse(resp_obj.get(), content_type='application/json')
    return resp_obj



@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def producttype_search(request):
    scope = request.scope
    producttype_service=ProducttypeService(scope)
    query = request.GET.get('query',None)
    productcat_id = request.GET.get('productcat_id',None)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj=producttype_service.producttype_search_list(vys_page,query,productcat_id)
    response=HttpResponse(resp_obj.get(), content_type='application/json')
    return response

@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_producttype_mtom(request):
    if request.method == 'POST':
        producttype_obj=json.loads(request.body)
        scope=request.scope
        user_id = request.employee_id
        action = request.GET.get('action')
        protypeobj=ProductypeRequest(producttype_obj)
        producttype_service=ProducttypeService(scope)
        resp_obj=producttype_service.create_producttype_mtom(protypeobj,action, emp_id)
        response=HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_productype_download(request):
    scope = request.scope
    producttype_service = ProducttypeService(scope)
    user_id = request.user.id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    pdtype_resp = producttype_service.fetch_download_pdttype_list(request)
    data = json.loads(json.dumps(pdtype_resp.__dict__, default=dictdefault))['data']
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
    worksheet.write_string(2, 2, 'Product Type master excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="Product Type master.xlsx"'
    logger.info("ProductType_Download Data:"+str(datetime.now()))
    return response
