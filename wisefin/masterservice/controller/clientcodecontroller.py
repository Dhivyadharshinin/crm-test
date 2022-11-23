import io
import json
from datetime import datetime

import pandas as pd
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from masterservice.data.request.clientcoderequest import ClientcodeRequest
from masterservice.service.clientcodeservice import ClientcodeService
from masterservice.util.masterutil import dictdefault
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.service.api_service import ApiService
#test

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_clientcode(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        client_service = ClientcodeService(scope)
        client_data = json.loads(request.body)
        client_obj = ClientcodeRequest(client_data)
        resp_obj = client_service.create_clientcode(client_obj, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return clientcode_list(request)

def clientcode_list(request):
    scope = request.scope
    client_service = ClientcodeService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = client_service.fetch_clientlist(request,vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def clientcode_activate_inactivate(request):
    if request.method == 'POST':
        scope = request.scope
        client_service = ClientcodeService(scope)
        client_data = json.loads(request.body)
        client_obj = ClientcodeRequest(client_data)
        resp_obj = client_service.clientcode_activate_inactivate(request,client_obj)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def clientcode_download(request):
    scope = request.scope
    client_service = ClientcodeService(scope)
    user_id = request.user.id
    resp_obj = client_service.fetch_clientcode_download(request)
    data = json.loads(json.dumps(resp_obj.__dict__, default=dictdefault))['data']
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
    worksheet.write_string(2, 2, 'Client Master Excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="Client Master.xlsx"'
    logger.info("Test_Download Data:")
    return response
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def rm_drop_down(request):
    scope = request.scope
    common_serv=ApiService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    user_id = request.employee_id
    query = request.GET.get('query')
    resp_obj=common_serv.fetch_rm_name(request, query,vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

