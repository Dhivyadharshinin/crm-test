from django.http import HttpResponse
from rest_framework.decorators import api_view , authentication_classes, permission_classes
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.permissions import IsAuthenticated
from inwardservice.data.request.inwardproductsubcategoryrequest import ProductsubcategoryRequest
from inwardservice.service.inwardproductsubcategoryservice import ProductsubcategoryService

#create
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_prosubcat(request):
    if request.method=='POST':
        prosubcat_obj=json.loads(request.body)
        # user_id = request.user.id
        # api_serv = ApiService()
        # emp = api_serv.get_emp_id(request, user_id)
        # emp_id = emp['id']
        scope = request.scope
        emp_id = request.employee_id
        prosubcatobj=ProductsubcategoryRequest(prosubcat_obj)
        prosubcat_service=ProductsubcategoryService(scope)
        resp_obj=prosubcat_service.create_prosubcat(prosubcatobj,emp_id)
        response=HttpResponse(resp_obj.get(),content_type='application/json')
        return response
    if request.method == 'GET':
        return fetch_prosubcat_list(request)
#listall
def fetch_prosubcat_list(request):
    scope = request.scope
    prosubcat_service=ProductsubcategoryService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query', None)
    resp_obj=prosubcat_service.prosubcat_list(vys_page,query)
    response=HttpResponse(resp_obj.get(),content_type='application/json')
    return response

#where condition to disforeign
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_procat_list(request,product_id):
    scope = request.scope
    prosubcat_service = ProductsubcategoryService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = prosubcat_service.prosubcats_list(vys_page,product_id)
    response=HttpResponse(resp_obj.get(), content_type='application/json')
    return response

#where condition
@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_prosubcat(request,prosubcat_id):
    if request.method=='GET':
        scope = request.scope
        prosubcat_service=ProductsubcategoryService(scope)
        resp_obj=prosubcat_service.fetch_prosubcat(prosubcat_id)
        resp_obj = HttpResponse(resp_obj.get(), content_type='application/json')
        return resp_obj

    if request.method == 'DELETE':
        return delete_prosubcat(request,prosubcat_id)
#delete
def delete_prosubcat(request,prosubcat_id):
    scope = request.scope
    prosubcat_service = ProductsubcategoryService(scope)
    resp_obj = prosubcat_service.delete_prosubcat(prosubcat_id)
    resp_obj = HttpResponse(resp_obj.get(), content_type='application/json')
    return resp_obj


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_prosubcat(request):
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = None
    query = request.GET.get('query', None)
    scope = request.scope
    prosubcat_service = ProductsubcategoryService(scope)
    resp_obj = prosubcat_service.search_prosubcat(request, query, vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response