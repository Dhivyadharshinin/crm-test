import json
from datetime import datetime

from utilityservice.data.response.nwisefinpaginator  import NWisefinPaginator
from django.http import HttpResponse
from taservice.data.request.Date_relaxation_req import Date_relaxation_req
from taservice.data.response.date_relaxatiion_resp import Date_relaxation_resp
from taservice.models import Date_relaxation, ClaimRequest, TADocuments, TourRequest as TourRequest_table, Ccbs, \
    InternationalTravel
from django.utils import timezone
from django.db import IntegrityError
from taservice.service.emp_name_get import emp_dtl
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
# from utilityservice.service.dbutil import DataBase
from taservice.util.ta_util import Status, Timecalculation, Validation
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.ta_api_service import ApiService

from utilityservice.service.threadlocal import NWisefinThread
time_function=Timecalculation()
class Date_relaxation_ser(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)
    def update_date_relaxation(self,request_obj,employee_id):
        for dtl in request_obj:

            data = Date_relaxation_req(dtl)
            # try:
            com=Date_relaxation.objects.using(self._current_app_schema()).filter(id=data.id, tour_id=data.tour_id,entity_id=self._entity_id()).update(
                    status=data.status,
                    updated_by=employee_id,
                    updated_date=timezone.now(),entity_id=self._entity_id())



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
            # except Date_relaxation.DoesNotExist:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            #     error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
            #     return error_obj
            # except:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj

    def approve_international_travel(self,request_obj,employee_id):
        for dtl in request_obj:

            data = Date_relaxation_req(dtl)
            # try:
            com=InternationalTravel.objects.using(self._current_app_schema()).filter(id=data.id, tour_id=data.tour_id,entity_id=self._entity_id()).update(
                    status=data.status,
                    updated_by=employee_id,
                    approved_by=employee_id,
                    comments=data.comments,
                    updated_date=timezone.now(),entity_id=self._entity_id())

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj

    def insure_international_travel(self,request_obj,employee_id):
        for dtl in request_obj:

            data = Date_relaxation_req(dtl)
            # try:
            com=InternationalTravel.objects.using(self._current_app_schema()).filter(id=data.id, tour_id=data.tour_id,entity_id=self._entity_id()).update(
                    insured=data.insured,
                    insurance_no=data.insurance_no,
                    updated_by=employee_id,
                    updated_date=timezone.now(),entity_id=self._entity_id())


        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj



    def get_date_relaxation(self,request,tour_no,vys_page):
        emp_id=request.employee_id
        api_service=ApiService(self._scope())
        emp_get=api_service.get_rm_emp(request,emp_id)
        module_permission = ApiService(self._scope())
        ceo_get = module_permission.onb_permission(request, emp_id)
        if tour_no is None:

            if (json.loads(ceo_get))["ceo"] != True:

                list=Date_relaxation.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour__empgid__in=emp_get).order_by("-id")[vys_page.get_offset():vys_page.get_query_limit()]
            else:
                list = Date_relaxation.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by(
                    "-id")[vys_page.get_offset():vys_page.get_query_limit()]
        else:
            if (json.loads(ceo_get))["ceo"] != True:

                list=Date_relaxation.objects.using(self._current_app_schema()).filter(tour__id__icontains=tour_no,entity_id=self._entity_id(),tour__empgid__in=emp_get).order_by("-id")[vys_page.get_offset():vys_page.get_query_limit()]
            else:
                list = Date_relaxation.objects.using(self._current_app_schema()).filter(tour__id__icontains=tour_no,entity_id=self._entity_id()).order_by(
                    "-id")[vys_page.get_offset():vys_page.get_query_limit()]
            # list=Date_relaxation.objects.using(self._current_app_schema()).filter(tour__id__icontains=tour_no,entity_id=self._entity_id(),tour__empgid__in=emp_get).order_by("-id")[vys_page.get_offset():vys_page.get_query_limit()]
        resp_list=NWisefinList()
        for data in list:
            details=emp_dtl(self._scope())
            empdtl = ApiService(self._scope())
            response=Date_relaxation_resp()
            response.set_id(data.id)
            response.set_tour_id(data.tour_id)
            # response.set_request_no(data.tour.requestno)
            response.set_request_date(data.tour.request_date)
            response.set_from_date(data.tour.start_date)
            response.set_to_date(data.tour.end_date)
            response.set_status(data.status)
            employee=empdtl.employee_details_get(data.tour.empgid,request)
            # empcode=details.employee_code_get(data.tour.empgid)
            reason_name=details.get_reason_name(data.tour.reason)
            response.set_employee_name(employee.full_name)
            response.set_employee_code(employee.code)
            response.set_reason(reason_name)
            response.set_reason_id(data.tour.reason)
            resp_list.append(response)
        vpage = NWisefinPaginator(list, vys_page.get_index(), 10)
        resp_list.set_pagination(vpage)
        return resp_list

    def get_international_travel(self,request,tour_no,vys_page):
        if tour_no is None:
            list=InternationalTravel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by("-id")[vys_page.get_offset():vys_page.get_query_limit()]
        else:
            list=InternationalTravel.objects.using(self._current_app_schema()).filter(tour__id__icontains=tour_no,entity_id=self._entity_id()).order_by("-id")[vys_page.get_offset():vys_page.get_query_limit()]
        resp_list=NWisefinList()
        for data in list:
            details=emp_dtl(self._scope())
            empdtl = ApiService(self._scope())
            response=Date_relaxation_resp()
            response.set_id(data.id)
            response.set_tour_id(data.tour_id)
            # response.set_request_no(data.tour.requestno)
            response.set_approved_date(data.approved_date)
            response.set_insured(data.insured)
            response.set_insurance_no(data.insurance_no)
            response.set_comments(data.comments)
            response.set_status(data.status)
            employee=empdtl.employee_details_get(data.approved_by,request)
            # empcode=details.employee_code_get(data.tour.empgid)
            reason_name=details.get_reason_name(data.tour.reason)
            response.set_approved_by(employee)
            response.set_reason(reason_name)
            response.set_reason_id(data.tour.reason)
            resp_list.append(response)
        vpage = NWisefinPaginator(list, vys_page.get_index(), 10)
        resp_list.set_pagination(vpage)
        return resp_list


    def fetch_date_relaxation(self,fetch_id):

        data = Date_relaxation.objects.using(self._current_app_schema()).get(id=fetch_id,entity_id=self._entity_id())
        response = Date_relaxation_resp()
        response.set_id(data.id)
        response.set_tour_id(data.tour_id)
        response.set_status(data.status)
        return response

    def fetch_date_relaxation_get(self,tour_id):

        data = Date_relaxation.objects.using(self._current_app_schema()).filter(tour_id=tour_id,entity_id=self._entity_id()).order_by("-id")
        if len(data)==0:
            return True
        if data[0].status==0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.DATE_RELAXATION)
            return error_obj
        else:
            return bool (data[0].status)
        
    def expense_movetoapprover_vali(self,request,expensedata):
        error_obj = NWisefinError()
        claim_check = ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=expensedata['tourgid'], status=1,entity_id=self._entity_id())
        if len(claim_check) == 0:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.NO_CLAIM)
            return error_obj
        claim_file_check = ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=expensedata['tourgid'],
                                                                             expensegid__in=[2, 5, 7], status=1,entity_id=self._entity_id())
        service = Date_relaxation_ser(self._scope())
        if len(claim_file_check) != 0 and len(request.FILES) == 0:
            tour_files = TADocuments.objects.using(self._current_app_schema()).filter(request_id=expensedata['tourgid'], status=1,entity_id=self._entity_id())
            
        

        tour_details = TourRequest_table.objects.using(self._current_app_schema()).get(id=expensedata['tourgid'],entity_id=self._entity_id())
        if tour_details.tour_status != Status.APPROVED:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.TOUR_NOT_APPROVED)
            return error_obj
        # if tour_details.advance_status == Status.PENDING:
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.ADVANCE_PENDING)
        #     return error_obj
        if tour_details.claim_status == Status.DEFAULT or tour_details.claim_status == Status.APPROVED or \
                tour_details.claim_status == Status.REJECTED or tour_details.claim_status == Status.FORWARDED or \
                tour_details.claim_status == Status.PENDING:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.CLAIM_APPROVER_ERROR)
            return error_obj
        if (tour_details.end_date).date() >= datetime.today().date():
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.TOUR_END_DATE)
            return error_obj


    def get_file_id(self,file_id):
        doc_obj = TADocuments.objects.using(self._current_app_schema()).get(file_id=file_id,entity_id=self._entity_id())
        return doc_obj


    def ccbs_vali_con(self,tourgid,userdata):
        tour_req_claim_status = TourRequest_table.objects.using(self._current_app_schema()).filter(id=tourgid,entity_id=self._entity_id())[0].claim_status
        if tour_req_claim_status != Status.RETURNED:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.CANT_EDIT)
            return error_obj
        val_service = Validation(self._scope())
        ccbs_validation = val_service.ccbs_validation("EXP", userdata, userdata[0]['tourgid'])
        if ccbs_validation != True:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.AMOUNT_ERROR)
            return error_obj
        del_prev_ccbs = Ccbs.objects.using(self._current_app_schema()).filter(tour_id=userdata[0]['tourgid'], requestid=0,entity_id=self._entity_id()).update(
            status=0)
