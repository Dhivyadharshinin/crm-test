import io
from datetime import datetime

import pandas as pd
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.defaultscopeservice import DefaultScopeService
from masterservice.util.masterutil import dictdefault
from nwisefin.settings import logger
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from vendorservice.util.vendorutil import get_classification_list, get_group_list, get_org_type_list, get_type_list, \
    get_composite_list, get_risk_type_list, search_org_type, search_composite_list
from django.http import HttpResponse
from masterservice.data.request.risktyperequest import RiskTypeRequest
from masterservice.service.vendorutilservice import VendorUtilService, MasterTableService, MasterDropDown
from utilityservice.data.response.nwisefinpage import NWisefinPage
import json


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_type_list(request):
    resp_obj = get_type_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_org_type_list(request):
    resp_obj = get_org_type_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_group_list(request):
    resp_obj = get_group_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_classification_list(request):
    resp_obj = get_classification_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_composite_list(request):
    resp_obj = get_composite_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_risk_type(request):
    resp_obj = get_risk_type_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


# risk type
@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_risk_type(request):
    if request.method == 'POST':
        employee_id = request.employee_id
        scope = request.scope
        risk_obj = json.loads(request.body)
        risk_obj = RiskTypeRequest(risk_obj)
        risk_service = VendorUtilService(scope)
        resp_obj = risk_service.create_risk_type(risk_obj,employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

    elif request.method == 'GET':
        resp_data = fetch_risktype_list(request)
        return resp_data


def fetch_risktype_list(request):
    scope = request.scope
    risk_service = VendorUtilService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query', None)
    risk_obj = risk_service.fetch_risktype_list(query,vys_page)
    response = HttpResponse(risk_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def risktype_download(request):
    scope = request.scope
    risk_service = VendorUtilService(scope)
    user_id = request.user.id
    risk_obj = risk_service.fetch_risktype_download(request)
    data = json.loads(json.dumps(risk_obj.__dict__, default=dictdefault))['data']
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
    worksheet.write_string(2, 2, 'Risk Type Master Excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="Risk Type Master.xlsx"'
    logger.info("Test_Download Data:")
    return response

@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_risktype(request, risk_id):
    if request.method == 'GET':
        scope = request.scope
        risk_service = VendorUtilService(scope)
        risk_obj = risk_service.fetch_risktype(risk_id)
        response = HttpResponse(risk_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        resp_data = delete_risktype(request,risk_id)
        return resp_data


def delete_risktype(request, risk_id):
    scope = request.scope
    risk_service = VendorUtilService(scope)
    risk_obj = risk_service.delete_risktype(risk_id)
    response = HttpResponse(risk_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_org_type_list(request):
    query = request.GET.get('query')
    resp_obj = search_org_type(query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_composite(request):
    query = request.GET.get('query')
    resp_obj = search_composite_list(query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'POST'])
def get_masters_data(request):
    scope_serv = DefaultScopeService()
    scope = scope_serv.set_default_scope(request)
    type = request.GET.get('type', None)
    data_id = request.GET.get('id', None)
    mst_serv = MasterTableService(scope)
    resp = mst_serv.get_masters_data(type, data_id)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'POST'])
def get_masters_data_list(request):
    scope_serv = DefaultScopeService()
    scope = scope_serv.set_default_scope(request)
    risk_obj = json.loads(request.body)
    type = risk_obj['type']
    id_arr = risk_obj['id_arr']
    mst_serv = MasterTableService(scope)
    resp = mst_serv.get_masters_data_list(type, id_arr)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
def masters_drop_down(request):
    type = request.GET.get('type', None)
    query = request.GET.get('query', None)
    page = request.GET.get('page', 1)
    state_id = request.GET.get('state_id', None)
    tax_id = request.GET.get('tax_id', None)
    name = request.GET.get('name', None)
    subtax_id = request.GET.get('subtax_id', None)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    scope_serv = DefaultScopeService()
    scope = scope_serv.set_default_scope(request)
    mst_serv = MasterDropDown(scope)
    params = {
        "type": type,
        "query": query,
        "vys_page": vys_page,
        "state_id": state_id,
        "tax_id": tax_id,
        "name": name,
        "subtax_id": subtax_id
    }
    resp = mst_serv.masters_drop_down(params)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response
