import datetime
import json
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.db.models.query import QuerySet
import requests


from taservice.data.request.onbehalfrequest import Onbehalfrequest
from taservice.data.response.tourmaker import TourMaker
from taservice.service.emp_name_get import emp_dtl
from taservice.service.onbehalf import Onbehalf_service
# from userservice.models import Employee
# from userservice.controller.authcontroller import get_authtoken
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants  import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from taservice.models.tamodels import TourRequest, TourAdvance as AdvanceTable, TourDetail, TravelHistory, Ccbs
from taservice.data.response.touradvance import TourAdvanceResponse
from taservice.data.request.touradvance import TourAdvanceRequest, Advance_Request
from taservice.service.tourapprovedby import TourApprovedby
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from taservice.util.ta_util import App_level, Status, Filterapptype, Filterapplevel, Ccbs_utils, status_get, App_type, \
    adv_status_get, Validation, Timecalculation
from datetime import datetime
import pytz
from utilityservice.data.response.nwisefinpaginator  import NWisefinPaginator
# from utilityservice.service.dbutil import DataBase

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.ta_api_service import ApiService
# from django.conf import settings
from nwisefin import settings
vysfin_url = settings.VYSFIN_URL

# IST = pytz.timezone('Asia/Kolkata')
# datetime_ist = datetime.now(IST)
# today = datetime_ist.strftime('%Y-%m-%d')
today_std=datetime.today()
time_function=Timecalculation()
from utilityservice.service.threadlocal import NWisefinThread
class TourAdvance(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)

    @transaction.atomic
    def create_advance(self, request_obj,emp_id,request):
        api_service = ApiService(self._scope())
        logger.info('ta_ Adv_create- '+str(emp_id)+str(request_obj))
        ccbs_type=Ccbs_utils.advance
        tour_id = request_obj['advance'][0]['tourgid']
        valid_service=Validation(self._scope())
        error_obj = NWisefinError()
        adv_maker_check=valid_service.permisssion_check_type(tour_id,emp_id,App_type.TOUR,App_level.ZERO_LEVEL)
        if adv_maker_check is False:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.VALID_USER)
            return error_obj

        tour_data=TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id,entity_id=self._entity_id())[0]
        tour_maker_id=tour_data.empgid
        onbehalf_id=tour_data.onbehalfof
        if "approval" not in request_obj['advance'][0]:
            rm_get = api_service.get_RM_ID(request, tour_maker_id)
            approver=rm_get
        else:
            approver = request_obj['advance'][0]['approval']
        if int(approver) == emp_id or int(approver) == tour_maker_id or int(approver)==0 or int(approver)==onbehalf_id:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.MAKER_APPROVER_SAME)
            return error_obj
        validation_service = Validation(self._scope())
        # approver_check = validation_service.approver_validation(App_type.advance, approver, request)
        # if approver_check is False:
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.APPROVER_NOT_IN_LIST)
        #     return error_obj

        if tour_data.tour_status != Status.APPROVED:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.TOUR_NOT_APPROVED)
            return error_obj



        for advance in request_obj['advance']:
            if 'id' in advance:
                #onb validation


                # try:
                tour_id=AdvanceTable.objects.using(self._current_app_schema()).get(id=advance['id'],entity_id=self._entity_id()).tour_id
                # adv_status=TourRequest.objects.using(self._current_app_schema()).get(id=tour_id,entity_id=self._entity_id()).advance_status
                # if adv_status==Status.DEFAULT or adv_status==Status.APPROVED or adv_status==Status.REJECTED :
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.CANT_EDIT)
                #     return error_obj

                valid_check = Validation(self._scope())
                ccbs_obj = request_obj['ccbs']
                scope = request.scope
                ccbs_ck_service=Onbehalf_service(scope)
                ccbs_id_check=ccbs_ck_service.ccbs_id_tour_id_check(ccbs_obj,tour_id)
                if ccbs_id_check != True:
                    return ccbs_id_check
                ccbs_validation = valid_check.ccbs_validation(advance['reqamount'], ccbs_obj, tour_id)
                if ccbs_validation != True:
                    return ccbs_validation

                if advance['remarks'] is None or advance['remarks'] == "":
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.COMMENT)
                    return error_obj
                if int(advance['tourgid']) !=tour_id:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_ID)
                    return error_obj

                # advance = request_obj['advance']
                # for dtl in advance:
                advance = TourAdvanceRequest(advance)
                id = advance.get_id()
                reason = advance.get_reason()
                reqamount = advance.get_reqamount()
                reqamount=round(float(reqamount),2)
                appamount = advance.get_appamount()
                invoiceheadergid = advance.get_invoiceheadergid()
                status = advance.get_status()
                if float(reqamount) <= 0 :
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.AMOUNT)
                    return error_obj
                Tourdetaildata = AdvanceTable.objects.using(self._current_app_schema()).filter(id=id,entity_id=self._entity_id()).update(reason=reason,
                                                             reqamount=reqamount,
                                                             appamount=reqamount,
                                                             #invoiceheadergid=invoiceheadergid,
                                                             updated_by=emp_id,
                                                             updated_date=timezone.now())
                # 13/1 delete_previous_ccbs-Ste
                delete_previous_ccbs=Ccbs.objects.using(self._current_app_schema()).filter(requestid=id,tour_id=tour_id,entity_id=self._entity_id()).update(status=0)

                adv_id = id

                service = Onbehalf_service(self._scope())
                resp_obj = service.insert_Ccbs(ccbs_obj, emp_id,adv_id,ccbs_type)

                status_get = TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=request_obj['advance'][0]['tourgid'],
                                                                                            request_type=(App_type.ADVANCE or App_type.advance), entity_id=self._entity_id()).last()
                if status_get is not None:
                    if status_get.status == Status.RETURNED:

                        advance = request_obj['advance']
                        for i in range(0, len(advance)):
                            data = TourAdvanceRequest(advance[i])

                            if data.onbehalfof >0:
                                tour_emp = data.onbehalfof
                                data.onbehalfof = emp_id
                            else:
                                tour_emp = emp_id

                            TravelHistory.objects.using(self._current_app_schema()).create(tour_id=data.tourgid, approvedby=emp_id, applevel=App_level.ZERO_LEVEL, approveddate=time_function.ist_time(),
                                                                                           request_type=App_type.ADVANCE,  comment=data.remarks, status=Status.REQUESTED, entity_id=self._entity_id())
                            TravelHistory.objects.using(self._current_app_schema()).create(tour_id=data.tourgid, approvedby=approver, applevel=App_level.FIRST_LEVEL, approveddate=time_function.ist_time(),
                                                                                           request_type=App_type.ADVANCE,  comment="", status=Status.PENDING, entity_id=self._entity_id())
                            TourRequest.objects.using(self._current_app_schema()).filter(id=data.tourgid).update(advance_status=Status.PENDING,entity_id=self._entity_id())

                    else:
                        advance = request_obj['advance'][0]
                        data = TourAdvanceRequest(advance)
                        approver_update = TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=request_obj['advance'][0]['tourgid'],
                                                                                                         request_type=App_type.ADVANCE,
                                                                                                         applevel=App_level.FIRST_LEVEL, entity_id=self._entity_id()).order_by('-id')[0]
                        TravelHistory.objects.using(self._current_app_schema()).filter(id=approver_update.id, entity_id=self._entity_id()).update(
                            approvedby=approver,approveddate=time_function.ist_time())

                        approved_by_id=TravelHistory.objects.using(self._current_app_schema()).filter(request_type=App_type.ADVANCE,
                                                                                                      status=Status.REQUESTED,
                                                                                                      tour_id=request_obj['advance'][0]['tourgid'], entity_id=self._entity_id()).last()

                        TravelHistory.objects.using(self._current_app_schema()).filter(id=approved_by_id.id).update(comment=request_obj['advance'][0]['remarks'], approveddate=time_function.ist_time(), entity_id=self._entity_id())






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
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                #     return error_obj
                # if resp_obj.status=="success":
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                return success_obj
            else:



                # try:
                # onbehalf_obj = Onbehalfrequest(request_obj)
                ccbs_obj = request_obj['ccbs']
                advance = request_obj['advance']
                for i in range(0 ,len(advance)):
                    data = TourAdvanceRequest(advance[i])
                    if data.onbehalfof >0:
                        if data.onbehalfof!=tour_maker_id:
                            error_obj = NWisefinError()
                            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                            error_obj.set_description(ErrorDescription.IN_VALID_ONB)
                            return error_obj
                        if int(data.onbehalfof) == emp_id:
                            error_obj = NWisefinError()
                            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                            error_obj.set_description(ErrorDescription.IN_VALID_ONB)
                            return error_obj
                        tour_emp = data.onbehalfof
                        data.onbehalfof = emp_id
                    else:
                        tour_emp = emp_id
                        if tour_emp!=tour_maker_id:
                            error_obj = NWisefinError()
                            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                            error_obj.set_description(ErrorDescription.INVALID_MAKER)
                            return error_obj

                        # onbehalfof_id = request_obj['onbehalfof']
                        # object = TourAdvance()
                        # request_obj = object.onbehalf_emoloyee(onbehalfof_id, request_obj)
                    tourgid = data.get_tourgid()

                    tour_req=TourRequest.objects.using(self._current_app_schema()).get(id=tourgid,entity_id=self._entity_id())
                    valid_check=Validation(self._scope())

                    # maker_check=valid_check.tour_maker_only_check(tourgid,tour_emp)
                    advance_date_check =valid_check.advance_datecheck(tour_req.end_date)
                    if advance_date_check is False:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        error_obj.set_description(ErrorDescription.ADVANCE_DATE)
                        return error_obj


                    # if tour_req.advance_status==Status.PENDING:
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.ADVANCE_PENDING)
                    #     return error_obj
                    # if tour_req.advance_status==Status.RETURNED:
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.ADVANCE_RETURNED)
                    #     return error_obj

                    if tour_req.tour_cancel_status==Status.PENDING or tour_req.tour_cancel_status==Status.APPROVED or tour_req.advance_cancel_status==Status.PENDING or tour_req.advance_cancel_status==Status.APPROVED :
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        error_obj.set_description(ErrorDescription.CANCEL_SUBMITTED)
                        return error_obj

                    ccbs_ck_service = Onbehalf_service(self._scope())
                    ccbs_id_check = ccbs_ck_service.ccbs_id_tour_id_check(ccbs_obj, 0)  # 0 tourid for create
                    if ccbs_id_check != True:
                        return ccbs_id_check

                    ccbs_validation=valid_check.ccbs_validation(advance[0]['reqamount'],ccbs_obj,tourgid)
                    if ccbs_validation != True:
                        return ccbs_validation


                    # onbehalfof = data.get_onbehalfof()
                    apptype = App_type.ADVANCE
                    remarks = data.get_remarks()
                    if remarks is None or remarks=="":
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        error_obj.set_description(ErrorDescription.COMMENT)
                        return error_obj

                    approval = data.get_approval()
                    for dtl in advance:
                        advance = TourAdvanceRequest(dtl)
                        reason = advance.get_reason()
                        reqamount = advance.get_reqamount()
                        reqamount=round(float(reqamount),2)
                        if float(reqamount)<=0 :
                            error_obj = NWisefinError()
                            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                            error_obj.set_description(ErrorDescription.AMOUNT)
                            return error_obj
                        appamount = reqamount
                        invoiceheadergid = advance.get_invoiceheadergid()
                        # status = 1
                        Tourdetaildata = AdvanceTable.objects.using(self._current_app_schema()).create(tour_id=tourgid,
                                                                     reason=reason,
                                                                     reqamount=reqamount,
                                                                     appamount=appamount,
                                                                     #invoiceheadergid=invoiceheadergid,
                                                                     status=Status.PENDING,
                                                                     created_by=emp_id,entity_id=self._entity_id())

                    data = {"tourgid": tourgid,
                            "approvedby": emp_id,
                            "onbehalfof": data.onbehalfof,
                            "approveddate": time_function.ist_time(),
                            "apptype": apptype,
                            "applevel": App_level.ZERO_LEVEL,
                            "appcomment": remarks,
                            "status": Status.REQUESTED}

                    req = TourApprovedby.insert_approvedby(self, data,request)
                    d = json.loads(req.get())
                    if d.get('status') == "success" and req.status=="success":
                        # try:
                        data = {"tourgid": tourgid,
                                "approvedby": approver,
                                "onbehalfof": 0,
                                "approveddate": time_function.ist_time(),
                                "apptype": apptype,
                                "applevel": App_level.FIRST_LEVEL,
                                "appcomment": "",
                                "status": Status.PENDING}
                        # a=data["status"]
                        tourrequest=TourRequest.objects.using(self._current_app_schema()).filter(id=tourgid,entity_id=self._entity_id()).update(advance_status=Status.PENDING)

                        approve = TourApprovedby.insert_approvedby(self, data,request)
                        adv_id = AdvanceTable.objects.using(self._current_app_schema()).latest('id').id
                        if approve.status == "success":
                            exp_service = Onbehalf_service(self._scope())
                            resp1 = exp_service.insert_Ccbs(ccbs_obj, emp_id,adv_id,ccbs_type)
                        if resp1.status=="success":
                            e = json.loads(resp1.get())
                        if e.get('status') == "success" and resp1.status=="success":
                            pass
                        else:
                            return approve

                        # except Exception as e:
                        #     print(e)
                        #     error_obj = NWisefinError()
                        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        #     error_obj.set_description(str(e))
                        #     return error_obj
                            # except:
                            #     error_obj = NWisefinError()
                            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                            #     return error_obj


                # except IntegrityError as error:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                #     return error_obj
                # except Exception as e:
                #     print(e)
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(str(e))
                #     return error_obj

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            return success_obj

    # def onbehalf_emoloyee(self,onbehalfof_id,tourdata):
    #     emp = Employee.objects.using(self._current_app_schema()).get(user_id = onbehalfof_id)
    #     employee_id = emp.id
    #     tourdata['onbahalfof'] = employee_id
    #     data = TourAdvanceRequest(tourdata)
    #     return data

    def get_advance(self,empid,onb,vys_page,request_date,tour_no,request,apptype,status):
        if request_date != "":
            try:
                request_date = int(request_date)
                request_date = str(datetime.fromtimestamp(int(request_date) / 1000.0))
                request_date = (datetime.strptime(request_date[:10], '%Y-%m-%d')).date()
            except:
                request_date = (datetime.strptime(request_date, '%d-%b-%Y')).date()

        if apptype is None:
            app_type = [App_type.ADVANCE, App_type.AdvanceCancel]
        else:
            app_type = [apptype]

        condition=Q()

        if apptype==App_type.AdvanceCancel:
            if status is not None:
                condition &= Q(tour__advance_cancel_status=status)
        else:
            if status is not None:
                condition &= Q(tour__advance_status=status)

        if onb is None:
            Tour = TravelHistory.objects.using(self._current_app_schema()).filter(condition,request_type__in=app_type, applevel=Filterapplevel.zero,
                                                tour__empgid=empid,tour__request_date__icontains=request_date,
                                                tour__id__icontains=tour_no,entity_id=self._entity_id()).all().order_by('-id')
        elif int(onb) == 0:
            Tour = TravelHistory.objects.using(self._current_app_schema()).filter(condition,request_type__in=app_type, applevel=Filterapplevel.zero,
                                                tour__request_date__icontains=request_date, tour__id__icontains=tour_no,
                                                                    tour__onbehalfof=empid,entity_id=self._entity_id()).all().order_by('-id')
        else:
            Tour = TravelHistory.objects.using(self._current_app_schema()).filter(condition,request_type__in=app_type, applevel=Filterapplevel.zero,
                                               tour__onbehalfof=empid, tour__request_date__icontains=request_date, tour__id__icontains=tour_no,
                                                    tour__empgid=onb, entity_id=self._entity_id()).all().order_by('-id')
        unique_tour=[]
        approvedby_id=[]
        for data in Tour:
            if len (unique_tour)<=vys_page.get_query_limit():
                if data.tour_id not in unique_tour:
                    unique_tour.append(data.tour_id)
                    approvedby_id.append(data.id)
        Tour = TravelHistory.objects.using(self._current_app_schema()).filter(id__in=approvedby_id, entity_id=self._entity_id()).all().order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]

            # Tour = TourRequest.objects.using(self._current_app_schema()).filter(empgid=empid)
        resp_list = NWisefinList()
        if len(Tour)>0:
            for appr in Tour:
                req_data = TourAdvanceResponse()
                tour=appr.tour
                req_data.set_tourgid(appr.tour_id)
                # req_data.set_requestno(tour.requestno)
                req_data.set_id(tour.id)
                req_data.set_requestdate(tour.request_date)
                req_data.set_empgid(tour.empgid)
                detail = emp_dtl(self._scope())
                empdtl = ApiService(self._scope())

                employee = empdtl.employee_details_get(appr.approvedby,request)
                req_data.set_employee_name(employee.full_name)
                # code = empdtl.employee_code_get(tour.empgid)
                req_data.set_employee_code(employee.code)
                req_data.set_empdesignation(tour.empdesignation)
                req_data.set_empgrade(tour.empgrade)

                reason = detail.get_reason_name(tour.reason)
                req_data.set_reason(reason)
                req_data.set_reason_id(tour.reason)


                req_data.set_empbranchgid(tour.empbranchgid)
                branch = empdtl.get_branch_data(tour.empbranchgid, request)
                req_data.set_branch_name(branch.name)
                req_data.set_branch_code(branch.code)

                req_data.set_startdate(tour.start_date)
                req_data.set_enddate(tour.end_date)
                req_data.set_remarks(appr.comment)
                # if appr.onbehalfof >0:
                #     onbehalf = empdtl.employee_details_get(appr.onbehalfof,request)
                #     req_data.set_onbehalfof(onbehalf.full_name)

                adv_approvedby=TravelHistory.objects.using(self._current_app_schema()).filter(request_type=Filterapptype.advance, applevel=Filterapplevel.one,
                                                                                              tour_id=appr.tour_id, entity_id=self._entity_id()).order_by("-id")[0]
                approvedby = empdtl.employee_details_get(adv_approvedby.approvedby,request)
                req_data.set_approvedby(approvedby.full_name)
                req_data.set_approver_code(approvedby.code)
                tour_status = status_get(tour.tour_status)
                advance_status = status_get(tour.advance_status)
                advance_cancel_status = status_get(tour.advance_cancel_status)
                claim_status = status_get(tour.claim_status)
                req_data.set_tour_status(tour_status)
                req_data.set_advance_status(advance_status)
                req_data.set_advance_cancel_status(advance_cancel_status)
                req_data.set_claim_status(claim_status)
                req_data.set_tour_status_id(tour.tour_status)
                req_data.set_advance_status_id(tour.advance_status)
                req_data.set_advance_cancel_status_id(tour.advance_cancel_status)
                req_data.set_claim_status_id(tour.claim_status)

                diffdays = (time_function.ist_date() - tour.end_date.date()).days
                req_data.set_is_tour_ended(bool(max(0, diffdays)))

                adv_amount=AdvanceTable.objects.using(self._current_app_schema()).filter(tour_id=appr.tour_id,entity_id=self._entity_id()).order_by("-id")
                if len(adv_amount)==0:
                    adv_amount.reqamount=0
                    adv_amount.appamount=0
                req_data.set_requested_amount(adv_amount[0].reqamount)
                req_data.set_approved_amount(adv_amount[0].appamount)

                resp_list.append(req_data)
            vpage = NWisefinPaginator(Tour, vys_page.get_index(), 10)
            resp_list.set_pagination(vpage)
        return resp_list

    def advance_summary(self,empid,onb,vys_page,request_date,tour_no,request):
        if request_date != "":
            try:
                request_date = int(request_date)
                request_date = str(datetime.fromtimestamp(int(request_date) / 1000.0))
                request_date = (datetime.strptime(request_date[:10], '%Y-%m-%d')).date()
            except:
                request_date = (datetime.strptime(request_date, '%d-%b-%Y')).date()
        tour_cancel_check=[Status.DEFAULT,Status.REJECTED]



        if onb is None:
            Tour = TravelHistory.objects.using(self._current_app_schema()).filter(request_type=Filterapptype.tour, applevel=Filterapplevel.zero,
                                        tour__empgid=empid, tour__tour_status=Status.APPROVED,tour__advance_status=Status.DEFAULT,
                                        tour__end_date__gte=time_function.ist_date(), tour__request_date__icontains=request_date,
                                        tour__id__icontains=tour_no, tour__tour_cancel_status__in=tour_cancel_check,
                                         entity_id=self._entity_id()).all().order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]
        elif int(onb) == 0:
            Tour = TravelHistory.objects.using(self._current_app_schema()).filter(request_type=Filterapptype.tour, applevel=Filterapplevel.zero,
                                     tour__tour_status=Status.APPROVED,tour__advance_status=Status.DEFAULT,tour__onbehalfof=empid,
                                    tour__end_date__gte=time_function.ist_date(), tour__request_date__icontains=request_date,
                                     tour__id__icontains=tour_no, tour__tour_cancel_status__in=tour_cancel_check,
                                      entity_id=self._entity_id()).all().order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]
        else:
            Tour = TravelHistory.objects.using(self._current_app_schema()).filter(request_type=Filterapptype.tour, applevel=Filterapplevel.zero,
                                    tour__empgid=onb, tour__onbehalfof=empid, tour__tour_status=Status.APPROVED,tour__advance_status=Status.DEFAULT,
                                    tour__end_date__gte=time_function.ist_date(), tour__request_date__icontains=request_date,
                                     tour__id__icontains=tour_no, tour__tour_cancel_status__in=tour_cancel_check,
                                      entity_id=self._entity_id()).all().order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]
        resp_list = NWisefinList()
        if len(Tour)>0:
            for appr in Tour:
                req_data = TourAdvanceResponse()
                tour=appr.tour
                req_data.set_tourgid(appr.tour_id)
                # req_data.set_requestno(tour.requestno)
                req_data.set_id(tour.id)
                req_data.set_requestdate(tour.request_date)
                req_data.set_empgid(tour.empgid)
                empdtl = ApiService(self._scope())
                detail=emp_dtl(self._scope())
                employee = empdtl.employee_details_get(tour.empgid,request)
                req_data.set_employee_name(employee.full_name)
                # code = empdtl.employee_code_get(tour.empgid)
                req_data.set_employee_code(employee.code)
                req_data.set_empdesignation(tour.empdesignation)
                req_data.set_empgrade(tour.empgrade)

                reason = detail.get_reason_name(tour.reason)
                req_data.set_reason(reason)
                req_data.set_reason_id(tour.reason)

                req_data.set_startdate(tour.start_date)
                req_data.set_enddate(tour.end_date)
                req_data.set_remarks(appr.comment)
                # if appr.onbehalfof >0:
                #     onbehalf = empdtl.employee_details_get(appr.onbehalfof,request)
                #     req_data.set_onbehalfof(onbehalf.full_name)

                tour_approver=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=appr.tour_id, request_type=App_type.TOUR,
                                                                                             status=Status.APPROVED, entity_id=self._entity_id()).order_by("-id")[0]
                approvedby = empdtl.employee_details_get(tour_approver.approvedby,request)
                req_data.set_approvedby(approvedby.full_name)
                req_data.set_approver_code(approvedby.code)
                tour_status = status_get(tour.tour_status)
                advance_status = status_get(tour.advance_status)
                advance_cancel_status = status_get(tour.advance_cancel_status)
                claim_status = status_get(tour.claim_status)
                req_data.set_tour_status(tour_status)
                req_data.set_advance_status(advance_status)
                req_data.set_advance_cancel_status(advance_cancel_status)
                req_data.set_claim_status(claim_status)
                req_data.set_tour_status_id(tour.tour_status)
                req_data.set_advance_status_id(tour.advance_status)
                req_data.set_advance_cancel_status_id(tour.advance_cancel_status)
                req_data.set_claim_status_id(tour.claim_status)
                resp_list.append(req_data)
            vpage = NWisefinPaginator(Tour, vys_page.get_index(), 10)
            resp_list.set_pagination(vpage)
        return resp_list

    def get_tour_advance(self,tour_id,request):
        # paid_advance_data jan 21
        total_paid_advance = 0
        emp_id = (TourRequest.objects.using(self._current_app_schema()).get(id=tour_id,entity_id=self._entity_id())).empgid
        emp_service = ApiService(self._scope())
        emp_code = (emp_service.employee_details_get(emp_id, request)).code
        # emp_code="Vsolv33"
        # try:
        # data = {
        #     "Type": "PAYMENT_EMPLOYEE",
        #     "Sub_Type": "PPX",
        #     "Filter":
        #         {
        #             "Tour_id": tour_id,
        #             "Employee_code": emp_code,
        #             "Supplier_code": ""
        #         }
        # }
        #
        # params = ''
        # ecf_service = ApiService(self._scope())
        # token = "Bearer  " + ecf_service.get_authtoken(request)
        # print(token)
        # headers = {"content-type": "application/json", "Authorization": "" + token + ""}
        # resp_data = json.dumps(data)
        # ecf_post_url = vysfin_url + 'AP_PPX_Details_Get_API'
        # # print(resp_data)
        # logger.info('ta_ AP_PPX_Details_Before- '+str(data))
        # resp = requests.post(ecf_post_url, params=params, data=resp_data, headers=headers, verify=False)
        # results = resp.content.decode("utf-8")
        # paid_advance_data = json.loads(results)
        # logger.info('ta_ AP_PPX_Details_After- '+str(paid_advance_data))
        # paid_advance_data


        dtl_list = []
        empdtl = ApiService(self._scope())

        approve = TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tour_id,
                                                                                 request_type=(App_type.advance or App_type.ADVANCE), status__lte=4, entity_id=self._entity_id()).all()
        approved_by_id=[]
        for app_data in approve:
            approved_by_id.append(app_data.id)


        # adv_status=TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id,advance_status=Status.RETURNED,entity_id=self._entity_id())
        # if len(adv_status)!=0:
            ret_id=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tour_id,
                                                                                  request_type=(App_type.advance or App_type.ADVANCE), entity_id=self._entity_id()).last()
            approved_by_id.append(ret_id.id)

        approve = TravelHistory.objects.using(self._current_app_schema()).filter(id__in=approved_by_id, entity_id=self._entity_id())
        req_data = TourAdvanceResponse()
        no_of_advance=0
        advance_list=[]
        tour_approver = []
        for appr in approve:
            approverdata = TourMaker()
            # if appr.onbehalfof > 0:
            #     onbehalfof = empdtl.employee_details_get(appr.onbehalfof, request)
            #     approverdata.set_onbehalfof(onbehalfof.full_name)
            #     approverdata.set_onbehalfof_code(onbehalfof.code)
            approverdata.set_id(appr.id)
            approverdata.set_comment(appr.comment)
            approvedby = empdtl.employee_details_get(appr.approvedby, request)
            approverdata.set_approvedby(approvedby.full_name)
            approverdata.set_approvedby_code(approvedby.code)
            approverdata.set_status(appr.status)
            approverdata.set_applevel(appr.applevel)
            approverdata.set_approveddate(appr.approveddate)
            approverdata.set_apptype(appr.request_type)
            approverdata.set_tourid(appr.tour_id)

            approverdata.set_approver_id(appr.approvedby)
            # approver_code= empdtl.employee_code_get(appr.approvedby)
            approverdata.set_approver_code(approvedby.code)

            if appr.applevel==1:
                advance_list.append(no_of_advance)
                no_of_advance+=1

                advance = AdvanceTable.objects.using(self._current_app_schema()).filter(tour_id=tour_id,entity_id=self._entity_id())[no_of_advance - 1]
                # for advance in Advance:
                req_advance = TourAdvanceResponse()
                req_advance.set_id(advance.id)
                req_advance.set_tourgid(advance.tour_id)
                req_advance.set_reason(advance.reason)
                req_advance.set_reqamount(advance.reqamount)
                req_advance.set_appamount(advance.appamount)
                req_advance.set_adjustamount(advance.adjustamount)
                req_advance.set_invoiceheadergid(advance.invoiceheadergid)
                req_advance.set_crnno(advance.crnno)
                req_advance.set_debit_categorygid(advance.debit_categorygid)
                req_advance.set_debit_subcategorygid(advance.debit_subcategorygid)
                req_advance.set_ppx_headergid(advance.ppx_headergid)
                advance_status = adv_status_get(advance.status)
                # req_advance.set_status_name(advance_status)
                req_advance.set_status(advance.status)
                req_advance.set_approver_id(appr.approvedby)
                req_advance.set_approver_code(approvedby.code)
                approver = empdtl.employee_details_get(appr.approvedby, request)
                req_advance.set_approver(approver.full_name)
                paid_advance_amount=0
                paid_advance_balance=0
                ppxheader_date=None
                # if type(paid_advance_data) == list:
                #     for each_list in paid_advance_data:
                #         total_paid_advance+=each_list['ppxheader_amount']
                #         if advance.crnno == each_list['invoiceheader_crno']:
                #             paid_advance_amount=each_list['ppxheader_amount']
                #             paid_advance_balance=each_list['ppxheader_balance']
                #             ppxheader_date=each_list['ppxheader_date']
                #             if ppxheader_date is not None:
                #                 ppxheader_date=str(datetime.fromtimestamp(ppxheader_date / 1000.0).date())
                req_advance.set_paid_advance_amount(paid_advance_amount)
                req_advance.set_paid_advance_balance(paid_advance_balance)
                req_advance.set_ppxheader_date(ppxheader_date)
                dtl_list.append(json.loads(req_advance.get()))

            tour_approver.append(json.loads(approverdata.get()))



        req_data.set_approve(tour_approver)
        req_data.set_total_paid_advance(total_paid_advance)


        # for i in advance_list:

        req_data.set_detail(dtl_list)





        tour_approver = TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tour_id, request_type=(App_type.advance or App_type.ADVANCE), applevel=App_level.FIRST_LEVEL, entity_id=self._entity_id()).last()
        if tour_approver is not None:
            tour_app=tour_approver.approvedby
            approvedby = empdtl.employee_details_get(tour_app,request)
            # tour_approver_code = empdtl.employee_code_get(tour_app)
            req_data.set_approver_data(tour_app,approvedby.full_name,approvedby.code)

            ta_api_service = ApiService(self._scope())
            approver_branch_data = ta_api_service.get_branch_data_empid([tour_app], request)
            req_data.set_approver_branch_data(approver_branch_data)

            tour=tour_approver.tour
            req_data.set_branch_id(tour.empbranchgid)
            branch= empdtl.get_branch_data(tour.empbranchgid,request)
            req_data.set_branch_name(branch.name)
            # branch_code= empdtl.get_branch_code(tour.empbranchgid)
            req_data.set_branch_code(branch.code)
        tour=TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id,entity_id=self._entity_id()).last()

        req_data.set_tourgid(tour_id)
        req_data.set_id(tour_id)
        # req_data.set_requestno(tour.requestno)
        req_data.set_requestdate(tour.request_date)
        detail=emp_dtl(self._scope())
        reason = detail.get_reason_name(tour.reason)
        req_data.set_reason(reason)
        req_data.set_reason_id(tour.reason)
        req_data.set_startdate(tour.start_date)
        req_data.set_enddate(tour.end_date)

        diffdays = (datetime.today().date() - tour.end_date.date()).days
        req_data.set_is_tour_ended(bool(max(0, diffdays)))

        return req_data

    # def delete_advance(self,id):
    #     try:
    #         delete = AdvanceTable.objects.using(self._current_app_schema()).filter(id=id).update(status=Status.DELETED)
    #         msg_obj = NWisefinSuccess()
    #         msg_obj.set_status(SuccessMessage.DELETE_MESSAGE)
    #         msg_obj.set_message({"id": id})
    #         return msg_obj
    #
    #     except Exception as e:
    #         error_obj = NWisefinError()
    #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #         error_obj.set_description(str(e))
    #         return error_obj

    # def tourid_advance(self,empid,tour_id):
    #     tour = TourRequest.objects.using(self._current_app_schema()).get(empgid=empid,id=tour_id)
    #     dtl_list = []
    #     empdtl = emp_dtl()
    #     req_advance = TourAdvanceResponse()
    #     Advance = AdvanceTable.objects.using(self._current_app_schema()).filter(tour_id=tour.id).all()
    #     for advance in Advance:
    #         req_data = TourAdvanceResponse()
    #         req_data.set_id(advance.id)
    #         req_advance.set_tourgid(advance.tour_id)
    #         # reason = empdtl.get_reason_name(advance.reason)
    #         req_data.set_reason(advance.reason)
    #         req_data.set_reqamount(advance.reqamount)
    #         req_data.set_appamount(advance.appamount)
    #         req_data.set_status(advance.status)
    #         dtl_list.append(json.loads(req_data.get()))
    #     approve = ApprovedBy.objects.using(self._current_app_schema()).filter(tour_id=tour.id, apptype=Filterapptype.advance,).all()
    #     for appr in approve:
    #         req_advance.set_tourgid(appr.tour_id)
    #         req_advance.set_requestno(tour.requestno)
    #         req_advance.set_requestdate(tour.requestdate)
    #         reason = empdtl.get_reason_name(tour.reason)
    #         req_advance.set_reason(reason)
    #         req_advance.set_reason_id(tour.reason)
    #         req_advance.set_startdate(tour.startdate)
    #         req_advance.set_enddate(tour.enddate)
    #         req_advance.set_remarks(appr.appcomment)
    #         if appr.onbehalfof >0:
    #             onbehalfof = empdtl.employee_name_get(appr.onbehalfof)
    #             req_advance.set_onbehalfof(onbehalfof)
    #         approvedby = empdtl.employee_name_get(appr.approvedby)
    #         req_advance.set_approvedby(approvedby)
    #         req_advance.set_status(appr.status)
    #     req_advance.set_detail(dtl_list)
    #     return req_advance

    # @transaction.atomic
    # def update_adv_amount(self,request_obj,user_id):
    #     logger.info('ta_ Update_adv_amt- '+str(user_id)+str(request_obj))
    #     # try:
    #     request_obj["appamount"]=float(request_obj["appamount"])
    #     if request_obj["appamount"]<=0:
    #         error_obj = NWisefinError()
    #         error_obj.set_code(ErrorMessage.INVALID_DATA)
    #         error_obj.set_description(ErrorDescription.CLAIM_AMOUNT)
    #         return error_obj
    #     adv_data=AdvanceTable.objects.using(self._current_app_schema()).get(id=request_obj["adv_id"],entity_id=self._entity_id())
    #     tourid=adv_data.tour_id
    #     # adv_status=TourRequest.objects.using(self._current_app_schema()).get(id=tourid,entity_id=self._entity_id()).advance_status
    #     # if adv_status!=Status.PENDING:
    #     #     error_obj = NWisefinError()
    #     #     error_obj.set_code(ErrorMessage.INVALID_DATA)
    #     #     error_obj.set_description(ErrorDescription.CANT_EDIT)
    #     #     return error_obj
    #     adv_approver=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tourid, apptype=App_type.ADVANCE,
    #                                                                                 applevel=App_level.FIRST_LEVEL, entity_id=self._entity_id()).order_by("-id")[0]
    #     adv_approverid=adv_approver.approvedby
    #     if adv_approverid!=int(user_id):
    #         error_obj = NWisefinError()
    #         error_obj.set_code(ErrorMessage.INVALID_DATA)
    #         error_obj.set_description(ErrorDescription.VALID_USER)
    #         return error_obj
    #
    #     claimed_amount=adv_data.reqamount
    #     validation_service=Validation(self._scope())
    #     approved_amt_validation=validation_service.higher_approve_amount(claimed_amount,request_obj["appamount"])
    #     if approved_amt_validation != True:
    #         return approved_amt_validation
    #
    #
    #     Touramount = AdvanceTable.objects.using(self._current_app_schema()).filter(id=request_obj["adv_id"],entity_id=self._entity_id()).update(appamount=round(request_obj["appamount"],2),
    #                                                                           updated_by=user_id,
    #                                                                           updated_date=today_std,entity_id=self._entity_id())
    #
    #     ccbs_obj=Ccbs.objects.using(self._current_app_schema()).filter(requestid=request_obj["adv_id"],entity_id=self._entity_id()).all()
    #     for each_ccbs in ccbs_obj:
    #         percentage=each_ccbs.percentage/100
    #         Ccbs.objects.using(self._current_app_schema()).filter(id=each_ccbs.id,entity_id=self._entity_id()).update(amount=round(request_obj["appamount"]*percentage,2),
    #                                                                           updated_by=user_id,updated_date=today_std)
    #
    #     # except IntegrityError as error:
    #     #     error_obj = NWisefinError()
    #     #     error_obj.set_code(ErrorMessage.INVALID_DATA)
    #     #     error_obj.set_description(ErrorDescription.INVALID_DATA)
    #     #     return error_obj
    #     # except Exception as e:
    #     #     print(e)
    #     #     error_obj = NWisefinError()
    #     #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #     #     error_obj.set_description(str(e))
    #     #     return error_obj
    #     success_obj = NWisefinSuccess()
    #     success_obj.set_status(SuccessStatus.SUCCESS)
    #     success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
    #     return success_obj
    #
    # def advance_invoice(self,id,invoiceheadergid,crn_no):
    #     try:
    #         AdvanceTable.objects.using(self._current_app_schema()).filter(id=id).update(invoiceheadergid=invoiceheadergid,crnno=crn_no)
    #
    #     except Exception as e:
    #         print(e)
    #         error_obj = NWisefinError()
    #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #         error_obj.set_description(str(e))
    #         return error_obj
    #     success_obj = NWisefinSuccess()
    #     success_obj.set_status(SuccessStatus.SUCCESS)
    #     success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
    #     return success_obj

    # def update_advance_table(self,id,advancedata):
    #     data=Advance_Request(advancedata)
    #     try:
    #         AdvanceTable.objects.using(self._current_app_schema()).filter(id=id).update(adjustamount=data.adjustamount,
    #                                                   ppx_headergid=data.ppx_headergid,debit_categorygid=data.debit_categorygid,
    #                                                   debit_subcategorygid=data.debit_subcategorygid)
    #
    #     except Exception as e:
    #         print(e)
    #         error_obj = NWisefinError()
    #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #         error_obj.set_description(str(e))
    #         return error_obj
    #     success_obj = NWisefinSuccess()
    #     success_obj.set_status(SuccessStatus.SUCCESS)
    #     success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
    #     return success_obj

    def adv_adjust_check(self,request,tourid):
        emp_id=(TourRequest.objects.using(self._current_app_schema()).get(id=tourid,entity_id=self._entity_id())).empgid
        emp_service=ApiService(self._scope())
        emp_code=(emp_service.employee_details_get(emp_id,request)).code
        # emp_code="Vsolv33"
        # try:
        data={
            "Type": "PAYMENT_EMPLOYEE",
            "Sub_Type": "PPX",
            "Filter":
                {
                "Tour_id": tourid,
                "Employee_code": emp_code,
                "Supplier_code": ""
                }
            }

        logger.info('ta_ Adv_check_before- '+str(data))

        params = ''
        ecf_service = ApiService(self._scope())
        token = "Bearer  " + ecf_service.get_authtoken(request)
        headers = {"content-type": "application/json", "Authorization": "" + token + ""}
        resp_data = json.dumps(data)
        ecf_post_url = vysfin_url+'AP_PPX_Details_Get_API'
        resp = requests.post(ecf_post_url, params=params, data=resp_data, headers=headers, verify=False)
        results = resp.content.decode("utf-8")
        result_data=json.loads(results)
        logger.info('ta_ Adv_check_after- ' + str(result_data))
        if type(result_data)==list:
            for data in result_data:
                AdvanceTable.objects.using(self._current_app_schema()).filter(crnno=data['invoiceheader_crno'],entity_id=self._entity_id()).update(
                    adjustamount=data['ppxheader_amount'],
                    ppx_headergid=data['ppxheader_gid'],
                    debit_categorygid=data['debit_categorygid'],
                    debit_subcategorygid=data['debit_subcategorygid']
                )
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.PAID_ADVANCE_NOT_PROCESSED)
            return error_obj

        # except Exception as e:
        #     print(e)
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(str(e))
        #     return error_obj

