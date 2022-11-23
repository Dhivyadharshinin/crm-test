import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from userservice.service.employeeservice import EmployeeService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from masterservice.data.request.documenttyperequest import DocumenttypeRequest
from masterservice.service.documenttypeservice import DocumenttypeService

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def Documenttype(request):
    if request.method == 'POST':
        scope=request.scope
        documenttype_service = DocumenttypeService(scope)
        doctype_obj = json.loads(request.body)
        doctype_json=doctype_obj
        Doc_obj = DocumenttypeRequest(doctype_obj)
        user_id = request.employee_id
        emp_service = EmployeeService(scope)
        emp_id = emp_service.get_empid_from_userid(user_id)
        resp_obj = documenttype_service.create_documenttype(Doc_obj, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
       return fetch_documenttype_list(request)

def fetch_documenttype_list(request):
        scope=request.scope
        documenttype_service = DocumenttypeService(scope)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        query = request.GET.get('query', None)
        resp_obj = documenttype_service.fetch_doctype_list(vys_page,query)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_doctype(request, doctype_id):
    if request.method == 'GET':
        scope=request.scope
        documenttype_service = DocumenttypeService(scope)
        resp_obj = documenttype_service.fetchdoctype(doctype_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
         return delete_Doctype(request, doctype_id)
def delete_Doctype(request, doctype_id):
    scope=request.scope
    documenttype_service = DocumenttypeService(scope)
    user_id = request.employee_id
    emp_service = EmployeeService(scope)
    emp_id = emp_service.get_empid_from_userid(user_id)
    resp_obj = documenttype_service.delete_doctype(doctype_id,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_doctype(request):
    scope=request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = None
    query = request.GET.get('query', None)
    doctype_service = DocumenttypeService(scope)
    resp_obj = doctype_service.search_doctype(request, query, vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


#inward
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def document_summarysearch(request):
    scope = request.scope
    doctype_service = DocumenttypeService(scope)
    name = request.GET.get('name')
    code = request.GET.get('code')
    query = {"name": name, "code": code}
    print(query)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = doctype_service.document_summarysearch(query, vys_page)
    response = HttpResponse(resp_obj.get(), content_type='application/json')
    return response
