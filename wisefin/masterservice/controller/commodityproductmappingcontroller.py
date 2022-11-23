import json
from django.db import transaction

from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from masterservice.service.commodityproductmappingservice import CommodityProductMapService


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def cpmapping(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        print(emp_id)
        cpmap_data = json.loads(request.body)
        user_id = request.user.id
        # api_serv = ApiService()
        # emp = api_serv.get_emp_id(request, user_id)
        # emp_id = emp['id']
        # with transaction.atomic(using=DataBase.PRPO_DB):
        commodityProduct_service = CommodityProductMapService(scope)
        resp_obj = commodityProduct_service.cpmapping(cpmap_data, emp_id)
        response = HttpResponse(resp_obj.get(), content_type='application/json')
        return response
    elif request.method == 'GET':
        return fetch_cpmap_list(request)

def fetch_cpmap_list(request):
    scope = request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    user_id = request.user.id
    emp_id = request.employee_id
    print("employee_id",emp_id)
    # api_serv = ApiService()
    # emp = api_serv.get_emp_id(request, user_id)
    # emp_id = emp['id']
    commodityProduct_service = CommodityProductMapService(scope)
    response_obj = commodityProduct_service.fetch_cpmap_list(vys_page, emp_id, request)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response


@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_cpmapping(request, cpmap_id):
    if request.method == 'GET':
        scope=request.scope
        commodityProduct_service = CommodityProductMapService(scope)
        resp_obj = commodityProduct_service.fetch_cpmap(cpmap_id, request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_cpmap(request, cpmap_id)

def delete_cpmap(request, cpmap_id):
    scope=request.scope
    user_id = request.user.id
    emp_id = request.employee_id
    # api_serv = ApiService()
    # emp = api_serv.get_emp_id(request, user_id)
    # emp_id = emp['id']
    commodityProduct_service = CommodityProductMapService(scope)
    resp_obj = commodityProduct_service.delete_cpmap(cpmap_id, emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_cpmap(request, commodity_id):
    scope=request.scope
    user_id = request.user.id
    emp_id = request.employee_id
    # api_serv = ApiService()
    # emp = api_serv.get_emp_id(request, user_id)
    # emp_id = emp['id']
    commodityProduct_service = CommodityProductMapService(scope)
    resp_obj = commodityProduct_service.fetch_CommodityProductMap(commodity_id, emp_id, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def commodity_productsearch(request, product_id):
    scope=request.scope
    query = request.GET.get('query')
    commodityProduct_service = CommodityProductMapService(scope)
    resp_obj = commodityProduct_service.commodity_productsearch(product_id, query, request)
    response = HttpResponse(resp_obj, content_type="application/json")
    return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def cpmapping_code(request):
    scope=request.scope
    cpmapping_data = json.loads(request.body)
    user_id = request.user.id
    emp_id = request.employee_id
    # api_serv = ApiService()
    # emp = api_serv.get_emp_id(request, user_id)
    # emp_id = emp['id']
    commodityProduct_service = CommodityProductMapService(scope)
    resp_obj = commodityProduct_service.cpmapping_code(cpmapping_data, emp_id, request)
    response = HttpResponse(resp_obj.get(), content_type='application/json')
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def commodity_product(request):
    scope=request.scope
    commodity_id = request.GET.get('commodity_id', None)
    category = request.GET.get('category')
    name = request.GET.get('name')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    commodityProduct_service = CommodityProductMapService(scope)
    resp_obj = commodityProduct_service.commodity_product(commodity_id, name, category, vys_page, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response