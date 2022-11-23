import io
import pdb
import traceback
from io import BytesIO
import boto3
import numpy as np
from utilityservice.permissions.util.dbutil import ModuleList,RoleList
from taservice.util.ta_util import Module, Travel_requirements
import requests
from django.http import HttpResponse
from django.http.response import StreamingHttpResponse
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from taservice.data.request.travelrequirement import Cab_request, Bus_request, Air_request, Train_request, \
    AccomodationBooking_Request, No_show_req
from taservice.service.admin_ser import Admin
from taservice.service.travelrequirement import Cab_requirement, Bus_requirement, Air_requirement, Train_requirement, \
    AccomodationBooking_requirement, Booking_requirement
# from taservice.data.request.
from rest_framework.permissions import IsAuthenticated
from xhtml2pdf import pisa
from taservice.data.request.approvedby import Ecf_req
from taservice.service.approvelist import Approve_list
from taservice.service.branch_emp_ser import Branch_emp_ser
from taservice.service.date_relaxation_ser import Date_relaxation_ser
from taservice.service.ecf_entry import Ecf_entry
from taservice.service.emp_name_get import Tourno_details
from taservice.service.onbehalf import Onbehalf_service
from taservice.service.payment import Payment
from taservice.service.report_ser import Report_ser
from nwisefin import settings
from utilityservice.data.response.nwisefinpage import NWisefinPage

# from utilityservice.service.dbutil import DataBase
from utilityservice.permissions.filter.commonpermission import ModulePermission

from utilityservice.service.ta_api_service import ApiService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from taservice.service.tourmaker import TourMaker
from taservice.service.tourexpense import TourExpense
from taservice.service.tourapprovedby import TourApprovedby
from taservice.service.touradvance import TourAdvance
from taservice.service.tourmaker import TourMaker
# from taservice.service.ta_email import ta_email
from taservice.data.request.tourmaker import TourRequest, Chat_Box, Booking
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from taservice.data.request.tourapproved import TourApprovedbyRequest
from taservice.data.request.tourallowance import Allowancerequest
from taservice.service.holiday_deim import HolidayDeim
from taservice.service.glmap_service import Glmap_ser
from django.db import transaction, connection
from taservice.service.employeemapping import EmployeemappingData
from taservice.service.holiday import HolidayData
from taservice.service.elligible_amount_ser import El_lod_ser
import json
from datetime import datetime
import pytz
from taservice.service.common_dropdown_ser import Common_dropdown_ser
from taservice.service.tourallowance import Tour_allowance,Tour_grade
from taservice.data.request.tol_amo_pkmo_req import Tol_amo_pkmo_req, Local_dept_res
from taservice.service.packing_moving_ser import Packing_moving_ser
from taservice.service.driver_data_ser import Driver_bata
from taservice.service.tourcancel import Canceltour
from taservice.data.request.tourcancel import TourCancelreq
from taservice.util.ta_util import TADocUtil, Validation, App_level, Status, Common_data

from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from taservice.models.tamodels import TADocuments, TourRequest as TourRequest_table, ClaimRequest, Ccbs
from taservice.util.ta_util import App_type,DocModule
from nwisefin.settings import BASE_DIR, logger, SERVER_IP
import pandas as pd
val_url = settings.VYSFIN_URL

IST = pytz.timezone('Asia/Kolkata')
datetime_ist = datetime.now(IST)
today = datetime_ist.strftime('%Y-%m-%d')

@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def tour_request(request):
    try:
        for i in request.FILES.getlist('file'):
            file_name = i.name
            extension = file_name.split('.')[-1]
            scope = request.scope
            file_validation=Validation(scope)
            filetype_check = file_validation.fileexe_validation(extension)
            if filetype_check is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_FILETYPE)
                error_obj.set_description(ErrorDescription.SUPPORTED_FILE_TYPES)
                response = HttpResponse(error_obj.get())
                return HttpResponse(response, content_type='application/json')
    except KeyError:
        pass
    with transaction.atomic():
        try:
            tourdata = json.loads(request.data.dict().get('data'))
            scope = request.scope
            Tour_service = TourMaker(scope)
            # user_id = request.user.id
            vysfinservice = ApiService(scope)
            # emp = vysfinservice.get_emp_id(request, user_id)
            employee_id = request.employee_id
            tour = TourRequest(tourdata)
            resp_obj = Tour_service.create_tour(tourdata,tour, employee_id, request)

            if isinstance(resp_obj, NWisefinError):
                return HttpResponse(resp_obj.get(), content_type='application/json')


            # refid = resp_obj.message
            if len(request.FILES) !=0:
                docmodule_obj = DocModule()
                params = {}
                # params['module'] = docmodule_obj.TA
                # params['ref_id'] = refid
                # params['ref_type'] = docmodule_obj.TA
                # params['']
                # new_tour=resp_obj.get()
                tour_id=resp_obj.message
                params['tour_id']=tour_id
                params['ref_type']=TADocUtil.TOUR
                doc_module=docmodule_obj.TA
                doc_serv=Booking_requirement(scope)
                doc_serv=doc_serv.insert_tadoc(request,params)

                # response_obj=vysfinservice.doc_upload(request, doc_module,refid)
                # for doc_data in response_obj['data']:
                #     ta_doc = TADocuments()
                #     ta_doc.file_id = doc_data['id']
                #     ta_doc.ref_id = refid
                #     ta_doc.request_id = refid
                #     ta_doc.ref_type = TADocUtil.TOUR
                #     ta_doc.file_name = doc_data['file_name']
                #     ta_doc.gen_file_name = doc_data['gen_file_name']
                #     ta_doc.created_by = employee_id
                #     ta_doc.save()
                # success_obj = NWisefinSuccess()
                # success_obj.set_status(SuccessStatus.SUCCESS)
                # success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                return HttpResponse(doc_serv.get(), content_type='application/json')
            else:
                if resp_obj.status=="success":
                    success_obj = NWisefinSuccess()
                    success_obj.set_status(SuccessStatus.SUCCESS)
                    success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                    return HttpResponse(success_obj.get(), content_type='application/json')
                else:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(resp_obj.description)
                    return HttpResponse(error_obj.get(), content_type='application/json')

        except Exception as e:
            exc=traceback.format_exc()
            error_obj = NWisefinError()
            transaction.set_rollback(True)
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            logger.info('ta_ tour_request- ' + str(e)+str(exc))
            return HttpResponse(error_obj.get(), content_type='application/json')

# @csrf_exempt
# @api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def tour_data(request):
#     try:
#         page = request.GET.get('page', 1)
#         page = int(page)
#         vys_page =NWisefinPage(page, 10)
#         scope = request.scope
#         Tour_service = TourMaker(scope)
#         employee_id=request.employee_id
#         onb = request.GET.get('onbehalf', 0)
#         request_date = request.GET.get('request_date','')
#         tour_no = request.GET.get('tour_no','')
#         resp_obj = Tour_service.get_alltour(employee_id,onb,vys_page,request_date,tour_no,request)
#         return HttpResponse(resp_obj.get(), content_type='application/json')
#     except Exception as e:
#         exc=traceback.format_exc()
#         error_obj = NWisefinError()
#         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#         error_obj.set_description(str(e))
#         logger.info('ta_ tour_data- ' + str(e)+str(exc))
#         return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def nac_tour_data(request):
    try:
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        Tour_service = TourMaker(scope)
        employee_id=request.employee_id
        # emp = Employee.objects.get(user_id=user_id)
        # employee_id = emp.id
        onb = request.GET.get('onbehalf')
        status = request.GET.get('status')
        apptype = request.GET.get('apptype')
        request_date = request.GET.get('request_date','')
        tour_no = request.GET.get('tour_no','')
        resp_obj = Tour_service.nac_get_alltour(employee_id,onb,vys_page,request_date,tour_no,request,status,apptype)
        return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ tour_data- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')
