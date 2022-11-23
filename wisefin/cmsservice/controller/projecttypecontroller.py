import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from cmsservice.data.request.projecttyperequest import ProjectTypeRequest
from cmsservice.service.projecttypeservice import ProjectTypeService,AgreementtypeService


@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_projecttype(request):
    if request.method == 'POST':
        projecttype_data = json.loads(request.body)
        projecttype_obj = ProjectTypeRequest(projecttype_data)
        scope = request.scope
        projecttype_service = ProjectTypeService(scope)
        emp_id = request.employee_id
        response_obj = projecttype_service.create_projecttype(projecttype_obj, emp_id, scope)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response
    elif request.method == 'GET':
        return fetch_projecttype_list(request)

def fetch_projecttype_list(request):
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query', None)
    scope = request.scope
    projecttype_service = ProjectTypeService(scope)
    response_obj = projecttype_service.fetch_projecttype_list(vys_page, query)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response


@transaction.atomic
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_projecttype(request, projecttype_id):
    if request.method == 'GET':
        scope = request.scope
        projecttype_service = ProjectTypeService(scope)
        resp_obj = projecttype_service.fetch_projecttype(projecttype_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_projecttype(request, projecttype_id)


def delete_projecttype(request, projecttype_id):
    scope = request.scope
    projecttype_service = ProjectTypeService(scope)
    emp_id = request.employee_id
    resp_obj = projecttype_service.delete_projecttype(projecttype_id, emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_agreementtype(request):
    if request.method == 'POST':
        agreement_data = json.loads(request.body)
        agreement_obj = ProjectTypeRequest(agreement_data)
        scope = request.scope
        agreement_serv=AgreementtypeService(scope)
        emp_id = request.employee_id
        resp_obj = agreement_serv.create_agreement(agreement_obj,emp_id,scope)
        respons = HttpResponse(resp_obj.get(), content_type="application/json")
    elif request.method == 'GET':
        scope = request.scope
        service = AgreementtypeService(scope)
        re_obj = service.agreementtypeall()
        respons = HttpResponse(re_obj, content_type="application/json")
    return respons
@transaction.atomic
@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def agreementtype(request,agreementtype_id):
    if request.method == 'GET':
        scope = request.scope
        service = AgreementtypeService(scope)
        re_obj = service.get_agreementype(agreementtype_id)
        response = HttpResponse(re_obj.get(), content_type="application/json")
    elif request.method == 'DELETE':
        scope = request.scope
        agreement_service = AgreementtypeService(scope)
        res_obj = agreement_service.delete_agreementtype(agreementtype_id)
        response = HttpResponse(res_obj.get(), content_type="application/json")
    return response