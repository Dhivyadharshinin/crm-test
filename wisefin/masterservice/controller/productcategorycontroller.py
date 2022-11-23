import io
import json
from datetime import datetime

import pandas as pd
from django.core.files.base import ContentFile
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from masterservice.util.masterutil import dictdefault
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from nwisefin.settings import logger
from masterservice.data.request.productcategoryrequest import  ProductcategoryRequest
from masterservice.service.productcategoryservice import Productcategoryservice
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.service.employeeservice import EmployeeService



@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_productcat(request):
    if request.method == 'POST':
        scope = request.scope
        productcat_obj=json.loads(request.body)
        emp_id = request.employee_id
        productcat_obj=ProductcategoryRequest(productcat_obj)
        productcat_service=Productcategoryservice(scope)
        resp_obj=productcat_service.create_productcatprocess(productcat_obj, emp_id)
        # response=HttpResponse(resp_obj, content_type="application/json")
        # print(response)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_pdtcat_list(request)

def fetch_pdtcat_list(request):
    scope = request.scope
    productcat_service=Productcategoryservice(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj=productcat_service.pdtcat_list(vys_page)
    response=HttpResponse(resp_obj.get(), content_type='application/json')
    return response


@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_productcat(request,productcat_id):
    if request.method == 'GET':
        scope = request.scope
        productcat_service = Productcategoryservice(scope)
        resp_obj = productcat_service.fetch_productcat(productcat_id)
        resp_obj = HttpResponse(resp_obj.get(), content_type="application/json")
        return resp_obj
    elif request.method == 'DELETE':
        return delete_productcat(request, productcat_id)

def delete_productcat(request, productcat_id):
    scope = request.scope
    productcat_service = Productcategoryservice(scope)
    user_id = request.employee_id
    resp_obj = productcat_service.delete_productcat(productcat_id,user_id)
    resp_obj = HttpResponse(resp_obj.get(), content_type='application/json')
    return resp_obj



def productcat_search(request):
    scope = request.scope
    productcat_service=Productcategoryservice(scope)
    query = request.GET.get('query', None)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj=productcat_service.productcat_search_list(vys_page,query)
    response=HttpResponse(resp_obj.get(), content_type='application/json')
    return response

@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_productcat_mtom(request):
    if request.method == 'POST':
        scope = request.scope
        productcat_obj=json.loads(request.body)
        user_id = request.employee_id
        action = request.GET.get('action')
        productcat_obj=ProductcategoryRequest(productcat_obj)
        productcat_service=Productcategoryservice(scope)
        resp_obj=productcat_service.create_productcatprocess_mtom(productcat_obj,action, user_id)
        response=HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_productcat_download(request):
    scope = request.scope
    productcat_service=Productcategoryservice(scope)
    user_id = request.user.id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    pdtcat_resp = productcat_service.fetch_product_category_download(request)
    data = json.loads(json.dumps(pdtcat_resp.__dict__, default=dictdefault))['data']
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
    worksheet.write_string(2, 2, 'Product master excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="ProductCategory master.xlsx"'
    logger.info("ProductCat_Download Data:"+str(datetime.now()))
    return response
