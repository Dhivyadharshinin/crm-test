import datetime
import io
import json

import pandas as pd
from datetime import datetime
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from masterservice.util.masterutil import dictdefault
from nwisefin.settings import logger
from masterservice.util.masterutil import get_category_type_list
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from masterservice.data.request.apcategoryrequest import ApcategoryRequest
from masterservice.service.apcategoryservice import CategoryService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.service.employeeservice import EmployeeService
from masterservice.models.mastermodels import APsubcategory
from utilityservice.data.response.nwisefinlist import NWisefinList

#category
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def Apcategory1(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        categoryservice = CategoryService(scope)
        cat_obj = json.loads(request.body)
        Category_obj = ApcategoryRequest(cat_obj)
        user_id = request.employee_id
        scope = request.scope
        emp_service = EmployeeService(scope)
        empid = emp_service.get_empid_from_userid(user_id)
        resp_obj = categoryservice.create_category(Category_obj, empid)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
       return fetch_category_list(request)
def fetch_category_list(request):
        scope = request.scope
        categoryservice = CategoryService(scope)
        user_id = request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = categoryservice.fetch_category_list(vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_category(request,category_id):
    if request.method == 'GET':
        scope = request.scope
        categoryservice = CategoryService(scope)
        user_id = request.employee_id
        resp_obj = categoryservice.fetchcategory(category_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_category(request,category_id)
def delete_category(request, category_id):
    scope = request.scope
    emp_id = request.employee_id
    categoryservice = CategoryService(scope)
    # user_id = request.user.id
    resp_obj = categoryservice.delete_category( category_id,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def Apcategory_search(request):
    scope = request.scope
    categoryservice = CategoryService(scope)
    user_id = request.employee_id
    query=request.GET.get('query')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = categoryservice.fetch_category_search_list(query, vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def Apcategory_search_fa(request):
    scope = request.scope
    categoryservice = CategoryService(scope)
    user_id = request.employee_id
    query=request.GET.get('query')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = categoryservice.fetch_category_search_list(query, vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def categorysearch(request):
    scope = request.scope
    categoryservice = CategoryService(scope)
    name = request.GET.get('name')
    no = request.GET.get('no')
    query = {"name": name, "no": no}
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = categoryservice.categorySearch_list(vys_page,query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def categorysearch_mst(request):
    scope = request.scope
    categoryservice = CategoryService(scope)
    name = request.GET.get('name')
    no = request.GET.get('no')
    # query = {"name": name, "no": no}
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = categoryservice.categorySearch_list_mst(vys_page,request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def updateisasset(request):
    scope = request.scope
    emp_id = request.employee_id
    categoryservice = CategoryService(scope)
    cat_obj = json.loads(request.body)
    Category_obj = ApcategoryRequest(cat_obj)
    user_id = request.employee_id
    # emp_service = EmployeeService()
    # empid = emp_service.get_empid_from_userid(user_id)
    resp_obj = categoryservice.UpdateIsasset(Category_obj, user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def categorylist(request):
    scope = request.scope
    categoryservice = CategoryService(scope)
    user_id = request.user.id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = categoryservice.fetch_prcategorylist(vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def categorylistinactive(request):
    scope = request.scope
    categoryservice = CategoryService(scope)
    user_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = categoryservice.categorylistInactive(vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def categorylistactive(request):
    scope = request.scope
    categoryservice = CategoryService(scope)
    user_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = categoryservice.categorylistActive(vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def updateStatus(request, category_id):
    scope = request.scope
    categoryservice = CategoryService(scope)
    status = request.GET.get('status')
    user_id = request.employee_id
    # emp_service = EmployeeService()
    # empid = emp_service.get_empid_from_userid(user_id)
    resp_obj = categoryservice.UpdateStatus(category_id, status, user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def categorytype(request):
    resp_obj = get_category_type_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def categoryname_search(request):
    scope = request.scope
    categoryservice = CategoryService(scope)
    user_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query=request.GET.get('query')
    resp_obj = categoryservice.categoryname_search(query, vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def Apcat_search(request):
    scope = request.scope
    categoryservice = CategoryService(scope)
    user_id = request.employee_id
    query=request.GET.get('query',None)
    resp_obj = categoryservice.fetch_cat_search_list(query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def Apcategory_mtom(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        categoryservice =CategoryService(scope)
        cat_obj = json.loads(request.body)
        logger.info("cat_json"+ str(cat_obj))
        Category_obj = ApcategoryRequest(cat_obj)
        user_id = request.employee_id
        action = request.GET.get('action')
        emp_service = EmployeeService(scope)
        empid = emp_service.get_empid_from_userid(user_id)
        resp_obj = categoryservice.create_category_mtom(Category_obj,action, empid)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def category_income(request):
    scope = request.scope
    categoryservice = CategoryService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query')
    resp_obj = categoryservice.category_income(query, vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_apsubcategory(request):
    id_obj = json.loads(request.body)
    scope=request.scope
    categoryservice = CategoryService(scope)
    response = categoryservice.get_apsubcategory(id_obj)
    # obj = APsubcategory.objects.filter(id__in=id_obj["subcategory_id"]).values('id','name','glno')
    # arr = []
    # for i in obj:
    #     data = {"id": i['id'], "name": i['name'],"gl":i['glno']}
    #     arr.append(data)
    # vendor_dic = json.dumps(arr, indent=4)
    return HttpResponse(response, content_type='application/json')
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_apsubcategory_data(request):
    id_obj = json.loads(request.body)
    scope = request.scope
    categoryservice = CategoryService(scope)
    res_obj = categoryservice.get_apsubcategory_data(id_obj)
    # obj = APsubcategory.objects.filter(id__in=id_obj["subcategory_id"])
    # arr = []
    # for i in obj:
    #     arr.append(i)
    # vendor_dic = json.dumps(arr, indent=4,default=dictdefault)
    return HttpResponse(res_obj, content_type='application/json')

# micro to micro New
# Get apcategory
# @csrf_exempt
# @api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def fetch_apcategory(request,apcat_code):
#     apcategory = Apcategory.objects.get(code=apcat_code)
#     apcategory_data = {"id": apcategory.id, "code": apcategory.code, "name": apcategory.name}
#     apcategory_dic = json.dumps(apcategory_data, indent=4)
#     return HttpResponse(apcategory_dic, content_type='application/json')
# #apcategory getlist
# @csrf_exempt
# @api_view(['POST'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def fetch_apcategorylist(request):
#     apcategory_ids = json.loads(request.body)
#     apcategory_id2 = apcategory_ids['apcat_id']
#     obj = Apcategory.objects.filter(code__in=apcategory_id2).values('id', 'name','code')
#     apcategory_list_data = NWisefinList()
#     for i in obj:
#         data = {"id": i['id'], "name": i['name'],"code": i['code']}
#         apcategory_list_data.append(data)
#     return HttpResponse(apcategory_list_data.get(), content_type='application/json')
#


@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def apcategory_active_inactivate(request):
    if request.method == 'POST':
        scope=request.scope
        taxrate_service = CategoryService(scope)
        user_id = request.employee_id
        apcate_data = json.loads(request.body)
        apcat_obj = ApcategoryRequest(apcate_data)
        emp_service = EmployeeService(scope)
        empid = emp_service.get_empid_from_userid(user_id)
        resp_obj = taxrate_service.apcategory_active_inactivate(request,apcat_obj,empid)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_apcategory_download(request):
    scope = request.scope
    categoryservice = CategoryService(scope)
    user_id = request.user.id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    cat_resp = categoryservice.fetch_category_download(request)
    data = json.loads(json.dumps(cat_resp.__dict__, default=dictdefault))['data']
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
    worksheet.write_string(2, 2, 'APcategory excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="ApCategory master.xlsx"'
    logger.info("APcat_Download Data:"+str(datetime.now()))
    return response