import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from inwardservice.data.request.inwardtemplaterequest import TemplateRequest
from inwardservice.service.inwardtemplateservice import InwardTemplateService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_inward_template(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        inward_service = InwardTemplateService(scope)
        inward_temp_data = json.loads(request.body)
        # user_id = request.user.id
        # api_serv = ApiService()
        # emp = api_serv.get_emp_id(request, user_id)
        # emp_id = emp['id']
        template_obj = TemplateRequest(inward_temp_data)
        resp_obj = inward_service.create_inward_template(template_obj, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_inward_temp_list(request)


def fetch_inward_temp_list(request):
    scope = request.scope
    inward_service = InwardTemplateService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = inward_service.fetch_inward_temp_list(vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_inward_temp(request,inwardtemp_id):
    if request.method == 'GET':
        scope = request.scope
        emp_id = request.employee_id
        inward_service = InwardTemplateService(scope)
        # user_id = request.user.id
        # api_serv = ApiService()
        # emp = api_serv.get_emp_id(request, user_id)
        # emp_id = emp['id']
        resp_obj = inward_service.fetch_inward_temp(inwardtemp_id, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_inward_temp(request, inwardtemp_id)

@csrf_exempt
def delete_inward_temp(request, inwardtemp_id):
    # user_id = request.user.id
    # api_serv = ApiService()
    # emp = api_serv.get_emp_id(request, user_id)
    # emp_id = emp['id']
    scope = request.scope
    emp_id = request.employee_id
    inward_service = InwardTemplateService(scope)
    resp_obj = inward_service.delete_inward_temp(inwardtemp_id, emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
