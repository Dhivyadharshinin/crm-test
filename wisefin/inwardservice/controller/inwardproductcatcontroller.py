import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from inwardservice.data.request.inwardproductcatrequest import ProductcategoryRequest
from inwardservice.service.inwardproductcatservice import Productcategoryservice
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_productcat(request):
    if request.method == 'POST':
        productcat_obj=json.loads(request.body)
        # user_id = request.user.id
        # api_serv = ApiService()
        # emp = api_serv.get_emp_id(request, user_id)
        # emp_id = emp['id']
        productcat_obj=ProductcategoryRequest(productcat_obj)
        scope = request.scope
        emp_id = request.employee_id
        productcat_service=Productcategoryservice(scope)
        resp_obj=productcat_service.create_productcatprocess(productcat_obj, emp_id)
        response=HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    if request.method == 'GET':
        return fetch_pdtcat_list(request)
#listall
def fetch_pdtcat_list(request):
    scope = request.scope
    productcat_service=Productcategoryservice(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query', None)
    resp_obj=productcat_service.pdtcat_list(vys_page, query)
    response=HttpResponse(resp_obj.get(), content_type='application/json')
    return response

#where condition
@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_productcat(request,productcat_id):
    if request.method == 'GET':
        scope = request.scope
        inward_service = Productcategoryservice(scope)
        resp_obj = inward_service.fetch_productcat(productcat_id)
        resp_obj = HttpResponse(resp_obj.get(), content_type="application/json")
        return resp_obj

    if request.method == 'DELETE':
        return delete_productcat(request, productcat_id)

def delete_productcat(request, productcat_id):
    scope = request.scope
    emp_id = request.employee_id
    inward_service = Productcategoryservice(scope)
    # user_id = request.user.id
    # api_serv = ApiService()
    # emp = api_serv.get_emp_id(request, user_id)
    # emp_id = emp['id']
    resp_obj = inward_service.delete_productcat(productcat_id, emp_id)
    resp_obj = HttpResponse(resp_obj.get(), content_type='application/json')
    return resp_obj


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_productcat(request):
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = None
    query = request.GET.get('query', None)
    scope = request.scope
    productcat_service = Productcategoryservice(scope)
    resp_obj = productcat_service.search_productcat(request, query, vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
