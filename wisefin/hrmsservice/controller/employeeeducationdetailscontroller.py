import json
from django.http import HttpResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view,authentication_classes, permission_classes
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.nwisefinpermission import NWisefinPermission
from hrmsservice.service.employeeeducationdetailsservice import EmployeeEducationInfoService
from hrmsservice.data.request.employeeeducationdetailsrequest import EmployeeEducationDetailsRequest,EmployeeExperiencesRequest

@transaction.atomic
@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employeeeducationdetails(request,employee_id):
    scope = request.scope
    if request.method == 'POST':
        data_json = json.loads(request.body)
        emp_request = EmployeeEducationDetailsRequest()
        user_id = request.employee_id
        req_dict = emp_request.empeducationdetails_request(data_json, user_id,employee_id)
        resp_obj = EmployeeEducationInfoService(scope).create_employeeeducationinfo(req_dict)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    else:
        resp = EmployeeEducationInfoService(scope).get_employeeeducationinfo(employee_id)
        response = HttpResponse(resp.get(), content_type="application/json")
        return response

@transaction.atomic
@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employeeexperiences(request, employee_id):
    scope = request.scope
    if request.method == 'POST':
        data_json = json.loads(request.body)
        emp_request = EmployeeExperiencesRequest()
        user_id = request.employee_id
        req_dict = emp_request.employeeexperiences_request(data_json, user_id, employee_id)
        resp_obj = EmployeeEducationInfoService(scope).create_employeeexperiences(req_dict)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    else:
        resp = EmployeeEducationInfoService(scope).get_employeeexperiences(employee_id)
        response = HttpResponse(resp.get(), content_type="application/json")
        return response
