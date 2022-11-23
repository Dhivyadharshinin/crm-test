import datetime
import io

import pandas as pd
from datetime import datetime
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from masterservice.util.masterutil import dictdefault
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from masterservice.data.request.apsubcategoryrequest import ApsubcategoryRequest
from masterservice.service.apsubcategoryservice import SubcategoryService
from masterservice.service.apcategoryservice import CategoryService
from nwisefin.settings import logger
import json
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.service.employeeservice import EmployeeService
from masterservice.models.mastermodels import Apcategory
from masterservice.models import APsubcategory
from utilityservice.data.response.nwisefinlist import NWisefinList

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def Apsubcategory(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        subcategoryservice =SubcategoryService(scope)
        subcat_obj = json.loads(request.body)
        Subcategory_obj = ApsubcategoryRequest(subcat_obj)
        # user_id = request.user.id
        # emp_service = EmployeeService(scope)
        # empid = emp_service.get_empid_from_userid(user_id)
        resp_obj = subcategoryservice.create_subcategory(Subcategory_obj, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
       return fetch_subcategory_list(request)
def fetch_subcategory_list(request):
        scope = request.scope
        subcategoryservice = SubcategoryService(scope)
        user_id = request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = subcategoryservice.fetch_subcategory_list(vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_subcategory(request,subcategory_id):
    if request.method == 'GET':
        scope = request.scope
        subcategoryservice = SubcategoryService(scope)
        user_id = request.employee_id
        resp_obj = subcategoryservice.fetchsubcategory(subcategory_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_subcategory(request,subcategory_id)
def delete_subcategory(request,subcategory_id):
    scope = request.scope
    emp_id = request.employee_id
    subcategoryservice = SubcategoryService(scope)
    # user_id = request.user.id
    resp_obj = subcategoryservice.delete_subcategory(subcategory_id,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def apsubcategory_search(request):
    scope = request.scope
    subcategoryservice = SubcategoryService(scope)
    user_id = request.employee_id
    query = request.GET.get('query')
    category = request.GET.get('category_id')
    resp_obj = subcategoryservice.fetch_subcategory_search(query,category)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def editsubcategory(request):
    scope = request.scope
    user_id = request.employee_id
    subcategoryservice = SubcategoryService(scope)
    subcat_obj = json.loads(request.body)
    Subcategory_obj = ApsubcategoryRequest(subcat_obj)
    # user_id = request.user.id
    # emp_service = EmployeeService()
    # empid = emp_service.get_empid_from_userid(user_id)
    resp_obj = subcategoryservice.edit_subcategory(Subcategory_obj, user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def subcategorylist(request):
    scope = request.scope
    subcategoryservice = SubcategoryService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = subcategoryservice.fetch_subcategorylist( vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def subcategorylistinactive(request):
    scope = request.scope
    subcategoryservice = SubcategoryService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = subcategoryservice.subcategorylistInactive( vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def subcategorylistactive(request):
    scope = request.scope
    subcategoryservice = SubcategoryService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = subcategoryservice.subcategorylistactive( vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_subcategoryname(request):
    scope = request.scope
    subcategoryservice = SubcategoryService(scope)
    # Subcategory_obj = json.loads(request.body)
    page = request.GET.get('page', 1)
    name = request.GET.get('name', None)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = subcategoryservice.fetch_subcat_name(name, vys_page)
    return HttpResponse(resp_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def updatestatus(request,subcategory_id):
    scope = request.scope
    emp_id = request.employee_id
    subcategoryservice = SubcategoryService(scope)
    # user_id = request.user.id
    status =request.GET.get('status')
    resp_obj = subcategoryservice.UpdateStatus(subcategory_id,status,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def subcategorysearch(request):
    scope = request.scope
    emp_id = request.employee_id
    subcategoryservice = SubcategoryService(scope)
    subcategory_obj = json.loads(request.body)
    # user_id = request.user.id
    # emp_id = emp_service.get_empid_from_userid(user_id)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = subcategoryservice.search_subcategory(vys_page, subcategory_obj, emp_id)
    return HttpResponse(resp_obj.get(), content_type='application/json')
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def subcategorysearch_mst(request):
    scope = request.scope
    emp_id = request.employee_id
    subcategoryservice = SubcategoryService(scope)
    # subcategory_obj = json.loads(request.body)
    # user_id = request.user.id
    # emp_id = emp_service.get_empid_from_userid(user_id)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = subcategoryservice.search_subcategory_mst(vys_page, request, emp_id)
    return HttpResponse(resp_obj.get(), content_type='application/json')
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def apsubcat_search(request):
    scope = request.scope
    subcategoryservice = SubcategoryService(scope)
    user_id = request.employee_id
    query = request.GET.get('query',None)
    category = request.GET.get('category_id',None)
    resp_obj = subcategoryservice.fetch_subcat_search(query,category)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def Apsubcategory_mtom(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        subcategoryservice =SubcategoryService(scope)
        subcat_obj = json.loads(request.body)
        logger.info("cat_json" + str(subcat_obj))
        Subcategory_obj = ApsubcategoryRequest(subcat_obj)
        # user_id = request.user.id
        # emp_service = EmployeeService(scope)
        # empid = emp_service.get_empid_from_userid(user_id)
        resp_obj = subcategoryservice.create_subcategory_mtom(Subcategory_obj, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def catsubsearch_credit(request):
    scope = request.scope
    subcategoryservice =SubcategoryService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query')
    category_id = request.GET.get('category_id', None)
    resp_obj = subcategoryservice.search_incCredit(query, category_id, vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def catsubsearch_debit(request):
    scope = request.scope
    subcategoryservice =SubcategoryService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query')
    resp_obj = subcategoryservice.search_incDebit(query, vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def subcatname_search(request):
    scope = request.scope
    subcategoryservice = SubcategoryService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query')
    category_id = request.GET.get('category_id', None)
    resp_obj = subcategoryservice.subcatname_search(query, category_id, vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_apcategory(request):
    id_obj = json.loads(request.body)
    scope = request.scope
    subcategoryservice = SubcategoryService(scope)
    res_obj = subcategoryservice.get_apcategory(id_obj)
    # obj = Apcategory.objects.filter(id__in=id_obj["category_id"]).values('id','name','isasset','no')
    # arr = []
    # for i in obj:
    #     data = {"id": i['id'], "no": i['no'],
    #             "name": i['name'], "isasset": i['isasset']}
    #     arr.append(data)
    # vendor_dic = json.dumps(arr, indent=4)
    return HttpResponse(res_obj, content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_apcategorydata(request, category_id):
    scope = request.scope
    subcategoryservice = SubcategoryService(scope)
    res_obj = subcategoryservice.fetch_apcategorydata(category_id)
    # obj = Apcategory.objects.get(id=category_id)
    # emp_data = {"id": obj.id,
    #             "code": obj.code,
    #             "name": obj.name,
    #             "isasset": obj.isasset,
    #             "no": obj.no}
    # employee_dic = json.dumps(emp_data, indent=4)
    return HttpResponse(res_obj, content_type='application/json')

#micro to micro New
#Get apsubcategory
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_apsubcategory(request):
    query = request.GET.get('query', None)
    apsubcategory1 = APsubcategory.objects.filter(code=query)
    apsubcategory = apsubcategory1[0]
    apsubcategory_data = {"id": apsubcategory.id, "code": apsubcategory.code, "name": apsubcategory.name}
    apcsubategory_dic = json.dumps(apsubcategory_data, indent=4)
    return HttpResponse(apcsubategory_dic, content_type='application/json')
#apcategory getlist
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_apsubcategorylist(request):
    apsubcategory_ids = json.loads(request.body)
    apsubcategory_id2 = apsubcategory_ids['apsubcat_id']
    obj = APsubcategory.objects.filter(code__in=apsubcategory_id2).values('id', 'name','code')
    apsubcategory_list_data = NWisefinList()
    for i in obj:
        data = {"id": i['id'], "name": i['name'],"code": i['code']}
        apsubcategory_list_data.append(data)
    return HttpResponse(apsubcategory_list_data.get(), content_type='application/json')

#micro to micro New
#Get apcategory
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_apcategory1(request):
    query = request.GET.get('query', None)
    apcategory1 = Apcategory.objects.filter(code=query)
    apcategory = apcategory1[0]
    apcategory_data = {"id": apcategory.id, "code": apcategory.code, "name": apcategory.name}
    apcategory_dic = json.dumps(apcategory_data, indent=4)
    return HttpResponse(apcategory_dic, content_type='application/json')
#apcategory getlist
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_apcategorylist(request):
    apcategory_ids = json.loads(request.body)
    apcategory_id2 = apcategory_ids['apcat_id']
    obj = Apcategory.objects.filter(code__in=apcategory_id2).values('id', 'name','code')
    apcategory_list_data = NWisefinList()
    for i in obj:
        data = {"id": i['id'], "name": i['name'],"code": i['code']}
        apcategory_list_data.append(data)
    return HttpResponse(apcategory_list_data.get(), content_type='application/json')

@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def apsubcategory_active_inactivate(request):
    if request.method == 'POST':
        scope=request.scope
        taxrate_service = SubcategoryService(scope)
        user_id = request.employee_id
        apsubcate_data = json.loads(request.body)
        apsubcat_obj = ApsubcategoryRequest(apsubcate_data)
        emp_service = EmployeeService(scope)
        empid = emp_service.get_empid_from_userid(user_id)
        resp_obj = taxrate_service.apsubcategory_active_inactivate(request,apsubcat_obj,empid)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_subcat_gl_list(request):
    if request.method == 'GET':
        scope = request.scope
        subcategoryservice = SubcategoryService(scope)
        user_id = request.employee_id
        query = request.GET.get('query')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = subcategoryservice.fetch_subcat_glno_list(query,vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_apsubcategory_download(request):
    scope = request.scope
    subcategoryservice = SubcategoryService(scope)
    user_id = request.user.id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    cat_resp = subcategoryservice.get_subcategory_download(request)
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
    worksheet.write_string(2, 4, 'APSubCategory Excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="ApSubCategory master.xlsx"'
    logger.info("APcat_Download Data:"+str(datetime.now()))
    return response