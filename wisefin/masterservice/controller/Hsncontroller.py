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
from masterservice.models import Hsn
from nwisefin.settings import logger
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from masterservice.data.request.Hsnrequest import  HsnRequest
from masterservice.service.Hsnservice import Hsnservice
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.service.employeeservice import EmployeeService



@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_hsn(request):
    if request.method == 'POST':
        scope = request.scope
        hsn_obj=json.loads(request.body)
        user_id = request.employee_id
        emp_service = EmployeeService(scope)
        hsn_obj=HsnRequest(hsn_obj)
        hsn_service=Hsnservice(scope)
        resp_obj=hsn_service.create_hsn(hsn_obj, user_id)
        response=HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_hsn_list(request)

def fetch_hsn_list(request):
    scope=request.scope
    hsn_service=Hsnservice(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj=hsn_service.fetch_hsn_list(vys_page)
    response=HttpResponse(resp_obj.get(), content_type='application/json')
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def hsn_taxrateget(request):
    if request.method == 'GET':
        scope=request.scope
        # print(subtax_id)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        hsn_service = Hsnservice(scope)
        resp_obj = hsn_service.hsn_taxrateget(request, vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_hsn(request,hsn_id):
    if request.method == 'GET':
        scope = request.scope
        hsn_service = Hsnservice(scope)
        resp_obj = hsn_service.fetch_hsn(hsn_id)
        resp_obj = HttpResponse(resp_obj.get(), content_type="application/json")
        return resp_obj
    elif request.method == 'DELETE':
        return delete_hsn(request, hsn_id)

def delete_hsn(request, hsn_id):
    scope=request.scope
    hsn_service = Hsnservice(scope)
    user_id = request.employee_id
    emp_service = EmployeeService(scope)
    emp_id = emp_service.get_empid_from_userid(user_id)
    resp_obj = hsn_service.delete_hsn(hsn_id,emp_id)
    resp_obj = HttpResponse(resp_obj.get(), content_type='application/json')
    return resp_obj

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_hsn(request):
    scope=request.scope
    hsn_service = Hsnservice(scope)
    query = request.GET.get('query')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = hsn_service.search_hsn(query,vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_hsn_mtom(request):
    if request.method == 'POST':
        scope = request.scope
        hsn_obj=json.loads(request.body)
        user_id = request.employee_id
        action = request.GET.get('action')
        emp_service = EmployeeService(scope)
        emp_id = emp_service.get_empid_from_userid(user_id)
        hsn_obj=HsnRequest(hsn_obj)
        hsn_service=Hsnservice(scope)
        resp_obj=hsn_service.create_hsn_mtom(hsn_obj,action, emp_id)
        response=HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_hsncode(request):
    scope=request.scope
    hsn_service = Hsnservice(scope)
    query = request.GET.get('query')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = hsn_service.search_hsncode(query, vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

#Get hsn
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_hsnone(request):
    scope=request.scope
    query = request.GET.get('query', None)
    x = query
    y = x.split("-")
    code = y[0]
    hsn = Hsn.objects.get(code=code)
    hsn_data = {"id": hsn.id, "code": hsn.code, "cgstrate": hsn.cgstrate,"sgstrate":hsn.sgstrate,"igstrate":hsn.igstrate}
    hsn_dic = json.dumps(hsn_data, indent=4)
    return HttpResponse(hsn_dic, content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_hsnone_ta(request):
    query = request.GET.get('query', None)
    x = query
    y = x.split("-")
    code = y[0]
    hsn = Hsn.objects.filter(code=code).first()
    if hsn is not None:
        hsn_data = {"id": hsn.id, "code": hsn.code, "cgstrate": hsn.cgstrate,"sgstrate":hsn.sgstrate,"igstrate":hsn.igstrate}
    else:
        hsn_data = {"id": None, "code": None, "cgstrate": None,"sgstrate":None,"igstrate":None}
    hsn_dic = json.dumps(hsn_data, indent=4)
    return HttpResponse(hsn_dic, content_type='application/json')


#Get hsn prpo
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_hsndata(request, hsn_id):
    hsn = Hsn.objects.get(id=hsn_id)
    hsn_data = {"id": hsn.id, "code": hsn.code, "cgstrate": hsn.cgstrate,
                "sgstrate": hsn.sgstrate,"igstrate": hsn.igstrate}
    hsn_dic = json.dumps(hsn_data, indent=4)
    return HttpResponse(hsn_dic, content_type='application/json')


# @api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def hsn_taxrateget(request):
#     if request.method == 'GET':
#         # print(subtax_id)
#         scope = request.scope
#         page = request.GET.get('page', 1)
#         page = int(page)
#         vys_page = NWisefinPage(page, 10)
#         hsn_service = Hsnservice(scope)
#         resp_obj = hsn_service.hsn_taxrateget(request, vys_page)
#         response = HttpResponse(resp_obj.get(), content_type="application/json")
#         return response

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def hsn_activate_inactivate(request):
    if request.method == 'POST':
        scope = request.scope
        hsn_service = Hsnservice(scope)
        obj = json.loads(request.body)
        hsn_obj = HsnRequest(obj)
        resp_obj = hsn_service.hsn_activate_inactivate(request,hsn_obj)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def hsn_get_iddata(request,hsn_id):
    if request.method == 'GET':
        scope = request.scope
        hsn_service = Hsnservice(scope)
        # hsn_obj = HsnRequest(obj)
        resp_obj = hsn_service.hsn_iddata(request,hsn_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_hsn_download(request):
    scope = request.scope
    hsn_service = Hsnservice(scope)
    user_id = request.user.id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    hsn_resp = hsn_service.fetch_hsn_list_download(request)
    data = json.loads(json.dumps(hsn_resp.__dict__, default=dictdefault))['data']
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
    worksheet.write_string(2, 2, 'Hsn master excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="Hsn master.xlsx"'
    logger.info("Hsn_Download Data:"+str(datetime.now()))
    return response


