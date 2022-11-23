import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from inwardservice.data.request.escalationtyperequest import EscalatonSubTypeRequest
from inwardservice.service.escalationsubtypeservice import EscalationSubTypeService

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_escaltionsubtype(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        escaltiontype_service = EscalationSubTypeService(scope)
        escaltiontype_obj = json.loads(request.body)
        escaltiontype_obj = EscalatonSubTypeRequest(escaltiontype_obj)
        # user_id = request.user.id
        # api_serv = ApiService()
        # emp = api_serv.get_emp_id(request, user_id)
        # emp_id = emp['id']
        resp_obj = escaltiontype_service.create_escaltionsubtype( escaltiontype_obj, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_escalationsub_list(request)


def fetch_escalationsub_list(request):
    scope = request.scope
    escal_service = EscalationSubTypeService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query', None)
    resp_obj = escal_service.fetch_escalationsub_list(query, vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_escalationsub(request, escalationsubtype_id):
    if request.method == 'GET':
        scope = request.scope
        escal_service = EscalationSubTypeService(scope)
        resp_obj = escal_service.fetch_escalationsub(escalationsubtype_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_escalationsub(request, escalationsubtype_id)


def delete_escalationsub(request, escalationsubtype_id):
    scope = request.scope
    escal_service = EscalationSubTypeService(scope)
    resp_obj = escal_service.delete_escalationsub(escalationsubtype_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_escalationsub(request):
    scope = request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = None
    query = request.GET.get('query', None)
    escalationsub_service = EscalationSubTypeService(scope)
    resp_obj = escalationsub_service.search_escalationsub(request, query, vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response