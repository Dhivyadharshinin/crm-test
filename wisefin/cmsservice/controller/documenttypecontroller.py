import json
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from cmsservice.data.request.documenttyperequest import DocumenttypeRequest
from cmsservice.service.documenttypeservice import DocumenttypeService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def Documenttype(request):
    if request.method == 'POST':
        scope = request.scope
        documenttype_service = DocumenttypeService(scope)
        doctype_obj = json.loads(request.body)
        Doc_obj = DocumenttypeRequest(doctype_obj)
        emp_id = scope['employee_id']
        resp_obj = documenttype_service.create_documenttype(Doc_obj, emp_id, scope)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_documenttype_list(request)


def fetch_documenttype_list(request):
    scope = request.scope
    documenttype_service = DocumenttypeService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query', None)
    resp_obj = documenttype_service.fetch_doctype_list(vys_page, query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@transaction.atomic
@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_doctype(request, doctype_id):
    if request.method == 'GET':
        scope = request.scope
        documenttype_service = DocumenttypeService(scope)
        resp_obj = documenttype_service.fetchdoctype(doctype_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_Doctype(request, doctype_id)


def delete_Doctype(request, doctype_id):
    scope = request.scope
    documenttype_service = DocumenttypeService(scope)
    emp_id = scope['employee_id']
    resp_obj = documenttype_service.delete_doctype(doctype_id, emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
