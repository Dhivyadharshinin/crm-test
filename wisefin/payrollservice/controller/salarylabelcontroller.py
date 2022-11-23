from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from rest_framework.permissions import IsAuthenticated
from utilityservice.data.response.nwisefinpage import NWisefinPage
from django.http import HttpResponse
import json
from payrollservice.data.request.payrollcomponentrequest import SalaryLabelRequest
from payrollservice.service.salarylabelservice import PayrollService


@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def salarylabel(request):
    scope = request.scope
    if request.method == 'POST':
        data_json = json.loads(request.body)
        salary_request = SalaryLabelRequest(data_json)
        user_id = request.employee_id
        payroll_service = PayrollService(scope)
        resp_obj = payroll_service.create_salarylabel(salary_request, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    else:
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp = PayrollService(scope).getall_salarylabel(vys_page)
        response = HttpResponse(resp.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_salarylabel(request, salary_id):
    scope = request.scope
    payroll_service = PayrollService(scope)
    if request.method == 'GET':
        resp = payroll_service.fetch_salarylabel(salary_id)
    else:
        resp = payroll_service.delete_salarylabel(salary_id)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response
