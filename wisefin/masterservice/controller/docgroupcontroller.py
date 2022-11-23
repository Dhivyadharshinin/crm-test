import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from masterservice.data.request.docgrouprequest import DocumentGroupRequest
from masterservice.service.docugroupservice import DocumentGroupService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.service.employeeservice import EmployeeService

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def docugroup(request):
    if request.method == 'POST':
        scope = request.scope
        docugroup_service = DocumentGroupService(scope)
        docugroup_obj = json.loads(request.body)
        docu_obj = DocumentGroupRequest(docugroup_obj)
        user_id = request.employee_id
        emp_service = EmployeeService(scope)
        resp_obj = docugroup_service.create_docugroup(docu_obj, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
       return fetch_docugroup_list(request)

def fetch_docugroup_list(request):
        scope=request.scope
        docugroup_service = DocumentGroupService(scope)
        user_id = request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = docugroup_service.fetch_docugroup_list(vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_docugroup(request, docugroup_id):
    if request.method == 'GET':
        scope=request.scope
        docugroup_service = DocumentGroupService(scope)
        # user_id = request.employee_id
        resp_obj = docugroup_service.fetch_docugroup(docugroup_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
         return delete_docugroup(request, docugroup_id)
def delete_docugroup(request, docugroup_id):
    scope=request.scope
    docugroup_service = DocumentGroupService(scope)
    user_id = request.employee_id
    resp_obj = docugroup_service.delete_docugroup(docugroup_id,user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

def documentgroup_search(request):
        scope=request.scope
        docugroup_service = DocumentGroupService(scope)
        user_id = request.employee_id
        query = request.GET.get('query', None)
        # vendor = request.GET.get('vendor', None)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = docugroup_service.fetch_documentgroup_list(vys_page,query)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
