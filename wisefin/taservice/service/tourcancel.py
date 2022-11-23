import json
from datetime import datetime

import pytz
from django.db import  IntegrityError
from django.db import transaction
# from taservice.service.emp_name_get import emp_dtl
from taservice.service.ta_email import ta_email
from taservice.util.ta_util import Status, status_get, App_level, App_type, Timecalculation, Admin
from taservice.data.response.tourmaker import TourMaker
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess,SuccessStatus,SuccessMessage
from taservice.models.tamodels import TourCancel, TourRequest, TravelHistory, TourAdvance
from taservice.service.tourapprovedby import TourApprovedby
from django.utils import timezone
from utilityservice.data.response.nwisefinlist  import NWisefinList
from utilityservice.data.response.nwisefinpaginator  import NWisefinPaginator
# from utilityservice.service.dbutil import DataBase

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.ta_api_service import ApiService
# IST = pytz.timezone('Asia/Kolkata')
# datetime_ist = datetime.now(IST)
# today = datetime_ist.strftime('%Y-%m-%d %H:%M:%S')
#
# today_date=datetime.strptime((today[:10]), '%Y-%m-%d').date()
# today_std=datetime.today()

time_function=Timecalculation()

from utilityservice.service.threadlocal import NWisefinThread
@transaction.atomic
class Canceltour(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)
    @transaction.atomic
    def cancel_tour(self,request_obj, user_id,request):
        if request_obj.get_id() is not None:
            # try:
            # Tourcanceldata = TourCancel.objects.using(self._current_app_schema()).filter(id=request_obj.get_id()).update(type=request_obj.get_apptype(),
            #                                                                     status=request_obj.get_status(),
            #                                                                     updated_by=user_id,
            #                                                                     updated_date=timezone.now)


            # except Exception as e:
            #     print(e)
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(str(e))
            #     return error_obj
            # except IntegrityError as error:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except TourRequest.DoesNotExist:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            #     error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
            #     return error_obj
            # except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj
            # success_obj = Success()
            # success_obj.set_status(SuccessStatus.SUCCESS)
            # success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            # return success_obj
        else:
            # try:

            tour_id = request_obj.tour_id
            onbehalfof = request_obj.onbehalfof
            approval = request_obj.approval
            appcomment = request_obj.appcomment
            if appcomment is None or appcomment == "":
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.COMMENT)
                return error_obj
            apptype = request_obj.apptype
            if apptype.upper()=="TOURCANCEL":
                apptype=App_type.TourCancel
            # elif apptype.upper()=="ADVANCECANCEL":
            #     apptype=App_type.AdvanceCancel
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.APPTYPE)
                return error_obj

            tour_data = TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id,entity_id=self._entity_id())[0]

            # if tour_data.claim_status==Status.REQUESTED or tour_data.claim_status==Status.PENDING or \
            #         tour_data.claim_status==Status.APPROVED or tour_data.claim_status==Status.RETURNED :
            if tour_data.claim_status!=Status.DEFAULT:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.EXPENSE_CANCEL)
                return error_obj


            if onbehalfof >0:
                if onbehalfof != tour_data.empgid:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.IN_VALID_ONB)
                    return error_obj
                if int(onbehalfof) == user_id:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.IN_VALID_ONB)
                    return error_obj
                tour_emp=onbehalfof
                request_obj.onbehalfof=user_id
            else:
                tour_emp=user_id
                if tour_emp != tour_data.empgid:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_MAKER)
                    return error_obj


            # tour_data=TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id)[0]
            error_obj = NWisefinError()
            # if tour_data.start_date.date()<datetime.today().date():
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.TOUR_NOT_APPROVED)
            #     return error_obj

            if apptype==App_type.TourCancel:
                tour_status=tour_data.tour_status
                if tour_status!=Status.APPROVED:
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.TOUR_NOT_APPROVED)
                    return error_obj
                if tour_data.tour_cancel_status!=Status.DEFAULT:
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.CANT_CANCEL)
                    return error_obj
                can_status_check=[Status.PENDING,Status.APPROVED]
                # prev_cancel=TravelHistory.objects.using(self._current_app_schema()).filter(apptype=App_type.AdvanceCancel,
                #                                                                            status__in=can_status_check, tour_id=tour_id, entity_id=self._entity_id())
                # if len(prev_cancel)!=0:
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.CANT_CANCEL)
                #     return error_obj



            # if apptype==App_type.AdvanceCancel:
            #     advance_status=tour_data.advance_status
            #     approved_advance=TourAdvance.objects.using(self._current_app_schema()).filter(tour_id=tour_id,status=Status.APPROVED,entity_id=self._entity_id())
            #     if len(approved_advance)==0:
            #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #         error_obj.set_description(ErrorDescription.ADVANCE_NOT_APPROVED)
            #         return error_obj
            #     if tour_data.advance_cancel_status!=Status.DEFAULT:
            #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #         error_obj.set_description(ErrorDescription.CANT_CANCEL)
            #         return error_obj
            #     # can_status_check = [Status.PENDING, Status.APPROVED]
            #     # prev_cancel = TravelHistory.objects.using(self._current_app_schema()).filter(apptype=App_type.TourCancel,
            #     #                                                                              status__in=can_status_check,
            #     #                                                                              tour_id=tour_id, entity_id=self._entity_id())
            #     if len(prev_cancel) != 0:
            #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #         error_obj.set_description(ErrorDescription.CANT_CANCEL)
            #         return error_obj
            #
            # pre_cancel=TourCancel.objects.using(self._current_app_schema()).filter(tour_id=tour_id,type=apptype,entity_id=self._entity_id())
            # if len(pre_cancel)!=0:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.CANT_CANCEL)
            #     return error_obj

            api_service = ApiService(self._scope())
            rm_get = api_service.get_RM_ID(request, tour_emp)
            if rm_get == None:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_RM)
                return error_obj
            with transaction.atomic():
                Tourcanceldata = TourCancel.objects.using(self._current_app_schema()).create(tour_id=tour_id,
                                                           type=apptype,
                                                           status=1,
                                                           created_by=tour_emp,entity_id=self._entity_id())


            data = {   "tourgid":tour_id,
                        "approvedby":user_id,
                        "onbehalfof":request_obj.onbehalfof,
                        "approveddate":time_function.ist_time(),
                        "apptype":apptype,
                        "applevel":App_level.ZERO_LEVEL,
                        "appcomment":appcomment,
                        "status": Status.REQUESTED}


            req = TourApprovedby.insert_approvedby(self,data,request)
            req_status =json.loads(req.get())
            if req_status.get('status') == "success":
                    data = {"tourgid": tour_id,
                            #ADMIN
                            "approvedby":rm_get,
                            "onbehalfof": "0",
                            "approveddate": time_function.ist_time(),
                            "apptype": apptype,
                            "applevel": App_level.FIRST_LEVEL,
                            "appcomment": "",
                            "status": Status.PENDING}

                    approve = TourApprovedby.insert_approvedby(self,data,request)
                    e = json.loads(approve.get())

                    mail_service = ta_email(self._scope())
                    mail_service.mail_data(tour_id)
                    # if e.get('status') == "success":
                    #     transaction.on_commit(TourCancel)
                    # else:
                    return approve
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(str(req_status))
                return error_obj


            # except Exception as e:
            #     print(e)
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(str(e))
            #     return error_obj


    def cancelled_data(self,type,employee_id,onb, vys_page,request_date,tour_no,request):
        if request_date != "":
            try:
                request_date = int(request_date)
                request_date = str(datetime.fromtimestamp(int(request_date) / 1000.0))
                request_date = (datetime.strptime(request_date[:10], '%Y-%m-%d')).date()
            except:
                request_date = (datetime.strptime(request_date, '%d-%b-%Y')).date()
        can_sts=[Status.PENDING,Status.APPROVED,Status.REJECTED]
        if type==App_type.TourCancel:
            if onb is None:
                Tour = TourRequest.objects.using(self._current_app_schema()).filter(empgid=employee_id, tour_cancel_status__in=can_sts,
                                                                        request_date__icontains=request_date,id__icontains=tour_no,entity_id=self._entity_id()).all().order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
            elif int(onb) == 0:
                Tour = TourRequest.objects.using(self._current_app_schema()).filter(onbehalfof=employee_id,tour_cancel_status__in=can_sts,
                                                                        request_date__icontains=request_date,id__icontains=tour_no,entity_id=self._entity_id()).all().order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
            else:
                Tour = TourRequest.objects.using(self._current_app_schema()).filter(empgid=onb,onbehalfof=employee_id,tour_cancel_status__in=can_sts,
                                                                        request_date__icontains=request_date,id__icontains=tour_no,entity_id=self._entity_id()).all().order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        # elif type==App_type.AdvanceCancel:
        #     if int(onb) > 0:
        #         Tour = TourRequest.objects.using(self._current_app_schema()).filter(empgid=onb, onbehalfof=employee_id,advance_cancel_status__in=can_sts,
        #                                                                 request_date__icontains=request_date,id__icontains=tour_no,entity_id=self._entity_id()).all().order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        #     else:
        #         Tour = TourRequest.objects.using(self._current_app_schema()).filter(empgid=employee_id,advance_cancel_status__in=can_sts,
        #                                                                 request_date__icontains=request_date,id__icontains=tour_no,entity_id=self._entity_id()).all().order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]

        resp_list =NWisefinList()
        if len(Tour)>0:
            for tour in Tour:
                req_data = TourMaker()
                req_data.set_id(tour.id)
                req_data.set_type(type)
                req_data.set_tourgid(tour.id)
                # req_data.set_requestno(tour.requestno)
                req_data.set_requestdate(tour.request_date)
                req_data.set_empgid(tour.empgid)
                empdtl = ApiService(self._scope())
                employee = empdtl.employee_details_get(tour.empgid,request)
                req_data.set_employee_name(employee.full_name)
                # code = empdtl.employee_code_get(tour.empgid)
                req_data.set_employee_code(employee.code)
                req_data.set_empdesignation(tour.empdesignation)
                req_data.set_empgrade(tour.empgrade)
                req_data.set_empbranchgid(tour.empbranchgid)

                branch = empdtl.get_branch_data(tour.empbranchgid,request)
                req_data.set_branch_name(branch.name)

                if tour.onbehalfof > 0:
                    onbehalf = empdtl.employee_details_get(tour.onbehalfof,request)
                    req_data.set_onbehalfof(onbehalf.full_name)
                tour_status = status_get(tour.tour_status)
                # advance_status = status_get(tour.advance_status)
                claim_status = status_get(tour.claim_status)
                tour_cancel_status = status_get(tour.tour_cancel_status)
                # advance_cancel_status = status_get(tour.advance_cancel_status)

                req_data.set_tour_status(tour_status)
                # req_data.set_advance_status(advance_status)
                req_data.set_claim_status(claim_status)
                req_data.set_tour_cancel_status(tour_cancel_status)
                # req_data.set_advance_cancel_status(advance_cancel_status)

                req_data.set_tour_status_id(tour.tour_status)
                # req_data.set_advance_status_id(tour.advance_status)
                req_data.set_claim_status_id(tour.claim_status)
                req_data.set_tour_cancel_status_id(tour.tour_cancel_status)
                # req_data.set_advance_cancel_status_id(tour.advance_cancel_status)

                tour_approver=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tour.id, applevel=App_level.FIRST_LEVEL, request_type=App_type.TOUR, entity_id=self._entity_id()).last()

                empdtl = ApiService(self._scope())
                tour_approved_by = empdtl.employee_details_get(tour_approver.approvedby,request)
                req_data.set_tour_approvedby(tour_approved_by)
                req_data.set_approver_code(tour_approved_by.code)

                resp_list.append(req_data)
            vpage = NWisefinPaginator(Tour, vys_page.get_index(), 10)
            resp_list.set_pagination(vpage)
        return resp_list