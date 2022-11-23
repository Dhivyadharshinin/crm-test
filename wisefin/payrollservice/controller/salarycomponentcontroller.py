from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from rest_framework.permissions import IsAuthenticated
from utilityservice.data.response.nwisefinpage import NWisefinPage
from django.http import HttpResponse
import json
from payrollservice.data.request.payrollcomponentrequest import SalaryComponentRequest
from payrollservice.service.payrollcomponentservice import PayrollService


@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def salarycomponent(request):
    scope = request.scope
    if request.method == 'POST':
        data_json = json.loads(request.body)
        salary_request = SalaryComponentRequest(data_json)
        user_id = request.employee_id
        payroll_service=PayrollService(scope)
        resp_obj = payroll_service.create_salarycomponent(salary_request,user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    else:
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp = PayrollService(scope).getall_salarycomponent(vys_page)
        response = HttpResponse(resp.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_salarycomponent(request, salary_id):
    scope = request.scope
    payroll_service = PayrollService(scope)
    if request.method == 'GET':
        resp = payroll_service.fetch_salarycomponent(salary_id)
    else:
        resp = payroll_service.delete_salarycomponent(salary_id)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response
