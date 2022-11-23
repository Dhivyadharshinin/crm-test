#Uom
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
from masterservice.data.request.uomrequest import UomRequest
from masterservice.models import Uom
from masterservice.service.uomservice import UomService
from masterservice.util.masterutil import dictdefault
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.service.employeeservice import EmployeeService

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def uom(request):
    if request.method == 'POST':
        # user_id = request.employee_id
        scope = request.scope
        emp_id = request.employee_id
        # emp_service = EmployeeService(scope)
        # empid = emp_service.get_empid_from_userid(user_id)
        uom_obj = json.loads(request.body)
        uom_obj=UomRequest(uom_obj)
        uom_service = UomService(scope)
        resp_obj = uom_service.create_uom(uom_obj,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_uom_list(request)


def fetch_uom_list(request):
    user_id = request.employee_id
    scope = request.scope
    uom_service = UomService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = uom_service.fetch_uom_list(vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_uom(request, uom_id):
    if request.method == 'GET':
        # user_id = request.employee_id
        scope = request.scope
        emp_id = request.employee_id
        uom_service = UomService(scope)
        resp_obj = uom_service.fetch_uom(uom_id, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_uom(request, uom_id)


def delete_uom(request, uom_id):
    # user_id = request.employee_id
    scope = request.scope
    emp_id = request.employee_id
    uom_service = UomService(scope)
    resp_obj = uom_service.delete_uom(uom_id, emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def uom_search(request):
    scope = request.scope
    uom_service = UomService(scope)
    query = request.GET.get('query')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = uom_service.fetch_uom_search(vys_page,query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def uom_mtom(request):
    if request.method == 'POST':
        # user_id = request.employee_id
        scope = request.scope
        emp_id = request.employee_id
        # emp_service = EmployeeService(scope)
        # empid = emp_service.get_empid_from_userid(user_id)
        uom_obj = json.loads(request.body)
        action = request.GET.get('action')
        uom_obj=UomRequest(uom_obj)
        uom_service = UomService(scope)
        resp_obj = uom_service.create_uom_mtom(uom_obj,action,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


# prpo-micro to micro
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_uomdata(request, uom_id):
    catelog = Uom.objects.get(id=uom_id)
    catelog_data = {"id": catelog.id, "name": catelog.name}
    catelog_dic = json.dumps(catelog_data, indent=4)
    return HttpResponse(catelog_dic, content_type='application/json')

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_uom_download(request):
    scope = request.scope
    uom_service = UomService(scope)
    user_id = request.user.id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    uom_resp = uom_service.fetch_uom_download(request)
    data = json.loads(json.dumps(uom_resp.__dict__, default=dictdefault))['data']
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
    worksheet.write_string(2, 2, 'Uom master excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="Uom master.xlsx"'
    logger.info("Uom_Download Data:"+str(datetime.now()))
    return response
