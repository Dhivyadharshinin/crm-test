# import datetime
import json
import traceback

from taservice.service.ta_email import ta_email
from utilityservice.permissions.util.dbutil import ModuleList,RoleList
import pytz
import requests
from django.db import IntegrityError
from django.db import transaction
from django.db.models.aggregates import Max
from django.db.models import Count
from django.db.models.query_utils import Q
from django.utils import timezone



from taservice.data.request.onbehalfrequest import Onbehalfrequest
from taservice.data.request.touradvance import Ecf_data_req
from taservice.data.request.tourmaker import Status_check
from taservice.data.response.touradvance import TourAdvanceResponse
from taservice.models import TravelHistory, TourRequest, TourAdvance, ClaimRequest, Ccbs, InternationalTravel, \
    TourDetail, FrequentData
from taservice.service.onbehalf import Onbehalf_service
from taservice.service.emp_name_get import emp_dtl, Tourno_details
# from userservice.models import Employee
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants  import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from nwisefin import settings
from taservice.data.response.tourmaker import TourMaker as TourMakerResponse, TourMaker
from utilityservice.data.response.nwisefinlist  import NWisefinList
from taservice.util.ta_util import Status, App_type, App_level, Onbehalfof, Ccbs_utils, TAStatus, status_get, \
     Validation, Timecalculation, Module, Admin
