from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from attendanceservice.service.attendancedocumentservice import AttendanceDocumentService
from rest_framework.permissions import IsAuthenticated
from utilityservice.data.response.nwisefinpage import NWisefinPage
from attendanceservice.service.checkinlogservice import CheckInLogService
from attendanceservice.service.attendanceservice import DailyAttendanceService
from docservice.service.documentservice import DocumentsService
from attendanceservice.data.request.attendancerequest import CheckInLogRequest
from attendanceservice.util.responsemessage import MessageResponse, StatusType
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription
from utilityservice.data.response.nwisefinsuccess import SuccessMessage
from attendanceservice.service import attendacescheduler
from django.http import HttpResponse
import json
from io import BytesIO
import pandas as pd
import datetime

# Check In Log
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def check_in(request):
    scope = request.scope
    employee_id = request.employee_id
    leave_service = CheckInLogService(scope)
    mode = request.GET.get('mode', 1)
    if request.method == 'POST':
        leave_data = json.loads(request.body)
        req_data = CheckInLogRequest(leave_data)
        #  CHECK IN OUT VALIDATION
        duplicate_entry = leave_service.check_in_out_val(employee_id, mode)
        if duplicate_entry == False:
            success_obj = MessageResponse()
            success_obj.set_status(StatusType.FAILED)
            success_obj.set_message('Invalid Check in / Check out')
            response = HttpResponse(success_obj.get(), content_type="application/json")
            return response

        # ORG VALIDATION
        org_id=leave_service.get_org_id(employee_id)
        if org_id == None:
            success_obj = MessageResponse()
            success_obj.set_status(StatusType.FAILED)
            success_obj.set_message('Employee org Mapping missing')
            response = HttpResponse(success_obj.get(), content_type="application/json")
            return response

        # LOCATION VALIDATION
        loc_val = leave_service.location_validation(req_data, org_id)
        if loc_val['status'] == False:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(loc_val['msg'])
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response

        org_arc_id = loc_val['org_arc_id']

        # IP VALIDATION
        # loc_val = leave_service.ip_validation(request, org_id)
        # if loc_val['status'] == False:
        #     error_obj = MessageResponse()
        #     error_obj.set_status(StatusType.FAILED)
        #     error_obj.set_message(loc_val['msg'])
        #     response = HttpResponse(error_obj.get(), content_type="application/json")
        #     return response

        #  CHECK IN/OUT MODE
        checkin_mode = leave_service.get_checkin_mode(request)

        resp = leave_service.checkin_out_log(employee_id, mode,org_arc_id,checkin_mode)
    else:
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        admin = request.GET.get('admin', 0)
        if admin == 0:
            resp = leave_service.check_in_log_list(vys_page, employee_id)
        else:
            resp = leave_service.check_in_general_list(vys_page)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_check_in_log(request, log_id):
    scope = request.scope
    leave_service = CheckInLogService(scope)
    if request.method == 'GET':
        resp = leave_service.fetch_check_in_log(log_id)
    else:
        resp = leave_service.delete_check_in_log(log_id)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def attendance_summary(request):
    action = request.GET.get('action')
    scope = request.scope

    if action == None :
        employee_id = request.employee_id
        atd_serv = DailyAttendanceService(scope)
        resp_data = atd_serv.attendance_summary(employee_id,request)
        response = HttpResponse(resp_data.get(), content_type="application/json")
        return response

    elif action == 'employee_report':
        employee_id = request.GET.get('emp_id')
        atd_serv = DailyAttendanceService(scope)
        resp_data = atd_serv.attendance_summary(employee_id, request)
        response = HttpResponse(resp_data.get(), content_type="application/json")
        return response

    elif action == 'report':
        atd_serv = DailyAttendanceService(scope)
        att_data = json.loads(request.body)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_data = atd_serv.attendance_report(request,att_data,vys_page)
        response = HttpResponse(resp_data.get(), content_type="application/json")
        return response

    elif action == 'exl_report':
        atd_serv = DailyAttendanceService(scope)
        att_data = json.loads(request.body)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_data = atd_serv.attendance_new_report(request, att_data, vys_page)
        response = HttpResponse(resp_data.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def attendanceexcel(request):
    scope = request.scope
    atd_serv = DailyAttendanceService(scope)
    month_year=atd_serv.month_year_report(request)
    month=month_year['month']
    year=month_year['year']
    resp_data = atd_serv.attendancereportexcel(request,month,year)

    with BytesIO() as b:
        # Use the StringIO object as the filehandle.
        writer = pd.ExcelWriter(b, engine='xlsxwriter')
        resp_data.to_excel(writer, sheet_name='Sheet1')
        writer.save()
        filename = 'monthly_attendance '+str(year)+"-"+str(month)
        # filename = 'monthly_attendance '+str(year)+"-"+str(month)+str(datetime.datetime.now())
        content_type = 'application/vnd.ms-excel'
        response = HttpResponse(b.getvalue(), content_type=content_type)
        response['Content-Disposition'] = 'attachment; filename="' + filename + '.xlsx"'
        return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_attendance(request, attendance_id):
    scope = request.scope
    atd_serv = DailyAttendanceService(scope)
    if request.method == 'GET':
        resp_data = atd_serv.fetch_attendance(attendance_id)
    else:
        resp_data = atd_serv.delete_attendance(attendance_id)
    response = HttpResponse(resp_data.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def per_day_attendance(request):
    serv = attendacescheduler
    resp = serv.attendance_scheduler_apicall(request)
    if resp == False:
        resp_data = MessageResponse()
        resp_data.set_status(StatusType.FAILED)
        resp_data.set_message('Scheduler already done')
    else:
        resp_data = MessageResponse()
        resp_data.set_status(StatusType.SUCCESS)
        resp_data.set_message(SuccessMessage.CREATE_MESSAGE)
    response = HttpResponse(resp_data.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def per_day_log(request):
    # page = request.GET.get('page', 1)
    # page = int(page)
    # vys_page = NWisefinPage(page, 10)
    scope = request.scope
    employee_id = request.employee_id
    mode = request.GET.get('mode', 1)
    serv = CheckInLogService(scope)
    if mode == 1:
        resp_data = serv.per_day_response(employee_id)
    else:
        resp_data = serv.per_day_data_list(employee_id)
    response = HttpResponse(resp_data.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def per_day_log_employee(request,emp_id):
    scope = request.scope
    serv = CheckInLogService(scope)
    resp_data = serv.perday_log(request,emp_id)
    response = HttpResponse(resp_data.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def attendance_download_file(request, file_id):
    scope = request.scope
    if request.method == 'GET':
        try:
            doc_serv = AttendanceDocumentService(scope)
            doc_id = doc_serv.get_file_id_by_id(file_id)
            doc_service = DocumentsService(scope)
            response = doc_service.doc_download(doc_id, request)
            return response
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DOCUMENT_ID)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response
    elif request.method == 'DELETE':
        doc_serv = AttendanceDocumentService(scope)
        doc_id = doc_serv.get_file_id_by_id(file_id)
        response = doc_serv.attendance_delete(doc_id)
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def day_log_summary(request):
    scope = request.scope
    employee_id = request.employee_id
    serv = CheckInLogService(scope)
    resp_data = serv.check_in_log_history(employee_id,request)
    response = HttpResponse(resp_data.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def payroll_attendance(request):
    scope = request.scope
    serv = DailyAttendanceService(scope)
    resp_data = serv.payroll_attendance_serv(request)
    response = HttpResponse(resp_data, content_type="application/json")
    return response