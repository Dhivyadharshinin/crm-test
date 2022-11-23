import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from pprservice.data.request.businesssubcategoryrequest import BusinessSubCategoryRequest
from pprservice.service.businesssubcategoryservice import BusinessSubCategoryService
from userservice.service.employeeservice import EmployeeService
from masterservice.models import Bank
from utilityservice.data.response.nwisefinlist import NWisefinList

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def business_subcategory(request):
    scope = request.scope
    if request.method == 'POST':
        business_service = BusinessSubCategoryService(scope)
        business_data = json.loads(request.body)
        business_obj = BusinessSubCategoryRequest(business_data)

        empid =  request.employee_id
        resp_obj = business_service.create_businesssubcategory(business_obj, empid)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_businesssubcategory_list(request)


def fetch_businesssubcategory_list(request):
    scope=request.scope
    business_service = BusinessSubCategoryService(scope)
    page = request.GET.get('page', 1)
    query = request.GET.get('query', None)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = business_service.fetch_subcategory_list(vys_page,query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_business_subcategory(request,businesscategory_id):
    scope = request.scope
    if request.method == 'GET':
        business_service = BusinessSubCategoryService(scope)
        user_id =  request.employee_id
        resp_obj = business_service.fetch_businesssubcategory(businesscategory_id,user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_businesssubcategory(request,businesscategory_id)


@csrf_exempt
def delete_businesssubcategory(request,businesscategory_id):
    scope = request.scope
    business_service = BusinessSubCategoryService(scope)
    user_id =  request.employee_id
    resp_obj = business_service.delete_subcategory(businesscategory_id,user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def business_subcategory_search(request):
    scope = request.scope
    business_service = BusinessSubCategoryService(scope)
    query = request.GET.get('query')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = business_service.fetch_businesssubcategory_search(query,vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