# @csrf_exempt
# @api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def all_tour_report(request):
#     try:
#         scope = request.scope
#         page = request.GET.get('page', 1)
#         view = request.GET.get('view', 1)
#         start_date = request.GET.get('start_date')
#         end_date = request.GET.get('end_date')
#         page = int(page)
#         vys_page = NWisefinPage(page, 10)
#         Tour_service = TourMaker(scope)
#         employee_id=request.employee_id
#         # emp = Employee.objects.get(user_id=user_id)
#         # employee_id = emp.id
#         emp_id = request.GET.get('emp_id')
#         request_date = request.GET.get('request_date','')
#         tour_no = request.GET.get('tour_no','')
#         if int(view)==1:
#             resp_obj = Tour_service.all_tour_report(emp_id,vys_page,request_date,tour_no,request,start_date,end_date)
#             return HttpResponse(resp_obj.get(), content_type='application/json')
#         else:
#             resp_obj = Tour_service.all_tour_report_download( emp_id, vys_page, request_date, tour_no, request,start_date,end_date)
#             return resp_obj
#             # return HttpResponse(resp_obj, content_type='application/json')
#         # resp_obj = Tour_service.all_tour_report(employee_id,onb,vys_page,request_date,tour_no,request)
#         # return HttpResponse(resp_obj.get(), content_type='application/json')
#     except Exception as e:
#         exc=traceback.format_exc()
#         error_obj = NWisefinError()
#         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#         error_obj.set_description(str(e))
#         logger.info('ta_ all_tour_report- ' + str(e)+str(exc))
#         return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def tourrequest_get(request, tour_id):
    try:
        # user_id = request.user.id
        employee_id=request.employee_id
        scope = request.scope
        service=Validation(scope)
        module_permission = ApiService(scope)
        role_arr = module_permission.employee_modulerole_get(employee_id, ModuleList.Ta_Expense, request)
        ceo_get = module_permission.onb_permission(request, employee_id)
        if RoleList.admin not in role_arr and (json.loads(ceo_get))["ceo"] != True:

            permission=service.permisssion_check(tour_id,employee_id)
            if permission is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.VALID_USER)
                return HttpResponse(error_obj.get(), content_type='application/json')
        scope = request.scope
        tour_service = TourMaker(scope)
        if request.method=='GET':
            resp_obj = tour_service.get_tour( tour_id,request)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ tourrequest_get- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def tour_reason(request):
    if request.method == 'GET':
        scope = request.scope
        Tour_service = TourMaker(scope)
        reason= request.GET.get('name','')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = Tour_service.get_tourreason(reason,vys_page)
        return HttpResponse(resp_obj.get(), content_type='application/json')

    elif request.method == 'POST':
        tourdata = json.loads(request.body)
        scope = request.scope
        Tour_service = TourMaker(scope)
        # user_id = request.user.id
        employee_id=request.employee_id
        resp_obj = Tour_service.insert_tourreason(tourdata, employee_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')

@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def tour_approve(request):
    if request.method == 'POST':
        try:
            tourdata = json.loads(request.body)
            scope = request.scope
            Tour_service = TourApprovedby(scope)
            # user_id = request.user.id
            employee_id=request.employee_id
            if "approvedby" in tourdata and tourdata['approvedby']==0:
                tourdata['login_emp'] = employee_id
            resp_obj = Tour_service.insert_approvedby(tourdata,request)
            return HttpResponse(resp_obj.get(), content_type='application/json')
        except Exception as e:
            exc=traceback.format_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            logger.info('ta_ tour_approve- ' + str(e)+str(exc))
            return HttpResponse(error_obj.get(), content_type='application/json')

# @csrf_exempt
# @api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def approver_data(request, type):
#     try:
#         page = request.GET.get('page', 1)
#         status = request.GET.get('status')
#         makerid = request.GET.get('makerid')
#         request_date = request.GET.get('request_date','')
#         tour_no = request.GET.get('tour_no','')
#         page = int(page)
#         vys_page =NWisefinPage(page, 10)
#         scope = request.scope
#         tour_service = TourApprovedby(scope)
#         # user_id = request.user.id
#         employee_id=request.employee_id
#         resp_obj = tour_service.get_approverdata(employee_id, type.upper(),vys_page,status,makerid,request_date,tour_no,request)
#         return HttpResponse(resp_obj.get(), content_type='application/json')
#     except Exception as e:
#         exc=traceback.format_exc()
#         error_obj = NWisefinError()
#         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#         error_obj.set_description(str(e))
#         logger.info('ta_ approver_data- ' + str(e)+str(exc))
#         return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def nac_approver_data(request, type):
    try:
        scope = request.scope
        page = request.GET.get('page', 1)
        status = request.GET.get('status')
        makerid = request.GET.get('makerid')
        branch_id = request.GET.get('branch_id')
        onbehalf = request.GET.get('onbehalf')
        request_date = request.GET.get('request_date','')
        tour_no = request.GET.get('tour_no','')
        cancel= request.GET.get('cancel')
        if cancel is not None:
            cancel=int(cancel)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        tour_service = TourApprovedby(scope)
        # user_id = request.user.id
        employee_id=request.employee_id
        # emp = Employee.objects.get(user_id=user_id)
        # employee_id = emp.id
        resp_obj = tour_service.nac_get_approverdata(employee_id, type.upper(), vys_page, status, makerid, request_date,
                                                     tour_no, request, onbehalf,branch_id,cancel)
        return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ approver_data- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@transaction.atomic
@csrf_exempt
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def tour_advance(request):
    try:
        if request.method == 'GET':
            page = request.GET.get('page', 1)
            page = int(page)
            vys_page =NWisefinPage(page, 10)
            scope = request.scope
            Advance_service = TourAdvance(scope)
            # user_id = request.user.id
            employee_id=request.employee_id
            onb = request.GET.get('onbehalf')
            apptype = request.GET.get('apptype')
            status = request.GET.get('status')
            request_date = request.GET.get('request_date','')
            tour_no = request.GET.get('tour_no','')
            resp_obj = Advance_service.get_advance(employee_id,onb,vys_page,request_date,tour_no,request,apptype,status)
            return HttpResponse(resp_obj.get(), content_type='application/json')

        elif request.method == 'POST':
            advance = json.loads(request.body)
            scope = request.scope
            Advance_service = TourAdvance(scope)
            # user_id = request.user.id
            employee_id=request.employee_id
            resp_obj = Advance_service.create_advance(advance, employee_id,request)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ tour_advance- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def advance_get(request, tour_id):
    try:
        # user_id = request.user.id
        employee_id=request.employee_id
        report = request.GET.get('report', 0)
        scope = request.scope
        service=Validation(scope)
        permission=service.permisssion_check(tour_id,employee_id)
        module_permission = ApiService(scope)
        role_arr = module_permission.employee_modulerole_get(employee_id, ModuleList.Ta_Expense, request)
        ceo_get = module_permission.onb_permission(request, employee_id)
        if RoleList.admin not in role_arr and (json.loads(ceo_get))["ceo"] != True:
            if permission is False and int(report)!=1:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.VALID_USER)
                return HttpResponse(error_obj.get(), content_type='application/json')
        scope = request.scope
        Advance_service = TourAdvance(scope)
        if request.method=='GET':
            resp_obj = Advance_service.get_tour_advance(tour_id,request)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ advance_get- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def advance_summary(request):
    try:
        if request.method == 'GET':
            page = request.GET.get('page', 1)
            page = int(page)
            vys_page =NWisefinPage(page, 10)
            scope = request.scope
            Advance_service = TourAdvance(scope)
            # user_id = request.user.id
            employee_id=request.employee_id
            onb = request.GET.get('onbehalf')
            request_date = request.GET.get('request_date','')
            tour_no = request.GET.get('tour_no','')
            resp_obj = Advance_service.advance_summary(employee_id,onb,vys_page,request_date,tour_no,request)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ advance_summary- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def admin_summary(request):
    try:
        if request.method == 'GET':

            page = request.GET.get('page', 1)
            request_date = request.GET.get('request_date', '')
            tour_no = request.GET.get('tour_no', '')
            status = request.GET.get('status')
            makerid = request.GET.get('makerid')
            branch_id = request.GET.get('branch_id')
            page = int(page)
            vys_page = NWisefinPage(page, 10)
            scope = request.scope
            admin_ser = Admin(scope)
            type = request.GET.get('type').lower()
            employee_id = request.employee_id
            if type==App_type.tour:
                module_permission = ApiService(scope)
                role_arr = module_permission.employee_modulerole_get(employee_id, ModuleList.Ta_Travel, request)
                if RoleList.admin not in role_arr:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_ADMIN)
                    return HttpResponse(error_obj.get(), content_type='application/json')
                booking_type = request.GET.get('booking_type',0)
                booking_status = request.GET.get('booking_status')
                if booking_status is not None:
                    booking_status=int(booking_status)
                resp_obj = admin_ser.admin_summary_tour(employee_id,vys_page,status,makerid,request_date,tour_no,request,int(booking_type),booking_status,branch_id)
                return HttpResponse(resp_obj.get(), content_type='application/json')
            elif type==App_type.claim:
                resp_obj = admin_ser.admin_summary_expense(employee_id, type.upper(), vys_page, status, makerid,
                                                             request_date, tour_no, request,branch_id)
                return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ admin_summary- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def expenselist(request):
    if request.method == 'GET':
        scope = request.scope
        Tour_service = TourExpense(scope)
        expense= request.GET.get('name')
        resp_obj = Tour_service.get_expenselist(expense)
        return HttpResponse(resp_obj.get(), content_type='application/json')

    elif request.method == 'POST':
        tourdata = json.loads(request.body)
        scope = request.scope
        Tour_service = TourExpense(scope)
        # user_id = request.user.id
        employee_id=request.employee_id
        resp_obj = Tour_service.insert_expenselist(tourdata, employee_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def dailydeim_insert(request):
    try:
        if request.method == 'POST':
            tourdata = json.loads(request.body)
            scope = request.scope
            Tour_service = TourExpense(scope)
            # user_id = request.user.id
            employee_id=request.employee_id
            resp_obj = Tour_service.create_dailydeim(tourdata, employee_id,request)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ dailydeim_insert- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def localdeputation(request):
    try:
        if request.method == 'POST':
            tourdata = json.loads(request.body)
            scope = request.scope
            Tour_service = TourExpense(scope)
            # user_id = request.user.id
            employee_id=request.employee_id
            resp_obj = Tour_service.create_local_deputation(tourdata, employee_id,request)
            return HttpResponse(resp_obj.get(), content_type='application/json')

    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ localdeputation- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def incidental_insert(request):
    try:
        if request.method == 'POST':
            tourdata = json.loads(request.body)
            scope = request.scope
            Tour_service = TourExpense(scope)
            # user_id = request.user.id
            employee_id=request.employee_id
            resp_obj = Tour_service.create_incidental(tourdata, employee_id,request)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ incidental_insert- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def localconv_insert(request):
    try:
        if request.method == 'POST':
            tourdata = json.loads(request.body)
            scope = request.scope
            Tour_service = TourExpense(scope)
            # user_id = request.user.id
            employee_id=request.employee_id
            resp_obj = Tour_service.create_localconveyence(tourdata, employee_id,request)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ localconv_insert- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def lodging_insert(request):
    try:
        if request.method == 'POST':
            tourdata = json.loads(request.body)
            scope = request.scope
            Tour_service = TourExpense(scope)
            # user_id = request.user.id
            employee_id=request.employee_id
            resp_obj = Tour_service.create_lodging(tourdata, employee_id,request)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ lodging_insert- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def misc_insert(request):
    try:
        if request.method == 'POST':
            tourdata = json.loads(request.body)
            scope = request.scope
            Tour_service = TourExpense(scope)
            # user_id = request.user.id
            employee_id=request.employee_id
            resp_obj = Tour_service.create_misc(tourdata, employee_id,request)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ misc_insert- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def packingmvg_insert(request):
    try:
        if request.method == 'POST':
            tourdata = json.loads(request.body)
            scope = request.scope
            Tour_service = TourExpense(scope)
            # user_id = request.user.id
            employee_id=request.employee_id
            resp_obj = Tour_service.create_packingmoving(tourdata, employee_id,request)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ packingmvg_insert- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def travel_insert(request):
    try:
        if request.method == 'POST':
            tourdata = json.loads(request.body)
            scope = request.scope
            Tour_service = TourExpense(scope)
            # user_id = request.user.id
            employee_id=request.employee_id
            resp_obj = Tour_service.create_travel(tourdata, employee_id,request)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ travel_insert- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def associate_insert(request):
    try:
        if request.method == 'POST':
            tourdata = json.loads(request.body)
            scope = request.scope
            Tour_service = TourExpense(scope)
            user_id = request.user.id
            vysfinservice = ApiService(scope)
            emp = vysfinservice.get_emp_id(request, user_id)
            employee_id = emp['id']
            resp_obj = Tour_service.create_associate(tourdata, employee_id, request)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ associate_insert- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

# @csrf_exempt
# @api_view(['POST'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def automate_email(request):
#     try:
#         tour_id = type
#         user_id = request.user.id
#         scope = request.scope
#         vysfinservice = ApiService(scope)
#         emp = vysfinservice.get_emp_id(request, user_id)
#         report = request.GET.get('report', 0)
#         employee_id = emp['id']
#         emp_namee = emp['full_name']
#         Tour_service = ta_email(scope)
#         if request.method == 'POST':
#             scope = request.scope
#             resp_obj = Tour_service.mail_data(request, emp)
#             return HttpResponse(error_obj.get(), content_type='application/json')
#     except Exception as e:
#         traceback.print_exc()
#         error_obj = NWisefinError()
#         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#         error_obj.set_description(str(e))
#         logger.info('ta_mail_info- ' + str(e))
#         return HttpResponse(error_obj.get(), content_type='application/json')


@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def associate_tour_get(request, tour_id):
    try:
        user_id = request.user.id
        scope = request.scope
        vysfinservice = ApiService(scope)
        emp = vysfinservice.get_emp_id(request, user_id)
        report = request.GET.get('report', 0)
        employee_id = emp['id']
        service = TourExpense(scope)
        if request.method=='GET':
            scope = request.scope
            validation_service = Validation(scope)
            permission = validation_service.permisssion_check(tour_id, employee_id)
            module_permission = ApiService(scope)
            role_arr = module_permission.employee_modulerole_get(employee_id, ModuleList.Ta_Expense, request)
            # if RoleList.admin and RoleList.checker not in role_arr:
            if RoleList.admin not in role_arr and RoleList.checker not in role_arr:
                if permission is False and int(report) != 1:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.VALID_USER)
                    return HttpResponse(error_obj.get(), content_type='application/json')
            resp_obj = service.get_associate_tour(tour_id,request)
            return HttpResponse(resp_obj.get(), content_type='application/json')
        elif request.method == 'DELETE':
            resp_obj = service.delete_associate(tour_id,request,employee_id)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ associate_tour_get- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def claimreq_tour_get(request, tour_id):
    try:
        # user_id = request.user.id
        employee_id=request.employee_id
        report = request.GET.get('report', 0)
        scope = request.scope
        service = Validation(scope)
        module_permission = ApiService(scope)
        role_arr = module_permission.employee_modulerole_get(employee_id, ModuleList.Ta_Expense, request)
        # if RoleList.admin and RoleList.checker not in role_arr:
        if RoleList.admin not in role_arr and RoleList.checker not in role_arr:
            permission = service.permisssion_check(tour_id, employee_id)
            if permission is False and int(report)!=1:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.VALID_USER)
                return HttpResponse(error_obj.get(), content_type='application/json')
        scope = request.scope
        service = TourExpense(scope)
        if request.method=='GET':
            resp_obj = service.get_claimreq_tour(tour_id,request)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ claimreq_tour_get- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def claimreq_tour_get_mobile(request, tour_id):
    try:
        # user_id = request.user.id
        scope=request.scope
        employee_id=request.employee_id
        report = request.GET.get('report', 0)
        scope = request.scope
        service = Validation(scope)
        permission = service.permisssion_check(tour_id, employee_id)
        if permission is False and int(report)!=1:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.VALID_USER)
            return HttpResponse(error_obj.get(), content_type='application/json')
        scope = request.scope
        service = TourExpense(scope)
        if request.method=='GET':
            resp_obj = service.get_claimreq_tour_mobile(tour_id,request)
            return HttpResponse(resp_obj.get(), content_type='application/json')

    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ claimreq_tour_get_mobile- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_each_expense(request, tour_id):
    try:
        # user_id = request.user.id
        scope=request.scope
        employee_id=request.employee_id
        scope = request.scope
        service = Validation(scope)
        permission = service.permisssion_check(tour_id, employee_id)
        if permission is False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.VALID_USER)
            return HttpResponse(error_obj.get(), content_type='application/json')
        scope = request.scope
        service = TourExpense(scope)
        if request.method=='GET':
            resp_obj = service.get_each_expense(tour_id,request)
            resp = json.dumps(resp_obj, default=lambda o: o.__dict__)
            return HttpResponse(resp, content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ get_each_expense- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

# @csrf_exempt
# @api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def claimreq_get(request):
#     try:
#         page = request.GET.get('page', 1)
#         page = int(page)
#         vys_page =NWisefinPage(page, 10)
#         scope = request.scope
#         Advance_service = TourExpense(scope)
#         # user_id = request.user.id
#         employee_id=request.employee_id
#         onb = request.GET.get('onbehalf', 0)
#         resp_obj = Advance_service.get_claimreq(employee_id,onb,vys_page,request)
#         return HttpResponse(resp_obj.get(), content_type='application/json')
#     except Exception as e:
#         exc=traceback.format_exc()
#         error_obj = NWisefinError()
#         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#         error_obj.set_description(str(e))
#         logger.info('ta_ claimreq_get- ' + str(e)+str(exc))
#         return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def dailydeim_tour_get(request, tour_id):
    try:
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        report = request.GET.get('report', 0)
        validation_service = Validation(scope)
        service = TourExpense(scope)
        module_permission = ApiService(scope)
        role_arr = module_permission.employee_modulerole_get(employee_id,ModuleList.Ta_Expense, request)
        if request.method == 'GET':
            # if RoleList.admin and RoleList.checker not in role_arr:
            if RoleList.admin not in role_arr and RoleList.checker not in role_arr:
                permission = validation_service.permisssion_check(tour_id, employee_id)
                if permission is False and int(report) != 1:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.VALID_USER)
                    return HttpResponse(error_obj.get(), content_type='application/json')
            resp_obj = service.get_dailydeim_tour(tour_id)
            return HttpResponse(resp_obj.get(), content_type='application/json')
        elif request.method == 'DELETE':
            resp_obj = service.delete_dailydeim(tour_id,request,employee_id)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ dailydeim_tour_get- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def localdeputation_get(request, tour_id):
    try:
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        report = request.GET.get('report', 0)
        validation_service = Validation(scope)
        if request.method=='GET':
            permission = validation_service.permisssion_check(tour_id, employee_id)
            if permission is False and int(report) != 1:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.VALID_USER)
                return HttpResponse(error_obj.get(), content_type='application/json')
            service = TourExpense(scope)
            resp_obj = service.get_deputation(tour_id)
            return HttpResponse(resp_obj.get(), content_type='application/json')
        elif request.method == 'DELETE':
            service = TourExpense(scope)
            resp_obj = service.delete_deputation(tour_id,request,employee_id)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ localdeputation_get- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def incidental_tour_get(request, tour_id):
    try:
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        report = request.GET.get('report', 0)
        service = TourExpense(scope)
        if request.method=='GET':
            validation_service = Validation(scope)
            permission = validation_service.permisssion_check(tour_id, employee_id)
            module_permission = ApiService(scope)
            role_arr = module_permission.employee_modulerole_get(employee_id, ModuleList.Ta_Expense, request)
            if RoleList.admin not in role_arr:
                if permission is False and int(report) != 1:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.VALID_USER)
                    return HttpResponse(error_obj.get(), content_type='application/json')
            resp_obj = service.get_incidental_tour(tour_id)
            return HttpResponse(resp_obj.get(), content_type='application/json')
        elif request.method == 'DELETE':
            resp_obj = service.delete_incidental(tour_id,request,employee_id)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ incidental_tour_get- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def localconv_tour_get(request, tour_id):
    try:
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        report = request.GET.get('report', 0)
        validation_service = Validation(scope)
        service = TourExpense(scope)
        if request.method=='GET':
            permission = validation_service.permisssion_check(tour_id, employee_id)
            module_permission = ApiService(scope)
            role_arr = module_permission.employee_modulerole_get(employee_id, ModuleList.Ta_Expense, request)
            # if RoleList.admin and RoleList.checker not in role_arr:
            if RoleList.admin not in role_arr and RoleList.checker not in role_arr:
                if permission is False and int(report) != 1:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.VALID_USER)
                    return HttpResponse(error_obj.get(), content_type='application/json')
            resp_obj = service.get_localconveyence_tour(tour_id)
            return HttpResponse(resp_obj.get(), content_type='application/json')
        elif request.method == 'DELETE':
            resp_obj = service.delete_localconv(tour_id,request,employee_id)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ localconv_tour_get- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def lodging_tour_get(request, tour_id):
    try:
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        report = request.GET.get('report', 0)
        validation_service = Validation(scope)
        service = TourExpense(scope)
        if request.method=='GET':
            module_permission = ApiService(scope)
            role_arr = module_permission.employee_modulerole_get(employee_id, ModuleList.Ta_Expense, request)
            # if RoleList.admin and RoleList.checker not in role_arr:
            if RoleList.admin not in role_arr and RoleList.checker not in role_arr:
                permission = validation_service.permisssion_check(tour_id, employee_id)
                if permission is False and int(report) != 1:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.VALID_USER)
                    return HttpResponse(error_obj.get(), content_type='application/json')
            resp_obj = service.get_lodging_tour(tour_id,request)
            return HttpResponse(resp_obj.get(), content_type='application/json')
        elif request.method == 'DELETE':
            resp_obj = service.delete_lodging(tour_id,request,employee_id)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ lodging_tour_get- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def misc_tour_get(request, tour_id):
    try:
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        report = request.GET.get('report', 0)
        validation_service = Validation(scope)
        service = TourExpense(scope)
        if request.method=='GET':
            permission = validation_service.permisssion_check(tour_id, employee_id)
            module_permission = ApiService(scope)
            role_arr = module_permission.employee_modulerole_get(employee_id, ModuleList.Ta_Expense, request)
            if RoleList not in role_arr:
                if permission is False and int(report) !=0:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.VALID_USER)
                    return HttpResponse(error_obj.get(), content_type='application/json')
            resp_obj = service.get_misc_tour(tour_id)
            return HttpResponse(resp_obj.get(), content_type='application/json')
        elif request.method == 'DELETE':
            resp_obj = service.delete_misc(tour_id,request,employee_id)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ misc_tour_get- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def packingmvg_tour_get(request, tour_id):
    try:
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        report = request.GET.get('report', 0)
        validation_service = Validation(scope)
        service = TourExpense(scope)
        if request.method=='GET':
            permission = validation_service.permisssion_check(tour_id, employee_id)
            module_permission = ApiService(scope)
            role_arr = module_permission.employee_modulerole_get(employee_id, ModuleList.Ta_Expense, request)
            if RoleList.admin not in role_arr:
                if permission is False and int(report) != 1:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.VALID_USER)
                    return HttpResponse(error_obj.get(), content_type='application/json')
            resp_obj = service.get_packingmoving_tour(tour_id,request)
            return HttpResponse(resp_obj.get(), content_type='application/json')
        elif request.method == 'DELETE':
            resp_obj = service.delete_packing(tour_id,request,employee_id)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ packingmvg_tour_get- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def travel_tour_get(request, tour_id):
    try:
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        service = TourExpense(scope)
        report = request.GET.get('report', 0)
        if request.method=='GET':
            scope = request.scope
            validation_service = Validation(scope)
            permission = validation_service.permisssion_check(tour_id, employee_id)
            module_permission = ApiService(scope)
            role_arr = module_permission.employee_modulerole_get(employee_id, ModuleList.Ta_Expense, request)
            # if RoleList.admin and RoleList.checker not in role_arr:
            if RoleList.admin not in role_arr and RoleList.checker not in role_arr:
                if permission is False and int(report) != 1:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.VALID_USER)
                    return HttpResponse(error_obj.get(), content_type='application/json')
            resp_obj = service.get_travel_tour(tour_id,request)
            return HttpResponse(resp_obj.get(), content_type='application/json')
        elif request.method == 'DELETE':
            resp_obj = service.delete_travel(tour_id,request,employee_id)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ travel_tour_get- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')
