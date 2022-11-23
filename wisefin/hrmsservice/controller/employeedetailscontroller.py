import json
from django.http import HttpResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view,authentication_classes, permission_classes
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.nwisefinpermission import NWisefinPermission
from hrmsservice.service.employeedetailsservice import EmployeeDetailsService
from hrmsservice.data.request.employeedetailsrequest import EmployeeDetialsRequest,EmployeeFamilyInfoRequest,EmpEmergencyContactRequest
from hrmsservice.util.hrmsutil import relationship_summary, templateutil_summary
from utilityservice.data.response.nwisefinpage import NWisefinPage
@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employeedetails(request,employeeid):
    scope = request.scope
    service = EmployeeDetailsService(scope)
    action=request.GET.get('action')
    if action == 'deatils' or action == None:
        if request.method == 'POST':
            body_data = json.loads(request.body)
            emp_request = EmployeeDetialsRequest(body_data)
            user_id = request.employee_id
            resp = service.create_employeedetails(emp_request,user_id,employeeid)
            response = HttpResponse(resp.get(), content_type="application/json")
            return response
        else:
            resp = service.get_employeedetails(employeeid)
            response = HttpResponse(resp.get(), content_type="application/json")
            return response

    elif action == 'shift':
        if request.method == 'POST':
            body_data = json.loads(request.body)
            user_id = request.employee_id
            resp = service.createshiftmapping(user_id, body_data, employeeid)
            response = HttpResponse(resp.get(), content_type="application/json")
            return response
        else:
            resp = service.get_shiftmapping(employeeid)
            response = HttpResponse(json.dumps(resp), content_type="application/json")
            return response

@csrf_exempt
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employeeshiftmapping(request):
    scope = request.scope
    service = EmployeeDetailsService(scope)
    action = request.GET.get('action')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    if request.method == 'POST':
        body_data = json.loads(request.body)
        resp = service.employeeshiftmapping(vys_page,body_data)
        response = HttpResponse(resp.get(), content_type="application/json")
        return response
    if request.method == 'GET':
        if action == 'shifthistory':
            employeeid = request.GET.get('employeeid', None)
            resp = service.empshifthistory(vys_page, employeeid)
        response = HttpResponse(resp.get(), content_type="application/json")
        return response
@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employeefamilyinfo(request,employee_id):
    scope = request.scope
    if request.method == 'POST':
        data_json = json.loads(request.body)
        emp_request = EmployeeFamilyInfoRequest()
        user_id = request.employee_id
        req_dict = emp_request.empfamilyinfo_request(data_json, user_id,employee_id)
        resp_obj = EmployeeDetailsService(scope).create_employeefamilyinfo(req_dict)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    else:
        resp = EmployeeDetailsService(scope).get_employeefamilyinfo(employee_id)
        response = HttpResponse(resp.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def empemergencycontact(request, employee_id):
    scope = request.scope
    if request.method == 'POST':
        data_json = json.loads(request.body)
        emp_request = EmpEmergencyContactRequest()
        user_id = request.employee_id
        req_dict = emp_request.empemergencycontact_request(data_json, user_id, employee_id)
        resp_obj = EmployeeDetailsService(scope).create_empemergencycontact(req_dict, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    else:
        resp = EmployeeDetailsService(scope).get_empemergencycontact(employee_id)
        response = HttpResponse(resp.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def hrms_drop_down(request):
    if request.method == 'GET':
        action = request.GET.get('action')
        if action == 'relationship':
            req_obj = relationship_summary().get()
        elif action == 'template':
            req_obj = templateutil_summary().get()
        else:
            req_obj = []
        response = HttpResponse(req_obj, content_type='application/json')
        return response