from datetime import date, datetime
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
time_function = Timecalculation()
from utilityservice.service.threadlocal import NWisefinThread
class TourApprovedby(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)
    @transaction.atomic
    def insert_approvedby(self,request_obj,request):
        from taservice.service.ecf_entry import Ecf_entry
        # from taservice.data.request.approvedby import Ecf_req
        if 'id' in request_obj:
            if "onbehalf" in request_obj:
                login_emp=request.employee_id
                approver_nac=request_obj["onbehalf"]
            else:
                login_emp=0
                approver_nac=request.employee_id
            employee_id=approver_nac

            if 'appcomment' not in request_obj or request_obj['appcomment']=="":
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.COMMENT)
                return error_obj
            # try:
            request_obj['status']=3
            service=ApiService(self._scope())
            # emp = service.get_emp_id(request, request.user.id)
            # employee_id = request.employee_id
            logger.info('ta_ Tour_approve_id- ' + str(employee_id) + str(request_obj))
            approver_id=employee_id
            approver_code=service.employee_details_get(approver_id,request).code
            maker_id=(TourRequest.objects.using(self._current_app_schema()).get(id=request_obj['tourgid'],entity_id=self._entity_id())).empgid
            maker_code = service.employee_details_get(maker_id, request).code

            approver_data=(TravelHistory.objects.using(self._current_app_schema()).get(id=request_obj['id'], entity_id=self._entity_id()))
            if approver_data.status!=Status.PENDING:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.APPROVEDBY_TABLE_NOT_PENDING)
                return error_obj

            if (request_obj['apptype'].upper()==App_type.CLAIM and approver_data.applevel!=App_level.THIRD_LEVEL) or (request_obj['apptype'].upper()==App_type.TOUR and approver_data.applevel!=App_level.SECOND_LEVEL):
                if employee_id!=approver_data.approvedby:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.VALID_USER)
                    return error_obj
            elif approver_data.request_type.upper()!=(request_obj['apptype']).upper() or approver_data.tour_id!=request_obj['tourgid']:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID)
                return error_obj

            if approver_data.approvedby > 0:
                if approver_data.approvedby != approver_nac:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.APPROVER)
                    return error_obj

            if  (request_obj['apptype']).upper()==App_type.CLAIM and approver_data.applevel==App_level.FIRST_LEVEL:
                request_obj['approvedby'] = Admin.ADMIN
                claim_req = ClaimRequest.objects.using(self._current_app_schema()).filter(
                    tour_id=request_obj['tourgid'], status=1, entity_id=self._entity_id())
                claim_amount = 0
                api_service = ApiService(self._scope())
                functionalhead = api_service.get_functional_head(request, maker_id)
                for claim_table in claim_req:
                    claim_amount += claim_table.claimedamount


                error_obj = NWisefinError()
                if int(request_obj['approvedby'])==employee_id or maker_id==employee_id:
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.APPROVER)
                    return error_obj
                # validation_service = Validation(self._scope())
                # approver_check = validation_service.approver_validation(App_type.expense, int(request_obj['approvedby']),
                #                                                         request)
                # if approver_check is False:
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.APPROVER_NOT_IN_LIST)
                #     return error_obj
                tourrequest = TourRequest.objects.using(self._current_app_schema()).get(id=request_obj['tourgid'],entity_id=self._entity_id())
                if tourrequest.claim_status == Status.DEFAULT or tourrequest.claim_status == Status.APPROVED or \
                        tourrequest.claim_status == Status.REJECTED or tourrequest.claim_status == Status.RETURNED:
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.APPROVE_ERROR)
                    return error_obj
                api_service = ApiService(self._scope())
                emp_rm = api_service.get_RM_ID(request, maker_id)
                emp_fm=functionalhead["Fictional_head"]
                if int(claim_amount) >= 25000 and emp_rm!=emp_fm:
                    if functionalhead["Fictional_head"]==None:
                        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        error_obj.set_description(ErrorDescription.INVALID_FUNCTIONAL_HEAD)
                        return error_obj

                    request_obj["approvedby"] = functionalhead["Fictional_head"]
                    TravelHistory.objects.using(self._current_app_schema()).create(approvedby=request_obj['approvedby'],
                                                                                   approveddate=time_function.ist_time(),
                                                                                   request_type=App_type.CLAIM,
                                                                                   applevel=App_level.SECOND_LEVEL,
                                                                                   comment="",
                                                                                   status=Status.PENDING,
                                                                                   tour_id=request_obj['tourgid'], entity_id=self._entity_id())


                else:
                    TravelHistory.objects.using(self._current_app_schema()).create(approvedby=request_obj['approvedby'],
                                                                                   approveddate=time_function.ist_time(),
                                                                                   request_type=App_type.CLAIM,
                                                                                   applevel=App_level.THIRD_LEVEL,
                                                                                   comment="",
                                                                                   status=Status.PENDING,
                                                                                   tour_id=request_obj['tourgid'],
                                                                                   entity_id=self._entity_id())
                tourrequest = TourRequest.objects.using(self._current_app_schema()).filter(id=request_obj['tourgid'],
                                                                                           entity_id=self._entity_id()).update(
                    claim_status=Status.PENDING, entity_id=self._entity_id())
            elif request_obj['apptype'].upper()==App_type.CLAIM and approver_data.applevel==App_level.SECOND_LEVEL:
                request_obj["approvedby"]=Admin.ADMIN
                # claim_req = ClaimRequest.objects.using(self._current_app_schema()).filter(
                #     tour_id=request_obj['tourgid'], status=1, entity_id=self._entity_id())
                # claim_amount = 0
                # for claim_table in claim_req:
                #     claim_amount += claim_table.claimedamount
                # if int(claim_amount) >= 25000:
                # tourrequest = TourRequest.objects.using(self._current_app_schema()).filter(
                #     id=request_obj['tourgid'], entity_id=self._entity_id()).update(
                #     tour_status=Status.PENDING, entity_id=self._entity_id())
                trav_his = TravelHistory.objects.using(self._current_app_schema()).filter(
                    tour_id=request_obj['tourgid'], status=Status.APPROVED,
                    applevel__in=[App_level.FIRST_LEVEL],
                    request_type=App_type.CLAIM, entity_id=self._entity_id())
                arr = []
                for data in trav_his:
                    arr.append(data.approvedby)
                if employee_id in arr:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.ADMIN_PERMISSION)
                    return error_obj

                create_approve = TravelHistory.objects.using(self._current_app_schema()).create(
                    approvedby=request_obj["approvedby"], approveddate=time_function.ist_time(),
                    request_type=App_type.CLAIM, applevel=App_level.THIRD_LEVEL,
                    comment='',
                    status=Status.PENDING, entity_id=self._entity_id(), tour_id=request_obj["tourgid"])
                tourrequest = TourRequest.objects.using(self._current_app_schema()).filter(
                    id=request_obj['tourgid'], entity_id=self._entity_id()).update(
                    claim_status=Status.PENDING, entity_id=self._entity_id())

            elif request_obj['apptype'].upper()==App_type.CLAIM and approver_data.applevel==App_level.THIRD_LEVEL:
                module_permission = ApiService(self._scope())
                role_arr = module_permission.employee_modulerole_get(employee_id, ModuleList.Ta_Travel, request)
                if RoleList.admin not in role_arr:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_ADMIN)
                    return error_obj
                trav_his = TravelHistory.objects.using(self._current_app_schema()).filter(
                    tour_id=request_obj['tourgid'], status=Status.APPROVED, applevel__in=[App_level.FIRST_LEVEL,App_level.SECOND_LEVEL],
                    request_type=App_type.CLAIM, entity_id=self._entity_id())
                arr=[]
                for data in trav_his:
                    arr.append(data.approvedby)
                if employee_id in arr:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.ADMIN_PERMISSION)
                    return error_obj





                total_approved_amount=0
                total_ccbs_amount=0
                total_ccbs_percentage=0

                ccbs_arr=Ccbs.objects.using(self._current_app_schema()).filter(tour_id=request_obj['tourgid'],ccbs_type=2,requestid=0,status=1,entity_id=self._entity_id())
                for ccbs in ccbs_arr:
                    total_ccbs_amount+=ccbs.amount
                    total_ccbs_percentage+=ccbs.percentage

                approved_amount_arr=ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=request_obj['tourgid'],status=1,entity_id=self._entity_id())
                for approved_amount in approved_amount_arr:
                    total_approved_amount += approved_amount.approvedamount

                if round(total_approved_amount)!=round(total_ccbs_amount):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.AMOUNT_ERROR)
                    return error_obj
                if round(total_ccbs_percentage)!=100:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.PERCENTAGE_ERROR)
                    return error_obj


                lvl_one_approver=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=request_obj['tourgid'], status=Status.APPROVED, applevel=App_level.FIRST_LEVEL, request_type=App_type.CLAIM, entity_id=self._entity_id())
                if len(lvl_one_approver)==0:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.CLAIM_SECOND_LVL_APPROVER)
                    return error_obj
                tourrequest = TourRequest.objects.using(self._current_app_schema()).get(id=request_obj['tourgid'],entity_id=self._entity_id())
                if tourrequest.claim_status == Status.DEFAULT or tourrequest.claim_status == Status.APPROVED or \
                        tourrequest.claim_status == Status.REJECTED or tourrequest.claim_status == Status.RETURNED:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.APPROVE_ERROR)
                    return error_obj

                error_obj = NWisefinError()
                branch_service = ApiService(self._scope())
                # service = Tourno_details(self._scope())
                # employee = branch_service.employee_details_get(request_obj['login_emp'], request)
                # branch_code = branch_service.get_branch_data(employee.employee_branch_id, request)
                # appr_branch = ['1101', '2135', '1618', '1260', '1299']
                # tour_maker = service.requestno_get(request_obj['tourgid'], request)
                # maker_grade = tour_maker.employee_grade
                # emp_service = ApiService(self._scope())NAC_UAT_RELEASE
                # approver_grade = emp_service.emp_all_details(request_obj['login_emp'], request)
                # approver_grade=approver_grade.grade1
                # if maker_grade[1].isdigit():
                #     if int(maker_grade[1]) > 3:
                #         if (int(maker_grade[1]) <= int(approver_grade[1])):
                #             if branch_code.code not in appr_branch:
                #                 error_obj.set_code(ErrorMessage.BRANCH_APPROVER)
                #                 return error_obj
                #         else:
                #             error_obj.set_code(ErrorMessage.APPROVER_GRADE)
                #             return error_obj


                data = {"tourgid": request_obj['tourgid'], "type": "CLAIM"}
                jsondata = Ecf_data_req(data)
                service = Ecf_entry(self._scope())
                try:
                    data = service.invoice_entry(jsondata, request,approver_code,maker_code,approver_id)
                except Exception as e:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_ECF_VALUE)
                    error_obj.set_description(data)
                    exc = traceback.format_exc()
                    print('ta_ INVALID_ECF- ' + str(e) + str(exc))
                    logger.info('ta_ INVALID_ECF- ' + str(e) + str(exc))
                    return error_obj
                if isinstance(data, NWisefinError):
                    return data
                invoice_no=0
                if data['status']=="success":
                    invoice_no=data['ecf_id']
                    crn_no=data['crno']
                else:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_ECF_VALUE)
                    error_obj.set_description(data)
                    return error_obj



                # if data["MESSAGE"].split(",")[0] == "SUCCESS":
                #     invoice_no=int(data["MESSAGE"].split(",")[-1])
                    # crn_no=self.get_crnno(invoice_no,tourrequest.empgid)

                ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=request_obj['tourgid'],status=1,entity_id=self._entity_id()).update(entity_id=self._entity_id(),
                                                                                                                                crn_no=crn_no,invoiceheadergid=invoice_no)


                tourrequest = TourRequest.objects.using(self._current_app_schema()).filter(id=request_obj['tourgid'],entity_id=self._entity_id()).update(
                        claim_status=request_obj['status'],entity_id=self._entity_id())
                approvedby = TravelHistory.objects.using(self._current_app_schema()).filter(id=request_obj['id'],
                                                                                            entity_id=self._entity_id()).update(
                    approveddate=time_function.ist_time(),
                    comment=request_obj['appcomment'],
                    status=request_obj['status'], entity_id=self._entity_id(),approvedby=approver_nac,
                    onbehalfof_approval = login_emp
                    )

                mail_service = ta_email(self._scope())
                mail_service.mail_data(request_obj['tourgid'])

                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                return success_obj
                # else:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(data)
                #     return error_obj






            if (request_obj['apptype']).lower() == TAStatus.tour:
                # if approver_data.applevel == App_level.FIRST_LEVEL:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.FORWADER_CANT_APPROVE)
                #     return error_obj

                # inter_national_travel=InternationalTravel.objects.using(self._current_app_schema()).filter(tour_id=request_obj['tourgid'],
                #                                                                         entity_id=self._entity_id()).last()
                # if inter_national_travel is not None:
                #     if inter_national_travel.insured==0:
                #         error_obj = NWisefinError()
                #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #         error_obj.set_description(ErrorDescription.INSURANCE_REQUIRED_INTERNATIONAL_TOUR)
                #         return error_obj
                #     if inter_national_travel.approved_by==0:
                #         error_obj = NWisefinError()
                #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #         error_obj.set_description(ErrorDescription.INTERNATIONAL_TOUR_NEED_CEO_APPROVAL)
                #         return error_obj

                tourrequest = TourRequest.objects.using(self._current_app_schema()).get(id=request_obj['tourgid'],
                                                                                        entity_id=self._entity_id())
                if tourrequest.tour_status == Status.DEFAULT or tourrequest.tour_status == Status.APPROVED or \
                        tourrequest.tour_status == Status.RETURNED or tourrequest.tour_status == Status.REJECTED:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.APPROVE_ERROR)
                    return error_obj
                approvedby_applevel = TravelHistory.objects.using(self._current_app_schema()).get(id=request_obj['id'],entity_id=self._entity_id())
                # if approvedby_applevel.applevel == App_level.FIRST_LEVEL:
                #     # ADMIN
                #     request_obj["approvedby"]=6
                #     tourrequest = TourRequest.objects.using(self._current_app_schema()).filter(
                #         id=request_obj['tourgid'], entity_id=self._entity_id()).update(
                #         tour_status=Status.PENDING, entity_id=self._entity_id())
                #     create_approve = TravelHistory.objects.using(self._current_app_schema()).create(
                #         approvedby=request_obj["approvedby"],approveddate=time_function.ist_time(),
                #         request_type=App_type.TOUR, applevel=App_level.THIRD_LEVEL, comment="",
                #         status=Status.PENDING, entity_id=self._entity_id(), tour_id=request_obj["tourgid"])

                if approvedby_applevel.applevel == App_level.FIRST_LEVEL:

                    if tourrequest.international_travel==1:
                        # request_obj["approvedby"] = functionalhead["Fictional_head"]
                        # CEO_ID = 262
                        TravelHistory.objects.using(self._current_app_schema()).create(
                            approvedby=Admin.CEO,
                            approveddate=time_function.ist_time(),
                            request_type=App_type.TOUR,
                            applevel=App_level.SECOND_LEVEL,
                            comment="",
                            status=Status.PENDING,
                            tour_id=request_obj['tourgid'], entity_id=self._entity_id())


                    else:
                        # ADMIN
                        request_obj["approvedby"] = Admin.ADMIN
                        TravelHistory.objects.using(self._current_app_schema()).create(
                            approvedby=request_obj['approvedby'],
                            approveddate=time_function.ist_time(),
                            request_type=App_type.TOUR,
                            applevel=App_level.THIRD_LEVEL,
                            comment="",
                            status=Status.APPROVED,
                            tour_id=request_obj['tourgid'],
                            entity_id=self._entity_id())
                        tourrequest = TourRequest.objects.using(self._current_app_schema()).filter(
                            id=request_obj['tourgid'], entity_id=self._entity_id()).update(
                            tour_status=Status.APPROVED, entity_id=self._entity_id())

                        self.insert_frequent_data(request_obj['tourgid'])

                if approvedby_applevel.applevel == App_level.SECOND_LEVEL:
                    # ADMIN
                    request_obj["approvedby"]=Admin.ADMIN
                    create_approve = TravelHistory.objects.using(self._current_app_schema()).create(
                        approvedby=request_obj["approvedby"],approveddate=time_function.ist_time(),
                        request_type=App_type.TOUR, applevel=App_level.THIRD_LEVEL, comment="",
                        status=Status.APPROVED, entity_id=self._entity_id(), tour_id=request_obj["tourgid"])
                    tourrequest = TourRequest.objects.using(self._current_app_schema()).filter(
                        id=request_obj['tourgid'], entity_id=self._entity_id()).update(
                        tour_status=Status.APPROVED, entity_id=self._entity_id())

                if approvedby_applevel.applevel == App_level.THIRD_LEVEL:
                    tourrequest = TourRequest.objects.using(self._current_app_schema()).filter(
                        id=request_obj['tourgid'], entity_id=self._entity_id()).update(
                        tour_status=Status.APPROVED, entity_id=self._entity_id())

            # elif (request_obj['apptype']).lower() == TAStatus.advance:
            #     tour_id = int(request_obj['tourgid'])
            #     tourrequest = TourRequest.objects.using(self._current_app_schema()).get(id=tour_id,
            #                                                                             entity_id=self._entity_id())
            #     adv_data = TourAdvance.objects.using(self._current_app_schema()).filter(tour_id=tour_id,
            #                                                                             entity_id=self._entity_id()).last()
            #     if tourrequest.advance_status != Status.PENDING:
            #         error_obj = NWisefinError()
            #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #         error_obj.set_description(ErrorDescription.APPROVE_ERROR)
            #         return error_obj
            #
            #     if "appamount" in request_obj:
            #         request_obj["appamount"]=round(request_obj["appamount"],2)
            #         claimed_amount = adv_data.reqamount
            #         validation_service = Validation(self._scope())
            #         approved_amt_validation = validation_service.higher_approve_amount(claimed_amount,
            #                                                                            request_obj["appamount"])
            #         if approved_amt_validation != True:
            #             return approved_amt_validation
            #
            #
            #         request_obj["appamount"] = float(request_obj["appamount"])
            #         if request_obj["appamount"]<=0:
            #             error_obj = NWisefinError()
            #             error_obj.set_code(ErrorMessage.INVALID_DATA)
            #             error_obj.set_description(ErrorDescription.CLAIM_AMOUNT)
            #             return error_obj
            #
            #         Touramount = TourAdvance.objects.using(self._current_app_schema()).filter(id=adv_data.id,
            #                                                                                   entity_id=self._entity_id()).update(
            #             appamount=request_obj["appamount"],
            #             updated_by=employee_id,
            #             updated_date=time_function.standard_time(), entity_id=self._entity_id())
            #
            #         ccbs_obj = Ccbs.objects.using(self._current_app_schema()).filter(requestid=adv_data.id,
            #                                                                          entity_id=self._entity_id()).all()
            #         for each_ccbs in ccbs_obj:
            #             percentage = each_ccbs.percentage / 100
            #             Ccbs.objects.using(self._current_app_schema()).filter(id=each_ccbs.id,
            #                                                                   entity_id=self._entity_id()).update(
            #                 amount=request_obj["appamount"] * percentage,
            #                 updated_by=employee_id, updated_date=time_function.standard_time())
            #
            #
            #     if approver_data.applevel==App_level.FIRST_LEVEL:
            #         TravelHistory.objects.using(self._current_app_schema()).create(
            #             approvedby=Admin.ADMIN,
            #             approveddate=time_function.ist_time(),
            #             request_type=App_type.ADVANCE,
            #             applevel=App_level.THIRD_LEVEL,
            #             comment="",
            #             status=Status.PENDING,
            #             tour_id=request_obj['tourgid'],
            #             entity_id=self._entity_id())
            #     if approver_data.applevel==App_level.THIRD_LEVEL:
            #         # data = {"tourgid": tour_id, "type": "ADVANCE"}
            #         # jsondata = Ecf_data_req(data)
            #         # service = Ecf_entry(self._scope())
            #         # data = service.invoice_entry(jsondata, request,approver_code,maker_code)
            #         # if data["MESSAGE"].split(",")[0]=="SUCCESS":
            #         #     invoice_no=int(data["MESSAGE"].split(",")[-1])
            #         #     crn_no=self.get_crnno(invoice_no,tourrequest.empgid,request)
            #         tourrequest = TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id,
            #                                                                                    entity_id=self._entity_id()).update(
            #             advance_status=request_obj['status'], entity_id=self._entity_id())
            #
            #         crn_no = 0
            #         invoice_no = 0
            #         if int(request_obj['status']) == Status.APPROVED:
            #             adv = TourAdvance.objects.using(self._current_app_schema()).filter(tour_id=tour_id,
            #                                                                                status=Status.PENDING,
            #                                                                                entity_id=self._entity_id()).last()
            #             # TourAdvance.objects.using(self._current_app_schema()).filter(id=adv.id).update(status=Status_adv.APPROVED)
            #             TourAdvance.objects.using(self._current_app_schema()).filter(id=adv.id).update(
            #                 status=Status.APPROVED, crnno=crn_no, invoiceheadergid=invoice_no,
            #                 entity_id=self._entity_id())
            #
            #
            #
            #
            #
            #
            #
            #
            #
            #
            #
            #     # else:
            #     #     error_obj = NWisefinError()
            #     #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     #     error_obj.set_description(data)
            #     #     return error_obj

            # elif request_obj['apptype'] == TAStatus.claim:
            #     tourrequest = TourRequest.objects.using(self._current_app_schema()).filter(id=request_obj['tourgid']).update(
            #         claim_status=request_obj['status'])

            elif (request_obj['apptype']).lower() == TAStatus.tourcancel.lower():
                tourrequest = TourRequest.objects.using(self._current_app_schema()).get(id=request_obj['tourgid'],entity_id=self._entity_id())
                if tourrequest.tour_cancel_status != Status.PENDING:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.APPROVE_ERROR)
                    return error_obj
                tourrequest = TourRequest.objects.using(self._current_app_schema()).filter(id=request_obj['tourgid'],entity_id=self._entity_id()).update(
                    tour_cancel_status=Status.APPROVED,entity_id=self._entity_id())

            # elif (request_obj['apptype']).lower() == TAStatus.advancecancel.lower():
            #     tourrequest = TourRequest.objects.using(self._current_app_schema()).get(id=request_obj['tourgid'],entity_id=self._entity_id())
            #     if tourrequest.advance_cancel_status!= Status.PENDING:
            #         error_obj = NWisefinError()
            #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #         error_obj.set_description(ErrorDescription.APPROVE_ERROR)
            #         return error_obj
            #     tourrequest = TourRequest.objects.using(self._current_app_schema()).filter(id=request_obj['tourgid'],entity_id=self._entity_id()).update(
            #         advance_cancel_status=Status.APPROVED,entity_id=self._entity_id())

            approvedby = TravelHistory.objects.using(self._current_app_schema()).filter(id=request_obj['id'], entity_id=self._entity_id()).update(
                approveddate=time_function.ist_time(),
                comment=request_obj['appcomment'],approvedby=approver_nac,
                status=request_obj['status'],entity_id=self._entity_id(),
                onbehalfof_approval=login_emp)


            mail_service=ta_email(self._scope())
            mail_service.mail_data(request_obj['tourgid'])




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
            # except ApprovedBy.DoesNotExist:
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
        else:
            # try:
            employee_id = request.employee_id
            api_service = ApiService(self._scope())
            # rm_get = api_service.get_RM_ID(request, employee_id)
            # request_obj['approvedby']=rm_get
            logger.info('ta_ Tour_approve- ' + str(employee_id) + str(request_obj))

            approvedby = TravelHistory.objects.using(self._current_app_schema()).create(tour_id=request_obj['tourgid'],
                                                                                        approvedby=request_obj['approvedby'],
                                                                                        approveddate=time_function.ist_time(),
                                                                                        request_type=request_obj['apptype'],
                                                                                        applevel=request_obj['applevel'],
                                                                                        comment=request_obj['appcomment'],
                                                                                        status=request_obj['status'], entity_id=self._entity_id())

            if request_obj['apptype'] == TAStatus.tour:
                tourrequest=TourRequest.objects.using(self._current_app_schema()).filter(id=request_obj['tourgid'],entity_id=self._entity_id()).update(tour_status=request_obj['status'],entity_id=self._entity_id())

            # elif request_obj['apptype'] == TAStatus.advance:
            #     tourrequest=TourRequest.objects.using(self._current_app_schema()).filter(id=request_obj['tourgid'],entity_id=self._entity_id()).update(advance_status=request_obj['status'],entity_id=self._entity_id())

            elif request_obj['apptype'] == TAStatus.claim:
                tourrequest=TourRequest.objects.using(self._current_app_schema()).filter(id=request_obj['tourgid'],entity_id=self._entity_id()).update(claim_status=request_obj['status'],entity_id=self._entity_id())


            elif request_obj['apptype'] == TAStatus.tourcancel:
                tourrequest = TourRequest.objects.using(self._current_app_schema()).filter(id=request_obj['tourgid'],entity_id=self._entity_id()).update(
                    tour_cancel_status=Status.PENDING,entity_id=self._entity_id())

            # elif request_obj['apptype'] == TAStatus.advancecancel:
            #     tourrequest = TourRequest.objects.using(self._current_app_schema()).filter(id=request_obj['tourgid'],entity_id=self._entity_id()).update(
            #         advance_cancel_status=Status.PENDING,entity_id=self._entity_id())


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


    # def get_approverdata(self,empid,type,vys_page,status,makerid,request_date,tour_no,request):
    #     if request_date !="":
    #         request_date=(datetime.strptime(request_date, '%d-%b-%Y')).date()
    #
    #     # if type==App_type.ADVANCE:
    #     #
    #     #     condition = Q(approvedby=empid, apptype=type, applevel__gte=Status.REQUESTED, tour__request_date__icontains=request_date,
    #     #                   tour__id__icontains=tour_no,status=status,entity_id=self._entity_id())
    #     #     if makerid is not None:
    #     #         condition &= Q(tour__empgid=makerid)
    #     #
    #     #     # if status is not None:
    #     #     #     condition &= Q(tour__advance_status=status)
    #     #
    #     #     approverdata=TravelHistory.objects.using(self._current_app_schema()).filter(condition).order_by('-id')
    #     #
    #     #     # if status is None and makerid is None:
    #     #     #     approverdata = ApprovedBy.objects.using(self._current_app_schema()).filter(Q(approvedby=empid, apptype=type, applevel=2,tour__request_date__icontains=request_date,tour__id__icontains=tour_no) |
    #     #     #                                              Q(approvedby=empid, apptype=type, applevel=1,tour__request_date__icontains=request_date,tour__id__icontains=tour_no)).all()
    #     #     # elif status is not None and makerid is None:
    #     #     #     approverdata = ApprovedBy.objects.using(self._current_app_schema()).filter(Q(approvedby=empid, apptype=type, applevel=2, status=status,tour__request_date__icontains=request_date,tour__id__icontains=tour_no) |
    #     #     #                                              Q(approvedby=empid, apptype=type, applevel=1,status=status,tour__request_date__icontains=request_date,tour__id__icontains=tour_no)).all()
    #     #     # elif status is None and makerid is not None:
    #     #     #     approverdata = ApprovedBy.objects.using(self._current_app_schema()).filter(
    #     #     #         Q(approvedby=empid, apptype=type, applevel=2, tour__empgid=makerid,tour__request_date__icontains=request_date,tour__id__icontains=tour_no) |
    #     #     #         Q(approvedby=empid, apptype=type, applevel=1, tour__empgid=makerid,tour__request_date__icontains=request_date,tour__id__icontains=tour_no)).all()
    #     #     # # elif status is not None and makerid is not None:
    #     #     # else:
    #     #     #     approverdata = ApprovedBy.objects.using(self._current_app_schema()).filter(
    #     #     #         Q(approvedby=empid, apptype=type, applevel=2, status=status, tour__empgid=makerid,tour__request_date__icontains=request_date,tour__id__icontains=tour_no) |
    #     #     #         Q(approvedby=empid, apptype=type, applevel=1, status=status, tour__empgid=makerid,tour__request_date__icontains=request_date,tour__id__icontains=tour_no))
    #     #
    #     #     unique_tour = []
    #     #     approvedby_id = []
    #     #     for data in approverdata:
    #     #         if len(unique_tour) <= vys_page.get_query_limit():
    #     #             if data.tour_id not in unique_tour:
    #     #                 unique_tour.append(data.tour_id)
    #     #                 approvedby_id.append(data.id)
    #     #     # print("unique_tour",unique_tour)
    #     #     # print("approvedby_id",approvedby_id)
    #     #     approverdata = TravelHistory.objects.using(self._current_app_schema()).filter(id__in=approvedby_id, entity_id=self._entity_id()).all().order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]
    #
    #     elif type=='TOURCANCEL' :
    #
    #         if type=='TOURCANCEL':
    #             type=App_type.TourCancel
    #         # elif type=='ADVANCECANCEL':
    #         #     type=App_type.AdvanceCancel
    #
    #         condition=Q(approvedby=empid, request_type=type, applevel__gte=Status.REQUESTED,tour__request_date__icontains=request_date,tour__id__icontains=tour_no,status=status,entity_id=self._entity_id())
    #         if makerid is not None:
    #             condition &=Q(tour__empgid=makerid)
    #
    #         if status is not None:
    #             # if type==App_type.TOUR:
    #             #     condition &= Q(tour__tour_status=status)
    #             # elif type==App_type.CLAIM:
    #             #     condition &= Q(tour__claim_status=status)
    #             if type==App_type.TourCancel:
    #                 condition &= Q(tour__tour_cancel_status=status)
    #             # elif type==App_type.AdvanceCancel:
    #             #     condition &= Q(tour__advance_cancel_status=status)
    #
    #
    #         approverdata= TravelHistory.objects.using(self._current_app_schema()).filter(condition).order_by('-id')[
    #                                                         vys_page.get_offset():vys_page.get_query_limit()]
    #
    #     elif type==App_type.TOUR :
    #         condition = Q(approvedby=empid, request_type=type, applevel__gte=Status.REQUESTED, tour__request_date__icontains=request_date,applevel__in=[App_level.FIRST_LEVEL,App_level.SECOND_LEVEL],
    #                       tour__id__icontains=tour_no,status=status,entity_id=self._entity_id())
    #         if makerid is not None:
    #             condition &= Q(tour__empgid=makerid)
    #         Tour_3 = TravelHistory.objects.using(self._current_app_schema()).filter(condition).values('tour').annotate(id=Max('id')).order_by('-tour_id')[
    #                        vys_page.get_offset():vys_page.get_query_limit()]
    #         arr_list=[]
    #         for each_tour in Tour_3:
    #             arr_list.append(each_tour['id'])
    #         approverdata = TravelHistory.objects.using(self._current_app_schema()).filter(id__in=arr_list, entity_id=self._entity_id()).order_by('-tour_id')
    #
    #     elif type==App_type.CLAIM:
    #         condition = Q(approvedby=empid, request_type=type, applevel__gte=Status.REQUESTED, tour__request_date__icontains=request_date,applevel__in=[App_level.FIRST_LEVEL,App_level.SECOND_LEVEL],
    #                       tour__id__icontains=tour_no,status=status,entity_id=self._entity_id())
    #         if makerid is not None:
    #             condition &= Q(tour__empgid=makerid)
    #         Tour_3 = TravelHistory.objects.using(self._current_app_schema()).filter(condition).values('tour').annotate(id=Max('id')).order_by('-tour_id')[
    #                        vys_page.get_offset():vys_page.get_query_limit()]
    #         arr_list=[]
    #         for each_tour in Tour_3:
    #             arr_list.append(each_tour['id'])
    #         approverdata = TravelHistory.objects.using(self._current_app_schema()).filter(id__in=arr_list, entity_id=self._entity_id()).order_by('-tour_id')
    #
    #         # Tour = ApprovedBy.objects.using(self._current_app_schema()).filter(approvedby=empid, apptype=type, status=status).values(
    #         #     'approvedby', 'onbehalfof', 'approveddate', 'apptype', 'applevel', 'status','appcomment', 'tour'
    #         # ).annotate(dcount=Max('tour_id')).order_by('-tour_id')
    #         #
    #         # Tour_2=ApprovedBy.objects.using(self._current_app_schema()).filter(approvedby=empid, apptype=type, status=status).values(
    #         #     'tour', "apptype", "approvedby", "onbehalfof", "approveddate", "applevel", "status"
    #         #     ).annotate(tour_id=Max('tour_id')).order_by('-tour_id')
    #         # Tour_3=ApprovedBy.objects.using(self._current_app_schema()).filter(approvedby=empid, apptype=type, status=status).values(
    #         #     'approvedby', 'onbehalfof', 'approveddate', 'apptype', 'applevel', 'status', 'tour'
    #         #     ).annotate(tour_id=Max('tour_id')).order_by('-tour_id')
    #
    #         # if int(status)==5:
    #         #     if type==App_type.TOUR:
    #         #         condition &= Q(tour__tour_status=5)
    #         #     if type==App_type.CLAIM:
    #         #         condition &= Q(tour__claim_status=5)
    #         # if int(status)==6:
    #         #     if type=='TOUR':
    #         #         condition &= Q(tour__tour_status=6)| Q( tour__tour_status=2)
    #         #     if type=='CLAIM':
    #         #         condition &= Q(tour__claim_status=6)|Q( tour__tour_status=2)
    #         # approverdata = ApprovedBy.objects.using(self._current_app_schema()).filter(condition).order_by('-id')[
    #         #                vys_page.get_offset():vys_page.get_query_limit()]
    #         # print(len(Tour), len(approverdata))
    #
    #         # if status is None and makerid is None:
    #         #     approverdata = ApprovedBy.objects.using(self._current_app_schema()).filter(Q(approvedby=empid, apptype=type, applevel=2,tour__request_date__icontains=request_date,tour__id__icontains=tour_no) |
    #         #                                              Q(approvedby=empid, apptype=type, applevel=1,tour__request_date__icontains=request_date,tour__id__icontains=tour_no)).all().order_by('-id')[
    #         #                                                 vys_page.get_offset():vys_page.get_query_limit()]
    #         # elif status is not None and makerid is None:
    #         #     approverdata = ApprovedBy.objects.using(self._current_app_schema()).filter(Q(approvedby=empid, apptype=type, applevel=2,status=status ,tour__request_date__icontains=request_date,tour__id__icontains=tour_no) |
    #         #                                              Q(approvedby=empid, apptype=type, applevel=1,status=status,tour__request_date__icontains=request_date,tour__id__icontains=tour_no)).all().order_by('-id')[
    #         #                                                 vys_page.get_offset():vys_page.get_query_limit()]
    #         # elif status is None and makerid is not None:
    #         #     approverdata = ApprovedBy.objects.using(self._current_app_schema()).filter(Q(approvedby=empid, apptype=type, applevel=2,tour__empgid=makerid ,tour__request_date__icontains=request_date,tour__id__icontains=tour_no) |
    #         #                                              Q(approvedby=empid, apptype=type, applevel=1,tour__empgid=makerid,tour__request_date__icontains=request_date,tour__id__icontains=tour_no)).all().order_by('-id')[
    #         #                                                 vys_page.get_offset():vys_page.get_query_limit()]
    #         # elif status is not None and makerid is not None:
    #         # else:
    #             # approverdata = ApprovedBy.objects.using(self._current_app_schema()).filter(Q(approvedby=empid , apptype=type , applevel=2, status=status,tour__empgid=makerid,
    #             #                                                                  tour__request_date__icontains=request_date,tour__id__icontains=tour_no,tour__tour_status=tour_status,
    #             #                                                                  tour__advance_status=advance_status,tour__claim_status=claim_status,tour__tour_cancel_status=tc_status,
    #             #                                                                  tour__advance_cancel_status=ac_status
    #             #                                                                  )) .all().order_by('-id')[
    #             #                                             vys_page.get_offset():vys_page.get_query_limit()]
    #     resp_list = NWisefinList()
    #     if len(approverdata) > 0:
    #         for apr in approverdata:
    #             # Tour = TourRequest.objects.using(self._current_app_schema()).get(id=apr.tour_id)
    #             Tour=apr.tour
    #             emp_id = Tour.empgid
    #             empdtl = ApiService(self._scope())
    #             detail=emp_dtl(self._scope())
    #             employee = empdtl.employee_details_get(emp_id,request)
    #             # code = empdtl.employee_code_get(emp_id)
    #             tour_apr = TourMakerResponse()
    #             tour_apr.set_employee_name(employee.full_name)
    #             tour_apr.set_employee_code(employee.code)
    #             tour_apr.set_tourid(Tour.id)
    #             # tour_apr.set_requestno(Tour.requestno)
    #             tour_apr.set_requestdate(Tour.request_date)
    #             tour_apr.set_empgid(Tour.empgid)
    #             tour_apr.set_empdesignation(Tour.empdesignation)
    #             tour_apr.set_empgrade(Tour.empgrade)
    #             tour_apr.set_empbranchgid(Tour.empbranchgid)
    #
    #             branch=empdtl.get_branch_data(Tour.empbranchgid,request)
    #             tour_apr.set_branch_name(branch.name)
    #             # brcode=empdtl.get_branch_code(Tour.empbranchgid)
    #             tour_apr.set_branch_code(branch.code)
    #
    #             reason = detail.get_reason_name(Tour.reason)
    #             tour_apr.set_reason(reason)
    #             tour_apr.set_startdate(Tour.start_date)
    #             tour_apr.set_enddate(Tour.end_date)
    #             tour_apr.set_quantum_of_funds(Tour.quantum_of_funds)
    #             tour_apr.set_opening_balance(Tour.opening_balance)
    #             tour_apr.set_id(apr.id)
    #             approver=empdtl.employee_details_get(apr.approvedby,request)
    #             tour_apr.set_approvedby(approver.full_name)
    #             tour_apr.set_approver_code(approver.code)
    #             tour_apr.set_approver_id(apr.approvedby)
    #             raised_by_data=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=Tour.id, request_type=type, applevel=App_level.ZERO_LEVEL, id__lt=apr.id, entity_id=self._entity_id()).order_by("-id")
    #             if len(raised_by_data)!=0:
    #                 raised_by_data=raised_by_data[0]
    #                 # if raised_by_data.onbehalfof > 0:
    #                 #     onbehalfof = empdtl.employee_details_get(raised_by_data.onbehalfof ,request)
    #                 #     # tour_apr.set_onbehalfof(onbehalfof)
    #                 # else:
    #                 onbehalfof = empdtl.employee_details_get(raised_by_data.approvedby, request)
    #                 tour_apr.set_onbehalfof(onbehalfof)
    #             tour_apr.set_approveddate(apr.approveddate)
    #             tour_apr.set_apptype(apr.request_type)
    #             tour_apr.set_applevel(apr.applevel)
    #             tour_apr.set_appcomment(apr.comment)
    #             tour_apr.set_status(apr.status)
    #             status_name = status_get(apr.status)
    #             tour_apr.set_status_name(status_name)
    #
    #             # if type=='TOUR' and Tour.tour_status==Status.FORWARDED:
    #             if type==App_type.TOUR :
    #                 Tour.tour_status=int(status)
    #             # elif type=='CLAIM' and Tour.claim_status==Status.FORWARDED:
    #             elif type==App_type.CLAIM:
    #                 Tour.claim_status=int(status)
    #             tour_status = status_get(Tour.tour_status)
    #             # advance_status = status_get(Tour.advance_status)
    #             claim_status = status_get(Tour.claim_status)
    #             tour_cancel_status = status_get(Tour.tour_cancel_status)
    #             # advance_cancel_status = status_get(Tour.advance_cancel_status)
    #             tour_apr.set_tour_status(tour_status)
    #             tour_apr.set_tour_cancel_status(tour_cancel_status)
    #             # tour_apr.set_advance_status(advance_status)
    #             # tour_apr.set_advance_cancel_status(advance_cancel_status)
    #             tour_apr.set_claim_status(claim_status)
    #             tour_apr.set_tour_cancel_status_id(Tour.tour_cancel_status)
    #             tour_apr.set_tour_status_id(Tour.tour_status)
    #             # tour_apr.set_advance_cancel_status_id(Tour.advance_cancel_status)
    #             # tour_apr.set_advance_status_id(Tour.advance_status)
    #             tour_apr.set_claim_status_id(Tour.claim_status)
    #
    #
    #             # if type==App_type.ADVANCE:
    #             #     tourapprovedby = TravelHistory.objects.using(self._current_app_schema()).filter(tour_id =Tour.id, status=Status.APPROVED, entity_id=self._entity_id())
    #             #     if len(tourapprovedby)==0:
    #             #         tour_apr.set_tour_approvedby(None)
    #             #     else:
    #             #         tour_apr.set_tour_approvedby(tourapprovedby.last().approvedby)
    #             #
    #             #     adv_condition=Q(tour_id=Tour.id,entity_id=self._entity_id())
    #             #     status=int(status)
    #             #     if status==Status.APPROVED:
    #             #         adv_condition &=Q(status=Status_adv.APPROVED)
    #             #     if status==Status.REJECTED:
    #             #         adv_condition &= Q(status=Status_adv.REJECTED)
    #             #     if status==Status.PENDING:
    #             #         adv_condition &= Q(status=Status_adv.PENDING)
    #             #     else:
    #             #         pass
    #             #     advance_list=TourAdvance.objects.using(self._current_app_schema()).filter(adv_condition).order_by("-id")
    #             #     req_amt = 0
    #             #     app_amt = 0
    #             #     if len(advance_list) !=0:
    #             #         req_amt=advance_list[0].reqamount
    #             #         app_amt=advance_list[0].appamount
    #             #     # adv_amt=0
    #             #     # for advance in advance_list:
    #             #     #     adv_amt=advance.appamount+adv_amt
    #             #     tour_apr.set_requested_amount(req_amt)
    #             #     tour_apr.set_approved_amount(app_amt)
    #             #
    #             #     # advance_list = TourAdvance.objects.using(self._current_app_schema()).filter(tour_id=Tour.id, status=Status_adv.APPROVED,entity_id=self._entity_id())
    #             #     # total_advance = 0
    #             #     # for advance in advance_list:
    #             #     #     total_advance = advance.appamount + total_advance
    #             #     # tour_apr.set_total_advance(total_advance)
    #
    #             if type==App_type.CLAIM:
    #                 claimed_amount=0
    #                 claim=ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=Tour.id,entity_id=self._entity_id())
    #                 for each_claim in claim:
    #                     claimed_amount+=each_claim.claimedamount
    #                 tour_apr.set_claim_amount(claimed_amount)
    #
    #             resp_list.append(tour_apr)
    #         vpage = NWisefinPaginator(approverdata, vys_page.get_index(), 10)
    #         resp_list.set_pagination(vpage)
    #     return resp_list

    def nac_get_approverdata(self,empid,type,vys_page,status,makerid,request_date,tour_no,request,onbehalf,branch_id,cancel):
        if request_date != "":
            try:
                request_date = int(request_date)
                request_date = str(datetime.fromtimestamp(int(request_date) / 1000.0))
                request_date = (datetime.strptime(request_date[:10], '%Y-%m-%d')).date()
            except:
                request_date = (datetime.strptime(request_date, '%d-%b-%Y')).date()

        api_service = ApiService(self._scope())
        ceo_get = api_service.onb_permission(request, empid)
        if type==App_type.ADVANCE:
            if cancel== 1:
                apptype_data = [App_type.AdvanceCancel]
            elif cancel==0:
                apptype_data = [App_type.ADVANCE]
            else:
                apptype_data = [App_type.ADVANCE, App_type.AdvanceCancel]

            if onbehalf is None:
                # if (json.loads(ceo_get))["ceo"] == True:
                #     condition = Q(request_type__in=apptype_data,
                #                   applevel__in=[App_level.FIRST_LEVEL, App_level.SECOND_LEVEL],
                #                   tour__request_date__icontains=request_date,
                #                   tour__id__icontains=tour_no, status=status, entity_id=self._entity_id(),
                #                   approvedby__in=[empid, Admin.CEO])
                #     if makerid is not None:
                #         api_service = ApiService(self._scope())
                #         maker_id = api_service.get_emp_name(request, makerid)
                #         condition &= Q(tour__empgid__in=maker_id)
                #     if branch_id is not None:
                #         api_service = ApiService(self._scope())
                #         branch_id = api_service.get_emp_branchid(request, branch_id)
                #         condition &= Q(tour__empgid__in=branch_id)
                # else:
                module_permission = ApiService(self._scope())
                role_arr = module_permission.employee_modulerole_get(empid, ModuleList.Ta_Expense, request)

                if RoleList.admin in role_arr:
                    filter_applevel=[App_level.FIRST_LEVEL,App_level.THIRD_LEVEL]
                    empid_arr=[empid,Admin.ADMIN]
                else:
                    filter_applevel = [App_level.FIRST_LEVEL]
                    empid_arr=[empid]

                condition = Q(approvedby__in=empid_arr, request_type__in=apptype_data,
                              applevel__in=filter_applevel,
                              tour__request_date__icontains=request_date,
                              tour__id__icontains=tour_no, status=status, entity_id=self._entity_id())
                if makerid is not None:
                    api_service = ApiService(self._scope())
                    maker_id = api_service.get_emp_name(request, makerid)
                    condition &= Q(tour__empgid__in=maker_id)
                if branch_id is not None:
                    api_service = ApiService(self._scope())
                    branch_id = api_service.get_emp_branchid(request, branch_id)
                    condition &= Q(tour__empgid__in=branch_id)
            else:

                if int(status) == Status.PENDING:
                    onbehalfof_approval = [empid, 0]
                else:
                    onbehalfof_approval = [empid]

                if (json.loads(ceo_get))["ceo"] == True:
                    condition = Q(request_type__in=apptype_data,
                                  applevel__in=[App_level.FIRST_LEVEL, App_level.SECOND_LEVEL],
                                  tour__request_date__icontains=request_date,
                                  tour__id__icontains=tour_no, status=status, entity_id=self._entity_id(),
                                  approvedby__in=[onbehalf, Admin.CEO], onbehalfof_approval__in=onbehalfof_approval)
                    if makerid is not None:
                        api_service = ApiService(self._scope())
                        maker_id = api_service.get_emp_name(request, makerid)
                        condition &= Q(tour__empgid__in=maker_id)
                    if branch_id is not None:
                        api_service = ApiService(self._scope())
                        branch_id = api_service.get_emp_branchid(request, branch_id)
                        condition &= Q(tour__empgid__in=branch_id)
                else:
                    condition = Q(approvedby=onbehalf, request_type__in=apptype_data,
                                  applevel__in=[App_level.FIRST_LEVEL],
                                  tour__request_date__icontains=request_date,
                                  onbehalfof_approval__in=onbehalfof_approval,
                                  tour__id__icontains=tour_no, status=status, entity_id=self._entity_id())
                    if makerid is not None:
                        api_service = ApiService(self._scope())
                        maker_id = api_service.get_emp_name(request, makerid)
                        condition &= Q(tour__empgid__in=maker_id)
                    if branch_id is not None:
                        api_service = ApiService(self._scope())
                        branch_id = api_service.get_emp_branchid(request, branch_id)

                        condition &= Q(tour__empgid__in=branch_id)

            """condition = Q(approvedby=empid,
             apptype__in=type, 
             applevel__gte=Status.REQUESTED, 
             tour__request_date__icontains=request_date,
                          tour__id__icontains=tour_no,status=status,entity_id=self._entity_id())
            if makerid is not None:
                condition &= Q(tour__empgid=makerid)"""

            # if status is not None:
            #     condition &= Q(tour__advance_status=status)

            approverdata=TravelHistory.objects.using(self._current_app_schema()).filter(condition).order_by('-id')

            unique_tour = []
            approvedby_id = []
            for data in approverdata:
                if len(unique_tour) <= vys_page.get_query_limit():
                    if data.tour_id not in unique_tour:
                        unique_tour.append(data.tour_id)
                        approvedby_id.append(data.id)
            # print("unique_tour",unique_tour)
            # print("approvedby_id",approvedby_id)
            approverdata = TravelHistory.objects.using(self._current_app_schema()).filter(id__in=approvedby_id, entity_id=self._entity_id()).all().order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]

        # elif type=='TOURCANCEL' or type=='ADVANCECANCEL':
        #
        #     if type=='TOURCANCEL':
        #         type=App_type.TourCancel
        #     elif type=='ADVANCECANCEL':
        #         type=App_type.AdvanceCancel
        #
        #     condition=Q(approvedby=empid, apptype=type, applevel__gte=Status.REQUESTED,tour__request_date__icontains=request_date,tour__id__icontains=tour_no,status=status,entity_id=self._entity_id())
        #     if makerid is not None:
        #         condition &=Q(tour__empgid=makerid)
        #
        #     if status is not None:
        #         # if type==App_type.TOUR:
        #         #     condition &= Q(tour__tour_status=status)
        #         # elif type==App_type.CLAIM:
        #         #     condition &= Q(tour__claim_status=status)
        #         if type==App_type.TourCancel:
        #             condition &= Q(tour__tour_cancel_status=status,entity_id=self._entity_id())
        #         elif type==App_type.AdvanceCancel:
        #             condition &= Q(tour__advance_cancel_status=status,entity_id=self._entity_id())
        #
        #
        #     approverdata=ApprovedBy.objects.using(self._current_app_schema()).filter(condition).order_by('-id')[
        #                                                     vys_page.get_offset():vys_page.get_query_limit()]


        elif type==App_type.TOUR:

            if cancel== 1:
                apptype_data = [App_type.TourCancel]
            elif cancel==0:
                apptype_data = [App_type.TOUR]
            else:
                apptype_data = [App_type.TOUR, App_type.TourCancel]

            if onbehalf is None:
                if (json.loads(ceo_get))["ceo"] == True:
                    condition = Q(request_type__in=apptype_data, applevel__in=[App_level.FIRST_LEVEL,App_level.SECOND_LEVEL], tour__request_date__icontains=request_date,
                                  tour__id__icontains=tour_no,status=status,entity_id=self._entity_id(),approvedby__in=[empid,Admin.CEO])
                    if makerid is not None:
                        api_service = ApiService(self._scope())
                        maker_id = api_service.get_emp_name(request, makerid)
                        condition &= Q(tour__empgid__in=maker_id)
                    if branch_id is not None:
                        api_service = ApiService(self._scope())
                        branch_id = api_service.get_emp_branchid(request, branch_id)
                        condition &= Q(tour__empgid__in=branch_id)
                else:
                    condition = Q(approvedby=empid, request_type__in=apptype_data,
                                  applevel__in=[App_level.FIRST_LEVEL],
                                  tour__request_date__icontains=request_date,
                                  tour__id__icontains=tour_no, status=status, entity_id=self._entity_id())
                    if makerid is not None:
                        api_service = ApiService(self._scope())
                        maker_id = api_service.get_emp_name(request, makerid)
                        condition &= Q(tour__empgid__in=maker_id)
                    if branch_id is not None:
                        api_service = ApiService(self._scope())
                        branch_id = api_service.get_emp_branchid(request, branch_id)
                        condition &= Q(tour__empgid__in=branch_id)
            else:

                if int(status)==Status.PENDING:
                    onbehalfof_approval=[empid,0]
                else:
                    onbehalfof_approval = [empid]


                if (json.loads(ceo_get))["ceo"] == True:
                    condition = Q(request_type__in=apptype_data, applevel__in=[App_level.FIRST_LEVEL,App_level.SECOND_LEVEL], tour__request_date__icontains=request_date,
                                  tour__id__icontains=tour_no,status=status,entity_id=self._entity_id(),approvedby__in=[onbehalf,Admin.CEO],onbehalfof_approval__in=onbehalfof_approval)
                    if makerid is not None:
                        api_service = ApiService(self._scope())
                        maker_id = api_service.get_emp_name(request, makerid)
                        condition &= Q(tour__empgid__in=maker_id)
                    if branch_id is not None:
                        api_service = ApiService(self._scope())
                        branch_id = api_service.get_emp_branchid(request, branch_id)
                        condition &= Q(tour__empgid__in=branch_id)
                else:
                    condition = Q(approvedby=onbehalf, request_type__in=apptype_data,
                                  applevel__in=[App_level.FIRST_LEVEL],
                                  tour__request_date__icontains=request_date,onbehalfof_approval__in=onbehalfof_approval,
                                  tour__id__icontains=tour_no, status=status, entity_id=self._entity_id())
                    if makerid is not None:
                        api_service = ApiService(self._scope())
                        maker_id = api_service.get_emp_name(request, makerid)
                        condition &= Q(tour__empgid__in=maker_id)
                    if branch_id is not None:
                        api_service = ApiService(self._scope())
                        branch_id = api_service.get_emp_branchid(request, branch_id)

                        condition &= Q(tour__empgid__in=branch_id)

            Tour_3 = TravelHistory.objects.using(self._current_app_schema()).filter(condition).values('tour').annotate(id=Max('id')).order_by('-tour_id')[
                           vys_page.get_offset():vys_page.get_query_limit()]
            arr_list=[]
            for each_tour in Tour_3:
                arr_list.append(each_tour['id'])
            approverdata = TravelHistory.objects.using(self._current_app_schema()).filter(id__in=arr_list, entity_id=self._entity_id()).order_by('-id')
        elif type==App_type.CLAIM:
            if onbehalf is None:
                if int(status)==Status.PENDING:
                    module_permission = ApiService(self._scope())
                    role_arr = module_permission.employee_modulerole_get(empid,ModuleList.Ta_Expense,request)

                    if RoleList.admin in role_arr:
                        condition = Q(request_type=type, applevel__in=[App_level.FIRST_LEVEL,App_level.SECOND_LEVEL,App_level.THIRD_LEVEL], tour__request_date__icontains=request_date,
                                      tour__id__icontains=tour_no,status=status,entity_id=self._entity_id(),approvedby__in=[empid,Admin.ADMIN])
                    else:
                        condition = Q(approvedby=empid, request_type=type,
                                      applevel__in=[App_level.FIRST_LEVEL, App_level.SECOND_LEVEL, App_level.THIRD_LEVEL],
                                      tour__request_date__icontains=request_date,
                                      tour__id__icontains=tour_no, status=status, entity_id=self._entity_id())
                else:
                    module_permission = ApiService(self._scope())
                    role_arr = module_permission.employee_modulerole_get(empid, ModuleList.Ta_Expense, request)

                    if RoleList.admin in role_arr:
                        if int(status) == 7:
                            condition = Q(request_type=type,
                                          applevel__in=[App_level.THIRD_LEVEL],
                                          tour__request_date__icontains=request_date,
                                          tour__id__icontains=tour_no, status=Status.APPROVED, entity_id=self._entity_id())
                        else:
                            condition = Q(approvedby=empid, request_type=type,
                                          applevel__in=[App_level.FIRST_LEVEL, App_level.SECOND_LEVEL,
                                                        App_level.THIRD_LEVEL],
                                          tour__request_date__icontains=request_date,
                                          tour__id__icontains=tour_no, status=status, entity_id=self._entity_id())
                    else:

                        condition = Q(approvedby=empid, request_type=type,
                                      applevel__in=[App_level.FIRST_LEVEL, App_level.SECOND_LEVEL, App_level.THIRD_LEVEL],
                                      tour__request_date__icontains=request_date,
                                      tour__id__icontains=tour_no, status=status, entity_id=self._entity_id())
            else:
                if int(status)==Status.PENDING:
                    onbehalfof_approval = [empid, 0]

                    module_permission = ApiService(self._scope())
                    role_arr = module_permission.employee_modulerole_get(empid,ModuleList.Ta_Expense,request)

                    if RoleList.admin in role_arr:
                        condition = Q(request_type=type, applevel__in=[App_level.FIRST_LEVEL,App_level.SECOND_LEVEL,App_level.THIRD_LEVEL], tour__request_date__icontains=request_date,
                                      tour__id__icontains=tour_no,status=status,entity_id=self._entity_id(),approvedby__in=[onbehalf,Admin.ADMIN],onbehalfof_approval__in=onbehalfof_approval)
                    else:
                        condition = Q(approvedby=onbehalf, request_type=type,
                                      applevel__in=[App_level.FIRST_LEVEL, App_level.SECOND_LEVEL, App_level.THIRD_LEVEL],
                                      tour__request_date__icontains=request_date,
                                      tour__id__icontains=tour_no, status=status, entity_id=self._entity_id(),onbehalfof_approval__in=onbehalfof_approval)
                else:
                    module_permission = ApiService(self._scope())
                    role_arr = module_permission.employee_modulerole_get(empid, ModuleList.Ta_Expense, request)

                    if RoleList.admin in role_arr:
                        if int(status) == 7:
                            condition = Q(request_type=type,
                                          applevel__in=[App_level.THIRD_LEVEL],
                                          tour__request_date__icontains=request_date,
                                          tour__id__icontains=tour_no, status=Status.APPROVED, entity_id=self._entity_id())
                        else:
                            condition = Q(approvedby=onbehalf, request_type=type,
                                          applevel__in=[App_level.FIRST_LEVEL, App_level.SECOND_LEVEL,
                                                        App_level.THIRD_LEVEL],
                                          tour__request_date__icontains=request_date,
                                          tour__id__icontains=tour_no, status=status, entity_id=self._entity_id(),
                                          onbehalfof_approval=empid)
                    else:
                        condition = Q(approvedby=onbehalf, request_type=type,
                                      applevel__in=[App_level.FIRST_LEVEL, App_level.SECOND_LEVEL, App_level.THIRD_LEVEL],
                                      tour__request_date__icontains=request_date,
                                      tour__id__icontains=tour_no, status=status, entity_id=self._entity_id(),onbehalfof_approval=empid)

            if makerid is not None:
                api_service = ApiService(self._scope())
                maker_id = api_service.get_emp_name(request, makerid)
                condition &= Q(tour__empgid__in=maker_id)
            if branch_id is not None:
                api_service = ApiService(self._scope())
                branch_id = api_service.get_emp_branchid(request, branch_id)
                condition &= Q(tour__empgid__in=branch_id)
            Tour_3 = TravelHistory.objects.using(self._current_app_schema()).filter(condition).values('tour').annotate(id=Max('id')).order_by('-tour_id')[
                           vys_page.get_offset():vys_page.get_query_limit()]
            arr_list=[]
            for each_tour in Tour_3:
                arr_list.append(each_tour['id'])
            approverdata = TravelHistory.objects.using(self._current_app_schema()).filter(id__in=arr_list, entity_id=self._entity_id()).order_by('-tour_id')

            # Tour = ApprovedBy.objects.using(self._current_app_schema()).filter(approvedby=empid, apptype=type, status=status).values(
            #     'approvedby', 'onbehalfof', 'approveddate', 'apptype', 'applevel', 'status','appcomment', 'tour'
            # ).annotate(dcount=Max('tour_id')).order_by('-tour_id')
            #
            # Tour_2=ApprovedBy.objects.using(self._current_app_schema()).filter(approvedby=empid, apptype=type, status=status).values(
            #     'tour', "apptype", "approvedby", "onbehalfof", "approveddate", "applevel", "status"
            #     ).annotate(tour_id=Max('tour_id')).order_by('-tour_id')
            # Tour_3=ApprovedBy.objects.using(self._current_app_schema()).filter(approvedby=empid, apptype=type, status=status).values(
            #     'approvedby', 'onbehalfof', 'approveddate', 'apptype', 'applevel', 'status', 'tour'
            #     ).annotate(tour_id=Max('tour_id')).order_by('-tour_id')

            # if int(status)==5:
            #     if type==App_type.TOUR:
            #         condition &= Q(tour__tour_status=5)
            #     if type==App_type.CLAIM:
            #         condition &= Q(tour__claim_status=5)
            # if int(status)==6:
            #     if type=='TOUR':
            #         condition &= Q(tour__tour_status=6)| Q( tour__tour_status=2)
            #     if type=='CLAIM':
            #         condition &= Q(tour__claim_status=6)|Q( tour__tour_status=2)
            # approverdata = ApprovedBy.objects.using(self._current_app_schema()).filter(condition).order_by('-id')[
            #                vys_page.get_offset():vys_page.get_query_limit()]
            # print(len(Tour), len(approverdata))

            # if status is None and makerid is None:
            #     approverdata = ApprovedBy.objects.using(self._current_app_schema()).filter(Q(approvedby=empid, apptype=type, applevel=2,tour__request_date__icontains=request_date,tour__id__icontains=tour_no) |
            #                                              Q(approvedby=empid, apptype=type, applevel=1,tour__request_date__icontains=request_date,tour__id__icontains=tour_no)).all().order_by('-id')[
            #                                                 vys_page.get_offset():vys_page.get_query_limit()]
            # elif status is not None and makerid is None:
            #     approverdata = ApprovedBy.objects.using(self._current_app_schema()).filter(Q(approvedby=empid, apptype=type, applevel=2,status=status ,tour__request_date__icontains=request_date,tour__id__icontains=tour_no) |
            #                                              Q(approvedby=empid, apptype=type, applevel=1,status=status,tour__request_date__icontains=request_date,tour__id__icontains=tour_no)).all().order_by('-id')[
            #                                                 vys_page.get_offset():vys_page.get_query_limit()]
            # elif status is None and makerid is not None:
            #     approverdata = ApprovedBy.objects.using(self._current_app_schema()).filter(Q(approvedby=empid, apptype=type, applevel=2,tour__empgid=makerid ,tour__request_date__icontains=request_date,tour__id__icontains=tour_no) |
            #                                              Q(approvedby=empid, apptype=type, applevel=1,tour__empgid=makerid,tour__request_date__icontains=request_date,tour__id__icontains=tour_no)).all().order_by('-id')[
            #                                                 vys_page.get_offset():vys_page.get_query_limit()]
            # elif status is not None and makerid is not None:
            # else:
                # approverdata = ApprovedBy.objects.using(self._current_app_schema()).filter(Q(approvedby=empid , apptype=type , applevel=2, status=status,tour__empgid=makerid,
                #                                                                  tour__request_date__icontains=request_date,tour__id__icontains=tour_no,tour__tour_status=tour_status,
                #                                                                  tour__advance_status=advance_status,tour__claim_status=claim_status,tour__tour_cancel_status=tc_status,
                #                                                                  tour__advance_cancel_status=ac_status
                #                                                                  )) .all().order_by('-id')[
                #                                             vys_page.get_offset():vys_page.get_query_limit()]
        resp_list = NWisefinList()
        if len(approverdata) > 0:
            for apr in approverdata:
                # Tour = TourRequest.objects.using(self._current_app_schema()).get(id=apr.tour_id)
                Tour=apr.tour
                emp_id = Tour.empgid
                empdtl = ApiService(self._scope())
                detail=emp_dtl(self._scope())
                employee = empdtl.employee_details_get(emp_id,request)
                # code = empdtl.employee_code_get(emp_id)
                tour_apr = TourMakerResponse()
                tour_apr.set_employee_name(employee.full_name)
                tour_apr.set_employee_code(employee.code)
                tour_apr.set_tourid(Tour.id)
                # tour_apr.set_requestno(Tour.requestno)
                tour_apr.set_requestdate(Tour.request_date)
                tour_apr.set_empgid(Tour.empgid)
                tour_apr.set_empdesignation(Tour.empdesignation)
                tour_apr.set_empgrade(Tour.empgrade)
                tour_apr.set_empbranchgid(Tour.empbranchgid)

                branch=empdtl.get_branch_data(Tour.empbranchgid,request)
                tour_apr.set_branch_name(branch.name)
                # brcode=empdtl.get_branch_code(Tour.empbranchgid)
                tour_apr.set_branch_code(branch.code)

                reason = detail.get_reason_name(Tour.reason)
                tour_apr.set_reason(reason)
                tour_apr.set_startdate(Tour.start_date)
                tour_apr.set_enddate(Tour.end_date)
                tour_apr.set_quantum_of_funds(Tour.quantum_of_funds)
                tour_apr.set_opening_balance(Tour.opening_balance)
                tour_apr.set_id(apr.id)
                if apr.request_type==App_type.TOUR and apr.applevel!=App_level.SECOND_LEVEL:
                    approver=empdtl.employee_details_get(apr.approvedby,request)
                    tour_apr.set_approvedby(approver.full_name)
                    tour_apr.set_approver_code(approver.code)
                    tour_apr.set_approver_id(apr.approvedby)
                elif apr.approvedby==Admin.CEO:
                    tour_apr.set_approvedby("CEO")
                    tour_apr.set_approver_code("CEO")
                    tour_apr.set_approver_id("CEO")
                elif apr.approvedby==Admin.ADMIN:
                    tour_apr.set_approvedby("ADMIN")
                    tour_apr.set_approver_code("ADMIN")
                    tour_apr.set_approver_id("ADMIN")
                else:
                    approver = empdtl.employee_details_get(apr.approvedby, request)
                    tour_apr.set_approvedby(approver.full_name)
                    tour_apr.set_approver_code(approver.code)
                    tour_apr.set_approver_id(apr.approvedby)

                onb_approver = empdtl.employee_details_get(apr.onbehalfof_approval, request)
                tour_apr.set_onb_approvedby(onb_approver.full_name)
                tour_apr.set_onb_approver_code(onb_approver.code)
                tour_apr.set_onb_approver_id(apr.onbehalfof_approval)
                raised_by_data=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=Tour.id, request_type=type, applevel=App_level.ZERO_LEVEL, id__lt=apr.id, entity_id=self._entity_id()).order_by("-id")
                if len(raised_by_data)!=0:
                    raised_by_data=raised_by_data[0]
                    # if raised_by_data.onbehalfof > 0:
                    #     onbehalfof = empdtl.employee_details_get(raised_by_data.onbehalfof ,request)
                    #     # tour_apr.set_onbehalfof(onbehalfof)
                    # else:
                    onbehalfof = empdtl.employee_details_get(raised_by_data.approvedby, request)
                    tour_apr.set_onbehalfof(onbehalfof)
                tour_apr.set_approveddate(apr.approveddate)
                tour_apr.set_apptype(apr.request_type)
                tour_apr.set_applevel(apr.applevel)
                tour_apr.set_appcomment(apr.comment)
                tour_apr.set_status(apr.status)
                status_name = status_get(apr.status)
                tour_apr.set_status_name(status_name)

                # if type=='TOUR' and Tour.tour_status==Status.FORWARDED:
                if type==App_type.TOUR :
                    Tour.tour_status=int(status)
                # elif type=='CLAIM' and Tour.claim_status==Status.FORWARDED:
                elif type==App_type.CLAIM:
                    if int(status)==7:
                        Tour.claim_status = int(Status.APPROVED)
                    else:
                        Tour.claim_status=int(status)
                tour_status = status_get(Tour.tour_status)
                advance_status = status_get(Tour.advance_status)
                if int(status)==7:
                    claim_status = status_get(Status.APPROVED)
                else:
                    claim_status = status_get(Tour.claim_status)
                tour_cancel_status = status_get(Tour.tour_cancel_status)
                advance_cancel_status = status_get(Tour.advance_cancel_status)
                tour_apr.set_tour_status(tour_status)
                tour_apr.set_tour_cancel_status(tour_cancel_status)
                tour_apr.set_advance_status(advance_status)
                tour_apr.set_advance_cancel_status(advance_cancel_status)
                tour_apr.set_claim_status(claim_status)
                tour_apr.set_tour_cancel_status_id(Tour.tour_cancel_status)
                tour_apr.set_tour_status_id(Tour.tour_status)
                tour_apr.set_advance_cancel_status_id(Tour.advance_cancel_status)
                tour_apr.set_advance_status_id(Tour.advance_status)
                if int(status)==7:
                    tour_apr.set_claim_status_id(Status.APPROVED)
                else:
                    tour_apr.set_claim_status_id(Tour.claim_status)
                tour_apr.set_air_status_checker(Tour.air_status)
                tour_apr.set_train_status_checker(Tour.train_status)
                tour_apr.set_bus_status_checker(Tour.bus_status)
                tour_apr.set_cab_status_checker(Tour.cab_status)
                tour_apr.set_accomodation_status_checker(Tour.accomodation_status)


                # if type==App_type.ADVANCE:
                #     tourapprovedby = TravelHistory.objects.using(self._current_app_schema()).filter(tour_id =Tour.id, status=Status.APPROVED, entity_id=self._entity_id())
                #     if len(tourapprovedby)==0:
                #         tour_apr.set_tour_approvedby(None)
                #     else:
                #         tour_apr.set_tour_approvedby(tourapprovedby.last().approvedby)
                #
                #     adv_condition=Q(tour_id=Tour.id)
                #     status=int(status)
                #     if status==Status.APPROVED:
                #         adv_condition &=Q(status=Status_adv.APPROVED,entity_id=self._entity_id())
                #     if status==Status.REJECTED:
                #         adv_condition &= Q(status=Status_adv.REJECTED,entity_id=self._entity_id())
                #     if status==Status.PENDING:
                #         adv_condition &= Q(status=Status_adv.PENDING,entity_id=self._entity_id())
                #     else:
                #         pass
                #     advance_list=TourAdvance.objects.using(self._current_app_schema()).filter(adv_condition).order_by("-id")
                #     req_amt = 0
                #     app_amt = 0
                #     if len(advance_list) !=0:
                #         req_amt=advance_list[0].reqamount
                #         app_amt=advance_list[0].appamount
                #     # adv_amt=0
                #     # for advance in advance_list:
                #     #     adv_amt=advance.appamount+adv_amt
                #     tour_apr.set_requested_amount(req_amt)
                #     tour_apr.set_approved_amount(app_amt)
                #
                #     # advance_list = TourAdvance.objects.using(self._current_app_schema()).filter(tour_id=Tour.id, status=Status_adv.APPROVED,entity_id=self._entity_id())
                #     # total_advance = 0
                #     # for advance in advance_list:
                #     #     total_advance = advance.appamount + total_advance
                #     # tour_apr.set_total_advance(total_advance)

                if type==App_type.CLAIM:
                    claimed_amount=0
                    claim=ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=Tour.id,status=1,entity_id=self._entity_id())
                    for each_claim in claim:
                        claimed_amount+=each_claim.claimedamount
                    tour_apr.set_claim_amount(claimed_amount)
                if apr.request_type==App_type.CLAIM and apr.applevel==App_level.THIRD_LEVEL and apr.status==Status.PENDING:
                    if emp_id==empid:
                        pass
                    else:
                        resp_list.append(tour_apr)
                else:
                    resp_list.append(tour_apr)
            vpage = NWisefinPaginator(approverdata, vys_page.get_index(), 10)
            resp_list.set_pagination(vpage)
        return resp_list


    # def insert_forward(self, request_obj):
    #     # try:
    #     approvedby = TravelHistory.objects.using(self._current_app_schema()).create(tour_id=request_obj.get_tour_id(),
    #                                                                                 approvedby=request_obj.get_approvedby(),
    #                                                                                 onbehalfof=request_obj.get_onbehalfof(),
    #                                                                                 approveddate=time_function.ist_time(),
    #                                                                                 request_type=request_obj.get_apptype(),
    #                                                                                 applevel=request_obj.get_applevel(),
    #                                                                                 comment=request_obj.get_appcomment(),
    #                                                                                 status=request_obj.get_status(), entity_id=self._entity_id())
    #     if request_obj.get_apptype() == App_type.tour:
    #         tourrequest = TourRequest.objects.using(self._current_app_schema()).filter(id=request_obj.get_tour_id(),entity_id=self._entity_id()).update(tour_status=Status.FORWARDED,entity_id=self._entity_id())
    #
    #     # elif request_obj.get_apptype() == App_type.advance:
    #     #     tourrequest = TourRequest.objects.using(self._current_app_schema()).filter(id=request_obj.get_tour_id(),entity_id=self._entity_id()).update(advance_status=Status.FORWARDED,entity_id=self._entity_id())
    #
    #     elif request_obj.get_apptype() == App_type.claim:
    #         tourrequest = TourRequest.objects.using(self._current_app_schema()).filter(id=request_obj.get_tour_id(),entity_id=self._entity_id()).update(claim_status=Status.FORWARDED,entity_id=self._entity_id())
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
    #
    #     success_obj = NWisefinSuccess()
    #     success_obj.set_status(SuccessStatus.SUCCESS)
    #     success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
    #     return success_obj

    def update_return(self,request_obj):
        # try:
        approve = TravelHistory.objects.using(self._current_app_schema()).filter(id=request_obj.id, entity_id=self._entity_id()).filter(request_type=request_obj.request_type).update(comment=request_obj.get_appcomment(),
                                                                                                                                                                                 status=request_obj.get_status(), entity_id=self._entity_id())

        if request_obj.request_type == App_type.tour:
            tourrequest = TourRequest.objects.using(self._current_app_schema()).filter(id=request_obj.tour_id).update(tour_status=Status.RETURNED,entity_id=self._entity_id())

        # elif request_obj.request_type == App_type.advance:
        #     tourrequest = TourRequest.objects.using(self._current_app_schema()).filter(id=request_obj.tour_id).update(advance_status=Status.RETURNED,entity_id=self._entity_id())

        elif request_obj.request_type== App_type.claim:
            tourrequest = TourRequest.objects.using(self._current_app_schema()).filter(id=request_obj.tour_id).update(claim_status=Status.RETURNED,entity_id=self._entity_id())



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
        # except ApprovedBy.DoesNotExist:
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

    @transaction.atomic
    def insert_reject(self,request_obj,employee_id,request):
        if 'id' in request_obj:
            logger.info('ta_ Tour_reject- ' + str(employee_id) + str(request_obj))
            # try:
            if "onbehalf" in request_obj:
                login_emp = request.employee_id
                approver_nac = request_obj["onbehalf"]
            else:
                login_emp = 0
                approver_nac = request.employee_id

            employee_id=approver_nac

            if 'appcomment' not in request_obj or request_obj['appcomment']=="":
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.COMMENT)
                return error_obj

            approver_data = (TravelHistory.objects.using(self._current_app_schema()).get(id=request_obj['id'], entity_id=self._entity_id()))

            if approver_data.approvedby > 0:
                if approver_data.approvedby != approver_nac:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.APPROVER)
                    return error_obj

            module_permission = ApiService(self._scope())
            role_arr = module_permission.employee_modulerole_get(employee_id, ModuleList.Ta_eclaim, request)
            ceo_get = module_permission.onb_permission(request, employee_id)
            if RoleList.admin not in role_arr and (json.loads(ceo_get))["ceo"] != True:
                if employee_id != approver_data.approvedby:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.VALID_USER)
                    return error_obj
            elif approver_data.request_type.upper() != (request_obj['apptype']).upper() or approver_data.tour_id != \
                    int(request_obj['tour_id']):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID)
                return error_obj



            if request_obj['apptype'] == App_type.tour:
                tourrequest = TourRequest.objects.using(self._current_app_schema()).get(id=request_obj['tour_id'],entity_id=self._entity_id())

                if approver_data.applevel == App_level.THIRD_LEVEL:
                    time_service = Timecalculation()
                    if tourrequest.end_date.date() < time_service.ist_time_format().date():
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        error_obj.set_description(ErrorDescription.TOUR_ENDED)
                        return error_obj
                    if tourrequest.tour_status == Status.DEFAULT or \
                            tourrequest.tour_status == Status.RETURNED or tourrequest.tour_status == Status.REJECTED:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        error_obj.set_description(ErrorDescription.APPROVE_ERROR)
                        return error_obj

                else:
                    if tourrequest.tour_status == Status.DEFAULT or \
                            tourrequest.tour_status == Status.RETURNED or tourrequest.tour_status == Status.REJECTED:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        error_obj.set_description(ErrorDescription.APPROVE_ERROR)
                        return error_obj
                tourrequest = TourRequest.objects.using(self._current_app_schema()).filter(id=request_obj['tour_id'],entity_id=self._entity_id()).update(tour_status=Status.REJECTED)

            # elif request_obj['apptype'] == App_type.advance:
            #     tourrequest = TourRequest.objects.using(self._current_app_schema()).get(id=request_obj['tour_id'],entity_id=self._entity_id())
            #     if tourrequest.advance_status != Status.PENDING:
            #         error_obj = NWisefinError()
            #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #         error_obj.set_description(ErrorDescription.APPROVE_ERROR)
            #         return error_obj
            #     tourrequest = TourRequest.objects.using(self._current_app_schema()).filter(id=request_obj['tour_id'],entity_id=self._entity_id()).update(advance_status=Status.REJECTED,entity_id=self._entity_id())
            #
            #     advance_id = TourAdvance.objects.using(self._current_app_schema()).filter(tour_id=request_obj['tour_id'],entity_id=self._entity_id()).last().id
            #     TourAdvance.objects.using(self._current_app_schema()).filter(id=advance_id,entity_id=self._entity_id()).update(status=Status.REJECTED)

            elif request_obj['apptype'] == App_type.claim:
                tourrequest = TourRequest.objects.using(self._current_app_schema()).get(id=request_obj['tour_id'],entity_id=self._entity_id())
                if tourrequest.claim_status == Status.DEFAULT or tourrequest.claim_status == Status.APPROVED or \
                        tourrequest.claim_status == Status.REJECTED or tourrequest.claim_status == Status.RETURNED:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.APPROVE_ERROR)
                    return error_obj
                tourrequest = TourRequest.objects.using(self._current_app_schema()).filter(id=request_obj['tour_id'],entity_id=self._entity_id()).update(claim_status=Status.REJECTED)

            elif (request_obj['apptype']).upper() == (App_type.TourCancel).upper():
                tourrequest = TourRequest.objects.using(self._current_app_schema()).get(id=request_obj['tour_id'],entity_id=self._entity_id())
                if tourrequest.tour_cancel_status != Status.PENDING:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.APPROVE_ERROR)
                    return error_obj
                tourrequest = TourRequest.objects.using(self._current_app_schema()).filter(id=request_obj['tour_id'],entity_id=self._entity_id()).update(tour_cancel_status=Status.REJECTED,entity_id=self._entity_id())

            # elif (request_obj['apptype']).upper() == (App_type.AdvanceCancel).upper():
            #     tourrequest = TourRequest.objects.using(self._current_app_schema()).get(id=request_obj['tour_id'],entity_id=self._entity_id())
            #     if tourrequest.advance_cancel_status != Status.PENDING:
            #         error_obj = NWisefinError()
            #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #         error_obj.set_description(ErrorDescription.APPROVE_ERROR)
            #         return error_obj
            #     tourrequest = TourRequest.objects.using(self._current_app_schema()).filter(id=request_obj['tour_id'],entity_id=self._entity_id()).update(advance_cancel_status=Status.REJECTED,entity_id=self._entity_id())


            approvedby = TravelHistory.objects.using(self._current_app_schema()).filter(id=request_obj['id'], entity_id=self._entity_id()).update(
                                                       approveddate=time_function.ist_time(),
                                                       comment=request_obj['appcomment'],
                                                       status=Status.REJECTED,entity_id=self._entity_id(),approvedby=employee_id,
                                                        onbehalfof_approval=login_emp)

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
            # except ApprovedBy.DoesNotExist:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            #     error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
            #     return error_obj
            # except:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj

            mail_service=ta_email(self._scope())
            mail_service.mail_data( request_obj['tour_id'])

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj

    @transaction.atomic
    def expense_submit(self, expensedata, user_id,request):

        from taservice.service.touradvance import TourAdvance as TourAdvance_ser
        # try:
        ccbs_obj = expensedata['ccbs']

        tour_req = TourRequest.objects.using(self._current_app_schema()).get(id=expensedata['tourgid'],entity_id=self._entity_id())

        if tour_req.claim_status==Status.REQUESTED:
            ccbs_tourid=0
        else:
            ccbs_tourid=expensedata['tourgid']

        ccbs_ck_service = Onbehalf_service(self._scope())
        ccbs_id_check = ccbs_ck_service.ccbs_id_tour_id_check(ccbs_obj, ccbs_tourid)  # 0 tourid for create
        if ccbs_id_check != True:
            return ccbs_id_check

        valid_check=Validation(self._scope())
        ccbs_validation = valid_check.ccbs_validation("EXP", ccbs_obj, expensedata['tourgid'])
        if ccbs_validation != True:
            return ccbs_validation


        # if tour_req.claim_status==Status.PENDING or tour_req.claim_status==Status.APPROVED or tour_req.claim_status==Status.FORWARDED:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.INVALID_CLAIM)
        #     return error_obj
        if tour_req.tour_cancel_status == Status.PENDING or tour_req.tour_cancel_status == Status.APPROVED:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.CANCEL_SUBMITTED)
            return error_obj

        ccbs_type = Ccbs_utils.expense
        req_id=0
        detail = expensedata['ccbs']
        exp_data = Onbehalfrequest(expensedata)
        onbehalfof_id = exp_data.onbehalfof
        if onbehalfof_id > 0:
            if onbehalfof_id != tour_req.empgid:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.IN_VALID_ONB)
                return error_obj
            if int(onbehalfof_id) == user_id:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.IN_VALID_ONB)
                return error_obj
            tour_emp = onbehalfof_id
            exp_data.onbehalfof = user_id
        else:
            tour_emp = user_id
            if tour_emp!=tour_req.empgid:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_MAKER)
                return error_obj
        if exp_data.appcomment is None or exp_data.appcomment=="":
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.COMMENT)
            return error_obj
        # exp_data.approvedby=int(exp_data.approvedby)
        # if exp_data.approvedby==0 or exp_data.approvedby==tour_req.empgid or exp_data.approvedby==tour_req.onbehalfof:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.APPROVER)
        #     return error_obj
        # onbehalf_data = expensedata['onbehalfof']
        # if exp_data.get_onbehalfof() is not None:
        #     onbehalfof_id = expensedata['onbehalfof']
        #     # object = TourApprovedby()
        #     # expensedata = object.onbehalf_emoloyee(onbehalfof_id, expensedata)
        # else:

        # advance adjustment
        adv_service=TourAdvance_ser(self._scope())
        # adv_adjust=adv_service.adv_adjust_check(request, expensedata['tourgid'])
        # if isinstance(adv_adjust, NWisefinError):
        #     return adv_adjust
        # if adv_adjust.status == "success":

            # if tour_req.claim_status==Status.RETURNED:
            #
            #     expensedata['approvedby'] = tour_emp
            #     expensedata['onbehalfof'] = exp_data.onbehalfof
            #     expensedata['approveddate'] = time_function.ist_time()
            #     expensedata['apptype'] = App_type.CLAIM
            #     expensedata['applevel'] = App_level.ZERO_LEVEL
            #     expensedata['status'] = Status.REQUESTED
            #     expensedata['appcomment'] = exp_data.appcomment
            #     # exp_service = TourApprovedby()
            #     resp1 = self.insert_approvedby(expensedata,request)
            # else:
        approvedby_data=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=expensedata['tourgid'], request_type=App_type.CLAIM,
                                                                                       applevel=App_level.ZERO_LEVEL, status=Status.REQUESTED, entity_id=self._entity_id()).last()
        if approvedby_data is None:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.CREATE_NEW_CLAIM)
            return error_obj
        else:
            TravelHistory.objects.using(self._current_app_schema()).filter(id=approvedby_data.id).update(approvedby=user_id,
                                                                                                         # onbehalfof=exp_data.onbehalfof,
                                                                                                         approveddate=time_function.ist_time(), comment=exp_data.appcomment, entity_id=self._entity_id())
            # try:
            # if resp1.status == "success":
                # if exp_data.get_onbehalfof() is not None:
                #     onbehalfof_id = expensedata['onbehalfof']
                #     emp = Employee.objects.using(self._current_app_schema()).get(user_id=onbehalfof_id)
                #     employee_id = emp.id
                # else:
                #     employee_id = Onbehalfof.ZERO
            api_service=ApiService(self._scope())
            rm_get = api_service.get_RM_ID(request,tour_emp )
            if rm_get == None:
                error_obj=NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_RM)
                return error_obj
            # request_obj['approvedby'] = rm_get
            expensedata['onbehalfof'] = 0
            expensedata['approveddate'] = time_function.ist_time()
            expensedata['approvedby'] = rm_get
            expensedata['apptype'] = App_type.CLAIM
            expensedata['applevel'] = App_level.FIRST_LEVEL
            expensedata['status'] = Status.PENDING
            expensedata['appcomment'] = ""
            # exp_service = TourApprovedby()
            resp2 = self.insert_approvedby(expensedata,request)


            mail_service=ta_email(self._scope())
            mail_service.mail_data( expensedata['tourgid'])

            if resp2.status == "success":
                exp_service = Onbehalf_service(self._scope())
                del_prev_ccbs=Ccbs.objects.using(self._current_app_schema()).filter(tour_id=expensedata['tourgid'],requestid=0,entity_id=self._entity_id()).update(status=0,entity_id=self._entity_id())
                resp1 = exp_service.insert_Ccbs(detail,user_id,req_id,ccbs_type)
                return resp1


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

    # def onbehalf_emoloyee(self, onbehalfof_id, tourdata):
    #     emp = Employee.objects.using(self._current_app_schema()).get(user_id=onbehalfof_id)
    #     employee_id = emp.id
    #     tourdata['onbahalfof'] = employee_id
    #     tourdata['approveddate'] = date.today()
    #     tourdata['apptype'] = App_type.CLAIM
    #     tourdata['applevel'] = App_level.FIRST_LEVEL
    #     tourdata['status'] = Status.PENDING
    #     # tour = TourRequest(tourdata)
    #     return tourdata


    # def adv_summary(self, employee_id, onb,vys_page,request_date,tour_no,request):
    #     if request_date !="":
    #         request_date=(datetime.strptime(request_date, '%d-%b-%Y')).date()
    #     if int(onb) > 0:
    #         Tour = TravelHistory.objects.using(self._current_app_schema()).filter(tour__empgid=onb, tour__onbehalfof=employee_id, status=Status.APPROVED, applevel=App_level.FIRST_LEVEL,
    #                                                                               apptype=(App_type.ADVANCE or App_type.advance), tour__request_date__icontains=request_date, tour__id__icontains=tour_no,
    #                                                                               tour__advance_cancel_status=Status.DEFAULT, tour__claim_status=Status.DEFAULT).values('approvedby','onbehalfof','approveddate','apptype','applevel','status',
    #                                             'appcomment','tour').annotate(id=Max('id'),entity_id=self._entity_id()).order_by('-tour_id')[vys_page.get_offset():vys_page.get_query_limit()]
    #     else:
    #         # Tour = ApprovedBy.objects.using(self._current_app_schema()).filter(tour__empgid=employee_id, status=Status.APPROVED, applevel=App_level.FIRST_LEVEL,
    #         #                                     apptype=(App_type.ADVANCE or App_type.advance),tour__request_date__icontains=request_date,tour__id__icontains=tour_no,
    #         #                                                        tour__advance_cancel_status=Status.REQUESTED).order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]
    #         Tour = TravelHistory.objects.using(self._current_app_schema()).filter(tour__empgid=employee_id, status=Status.APPROVED, applevel=App_level.FIRST_LEVEL,
    #                                                                               apptype=(App_type.ADVANCE or App_type.advance), tour__request_date__icontains=request_date, tour__id__icontains=tour_no,
    #                                                                               tour__advance_cancel_status=Status.DEFAULT, tour__claim_status=Status.DEFAULT).values('approvedby','onbehalfof','approveddate','apptype','applevel','status',
    #                                             'appcomment','tour').annotate(id=Max('id'),entity_id=self._entity_id()).order_by('-tour_id')[vys_page.get_offset():vys_page.get_query_limit()]
    #
    #     resp_list = NWisefinList()
    #     if len(Tour)>0:
    #         for data in Tour:
    #             # tour=data.tour
    #             tour=TourRequest.objects.using(self._current_app_schema()).get(id=data['tour'],entity_id=self._entity_id())
    #             req_data = TourMakerResponse()
    #             req_data.set_tourid(tour.id)
    #             req_data.set_id(tour.id)
    #             # req_data.set_requestno(tour.requestno)
    #             req_data.set_requestdate(tour.request_date)
    #             req_data.set_startdate(tour.start_date)
    #             req_data.set_enddate(tour.end_date)
    #             req_data.set_reason_id(tour.reason)
    #             detail = emp_dtl(self._scope())
    #             reason = detail.get_reason_name(tour.reason)
    #             req_data.set_reason(reason)
    #             req_data.set_empgid(tour.empgid)
    #             empdtl = ApiService(self._scope())
    #
    #             tour_app = TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tour.id,
    #                                                                                       applevel=App_level.FIRST_LEVEL,
    #                                                                                       status=Status.APPROVED, entity_id=self._entity_id())
    #             if len(tour_app) != 0:
    #                 tour_approvedby = empdtl.employee_details_get(tour_app[0].approvedby, request)
    #                 req_data.set_tour_approvedby(tour_approvedby)
    #
    #             employee = empdtl.employee_details_get(tour.empgid,request)
    #             req_data.set_employee_name(employee.full_name)
    #             approve=data['approvedby']
    #             if approve is not None:
    #                 approvedby = empdtl.employee_details_get(data['approvedby'],request)
    #                 req_data.set_approvedby(approvedby.full_name)
    #                 req_data.set_approvedby_id(data['approvedby'])
    #             # code = empdtl.employee_code_get(tour.empgid)
    #             req_data.set_employee_code(employee.code)
    #             req_data.set_empdesignation(tour.empdesignation)
    #             req_data.set_empgrade(tour.empgrade)
    #             req_data.set_empbranchgid(tour.empbranchgid)
    #
    #             branch = empdtl.get_branch_data(tour.empbranchgid,request)
    #             req_data.set_branch_name(branch.name)
    #
    #             if tour.onbehalfof > 0:
    #                 onbehalf = empdtl.employee_details_get(tour.onbehalfof,request)
    #                 req_data.set_onbehalfof(onbehalf.full_name)
    #             tour_status = status_get(tour.tour_status)
    #             # advance_status = status_get(tour.advance_status)
    #             claim_status = status_get(tour.claim_status)
    #             req_data.set_tour_status(tour_status)
    #             # req_data.set_advance_status(advance_status)
    #             req_data.set_tour_status_id(tour.tour_status)
    #             # req_data.set_advance_status_id(tour.advance_status)
    #             # req_data.set_claim_status(claim_status)
    #             resp_list.append(req_data)
    #         vpage = NWisefinPaginator(Tour, vys_page.get_index(), 10)
    #         resp_list.set_pagination(vpage)
    #     return resp_list

    # def adv_summary(self, employee_id, onb,vys_page,request_date,tour_no,request):
    #     if request_date !="":
    #         request_date=(datetime.strptime(request_date, '%d-%b-%Y')).date()
    #     if int(onb) > 0:
    #         Tour = ApprovedBy.objects.using(self._current_app_schema()).filter(tour__empgid=onb, tour__onbehalfof=employee_id, tour__advance_status=Status.APPROVED, applevel=App_level.FIRST_LEVEL,
    #                                             apptype=(App_type.ADVANCE or App_type.advance),tour__request_date__icontains=request_date,tour__id__icontains=tour_no).all().order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]
    #         # Tour = TourRequest.objects.using(self._current_app_schema()).filter(empgid=onb, onbehalfof=employee_id, advance_status=Status.APPROVED).all()
    #     else:
    #         Tour = ApprovedBy.objects.using(self._current_app_schema()).filter(tour__empgid=employee_id, tour__advance_status=Status.APPROVED, applevel=App_level.FIRST_LEVEL,
    #                                             apptype=(App_type.ADVANCE or App_type.advance),tour__request_date__icontains=request_date,tour__id__icontains=tour_no).all().order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]
    #         # Tour = TourRequest.objects.using(self._current_app_schema()).filter(empgid=employee_id, advance_status=Status.APPROVED).all()
    #
    #     resp_list = NWisefinList()
    #     if len(Tour)>0:
    #         for data in Tour:
    #             tour=data.tour
    #             req_data = TourMakerResponse()
    #             req_data.set_tourid(tour.id)
    #             req_data.set_id(tour.id)
    #             req_data.set_requestno(tour.requestno)
    #             req_data.set_requestdate(tour.request_date)
    #             req_data.set_empgid(tour.empgid)
    #             empdtl = ApiService()
    #
    #             tour_app = ApprovedBy.objects.using(self._current_app_schema()).filter(tour_id=tour.id,
    #                                                                        applevel=App_level.FIRST_LEVEL,
    #                                                                        status=Status.APPROVED)
    #             if len(tour_app) != 0:
    #                 tour_approvedby = empdtl.employee_details_get(tour_app[0].approvedby, request)
    #                 req_data.set_tour_approvedby(tour_approvedby)
    #
    #             employee = empdtl.employee_details_get(tour.empgid,request)
    #             req_data.set_employee_name(employee.full_name)
    #             approve=data.approvedby
    #             if approve is not None:
    #                 approvedby = empdtl.employee_details_get(data.approvedby,request)
    #                 req_data.set_approvedby(approvedby.full_name)
    #                 req_data.set_approvedby_id(data.approvedby)
    #             # code = empdtl.employee_code_get(tour.empgid)
    #             req_data.set_employee_code(employee.code)
    #             req_data.set_empdesignation(tour.empdesignation)
    #             req_data.set_empgrade(tour.empgrade)
    #             req_data.set_empbranchgid(tour.empbranchgid)
    #
    #             branch = empdtl.get_branch_data(tour.empbranchgid,request)
    #             req_data.set_branch_name(branch.name)
    #
    #             if tour.onbehalfof > 0:
    #                 onbehalf = empdtl.employee_details_get(tour.onbehalfof,request)
    #                 req_data.set_onbehalfof(onbehalf.full_name)
    #             tour_status = status_get(tour.tour_status)
    #             advance_status = status_get(tour.advance_status)
    #             claim_status = status_get(tour.claim_status)
    #             req_data.set_tour_status(tour_status)
    #             req_data.set_advance_status(advance_status)
    #             req_data.set_tour_status_id(tour.tour_status)
    #             req_data.set_advance_status_id(tour.advance_status)
    #             # req_data.set_claim_status(claim_status)
    #             resp_list.append(req_data)
    #         vpage = NWisefinPaginator(Tour, vys_page.get_index(), 10)
    #         resp_list.set_pagination(vpage)
    #     return resp_list


    def tourapprovedby_table(self):
        approverdata = TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).all().order_by('-id')
        resp_list = NWisefinList()
        for apr in approverdata:
            tour_apr = TourMakerResponse()

            tour_apr.set_id(apr.id)
            tour_apr.set_approvedby(apr.approvedby)
            # tour_apr.set_onbehalfof(apr.onbehalfof)
            tour_apr.set_approveddate(apr.approveddate)
            tour_apr.set_apptype(apr.request_type)
            tour_apr.set_applevel(apr.applevel)
            tour_apr.set_appcomment(apr.comment)
            tour_apr.set_status(apr.status)
            tour_apr.set_tourid(apr.tour_id)

            resp_list.append(tour_apr)
        return resp_list


    # def approval_flow_get(self,tour_id,type,request):
    #     empdtl = ApiService(self._scope())
    #     req_data = TourAdvanceResponse()
    #     tour_approver = []
    #     arr=[0,1,2,3]
    #     if type is None or type.upper()=="ALL":
    #         approve= TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tour_id, entity_id=self._entity_id())
    #     elif type==App_type.TOUR or type==App_type.tour:
    #         type=[App_type.TOUR,App_type.TourCancel]
    #         approve= TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tour_id, request_type__in=type,applevel__in=arr, entity_id=self._entity_id())
    #     else:
    #         approve= TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tour_id, request_type=type, entity_id=self._entity_id())
    #     for appr in approve:
    #         approverdata = TourMaker()
    #         approverdata.set_id(appr.id)
    #         approverdata.set_comment(appr.comment)
    #         approvedby = empdtl.employee_details_get(appr.approvedby,request)
    #         tour_emp_id=appr.approvedby
    #         if appr.applevel==0:
    #             tour_emp_id=appr.tour.id
    #             appr.approvedby=appr.tour.empgid
    #
    #         tour_emp = empdtl.employee_details_get(appr.approvedby,request)
    #
    #
    #         approverdata.set_status(appr.status)
    #         approverdata.set_applevel(appr.applevel)
    #         approverdata.set_approveddate(appr.approveddate)
    #         app_type=appr.request_type.upper()
    #         if appr.request_type.upper()=="TOUR":
    #             app_type="TRAVEL"
    #         elif appr.request_type.upper()=="TOURCANCEL":
    #             app_type="TRAVELCANCEL"
    #         approverdata.set_apptype(app_type + " CREATION")
    #         approverdata.set_tourid(appr.tour_id)
    #         ta_api_service = ApiService(self._scope())
    #         branch_data = ta_api_service.get_branch_data_empid([appr.approvedby], request)
    #         approverdata.set_branch_code(branch_data['branch_code'])
    #         approverdata.set_branch_name(branch_data['branch_name'])
    #         if appr.request_type ==App_type.CLAIM and appr.applevel==App_level.THIRD_LEVEL and appr.status==Status.PENDING :
    #             approverdata.set_approvedby("ADMIN")
    #             approverdata.set_approver_id("ADMIN")
    #             approverdata.set_approver_code("ADMIN")
    #             approvedby={}
    #             approvedby["code"]="ADMIN"
    #             approvedby["full_name"]="ADMIN"
    #             approvedby["id"]="ADMIN"
    #             approverdata.set_onbehalfof(approvedby)
    #         elif appr.request_type ==App_type.TOUR and appr.applevel==App_level.SECOND_LEVEL and appr.status==Status.PENDING :
    #             approverdata.set_approvedby("CEO")
    #             approverdata.set_approver_id("CEO")
    #             approverdata.set_approver_code("CEO")
    #             approvedby={}
    #             approvedby["code"]="CEO"
    #             approvedby["full_name"]="CEO"
    #             approvedby["id"]="CEO"
    #             approverdata.set_onbehalfof(approvedby)
    #
    #         # elif appr.onbehalfof_approval ==0:
    #         #     approverdata.set_approvedby(tour_emp.full_name)
    #         #     approverdata.set_approver_id(tour_emp_id)
    #         #     approverdata.set_approver_code(tour_emp.code)
    #         #     approverdata.set_onbehalfof(approvedby)
    #         else:
    #             onb_approvedby = empdtl.employee_details_get(appr.onbehalfof_approval, request)
    #             approvedby = empdtl.employee_details_get(appr.approvedby, request)
    #             if appr.approvedby==-1:
    #                 approver_name="ADMIN"
    #                 approver_code="ADMIN"
    #             elif appr.approvedby==-2:
    #                 approver_name="CEO"
    #                 approver_code="CEO"
    #             else:
    #                 approver_name=approvedby.full_name
    #                 approver_code=approvedby.code
    #             approverdata.set_approvedby(approver_name)
    #             approverdata.set_approver_code(approver_code)
    #             approverdata.set_approver_id(appr.approvedby)
    #
    #             approverdata.set_onbehalfof(onb_approvedby)
    #
    #
    #         # if appr.request_type ==App_type.TOUR and appr.applevel==App_level.THIRD_LEVEL:
    #         #     pass
    #         # else:
    #         #     tour_approver.append(json.loads(approverdata.get()))
    #         tour_approver.append(json.loads(approverdata.get()))
    #     req_data.set_approve(tour_approver)
    #     return req_data

    def approval_flow_get(self,tour_id,type,request):
        empdtl = ApiService(self._scope())
        req_data = TourAdvanceResponse()
        tour_approver = []
        arr=[0,1,2,3]
        if type is None or type.upper()=="ALL":
            approve= TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tour_id, entity_id=self._entity_id())
        elif type==App_type.TOUR or type==App_type.tour:
            type=[App_type.TOUR,App_type.TourCancel]
            approve= TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tour_id, request_type__in=type,applevel__in=arr, entity_id=self._entity_id())
        else:
            approve= TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tour_id, request_type=type, entity_id=self._entity_id())
        for appr in approve:
            approverdata = TourMaker()
            approverdata.set_id(appr.id)
            approverdata.set_comment(appr.comment)
            approvedby = empdtl.employee_details_get(appr.approvedby,request)
            tour_emp_id=appr.approvedby
            raised_by=appr.approvedby
            if appr.applevel==0:
                tour_emp_id=appr.tour.id
                appr.approvedby=appr.tour.empgid

            tour_emp = empdtl.employee_details_get(appr.approvedby,request)


            approverdata.set_status(appr.status)
            status_name=""
            if appr.status==1:
                status_name="REQUESTED"
            elif appr.status==2:
                status_name="PENDING"
            elif appr.status==3:
                status_name="APPROVED"
            elif appr.status==4:
                status_name="REJECTED"
            elif appr.status==5:
                status_name="RETURNED"

            approverdata.set_applevel(appr.applevel)
            approverdata.set_approveddate(appr.approveddate)
            app_type=appr.request_type.upper()
            if appr.request_type.upper()=="TOUR":
                app_type="TRAVEL"
            elif appr.request_type.upper()=="TOURCANCEL":
                app_type="TRAVELCANCEL"
            approverdata.set_apptype(app_type + " CREATION")
            approverdata.set_status_name(app_type + " CREATION " +status_name)
            approverdata.set_tourid(appr.tour_id)
            ta_api_service = ApiService(self._scope())
            branch_data = ta_api_service.get_branch_data_empid([appr.approvedby], request)
            approverdata.set_branch_code(branch_data['branch_code'])
            approverdata.set_branch_name(branch_data['branch_name'])
            # if appr.request_type ==App_type.CLAIM and appr.applevel==App_level.THIRD_LEVEL and appr.status==Status.PENDING :
            #     approverdata.set_approvedby("ADMIN")
            #     approverdata.set_approver_id("ADMIN")
            #     approverdata.set_approver_code("ADMIN")
            #     approvedby={}
            #     approvedby["code"]="ADMIN"
            #     approvedby["full_name"]="ADMIN"
            #     approvedby["id"]="ADMIN"
            #     approverdata.set_onbehalfof(approvedby)
            # elif appr.request_type ==App_type.TOUR and appr.applevel==App_level.SECOND_LEVEL and appr.status==Status.PENDING :
            #     approverdata.set_approvedby("CEO")
            #     approverdata.set_approver_id("CEO")
            #     approverdata.set_approver_code("CEO")
            #     approvedby={}
            #     approvedby["code"]="CEO"
            #     approvedby["full_name"]="CEO"
            #     approvedby["id"]="CEO"
            #     approverdata.set_onbehalfof(approvedby)
            #
            # # elif appr.onbehalfof_approval ==0:
            # #     approverdata.set_approvedby(tour_emp.full_name)
            # #     approverdata.set_approver_id(tour_emp_id)
            # #     approverdata.set_approver_code(tour_emp.code)
            # #     approverdata.set_onbehalfof(approvedby)
            # else:

            approvedby = empdtl.employee_details_get(appr.approvedby, request)
            if appr.approvedby==-1:
                approver_name="ADMIN"
                approver_code="ADMIN"

                app_onb_approvedby = {}
                app_onb_approvedby["code"]="ADMIN"
                app_onb_approvedby["full_name"]="ADMIN"
                app_onb_approvedby["id"]="ADMIN"
            elif appr.approvedby==-2:
                approver_name="CEO"
                approver_code="CEO"

                app_onb_approvedby = {}
                app_onb_approvedby["code"] = "CEO"
                app_onb_approvedby["full_name"] = "CEO"
                app_onb_approvedby["id"] = "CEO"
            else:
                approver_name=approvedby.full_name
                approver_code=approvedby.code

                app_onb_approvedby = {}
                app_onb_approvedby["code"] = approver_code
                app_onb_approvedby["full_name"] = approver_name
                app_onb_approvedby["id"] = appr.approvedby

            approverdata.set_approvedby(approver_name)
            approverdata.set_approver_code(approver_code)
            approverdata.set_approver_id(appr.approvedby)

            if appr.onbehalfof_approval>0:
                app_onb_approvedby = empdtl.employee_details_get(appr.onbehalfof_approval, request)
                approverdata.set_onbehalfof(app_onb_approvedby)
            else:
                if appr.applevel==App_level.ZERO_LEVEL:
                    app_onb_approvedby = empdtl.employee_details_get(raised_by, request)
                approverdata.set_onbehalfof(app_onb_approvedby)


            if appr.request_type ==App_type.TOUR and appr.applevel==App_level.THIRD_LEVEL and appr.status==Status.APPROVED:
                pass
            else:
                tour_approver.append(json.loads(approverdata.get()))
            # tour_approver.append(json.loads(approverdata.get()))
        req_data.set_approve(tour_approver)
        return req_data

    def get_crnno(self,ecf_no,emp_id,request):
        crn_no=self.ecf_pdf_generate(ecf_no,emp_id,request)
        return crn_no['DATA']['INVOICE_HEADER'][0]['invoiceheader_crno']

    def ecf_pdf_generate(self,no, emp_id,request):
        # ecfno = ecfPdf(self,no, emp_id)
        ecfno ={
              "Classification": {
                "Entity_Gid": 1
              },
              "Params": {
                "InvoiceHeader_Gid": no,
                "employee_gid": emp_id
              }
            }
        logger.info('ta_ ECF_pdf_generate- '+str(ecfno))

        params = ''
        vysfin_url = settings.VYSFIN_URL
        ecf_pdf_url = vysfin_url + str("get_ecfpdf_fr_memo?Group=ECF_PDF_GET&Action=GET&Type=BARCODE_GENERATION")
        api_service=ApiService(self._scope())
        pdf_resp = requests.post(ecf_pdf_url, params=params, data=json.dumps(ecfno),
                                 headers={'Authorization': 'Bearer ' + api_service.get_authtoken(request)}, verify=False)
        pdf_results = pdf_resp.content.decode("utf-8")
        pdf_results = json.loads(pdf_results)

        return pdf_results


    def insert_frequent_data(self,tour_id):
        data=TourDetail.objects.using(self._current_app_schema()).filter(tour_id=tour_id,status=1,
                                                                         entity_id=self._entity_id())
        for each_data in data:
            emp_id=each_data.tour.empgid
            req_date=each_data.tour.request_date
            req_date=req_date.replace(day = 1).date()
            client_id=each_data.client
            from_place=each_data.startingpoint
            placeofvisit=each_data.placeofvisit
            self.inset_freq_client(client_id,emp_id,req_date)
            self.inset_freq_from_place(from_place,emp_id,req_date)
            self.inset_freq_to_place(placeofvisit,emp_id,req_date)



    def inset_freq_client(self,client_id,emp_id,req_date):
        prev_data=FrequentData.objects.using(self._current_app_schema()).filter(client=client_id,status=1,
                                                                employee=emp_id,entity_id=self._entity_id())
        if len(prev_data)>0:
            prev_id=prev_data.last().id
            count=prev_data.last().client_count
            FrequentData.objects.using(self._current_app_schema()).filter(id=prev_id).update(client_count=count+1,latest_date=req_date)
        else:
            FrequentData.objects.using(self._current_app_schema()).create(client=client_id,employee=emp_id,client_count=1,
                                                                         entity_id=self._entity_id(),latest_date=req_date)


    def inset_freq_from_place(self,from_place,emp_id,req_date):
        prev_data=FrequentData.objects.using(self._current_app_schema()).filter(from_place=from_place,status=1,
                                                                employee=emp_id,entity_id=self._entity_id())
        if len(prev_data)>0:
            prev_id=prev_data.last().id
            count=prev_data.last().from_place_count
            FrequentData.objects.using(self._current_app_schema()).filter(id=prev_id).update(from_place_count=count+1,latest_date=req_date)
        else:
            FrequentData.objects.using(self._current_app_schema()).create(from_place=from_place,employee=emp_id,
                                                                          from_place_count=1,
                                                                         entity_id=self._entity_id(),latest_date=req_date)


    def inset_freq_to_place(self,placeofvisit,emp_id,req_date):
        prev_data=FrequentData.objects.using(self._current_app_schema()).filter(placeofvisit=placeofvisit,status=1,
                                                                employee=emp_id,entity_id=self._entity_id())
        if len(prev_data)>0:
            prev_id=prev_data.last().id
            count=prev_data.last().placeofvisit_count
            FrequentData.objects.using(self._current_app_schema()).filter(id=prev_id).update(placeofvisit_count=count+1,latest_date=req_date)
        else:
            FrequentData.objects.using(self._current_app_schema()).create(placeofvisit=placeofvisit,
                                                                          employee=emp_id,placeofvisit_count=1,
                                                                         entity_id=self._entity_id(),latest_date=req_date)

    # def ecfPdf(self,pdf_code, emp_id):
    #     rcn_data = TourMaker()
    #     ecf_data = EcfResponse()
    #     ecf_data.InvoiceHeader_Gid=pdf_code
    #     ecf_data.set_employee_gid(emp_id)
    #     rcn_data.set_Params(ecf_data)
    #     clas_data = ClassificationResponse()
    #     clas_data.set_Entity_Gid(1)
    #     rcn_data.set_Classification(clas_data)
    #     return rcn_data.get()