@transaction.atomic
@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def expense_movetoapprover(request,type):
    if request.method=='POST' and type=="submit":
        try:
            for i in request.FILES.getlist('file'):
                file_name=i.name
                extension= file_name.split('.')[-1]
                scope = request.scope
                file_validation = Validation(scope)
                filetype_check = file_validation.fileexe_validation(extension)
                if filetype_check is False:
                    error_obj=NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_FILETYPE)
                    error_obj.set_description(ErrorDescription.SUPPORTED_FILE_TYPES)
                    response = HttpResponse(error_obj.get(),content_type='application/json')
                    return HttpResponse(response,content_type='application/json')
        except KeyError:
            pass
        try:
            error_obj = NWisefinError()
            expensedata = json.loads(request.data.dict().get('data'))
            # user_id = request.user.id
            scope = request.scope
            employee_id=request.employee_id
            logger.info('ta_ Expense_submit- ' + str(employee_id) + str(expensedata))
            # if int(expensedata['approvedby'])==employee_id or int(expensedata['approvedby'])==0:
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.MAKER_APPROVER_SAME)
            #     return HttpResponse(error_obj.get(), content_type='application/json')
            valid_service=Validation(scope)
            # approver_check = valid_service.approver_validation(App_type.expense,int(expensedata['approvedby']), request)
            # if approver_check is False:
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.APPROVER_NOT_IN_LIST)
            #     return HttpResponse(error_obj.get(), content_type='application/json')
            exp_maker_check = valid_service.tour_maker_check(expensedata['tourgid'], employee_id)
            if exp_maker_check is False:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.VALID_USER)
                return HttpResponse(error_obj.get(), content_type='application/json')
            scope = request.scope
            service = Date_relaxation_ser(scope)


            service_moveto_vali=service.expense_movetoapprover_vali(request,expensedata)
            if service_moveto_vali !=None:
                if service_moveto_vali.code== 'UNEXPECTED_ERROR':
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(service_moveto_vali.description)
                    return HttpResponse(error_obj.get(),content_type='application/json')
            date_relaxation = service.fetch_date_relaxation_get(expensedata['tourgid'])
            if date_relaxation is not True:
                return HttpResponse(date_relaxation.get(), content_type='application/json')
            scope = request.scope
            expense_service = TourApprovedby(scope)
            resp_obj=expense_service.expense_submit(expensedata,employee_id,request)
            if isinstance(resp_obj,NWisefinError):
                return HttpResponse(resp_obj.get(),content_type='application/json')
            if resp_obj.status=='success':
                scope = request.scope
                tourservice=TourMaker(scope)
                resp_obj=tourservice.update_claim_status(expensedata['tourgid'])

            tour_id = expensedata['tourgid']
            vysfinservice = ApiService(scope)
            if len(request.FILES) !=0:
                docmodule_obj = DocModule()
                params = {}
                params['module'] = docmodule_obj.TA
                params['ref_id'] = tour_id
                params['ref_type'] = docmodule_obj.TA
                doc_module = docmodule_obj.TA
                response_obj = vysfinservice.doc_upload(request, doc_module, tour_id)
                for doc_data in response_obj['data']:
                    ta_doc = TADocuments()
                    ta_doc.file_id = doc_data['id']
                    ta_doc.ref_id = tour_id
                    ta_doc.request_id = tour_id
                    ta_doc.ref_type = TADocUtil.CLAIM
                    ta_doc.file_name = doc_data['file_name']
                    ta_doc.gen_file_name = doc_data['gen_file_name']
                    ta_doc.created_by = employee_id
                    ta_doc.save()
                return HttpResponse(resp_obj.get(), content_type='application/json')
            else:
                return HttpResponse(resp_obj.get(), content_type='application/json')
        except Exception as e:
            exc=traceback.format_exc()
            transaction.set_rollback(True)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            logger.info('ta_ expense_movetoapprover- ' + str(e)+str(exc))
            return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def dailydeim_logic(request, type):
    if type =="logic":
        userdata = json.loads(request.body)
        scope = request.scope
        Tour_service = Tour_grade(scope)
        dtl = userdata
        resp_obj = Tour_service.dailydiem_eligible_amount(dtl,request)
        return HttpResponse(resp_obj, content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def localdeputation_logic(request, type):
    if type =="logic":
        userdata = json.loads(request.body)
        data = Local_dept_res(userdata)
        scope = request.scope
        service = Driver_bata(scope)
        resp = service.deputation_amount(data,request)
        return HttpResponse(resp, content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def incidental_logic(request, type):
    if type =="logic":
        userdata = json.loads(request.body)
        request_data = Allowancerequest(userdata)
        scope = request.scope
        Tour_service = Tour_allowance(scope)
        resp_obj = Tour_service.get_allowanceamount(request_data)
        return HttpResponse(resp_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def localconv_logic(request, type):
    if type =="logic":
        userdata = json.loads(request.body)
        data = Allowancerequest(userdata)
        scope = request.scope
        Tour_service = Tour_allowance(scope)
        dtl = userdata
        resp_obj = Tour_service.get_eligibleamount(dtl, request)
        return HttpResponse(resp_obj, content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def lodging_logic(request, type, elservice=None):
    if type =="logic":
        userdata=json.loads(request.body)
        # data=El_lod_req(userdata)
        scope = request.scope
        elservice=El_lod_ser(scope)
        dtl = userdata
        resp_obj=elservice.get_elligible_amount(dtl, request)
        return HttpResponse(resp_obj,content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def misc_logic(request, type):
    if type =="logic":
        userdata = json.loads(request.body)
        data = Allowancerequest(userdata)
        scope = request.scope
        Tour_service = Tour_allowance(scope)
        resp_obj = Tour_service.get_eligibleamount_misc(data)
        return HttpResponse(resp_obj, content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def packingmvg_logic(request, type):
    if type =="logic":
        userdata = json.loads(request.body)
        data=Tol_amo_pkmo_req(userdata)
        scope = request.scope
        service=Packing_moving_ser(scope)
        # grade=service.get_grade_elligibility(data)
        resp=service.total_amount(data)
        return HttpResponse(resp,content_type='application/json')

@csrf_exempt
@transaction.atomic
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def common_dropdown(request):
    if request.method == 'GET':
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        dropservice = Common_dropdown_ser(scope)
        resp_obj = dropservice.get_common_dropdown(vys_page)
        return HttpResponse(resp_obj.get(), content_type='application/json')

    elif request.method == 'POST':
        data = json.loads(request.body)
        scope = request.scope
        dropservice = Common_dropdown_ser(scope)
        # user_id = request.user.id
        employee_id=request.employee_id
        # emp = Employee.objects.get(user_id=user_id)
        # employee_id = emp.id
        resp_obj = dropservice.insert_common_dropdown(data,employee_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_common_dropdown(request,id):
    if request.method == 'GET':
        scope = request.scope
        dropservice = Common_dropdown_ser(scope)
        resp_obj = dropservice.fetch_dropdown(id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        scope = request.scope
        dropservice = Common_dropdown_ser(scope)
        resp_obj = dropservice.delete_dropdown(id)
        return HttpResponse(resp_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def common_dropdown_get(request,code):
    if request.method == 'GET':
        scope = request.scope
        dropservice = Common_dropdown_ser(scope)
        resp_obj = dropservice.dropdown_code_get(code)
        resp = json.dumps(resp_obj, default=lambda o: o.__dict__)
        response = HttpResponse(resp, content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def common_dropdown_search(request,code):
    if request.method == 'GET':
        scope = request.scope
        dropservice = Common_dropdown_ser(scope)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        query = request.GET.get('query', None)
        resp_obj = dropservice.dropdown_code_search(code ,vys_page, query)
        resp = json.dumps(resp_obj, default=lambda o: o.__dict__)
        response = HttpResponse(resp, content_type="application/json")
        return response

@csrf_exempt
@transaction.atomic
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def common_dropdown_details(request):
    if request.method == 'GET':
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        dropservice = Common_dropdown_ser(scope)
        resp_obj = dropservice.get_cd_details(vys_page)
        return HttpResponse(resp_obj.get(), content_type='application/json')

    elif request.method == 'POST':
        data = json.loads(request.body)
        scope = request.scope
        dropservice = Common_dropdown_ser(scope)
        # user_id = request.user.id
        employee_id=request.employee_id
        resp_obj = dropservice.insert_cd_details(data,employee_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_dropdown_details(request,id):
    if request.method == 'GET':
        scope = request.scope
        dropservice = Common_dropdown_ser(scope)
        resp_obj = dropservice.fetch_cd_details(id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        scope = request.scope
        dropservice = Common_dropdown_ser(scope)
        resp_obj = dropservice.delete_cd_details(id)
        return HttpResponse(resp_obj.get(), content_type='application/json')\

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_dropdown_details(request,id):
    if request.method == 'GET':
        scope = request.scope
        dropservice = Common_dropdown_ser(scope)
        resp_obj = dropservice.fetch_cd_details_header(id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def allowance_insert(request):
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page =NWisefinPage(page, 10)
        expense_name = request.GET.get('expensename', None)
        employee_grade = request.GET.get('employeegrade', None)
        city = request.GET.get('city', None)
        scope = request.scope
        Tour_service = Tour_allowance(scope)
        resp_obj = Tour_service.get_allowance(vys_page, expense_name, employee_grade, city)
        return HttpResponse(resp_obj.get(), content_type='application/json')

    elif request.method == 'POST':
        userdata = json.loads(request.body)
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        Tour_service = Tour_allowance(scope)
        resp_obj = Tour_service.insert_allowance(userdata,employee_id)
        response= HttpResponse(resp_obj.get(), content_type='application/json')
        return response
@csrf_exempt
@api_view(['DELETE','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def allowance_fetch(request,fetch_id):
    if request.method == 'DELETE':
        scope = request.scope
        Tour_service = Tour_allowance(scope)
        resp_obj = Tour_service.delete_allowance(fetch_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')

    if request.method == 'GET':
        scope = request.scope
        Tour_service = Tour_allowance(scope)
        resp_obj = Tour_service.get_allowance_id(fetch_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def allowance_get(request):
    if request.method == 'GET':
        scope = request.scope
        Tour_service = Tour_allowance(scope)
        expense= request.GET.get('expense')
        salarygrade= request.GET.get('salarygrade')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page =NWisefinPage(page, 10)
        resp_obj = Tour_service.allowance_get_grade(expense,salarygrade,vys_page)
        resp = json.dumps(resp_obj, default=lambda o: o.__dict__)
        return HttpResponse(resp, content_type='application/json')
@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def grade_insert(request):
    if request.method == 'GET':
        scope = request.scope
        Tour_service = Tour_grade(scope)
        resp_obj = Tour_service.get_grades()
        return HttpResponse(resp_obj.get(), content_type='application/json')

    elif request.method == 'POST':
        userdata = json.loads(request.body)
        scope = request.scope
        Tour_service = Tour_grade(scope)
        resp_obj = Tour_service.insert_grade(userdata)
        return HttpResponse(resp_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['DELETE','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def grade_fetch(request,fetch_id):
    if request.method == 'DELETE':
        scope = request.scope
        Tour_service =  Tour_grade(scope)
        resp_obj = Tour_service.delete_grades(fetch_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')

    if request.method == 'GET':
        scope = request.scope
        Tour_service = Tour_grade(scope)
        resp_obj = Tour_service.get_grade_id(fetch_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')

@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def approved_forward(request):
    try:
        if request.method == 'POST':
            # user_id = request.user.id
            scope = request.scope
            employee_id=request.employee_id
            userdata = json.loads(request.body)
            data=TourApprovedbyRequest(userdata)
            Tour_service = Tour_grade(scope)
            resp_obj = Tour_service.insert_forward(data,employee_id,request)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ approved_forward- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def approved_return(request):
    try:
        if request.method == "POST":
            # user_id = request.user.id
            scope = request.scope
            employee_id=request.employee_id
            userdata = json.loads(request.body)
            data = TourApprovedbyRequest(userdata)
            return_service = Tour_grade(scope)
            resp_obj = return_service.update_return(data,employee_id,request)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ approved_return- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def holiday_insert(request):
    if request.method == 'GET':
        scope = request.scope
        Tour_service = HolidayData(scope)
        from datetime import date
        todays_date = date.today().year
        date = request.GET.get('date',todays_date)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = Tour_service.get_holiday(vys_page,date)
        return HttpResponse(resp_obj.get(), content_type='application/json')
    elif request.method == 'POST':
        arr=[]
        tourdata = json.loads(request.body)
        scope = request.scope
        Tour_service = HolidayData(scope)
        # user_id = request.user.id
        employee_id=request.employee_id
        arr.append(tourdata)
        resp_obj = Tour_service.create_holiday(arr,employee_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def holiday_file(request):
    try:
        if request.method == 'POST':
            file_name = request.FILES.getlist('file')[0].name
            scope = request.scope
            budget_service = TourMaker(scope)
            employee_id = request.employee_id
            import pandas as pd
            import numpy as np
            excel_data = pd.read_excel(request.FILES['file'], engine='openpyxl')
            df = pd.DataFrame(excel_data)
            transation_obj = df.fillna(np.nan).replace([np.nan], [0]).to_dict(orient='records')
            resp_obj = budget_service.holiday_file(transation_obj, employee_id)
            response = HttpResponse(resp_obj.get(), content_type='application/json')
            return response
    except Exception as e:
        exc = traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ city_dropdown- ' + str(e) + str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['DELETE','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_holiday(request,fetch_id):
    if request.method == "DELETE" :
        scope = request.scope
        Tour_service = HolidayData(scope)
        resp_obj = Tour_service.delete_holiday(fetch_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')
    if request.method == 'GET':
        scope = request.scope
        Tour_service = HolidayData(scope)
        resp_obj = Tour_service.get_holiday_id(fetch_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['GET','POST',])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employeemapping_insert(request):
    if request.method == 'GET':
        scope = request.scope
        Tour_service = EmployeemappingData(scope)
        resp_obj = Tour_service.get_employeemapping()
        return HttpResponse(resp_obj.get(), content_type='application/json')
    elif request.method == 'POST':
        tourdata = json.loads(request.body)
        scope = request.scope
        Tour_service = EmployeemappingData(scope)
        resp_obj = Tour_service.create_employeemapping(tourdata)
        return HttpResponse(resp_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['DELETE','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_employeemapping(request,fetch_id):
    if request.method == "DELETE" :
        scope = request.scope
        Tour_service = EmployeemappingData(scope)
        resp_obj = Tour_service.delete_employeemapping(fetch_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')
    elif request.method == 'GET':
        scope = request.scope
        Tour_service = EmployeemappingData(scope)
        resp_obj = Tour_service.get_employeemapping_id(fetch_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employee_designation(request,designation):
    if request.method == 'GET':
        scope = request.scope
        Tour_service = EmployeemappingData(scope)
        resp_obj = Tour_service.get_emp_designation(designation)
        resp = json.dumps(resp_obj, default=lambda o: o.__dict__)
        return HttpResponse(resp, content_type='application/json')

@csrf_exempt
@transaction.atomic
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def holidaydeim(request):
    if request.method == 'GET':
        scope = request.scope
        hol_deimservice = HolidayDeim(scope)
        resp_obj = hol_deimservice.get_hol_deim()
        return HttpResponse(resp_obj.get(), content_type='application/json')
    elif request.method == 'POST':
        tourdata = json.loads(request.body)
        scope = request.scope
        hol_deimservice = HolidayDeim(scope)
        # user_id = request.user.id
        employee_id=request.employee_id
        resp_obj = hol_deimservice.insert_hol_deim(tourdata,employee_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_hol_deim(request,id):
    if request.method == 'GET':
        scope = request.scope
        hol_deimservice = HolidayDeim(scope)
        resp_obj = hol_deimservice.fetch_hol_deim(id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        scope = request.scope
        hol_deimservice = HolidayDeim(scope)
        resp_obj = hol_deimservice.deleteid(id)
        return HttpResponse(resp_obj.get(), content_type='application/json')
@csrf_exempt
@transaction.atomic
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def glmapping(request):
    if request.method == 'GET':
        scope = request.scope
        glservice = Glmap_ser(scope)
        resp_obj = glservice.get_glmapping()
        return HttpResponse(resp_obj.get(), content_type='application/json')
    elif request.method == 'POST':
        tourdata = json.loads(request.body)
        scope = request.scope
        glservice = Glmap_ser(scope)
        # user_id = request.user.id
        employee_id=request.employee_id
        resp_obj = glservice.insert_glmapping(tourdata,employee_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_glmapping(request,id):
    if request.method == 'GET':
        scope = request.scope
        glservice = Glmap_ser(scope)
        resp_obj = glservice.fetch_glmapping(id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        scope = request.scope
        glservice = Glmap_ser(scope)
        resp_obj = glservice.delete_glmapping(id)
        return HttpResponse(resp_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def expense_amount(request):
    try:
        if request.method == 'POST':
            userdata = json.loads(request.body)
            # user_id = request.user.id
            scope = request.scope
            employee_id=request.employee_id
            expense_id = request.GET.get('expense_id')
            tour_id = request.GET.get('tour_id')
            Tour_service = Tour_grade(scope)
            resp_obj = Tour_service.update_claimamount(userdata,employee_id,int(tour_id),int(expense_id))
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ expense_amount- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def app_amt_ccbs_update(request,tourid):
    try:
        if request.method == 'POST':
            # user_id = request.user.id
            scope = request.scope
            employee_id=request.employee_id
            Tour_service = Tour_grade(scope)
            resp_obj = Tour_service.app_amt_ccbs_update(tourid,employee_id)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ app_amt_ccbs_update- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def approvelist_insert(request):
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page =NWisefinPage(page, 10)
        approver = request.GET.get('query')
        scope = request.scope

        Tour_service = Approve_list(scope)
        resp_obj = Tour_service.get_approve(request,approver,vys_page)
        return HttpResponse(resp_obj.get(), content_type='application/json')

    elif request.method == 'POST':
        userdata = json.loads(request.body)
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        Tour_service = Approve_list(scope)
        resp_obj = Tour_service.insert_approve(userdata,employee_id)
        response= HttpResponse(resp_obj.get(), content_type='application/json')
        return response

@csrf_exempt
@api_view(['DELETE','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def approvelist_fetch(request,fetch_id):
    if request.method == 'DELETE':
        scope = request.scope
        Tour_service = Approve_list(scope)
        resp_obj = Tour_service.delete_approve(fetch_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')

    if request.method == 'GET':
        scope = request.scope
        Tour_service = Approve_list(scope)
        resp_obj = Tour_service.get_approve_byid(fetch_id, request)
        return HttpResponse(resp_obj.get(), content_type='application/json')

@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def tour_cancel(request):
    try:
        if request.method=='POST':
            tourdata = json.loads(request.body)
            scope = request.scope
            Tour_service = Canceltour(scope)
            # user_id = request.user.id
            employee_id=request.employee_id
            error_obj = NWisefinError()

            logger.info('ta_ Tour_cancel- ' + str(employee_id) + str(tourdata))
            scope = request.scope
            service = Validation(scope)
            permission = service.permisssion_check_type(tourdata["tour_id"], employee_id, App_type.TOUR,
                                                        App_level.ZERO_LEVEL)
            if permission is False:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.VALID_USER)
                return HttpResponse(error_obj.get(), content_type='application/json')
            # approver_permission = service.permisssion_check_type(tourdata["tour_id"], int(tourdata["approval"]),
            #                                                      App_type.TOUR, App_level.ZERO_LEVEL)
            # if approver_permission is True:
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.VALID_USER)
            #     return HttpResponse(error_obj.get(), content_type='application/json')
            # if int(tourdata["approval"])==0:
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.APPROVER)
            #     return HttpResponse(error_obj.get(), content_type='application/json')
            # scope = request.scope
            # validation_service = Validation(scope)
            # if tourdata["apptype"].lower()=="tourcancel":
            #     checker_type="tour"
            # else:
            #     checker_type="advance"
            # approver_check = validation_service.approver_validation(checker_type, int(tourdata["approval"]), request)
            # if approver_check is False:
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.APPROVER_NOT_IN_LIST)
            #     return HttpResponse(error_obj.get(), content_type='application/json')
            object= TourCancelreq(tourdata)
            resp_obj = Tour_service.cancel_tour(object, employee_id,request)
            return HttpResponse(resp_obj.get(), content_type='application/json')

    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ tour_cancel- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

# @csrf_exempt
# @api_view(['POST'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def advance_updamt(request):
#     try:
#         if request.method=='POST':
#             userdata = json.loads(request.body)
#             scope = request.scope
#             Advance_service = TourAdvance(scope)
#             # user_id = request.user.id
#             employee_id=request.employee_id
#
#             resp_obj = Advance_service.update_adv_amount(userdata,employee_id)
#             return HttpResponse(resp_obj.get(), content_type='application/json')
#     except Exception as e:
#         exc=traceback.format_exc()
#         error_obj = NWisefinError()
#         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#         error_obj.set_description(str(e))
#         logger.info('ta_ advance_updamt- ' + str(e)+str(exc))
#         return HttpResponse(error_obj.get(), content_type='application/json')


@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def tour_reject(request):
    try:
        if request.method == 'POST':
            tourdata = json.loads(request.body)
            scope = request.scope
            Tour_service = TourApprovedby(scope)
            # user_id = request.user.id
            employee_id=request.employee_id
            resp_obj = Tour_service.insert_reject(tourdata,employee_id,request)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ tour_reject- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def approvetype(request):
    if request.method == 'POST':
        userdata = json.loads(request.body)
        scope = request.scope
        Tour_service = Approve_list(scope)
        resp_obj = Tour_service.approve_filterby_type(userdata,request)
        resp=json.dumps(resp_obj, default=lambda o: o.__dict__)
        return HttpResponse(resp, content_type='application/json')


@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def onbehalfof_insert(request):
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page =NWisefinPage(page, 10)
        scope = request.scope
        Tour_service = Onbehalf_service(scope)
        resp_obj = Tour_service.get_onbehalfof(vys_page,request)
        return HttpResponse(resp_obj.get(), content_type='application/json')

    elif request.method == 'POST':
        userdata = json.loads(request.body)
        # user_id = request.user.id
        employee_id=request.employee_id
        scope = request.scope
        Tour_service = Onbehalf_service(scope)
        resp_obj = Tour_service.insert_onbehalfof(userdata,employee_id)
        response= HttpResponse(resp_obj.get(), content_type='application/json')
        return response

@csrf_exempt
@api_view(['DELETE','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def onbehalfof_fetch(request,fetch_id):
    if request.method == 'DELETE':
        scope = request.scope
        Tour_service = Onbehalf_service(scope)
        resp_obj = Tour_service.delete_onbehalfof(fetch_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')

    if request.method == 'GET':
        scope = request.scope
        Tour_service = Onbehalf_service(scope)
        resp_obj = Tour_service.get_onbehalfof_byid(fetch_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def onbehalfof_status(request):
    if request.method == "POST":
        data = json.loads(request.body)
        id=data['id']
        status=data['status']
        scope = request.scope
        status_ser=Onbehalf_service(scope)
        status_service=status_ser.update_status(id,status)
        return HttpResponse(status_service.get(),content_type='application/json')




@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def onbehalf_present(request):

    if request.method == 'POST':
        userdata = json.loads(request.body)
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        Tour_service = Onbehalf_service(scope)
        resp_obj = Tour_service.onbehalf_ifpresent(userdata,employee_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')\

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def onbehalf_notpresent(request):
    if request.method == 'POST':
        userdata = json.loads(request.body)
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        Tour_service = Onbehalf_service(scope)
        resp_obj = Tour_service.onbehalf_ifnotpresent(userdata,employee_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def update_approvedby(request):
    if request.method == 'POST':
        userdata = json.loads(request.body)
        scope = request.scope
        Tour_service = Onbehalf_service(scope)
        resp_obj = Tour_service.update_approvedby(userdata)
        return HttpResponse(resp_obj, content_type='application/json')


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def onbehalf_emp_get(request):
    if request.method == 'GET':
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        Tour_service = Onbehalf_service(scope)
        resp_obj = Tour_service.onbehalf_emp_get(employee_id,request)
        return HttpResponse(resp_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def nac_onbehalf_emp_get(request):
    if request.method == 'GET':
        scope = request.scope
        # user_id = request.user.id
        employee_id=request.employee_id
        query = request.GET.get('query')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        # emp = Employee.objects.get(user_id=user_id)
        # employee_id = emp.id
        Tour_service = Onbehalf_service(scope)
        resp_obj = Tour_service.nac_onbehalf_emp_get(employee_id,request,query,vys_page)
        # resp=json.dumps(resp_obj, default=lambda o: o.__dict__)
        return HttpResponse(resp_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def nac_onbehalf_emp_get_check(request):
    if request.method == 'GET':
        scope = request.scope
        # user_id = request.user.id
        employee_id=request.employee_id
        query = request.GET.get('query')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        Tour_service = Onbehalf_service(scope)
        resp_obj = Tour_service.nac_onbehalf_emp_get_check(employee_id,request,query,vys_page)
        return HttpResponse(resp_obj, content_type='application/json')


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def onbehalf_emp_get_branch(request,branch):
    if request.method == 'GET':
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        query = request.GET.get('query')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page =NWisefinPage(page, 10)
        Tour_service = Onbehalf_service(scope)
        resp_obj = Tour_service.onbehalf_emp_get_branch(employee_id,branch,request,query,vys_page)
        resp=json.dumps(resp_obj, default=lambda o: o.__dict__)
        return HttpResponse(resp, content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def report_tour_summary(request):
    try:
        if request.method == 'GET':
            tourno= request.GET.get('tourno')
            empid= request.GET.get('empid')
            from_date= request.GET.get('from_date')
            to_date= request.GET.get('to_date')
            month= request.GET.get('month')

            page = request.GET.get('page', 1)
            page = int(page)
            vys_page =NWisefinPage(page, 10)
            scope = request.scope
            service = Report_ser(scope)
            resp_obj = service.get_tour_report(tourno,empid,from_date,to_date,month,request,vys_page)
            resp=json.dumps(resp_obj, default=lambda o: o.__dict__)
            response = HttpResponse(resp, content_type="application/json")
            return response
    except Exception as e:
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        return HttpResponse(error_obj.get(), content_type='application/json')

# @csrf_exempt
# @api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def nac_report(request):
#     try:
#         if request.method == 'GET':
#             type= request.GET.get('type')
#             view= request.GET.get('view',1)
#             tourno= request.GET.get('tourno')
#             empid= request.GET.get('empid')
#             from_date= request.GET.get('from_date')
#             to_date= request.GET.get('to_date')
#             month= request.GET.get('month')
#             page = request.GET.get('page', 1)
#             page = int(page)
#             vys_page =NWisefinPage(page, 10)
#             scope = request.scope
#             service = Report_ser(scope)
#             if (type).upper()==App_type.TOUR and int(view)==1:
#                 resp_obj = service.tour_report_view(tourno,empid,from_date,to_date,month,request,vys_page)
#             # if (type).upper()==App_type.TOUR and int(view)==0:
#             #     resp_obj = service.tour_report_download(tourno,empid,from_date,to_date,month,request,vys_page)
#             if (type).upper()==App_type.CLAIM and int(view)==1:
#                 resp_obj = service.claim_report_view(tourno,empid,from_date,to_date,month,request,vys_page)
#             if (type).upper()==App_type.CLAIM and int(view)==0:
#                 resp_obj = service.claim_report_download(tourno,empid,from_date,to_date,month,request,vys_page)
#                 return resp_obj
#             # resp=json.dumps(resp_obj, default=lambda o: o.__dict__)
#             response = HttpResponse(resp_obj.get(), content_type="application/json")
#             return response
#     except Exception as e:
#         error_obj = NWisefinError()
#         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#         error_obj.set_description(str(e))
#         return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def nac_report(request):
    try:
        if request.method == 'GET':
            type= request.GET.get('type')
            view= request.GET.get('view',1)
            tourno= request.GET.get('tour_no')
            request_date= request.GET.get('request_date')
            empid= request.GET.get('empid')
            from_date= request.GET.get('start_date')
            to_date= request.GET.get('end_date')
            page = request.GET.get('page', 1)
            page = int(page)
            vys_page =NWisefinPage(page, 10)
            scope = request.scope
            service = Report_ser(scope)
            Tour_service = TourMaker(scope)
            if (type).upper()==App_type.TRAVEL and int(view)==1:
                resp_obj = Tour_service.all_tour_report(empid,vys_page,request_date,tourno,request,from_date,to_date)
            elif (type).upper()==App_type.TRAVEL and int(view)==0:
                resp_obj = Tour_service.all_tour_report_download( empid, None, request_date, tourno, request,from_date,to_date)
                return resp_obj
            elif (type).upper()==App_type.CLAIM and int(view)==1:
                resp_obj = service.claim_report_view(tourno,empid,from_date,to_date,request,vys_page)
            elif (type).upper()==App_type.CLAIM and int(view)==0:
                resp_obj = service.claim_report_download(tourno,empid,from_date,to_date)
                return resp_obj
            elif (type).upper()==(App_type.REQUIRMENTS).upper() and int(view)==1:
                booking_type = request.GET.get('booking_type')
                all_report = request.GET.get('all_report')
                resp_obj = service.report_tour_requirements(request,tourno,vys_page,all_report,booking_type,from_date,to_date,empid)
            elif (type).upper()==(App_type.REQUIRMENTS).upper() and int(view)==0:
                booking_type = request.GET.get('booking_type')
                all_report = request.GET.get('all_report')
                resp_obj = service.report_requirement_download(request,tourno,vys_page,all_report,booking_type,from_date,to_date,empid)
                return resp_obj

            # resp=json.dumps(resp_obj, default=lambda o: o.__dict__)
            response = HttpResponse(resp_obj.get(), content_type="application/json")
            return response
    except Exception as e:
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        exc = traceback.format_exc()
        print(exc)
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def report_tourid_summary(request,tourid):
    try:
        if request.method == 'GET':
            scope = request.scope
            service = Report_ser(scope)
            # user_id = request.user.id
            employee_id=request.employee_id
            page = request.GET.get('page', 1)
            page = int(page)
            vys_page =NWisefinPage(page, 10)
            resp_obj = service.get_tourid_report(tourid,employee_id,request,vys_page)
            resp=json.dumps(resp_obj, default=lambda o: o.__dict__)
            response = HttpResponse(resp, content_type="application/json")
            return response
    except Exception as e:
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def report_download_tour_summary(request):
    try:
        if request.method == 'GET':
            all_report= request.GET.get('all_report')
            tourno= request.GET.get('tourno')
            empid= request.GET.get('empid')
            scope = request.scope
            service = Report_ser(scope)
            page = request.GET.get('page', 1)
            from_date = request.GET.get('from_date')
            to_date = request.GET.get('to_date')
            month = request.GET.get('month')
            page = int(page)
            vys_page =NWisefinPage(page, 10)

            resp_obj = service.get_tour_report_download(tourno,empid,from_date,to_date,month,request,vys_page,all_report)
            return resp_obj
    except Exception as e:
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def report_download_tourid(request,tourid):
    try:
        if request.method == 'GET':
            scope = request.scope
            service = Report_ser(scope)
            # user_id = request.user.id

            employee_id=request.employee_id
            all_report = request.GET.get('all_report')
            page = request.GET.get('page', 1)
            page = int(page)
            vys_page =NWisefinPage(page, 10)
            resp_obj = service.get_tourid_download(tourid,employee_id,request,vys_page,all_report)
            return resp_obj
    except Exception as e:
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def report_tour_detail(request,tourno):
    try:
        if request.method == 'GET':
            scope = request.scope
            service = Report_ser(scope)
            resp_obj = service.get_tour_detail(tourno,request)
            resp=json.dumps(resp_obj, default=lambda o: o.__dict__)
            response = HttpResponse(resp, content_type="application/json")
            return response
    except Exception as e:
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def report_download_tour_detail(request,tourno):
    try:
        if request.method == 'GET':
            scope = request.scope
            service = Report_ser(scope)
            resp_obj = service.get_tour_detail_download(tourno,request)
            return resp_obj
    except Exception as e:
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def report_tour_advance(request,tourno):
    try:
        if request.method == 'GET':
            scope = request.scope
            service = Report_ser(scope)
            resp_obj = service.get_tour_advance(tourno)
            resp=json.dumps(resp_obj, default=lambda o: o.__dict__)
            response = HttpResponse(resp, content_type="application/json")
            return response
    except Exception as e:
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def download_tour_advance(request,tourno):
    try:
        if request.method == 'GET':
            scope = request.scope
            service = Report_ser(scope)
            resp_obj = service.get_download_tour_advance(tourno)
            return resp_obj
    except Exception as e:
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def report_download_tour_expense(request,tourno):
    try:
        if request.method == 'GET':
            scope = request.scope
            service = Report_ser(scope)
            resp_obj = service.get_download_tour_expense(tourno,request)
            return resp_obj
    except Exception as e:
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def consolidate_report(request,tourno):
    try:
        if request.method == 'GET':
            scope = request.scope
            service = Report_ser(scope)
            resp_obj = service.consolidate_report(tourno,request)
            resp=json.dumps(resp_obj, default=lambda o: o.__dict__)
            response = HttpResponse(resp, content_type="application/json")
            return response

    except Exception as e:
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def branchwise_pending(request,empgid):
    try:
        if request.method == 'GET':
            page = request.GET.get('page', 1)
            page = int(page)
            vys_page =NWisefinPage(page, 10)
            all_report = request.GET.get('all_report')
            scope = request.scope
            service = Report_ser(scope)
            resp_obj = service.branchwise_pending(empgid,request,vys_page)
            resp=json.dumps(resp_obj, default=lambda o: o.__dict__)
            response = HttpResponse(resp, content_type="application/json")
            return response
    except Exception as e:
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def report_tour_requirements(request):
    try:
        if request.method == 'GET':
            page = request.GET.get('page', 1)
            tour_id= request.GET.get('tour_id')
            request_date= request.GET.get('request_date')
            page = int(page)
            vys_page =NWisefinPage(page, 10)
            scope = request.scope
            service = Report_ser(scope)
            tour_id = request.GET.get('tour_no')
            booking_type = request.GET.get('booking_type')
            from_date = request.GET.get('start_date')
            to_date = request.GET.get('end_date')
            emp_id= request.GET.get('emp_id')

            all_report = request.GET.get('all_report')
            resp_obj = service.report_tour_requirements(request, tour_id, vys_page, all_report,booking_type,from_date,to_date,emp_id)
            resp=json.dumps(resp_obj, default=lambda o: o.__dict__)
            response = HttpResponse(resp, content_type="application/json")
            return response
    except Exception as e:
        exc = traceback.format_exc()
        print(exc)
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ report_summary- ' + str(e) + str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def report_requirements_download(request):
    try:
        if request.method == 'GET':

            tour_id= request.GET.get('tour_id')
            booking_type= request.GET.get('booking_type')
            page = request.GET.get('page', 1)
            page = int(page)
            vys_page =NWisefinPage(page, 10)
            scope = request.scope
            service = Report_ser(scope)
            tour_id = request.GET.get('tour_no')
            booking_type = int(request.GET.get('booking_type'))
            from_date = request.GET.get('start_date')
            to_date = request.GET.get('end_date')
            emp_id = request.GET.get('emp_id')

            all_report = request.GET.get('all_report')
            resp_obj = service.report_requirement_download(request,tour_id,vys_page,all_report,booking_type,from_date,to_date,emp_id)
            # resp=json.dumps(resp_obj, default=lambda o: o.__dict__)
            response = HttpResponse(resp_obj, content_type="application/json")
            return response
    except Exception as e:
        exc = traceback.format_exc()
        print(exc)
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ report_download- ' + str(e) + str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@transaction.atomic
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def date_relaxation(request):
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page =NWisefinPage(page, 10)
        tour_no = request.GET.get('tour_no', None)
        scope = request.scope
        service = Date_relaxation_ser(scope)
        resp_obj = service.get_date_relaxation(request,tour_no,vys_page)
        return HttpResponse(resp_obj.get(), content_type='application/json')

    elif request.method == 'POST':
        data = json.loads(request.body)
        scope = request.scope
        service = Date_relaxation_ser(scope)
        # user_id = request.user.id
        employee_id=request.employee_id
        resp_obj = service.update_date_relaxation(data,employee_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')

@csrf_exempt
@transaction.atomic
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def approve_international_travel(request):
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page =NWisefinPage(page, 10)
        tour_no = request.GET.get('tour_no', None)
        scope = request.scope
        service = Date_relaxation_ser(scope)
        resp_obj = service.get_international_travel(request,tour_no,vys_page)
        return HttpResponse(resp_obj.get(), content_type='application/json')

    elif request.method == 'POST':
        data = json.loads(request.body)
        scope = request.scope
        service = Date_relaxation_ser(scope)
        # user_id = request.user.id
        employee_id=request.employee_id
        resp_obj = service.approve_international_travel(data,employee_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')

@csrf_exempt
@transaction.atomic
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def insure_international_travel(request):
    # if request.method == 'GET':
    #     page = request.GET.get('page', 1)
    #     page = int(page)
    #     vys_page =NWisefinPage(page, 10)
    #     tour_no = request.GET.get('tour_no', None)
    #     scope = request.scope
    #     service = Date_relaxation_ser(scope)
    #     resp_obj = service.get_date_relaxation(request,tour_no,vys_page)
    #     return HttpResponse(resp_obj.get(), content_type='application/json')

    if request.method == 'POST':
        data = json.loads(request.body)
        scope = request.scope
        service = Date_relaxation_ser(scope)
        # user_id = request.user.id
        employee_id=request.employee_id
        resp_obj = service.insure_international_travel(data,employee_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def date_relaxation_fetch(request,id):
    if request.method == 'GET':
        scope = request.scope
        service = Date_relaxation_ser(scope)
        resp_obj = service.fetch_date_relaxation(id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def branch_approver_get(request,type,branch):
    try:
        if request.method == 'GET':
            # user_id = request.user.id
            scope = request.scope
            employee_id=request.employee_id
            maker = request.GET.get('maker', employee_id)
            tourid = request.GET.get('tourid')
            onbehalfof = request.GET.get('onbehalfof',0)
            approver_except=[int(maker),int(onbehalfof)]
            approver= request.GET.get('name')
            if approver is not None:
                approver=approver.lower()
            tour_service = Branch_emp_ser(scope)
            resp_obj = tour_service.branch_approver_get(type,branch,approver,approver_except, request, tourid)
            resp=json.dumps(resp_obj, default=lambda o: o.__dict__)
            return HttpResponse(resp, content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ branch_approver_get- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_documents(request, refid):
    try:
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        if request.method =='GET':
            scope = request.scope
            service=Validation(scope)
            permission = service.permisssion_check(refid, employee_id)
            if permission is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.VALID_USER)
                return HttpResponse(error_obj.get(), content_type='application/json')
            scope = request.scope
            document_service = TourMaker(scope)
            type=request.GET.get("type",0)
            resp_obj = document_service.fetch_documents(refid,int(type))
            resp=json.dumps(resp_obj, default=lambda o: o.__dict__)
            return HttpResponse(resp, content_type='application/json')
        if request.method=='DELETE':
            scope = request.scope
            document_service = TourMaker(scope)
            resp_obj = document_service.delete_document(refid,employee_id)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ fetch_documents- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def download_attachment(request, file_id):
    try:
        contentType = request.GET.get('type', None)
        scope = request.scope

        service = Date_relaxation_ser(scope)
        doc_obj = service.get_file_id(file_id)


        tour_id = doc_obj.request_id
        # user_id = request.user.id
        employee_id=request.employee_id
        service = Validation(scope)
        permission = service.permisssion_check(tour_id, employee_id)
        if permission is False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.VALID_USER)
            return HttpResponse(error_obj.get(), content_type='application/json')

        file_name = doc_obj.file_name
        gen_file_name = doc_obj.gen_file_name
        if doc_obj.ref_type != 3:
            s3 = boto3.resource('s3')
            s3_obj = s3.Object(bucket_name=settings.BUCKET_NAME_FOR_ASSETS, key=gen_file_name)
            body = s3_obj.get()['Body']
        else:
            scope = request.scope
            api_service = ApiService(scope)
            token = "Bearer  " + api_service.get_authtoken(request)
            headers_ = {"content-type": "application/json", "Authorization": "" + token + ""}
            file_path=gen_file_name
            resp_ = requests.get("" + val_url + "ppr_file_downloader/?filename=" + file_path, headers=headers_,
                                 verify=False)
            inmemory_content = io.BytesIO(resp_.content)
            body=inmemory_content
        if contentType == 'pdf' or contentType == 'PDF':
            response = HttpResponse(body, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="{}"'.format(file_name)
        elif contentType == 'JPEG' or contentType == 'jpeg' or contentType == 'jpg' or contentType == 'JPG':
            response = HttpResponse(body, content_type='image/jpeg')
            response['Content-Disposition'] = 'inline; filename="{}"'.format(file_name)
        elif contentType == 'png' or contentType == 'PNG':
            response = HttpResponse(body, content_type='image/png')
            response['Content-Disposition'] = 'inline; filename="{}"'.format(file_name)
        else:
            response = StreamingHttpResponse(body, content_type='application/octet-stream')
            response['Content-Disposition'] = 'inline; filename="{}"'.format(file_name)
        return response

    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ download_attachment- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

# @csrf_exempt
# @api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def requirement_file(request, file_id):
#     try:
#         if request.method=="GET":
#             contentType = request.GET.get('type', None)
#             scope = request.scope
#
#             service = Date_relaxation_ser(scope)
#             doc_obj = service.get_file_id(file_id)
#
#
#             tour_id = doc_obj.request_id
#             # user_id = request.user.id
#             employee_id=request.employee_id
#             service = Validation(scope)
#             permission = service.permisssion_check(tour_id, employee_id)
#             if permission is False:
#                 error_obj = NWisefinError()
#                 error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#                 error_obj.set_description(ErrorDescription.VALID_USER)
#                 return HttpResponse(error_obj.get(), content_type='application/json')
#
#             file_name = doc_obj.file_name
#             gen_file_name = doc_obj.gen_file_name
#             # if doc_obj.ref_type != 3:
#             s3 = boto3.resource('s3')
#             s3_obj = s3.Object(bucket_name=settings.BUCKET_NAME_FOR_ASSETS, key=gen_file_name)
#             body = s3_obj.get()['Body']
#             # else:
#             # scope = request.scope
#             # api_service = ApiService(scope)
#             # token = "Bearer  " + api_service.get_authtoken(request)
#             # headers_ = {"content-type": "application/json", "Authorization": "" + token + ""}
#             # file_path=gen_file_name
#             # resp_ = requests.get("" + val_url + "ppr_file_downloader/?filename=" + file_path, headers=headers_,
#             #                      verify=False)
#             # inmemory_content = io.BytesIO(resp_.content)
#             # body=inmemory_content
#             if contentType == 'pdf' or contentType == 'PDF':
#                 response = HttpResponse(body, content_type='application/pdf')
#                 response['Content-Disposition'] = 'inline; filename="{}"'.format(file_name)
#             elif contentType == 'JPEG' or contentType == 'jpeg' or contentType == 'jpg' or contentType == 'JPG':
#                 response = HttpResponse(body, content_type='image/jpeg')
#                 response['Content-Disposition'] = 'inline; filename="{}"'.format(file_name)
#             elif contentType == 'png' or contentType == 'PNG':
#                 response = HttpResponse(body, content_type='image/png')
#                 response['Content-Disposition'] = 'inline; filename="{}"'.format(file_name)
#             else:
#                 response = StreamingHttpResponse(body, content_type='application/octet-stream')
#                 response['Content-Disposition'] = 'inline; filename="{}"'.format(file_name)
#             return response
#         if request.method=="POST":
#             try:
#                 for i in request.FILES.getlist('file'):
#                     file_name = i.name
#                     extension = file_name.split('.')[-1]
#                     scope = request.scope
#                     file_validation = Validation(scope)
#                     filetype_check = file_validation.fileexe_validation(extension)
#                     if filetype_check is False:
#                         error_obj = NWisefinError()
#                         error_obj.set_code(ErrorMessage.INVALID_FILETYPE)
#                         error_obj.set_description(ErrorDescription.SUPPORTED_FILE_TYPES)
#                         response = HttpResponse(error_obj.get(), content_type='application/json')
#                         return HttpResponse(response, content_type='application/json')
#             except KeyError:
#                 pass
#             try:
#                 error_obj = NWisefinError()
#                 # expensedata = json.loads(request.data.dict().get('data'))
#                 # user_id = request.user.id
#                 scope = request.scope
#                 employee_id = request.employee_id
#                 # logger.info('ta_ Expense_submit- ' + str(employee_id) + str(expensedata))
#                 # if int(expensedata['approvedby']) == employee_id or int(expensedata['approvedby']) == 0:
#                 #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#                 #     error_obj.set_description(ErrorDescription.MAKER_APPROVER_SAME)
#                 #     return HttpResponse(error_obj.get(), content_type='application/json')
#                 # valid_service = Validation(scope)
#                 # approver_check = valid_service.approver_validation(App_type.expense, int(expensedata['approvedby']),
#                 #                                                    request)
#                 # if approver_check is False:
#                 #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#                 #     error_obj.set_description(ErrorDescription.APPROVER_NOT_IN_LIST)
#                 #     return HttpResponse(error_obj.get(), content_type='application/json')
#                 # exp_maker_check = valid_service.tour_maker_check(expensedata['tourgid'], employee_id)
#                 # if exp_maker_check is False:
#                 #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#                 #     error_obj.set_description(ErrorDescription.VALID_USER)
#                 #     return HttpResponse(error_obj.get(), content_type='application/json')
#                 # scope = request.scope
#                 # service = Date_relaxation_ser(scope)
#                 #
#                 # service_moveto_vali = service.expense_movetoapprover_vali(request, expensedata)
#                 # if service_moveto_vali != None:
#                 #     if service_moveto_vali.code == 'UNEXPECTED_ERROR':
#                 #         error_obj = NWisefinError()
#                 #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#                 #         error_obj.set_description(ErrorDescription.INVALID)
#                 #         return HttpResponse(error_obj.get(), content_type='application/json')
#                 # date_relaxation = service.fetch_date_relaxation_get(expensedata['tourgid'])
#                 # if date_relaxation is not True:
#                 #     return HttpResponse(date_relaxation.get(), content_type='application/json')
#                 # scope = request.scope
#                 # expense_service = TourApprovedby(scope)
#                 # resp_obj = expense_service.expense_submit(expensedata, employee_id, request)
#                 # if isinstance(resp_obj, NWisefinError):
#                 #     return HttpResponse(resp_obj.get(), content_type='application/json')
#                 # if resp_obj.status == 'success':
#                 #     scope = request.scope
#                 #     tourservice = TourMaker(scope)
#                 #     resp_obj = tourservice.update_claim_status(expensedata['tourgid'])
#
#                 # tour_id = expensedata['tourgid']
#                 requirement_id=0
#                 vysfinservice = ApiService(scope)
#                 if len(request.FILES) != 0:
#                     docmodule_obj = DocModule()
#                     params = {}
#                     params['module'] = docmodule_obj.TA
#                     params['ref_id'] = requirement_id
#                     params['ref_type'] = docmodule_obj.TA
#                     doc_module = docmodule_obj.TA
#                     response_obj = vysfinservice.doc_upload(request, doc_module, requirement_id)
#                     for doc_data in response_obj['data']:
#                         ta_doc = TADocuments()
#                         ta_doc.file_id = doc_data['id']
#                         ta_doc.ref_id = requirement_id
#                         ta_doc.request_id = requirement_id
#                         ta_doc.ref_type = TADocUtil.TICKET
#                         ta_doc.file_name = doc_data['file_name']
#                         ta_doc.gen_file_name = doc_data['gen_file_name']
#                         ta_doc.created_by = employee_id
#                         ta_doc.save()
#                     success_obj = NWisefinSuccess()
#                     success_obj.set_status(SuccessStatus.SUCCESS)
#                     success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
#                     return HttpResponse(success_obj.get(), content_type='application/json')
#                 else:
#                     error_obj = NWisefinError()
#                     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#                     error_obj.set_description(ErrorDescription.NO_FILE)
#                     # logger.info('ta_ expense_movetoapprover- ' + str(e))
#                     return HttpResponse(error_obj.get(), content_type='application/json')
#             except Exception as e:
#                 transaction.set_rollback(True)
#                 error_obj = NWisefinError()
#                 error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#                 error_obj.set_description(str(e))
#                 # logger.info('ta_ expense_movetoapprover- ' + str(e))
#                 return HttpResponse(error_obj.get(), content_type='app'
#                                                                   'lication/json')
#
#
#     except Exception as e:
#         error_obj = NWisefinError()
#         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#         error_obj.set_description(str(e))
#         logger.info('ta_ download_attachment- ' + str(e))
#         return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def tour_status_get(request):
    if request.method == 'GET':
        scope = request.scope
        service = TourMaker(scope)
        # user_id = request.user.id
        employee_id=request.employee_id
        type= request.GET.get('type')
        get_status= request.GET.get('status')
        resp_obj = service.tour_status(employee_id,type,get_status,request)
        resp=json.dumps(resp_obj, default=lambda o: o.__dict__)
        response = HttpResponse(resp, content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def expense_summary(request):
    try:
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page =NWisefinPage(page, 10)
        scope = request.scope
        Tour_service = TourExpense(scope)
        # user_id = request.user.id

        employee_id=request.employee_id
        onb = request.GET.get('onbehalf')
        status = request.GET.get('status')
        request_date = request.GET.get('request_date','')
        tour_no = request.GET.get('tour_no','')
        resp_obj = Tour_service.exp_summary(employee_id,onb,vys_page,request_date,tour_no,request,status)
        return HttpResponse(resp_obj.get(), content_type='application/json')

    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ expense_summary- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def approved_data(request):
    try:
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page =NWisefinPage(page, 10)
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        onb = request.GET.get('onbehalf', 0)
        request_date = request.GET.get('request_date','')
        tour_no = request.GET.get('tour_no','')
        type = (request.GET.get('type')).upper()
        if type==App_type.TOUR:
            scope = request.scope
            service=TourExpense(scope)
            data=service.approved_tour_cancel_summary(employee_id,onb,vys_page,request_date,tour_no,request)
        # elif type==App_type.ADVANCE:
        #     scope = request.scope
        #     service = TourApprovedby(scope)
        #     data = service.adv_summary(employee_id, onb,vys_page,request_date,tour_no,request)
        return HttpResponse(data.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ approved_data- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def cancelled_data(request):
    try:
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page =NWisefinPage(page, 10)
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        onb = request.GET.get('onbehalf', 0)
        type = request.GET.get('type')
        request_date = request.GET.get('request_date','')
        tour_no = request.GET.get('tour_no','')
        scope = request.scope
        service=Canceltour(scope)
        data = service.cancelled_data(type,employee_id, onb,vys_page,request_date,tour_no,request)
        return HttpResponse(data.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ cancelled_data- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def tourapprovedby_table(request):
    scope = request.scope
    service=TourApprovedby(scope)
    data = service.tourapprovedby_table()
    return HttpResponse(data.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ccbs_get(request):
    try:
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        scope = request.scope
        service = Validation(scope)

        if request.method=="GET":
            tour = request.GET.get('tour')
            module_permission = ApiService(scope)
            role_arr = module_permission.employee_modulerole_get(employee_id, ModuleList.Ta_eclaim, request)
            ceo_get = module_permission.onb_permission(request, employee_id)
            if RoleList.admin not in role_arr and (json.loads(ceo_get))["ceo"] != True:
                # permission = service.permisssion_check(tourid, employee_id)
                if RoleList.admin not in role_arr and RoleList.checker not in role_arr:
                    permission = service.permisssion_check(tour, employee_id)
                    if permission is False:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        error_obj.set_description(ErrorDescription.VALID_USER)
                        return HttpResponse(error_obj.get(), content_type='application/json')
            type = request.GET.get('type')
            scope = request.scope
            service=Common_dropdown_ser(scope)
            data = service.ccbs_get(tour,type,request,0)
            resp=json.dumps(data, default=lambda o: o.__dict__)
            return HttpResponse(resp, content_type='application/json')
        if request.method=='DELETE':
            id = request.GET.get('id')
            scope = request.scope
            service = Common_dropdown_ser(scope)
            resp_obj = service.delete_ccbs(id,employee_id)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ ccbs_get- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@transaction.atomic
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ccbs_update(request):
    try:
        userdata = json.loads(request.body)
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        logger.info('ta_ Ccbs_update- '+str(employee_id)+str(userdata))
        scope = request.scope
        service = Validation(scope)
        permission = service.tour_maker_check(userdata[0]['tourgid'], employee_id)
        if permission is False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.VALID_USER)
            return HttpResponse(error_obj.get(), content_type='application/json')
        type = request.GET.get('type',2)
        req_id = request.GET.get('req_id',0)
        scope = request.scope
        service=Onbehalf_service(scope)
        scope = request.scope
        val_service=Validation(scope)
        tourgid=userdata[0]['tourgid']
        scope = request.scope
        service = Date_relaxation_ser(scope)
        ccbs_update_vali = service.ccbs_vali_con(tourgid,userdata)
        if ccbs_update_vali !=None:
            if ccbs_update_vali.code == 'UNEXPECTED_ERROR':
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID)
                return HttpResponse(error_obj.get(), content_type='application/json')

        scope = request.scope
        service = Onbehalf_service(scope)

        resp = service.insert_Ccbs(userdata,employee_id,req_id,type)
        return HttpResponse(resp.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ ccbs_update- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def tourno_grade_get(request,tourid):
    try:
        if request.method=='GET':
            scope = request.scope
            service=Tourno_details(scope)
            data = service.requestno_get(tourid,request)
            return HttpResponse(data.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ tourno_grade_get- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def approval_flow_get(request):
    try:
        if request.method=='GET':
            report = request.GET.get('report', 0)
            tourid = request.GET.get('tourid')
            type = request.GET.get('type')
            # user_id = request.user.id
            scope = request.scope
            employee_id=request.employee_id
            service = Validation(scope)
            module_permission = ApiService(scope)
            role_arr = module_permission.employee_modulerole_get(employee_id, ModuleList.Ta_eclaim, request)
            ceo_get = module_permission.onb_permission(request, employee_id)
            if RoleList.admin not in role_arr and (json.loads(ceo_get))["ceo"] != True:
                if RoleList.admin not in role_arr and RoleList.checker not in role_arr:
                    permission = service.permisssion_check(tourid, employee_id)
                    if permission is False and int(report)!=1:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        error_obj.set_description(ErrorDescription.VALID_USER)
                        return HttpResponse(error_obj.get(), content_type='application/json')
            scope = request.scope
            service=TourApprovedby(scope)
            data = service.approval_flow_get(tourid,type,request)
            return HttpResponse(data.get(), content_type='application/json')

    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ approval_flow_get- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def effective_date(request):
    if request.method=='POST':
        data= json.loads(request.body)
        scope = request.scope
        service=El_lod_ser(scope)
        data = service.elig_citytoamount_effectivedate(data,"S3",request)
        return HttpResponse(data, content_type='application/json')

@transaction.atomic
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ecf_entry(request):
    if request.method=='POST':
        data= json.loads(request.body)
        jsondata=Ecf_req(data)
        scope = request.scope
        service=Ecf_entry(scope)
        data = service.invoice_entry(jsondata,request,"empl74","empl75",1)
        resp=json.dumps(data, default=lambda o: o.__dict__)
        return HttpResponse(resp, content_type='application/json')

# @transaction.atomic
# @api_view(['POST'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def all_booking_get(request):
#     try:
#         if request.method=='POST':
#             tour_id=request.GET.get("tour_id")
#             admin_paid=request.GET.get("admin_paid",1)
#             scope = request.scope
#             service=Ecf_entry(scope)
#             data = service.all_booking_get_ecf(int(tour_id),request,0,int(admin_paid))
#             resp=json.dumps(data, default=lambda o: o.__dict__)
#             return HttpResponse(resp, content_type='application/json')
#     except Exception as e:
#         exc=traceback.format_exc()
#         error_obj = NWisefinError()
#         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#         error_obj.set_description(str(e))
#         logger.info('ta_ all_booking_get- ' + str(e)+str(exc))
#         return HttpResponse(error_obj.get(), content_type='application/json')


# @csrf_exempt
# @api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def pdf_download(request, id):
#     try:
#         if request.method == 'GET':
#             type=request.GET.get('type')
#             params = {}
#             # ip = 'http://emc-vysfin-sit.kvbank.in/'
#             scope = request.scope
#             # api_service=ApiService(scope)
#             # token = "Bearer  " + api_service.get_authtoken(request)
#             # headers = {"content-type": "application/json", "Authorization": "" + token + ""}
#             # datas='{"filter": {"action": "GET", "type": "BARCODE_GENERATION", "InvoiceHeader_Gid": '+id+', "create_by": 1}, "CLASSIFICATION": {"Entity_Gid": 1}}'
#             datas=''
#             token_name = request.headers['Authorization']
#             headers = {'Authorization': token_name}
#             SERVER_IP = "http://143.110.244.51:8185"
#             memo_data = requests.get( SERVER_IP + "/ecfserv/ecf_covernote/"+id, params=params, data=datas, headers=headers,
#                                  verify=False)
#             response = json.loads(memo_data.content.decode("utf-8"))
#             pdf = HttpResponse(content_type='application/pdf')
#             pdf['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'
#             pdf = render_to_pdf(BASE_DIR + '/taservice/Templates/Shared/claimform_template.html', response)
#             pdf2 = read_xlsx(pdf,type)
#             return pdf2
#
#     except Exception as e:
#         error_obj = NWisefinError()
#         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#         error_obj.set_description(str(e))
#         logger.info('ta_ pdf_download- ' + str(e))
#         return HttpResponse(error_obj.get(), content_type='application/json')


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def read_xlsx(fn,type):
    if type is not None:
        file = io.BytesIO(fn.content)
        # target = "Karur Vysya bank"
        # output = watermark_pdf(target,file)
        return HttpResponse(file.getvalue(), content_type='application/pdf')
    else:

        inmemory_content = io.BytesIO(fn.content)
        file = inmemory_content
        response = StreamingHttpResponse(file, content_type='application/octet-stream')
        response['Content-Disposition'] = 'inline; filename="{}"'.format(file)
        return response

@csrf_exempt
@api_view(['DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def expense_delete(request,tourid,type):
    try:
        if request.method== "DELETE":
            # user_id = request.user.id
            scope = request.scope
            employee_id=request.employee_id
            service = Validation(scope)
            permission = service.tour_maker_check(tourid, employee_id)
            if permission is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.VALID_USER)
                return HttpResponse(error_obj.get(), content_type='application/json')
            claim_check = service.exp_claim_status(tourid)
            if claim_check is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.CANT_DELETE_EXP)
                return HttpResponse(error_obj.get(), content_type='application/json')
            scope = request.scope
            service=TourExpense(scope)
            resp= service.delete_expense(int(tourid),int(type))
            return HttpResponse(resp.get(),content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ expense_delete- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@transaction.atomic
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def dependencies(request):
    if request.method == 'GET':
        scope = request.scope
        service = EmployeemappingData(scope)
        resp_obj = service.get_all_dependencies()
        return HttpResponse(resp_obj.get(), content_type='application/json')

    elif request.method == 'POST':
        data = json.loads(request.body)
        scope = request.scope
        service = EmployeemappingData(scope)
        # user_id = request.user.id
        employee_id=request.employee_id
        # emp = Employee.objects.get(user_id=user_id)
        # employee_id = emp.id
        resp_obj = service.dependencies(data,employee_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')

@csrf_exempt
@transaction.atomic
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def travel_dependencies(request):
    if request.method == 'GET':
        scope = request.scope
        service = EmployeemappingData(scope)
        resp_obj = service.get_all_travel_dependencies()
        return HttpResponse(resp_obj.get(), content_type='application/json')

    elif request.method == 'POST':
        data = json.loads(request.body)
        scope = request.scope
        service = EmployeemappingData(scope)
        # user_id = request.user.id
        employee_id=request.employee_id
        # emp = Employee.objects.get(user_id=user_id)
        # employee_id = emp.id
        resp_obj = service.travel_dependencies(data,employee_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')

@csrf_exempt
@transaction.atomic
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def travel_dependencies_travelid(request,travelid):
    try:
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        if request.method == 'GET':
            service = EmployeemappingData(scope)
            resp_obj = service.get_travel_dependencies_id(travelid,employee_id)
            return HttpResponse(resp_obj.get(), content_type='application/json')
        if request.method == 'DELETE':
            scope = request.scope
            service = EmployeemappingData(scope)
            resp_obj = service.delete_depenceies_id(travelid,employee_id)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ travel_dependencies_travelid- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def dependencies_get(request):
    try:
        if request.method=='GET':
            # user_id = request.user.id
            scope = request.scope
            employee_id=request.employee_id
            service=EmployeemappingData(scope)
            onbehalfof= int(request.GET.get('onbehalfof',0))
            if onbehalfof is not None and onbehalfof >0:
                data = service.get_dependencies(onbehalfof,request)
            else:
                data = service.get_dependencies(employee_id,request)
            resp = json.dumps(data, default=lambda o: o.__dict__)
            return HttpResponse(resp, content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ dependencies_get- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ongoing_tour(request):
    try:
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        service = TourMaker(scope)
        page = request.GET.get('page', 1)
        onb = request.GET.get('onbehalf', None)
        requestno = request.GET.get('requestno', None)
        requestdate = request.GET.get('requestdate', None)
        page = int(page)
        vys_page =NWisefinPage(page, 10)
        resp_obj = service.ongoing_tour(employee_id,onb,vys_page,requestno,requestdate,request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ ongoing_tour- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def forward_data_get(request):
    try:
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        service = TourMaker(scope)
        apptype = request.GET.get('apptype')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page =NWisefinPage(page, 10)
        resp_obj = service.forward_data_get(employee_id,apptype,vys_page,request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ forward_data_get- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def emp_details_get(request):
    try:
    # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        service = ApiService(scope)
        emp_id = request.GET.get('onbehalf',employee_id)
        resp_obj = service.employee_details_get(emp_id,request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ emp_details_get- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def emp_elig_travel(request):
    # user_id = request.user.id
    scope = request.scope
    employee_id=request.employee_id
    emp_id = request.GET.get('onbehalf',employee_id)
    service = ApiService(scope)
    resp_obj = service.employee_details_get(emp_id,request)
    grade=resp_obj.grade
    grade_service=Tourno_details(scope)
    resp_obj=grade_service.emp_elig_travel(grade)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@transaction.atomic
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def provision(request):
    try:
        data = json.loads(request.body)
        scope = request.scope
        service = Payment(scope)
        resp_obj = service.provision(request,data)
        return HttpResponse(resp_obj, content_type='application/json')
    except Exception as e:
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        return HttpResponse(error_obj.get(), content_type='application/json')

@transaction.atomic
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def adv_adjust_check(request,tourid):
    scope = request.scope
    service = TourAdvance(scope)
    resp_obj = service.adv_adjust_check(request,tourid)
    return HttpResponse(resp_obj.get(), content_type="application/json")

@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def change_approver(request):
    try:
        # user_id = request.user.id
        approver_data = json.loads(request.body)
        scope = request.scope
        employee_id=request.employee_id
        service=Validation(scope)
        approver_permission=service.permisssion_check_type(approver_data["tour_id"],approver_data["approver"],App_type.TOUR,App_level.ZERO_LEVEL)
        if approver_permission is True:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.VALID_USER)
            return HttpResponse(error_obj.get(), content_type='application/json')
        service = TourMaker(scope)
        resp_obj = service.change_approver(approver_data,request,employee_id)
        return HttpResponse(resp_obj.get(), content_type="application/json")

    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ change_approver- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def allowance_file_upload(request):
    if request.method == 'POST':
        file_name = request.FILES.getlist('file')[0].name
        extension = file_name.split('.')[-1]
        scope = request.scope
        file_validation=Validation(scope)
        filetype_check = file_validation.exel_file_validation(extension)
        # user_id = request.user.id
        employee_id=request.employee_id

        if filetype_check is False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_FILETYPE)
            error_obj.set_description(ErrorDescription.SUPPORTED_FILE_TYPES)
            response = HttpResponse(error_obj.get())
            return HttpResponse(response, content_type='application/json')
        else:
            excel_data = pd.read_excel(request.FILES['file'], engine='xlrd')
            df = pd.DataFrame(excel_data)
            transation_obj = df.fillna(np.nan).replace([np.nan], [None]).to_dict(orient='records')
            scope = request.scope
            allowance=Tour_allowance(scope)
            allowance_file_insert=allowance.excel_file(transation_obj,employee_id)
            return  HttpResponse(allowance_file_insert.get(), content_type='application/json')
#
# @csrf_exempt
# @api_view(['POST','GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def holiday_file_upload(request):
#     if request.method == 'POST':
#         file_name = request.FILES.getlist('file')[0].name
#         extension = file_name.split('.')[-1]
#         scope = request.scope
#         file_validation=Validation(scope)
#         filetype_check = file_validation.exel_file_validation(extension)
#         #user_id = request.user.id
#         employee_id=request.employee_id
#
#         if filetype_check is False:
#             error_obj = NWisefinError()
#             error_obj.set_code(ErrorMessage.INVALID_FILETYPE)
#             error_obj.set_description(ErrorDescription.SUPPORTED_FILE_TYPES)
#             response = HttpResponse(error_obj.get())
#             return HttpResponse(response, content_type='application/json')
#         else:
#             excel_data = pd.read_excel(request.FILES['file'], engine='xlrd')
#             df = pd.DataFrame(excel_data)
#             transation_obj = df.fillna(np.nan).replace([np.nan], [None]).to_dict(orient='records')
#             scope = request.scope
#             allowance=Tour_allowance(scope)
#             allowance_file_insert=allowance.holiday_file(transation_obj,employee_id)
#             return  HttpResponse(allowance_file_insert.get(), content_type='application/json')
#
@csrf_exempt
@transaction.atomic
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def recovery_summary(request):
    try:
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        data = json.loads(request.body)
        scope = request.scope
        service = Payment(scope)
        resp_obj = service.recovery_summary(request,data,employee_id)
        # resp = json.dumps(resp_obj, default=lambda o: o.__dict__)
        return HttpResponse(resp_obj, content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ recovery_summary- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@transaction.atomic
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def recovery_get_jv(request):
    try:
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        data = json.loads(request.body)
        service = Payment(scope)
        resp_obj = service.recovery_get_jv(request,data,employee_id)
        resp = json.dumps(resp_obj, default=lambda o: o.__dict__)
        return HttpResponse(resp, content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ recovery_get_jv- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def branch_onbehalf_status(request,branch,empid):
    try:
        page = request.GET.get('page', 1)
        maker = request.GET.get('maker',0)
        page = int(page)
        vys_page =NWisefinPage(page, 10)
        scope = request.scope
        service = Onbehalf_service(scope)
        resp_obj = service.branch_based_onb_get(request,branch,empid,vys_page,maker)
        return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        return HttpResponse(error_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def common_excelUpload(request):
    check = request.GET['recheck']
    table_name = request.GET['table']
    date_time = datetime.now()
    ignore_keys = ['id', 'created_by', 'created_date', 'updated_by', 'updated_date']
    # user_id = request.user.id
    # emp_service = EmployeeService()
    empid =1
    if check=='false':
        file_obj = pd.read_excel(request.FILES['file']).to_dict(orient='records')
        values = []
        columns = ""
        for j in file_obj[0]:
            if j in ignore_keys:
                continue
            else:
                columns += f"{j},"
        for i in file_obj:
            values.append(tuple(ignore_values(i,columns.split(','),empid,date_time)))
        original_values = ""
        for k in range(0,len(values)):
            if k == 0:
                original_values+=f"{values[k]}"
            else:
                original_values += f",{values[k]}"
        query = f"insert into {table_name} ({columns}created_by,created_date) values{original_values}".replace('nan','NULL')
        print(query)
        cursor = connection.cursor()
        cursor.execute(query)
        cursor.close()
        suc_obj =NWisefinSuccess()
        suc_obj.set_status(SuccessStatus.SUCCESS)
        return HttpResponse(suc_obj.get(),content_type="application/json")
    elif check=='true':
        file_obj = pd.read_excel(request.FILES['file']).to_dict(orient='records')
        for i in file_obj:
            column_values = "set "
            for index,k in enumerate(i,start=0):
                if k in ignore_keys:
                    continue
                else:
                    column_values+=f"{k}='{i[k]}',"
            query = f"update {table_name} {column_values}updated_by={empid},updated_date='{date_time}' where id={i['id']}".replace('nan','NULL')
            cursor = connection.cursor()
            cursor.execute(query)
            cursor.close()
        update_obj = SuccessStatus()
        update_obj.set_status(update_obj.SUCCESS)
        return HttpResponse(update_obj.get(), content_type="application/json")
    else:
        invalid_obj =NWisefinSuccess()
        invalid_obj.set_status(SuccessStatus.SUCCESS)
        return HttpResponse(invalid_obj.get(), content_type="application/json")

def ignore_values(dict_,needed_keys,empid,data_time):
    arr = []
    for i in needed_keys:
        if i != "":
            arr.append(dict_[i])
    arr.append(empid)
    arr.append(f'{data_time}')
    return arr

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def recovery_jv_entry(request,branch,empid):
    try:
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        data = json.loads(request.body)
        service = Payment(scope)
        resp_obj = service.recovery_get_jv(request, data, employee_id)
        resp = json.dumps(resp_obj, default=lambda o: o.__dict__)
        return HttpResponse(resp, content_type='application/json')
    except Exception as e:
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@transaction.atomic
@api_view(['DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def tour_detail_delete(request,id):
    try:
        scope = request.scope
        validation=Validation(scope)
        # user_id = request.user.id
        service = TourMaker(scope)
        employee_id=request.employee_id
        tour_id = service.tourid_get_detail_id(id)
        permission_check = validation.tour_maker_check(tour_id, employee_id)
        tour_status = validation.tour_status_del(tour_id)
        if permission_check is False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.CANT_DELETE)
            return HttpResponse(error_obj.get(), content_type='application/json')
        elif tour_status is False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.VALID_USER)
            return HttpResponse(error_obj.get(), content_type='application/json')

        elif request.method == 'DELETE':

            resp_obj = service.delete_tour_details(id,employee_id,request)
            return HttpResponse(resp_obj.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ tour_detail_delete- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')
# @csrf_exempt
# @transaction.atomic
# @api_view(['DELETE'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def travel_req_delete(request,req_id):
#     try:
#         scope = request.scope
#         tour_id = request.GET.get("tour_id")
#         validation=Validation(scope)
#         # user_id = request.user.id
#         employee_id=request.employee_id
#         permission_check = validation.tour_maker_check(tour_id, employee_id)
#         tour_status = validation.tour_status_del(tour_id)
#         if permission_check is False:
#             error_obj = NWisefinError()
#             error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#             error_obj.set_description(ErrorDescription.VALID_USER)
#             return HttpResponse(error_obj.get(), content_type='application/json')
#         elif tour_status is False:
#             error_obj = NWisefinError()
#             error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#             error_obj.set_description(ErrorDescription.CANT_DELETE)
#             return HttpResponse(error_obj.get(), content_type='application/json')
#
#         scope = request.scope
#         service = TourMaker(scope)
#         resp_obj = service.delete_travel_requirement(req_id,employee_id,tour_id)
#         return HttpResponse(resp_obj.get(), content_type='application/json')
#     except Exception as e:
#         error_obj = NWisefinError()
#         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#         error_obj.set_description(str(e))
#         return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def common_excelUpload(request):
    check = request.GET['recheck']
    table_name = request.GET['table']
    date_time = datetime.now()
    ignore_keys = ['id', 'created_by', 'created_date', 'updated_by', 'updated_date']
#     # user_id = request.user.id
    # emp_service = EmployeeService()
    empid = 1#emp_service.get_empid_from_userid(user_id)
    if check=='false':
        file_obj = pd.read_excel(request.FILES['file']).to_dict(orient='records')
        values = []
        columns = ""
        for j in file_obj[0]:
            if j in ignore_keys:
                continue
            else:
                columns += f"{j},"
        for i in file_obj:
            values.append(tuple(ignore_values(i,columns.split(','),empid,date_time)))
        original_values = ""
        for k in range(0,len(values)):
            if k == 0:
                original_values+=f"{values[k]}"
            else:
                original_values += f",{values[k]}"
        query = f"insert into {table_name} ({columns}created_by,created_date) values{original_values}".replace('nan','NULL')
        cursor = connection.cursor()
        cursor.execute(query)
        cursor.close()
        suc_obj = NWisefinSuccess()
        suc_obj.set_status(SuccessStatus.SUCCESS)
        return HttpResponse(suc_obj.get(),content_type="application/json")
    elif check=='true':
        file_obj = pd.read_excel(request.FILES['file']).to_dict(orient='records')
        for i in file_obj:
            column_values = "set "
            for index,k in enumerate(i,start=0):
                if k in ignore_keys:
                    continue
                else:
                    column_values+=f"{k}='{i[k]}',"
            query = f"update {table_name} {column_values}updated_by={empid},updated_date='{date_time}' where id={i['id']}".replace('nan','NULL')
            cursor = connection.cursor()
            cursor.execute(query)
            cursor.close()
        update_obj = NWisefinSuccess()
        update_obj.set_status(SuccessStatus.SUCCESS)
        return HttpResponse(update_obj.get(), content_type="application/json")
    else:
        invalid_obj = NWisefinSuccess()
        invalid_obj.set_status(SuccessStatus.SUCCESS)
        return HttpResponse(invalid_obj.get(), content_type="application/json")

def ignore_values(dict_,needed_keys,empid,data_time):
    arr = []
    for i in needed_keys:
        if i != "":
            arr.append(dict_[i])
    arr.append(empid)
    arr.append(f'{data_time}')
    return arr

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def role_permission(request):
    try:
        scope = request.scope
        # user_id = request.user.id
        employee_id=request.employee_id
        data = json.loads(request.body)
        service = ModulePermission(scope)
        resp_obj = service.employee_modulerole(employee_id,data["key"])
        onb_service=Onbehalf_service(scope)
        onb_status=onb_service.onbehalf_emp_get(employee_id, request)
        if onb_status is True:
            resp_obj.append(Common_data.onbehalf)
        return HttpResponse(json.dumps(resp_obj), content_type='application/json')
    except Exception as e:
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        return HttpResponse(error_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def chat_box(request):
    if request.method=='POST':
        try:
            scope = request.scope
            employeeid = request.employee_id
            tour_comments=TourMaker(scope)
            data = json.loads(request.body)
            # data =Chat_Box(data)
            tour_chat=tour_comments.request_comment_chat(request,data,employeeid)
            return HttpResponse(tour_chat.get(), content_type='application/json')
        except Exception as e:
            exc=traceback.format_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            logger.info('ta_ chat_box- ' + str(e)+str(exc))
            return HttpResponse(error_obj.get(), content_type='application/json')
    elif request.method=='GET':
        try:
            scope=request.scope
            employeeid = request.employee_id
            tour_comments = TourMaker(scope)
            # approver_id = request.GET.get('approver_id')
            tour_id= request.GET.get('tourid')
            page = request.GET.get('page', 1)
            page = int(page)
            vys_page = NWisefinPage(page, 10)
            get_chat=tour_comments.chats(tour_id,employeeid,vys_page,request)
            return HttpResponse(get_chat.get(), content_type='application/json')
        except Exception as e:
            exc=traceback.format_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            logger.info('ta_ chat_box_get- ' + str(e)+str(exc))
            return HttpResponse(error_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def chat_box_view(request):
    if request.method=='POST':
        try:
            scope = request.scope
            employeeid = request.employee_id
            tour_comments=TourMaker(scope)
            tour_id = request.GET.get('tourid')
            # data =Chat_Box(data)
            tour_chat=tour_comments.chat_view(request,tour_id,employeeid)
            return HttpResponse(tour_chat.get(), content_type='application/json')
        except Exception as e:
            exc=traceback.format_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            logger.info('ta_ chat_box_view- ' + str(e)+str(exc))
            return HttpResponse(error_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def chat_summary(request):
    try:
        start_time=datetime.now()
        scope = request.scope
        employee_id = request.employee_id
        tour_comments = TourMaker(scope)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        option = request.GET.get("option")
        created_pending = request.GET.get("created_or_pending")
        get_chat = tour_comments.chat_summary(request,employee_id,option,created_pending,vys_page)
        end_time=datetime.now()
        return HttpResponse(get_chat.get(), content_type='application/json')
    except Exception as e:
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ approved_by_get- ' + str(e))
        return HttpResponse(error_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def del_chat_box(request):
    try:
        scope = request.scope
        employeeid = request.employee_id
        tour_comments = TourMaker(scope)
        chat_id = request.GET.get('chatid')
        tour_id = request.GET.get('tourid')
        chat_del=tour_comments.dele_chat(employeeid,tour_id,chat_id)
        return HttpResponse(chat_del.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ del_chat_box- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def undo_chat_box(request):
    try:
        if request.method=='POST':
            scope = request.scope
            employeeid = request.employee_id
            tour_comments = TourMaker(scope)
            chat_id = request.GET.get('chatid')
            tour_id = request.GET.get('tourid')
            chat_del=tour_comments.undo_chat_box(employeeid,tour_id,chat_id,request)
            return HttpResponse(chat_del.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ del_chat_box- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def approved_by_get(request):
    try:
        scope = request.scope
        employeeid = request.employee_id
        tour_comments = TourMaker(scope)
        approver_id = request.GET.get('approver_id')
        tour_id = request.GET.get('tourid')
        get_chat = tour_comments.approvedby_empget(tour_id)
        return HttpResponse(get_chat.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ approved_by_get- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

# @csrf_exempt
# @api_view(['POST','GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def insert_doctype(request):
#     if request.method=='POST':
#         try:
#             scope = request.scope
#             employeeid = request.employee_id
#             create_doc=TourMaker(scope)
#             data = json.loads(request.body)
#             tour_chat=create_doc.insert_doc(data,employeeid)
#             return HttpResponse(tour_chat.get(), content_type='application/json')
#         except Exception as e:
#             error_obj = NWisefinError()
#             error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#             error_obj.set_description(str(e))
#             return HttpResponse(error_obj.get(), content_type='application/json')
#     elif request.method=='GET':
#         try:
#             scope=request.scope
#             employeeid = request.employee_id
#             get_doc= TourMaker(scope)
#             file_name = request.GET.get('file_name')
#             page = request.GET.get('page', 1)
#             page = int(page)
#             vys_page = NWisefinPage(page, 10)
#             get_chat=get_doc.get_doc(file_name,vys_page)
#             return HttpResponse(get_chat.get(), content_type='application/json')
#         except Exception as e:
#             error_obj = NWisefinError()
#             error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#             error_obj.set_description(str(e))
#             return HttpResponse(error_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def doc_insert(request):
    if request.method=='POST':
        try:
            scope = request.scope
            employeeid = request.employee_id
            create_doc= Booking_requirement(scope)
            # data = json.loads(request.body)
            data = json.loads(request.data.dict().get('data'))
            insert_docc=create_doc.insert_tadoc(request,data)
            return HttpResponse(insert_docc.get(), content_type='application/json')
        except Exception as e:
            exc=traceback.format_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            logger.info('ta_ doc_insert- ' + str(e)+str(exc))
            return HttpResponse(error_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def doc_fetch(request):
    if request.method=='GET':
        try:
            scope = request.scope
            employeeid = request.employee_id
            create_doc= Booking_requirement(scope)
            # data = json.loads(request.body)
            tour_id=request.GET.get('tour_id')
            # detail_id=request.GET.get('detail_id')
            requirement_type=request.GET.get('requirement_type')
            ref_type=request.GET.get('ref_type')
            requirment=request.GET.get('requirement')
            id=request.GET.get('id')
            fetch_doc=create_doc.fetch_tadoc(request,tour_id,id,requirement_type,requirment,ref_type)
            return HttpResponse(fetch_doc, content_type='application/json')
        except Exception as e:
            exc=traceback.format_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            logger.info('ta_ doc_fetch- ' + str(e)+str(exc))
            return HttpResponse(error_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def doc_view(request):
    if request.method=='GET':
        try:
            scope = request.scope
            employeeid = request.employee_id
            create_doc= Booking_requirement(scope)
            # data = json.loads(request.body)
            # tour_id=request.GET.get('tour_id')
            # detail_id=request.GET.get('detail_id')
            id=request.GET.get('id')
            doc_option=request.GET.get('doc_option')
            # ref_type = request.GET.get('ref_type')
            # requirement_type=request.GET.get('requirement_type')
            # requirment=request.GET.get('requirement')
            fetch_doc=create_doc.document_view(request,id,doc_option)
            return fetch_doc
            # return HttpResponse(fetch_doc, content_type='application/json')
        except Exception as e:
            exc=traceback.format_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            logger.info('ta_ doc_view- ' + str(e)+str(exc))
            return HttpResponse(error_obj.get(), content_type='application/json')
# @csrf_exempt
# @api_view(['DELETE'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def del_doctype(request):
#     try:
#         scope = request.scope
#         employeeid = request.employee_id
#         tour_comments = TourMaker(scope)
#         file_name = request.GET.get('file_name')
#         chat_del=tour_comments.dele_doc_type(file_name)
#         return HttpResponse(chat_del.get(), content_type='application/json')
#     except Exception as e:
#         error_obj = NWisefinError()
#         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#         error_obj.set_description(str(e))
#         return HttpResponse(error_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['DELETE','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def particulardoc_get(request,id):
    if request.method=="GET":
        try:
            scope = request.scope
            employeeid = request.employee_id
            tour_comments =  Booking_requirement(scope)
            # file_name = request.GET.get('file_name')
            chat_del=tour_comments.doc_particularget(id,employeeid)
            return HttpResponse(chat_del.get(), content_type='application/json')
        except Exception as e:
            exc=traceback.format_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            logger.info('ta_ particulardoc_get- ' + str(e)+str(exc))
            return HttpResponse(error_obj.get(), content_type='application/json')
    elif request.method=="DELETE":
        try:
            scope = request.scope
            employeeid = request.employee_id
            tour_comments =  Booking_requirement(scope)
            # file_name = request.GET.get('file_name')
            chat_del=tour_comments. doc_particular_del(id,employeeid)
            return HttpResponse(chat_del.get(), content_type='application/json')
        except Exception as e:
            exc=traceback.format_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            logger.info('ta_ particulardoc_get_delete- ' + str(e)+str(exc))
            return HttpResponse(error_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def holiday_check(request):
    try:
        scope = request.scope
        tour=TourMaker(scope)
        onbehalf = request.GET.get('onbehalf',request.employee_id)
        tour_id = request.GET.get('tour_id')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        week_end_travel=tour.holidaycheck_weekend(start_date,end_date,onbehalf,tour_id)
        return HttpResponse(week_end_travel.get(), content_type='application/json')
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ holiday_check- ' + str(e) + str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def all_travel_employee(request):
    try:
        scope = request.scope
        employeeid = request.employee_id
        get_emp_travel = TourMaker(scope)
        emp_id = request.GET.get('employee_id')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        get_chat = get_emp_travel.emp_alltravel_count(emp_id,vys_page)
        return HttpResponse(get_chat.get(), content_type='application/json')
    except Exception as e:
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        return HttpResponse(error_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def total_claim_count(request):
    try:
        scope = request.scope
        employeeid = request.employee_id
        get_emp_travel = TourMaker(scope)
        emp_id = request.GET.get('employee_id')
        tour_id = request.GET.get('tour_id')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        get_chat = get_emp_travel.total_claim_count(emp_id,vys_page)
        return HttpResponse(get_chat.get(), content_type='application/json')
    except Exception as e:
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        return HttpResponse(error_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def alltravelget_date(request):
    try:
        scope = request.scope
        employeeid = request.employee_id
        get_emp_travel = TourMaker(scope)
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        get_chat = get_emp_travel.alltravelget_date(start_date,end_date,vys_page)
        return HttpResponse(get_chat.get(), content_type='application/json')
    except Exception as e:
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        return HttpResponse(error_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def allclaimget_date(request):
    try:
        scope = request.scope
        employeeid = request.employee_id
        get_emp_travel = TourMaker(scope)
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        get_chat = get_emp_travel.allclaimget_date(start_date,end_date,vys_page)
        return HttpResponse(get_chat.get(), content_type='application/json')
    except Exception as e:
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        return HttpResponse(error_obj.get(), content_type='application/json')

# @csrf_exempt
# @api_view(['POST','GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def booking(request):
#     try:
#         scope = request.scope
#         booking_service = TourMaker(scope)
#         employeeid = request.employee_id
#         if request.method=="POST":
#             user_data = json.loads(request.body)
#             booking_data=booking_service.booking(user_data['data'],employeeid)
#         elif request.method=="GET":
#             tour_id = request.GET.get('tour_id')
#             booking_data = booking_service.get_all_booked_details(tour_id)
#         return HttpResponse(booking_data.get(), content_type='application/json')



    # except Exception as e:
    #     error_obj = NWisefinError()
    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #     error_obj.set_description(str(e))
    #     return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def cab_booking(request):

    if request.method == 'POST':
        # userdata = json.loads(request.body)
        data = json.loads(request.body)
        # obj = Cab_request(data)
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        requirment_service = Cab_requirement(scope)

        # Tour_service = Approve_list(scope)
        resp_obj = requirment_service.cab_data(data,employee_id,1)
        response= HttpResponse(resp_obj.get(), content_type='application/json')
        return response
    elif request.method=='GET':

        scope = request.scope
        order_service = Cab_requirement(scope)
        order_dec = order_service.fetch_cab()
        product_details = HttpResponse(order_dec.get(), content_type='application/json')
        return product_details

@csrf_exempt
@api_view(['DELETE','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def cab_details(request,id):
    try:
        if request.method == 'DELETE':
            scope = request.scope

            state_service = Cab_requirement(scope)
            resp_obj = state_service.Cab_delete(id)

            return HttpResponse(resp_obj.get(), content_type='application/json')
        elif request.method == 'GET':

            scope = request.scope
            order_service = Cab_requirement(scope)
            order_dec = order_service.get_cab(id)
            product_details = HttpResponse(order_dec.get(), content_type='application/json')
            return product_details
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ cab_details- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def bus_booking(request):

    if request.method == 'POST':
        # userdata = json.loads(request.body)
        data = json.loads(request.body)

        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        requirment_service = Bus_requirement(scope)

        # Tour_service = Approve_list(scope)
        resp_obj = requirment_service.insert_bus_data(data,employee_id,1)
        response= HttpResponse(resp_obj.get(), content_type='application/json')
        return response
    elif request.method=='GET':

        scope = request.scope
        order_service = Bus_requirement(scope)
        order_dec = order_service.fetch_Bus()
        product_details = HttpResponse(order_dec.get(), content_type='application/json')
        return product_details

@csrf_exempt
@api_view(['DELETE','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def bus_details(request,id):
    try:
        if request.method == 'DELETE':
            scope = request.scope
            service = Bus_requirement(scope)
            resp_obj = service.bus_delete(id)
            return HttpResponse(resp_obj, content_type='application/json')
        elif request.method == 'GET':

            scope = request.scope
            order_service = Bus_requirement(scope)
            order_dec = order_service.get_Bus(id)
            product_details = HttpResponse(order_dec.get(), content_type='application/json')
            return product_details
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ bus_details- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def accommodation_booking(request):

    if request.method == 'POST':
        # userdata = json.loads(request.body)
        data = json.loads(request.body)
        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        requirment_service = AccomodationBooking_requirement(scope)

        # Tour_service = Approve_list(scope)
        resp_obj = requirment_service.accomadation_data(data,employee_id,1)
        response= HttpResponse(resp_obj.get(), content_type='application/json')
        return response
    elif request.method=='GET':

        scope = request.scope
        order_service = AccomodationBooking_requirement(scope)
        order_dec = order_service.fetch_accomadation()
        product_details = HttpResponse(order_dec.get(), content_type='application/json')
        return product_details

@csrf_exempt
@api_view(['DELETE','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def accommodation_details(request,id):
    try:
        if request.method == 'DELETE':
            scope = request.scope
            service = AccomodationBooking_requirement(scope)
            resp_obj = service.accomadation_delete(id)

            return HttpResponse(resp_obj, content_type='application/json')
        elif request.method == 'GET':
            scope = request.scope
            service = AccomodationBooking_requirement(scope)
            order_dec = service.get_accomadation(id)
            product_details = HttpResponse(order_dec.get(), content_type='application/json')
            return product_details
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ accommodation_details- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def air_booking(request):
    try:

        if request.method == 'POST':
            # userdata = json.loads(request.body)
            data = json.loads(request.body)

            # user_id = request.user.id
            scope = request.scope
            employee_id=request.employee_id
            requirment_service = Air_requirement(scope)

            # Tour_service = Approve_list(scope)
            resp_obj = requirment_service.Air_data(data,employee_id,1)
            response= HttpResponse(resp_obj.get(), content_type='application/json')
            return response
        elif request.method=='GET':

            scope = request.scope
            order_service = Air_requirement(scope)
            order_dec = order_service.fetch_Air()
            product_details = HttpResponse(order_dec.get(), content_type='application/json')
            return product_details
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ air_booking- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def sameday_booking(request):

    # if request.method == 'POST':
    #     # userdata = json.loads(request.body)
    #     data = json.loads(request.body)
    #
    #     # user_id = request.user.id
    #     scope = request.scope
    #     employee_id=request.employee_id
    #     requirment_service = Air_requirement(scope)
    #
    #     # Tour_service = Approve_list(scope)
    #     resp_obj = requirment_service.Air_data(data,employee_id,1)
    #     response= HttpResponse(resp_obj.get(), content_type='application/json')
    #     return response
    try:
        if request.method=='POST':
            scope = request.scope
            order_service = Air_requirement(scope)
            data=json.loads(request.body)
            from_time = data["from_time"]
            # to_time = request.GET.get('to_time')
            from_place = data["from_place"]
            to_place = data["to_place"]
            booking_type =data["booking_type"]
            order_dec = order_service.sameday_booking(request,from_time,from_place,to_place,booking_type)
            product_details = HttpResponse(order_dec.get(), content_type='application/json')
            return product_details
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ sameday_booking- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['DELETE','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def air_details(request,id):
    try:
        if request.method == 'DELETE':
            scope = request.scope

            state_service = Air_requirement(scope)
            resp_obj = state_service.Air_delete(id)

            return HttpResponse(resp_obj, content_type='application/json')
        elif request.method == 'GET':

            scope = request.scope
            order_service = Air_requirement(scope)
            order_dec = order_service.get_Air(id)
            product_details = HttpResponse(order_dec.get(), content_type='application/json')
            return product_details
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ air_details- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def train_booking(request):

    if request.method == 'POST':
        # userdata = json.loads(request.body)
        data = json.loads(request.body)

        # user_id = request.user.id
        scope = request.scope
        employee_id=request.employee_id
        requirment_service = Train_requirement(scope)

        # Tour_service = Approve_list(scope)
        resp_obj = requirment_service.Train_data(data,employee_id,1)
        response= HttpResponse(resp_obj.get(), content_type='application/json')
        return response
    elif request.method=='GET':

        scope = request.scope
        order_service = Train_requirement(scope)
        order_dec = order_service.fetch_Train()
        product_details = HttpResponse(order_dec.get(), content_type='application/json')
        return product_details

@csrf_exempt
@api_view(['DELETE','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def train_details(request,id):
    try:
        if request.method == 'DELETE':
            scope = request.scope
            state_service = Train_requirement(scope)
            resp_obj = state_service.train_delete(id)
            return HttpResponse(resp_obj, content_type='application/json')
        elif request.method == 'GET':
            scope = request.scope
            order_service = Train_requirement(scope)
            order_dec = order_service.get_Train(id)
            product_details = HttpResponse(order_dec.get(), content_type='application/json')
            return product_details
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ train_details- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')



@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def cab_booking_admin(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.data.dict().get('data'))
            scope = request.scope
            employee_id=request.employee_id
            requirment_service = Cab_requirement(scope)
            logger.info('ta_ cab_booking_admin- ' + str(employee_id) + str(data))
            resp_obj = requirment_service.cab_data_admin(request,data,employee_id)
            response= HttpResponse(resp_obj.get(), content_type='application/json')
            return response
        elif request.method=='GET':
            scope = request.scope
            order_service = Cab_requirement(scope)
            detail_id = request.GET.get('detail_id')
            tour_id = request.GET.get('tour_id')
            page = request.GET.get('page', 1)
            page = int(page)
            vys_page = NWisefinPage(page, 10)
            all_report = request.GET.get('all_report')
            order_dec = order_service.fetch_cab_admin(detail_id,request,all_report,vys_page,tour_id)
            product_details = HttpResponse(order_dec.get(), content_type='application/json')
            return product_details
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ cab_booking_admin- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['DELETE','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def cab_details_admin(request,id):
    try:
        if request.method == 'DELETE':
            scope = request.scope
            state_service = Cab_requirement(scope)
            resp_obj = state_service.Cab_delete_admin(id)
            return HttpResponse(resp_obj.get(), content_type='application/json')
        elif request.method == 'GET':
            scope = request.scope
            order_service = Cab_requirement(scope)
            order_dec = order_service.get_cab_admin(id)
            product_details = HttpResponse(order_dec.get(), content_type='application/json')
            return product_details
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ cab_details_admin- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def bus_booking_admin(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.data.dict().get('data'))
            scope = request.scope
            booking_service=Booking_requirement(scope)
            prev_files=booking_service.fetch_tadoc(request, None, None, Travel_requirements.bus, data['requirement_id'], 1)

            if "description" in json.loads(prev_files):
                if len(request.FILES) == 0 and json.loads(prev_files)['description']==ErrorDescription.NO_FILE_TA:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.FILE_REQUIRED_BOOKING)
                    return HttpResponse(error_obj.get(), content_type='application/json')

            employee_id=request.employee_id
            requirment_service = Bus_requirement(scope)
            logger.info('ta_ bus_booking_admin- ' + str(employee_id) + str(data))
            resp_obj = requirment_service.insert_bus_data_admin(request,data,employee_id)
            response= HttpResponse(resp_obj.get(), content_type='application/json')
            return response
        elif request.method=='GET':
            scope = request.scope
            order_service = Bus_requirement(scope)
            detail_id = request.GET.get('detail_id')
            tour_id = request.GET.get('tour_id')
            page = request.GET.get('page', 1)
            page = int(page)
            vys_page = NWisefinPage(page, 10)
            all_report = request.GET.get('all_report')
            order_dec = order_service.fetch_Bus_admin(detail_id,request,all_report,vys_page,tour_id)
            product_details = HttpResponse(order_dec.get(), content_type='application/json')
            return product_details
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ bus_booking_admin- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['DELETE','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def bus_details_admin(request,id):
    try:
        if request.method == 'DELETE':
            scope = request.scope
            service = Bus_requirement(scope)
            resp_obj = service.bus_delete_admin(id)
            return HttpResponse(resp_obj, content_type='application/json')
        elif request.method == 'GET':
            scope = request.scope
            order_service = Bus_requirement(scope)
            order_dec = order_service.get_Bus_admin(id)
            product_details = HttpResponse(order_dec.get(), content_type='application/json')
            return product_details
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ bus_details_admin- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_requirements_admin(request):
    try:
        if request.method == 'GET':
            scope = request.scope
            req_id = request.GET.get('requirement_id')
            type = request.GET.get('type',0)
            tour_id = request.GET.get('tour_id')
            detail_id = request.GET.get('detail_id')
            service = AccomodationBooking_requirement(scope)
            if req_id is not None:
                req_id=int(req_id)
            if type is not None:
                type=int(type)
            if tour_id is not None:
                tour_id=int(tour_id)
            if detail_id is not None:
                detail_id=int(detail_id)
            order_dec = service.get_requirements_admin(req_id,type,tour_id,detail_id)
            product_details = HttpResponse(order_dec.get(), content_type='application/json')
            return product_details
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ get_requirements_admin- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def accommodation_booking_admin(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.data.dict().get('data'))
            scope = request.scope
            booking_service = Booking_requirement(scope)
            prev_files = booking_service.fetch_tadoc(request, None, None, Travel_requirements.accomodation,
                                                     data['requirement_id'], 1)

            if "description" in json.loads(prev_files):
                if len(request.FILES) == 0 and json.loads(prev_files)['description'] == ErrorDescription.NO_FILE_TA:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.FILE_REQUIRED_BOOKING)
                    return HttpResponse(error_obj.get(), content_type='application/json')

            employee_id=request.employee_id
            requirment_service = AccomodationBooking_requirement(scope)
            logger.info('ta_ accommodation_booking_admin- ' + str(employee_id) + str(data))
            resp_obj = requirment_service.accomadation_data_admin(request,data,employee_id)
            response= HttpResponse(resp_obj.get(), content_type='application/json')
            return response
        elif request.method=='GET':
            scope = request.scope
            order_service = AccomodationBooking_requirement(scope)
            detail_id = request.GET.get('detail_id')
            tour_id = request.GET.get('tour_id')
            detail_array=[detail_id]
            page = request.GET.get('page', 1)
            page = int(page)
            vys_page = NWisefinPage(page, 10)
            all_report = request.GET.get('all_report')
            order_dec = order_service.fetch_accomadation_admin(detail_array,request,all_report,vys_page,tour_id)
            product_details = HttpResponse(order_dec.get(), content_type='application/json')
            return product_details
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ accommodation_booking_admin- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['DELETE','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def accommodation_details_admin(request,id):
    try:
        if request.method == 'DELETE':
            scope = request.scope
            service = AccomodationBooking_requirement(scope)
            resp_obj = service.accomadation_delete_admin(id)
            return HttpResponse(resp_obj, content_type='application/json')
        elif request.method == 'GET':
            scope = request.scope
            service = AccomodationBooking_requirement(scope)
            order_dec = service.get_accomadation_admin(id)
            product_details = HttpResponse(order_dec.get(), content_type='application/json')
            return product_details
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ accommodation_details_admin- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def air_booking_admin(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.data.dict().get('data'))
            scope = request.scope
            booking_service = Booking_requirement(scope)
            prev_files = booking_service.fetch_tadoc(request, None, None, Travel_requirements.air,
                                                     data['requirement_id'], 1)

            if "description" in json.loads(prev_files):
                if len(request.FILES) == 0 and json.loads(prev_files)['description'] == ErrorDescription.NO_FILE_TA:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.FILE_REQUIRED_BOOKING)
                    return HttpResponse(error_obj.get(), content_type='application/json')
            employee_id=request.employee_id
            requirment_service = Air_requirement(scope)
            logger.info('ta_ air_booking_admin- ' + str(employee_id) + str(data))
            resp_obj = requirment_service.Air_data_admin(request,data,employee_id)
            response= HttpResponse(resp_obj.get(), content_type='application/json')
            return response
        elif request.method=='GET':
            scope = request.scope
            order_service = Air_requirement(scope)
            detail_id = request.GET.get('detail_id')
            tour_id = request.GET.get('tour_id')
            page = request.GET.get('page', 1)
            page = int(page)
            vys_page = NWisefinPage(page, 10)
            all_report = request.GET.get('all_report')
            order_dec = order_service.fetch_Air_admin(detail_id,request,all_report,vys_page,tour_id)
            product_details = HttpResponse(order_dec.get(), content_type='application/json')
            return product_details
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ air_booking_admin- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['DELETE','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def air_details_admin(request,id):
    try:
        if request.method == 'DELETE':
            scope = request.scope
            state_service = Air_requirement(scope)
            resp_obj = state_service.Air_delete_admin(id)
            return HttpResponse(resp_obj, content_type='application/json')
        elif request.method == 'GET':
            scope = request.scope
            order_service = Air_requirement(scope)
            order_dec = order_service.get_Air_admin(id)
            product_details = HttpResponse(order_dec.get(), content_type='application/json')
            return product_details
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ air_details_admin- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def train_booking_admin(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.data.dict().get('data'))
            scope = request.scope
            booking_service = Booking_requirement(scope)
            prev_files = booking_service.fetch_tadoc(request, None, None, Travel_requirements.train,
                                                     data['requirement_id'], 1)

            if "description" in json.loads(prev_files):
                if len(request.FILES) == 0 and json.loads(prev_files)['description'] == ErrorDescription.NO_FILE_TA:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.FILE_REQUIRED_BOOKING)
                    return HttpResponse(error_obj.get(), content_type='application/json')
            employee_id=request.employee_id
            requirment_service = Train_requirement(scope)
            logger.info('ta_ train_booking_admin- ' + str(employee_id) + str(data))
            resp_obj = requirment_service.Train_data_admin(request,data,employee_id)
            response= HttpResponse(resp_obj.get(), content_type='application/json')
            return response
        elif request.method=='GET':
            scope = request.scope
            order_service = Train_requirement(scope)
            detail_id = request.GET.get('detail_id')
            tour_id = request.GET.get('tour_id')
            page = request.GET.get('page', 1)
            page = int(page)
            vys_page = NWisefinPage(page, 10)
            all_report = request.GET.get('all_report')
            order_dec = order_service.fetch_Train_admin(detail_id,request,all_report,vys_page,tour_id)
            product_details = HttpResponse(order_dec.get(), content_type='application/json')
            return product_details
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ train_booking_admin- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['DELETE','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def train_details_admin(request,id):
    try:
        if request.method == 'DELETE':
            scope = request.scope
            state_service = Train_requirement(scope)
            resp_obj = state_service.train_delete_admin(id)
            return HttpResponse(resp_obj, content_type='application/json')
        elif request.method == 'GET':
            scope = request.scope
            order_service = Train_requirement(scope)
            order_dec = order_service.get_Train_admin(id)
            product_details = HttpResponse(order_dec.get(), content_type='application/json')
            return product_details
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ train_details_admin- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def short_term_travel(request):
    try:
        if request.method == 'GET':
            page = request.GET.get('page', 1)
            page = int(page)
            vys_page = NWisefinPage(page, 10)
            scope = request.scope
            Tour_service = TourMaker(scope)
            employee_id = request.employee_id
            onb = request.GET.get('onbehalf', 0)
            request_date = request.GET.get('request_date', '')
            tour_no = request.GET.get('tour_no', '')
            travel_ser = TourMaker(scope)
            order_dec = travel_ser.short_term_travel(vys_page,request_date,tour_no,request)
            resp_obj = HttpResponse(order_dec.get(), content_type='application/json')
            return resp_obj
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ short_term_travel- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def delete_travel_requirements(request):
    try:
        if request.method == 'DELETE':
            scope = request.scope
            employee_id = request.employee_id
            id = request.GET.get('id')
            type = request.GET.get('type')
            tour_service = AccomodationBooking_requirement(scope)
            delete_req = tour_service.delete_travel_requirements(int(type),int(id),employee_id,request)
            resp_obj = HttpResponse(delete_req.get(), content_type='application/json')
            return resp_obj
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ delete_travel_requirements- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def daterelaxation_popup(request):
    if request.method == 'GET':
        data = json.loads(request.body)
        scope = request.scope
        employee_id=request.employee_id
        travel_maker=TourMaker(scope)
        # start_date=request.GET.get("start_date")
        # end_date=request.GET.get("end_date")
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)


        resp_obj = travel_maker.daterelaxation_popup(request,vys_page)
        response= HttpResponse(resp_obj.get(), content_type='application/json')
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def popup_nine_days(request):
    if request.method == 'GET':
        data = json.loads(request.body)
        scope = request.scope
        employee_id=request.employee_id
        travel_maker=TourMaker(scope)
        # start_date=request.GET.get("start_date")
        # end_date=request.GET.get("end_date")
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)


        resp_obj = travel_maker.popup_nine_days(request,vys_page)
        response= HttpResponse(resp_obj.get(), content_type='application/json')
        return response

@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def client_insert(request):
    if request.method == 'GET':
        try:
            # data = json.loads(request.body)
            scope = request.scope
            # employee_id=request.employee_id
            travel_maker=TourMaker(scope)
            # start_date=request.GET.get("start_date")
            # end_date=request.GET.get("end_date")
            page = request.GET.get('page', 1)
            page = int(page)
            vys_page = NWisefinPage(page, 10)
            resp_obj = travel_maker.fetch_client(request,vys_page)
            response= HttpResponse(resp_obj.get(), content_type='application/json')
            return response
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            scope = request.scope
            employee_id=request.employee_id
            travel_maker=TourMaker(scope)
            resp_obj = travel_maker.insert_client(data,employee_id)
            response= HttpResponse(resp_obj.get(), content_type='application/json')
            return response
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj
@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_client(request,id):
    if request.method == 'GET':
        try:
            data = json.loads(request.body)
            scope = request.scope
            employee_id=request.employee_id
            travel_maker=TourMaker(scope)
            resp_obj = travel_maker.get_client(request,id)
            response= HttpResponse(resp_obj.get(), content_type='application/json')
            return response
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj
    if request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            scope = request.scope
            employee_id=request.employee_id
            travel_maker=TourMaker(scope)
            resp_obj = travel_maker.delete_client(request,id)
            response= HttpResponse(resp_obj.get(), content_type='application/json')
            return response
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def personal_official(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            employee_id = request.employee_id
            scope = request.scope
            travel_maker=TourMaker(scope)
            resp_obj = travel_maker.personal_official(data,employee_id)
            response= HttpResponse(resp_obj.get(), content_type='application/json')
            return response
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ personal_official- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def no_show(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            employee_id = request.employee_id
            scope = request.scope
            travel_maker=TourMaker(scope)
            resp_obj = travel_maker.no_show(data,employee_id)
            response= HttpResponse(resp_obj.get(), content_type='application/json')
            return response
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ no_show- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def admin_reserv(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            employee_id = request.employee_id
            scope = request.scope
            travel_maker=Admin(scope)
            resp_obj = travel_maker.admin_reserv(data,employee_id)
            response= HttpResponse(resp_obj.get(), content_type='application/json')
            return response
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ admin_reserv- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_emp_rm(request):
    try:
        if request.method == 'GET':
            employee_id = request.employee_id
            scope = request.scope
            onbehalf = request.GET.get('onbehalf', employee_id)
            travel_maker=ApiService(scope)
            rm_id = travel_maker.get_RM_ID(request,onbehalf)
            resp_obj = travel_maker.employee_details_get(rm_id,request)
            response= HttpResponse(resp_obj.get(), content_type='application/json')
            return response
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ get_emp_rm- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_emp_fm(request):
    try:
        if request.method == 'GET':
            employee_id = request.employee_id
            scope = request.scope
            onbehalf = request.GET.get('onbehalf', employee_id)
            travel_maker=ApiService(scope)
            fm_id = travel_maker.get_functional_head(request,onbehalf)
            resp_obj = travel_maker.employee_details_get(fm_id['Fictional_head'],request)
            response= HttpResponse(resp_obj.get(), content_type='application/json')
            return response
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ get_emp_fm- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

# @csrf_exempt
# @api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def eligible_amount_popup(request):
#     if request.method == 'GET':
#         try:
#             data = json.loads(request.body)
#             scope = request.scope
#             employee_id=request.employee_id
#             travel_maker=TourMaker(scope)
#             claim_amount = request.GET.get('cliam_amount')
#             eligible_amount = request.GET.get('eligible_amount')
#
#             resp_obj = travel_maker.amount_popup(claim_amount,eligible_amount)
#             response= HttpResponse(resp_obj.get(), content_type='application/json')
#             return response
#         except Exception as e:
#             error_obj = NWisefinError()
#             error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#             error_obj.set_description(str(e))
#             return error_obj
@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def cancel_booking_request(request):
    try:

        if request.method == 'POST':
            # userdata = json.loads(request.body)
            # data = json.loads(request.body)
            # obj = Cab_request(data)
            # user_id = request.user.id
            scope = request.scope
            employee_id=request.employee_id
            booking_type=request.GET.get('booking_type')
            requirement_id=request.GET.get('requirement_id')
            requirment_service = Booking_requirement(scope)

            # Tour_service = Approve_list(scope)
            resp_obj = requirment_service.cancel_request(booking_type,requirement_id,employee_id)
            response= HttpResponse(resp_obj.get(), content_type='application/json')
            return response
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ cancel_booking_request- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def req_cancel_approve(request):
    try:

        if request.method == 'POST':
            # userdata = json.loads(request.body)
            data = json.loads(request.data.dict().get('data'))
            # obj = Cab_request(data)
            # user_id = request.user.id
            scope = request.scope
            employee_id=request.employee_id
            requirment_service = Booking_requirement(scope)
            # booking_type = request.GET.get('booking_type')
            # requirement_id = request.GET.get('requirement_id')

            # Tour_service = Approve_list(scope)
            resp_obj = requirment_service.cancel_approve(data)
            response= HttpResponse(resp_obj.get(), content_type='application/json')
            return response
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ req_cancel_approve- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def requirement_reject(request):
    try:

        if request.method == 'POST':
            userdata = json.loads(request.body)
            scope = request.scope
            employee_id=request.employee_id
            requirment_service = Booking_requirement(scope)

            data = No_show_req(userdata)
            resp_obj = requirment_service.reject_requirement(data)
            response= HttpResponse(resp_obj.get(), content_type='application/json')
            return response
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ req_cancel_approve- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employee_base_get(request):
    try:

        if request.method == 'GET':
            scope = request.scope
            employee_id=request.employee_id
            requirment_service = Booking_requirement(scope)
            employee_id= request.GET.get("onbehalf",employee_id)

            # Tour_service = Approve_list(scope)
            resp_obj = requirment_service.employeeid_city(employee_id,request)
            response= HttpResponse(resp_obj.get(), content_type='application/json')
            return response
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ employee_base_get- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def city_dropdown(request):
    try:
        if request.method == 'GET':
            scope = request.scope
            employee_id=request.employee_id
            maker_service = TourMaker(scope)
            city_name = request.GET.get('city_name',None)
            page = request.GET.get('page', 1)
            page = int(page)
            vys_page = NWisefinPage(page, 10)
            resp_obj = maker_service.city_dropdown(request,city_name,vys_page)
            response= HttpResponse(resp_obj.get(), content_type='application/json')
            return response
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ city_dropdown- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')
# @csrf_exempt
# @api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def money_conversion(request):
#     try:
#         if request.method == 'GET':
#             scope = request.scope
#             employee_id=request.employee_id
#             maker_service = TourMaker(scope)
#             # city_name = request.GET.get('city_name',None)
#             page = request.GET.get('page', 1)
#             page = int(page)
#             vys_page = NWisefinPage(page, 10)
#             amount=request.GET.get("amount")
#             resp_obj = maker_service.money_conversion(request,amount)
#             response= HttpResponse(resp_obj, content_type='application/json')
#             return response
#     except Exception as e:
#         error_obj = NWisefinError()
#         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#         error_obj.set_description(str(e))
#         logger.info('ta_ employee_base_get- ' + str(e))
#         return HttpResponse(error_obj.get(), content_type='application/json')
#


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def state_dropdown(request):
    try:
        if request.method == 'GET':
            scope = request.scope
            city_get = TourMaker(scope)
            city_name = request.GET.get('state_name', None)
            page = request.GET.get('page', 1)
            page = int(page)
            vys_page = NWisefinPage(page, 10)

            city_filter = city_get.state_dropdown(request, city_name, vys_page)
            response = HttpResponse(city_filter.get(), content_type='application/json')
            return response
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ city_dropdown- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def citytype_dropdown(request):
    try:
        if request.method == 'GET':
            scope = request.scope
            city_get = TourMaker(scope)
            city_name = request.GET.get('state_name', None)
            page = request.GET.get('page', 1)
            page = int(page)
            vys_page = NWisefinPage(page, 10)

            city_filter = city_get.citytype_dropdown(request, city_name, vys_page)
            response = HttpResponse(city_filter.get(), content_type='application/json')
            return response
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ city_dropdown- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def branch_dropdown(request):
    try:
        if request.method == 'GET':
            scope = request.scope
            city_get = TourMaker(scope)
            branch = request.GET.get('branch', None)
            page = request.GET.get('page', 1)
            page = int(page)
            vys_page = NWisefinPage(page, 10)

            city_filter = city_get.branch_dropdown(request, branch, vys_page)
            response = HttpResponse(city_filter.get(), content_type='application/json')
            return response
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ city_dropdown- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def city_delete(request,id):
    try:
        if request.method == 'DELETE':
            scope = request.scope
            city_get = TourMaker(scope)

            city_filter = city_get.city_delete(request, id)
            response = HttpResponse(city_filter.get(), content_type='application/json')
            return response
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ city_dropdown- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def tourreason_delete(request,id):
    try:
        if request.method == 'DELETE':
            scope = request.scope
            city_get = TourMaker(scope)

            city_filter = city_get.tourreason_delete(request, id)
            response = HttpResponse(city_filter.get(), content_type='application/json')
            return response
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ city_dropdown- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def tourexpense_delete(request,id):
    try:
        if request.method == 'DELETE':
            scope = request.scope
            city_get = TourMaker(scope)

            city_filter = city_get.expense_delete(request, id)
            response = HttpResponse(city_filter.get(), content_type='application/json')
            return response
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ city_dropdown- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

# @csrf_exempt
# @api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def money_conversion(request):
#     try:
#         if request.method == 'GET':
#             scope = request.scope
#             employee_id=request.employee_id
#             maker_service = TourMaker(scope)
#             # city_name = request.GET.get('city_name',None)
#             page = request.GET.get('page', 1)
#             page = int(page)
#             vys_page = NWisefinPage(page, 10)
#             amount=request.GET.get("amount")
#             resp_obj = maker_service.money_conversion(request,amount)
#             response= HttpResponse(resp_obj, content_type='application/json')
#             return response
#     except Exception as e:
#         error_obj = NWisefinError()
#         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
#         error_obj.set_description(str(e))
#         logger.info('ta_ employee_base_get- ' + str(e))
#         return HttpResponse(error_obj.get(), content_type='application/json')
#
#

@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def insert_ta_city(request):
    try:

        if request.method == 'POST':
            userdata = json.loads(request.body)
            scope = request.scope
            employee_id=request.employee_id
            city_insert = TourMaker(scope)
            data=json.loads(request.body)

            # data = No_show_req(userdata)
            resp_obj = city_insert.city_insert(request,data,employee_id)
            response= HttpResponse(resp_obj.get(), content_type='application/json')
            return response
        if request.method == 'GET':
            scope = request.scope
            city_get = TourMaker(scope)
            city_name = request.GET.get('city_name', None)
            page = request.GET.get('page', 1)
            page = int(page)
            vys_page = NWisefinPage(page, 10)

            city_filter=city_get.city_get(request,city_name,vys_page)
            response = HttpResponse(city_filter.get(), content_type='application/json')
            return response
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ city_dropdown- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def city_file(request):
    try:
        if request.method == 'POST':
            file_name = request.FILES.getlist('file')[0].name
            scope = request.scope
            budget_service=TourMaker(scope)
            employee_id = request.employee_id
            import pandas as pd
            import numpy as np
            excel_data = pd.read_excel(request.FILES['file'], engine='openpyxl')
            df = pd.DataFrame(excel_data)
            transation_obj = df.fillna(np.nan).replace([np.nan], [0]).to_dict(orient='records')
            resp_obj = budget_service.city_file(transation_obj,employee_id)
            response = HttpResponse(resp_obj.get(), content_type='application/json')
            return response
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ city_dropdown- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def tour_expense(request):
    try:

        if request.method == 'POST':
            userdata = json.loads(request.body)
            scope = request.scope
            employee_id=request.employee_id
            city_insert = TourMaker(scope)
            data=json.loads(request.body)

            # data = No_show_req(userdata)
            resp_obj = city_insert.tour_expense_insert(request,data,employee_id)
            response= HttpResponse(resp_obj.get(), content_type='application/json')
            return response
        if request.method == 'GET':
            scope = request.scope
            city_get = TourMaker(scope)
            city_name = request.GET.get('expense')
            page = request.GET.get('page', 1)
            page = int(page)
            vys_page = NWisefinPage(page, 10)

            city_filter=city_get.tour_expense_get(request,city_name,vys_page)
            response = HttpResponse(city_filter.get(), content_type='application/json')
            return response
    except Exception as e:
        exc=traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ city_dropdown- ' + str(e)+str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def frequent_city(request):
    try:
        if request.method == 'GET':
            city_name = request.GET.get('city_name', None)
            page = request.GET.get('page', 1)
            from_place = request.GET.get('from_place',1)
            page = int(page)
            vys_page = NWisefinPage(page, 10)
            scope = request.scope
            travel = TourMaker(scope)
            employee_id = request.employee_id
            employee = request.GET.get('employee', employee_id)
            data = travel.frequent_city_2(request,employee,vys_page,from_place,city_name)
            response = HttpResponse(json.dumps(data, default=lambda o: o.__dict__), content_type='application/json')
            return response
    except Exception as e:
        exc = traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ frequent_city- ' + str(e) + str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def frequent_client(request):
    try:
        if request.method == 'GET':
            query = request.GET.get('query', None)
            page = request.GET.get('page', 1)
            page = int(page)
            vys_page = NWisefinPage(page, 10)
            scope = request.scope
            travel = TourMaker(scope)
            employee_id = request.employee_id
            employee = request.GET.get('employee', employee_id)
            data = travel.frequent_client_2(request,employee,vys_page,query)
            response = HttpResponse(json.dumps(data, default=lambda o: o.__dict__), content_type='application/json')
            return response
    except Exception as e:
        exc = traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ frequent_client- ' + str(e) + str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def frequent_data_insert(request):
    try:
        if request.method == 'POST':
            scope = request.scope
            travel = TourMaker(scope)
            data = travel.frequent_data_insert()
            response = HttpResponse(data.get(), content_type='application/json')
            return response
    except Exception as e:
        exc = traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ frequent_client- ' + str(e) + str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def team_update(request):
    try:
        if request.method == 'GET':
            scope = request.scope
            travel = TourMaker(scope)
            data = travel.team_update()
            response = HttpResponse(data.get(), content_type='application/json')
            return response
    except Exception as e:
        exc = traceback.format_exc()
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        logger.info('ta_ frequent_client- ' + str(e) + str(exc))
        return HttpResponse(error_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def edit_history(request,id):
    if request.method == 'GET':
        try:
            scope = request.scope
            travel_maker=TourMaker(scope)
            action = request.GET.get('action',1)
            resp_obj = travel_maker.edit_history_get(id,int(action))
            response= HttpResponse(resp_obj.get(), content_type='application/json')
            return response
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj

@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def edited_difference(request,id):
    if request.method == 'GET':
        try:
            scope = request.scope
            travel_maker=TourMaker(scope)
            action = request.GET.get('action',1)
            dict1 = travel_maker.edit_history_get(id,int(action))
            dict1 = json.dumps(dict1.data[0].history_data, default=lambda o: o.__dict__)

            tour_data = travel_maker.get_tour(id, request)
            dict2 = json.dumps(tour_data, default=lambda o: o.__dict__)

            diff = set(dict2) - set(dict1)
            if len(diff)==0:
                diff=None
            response= HttpResponse(diff, content_type='application/json')
            return response
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj
