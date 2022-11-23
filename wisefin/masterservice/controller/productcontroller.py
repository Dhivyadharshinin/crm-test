import io
import json
from datetime import datetime

import pandas as pd
from django.core.files.base import ContentFile
from django.db.models import Q
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from masterservice.models import Product
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from masterservice.data.request.productrequest import  ProductRequest
from masterservice.service.productservice import ProductService
from masterservice.service.apcategoryservice import CategoryService
from masterservice.service.apsubcategoryservice import SubcategoryService
from masterservice.service.uomservice import UomService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.service.employeeservice import EmployeeService
from masterservice.util.masterutil import ProductClassification, dictdefault


# from masterservice.util.masterutil import getclassificationType
# supplier product - create , insert , update , delete
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])

def product(request):
    if request.method == 'POST':
        scope = request.scope
        product_service = ProductService(scope)
        product_obj = json.loads(request.body)
        prdct_obj = ProductRequest(product_obj)
        user_id = request.employee_id
        resp_obj = product_service.create_product(prdct_obj,user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_product_list(request)

def fetch_product_list(request):
    scope = request.scope
    product_service = ProductService(scope)
    user_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = product_service.fetch_product_list(request,vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


def delete_product(request,product_id):
    scope = request.scope
    product_service = ProductService(scope)
    user_id = request.employee_id
    resp_obj = product_service.delete_product(product_id,user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_product(request, product_id):
    if request.method == 'GET':
        scope = request.scope
        product_service = ProductService(scope)
        user_id = request.employee_id
        resp_obj = product_service.fetch_product(product_id,user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_product(request,product_id)
@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_product_code(request, product_code):
    if request.method == 'GET':
        scope = request.scope
        product_service = ProductService(scope)
        user_id = request.employee_id
        resp_obj = product_service.fetch_product_code(product_code,user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_product(request,product_code)

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def product_search(request):
    scope = request.scope
    product_service = ProductService(scope)
    user_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query')
    resp_obj = product_service.fetch_product_search(query,vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def product_mtom(request):
    if request.method == 'POST':
        scope = request.scope
        product_service = ProductService(scope)
        product_obj = json.loads(request.body)
        prdct_obj = ProductRequest(product_obj)
        action = request.GET.get('action')
        user_id = request.employee_id

        logger.info("product mtom data :" + str(product_obj))
        resp_obj = product_service.create_product_mtom(prdct_obj,action,user_id)
        logger.info("product mtom response: " + str(resp_obj))
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

#prpo-related api
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def product_get(request):
    product_data = json.loads(request.body)
    productId_arr = product_data['product_id']
    product = Product.objects.filter(id__in = productId_arr).values('id', 'code', 'name')
    product_list_data = NWisefinList()
    for i in product:
        data = {"id": i['id'], "code": i['code'], "name": i['name']}
        product_list_data.append(data)
    return HttpResponse(product_list_data.get(), content_type='application/json')

#prpo
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_productdata(request, product_id):
    product = Product.objects.get(id=product_id)
    product_data = {"id": product.id,
                    "code": product.code,
                    "name": product.name,
                    "uom_id": product.uom_id,
                    "product_details": product.product_details,
                    "unitprice": str(product.unitprice),
                    "productcategory_id": product.productcategory_id,
                    "producttype_id": product.producttype_id,
                    "category_id": product.category_id}
    product_dic = json.dumps(product_data, indent=4)
    return HttpResponse(product_dic, content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_productcode(request, product_code):
    product = Product.objects.get(code=product_code)
    product_data = {"id": product.id, "code": product.code, "name": product.name}
    employee_dic = json.dumps(product_data, indent=4)
    return HttpResponse(employee_dic, content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def productsearch(request):
    scope=request.scope
    query = request.GET.get('query')
    product_service = ProductService(scope)
    resp_obj = product_service.search_product(query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_productname(request):
    query = request.GET.get('query', None)
    scope=request.scope
    product_service = ProductService(scope)
    resp_obj = product_service.search_productname(query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

#micro to micro New
#Get product
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_productone(request,product_code):
    product = Product.objects.get(code=product_code)
    product_data = {"id": product.id, "code": product.code, "name": product.name}
    product_dic = json.dumps(product_data, indent=4)
    return HttpResponse(product_dic, content_type='application/json')
#product getlist
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_productlist(request):
    product_ids = json.loads(request.body)
    product_id2 = product_ids['product_id']
    obj = Product.objects.filter(code__in=product_id2).values('id', 'name','code')
    product_list_data = NWisefinList()
    for i in obj:
        data = {"id": i['id'], "name": i['name'],"code": i['code']}
        product_list_data.append(data)
    return HttpResponse(product_list_data.get(), content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_productlistget(request):
    product_data = json.loads(request.body)
    productId_arr = product_data['product_id']
    product = Product.objects.filter(id__in = productId_arr).values('id', 'code', 'name')
    product_list_data = NWisefinList()
    for i in product:
        data = {"id": i['id'], "code": i['code'], "name": i['name']}
        product_list_data.append(data)
    return HttpResponse(product_list_data.get(), content_type='application/json')


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def productcat_list(request):
    scope=request.scope
    product_data = json.loads(request.body)
    product_service = ProductService(scope)
    resp_obj = product_service.productcat_list(product_data)
    print("resp", resp_obj.get())
    return HttpResponse(resp_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def product_cat_type(request, product_category_id, product_type_id):
    condition1 = Q(productcategory_id=product_category_id) \
                 & Q(producttype_id=product_type_id)
    product = Product.objects.filter(condition1).values_list('id', flat=True)
    prod_arr = []
    for i in product:
        prod_arr.append(i)
    product_data = {"id": prod_arr}
    print(prod_arr)
    product_dic = json.dumps(product_data, indent=4)
    return HttpResponse(product_dic, content_type='application/json')


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def product_name(request):
    query = request.GET.get('query')
    product = Product.objects.filter(name__icontains=query).values_list('id', flat=True)
    prod_arr = []
    for i in product:
        prod_arr.append(i)
    product_data = {"id": prod_arr}
    print(prod_arr)
    product_dic = json.dumps(product_data, indent=4)
    return HttpResponse(product_dic, content_type='application/json')


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def pdtcat_name(request):
    scope=request.scope
    product_data = json.loads(request.body)
    product_service = ProductService(scope)
    query = request.GET.get('query', None)
    resp_obj = product_service.pdtcat_name(product_data, query)
    print("resp", resp_obj.get())
    return HttpResponse(resp_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def producttype_name(request, product_category_id):
    product_data = json.loads(request.body)
    scope=request.scope
    query = request.GET.get('query', None)
    product_service = ProductService(scope)
    resp_obj = product_service.producttype_name(product_data, product_category_id, query)
    print("resp", resp_obj.get())
    return HttpResponse(resp_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def producttype_list(request, productcategory_id):
    product_data = json.loads(request.body)
    scope=request.scope
    product_service = ProductService(scope)
    resp_obj = product_service.producttype_list(product_data, productcategory_id)
    print("resp", resp_obj.get())
    return HttpResponse(resp_obj.get(), content_type='application/json')

#prpo
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_productcode(request):
    query = request.GET.get('query', None)
    product = Product.objects.get(code=query)
    product_data = {"id": product.id,
                    "code": product.code,
                    "name": product.name,
                    "hsn_id": product.hsn_id,
                    "uom_id": product.uom_id,
                    "category_id": product.category_id}
    employee_dic = json.dumps(product_data, indent=4)
    return HttpResponse(employee_dic, content_type='application/json')

# @csrf_exempt
# @api_view(['POST'])
# def product_category_Devision(request):
#    if request.method=='POST':
#        devision_obj=json.loads(request.body)
#        prdct_dev_obj = productDevisionRequest(devision_obj)
#        product_service = ProductService()
#        resp_obj = product_service.product_devision(prdct_dev_obj)
#        print("resp", resp_obj.get())
#        return HttpResponse(resp_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
def productclassification_resp(request):
    if request.method == 'GET':
        # print(number)
        app_service = ProductClassification()
        resp_obj = app_service.getclassificationType()
        # print(resp_obj.get)
        employee_dic = json.dumps(resp_obj, indent=4)
        return HttpResponse(employee_dic, content_type='application/json')

@csrf_exempt
@api_view(['GET'])
def get_product_classification(request,number):
    if request.method == 'GET':
        print(number)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        scope = request.scope
        product_service = ProductService(scope)
        resp_obj = product_service.productclassication_service_cat_map(request,number,vys_page)
        return HttpResponse(resp_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['GET'])
def get_product_classification_cat(request,product_cat_id):
    if request.method == 'GET':
        print(product_cat_id)
        page = request.GET.get('page', 1)
        page = int(page)
        scope = request.scope
        vys_page = NWisefinPage(page, 10)
        product_service = ProductService(scope)
        resp_obj = product_service.product_classication_service_subcat_map(request,product_cat_id,vys_page)
        return HttpResponse(resp_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
def get_hsn(request):
    if request.method == 'GET':
        # print(product_cat_id)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        scope = request.scope
        product_service = ProductService(scope)
        resp_obj = product_service.get_hsn_service(request,vys_page)
        return HttpResponse(resp_obj.get(), content_type='application/json')

#prpo
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_productcode(request):
    scope=request.scope
    product_service = ProductService(scope)
    code = request.GET.get('query', None)
    resp_obj = product_service.search_productcode(code)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
# @csrf_exempt
@api_view(['POST',])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_product_data(request,product_id):
    if request.method == 'POST':
        print(product_id)
        scope = request.scope
        product_service = ProductService(scope)
        product_obj = json.loads(request.body)
        prdct_obj = ProductRequest(product_obj)
        resp_obj = product_service.create_product_inactivate(request,prdct_obj,product_id)
        print(resp_obj.get())
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_product_download(request):
    scope = request.scope
    product_service = ProductService(scope)
    user_id = request.user.id
    pdt_resp = product_service.fetch_product_download(request)
    data = json.loads(json.dumps(pdt_resp.__dict__, default=dictdefault))['data']
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
    worksheet.write_string(2, 2, 'Product Master Excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="Product Master.xlsx"'
    logger.info("Test_Download Data:"+str(datetime.now()))
    return response