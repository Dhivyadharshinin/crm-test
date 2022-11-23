from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from rest_framework.permissions import IsAuthenticated
from utilityservice.data.response.nwisefinpage import NWisefinPage
from attendanceservice.service.leaverequestservice import LeaveRequestService
from attendanceservice.service.leaveapproveservice import LeaveApproveService
from attendanceservice.service.leavecalucationservice import LeaveCalculationServ
from attendanceservice.data.request.leaverequest import LeaveDataRequest, LeaveApproveRequest
from attendanceservice.util.responsemessage import MessageResponse, StatusType
from attendanceservice.util.attendanceutil import AttendanceDocumentUtil
from utilityservice.data.response.nwisefinsuccess import SuccessMessage
from attendanceservice.service.attendancedocumentservice import AttendanceDocumentService
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription
from django.http import HttpResponse
import json


# 0011
# leave request
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def leave_request(request):
    scope = request.scope
    employee_id = request.employee_id

    if request.method == 'POST':
        leave_service = LeaveRequestService(scope)

        leave_data = json.loads(request.data.dict().get('data'))
        req_data = LeaveDataRequest(leave_data)
        response = leave_service.new_leave_req(req_data, employee_id)
        try:
            if not request.FILES['file'] is None:
                doc_serv = AttendanceDocumentService(scope)
                doc_serv.create_attendance_document(response, AttendanceDocumentUtil.LEAVE_REQUEST, request)
        except KeyError:
            print('error while uploading documents for the below data')
            print('select * from attendanceservice_leaverequest where id='+str(response.id))
        resp = MessageResponse()
        resp.set_status(StatusType.SUCCESS)
        resp.set_message(SuccessMessage.CREATE_MESSAGE)
        response = HttpResponse(resp.get(), content_type="application/json")
        return response

    elif request.method == 'GET':
        # scope = request.scope
        # employee_id = request.employee_id
        # leave_service = LeaveRequestService(scope)
        # status = request.GET.get('status', 1)
        # from_date = request.GET.get('fromdate', None)
        # to_date = request.GET.get('todate', None)
        # page = request.GET.get('page', 1)
        # page = int(page)
        # vys_page = NWisefinPage(page, 10)
        # resp = leave_service.leave_summary(status, vys_page, employee_id, from_date, to_date)
        # response = HttpResponse(resp.get(), content_type="application/json")
        # return response
        scope = request.scope
        emp_id = request.employee_id
        leave_serv = LeaveRequestService(scope)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp = leave_serv.new_leave_summary(vys_page, request, emp_id)
        response = HttpResponse(resp.get(), content_type="application/json")
        return response



# 0012
@csrf_exempt
@api_view(['POST','GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_leave(request, leave_id):
    scope = request.scope
    action = request.GET.get('action')
    if request.method == 'POST':
        # approval - api
        if action == 'approval' or action == None:
            resp=leave_approver_status(request,leave_id)
            return resp

    elif request.method == 'GET':
        leave_service = LeaveRequestService(scope)
        # leave request by id
        if action == None:
            resp = leave_service.fetch_leave_request(leave_id)
        # leave request close by id
        elif action =='close':
            resp = leave_service.delete_leave_request(leave_id)

        response = HttpResponse(resp.get(), content_type="application/json")
        return response


# leave approve
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def leave_approve(request):
    scope = request.scope
    employee_id = request.employee_id
    leave_service = LeaveApproveService(scope)
    if request.method == 'POST':
        status = request.GET.get('status', 1)
        status = int(status)
        leave_data = json.loads(request.body)
        req_data = LeaveApproveRequest(leave_data)
        leave_serv = LeaveRequestService(scope)
        leave_id = req_data.get_leave_request_id()
        leave_update = leave_serv.update_approve(employee_id, status, leave_id)
        if leave_update is True:
            resp = leave_service.create_leave_approve(req_data, employee_id)
        else:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj
    else:
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp = leave_service.leave_approve_list(vys_page)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_leave_approve(request, leave_id):
    scope = request.scope
    leave_service = LeaveApproveService(scope)
    if request.method == 'GET':
        resp = leave_service.fetch_leave_approve(leave_id)
    else:
        resp = leave_service.delete_leave_approve(leave_id)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def leave_summary(request):
    scope = request.scope
    employee_id = request.employee_id
    leave_service = LeaveRequestService(scope)
    status = request.GET.get('status', 1)
    from_date = request.GET.get('fromdate', None)
    to_date = request.GET.get('todate', None)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp = leave_service.leave_summary(status, vys_page, employee_id, from_date, to_date)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employee_count_mapping(request):
    scope = request.scope
    employee_id = request.employee_id
    leave_service = LeaveCalculationServ(scope)
    year = request.GET.get('year')
    resp = leave_service.employee_leave_mapping(year)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response

#  EMPLOYEE LEAVE COUNT
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_leave_count(request):
    scope = request.scope
    employee_id = request.employee_id
    leave_count=LeaveCalculationServ(scope)
    get_leave_count=leave_count.employee_leavecount(request,employee_id)
    return HttpResponse(get_leave_count, content_type="application/json")

def leave_approver_status(request,leave_id):
    scope = request.scope
    leave_service = LeaveApproveService(scope)
    user_id = request.employee_id
    leave_data = json.loads(request.body)
    check_approve_status = leave_service.approved_status(leave_id)
    if check_approve_status == False:
        success_obj = MessageResponse()
        success_obj.set_status(StatusType.FAILED)
        success_obj.set_message('Invalid leaverequest')
        response = HttpResponse(success_obj.get(), content_type="application/json")
        return response
    approve_data = leave_service.approve_status_data(leave_data)
    if approve_data == False:
        success_obj = MessageResponse()
        success_obj.set_status(StatusType.FAILED)
        success_obj.set_message('Invalid Approvestatus')
        response = HttpResponse(success_obj.get(), content_type="application/json")
        return response
    approve_request_update = leave_service.approve_status_update(user_id, leave_data, leave_id)
    response = HttpResponse(approve_request_update.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_leave_count(request):
    scope = request.scope
    employee_id = request.employee_id
    leave_count=LeaveCalculationServ(scope)
    get_leave_count=leave_count.employee_leavecount(request,employee_id)
    return HttpResponse(get_leave_count, content_type="application/json")