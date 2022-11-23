import json

from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from masterservice.service.customercategoryservice import CustomerCategoryService
from masterservice.data.request.customercategoryrequest import CustomerCategoryRequest
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.service.employeeservice import EmployeeService

# customercategory - create , insert , update , delete

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def customercategory(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        customercategory_service = CustomerCategoryService(scope)
        # user_id = request.user.id
        # emp_service = EmployeeService(scope)
        # empid = emp_service.get_empid_from_userid(user_id)
        customercategory_data = json.loads(request.body)
        customercategory_obj = CustomerCategoryRequest(customercategory_data)
        resp_obj = customercategory_service.create_customercategory(customercategory_obj, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_customercategory_list(request)


def fetch_customercategory_list(request):
    scope = request.scope
    customercategory_service = CustomerCategoryService(scope)
    user_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = customercategory_service.fetch_customercategory_list(vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


def delete_customercategory(request, customercategory_id):
    scope = request.scope
    emp_id = request.employee_id
    customercategory_service = CustomerCategoryService(scope)
    # user_id = request.user.id
    resp_obj = customercategory_service.delete_customercategory(customercategory_id, emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_customercategory(request, customercategory_id):
    if request.method == 'GET':
        scope = request.scope
        emp_id = request.employee_id
        customercategory_service = CustomerCategoryService(scope)
        # user_id = request.user.id
        resp_obj = customercategory_service.fetch_customercategory(customercategory_id, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_customercategory(request, customercategory_id)
@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def customercategory_search(request):
    scope = request.scope
    customercategory_service = CustomerCategoryService(scope)
    query = request.GET.get('query')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = customercategory_service.fetch_customercategory_search(query, vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
