import io
import json
from datetime import datetime

import pandas as pd
from django.core.files.base import ContentFile

from masterservice.models import Commodity
from masterservice.util.masterutil import dictdefault
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from masterservice.service.commodityservice import CommodityService
from masterservice.data.request.commodityrequest import CommodityRequest
from userservice.service.employeeservice import EmployeeService

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])

def create_commodity(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        commodity_data = json.loads(request.body)
        commodity_obj = CommodityRequest(commodity_data)
        # user_id = request.user.id
        # emp_id = emp_service.get_empid_from_userid(user_id)
        commodity_service = CommodityService(scope)
        response_obj = commodity_service.create_Commodity(commodity_obj, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response
    elif request.method == 'GET':
        return fetch_commodity_list(request)

def fetch_commodity_list(request):
    scope = request.scope
    emp_id = request.employee_id
    # emp_service = EmployeeService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    # query = request.GET.get('query', None)
    # user_id = request.user.id
    # emp_id = emp_service.get_empid_from_userid(user_id)
    commodity_service = CommodityService(scope)
    response_obj = commodity_service.fetch_Commodity_list(request,vys_page, emp_id)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def commodity_download(request):
    scope = request.scope
    commodity_service = CommodityService(scope)
    user_id = request.user.id
    response_obj = commodity_service.fetch_commodity_download(request, user_id)
    data = json.loads(json.dumps(response_obj.__dict__, default=dictdefault))['data']
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
    worksheet.write_string(2, 2, 'Commodity Master Excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="Commodity Master.xlsx"'
    logger.info("Test_Download Data:")
    return response

@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_commodity(request, commodity_id):
    if request.method == 'GET':
        # user_id = request.user.id
        scope = request.scope
        emp_id = request.employee_id
        # emp_service = EmployeeService(scope)
        # emp_id = emp_service.get_empid_from_userid(user_id)
        commodity_service = CommodityService(scope)
        resp_obj = commodity_service.fetch_Commodity(commodity_id, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_commodity(request, commodity_id)

def delete_commodity(request, commodity_id):
    user_id = request.employee_id
    scope = request.scope
    emp_id = request.employee_id
    # emp_service = EmployeeService(scope)
    # emp_id = emp_service.get_empid_from_userid(user_id)
    commodity_service = CommodityService(scope)
    resp_obj = commodity_service.delete_Commodity(commodity_id,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def commoditysearch(request):
    name = request.GET.get('name')
    code = request.GET.get('code')
    query = {"name": name, "code": code}
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    scope = request.scope
    commodity_service = CommodityService(scope)
    resp_obj = commodity_service.search_CommodityAll(vys_page, query)
    return HttpResponse(resp_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def update_commodityStatus(request,commodity_id):
    # user_id = request.user.id
    scope = request.scope
    emp_id = request.employee_id
    # emp_service = EmployeeService(scope)
    # emp_id = emp_service.get_empid_from_userid(user_id)
    status =request.GET.get('status')
    commodity_service = CommodityService(scope)
    resp_obj = commodity_service.UpdateStatus_Commodity(commodity_id,status,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_commodity_mtom(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        commodity_data = json.loads(request.body)
        logger.info("commodity_mtom json data" +str(commodity_data))
        commodity_obj = CommodityRequest(commodity_data)
        # user_id = request.user.id
        # emp_service = EmployeeService(scope)
        # emp_id = emp_service.get_empid_from_userid(user_id)
        commodity_service = CommodityService(scope)
        response_obj = commodity_service.create_Commodity_mtom(commodity_obj, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def commodity_get(request):
    commodity_data = json.loads(request.body)
    scope = request.scope
    commodity_service = CommodityService(scope)
    resp_obj = commodity_service.commodity_get(commodity_data)
    # commodityId_arr = commodity_data['commodity_id']
    # commodity = Commodity.objects.filter(id__in = commodityId_arr).values('id', 'code', 'name', 'status')
    # commodity_list_data = NWisefinList()
    # for i in commodity:
    #     data = {"id": i['id'],
    #             "code": i['code'],
    #             "status": i['status'],
    #             "name": i['name']}
    #     commodity_list_data.append(data)
    return HttpResponse(resp_obj, content_type='application/json')
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_commoditydata_delmat(request, commodity_id):
    scope = request.scope
    commodity_service = CommodityService(scope)
    resp_obj = commodity_service.fetch_commoditys(commodity_id)
    # commodity = Commodity.objects.get(id=commodity_id)
    # commodity_data = {"id": commodity.id, "code": commodity.code, "name": commodity.name}
    # employee_dic = json.dumps(commodity_data, indent=4)
    return HttpResponse(json.dumps(resp_obj), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_commoditydata(request, commodity_id):
    scope = request.scope
    commodity_service = CommodityService(scope)
    resp_obj = commodity_service.fetch_commoditys(commodity_id)
    # commodity = Commodity.objects.get(id=commodity_id)
    # commodity_data = {"id": commodity.id, "code": commodity.code, "name": commodity.name}
    # employee_dic = json.dumps(commodity_data, indent=4)
    return HttpResponse(resp_obj, content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_commoditycode(request, commodity_code):
    scope = request.scope
    commodity_service = CommodityService(scope)
    resp_obj = commodity_service.get_commoditycode(commodity_code)
    # commodity = Commodity.objects.get(code=commodity_code)
    # commodity_data = {"id": commodity.id, "code": commodity.code, "name": commodity.name}
    employee_dic = json.dumps(resp_obj, indent=4)
    return HttpResponse(employee_dic, content_type='application/json')


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def searchcommodity(request):
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    scope = request.scope
    emp_id = request.employee_id
    commodity_service = CommodityService(scope)
    # emp_service = EmployeeService(scope)
    query = request.GET.get('query')
    # user_id = request.user.id
    # emp_id = emp_service.get_empid_from_userid(user_id)
    resp_obj = commodity_service.search_Commodity(vys_page, emp_id, query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_commodityname(request):
    scope = request.scope
    commodity_service = CommodityService(scope)
    query = request.GET.get('query')
    resp_obj = commodity_service.search_commodityname(query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

#microtomicro New
#commodity get
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_commoditys(request,commodity_id):
    commodity = Commodity.objects.get(id=commodity_id)
    comm_data = {"id": commodity.id, "code": commodity.code, "name": commodity.name}
    comodity_dic = json.dumps(comm_data, indent=4)
    return HttpResponse(comodity_dic, content_type='application/json')
#commodity getlist
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_commoditylist(request):
    commo_id1 = json.loads(request.body)
    commo_id2 = commo_id1['commo_id1']
    obj = Commodity.objects.filter(id__in=commo_id2).values('id', 'name')
    ecf_list_data = NWisefinList()
    for i in obj:
        data = {"id": i['id'], "name": i['name']}
        ecf_list_data.append(data)
    return HttpResponse(ecf_list_data.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def commodity_name(request):
    query = request.GET.get('query', None)
    obj = Commodity.objects.filter(name__icontains=query).values('id', 'name')
    ecf_list_data = NWisefinList()
    for i in obj:
        data = {"id": i['id'], "name": i['name']}
        ecf_list_data.append(data)
    return HttpResponse(ecf_list_data.get(), content_type='application/json')

#prpo
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_commoditycode(request):
    query = request.GET.get('query', None)
    commodity = Commodity.objects.get(code=query)
    commodity_data = {"id": commodity.id, "code": commodity.code, "name": commodity.name}
    employee_dic = json.dumps(commodity_data, indent=4)
    return HttpResponse(employee_dic, content_type='application/json')

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_commoditycode(request):
    code = request.GET.get('query', None)
    scope = request.scope
    commodity_service = CommodityService(scope)
    resp_obj = commodity_service.fetch_commoditycode(code)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response