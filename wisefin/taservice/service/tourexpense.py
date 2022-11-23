# --------------------------------------------------------------------------------------------------------------------------------------------
# 6/1/2022 code changed for rollback (atomic transaction)   - RAGHUL
#08/01/2022 code changed for empty string validation     - SARAVANARAJ
# --------------------------------------------------------------------------------------------------------------------------------------------
import json
from datetime import datetime, timedelta

# from dateutil.utils import today
# from django.db import IntegrityError
# import validations as validations
from django.db import transaction
from django.utils import timezone

# from userservice.models import EmployeeBranch
from nwisefin.settings import logger
# from taservice.service.tourapprovedby import TourApprovedby
from taservice.data.request import tourexpense as expreq
# from masterservice.data.response.Hsnresponse import HsnResponse
# from masterservice.models import Hsn
from taservice.service.elligible_amount_ser import El_lod_ser
from taservice.data.request.tol_amo_pkmo_req import Tol_amo_pkmo_req, Local_dept_res
from taservice.data.request.tourallowance import Allowancerequest
from taservice.data.response import tourexpense as expres
from taservice.data.response.tourexpense import Common_dropdown_Response
from taservice.data.response.tourmaker import TourMaker
from taservice.data.response.tourmaker import TourMaker as TourMakerResponse
from taservice.models.tamodels import TourExpense as Expense, ClaimRequest, Dailydeim, Incidental, Localconveyence, \
    Lodging, Misc, PackingMoving, Travel, TourRequest, TravelHistory, Localdeputation, Traveldependent, TourReason, \
    Common_dropdown_details, Allowance as ALLOWANCE_table, Date_relaxation, associate, Common_dropdown, TourDetail, \
    AccomodationBookingDetails, AirBookingDetails, TrainBookingDetails, BusBookingDetails, CabBookingDetails, \
    CabMapping, TADocuments
from taservice.service.driver_data_ser import Driver_bata
from taservice.service.emp_name_get import emp_dtl, Expense_type_get, Tourno_details
from taservice.service.packing_moving_ser import Packing_moving_ser
from taservice.service.tourallowance import Tour_grade, Tour_allowance
from taservice.util.ta_util import Status, status_get, Filterapplevel, App_level, App_type, Validation, \
    Common_drop_down, Expense_dropdown, EXPENSE_ID, Timecalculation, TADocUtil, Requirements_official
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.ta_api_service import ApiService
from taservice.service.tourmaker import TourMaker as tamaker
# from django.db.models.query_utils import Q
# from utilityservice.service.dbutil import DataBase
# import pytz
# IST = pytz.timezone('Asia/Kolkata')
# datetime_ist = datetime.now(IST)
# today = datetime_ist.strftime('%Y-%m-%d')
time_function = Timecalculation()
from utilityservice.service.threadlocal import NWisefinThread
@transaction.atomic
class TourExpense(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)
    def get_expenselist(self,expense):
        if expense == None:
            expense = ""
        Reason = Expense.objects.using(self._current_app_schema()).filter(name__icontains=expense,status=1,entity_id=self._entity_id())
        resp_list = NWisefinList()
        for reason in Reason:
            req_data = TourMakerResponse()
            req_data.set_id(reason.id)
            req_data.set_code(reason.code)
            req_data.set_name(reason.name)
            req_data.set_status(reason.status)
            resp_list.append(req_data)
        return resp_list

    def insert_expenselist(self,request_obj,empid):
        if 'id' in request_obj:
            try:
                expensedata = Expense.objects.using(self._current_app_schema()).filter(id=request_obj['id']).update(code=request_obj['code'],
                                                                                     name=request_obj['name'],
                                                                                      status=request_obj['status'],
                                                                                      updated_by=empid,entity_id=self._entity_id())

            # except IntegrityError as NWisefinError:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except expensedata.DoesNotExist:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            #     error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
            #     return error_obj
            except Exception as e:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(str(e))
                return error_obj
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj
        else:
            try:
                expensedata = Expense.objects.using(self._current_app_schema()).create(
                    code=request_obj['code'],
                    name=request_obj['name'],
                    status=1,
                    created_by=empid,entity_id=self._entity_id())

            # except IntegrityError as NWisefinError:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            except Exception as e:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(str(e))
                return error_obj
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            return success_obj

    def get_expense_name(self,id):
        expense = Expense.objects.using(self._current_app_schema()).get(id=id,entity_id=self._entity_id())
        return expense.name

    def get_el_travel_amount(self,expensegid):
        # expense = Travel.objects.using(self._current_app_schema()).filter(claimreqgid=expensegid, status=1,entity_id=self._entity_id()).all()
        eligible_amount=0
        # for exp in expense:
        #     eligible_amount+= exp.eligibleamount
        return eligible_amount
    def get_el_daily_amount(self,expensegid):
        expense = Dailydeim.objects.using(self._current_app_schema()).filter(claimreq_id=expensegid, status=1,entity_id=self._entity_id()).all()
        eligible_amount=0
        for exp in expense:
            eligible_amount+= exp.eligibleamount
        return eligible_amount
    def get_el_incidental_amount(self,expensegid):
        expense = Incidental.objects.using(self._current_app_schema()).filter(claimreq_id=expensegid, status=1,entity_id=self._entity_id()).all()
        eligible_amount=0
        for exp in expense:
            eligible_amount+= exp.eligibleamount
        return eligible_amount
    def get_el_localconv_amount(self,expensegid):
        expense = Localconveyence.objects.using(self._current_app_schema()).filter(claimreq_id=expensegid, status=1,entity_id=self._entity_id()).all()
        eligible_amount=0
        for exp in expense:
            eligible_amount+= exp.eligibleamount
        return eligible_amount
    def get_el_lodging_amount(self,expensegid):
        expense = Lodging.objects.using(self._current_app_schema()).filter(claimreq_id=expensegid, status=1,entity_id=self._entity_id()).all()
        eligible_amount=0
        for exp in expense:
            eligible_amount+= exp.eligibleamount
        return eligible_amount
    def get_el_misc_amount(self,expensegid):
        expense = Misc.objects.using(self._current_app_schema()).filter(claimreq_id=expensegid, status=1,entity_id=self._entity_id()).all()
        eligible_amount=0
        for exp in expense:
            eligible_amount+= exp.eligibleamount
        return eligible_amount
    def get_el_pakmov_amount(self,expensegid):
        expense = PackingMoving.objects.using(self._current_app_schema()).filter(claimreq_id=expensegid, status=1,entity_id=self._entity_id()).all()
        eligible_amount=0
        for exp in expense:
            eligible_amount+= exp.eligibleamount
        return eligible_amount
    def get_el_locdept_amount(self,expensegid):
        expense = Localdeputation.objects.using(self._current_app_schema()).filter(claimreq_id=expensegid, status=1,entity_id=self._entity_id()).all()
        eligible_amount=0
        for exp in expense:
            eligible_amount+= exp.eligibleamount
        return eligible_amount

    def get_el_associate_amount(self, expensegid):
        eligible_amount = 0
        return eligible_amount


    def get_claimreq_tour(self,tourid,request):
        resp_list = NWisefinList()
        tour= TourRequest.objects.using(self._current_app_schema()).get(id=tourid,entity_id=self._entity_id())
        claim = ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=tour.id, status=1,entity_id=self._entity_id()).all()
        reason =TourReason.objects.using(self._current_app_schema()).get(id=tour.reason,entity_id=self._entity_id())
        forwarder =TravelHistory.objects.using(self._current_app_schema()).filter(request_type=App_type.CLAIM, applevel=App_level.FIRST_LEVEL, tour_id=tour.id, entity_id=self._entity_id()).last()
        approve = TravelHistory.objects.using(self._current_app_schema()).filter(request_type=App_type.CLAIM,
                                                                                 applevel=App_level.THIRD_LEVEL,
                                                                                 tour_id=tour.id, entity_id=self._entity_id()).last()
        empdtl = ApiService(self._scope())
        forwarder_name=None
        forwarder_code=None
        approver_name=None
        approver_code=None
        if forwarder != None:
            forwarde = empdtl.employee_details_get(forwarder.approvedby, request)
            forwarder_name=forwarde.full_name
            forwarder_code = forwarde.code

        if approve != None:
            approver = empdtl.employee_details_get(approve.approvedby, request)
            approver_name = approver.full_name
            approver_code=approver.code


        employee = empdtl.employee_details_get(tour.empgid,request)
        branch = empdtl.get_branch_data(tour.empbranchgid,request)
        claimed_amount=0
        approved_amount=0
        eligible_amount=0
        if len(claim)==0:
            req_data = expres.Claimreq_Response()
            req_data.set_employee_name(employee.full_name)
            req_data.set_designation(tour.empdesignation)
            req_data.set_emp_grade(tour.empgrade)
            req_data.set_branch_name(branch.name)
            req_data.set_tourid(tourid)
            req_data.set_id(None)
            req_data.set_expenseid(None)
            req_data.set_approvedamount(None)
            req_data.set_claimedamount(None)
            # expense = Expense.objects.using(self._current_app_schema()).get(id=clm.expensegid)
            req_data.set_expensename(None)
            req_data.set_requestercomment(None)
            req_data.set_invoiceheadergid(None)
            req_data.set_crn_no(None)
            req_data.set_payment_status(None)
            req_data.set_approvercomment(None)
            status = status_get(None)
            req_data.set_status(status)

            req_data.set_requestdate(tour.request_date)
            req_data.set_reason(reason.name)
            req_data.set_tour_startdate(tour.start_date)
            req_data.set_tour_enddate(tour.end_date)
            req_data.set_employee_code(employee.code)
            req_data.set_expensecode(None)
            # req_data.set_requestercomment(forwarder.appcomment)
            req_data.set_forwarder_name(forwarder_name)
            req_data.set_forwarder_code(forwarder_code)
            # req_data.set_requestercomment(approve.appcomment)
            req_data.set_approver_name(approver_name)
            req_data.set_approver_code(approver_code)

            # elligible = TourExpense.switch_expense(clm.expensegid, clm.id)
            req_data.set_eligibleamount(None)
            resp_list.append(req_data)



        for clm in claim:
            req_data = expres.Claimreq_Response()
            req_data.set_employee_name(employee.full_name)
            req_data.set_designation(tour.empdesignation)
            req_data.set_emp_grade(tour.empgrade)
            req_data.set_branch_name(branch.name)
            req_data.set_tourid(tourid)
            req_data.set_id(clm.id)
            req_data.set_expenseid(clm.expensegid)
            req_data.set_approvedamount(clm.approvedamount)
            req_data.set_claimedamount(clm.claimedamount)
            expense = Expense.objects.using(self._current_app_schema()).get(id=clm.expensegid,entity_id=self._entity_id())
            req_data.set_expensename(expense.name)
            req_data.set_requestercomment(clm.requestercomment)
            req_data.set_invoiceheadergid(clm.invoiceheadergid)
            req_data.set_crn_no(clm.crn_no)
            req_data.set_payment_status(clm.payment_status)
            req_data.set_approvercomment(clm.approvercomment)
            status = status_get(clm.status)
            req_data.set_status(status)

            req_data.set_requestdate(tour.request_date)
            req_data.set_reason(reason.name)
            req_data.set_tour_startdate(tour.start_date)
            req_data.set_tour_enddate(tour.end_date)
            req_data.set_employee_code(employee.code)
            req_data.set_expensecode(expense.code)
            req_data.set_forwarder_name(forwarder_name)
            req_data.set_forwarder_code(forwarder_code)
            req_data.set_approver_name(approver_name)
            req_data.set_approver_code(approver_code)

            client_entertainment=0
            file_count = len(TADocuments.objects.using(self._current_app_schema()).filter(requirement_type=clm.expensegid,request_id=tourid,
                                                                            ref_type=TADocUtil.CLAIM,status=1,entity_id=self._entity_id()))
            if clm.expensegid==9:
                client_entertainment=len(associate.objects.using(self._current_app_schema()).filter(expense="Client entertain",tour_id=tourid,
                                                                                                    status=1,entity_id=self._entity_id()))
            req_data.set_client_entertainment(bool(client_entertainment))
            req_data.set_file_count(bool(file_count))




            elligible = TourExpense.switch_expense(self,clm.expensegid,clm.id)
            req_data.set_eligibleamount(elligible)
            resp_list.append(req_data)

            claimed_amount+=clm.claimedamount
            approved_amount+=clm.approvedamount
            eligible_amount+=elligible

        employee_id = request.employee_id

        claim_approver_ckeck=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tourid, request_type=(App_type.claim or App_type.CLAIM), approvedby=employee_id, entity_id=self._entity_id()).last()
        if claim_approver_ckeck is not None:
            if claim_approver_ckeck.applevel==App_level.ZERO_LEVEL:
                claim_approver=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tourid, request_type=(App_type.claim or App_type.CLAIM), applevel=App_level.FIRST_LEVEL, entity_id=self._entity_id()).first()
            elif claim_approver_ckeck.applevel==App_level.FIRST_LEVEL:
                claim_approver=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tourid, request_type=(App_type.claim or App_type.CLAIM), applevel=App_level.THIRD_LEVEL, entity_id=self._entity_id()).first()
            else :
                claim_approver=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tourid, request_type=(App_type.claim or App_type.CLAIM), applevel=App_level.THIRD_LEVEL, entity_id=self._entity_id()).last()
            if claim_approver is not None:
                ta_api_service = ApiService(self._scope())
                approver_branch_data = ta_api_service.get_branch_data_empid([claim_approver.approvedby], request)
                resp_list.approver_branch_data=approver_branch_data
                resp_list.approver_comment=claim_approver_ckeck.comment

        maker=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tourid, request_type=(App_type.claim or App_type.CLAIM), applevel=0, entity_id=self._entity_id()).last()
        if maker is not None:
            resp_list.maker_comment = maker.comment
            claim_maker=empdtl.employee_details_get(maker.approvedby, request)
            resp_list.maker_data = claim_maker
            if maker.approvedby > 0:
                claim_maker_onb = empdtl.employee_details_get(maker.approvedby, request)
                resp_list.maker_onb = claim_maker_onb
        # if tour.end_date is None:
        #     diffdays= None
        if tour.end_date is not None:
            diffdays=(time_function.ist_date()-tour.end_date.date()).days
            resp_list.is_tour_ended=bool(max(0, diffdays))

        tr_dtl_id = TourDetail.objects.using(self._current_app_schema()).filter(tour_id=tourid,
                                                                                entity_id=self._entity_id())
        detail_array=[]
        for each_dtl in tr_dtl_id:
            detail_array.append(each_dtl.id)

        booking_amt_data_per=self.get_ofc_per_amt( detail_array, [Requirements_official.personal])
        booking_amt_data_ofc=self.get_ofc_per_amt( detail_array, [Requirements_official.official])
        booking_amt_data_per_ofc=self.get_ofc_per_amt( detail_array, [Requirements_official.personal_official])

        acc_amt_ofc= booking_amt_data_ofc['Accomadation']+booking_amt_data_per_ofc['Accomadation']
        acc_amt_per= booking_amt_data_per['Accomadation_per']+booking_amt_data_per_ofc['Accomadation_per']
        cab_amt_ofc=booking_amt_data_ofc['Cab']+booking_amt_data_per_ofc['Cab']
        cab_amt_per=booking_amt_data_per['Cab_per']+booking_amt_data_per_ofc['Cab_per']
        bus_amt_ofc=booking_amt_data_ofc['Bus']+booking_amt_data_per_ofc['Bus']
        bus_amt_per=booking_amt_data_per['Bus_per']+booking_amt_data_per_ofc['Bus_per']
        train_amt_ofc=booking_amt_data_ofc['Train']+booking_amt_data_per_ofc['Train']
        train_amt_per=booking_amt_data_per['Train_per']+booking_amt_data_per_ofc['Train_per']
        air_amt_ofc=booking_amt_data_ofc['Air']+booking_amt_data_per_ofc['Air']
        air_amt_per=booking_amt_data_per['Air_per']+booking_amt_data_per_ofc['Air_per']


        admin_ttl_tck_amt_official=[{"amount":acc_amt_ofc,"name":"Accomadation"},{"amount":air_amt_ofc,"name":"Flight"},
                                    {"amount":train_amt_ofc,"name":"Train"},
                                    {"amount":bus_amt_ofc,"name":"Bus"},{"amount":cab_amt_ofc,"name":"Cab"}]
        admin_ttl_tck_amt_personal=[{"amount":acc_amt_per,"name":"Accomadation"},{"amount":air_amt_per,"name":"Flight"},
                                    {"amount":train_amt_per,"name":"Train"},
                                    {"amount":bus_amt_per,"name":"Bus"},{"amount":cab_amt_per,"name":"Cab"}]
        admin_ttl_tck_amt_total=[{"amount":acc_amt_ofc+acc_amt_per,"name":"Accomadation"},{"amount":air_amt_ofc+air_amt_per,"name":"Flight"},
                                 {"amount":train_amt_ofc+train_amt_per,"name":"Train"},
                                    {"amount":bus_amt_ofc+bus_amt_per,"name":"Bus"},{"amount":cab_amt_per+cab_amt_ofc,"name":"Cab"}]

        booking_amount=[{"name": 'Accomadation', "personal_amt": acc_amt_per, "official_amt": acc_amt_ofc, "total_amt": acc_amt_ofc+acc_amt_per},
         {"name": 'Flight', "personal_amt": air_amt_per, "official_amt": air_amt_ofc, "total_amt": air_amt_ofc+air_amt_per},
         {"name": 'Train', "personal_amt": train_amt_per, "official_amt": train_amt_ofc, "total_amt": train_amt_ofc+train_amt_per},
         {"name": 'Bus', "personal_amt": bus_amt_per, "official_amt": bus_amt_ofc, "total_amt": bus_amt_ofc+bus_amt_per},
         {"name": 'Cab', "personal_amt": cab_amt_per, "official_amt": cab_amt_ofc, "total_amt": cab_amt_per+cab_amt_ofc}]






        resp_list.claimed_amount = claimed_amount
        resp_list.approved_amount = approved_amount
        resp_list.eligible_amount = eligible_amount
        resp_list.admin_ttl_tck_amt_official = admin_ttl_tck_amt_official
        resp_list.admin_ttl_tck_amt_personal = admin_ttl_tck_amt_personal
        resp_list.admin_ttl_tck_amt_total = admin_ttl_tck_amt_total
        resp_list.booking_amount = booking_amount
        return (resp_list)


    def get_ofc_per_amt(self,detail_array,type):
        accomadation = AccomodationBookingDetails.objects.using(self._current_app_schema()).filter(travel_detail_id__in=detail_array,
                                                                                                   official__in=type,
                                                                                                   entity_id=self._entity_id())
        ticket_amount = 0
        ticket_amount_personal = 0

        for i in accomadation:
            if i.ticket_amount == None:
                tkt_amt = 0
            else:
                tkt_amt = int(i.ticket_amount)
            if i.ticket_amount_personal == None:
                tkt_amt_per = 0
            else:
                tkt_amt_per = int(i.ticket_amount_personal)
            ticket_amount = ticket_amount + tkt_amt
            ticket_amount_personal = ticket_amount_personal + tkt_amt_per
        accomadationn = ticket_amount
        accomadationn_per = ticket_amount_personal

        air = AirBookingDetails.objects.using(self._current_app_schema()).filter(travel_detail_id__in=detail_array,
                                                                                                   official__in=type,
                                                                                 entity_id=self._entity_id())
        ticket_amount = 0
        ticket_amount_personal = 0
        for i in air:
            if i.ticket_amount == None:
                tkt_amt = 0
            else:
                tkt_amt = int(i.ticket_amount)
            if i.ticket_amount_personal == None:
                tkt_amt_per = 0
            else:
                tkt_amt_per = int(i.ticket_amount_personal)
            ticket_amount = ticket_amount + tkt_amt
            ticket_amount_personal = ticket_amount_personal + tkt_amt_per
        airr = ticket_amount
        airr_per = ticket_amount_personal

        train = TrainBookingDetails.objects.using(self._current_app_schema()).filter(travel_detail_id__in=detail_array,
                                                                                                   official__in=type,
                                                                                     entity_id=self._entity_id())
        ticket_amount = 0
        ticket_amount_personal = 0
        for i in train:
            if i.ticket_amount == None:
                tkt_amt = 0
            else:
                tkt_amt = int(i.ticket_amount)
            if i.ticket_amount_personal == None:
                tkt_amt_per = 0
            else:
                tkt_amt_per = int(i.ticket_amount_personal)
            ticket_amount = ticket_amount + tkt_amt
            ticket_amount_personal = ticket_amount_personal + tkt_amt_per
        trainn = ticket_amount
        trainn_per = ticket_amount_personal

        bus = BusBookingDetails.objects.using(self._current_app_schema()).filter(travel_detail_id__in=detail_array,
                                                                                                   official__in=type,
                                                                                 entity_id=self._entity_id())
        ticket_amount = 0
        ticket_amount_personal = 0
        for i in bus:
            if i.ticket_amount == None:
                tkt_amt = 0
            else:
                tkt_amt = int(i.ticket_amount)
            if i.ticket_amount_personal == None:
                tkt_amt_per = 0
            else:
                tkt_amt_per = int(i.ticket_amount_personal)
            ticket_amount = ticket_amount + tkt_amt
            ticket_amount_personal = ticket_amount_personal + tkt_amt_per
        buss = ticket_amount
        buss_per = ticket_amount_personal

        cab = CabMapping.objects.using(self._current_app_schema()).filter(travel_detail_id__in=detail_array,
                                                                                                   official__in=type,
                                                                          entity_id=self._entity_id())
        ticket_amount = 0
        ticket_amount_personal = 0
        for i in cab:
            if i.ticket_amount == None:
                tkt_amt = 0
            else:
                tkt_amt = int(i.ticket_amount)
            if i.ticket_amount_personal == None:
                tkt_amt_per = 0
            else:
                tkt_amt_per = int(i.ticket_amount_personal)
            ticket_amount = ticket_amount + tkt_amt
            ticket_amount_personal = ticket_amount_personal + tkt_amt_per
        cabb = ticket_amount
        cabb_per = ticket_amount_personal

        admin_ttl_tck_amt = {
            'Accomadation': accomadationn,
            'Air': airr,
            'Train': trainn,
            'Bus': buss,
            'Cab': cabb,
            'Accomadation_per': accomadationn_per,
            'Air_per': airr_per,
            'Train_per': trainn_per,
            'Bus_per': buss_per,
            'Cab_per': cabb_per
        }


        return admin_ttl_tck_amt



    def get_claimreq_tour_mobile(self,tourid,request):
        resp_list = NWisefinList()
        tour= TourRequest.objects.using(self._current_app_schema()).get(id=tourid,entity_id=self._entity_id())
        claim = ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=tour.id, status=1,entity_id=self._entity_id()).all()
        reason =TourReason.objects.using(self._current_app_schema()).get(id=tour.reason,entity_id=self._entity_id())
        forwarder =TravelHistory.objects.using(self._current_app_schema()).filter(request_type=App_type.CLAIM, applevel=App_level.FIRST_LEVEL, tour_id=tour.id, entity_id=self._entity_id()).last()
        approve = TravelHistory.objects.using(self._current_app_schema()).filter(request_type=App_type.CLAIM,
                                                                                 applevel=App_level.THIRD_LEVEL,
                                                                                 tour_id=tour.id, entity_id=self._entity_id()).last()
        empdtl = ApiService(self._scope())
        forwarder_name=None
        forwarder_code=None
        approver_name=None
        approver_code=None
        if forwarder != None:
            forwarde = empdtl.employee_details_get(forwarder.approvedby, request)
            forwarder_name=forwarde.full_name
            forwarder_code = forwarde.code

        if approve != None:
            approver = empdtl.employee_details_get(approve.approvedby, request)
            approver_name = approver.full_name
            approver_code=approver.code


        employee = empdtl.employee_details_get(tour.empgid,request)
        branch = empdtl.get_branch_data(tour.empbranchgid,request)
        claimed_amount=0
        approved_amount=0
        eligible_amount=0

        for clm in claim:
            req_data = expres.Claimreq_Response()
            req_data.set_employee_name(employee.full_name)
            req_data.set_designation(tour.empdesignation)
            req_data.set_emp_grade(tour.empgrade)
            req_data.set_branch_name(branch.name)
            req_data.set_tourid(tourid)
            req_data.set_id(clm.id)
            req_data.set_expenseid(clm.expensegid)
            req_data.set_approvedamount(clm.approvedamount)
            req_data.set_claimedamount(clm.claimedamount)
            expense = Expense.objects.using(self._current_app_schema()).get(id=clm.expensegid,entity_id=self._entity_id())
            req_data.set_expensename(expense.name)
            req_data.set_requestercomment(clm.requestercomment)
            req_data.set_invoiceheadergid(clm.invoiceheadergid)
            req_data.set_approvercomment(clm.approvercomment)
            status = status_get(clm.status)
            req_data.set_status(status)

            req_data.set_requestdate(tour.request_date)
            req_data.set_reason(reason.name)
            req_data.set_tour_startdate(tour.start_date)
            req_data.set_tour_enddate(tour.end_date)
            req_data.set_employee_code(employee.code)
            req_data.set_expensecode(expense.code)
            req_data.set_forwarder_name(forwarder_name)
            req_data.set_forwarder_code(forwarder_code)
            req_data.set_approver_name(approver_name)
            req_data.set_approver_code(approver_code)



            elligible = TourExpense.switch_expense(self,clm.expensegid,clm.id)
            req_data.set_eligibleamount(elligible)
            resp_list.append(req_data)

            claimed_amount+=clm.claimedamount
            approved_amount+=clm.approvedamount
            eligible_amount+=elligible


        employee_id = request.employee_id

        claim_approver_ckeck=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tourid, request_type=(App_type.claim or App_type.CLAIM), approvedby=employee_id, entity_id=self._entity_id()).last()
        if claim_approver_ckeck is not None:
            if claim_approver_ckeck.applevel==App_level.ZERO_LEVEL:
                claim_approver=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tourid, request_type=(App_type.claim or App_type.CLAIM), applevel=App_level.FIRST_LEVEL, entity_id=self._entity_id()).first()
            elif claim_approver_ckeck.applevel==App_level.FIRST_LEVEL:
                claim_approver=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tourid, request_type=(App_type.claim or App_type.CLAIM), applevel=App_level.THIRD_LEVEL, entity_id=self._entity_id()).first()
            else :
                claim_approver=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tourid, request_type=(App_type.claim or App_type.CLAIM), applevel=App_level.THIRD_LEVEL, entity_id=self._entity_id()).last()
            if claim_approver is not None:
                ta_api_service = ApiService(self._scope())
                approver_branch_data = ta_api_service.get_branch_data_empid([claim_approver.approvedby], request)
                resp_list.approver_branch_data=approver_branch_data
                resp_list.approver_comment=claim_approver_ckeck.comment

        maker=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tourid, request_type=(App_type.claim or App_type.CLAIM), applevel=0, entity_id=self._entity_id()).last()
        if maker is not None:
            resp_list.maker_comment = maker.comment
            claim_maker=empdtl.employee_details_get(maker.approvedby, request)
            resp_list.maker_data = claim_maker
            if maker.approvedby > 0:
                claim_maker_onb = empdtl.employee_details_get(maker.approvedby, request)
                resp_list.maker_onb = claim_maker_onb
        # if tour.end_date is None:
        #     diffdays= None
        if tour.end_date is not None:
            diffdays=(time_function.ist_date()-tour.end_date.date()).days
            resp_list.is_tour_ended=bool(max(0, diffdays))
        if claimed_amount > 0:
            resp_list.claimed_amount=claimed_amount
        if claimed_amount > 0:
            resp_list.approved_amount=approved_amount
        if claimed_amount > 0:
            resp_list.eligible_amount=eligible_amount
        return resp_list

    def get_each_expense(self,tourid,request):
        resp_list = NWisefinList()
        # tour= TourRequest.objects.using(self._current_app_schema()).get(id=tourid)
        claim = ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=tourid, status=1,entity_id=self._entity_id()).all()
        # empdtl = emp_dtl()
        for clm in claim:
            req_data = expres.Claimreq_Response()
            req_data.set_expenseid(clm.expensegid)
            exp_name = TourExpense.get_expense_name(self,clm.expensegid)
            req_data.set_expensename(exp_name)
            # req_data.set_requestercomment(clm.requestercomment)
            # req_data.set_invoiceheadergid(clm.invoiceheadergid)
            # req_data.set_approvercomment(clm.approvercomment)
            # status = status_get(clm.status)
            # req_data.set_status(status)

            if clm.expensegid==9:
                exp_data = TourExpense.switch_each_expense(self,clm.expensegid,tourid,request)
                for i in exp_data.data:
                    if i is not None:
                        resp_list.append(i)
            else:
                exp_data = TourExpense.switch_each_expense(self,clm.expensegid,tourid,request)
                for i in exp_data[0].data:
                    if i is not None:
                        resp_list.append(i)

            # exp_data = self.switch_each_expense(clm.expensegid, tourid, request)
            # for i in exp_data[0].data:
            #     resp_list.append(i)
        return resp_list

    # def delete_claim(self,id):
    #     try:
    #         delete = ClaimRequest.objects.using(self._current_app_schema()).filter(id=id).update(status=Status.DELETED)
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

    # def get_claimreq(self,empid,onb,vys_page,request):
    #     if int(onb) > 0:
    #         # Tour = TourRequest.objects.using(self._current_app_schema()).filter(empgid=onb, onbehalfof=empid).all()
    #         Tour = TravelHistory.objects.using(self._current_app_schema()).filter(tour__empgid=onb, tour__onbehalfof=empid,
    #                                                                               applevel=Filterapplevel.zero, entity_id=self._entity_id()).all().order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]
    #     else:
    #         # Tour = TourRequest.objects.using(self._current_app_schema()).filter(empgid=empid).all()
    #         Tour = TravelHistory.objects.using(self._current_app_schema()).filter(tour__empgid=empid,
    #                                                                               applevel=Filterapplevel.zero, entity_id=self._entity_id()).all().order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]
    #     resp_list = NWisefinList()
    #     if len(Tour)>0:
    #         for data in Tour:
    #             tour=data.tour
    #             req_data = expres.Claimreq_Response()
    #             req_data.set_tourid(tour.id)
    #             req_data.set_requestdate(tour.request_date)
    #             req_data.set_empgid(tour.empgid)
    #             empdtl = ApiService(self._scope())
    #             employee = empdtl.employee_details_get(tour.empgid,request)
    #             req_data.set_employee_name(employee.full_name)
    #             approver = empdtl.employee_details_get(tour.empgid,request)
    #             req_data.set_approver_name(approver.full_name)
    #             # code = empdtl.employee_code_get(appr.approvedby)
    #
    #             # if int(onb) > 0 and tour.onbehalfof>0:
    #             #     onbehalf = empdtl.employee_details_get(tour.onbehalfof,request)
    #             #     req_data.set_onbehalfof(onbehalf.full_name)
    #             status = status_get(data.status)
    #             req_data.set_status(status)
    #             req_data.set_status_id(data.status)
    #             req_data.set_id(data.id)
    #             resp_list.append(req_data)
    #         vpage = NWisefinPaginator(Tour, vys_page.get_index(), 10)
    #         resp_list.set_pagination(vpage)
    #     return resp_list

    def switch_expense(self,expensegid,id):
        switcher = {
            1:TourExpense.get_el_travel_amount(self,id),
            2:TourExpense.get_el_daily_amount(self,id),
            3:TourExpense.get_el_incidental_amount(self,id),
            4:TourExpense.get_el_localconv_amount(self,id),
            5:TourExpense.get_el_lodging_amount(self,id),
            6:TourExpense.get_el_misc_amount(self,id),
            7:TourExpense.get_el_pakmov_amount(self,id),
            8:TourExpense.get_el_locdept_amount(self,id),
            9:TourExpense.get_el_associate_amount(self, id),
        }
        return switcher.get(expensegid)

    def switch_each_expense(self,expense_id,tour_id,request):
        # switcher = {
        if expense_id==1:
            data=TourExpense.get_travel_tour(self,tour_id,request),
        elif expense_id == 2:
            data=TourExpense.get_dailydeim_tour(self,tour_id),
        elif expense_id == 3:
            data=TourExpense.get_incidental_tour(self,tour_id),
        elif expense_id == 4:
            data=TourExpense.get_localconveyence_tour(self,tour_id),
        elif expense_id == 5:
            data=TourExpense.get_lodging_tour(self,tour_id,request),
        elif expense_id == 6:
            data=TourExpense.get_misc_tour(self,tour_id),
        elif expense_id == 7:
            data=TourExpense.get_packingmoving_tour(self,tour_id,request),
        elif expense_id == 8:
            data=TourExpense.get_deputation(self,tour_id)
        elif expense_id == 9:
            data=TourExpense.get_associate_tour(self,tour_id,request)
        #     return []
        # }

        return data

    @transaction.atomic
    def create_dailydeim(self,request_obj,user_id,request):
        logger.info('ta_ Daily_create- '+str(user_id)+str(request_obj))
        success_obj = NWisefinSuccess()
        total_claimed_amount = 0
        total_approved_amount = 0
        error_obj = NWisefinError()
        scope=request.scope
        Tour_service=Tour_grade(scope)
        # try:
        tour_id = request_obj['data'][0]['tour_id']
        tour_data = TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id, entity_id=self._entity_id())[0]
        if tour_data.reason==11:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.ONLY_LOCAL_CONV)
            return error_obj

        # tour_start_date = tour_data.start_date.date()
        # tour_end_date = tour_data.end_date.date()
        # if tour_data.reason == 11:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.ONLY_LOCAL_DEPT)
        #     return error_obj
        tour_data = \
            TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id, entity_id=self._entity_id())[0]

        tour_empid = tour_data.empgid
        if user_id != tour_empid:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.VALID_USER)
            return error_obj
        #
        # status = validations.exp_claim_status(tour_id)
        # if status is False:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.CLAIM_STATUS)
        #     return error_obj

        # validation_check_date = self.daily_deim_validations(request_obj, request, user_id)
        validation_check = self.expense_validations(request_obj, user_id)
        # if validation_check == False:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
        #     return error_obj
        # else:
        #     pass

        if validation_check == True:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description("Please Check The Date")
            return error_obj
        else:
            pass

        # try:
        #     if validation_check.code == 'UNEXPECTED_ERROR':
        #         error_obj = NWisefinError()
        #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #         error_obj.set_description(ErrorDescription.INVALID)
        #         return error_obj
        # except:
        set_delete = True
        if 'mobile' in request_obj['data'][0]:
            if int(request_obj['data'][0]['mobile']) == 1:
                set_delete = False
        if set_delete == True:
            daily_deim = Dailydeim.objects.using(self._current_app_schema()).filter(tour_id=tour_id,
                                                                                    entity_id=self._entity_id()).update(
                status=0)

        for dtl in request_obj['data']:
            # if dtl["boardingbyorganiser"] == '0':
            #     yesno = "NO"
            # if dtl["boardingbyorganiser"] == '1':
            #     yesno ="YES"
            eligible_value = Tour_service.dailydiem_eligible_amount(dtl, request)
            eligible_value = json.loads(eligible_value)
            eligibleamount = float(eligible_value['Eligible_amount'])
            days = eligible_value['noofdays']
            hours = eligible_value['noofhours']

            # if isinstance(approved_amount, NWisefinError):
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.INVALID_CUSTOMER_ID)
            #     error_obj.set_description(approved_amount.description)
            #     return error_obj

            claimedamount = float(dtl['foodallowance']) + float(dtl['medicalexpense'])
            if eligibleamount > float(claimedamount):
                approvedamount = float(claimedamount)
            else:
                approvedamount = eligibleamount
            total_approved_amount = total_approved_amount + float(claimedamount)
            total_claimed_amount = total_claimed_amount + float(claimedamount)

            # try:
            #     int(dtl['startdate'])
            #     millisecond = True
            # except:
            #     millisecond = False
            #
            # if millisecond is True:
            #     dtl['fromdate'] = str(datetime.fromtimestamp(int(dtl['fromdate']) / 1000.0))
            #     dtl['todate'] = str(datetime.fromtimestamp(int(dtl['todate']) / 1000.0))

            previous_claim = ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=dtl['tour_id'],
                                                                                           expensegid=dtl[
                                                                                               'expensegid'],
                                                                                           entity_id=self._entity_id())
            tour_id = dtl['tour_id']

            if 'id' in dtl:
                maker=tamaker(self._scope())
                edit_check = maker.edit_validations(tour_id, App_type.CLAIM)
                if edit_check is False:
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.CANT_EDIT_THIS_TOUR)
                    return error_obj

                if len(previous_claim) != 0:
                    data = expreq.Dailydeim_Request(dtl)

                    with transaction.atomic():
                        claimreq = ClaimRequest.objects.using(self._current_app_schema()).filter(
                            id=previous_claim[0].id, entity_id=self._entity_id()).update(
                            claimedamount=round(total_claimed_amount, 2),
                            approvedamount=round(total_claimed_amount, 2),
                            requestercomment=data.get_requestercomment(),
                            updated_by=user_id, status=1, entity_id=self._entity_id())
                        with transaction.atomic():

                            dailydeim = Dailydeim.objects.using(self._current_app_schema()).filter(id=data.get_id(),
                                                                                                   entity_id=self._entity_id()).update(
                                citytype=data.get_citytype(),
                                visitcity=data.get_visitcity(),
                                fromdate=data.get_fromdate(),
                                todate=data.get_todate(),
                                remarks=data.get_remarks(),
                                billno=data.get_billno(),
                                noofdays=days,
                                noofhours=hours,
                                foodallowance=data.get_foodallowance(),
                                medicalexpense=data.get_medicalexpense(),
                                boardingbyorganiser=data.get_boardingbyorganiser(),
                                eligibleamount=eligibleamount,
                                claimedamount=round(claimedamount, 2),
                                approvedamount=round(
                                    claimedamount, 2),
                                updated_by=user_id, status=1, updated_date=timezone.now(),
                                entity_id=self._entity_id())
                            transaction.on_commit(ClaimRequest)
                            transaction.on_commit(Dailydeim)
                            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                else:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.NO_DATA)
                    return error_obj

            else:
                data = expreq.Dailydeim_Request(dtl)
                exp_get = Expense_type_get(self._scope())
                if len(previous_claim) == 0:
                    with transaction.atomic():

                        claimreq = ClaimRequest.objects.using(self._current_app_schema()).create(
                            tour_id=data.get_tour_id(),
                            expensegid=data.get_expensegid(),
                            claimedamount=round(total_claimed_amount, 2),
                            approvedamount=round(total_claimed_amount, 2),
                            requestercomment=data.get_requestercomment(),
                            status=1,
                            created_by=user_id, entity_id=self._entity_id())
                        claim_req_id = claimreq.id
                else:
                    with transaction.atomic():

                        claimreq = ClaimRequest.objects.using(self._current_app_schema()).filter(
                            id=previous_claim[0].id, entity_id=self._entity_id()).update(tour_id=data.get_tour_id(),
                                                                                         expensegid=data.get_expensegid(),
                                                                                         claimedamount=round(
                                                                                             total_claimed_amount,
                                                                                             2),
                                                                                         approvedamount=round(
                                                                                             total_claimed_amount,
                                                                                             2),
                                                                                         requestercomment=data.get_requestercomment(),
                                                                                         status=1,
                                                                                         created_by=user_id,
                                                                                         entity_id=self._entity_id())
                        claim_req_id = previous_claim[0].id
                self.initial_exp_approvedby(data.get_tour_id(), data.get_requestercomment(),user_id)
                with transaction.atomic():
                    dailydeim = Dailydeim.objects.using(self._current_app_schema()).create(
                        tour_id=data.get_tour_id(),
                        claimreq_id=claim_req_id,
                        citytype=data.get_citytype(),
                        visitcity=data.get_visitcity(),
                        fromdate=data.get_fromdate(),
                        todate=data.get_todate(),
                        remarks=data.get_remarks(),
                        billno=data.get_billno(),
                        noofdays=days,
                        noofhours=hours,
                        boardingbyorganiser=data.get_boardingbyorganiser(),
                        foodallowance=data.get_foodallowance(),
                        medicalexpense=data.get_medicalexpense(),
                        eligibleamount=eligibleamount,
                        claimedamount=round(claimedamount, 2),
                        approvedamount=round(
                            claimedamount, 2),
                        status=1,
                        created_by=user_id, entity_id=self._entity_id())

                    transaction.on_commit(ClaimRequest)
                    transaction.on_commit(Dailydeim)
                    success_obj.set_message(SuccessMessage.CREATE_MESSAGE)

            # self.update_claimtable_amount(2, tour_id, data.get_requestercomment(), request)

        success_obj.set_status(SuccessStatus.SUCCESS)
        return success_obj

    @transaction.atomic
    def create_local_deputation(self,request_obj,user_id,request):
        logger.info('ta_ Localdept_create- '+str(user_id)+str(request_obj))
        success_obj = NWisefinSuccess()
        total_claimed_amount = 0
        total_approved_amount = 0
        validations = Validation(self._scope())
        # try:
        tourid = request_obj['data'][0]['tourgid']
        tour_data = TourRequest.objects.using(self._current_app_schema()).filter(id=tourid,entity_id=self._entity_id())[0]
        if tour_data.reason!=11:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.LOCAL_DEPT)
            return error_obj

        # tour_start_date = tour_data.start_date.date()
        # tour_end_date = tour_data.end_date.date()
        validation_check = self.localdeputation_validation(request_obj, user_id)

        try:
            if validation_check.code == 'UNEXPECTED_ERROR':
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID)
                return error_obj
        except:
            set_delete = True
            if 'mobile' in request_obj['data'][0]:
                if int(request_obj['data'][0]['mobile']) == 1:
                    set_delete = False
            if set_delete==True:
                local_dep_status = Localdeputation.objects.using(self._current_app_schema()).filter(tour_id=tourid,entity_id=self._entity_id()).update(
                status=0)


            for dtl in request_obj['data']:

                data = Local_dept_res(dtl)

                # start_date = datetime.strptime((data.startdate[:10]), '%Y-%m-%d').date()
                # end_date = datetime.strptime((data.enddate[:10]), '%Y-%m-%d').date()
                #
                # if tour_start_date > start_date or tour_end_date < start_date or tour_start_date > end_date or tour_end_date < end_date:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description("Please check the date")
                #     return error_obj

                service = Driver_bata(self._scope())
                approved_amount = service.deputation_amount(data,request)
                dtl['eligibleamount'] = json.loads(approved_amount)["Eligible_amount"]
                dtl['sysdays'] = json.loads(approved_amount)["noofdays"]
                if dtl['eligibleamount'] > float(dtl['claimedamount']):
                    dtl['approvedamount'] = float(dtl['claimedamount'])
                else:
                    dtl['approvedamount'] = dtl['eligibleamount']
                total_approved_amount=total_approved_amount+dtl['approvedamount']
                total_claimed_amount=total_claimed_amount+float(dtl['claimedamount'])

                previous_claim = ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=dtl['tourgid'], expensegid=dtl['expense_id'],entity_id=self._entity_id())
                tour_id =dtl['tourgid']

                if 'id' in dtl:
                    # edit_claim_status = validations.edit_claimstatus(tour_id)
                    # if edit_claim_status is False:
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.EDIT_STATUS)
                    #     return error_obj

                    if len(previous_claim) != 0:
                        data = expreq.Local_dept_req(dtl)
                        # date_check = validations.start_end_date(data.get_fromdate(), data.get_todate())
                        # noof_days = validations.negative_amount(data.get_noofdays())
                        # noof_leavedays = validations.negative_amount(data.get_isleave())

                        # claim_amount = validations.negative_amount(dtl['claimedamount'])
                        #
                        # if (date_check and noof_days and noof_leavedays and claim_amount) is False:
                        #     error_obj = NWisefinError()
                        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                        #     return error_obj
                        with transaction.atomic():
                            claimreq = ClaimRequest.objects.using(self._current_app_schema()).filter(id=previous_claim[0].id,entity_id=self._entity_id()).update(
                                                                   claimedamount=round(total_claimed_amount,2),
                                                                   approvedamount=round(total_approved_amount,2),
                                                                   requestercomment=data.get_requestercomment(),
                                                                   updated_by=user_id,updated_date=timezone.now(),status=1,entity_id=self._entity_id())
                            with transaction.atomic():
                                localdept = Localdeputation.objects.using(self._current_app_schema()).filter(id=data.get_id(),entity_id=self._entity_id()).update(visitcity =data.get_visitcity(),
                                                                                    fromdate = data.get_fromdate(),
                                                                                    todate = data.get_todate(),
                                                                                    sysdays = data.get_sysdays(),
                                                                                    noofdays = data.get_noofdays(),
                                                                                    isleave = data.get_isleave(),
                                                                                    eligibleamount = data.get_eligibleamount(),
                                                                                    claimedamount = round(data.get_claimedamount(),2),
                                                                                    approvedamount = round(data.get_approvedamount(),2),
                                                                                    updated_by=user_id,updated_date=timezone.now(),status=1,entity_id=self._entity_id())
                                transaction.on_commit(ClaimRequest)
                                transaction.on_commit(Localdeputation)
                                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                    else:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        error_obj.set_description(ErrorDescription.NO_DATA)
                        return error_obj

                else:

                    data = expreq.Local_dept_req(dtl)
                    # # date_check = validations.start_end_date(data.get_fromdate(), data.get_todate())
                    # # noof_days = validations.negative_amount(data.get_noofdays())
                    # # noof_leavedays = validations.negative_amount(data.get_isleave())
                    # # claim_amount = validations.negative_amount(dtl['claimedamount'])
                    # if permission_check is False:
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.INVALID)
                    #     return error_obj
                    # tour_status = validations.tour_status(tour_id)
                    # if tour_status is False:
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.TOUR_STATUS)
                    #     return error_obj
                    # status = validations.exp_claim_status(tour_id)
                    # if status is False:
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.CLAIM_STATUS)
                    #     return error_obj
                    # if (date_check and noof_days and noof_leavedays and claim_amount) is False:
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                    #     return error_obj
                    # local_dep_status = Localdeputation.objects.using(self._current_app_schema()).filter(tour_id=tourid).update(
                    #     status=0)

                    if len(previous_claim)==0:
                        with transaction.atomic():
                            claimreq = ClaimRequest.objects.using(self._current_app_schema()).create(tour_id = data.get_tourid(),
                                                        expensegid = data.get_expenseid(),
                                                        claimedamount =round(total_claimed_amount,2) ,
                                                        approvedamount = round(total_approved_amount,2),
                                                        requestercomment = data.get_requestercomment(),
                                                        status =1,
                                                        created_by=user_id,entity_id=self._entity_id())
                            claim_req_id = claimreq.id
                    else:
                        with transaction.atomic():
                            claimreq = ClaimRequest.objects.using(self._current_app_schema()).filter(id=previous_claim[0].id,entity_id=self._entity_id()).update(tour_id=data.get_tourid(),
                                                                   expensegid=data.get_expenseid(),
                                                                   claimedamount=round(total_claimed_amount,2),
                                                                   approvedamount=round(total_approved_amount,2),
                                                                   requestercomment=data.get_requestercomment(),
                                                                   status=1,
                                                                   created_by=user_id,entity_id=self._entity_id())
                            claim_req_id = previous_claim[0].id
                    self.initial_exp_approvedby(data.get_tourid(), data.get_requestercomment(),user_id)
                    with transaction.atomic():
                        localdept = Localdeputation.objects.using(self._current_app_schema()).create(tour_id = data.get_tourid(),
                                                            claimreq_id = claim_req_id,
                                                            visitcity =data.get_visitcity(),
                                                            fromdate = data.get_fromdate(),
                                                            todate = data.get_todate(),
                                                            sysdays = data.get_sysdays(),
                                                            noofdays = data.get_noofdays(),
                                                            isleave = data.get_isleave(),
                                                            eligibleamount = data.get_eligibleamount(),
                                                            claimedamount = round(data.get_claimedamount(),2),
                                                            approvedamount = round(data.get_approvedamount(),2),
                                                            status = 1,
                                                            created_by=user_id,entity_id=self._entity_id())

                        transaction.on_commit(ClaimRequest)
                        transaction.on_commit(Localdeputation)
                        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                self.update_claimtable_amount(8, tour_id, data.get_requestercomment(), request)

            # except Exception as e:
            #     print(e)
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(str(e))
            #     return error_obj
            success_obj.set_status(SuccessStatus.SUCCESS)
            return success_obj

    def delete_deputation(self,id,request,employee_id):
        try:
            tourid = Localdeputation.objects.using(self._current_app_schema()).get(id=id,entity_id=self._entity_id()).tour_id
            service = Validation(self._scope())
            permission = service.tour_maker_check(tourid, employee_id)
            if permission is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.VALID_USER)
                return error_obj
            delete = Localdeputation.objects.using(self._current_app_schema()).filter(id=id,entity_id=self._entity_id()).update(status=Status.DELETED,entity_id=self._entity_id())
            msg_obj = NWisefinSuccess()
            msg_obj.set_status(SuccessMessage.DELETE_MESSAGE)
            msg_obj.set_message({"id": id})
            self.update_claimtable_amount(8, tourid, None, request)
            return msg_obj

        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj

    def get_deputation(self,tourid):
        deputation = Localdeputation.objects.using(self._current_app_schema()).filter(tour_id=tourid, status=1,entity_id=self._entity_id()).all()
        resp_list = NWisefinList()
        for dept in deputation:
            req_data = expres.Dailydeim_Response()
            req_data.set_id(dept.id)
            req_data.set_tourgid(dept.tour_id)
            req_data.set_approvedamount(dept.approvedamount)
            req_data.set_claimedamount(dept.claimedamount)
            req_data.set_claimreqid(dept.claimreq_id)
            req_data.set_startdate(dept.fromdate)
            req_data.set_eligibleamount(dept.eligibleamount)
            # req_data.set_leave(dept.isleave)

            service=TourExpense(self._scope())

            # common_service = Common_drop_down()
            # city = common_service.common_drop_down_get(dept.visitcity,Expense_dropdown.)
            req_data.set_city(dept.visitcity)
            # is_leave=service.yn_name_get(dept.isleave)
            # req_data.set_leave_name(is_leave)
            # commondropdown = Common_dropdown_Response()
            # commondropdown.set_name(is_leave)
            # commondropdown.set_value(dept.isleave)
            # req_data.set_leave(commondropdown)
            req_data.set_isleave(dept.isleave)

            req_data.set_no_of_days(dept.noofdays)
            req_data.set_status(dept.status)
            req_data.set_sysdays(dept.sysdays)

            req_data.set_enddate(dept.todate)
            req_data.set_exp_name("Local Deputation")
            req_data.set_exp_id(8)
            resp_list.append(req_data)
        claim=ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=tourid,expensegid=8,entity_id=self._entity_id())
        if len(claim)!=0:
            resp_list.requestercomment=claim[0].requestercomment
            resp_list.approvercomment=claim[0].approvercomment
        return resp_list


    def get_dailydeim_tour(self,tourid):
        dailydiem = Dailydeim.objects.using(self._current_app_schema()).filter(tour_id=tourid, status=1,
                                                                               entity_id=self._entity_id()).all()
        resp_list = NWisefinList()
        for daily in dailydiem:
            req_data = expres.Dailydeim_Response()
            req_data.set_id(daily.id)
            req_data.set_tour_id(daily.tour_id)
            req_data.set_exp_name("dailydeim Expenses")
            # req_data.set_accbybank(daily.accbybank)
            service = TourExpense(self._scope())
            # commondropdown=Common_dropdown_Response()
            # acc_by_bank=service.yn_name_get(daily.accbybank)
            # commondropdown.set_name(acc_by_bank)
            # commondropdown.set_value(daily.accbybank)
            # req_data.set_accbybank(commondropdown)
            #
            # req_data.set_approvedamount(daily.approvedamount)
            # req_data.set_claimedamount(daily.claimedamount)
            # req_data.set_claimreqid(daily.claimreq_id)
            #
            # # common_service = Common_drop_down()
            # # city = common_service.common_drop_down_get(daily.visitcity,Expense_dropdown.)
            # req_data.set_city(daily.visitcity)
            #
            # decl=service.yn_name_get(daily.declaration)
            # commondropdown = Common_dropdown_Response()
            # commondropdown.set_name(decl)
            # commondropdown.set_value(daily.declaration)
            # req_data.set_declaration(commondropdown)
            #
            # # req_data.set_declaration_name(decl)
            # # req_data.set_boardingbybank(daily.boardingbybank)
            # bor_by_bank=service.yn_name_get(daily.boardingbybank)
            # # req_data.set_boardingbybank_name(bor_by_bank)
            # commondropdown = Common_dropdown_Response()
            # commondropdown.set_name(bor_by_bank)
            # commondropdown.set_value(daily.boardingbybank)
            # req_data.set_boardingbybank(commondropdown)
            #
            # req_data.set_fromdate(daily.from_date)
            # req_data.set_eligibleamount(daily.eligibleamount)
            # # req_data.set_isleave(daily.isleave)
            # # is_leave=service.yn_name_get(daily.isleave)
            # # # req_data.set_isleave_name(is_leave)
            # # commondropdown = Common_dropdown_Response()
            # # commondropdown.set_name(is_leave)
            # # commondropdown.set_value(daily.isleave)

            # req_data.set_isleave(commondropdown)
            req_data.set_visitcity(daily.visitcity)
            req_data.set_citytype(daily.citytype)
            req_data.set_fromdate(daily.fromdate)
            req_data.set_todate(daily.todate)
            req_data.set_remarks(daily.remarks)
            req_data.set_billno(daily.billno)
            req_data.set_boardingbyorganiser(daily.boardingbyorganiser)
            req_data.set_noofhours(daily.noofhours)
            req_data.set_noofdays(daily.noofdays)
            req_data.set_foodallowance(daily.foodallowance)
            req_data.set_medicalexpense(daily.medicalexpense)
            req_data.set_eligibleamount(daily.eligibleamount)
            req_data.set_claimedamount(daily.claimedamount)
            req_data.set_approvedamount(daily.approvedamount)
            req_data.set_status(daily.status)

            req_data.set_exp_name("Daily Diem")
            req_data.set_exp_id(2)
            resp_list.append(req_data)
        claim = ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=tourid, expensegid=2,
                                                                              entity_id=self._entity_id())
        if len(claim) != 0:
            resp_list.requestercomment = claim[0].requestercomment
            resp_list.approvercomment = claim[0].approvercomment
        return resp_list

    def delete_dailydeim(self,id,request,employee_id):
        try:
            tourid=Dailydeim.objects.using(self._current_app_schema()).get(id=id,entity_id=self._entity_id()).tour_id
            service = Validation(self._scope())
            permission = service.tour_maker_check(tourid, employee_id)
            if permission is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.VALID_USER)
                return error_obj
            delete = Dailydeim.objects.using(self._current_app_schema()).filter(id=id,entity_id=self._entity_id()).update(status=Status.DELETED,entity_id=self._entity_id())
            msg_obj = NWisefinSuccess()
            msg_obj.set_status(SuccessMessage.DELETE_MESSAGE)
            msg_obj.set_message({"id": id})
            self.update_claimtable_amount( 2, tourid, None, request)
            return msg_obj

        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj

    @transaction.atomic
    def create_incidental(self,request_obj,user_id,request):
        logger.info('ta_ Incidental_create- '+str(user_id)+str(request_obj))
        success_obj = NWisefinSuccess()
        total_eligible_amount = 0
        validations = Validation(self._scope())
        tour_data = TourRequest.objects.using(self._current_app_schema()).filter(id=request_obj['data'][0]['tourid'],entity_id=self._entity_id())[0]
        if tour_data.reason==11:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.ONLY_LOCAL_DEPT)
            return error_obj
        validation_check = self.incidental_validations(request_obj, user_id)

        try:
            if validation_check.code == 'UNEXPECTED_ERROR':
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID)
                return error_obj
        except:
            set_delete = True
            if 'mobile' in request_obj['data'][0]:
                if int(request_obj['data'][0]['mobile'])==1:
                    set_delete = False
            if set_delete==True:
                inci_status = Incidental.objects.using(self._current_app_schema()).filter(
                    tour_id=request_obj['data'][0]['tourid'],entity_id=self._entity_id()).update(status=0,entity_id=self._entity_id())

            for dtl in request_obj['data']:
                service=Tour_allowance(self._scope())
                req_obj = Allowancerequest(dtl)
                approved_amount=service.get_allowanceamount(req_obj)
                dtl['eligibleamount'] = approved_amount.elgibleamount
                total_eligible_amount=total_eligible_amount+approved_amount.elgibleamount

                previous_claim=ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=dtl['tourid'],expensegid=dtl['expenseid'],entity_id=self._entity_id())
                tour_id =dtl["tourid"]
                if 'id' in dtl:

                    # edit_claim_status = validations.edit_claimstatus(tour_id)
                    # if edit_claim_status is False:
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.EDIT_STATUS)
                    #     return error_obj

                    if len(previous_claim) !=0:
                        data = expreq.Incidental_Request(dtl)
                        # travel_hours = validations.negative_amount(data.get_travelhours())
                        # fareamount_check = validations.negative_amount(data.get_singlefare())
                        #
                        # if travel_hours is False:
                        #     error_obj = NWisefinError()
                        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                        #     return error_obj
                        # if fareamount_check is False:
                        #     error_obj = NWisefinError()
                        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        #     error_obj.set_description(ErrorDescription.AMOUNT)
                        #     return error_obj

                        with transaction.atomic():
                            claimreq = ClaimRequest.objects.using(self._current_app_schema()).filter(id=previous_claim[0].id,entity_id=self._entity_id()).update(
                                                                   claimedamount=round(total_eligible_amount,2),
                                                                   approvedamount=round(total_eligible_amount,2),
                                                                   requestercomment=data.get_requestercomment(),
                                                                   updated_by=user_id,status=1,entity_id=self._entity_id())
                            with transaction.atomic():
                                incidental = Incidental.objects.using(self._current_app_schema()).filter(id=data.get_id(),entity_id=self._entity_id()).update(code=data.get_travel_mode(),
                                                                                    samedayreturn = data.get_samedayreturn(),
                                                                                    travelhours = data.get_travelhours(),
                                                                                    singlefare = data.get_singlefare(),
                                                                                    expenses = data.get_eligibleamount(),
                                                                                    eligibleamount = data.get_eligibleamount(),
                                                                                    claimedamount = round(data.get_eligibleamount(),2),
                                                                                    approvedamount = round(data.get_eligibleamount(),2),
                                                                                    updated_by=user_id,status=1,updated_date=timezone.now())
                                transaction.on_commit(ClaimRequest)
                                transaction.on_commit(Incidental)
                                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                    else:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        error_obj.set_description(ErrorDescription.NO_DATA)
                        return error_obj


                else:
                    data = expreq.Incidental_Request(dtl)
                    # travel_hours = validations.negative_amount(data.get_travelhours())
                    # fareamount_check = validations.negative_amount(data.get_singlefare())
                    # permission_check = validations.permisssion_check(tour_id, user_id)
                    # status = validations.exp_claim_status(tour_id)
                    #
                    # if permission_check is False:
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.INVALID)
                    #     return error_obj
                    # tour_status = validations.tour_status(tour_id)
                    # if tour_status is False:
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.TOUR_STATUS)
                    #     return error_obj
                    # if status is False:
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.CLAIM_STATUS)
                    #     return error_obj
                    # inci_status = Incidental.objects.using(self._current_app_schema()).filter(
                    #     tour_id=request_obj['data'][0]['tourid']).update(status=0)
                    #
                    # if travel_hours is False:
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                    #     return error_obj
                    # if fareamount_check is False:
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                    #     return error_obj

                    if len(previous_claim)==0:
                        with transaction.atomic():

                            claimreq = ClaimRequest.objects.using(self._current_app_schema()).create(tour_id=data.get_tourid(),
                                                                   expensegid=data.get_expenseid(),
                                                                   claimedamount=round(total_eligible_amount,2),
                                                                   approvedamount=round(total_eligible_amount,2),
                                                                   requestercomment=data.get_requestercomment(),
                                                                   status=1,
                                                                   created_by=user_id,entity_id=self._entity_id())
                            claim_req_id=claimreq.id
                    else:
                        with transaction.atomic():
                            claimreq = ClaimRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=previous_claim[0].id).update(
                                claimedamount=round(total_eligible_amount,2),
                                approvedamount= round(total_eligible_amount,2),
                                requestercomment=data.get_requestercomment(),
                                updated_by=user_id,status=1)
                            claim_req_id = previous_claim[0].id

                    self.initial_exp_approvedby(data.get_tourid(), data.get_requestercomment(),user_id)
                    with transaction.atomic():
                        incidental = Incidental.objects.using(self._current_app_schema()).create(tour_id=data.get_tourid(),
                                                               claimreq_id=claim_req_id,
                                                               code=data.get_travel_mode(),
                                                               samedayreturn=data.get_samedayreturn(),
                                                               travelhours=data.get_travelhours(),
                                                               singlefare=data.get_singlefare(),
                                                               expenses=data.get_eligibleamount(),
                                                               vendorname=data.get_vendorname(),
                                                               vendortype=data.get_vendortype(),
                                                               vendorcode=data.get_vendorcode(),
                                                               gstno=data.get_gstno(),
                                                               gstrate=data.get_gstrate(),
                                                               eligibleamount=data.get_eligibleamount(),
                                                               claimedamount=round(data.get_eligibleamount(),2),
                                                               approvedamount=round(data.get_eligibleamount(),2),
                                                               status=1,
                                                               created_by=user_id,entity_id=self._entity_id())

                        transaction.on_commit(ClaimRequest)
                        transaction.on_commit(Incidental)
                        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                self.update_claimtable_amount(3, tour_id, data.get_requestercomment(), request)

            # except Exception as e:
            #     print(e)
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(str(e))
            #     return error_obj
            success_obj.set_status(SuccessStatus.SUCCESS)
            return success_obj

    def get_incidental_tour(self, tourid):
        expense = Incidental.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=tourid, status=1).all()
        resp_list = NWisefinList()
        for epx in expense:
            req_data = expres.Incidental_Response()
            req_data.set_id(epx.id)
            req_data.set_tourid(epx.tour_id)

            req_data.set_approvedamount(epx.approvedamount)
            req_data.set_claimedamount(epx.claimedamount)
            req_data.set_claimreqid(epx.claimreq_id)
            commondropdown=Common_dropdown_Response()
            # req_data.set_samedayreturn(epx.samedayreturn)
            service=TourExpense(self._scope())
            same_day=service.yn_name_get(epx.samedayreturn)
            # req_data.set_samedayreturn_name(same_day)
            commondropdown.set_name(same_day)
            commondropdown.set_value(epx.samedayreturn)
            req_data.set_samedayreturn(commondropdown)

            common_service = Common_drop_down(self._scope())
            modeof_travel = common_service.common_drop_down_get(epx.code,Expense_dropdown.incidental_travelmode)

            req_data.set_travel_mode(modeof_travel)

            req_data.set_singlefare(epx.singlefare)
            req_data.set_travelhours(epx.travelhours)
            req_data.set_eligibleamount(epx.eligibleamount)
            req_data.set_expenses(epx.expenses)
            req_data.set_status(epx.status)
            req_data.set_exp_name("Incidental Expenses")
            req_data.set_exp_id(3)
            resp_list.append(req_data)
        claim=ClaimRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=tourid,expensegid=3)
        if len(claim) != 0:
            resp_list.requestercomment=claim[0].requestercomment
            resp_list.approvercomment=claim[0].approvercomment
        return resp_list

    def delete_incidental(self,id,request,employee_id):
        try:
            tourid = Incidental.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=id).tour_id
            service = Validation(self._scope())
            permission = service.tour_maker_check(tourid, employee_id)
            if permission is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.VALID_USER)
                return error_obj
            delete = Incidental.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=id).update(status=Status.DELETED)
            msg_obj = NWisefinSuccess()
            msg_obj.set_status(SuccessMessage.DELETE_MESSAGE)
            msg_obj.set_message({"id": id})
            self.update_claimtable_amount(3, tourid, None, request)
            return msg_obj

        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj

    @transaction.atomic
    def create_localconveyence(self,request_obj,user_id,request):
        logger.info('ta_ Localconv_create- '+str(user_id)+str(request_obj))
        success_obj = NWisefinSuccess()
        total_claimed_amount = 0
        total_approved_amount = 0
        # validations =Validation(self._scope())
        tour_data = TourRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                 id=request_obj['data'][0]['tour_id'])[
            0]
        # if tour_data.reason == 11:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.ONLY_LOCAL_DEPT)
        #     return error_obj
        # # try:
        # local_validation=self.local_conveyence_validations(request_obj,user_id)
        # try:
        #     if local_validation.code == 'UNEXPECTED_ERROR':
        #         error_obj = NWisefinError()
        #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #         error_obj.set_description(ErrorDescription.INVALID)
        #         return error_obj
        # except:
        validation_check = self.expense_validations(request_obj, user_id)
        if validation_check == True:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description("Please Check The Date")
            return error_obj
        else:
            pass
        # if validation_check == True:
        #     pass
        # else:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
        #     return error_obj

        tour_empid = tour_data.empgid
        if user_id != tour_empid:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.VALID_USER)
            return error_obj

        validations=Validation(self._scope())
        status = validations.exp_claim_status(request_obj['data'][0]['tour_id'])
        if status is False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.CLAIM_STATUS)
            return error_obj

        set_delete = True
        if 'mobile' in request_obj['data'][0]:
            if int(request_obj['data'][0]['mobile']) == 1:
                set_delete = False
        if set_delete == True:
            local_status = Localconveyence.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                            tour_id=tour_data.id).update(
                status=0)
        for dtl in request_obj['data']:
            eligible_value = Tour_allowance.get_eligibleamount(self, dtl, request)
            valu_fltr = json.loads(eligible_value)
            eligible_amount = valu_fltr['Eligible_amount']

            # data = Allowancerequest(dtl)
            # Tour_service = Tour_allowance(self._scope())
            # approved_amount = Tour_service.get_eligibleamount(data)
            # dtl['eligibleamount'] = json.loads(approved_amount)["Eligible_amount"]
            if eligible_amount > float(dtl['claimedamount']):
                approvedamount = float(dtl['claimedamount'])
            else:
                approvedamount = eligible_amount
            total_approved_amount = total_approved_amount + approvedamount
            total_claimed_amount = total_claimed_amount + float(dtl['claimedamount'])

            # try:
            #     int(dtl['startdate'])
            #     millisecond = True
            # except:
            #     millisecond = False
            #
            # if millisecond is True:
            #     dtl['fromdate'] = str(datetime.fromtimestamp(int(dtl['fromdate']) / 1000.0))
            #     dtl['todate'] = str(datetime.fromtimestamp(int(dtl['todate']) / 1000.0))

            previous_claim = ClaimRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                           tour_id=dtl['tour_id'],
                                                                                           expensegid=dtl['expensegid'])
            tour_id = dtl['tour_id']
            if 'id' in dtl:
                maker = tamaker(self._scope())
                edit_check = maker.edit_validations(tour_id, App_type.CLAIM)
                if edit_check is False:
                    error_obj=NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.CANT_EDIT_THIS_TOUR)
                    return error_obj

                if len(previous_claim) != 0:
                    data = expreq.Localconveyence_Request(dtl)

                    with transaction.atomic():
                        claimreq = ClaimRequest.objects.using(self._current_app_schema()).filter(
                            entity_id=self._entity_id(), id=previous_claim[0].id).update(
                            claimedamount=round(total_claimed_amount, 2),
                            approvedamount=round(total_claimed_amount, 2),
                            requestercomment=data.get_requestercomment(),
                            updated_by=user_id, status=1)
                        with transaction.atomic():
                            local = Localconveyence.objects.using(self._current_app_schema()).filter(
                                entity_id=self._entity_id(), id=data.get_id()).update(
                                modeoftravel=data.get_modeoftravel(),
                                fromplace=data.get_fromplace(),
                                fromdate=data.get_fromdate(),
                                toplace=data.get_toplace(),
                                todate=data.get_todate(),
                                billno=data.get_billno(),
                                remarks=data.get_remarks(),
                                distance=data.get_distance(),
                                eligibleamount=eligible_amount,
                                claimedamount=round(data.get_claimedamount(), 2),
                                approvedamount=round(
                                    data.get_claimedamount(), 2),
                                updated_by=user_id, status=1, updated_date=timezone.now())
                            # transaction.on_commit(ClaimRequest)
                            # transaction.on_commit(Localconveyence)
                            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                else:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.NO_DATA)
                    return error_obj

            else:
                data = expreq.Localconveyence_Request(dtl)
                if len(previous_claim) == 0:
                    with transaction.atomic():
                        claimreq = ClaimRequest.objects.using(self._current_app_schema()).create(
                            tour_id=data.get_tour_id(),
                            expensegid=data.get_expensegid(),
                            claimedamount=round(total_claimed_amount, 2),
                            approvedamount=round(total_claimed_amount, 2),
                            requestercomment=data.get_requestercomment(),
                            status=1,
                            created_by=user_id, entity_id=self._entity_id())
                        claim_req_id = claimreq.id
                else:
                    with transaction.atomic():
                        claimreq = ClaimRequest.objects.using(self._current_app_schema()).filter(
                            entity_id=self._entity_id(), id=previous_claim[0].id).update(tour_id=data.get_tour_id(),
                                                                                         expensegid=data.get_expensegid(),
                                                                                         claimedamount=round(
                                                                                             total_claimed_amount, 2),
                                                                                         approvedamount=round(
                                                                                             total_approved_amount, 2),
                                                                                         requestercomment=data.get_requestercomment(),
                                                                                         status=1,
                                                                                         created_by=user_id)
                        claim_req_id = previous_claim[0].id
                self.initial_exp_approvedby(data.get_tour_id(), data.get_requestercomment(),user_id)
                with transaction.atomic():
                    local = Localconveyence.objects.using(self._current_app_schema()).create(tour_id=data.get_tour_id(),
                                                                                             claimreq_id=claim_req_id,
                                                                                             modeoftravel=data.get_modeoftravel(),
                                                                                             fromplace=data.get_fromplace(),
                                                                                             fromdate=data.get_fromdate(),
                                                                                             toplace=data.get_toplace(),
                                                                                             todate=data.get_todate(),
                                                                                             billno=data.get_billno(),
                                                                                             remarks=data.get_remarks(),
                                                                                             distance=data.get_distance(),
                                                                                             eligibleamount=eligible_amount,
                                                                                             claimedamount=round(
                                                                                                 data.get_claimedamount(),
                                                                                                 2),
                                                                                             approvedamount=round(
                                                                                                 data.get_claimedamount(),
                                                                                                 2),
                                                                                             status=1,
                                                                                             created_by=user_id,
                                                                                             entity_id=self._entity_id())

                    transaction.on_commit(ClaimRequest)
                    transaction.on_commit(Localconveyence)
                    success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            # self.update_claimtable_amount(4, tour_id, data.get_requestercomment(), request)

        success_obj.set_status(SuccessStatus.SUCCESS)
        return success_obj

    def get_localconveyence_tour(self, tourid):
        expense = Localconveyence.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                   tour_id=tourid, status=1).all()
        resp_list = NWisefinList()
        for exp in expense:
            req_data = expres.Localconveyence_Response()
            req_data.set_id(exp.id)
            req_data.set_tour_id(exp.tour_id)
            req_data.set_exp_name("localconveyence Expenses")
            # req_data.set_approvedamount(exp.approvedamount)
            # req_data.set_claimedamount(exp.claimedamount)
            # req_data.set_claimreqid(exp.claimreq_id)
            # req_data.set_fromplace(exp.fromplace)
            #
            # # req_data.set_onwardreturn(exp.onwardreturn)
            # service=TourExpense(self._scope())
            # onward_return_name=service.onward_return(exp.onwardreturn)
            # # req_data.set_onwardreturn_name(onward_return_name)
            # commondropdown = Common_dropdown_Response()
            # commondropdown.set_name(onward_return_name)
            # commondropdown.set_value(exp.onwardreturn)
            # req_data.set_onwardreturn(commondropdown)
            #
            # common_service = Common_drop_down()
            # modeof_travel = common_service.common_drop_down_get(exp.modeoftravel,Expense_dropdown.conv_travelmode)
            # req_data.set_modeoftravel(modeof_travel)
            # if exp.modeoftravel =="Train":
            #     common_service = Common_drop_down()
            #     subcategory_travel = common_service.common_drop_down_get(exp.subcatogory,Expense_dropdown.conv_train)
            #     req_data.set_subcatogory(subcategory_travel)
            # if exp.modeoftravel =="Road":
            #     common_service = Common_drop_down()
            #     subcategory_travel = common_service.common_drop_down_get(exp.subcatogory, Expense_dropdown.conv_road)
            #     req_data.set_subcatogory(subcategory_travel)
            #
            # common_service = Common_drop_down()
            # centre = common_service.common_drop_down_get(exp.center,Expense_dropdown.conv_center)
            # req_data.set_center(centre)

            req_data.set_modeoftravel(exp.modeoftravel)
            req_data.set_fromplace(exp.fromplace)
            req_data.set_toplace(exp.toplace)
            req_data.set_distance(exp.distance)
            req_data.set_eligibleamount(exp.eligibleamount)
            req_data.set_claimedamount(exp.claimedamount)
            req_data.set_approvedamount(exp.approvedamount)
            req_data.set_fromdate(exp.fromdate)
            req_data.set_todate(exp.todate)
            req_data.set_remarks(exp.remarks)
            req_data.set_billno(exp.billno)
            req_data.set_status(exp.status)
            req_data.set_exp_name("Local Conveyance")
            req_data.set_exp_id(4)
            resp_list.append(req_data)
        claim = ClaimRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                              tour_id=tourid, expensegid=4)
        if len(claim) != 0:
            resp_list.requestercomment = claim[0].requestercomment
            resp_list.approvercomment = claim[0].approvercomment
        return resp_list

    def delete_localconv(self,id,request,employee_id):
        try:
            tourid = Localconveyence.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=id).tour_id
            service = Validation(self._scope())
            permission = service.tour_maker_check(tourid, employee_id)
            if permission is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.VALID_USER)
                return error_obj
            delete = Localconveyence.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=id).update(status=Status.DELETED)
            msg_obj = NWisefinSuccess()
            msg_obj.set_status(SuccessMessage.DELETE_MESSAGE)
            msg_obj.set_message({"id": id})
            self.update_claimtable_amount(4, tourid, None, request)
            return msg_obj

        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj

    @transaction.atomic
    def create_lodging(self,request_obj,user_id,request):
        logger.info('ta_ Lodging_create- '+str(user_id)+str(request_obj))
        success_obj = NWisefinSuccess()
        total_claimed_amount = 0
        total_approved_amount = 0
        # validations =Validation(self._scope())
        tour_data = TourRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                 id=request_obj['data'][0]['tour_id'])[0]
        if tour_data.reason==11:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.ONLY_LOCAL_CONV)
            return error_obj
        # if tour_data.reason == 11:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.ONLY_LOCAL_DEPT)
        #     return error_obj
        # tourid = request_obj['data'][0]['tourgid']
        # tour_data = TourRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=tourid)[0]
        # validation_check = self.expense_validations(request_obj, user_id)
        #
        # try:
        #     if validation_check.code == 'UNEXPECTED_ERROR':
        #         error_obj = NWisefinError()
        #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #         error_obj.set_description(ErrorDescription.INVALID)
        #         return error_obj
        # except:
        validation_check = self.expense_validations(request_obj, user_id)
        if validation_check == True:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description("Please Check The Date")
            return error_obj
        else:
            pass

        tour_empid = tour_data.empgid
        if user_id != tour_empid:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.VALID_USER)
            return error_obj

        set_delete = True
        if 'mobile' in request_obj['data'][0]:
            if int(request_obj['data'][0]['mobile']) == 1:
                set_delete = False
        if set_delete == True:
            lodging_status = Lodging.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                      tour_id=tour_data.id).update(
                status=0)

        for dtl in request_obj['data']:
            elservice = El_lod_ser(self._scope())
            eligible_value = El_lod_ser.get_elligible_amount(self,dtl, request)
            # dtl['eligibleamount'] = json.loads(approved_amount)["Eligible_amount"]
            #
            eligible_value = json.loads(eligible_value)
            eligible_amount = eligible_value['Eligible_amount']

            if eligible_amount > float(dtl['claimedamount']):
                approvedamount = float(dtl['claimedamount'])
            else:
                approvedamount = eligible_amount
            total_approved_amount = total_approved_amount + float(dtl['claimedamount'])
            total_claimed_amount = total_claimed_amount + float(dtl['claimedamount'])

            # try:
            #     int(dtl['fromdate'])
            #     millisecond = True
            # except:
            #     millisecond = False
            #
            # if millisecond is True:
            #     dtl['fromdate'] = str(datetime.fromtimestamp(int(dtl['fromdate']) / 1000.0))
            #     dtl['todate'] = str(datetime.fromtimestamp(int(dtl['todate']) / 1000.0))

            try:
                list = Common_dropdown_details.objects.using(self._current_app_schema()).filter(
                    name=dtl['city'], entity_id=self._entity_id(), status=1)[0]
                metro_nonmetro = list.value
            except:
                metro_nonmetro = "nonmetro"

            # list = Common_dropdown.objects.using(self._current_app_schema()).get(condition)
            # common_id = list.id

            # total_approved_amount = total_approved_amount + dtl['approvedamount']
            # total_claimed_amount = total_claimed_amount + float(dtl['claimedamount'])
            # eligible_amount = El_lod_ser.get_elligible_amount(self, dtl, request)
            previous_claim = ClaimRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                           tour_id=dtl['tour_id'],
                                                                                           expensegid=dtl['expensegid'])
            tour_id = dtl['tour_id']
            if 'id' in dtl:
                maker = tamaker(self._scope())
                edit_check = maker.edit_validations(tour_id, App_type.CLAIM)
                if edit_check is False:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.CANT_EDIT_THIS_TOUR)
                    return error_obj
                if len(previous_claim) != 0:
                    data = expreq.Lodging_Request(dtl)
                    with transaction.atomic():
                        claimreq = ClaimRequest.objects.using(self._current_app_schema()).filter(
                            entity_id=self._entity_id(), id=previous_claim[0].id).update(
                            claimedamount=round(total_claimed_amount, 2),
                            approvedamount=round(total_approved_amount, 2),
                            requestercomment=data.get_requestercomment(),
                            updated_by=user_id, status=1)
                        with transaction.atomic():
                            lodg = Lodging.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                            id=data.get_id()).update(
                                entity_id=self._entity_id(),
                                Lodge_Homestay=data.get_Lodge_Homestay(),
                                metro_nonmetro=metro_nonmetro,
                                fromdate=data.get_fromdate(),
                                todate=data.get_todate(),
                                billno=data.get_billno(),
                                city=data.get_city(),
                                vendorname=data.get_vendorname(),
                                remarks=data.get_remarks(),
                                noofdays=data.get_noofdays(),
                                eligibleamount=eligible_amount,
                                Billamountexculdingtax=round(data.get_Billamountexculdingtax(), 2),
                                approvedamount=round(
                                    data.get_claimedamount(), 2),
                                taxonly=data.get_taxonly(),
                                claimedamount=round(data.get_claimedamount(), 2),
                                updated_by=user_id, status=1, updated_date=timezone.now())
                        # transaction.on_commit(ClaimRequest)
                        # transaction.on_commit(Lodging)
                        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                else:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.NO_DATA)
                    return error_obj


            else:
                data = expreq.Lodging_Request(dtl)
                if len(previous_claim) == 0:
                    with transaction.atomic():
                        claimreq = ClaimRequest.objects.using(self._current_app_schema()).create(
                            tour_id=data.get_tour_id(),
                            expensegid=data.get_expensegid(),
                            claimedamount=round(total_claimed_amount, 2),
                            approvedamount=round(total_approved_amount, 2),
                            requestercomment=data.get_requestercomment(),
                            status=1,
                            created_by=user_id, entity_id=self._entity_id())
                        claim_req_id = claimreq.id
                else:
                    with transaction.atomic():
                        claimreq = ClaimRequest.objects.using(self._current_app_schema()).filter(
                            entity_id=self._entity_id(), id=previous_claim[0].id).update(entity_id=self._entity_id(),
                                                                                         tour_id=data.get_tour_id(),
                                                                                         expensegid=data.get_expensegid(),
                                                                                         claimedamount=round(
                                                                                             total_claimed_amount, 2),
                                                                                         approvedamount=round(
                                                                                             total_approved_amount, 2),
                                                                                         requestercomment=data.get_requestercomment(),
                                                                                         status=1,
                                                                                         created_by=user_id)
                        claim_req_id = previous_claim[0].id
                self.initial_exp_approvedby(data.get_tour_id(), data.get_requestercomment(),user_id)
                with transaction.atomic():
                    lodg = Lodging.objects.using(self._current_app_schema()).create(tour_id=data.get_tour_id(),
                                                                                    claimreq_id=claim_req_id,
                                                                                    Lodge_Homestay=data.get_Lodge_Homestay(),
                                                                                    metro_nonmetro=metro_nonmetro,
                                                                                    fromdate=data.get_fromdate(),
                                                                                    todate=data.get_todate(),
                                                                                    billno=data.get_billno(),
                                                                                    vendorname=data.get_vendorname(),
                                                                                    city=data.get_city(),
                                                                                    remarks=data.get_remarks(),
                                                                                    noofdays=data.get_noofdays(),
                                                                                    eligibleamount=eligible_amount,
                                                                                    Billamountexculdingtax=round(
                                                                                        data.get_Billamountexculdingtax(),
                                                                                        2),
                                                                                    approvedamount=round(
                                                                                        data.get_claimedamount(), 2),
                                                                                    taxonly=round(data.get_taxonly()),
                                                                                    claimedamount=round(
                                                                                        data.get_claimedamount(), 2),
                                                                                    status=1,
                                                                                    created_by=user_id,
                                                                                    entity_id=self._entity_id())

                    transaction.on_commit(ClaimRequest)
                    transaction.on_commit(Lodging)
                    success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            # self.update_claimtable_amount(5, tour_id, data.get_requestercomment(), request)

        success_obj.set_status(SuccessStatus.SUCCESS)
        return success_obj

    def get_lodging_tour(self, tourid,request):
        expense = Lodging.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), tour_id=tourid,
                                                                           status=1).all()
        resp_list = NWisefinList()
        for exp in expense:
            req_data = expres.Lodging_Response()
            req_data.set_id(exp.id)
            req_data.set_tour_id(exp.tour_id)
            # req_data.set_accbybank(exp.accbybank)
            service = TourExpense(self._scope())
            # acc_by_bank=service.yn_name_get(exp.accbybank)
            # # req_data.set_accbybank_name(acc_by_bank)
            # commondropdown = Common_dropdown_Response()
            # commondropdown.set_name(acc_by_bank)
            # commondropdown.set_value(exp.accbybank)
            # req_data.set_accbybank(commondropdown)
            req_data.set_exp_name("lodging Expenses")
            req_data.set_vendorname(exp.vendorname)
            req_data.set_approvedamount(exp.approvedamount)
            # req_data.set_claimedamount(exp.claimedamount)
            # req_data.set_claimreqid(exp.claimreq_id)
            # req_data.set_acrefno(exp.acrefno)
            # req_data.set_eligibleamount(exp.eligibleamount)
            # # req_data.set_billavailable(exp.billavailable)
            # bill_available=service.yn_name_get(exp.billavailable)
            # # req_data.set_billavailable_name(bill_available)
            # commondropdown = Common_dropdown_Response()
            # commondropdown.set_name(bill_available)
            # commondropdown.set_value(exp.billavailable)
            # req_data.set_billavailable(commondropdown)
            #
            req_data.set_city(exp.city)
            # req_data.set_billnumber(exp.billnumber)
            # req_data.set_centreclassification(exp.centreclassification)
            # req_data.set_fromdate(exp.checkindate)
            # req_data.set_todate(exp.checkoutdate)
            # req_data.set_lodgcheckoutdate(exp.lodgcheckoutdate)
            # req_data.set_noofdays(exp.noofdays)
            # req_data.set_placeofactualstay(exp.placeofactualstay)
            # req_data.set_taxonly(exp.taxonly)
            # req_data.set_totalbillamount(exp.totalbillamount)
            # commondropdown_service=Common_drop_down()
            # hsn_data=commondropdown_service.hsn_percentage_get(request,exp.hsncode)
            # if isinstance(hsn_data, NWisefinError):
            #     return hsn_data
            # req_data.set_hsncode(hsn_data)
            # req_data.set_vendorcode(exp.vendorcode)
            # req_data.set_vendorgstno(exp.vendorgstno)
            # req_data.set_bankgstno(exp.bankgstno)
            # req_data.set_vendorname(exp.vendorname)
            # req_data.set_vendortype(exp.vendortype)
            # req_data.set_igst(exp.igst)
            # req_data.set_sgst(exp.sgst)
            # req_data.set_cgst(exp.cgst)
            # req_data.set_status(exp.status)
            # req_data.set_exp_name("Lodging")
            req_data.set_Lodge_Homestay(exp.Lodge_Homestay)
            req_data.set_metro_nonmetro(exp.metro_nonmetro)
            req_data.set_fromdate(exp.fromdate)
            req_data.set_todate(exp.todate)
            req_data.set_billno(exp.billno)
            req_data.set_remarks(exp.remarks)
            req_data.set_noofdays(exp.noofdays)
            req_data.set_eligibleamount(exp.eligibleamount)
            req_data.set_Billamountexculdingtax(exp.Billamountexculdingtax)
            req_data.set_taxonly(exp.taxonly)
            req_data.set_claimedamount(exp.claimedamount)
            req_data.set_exp_id(5)
            resp_list.append(req_data)
        claim = ClaimRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                              tour_id=tourid, expensegid=5)
        if len(claim) != 0:
            resp_list.requestercomment = claim[0].requestercomment
            resp_list.approvercomment = claim[0].approvercomment
        return resp_list

    def delete_lodging(self,id,request,employee_id):
        try:
            tourid = Lodging.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=id).tour_id
            service = Validation(self._scope())
            permission = service.tour_maker_check(tourid, employee_id)
            if permission is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.VALID_USER)
                return error_obj
            delete = Lodging.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=id).update(status=Status.DELETED)
            msg_obj = NWisefinSuccess()
            msg_obj.set_status(SuccessMessage.DELETE_MESSAGE)
            msg_obj.set_message({"id": id})
            self.update_claimtable_amount(5, tourid, None, request)
            return msg_obj

        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj

    @transaction.atomic
    def create_misc(self,request_obj,user_id,request):
        logger.info('ta_ Misc_create- '+str(user_id)+str(request_obj))
        success_obj = NWisefinSuccess()
        total_claimed_amount = 0
        total_approved_amount = 0
        validations =Validation(self._scope())
        # try:
        tour_data = TourRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=request_obj['data'][0]['tourgid'])[0]
        if tour_data.reason==11:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.ONLY_LOCAL_DEPT)
            return error_obj
        validation_check =self.misc_validation(request_obj,user_id)
        try:
            if validation_check.code == 'UNEXPECTED_ERROR':
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID)
                return error_obj
        except:
            set_delete = True
            if 'mobile' in request_obj['data'][0]:
                if int(request_obj['data'][0]['mobile']) == 1:
                    set_delete = False
            if set_delete == True:
                misc_status = Misc.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=request_obj['data'][0]['tourgid']).update(status=0)

            for dtl in request_obj['data']:
                data = Allowancerequest(dtl)
                Tour_service = Tour_allowance(self._scope())
                approved_amount = Tour_service.get_eligibleamount_misc(data)
                dtl['eligibleamount'] = float(json.loads(approved_amount)["Eligible_amount"])
                if dtl['eligibleamount'] > float(dtl['claimedamount']):
                    dtl['approvedamount'] = float(dtl['claimedamount'])
                else:
                    dtl['approvedamount'] = dtl['eligibleamount']
                total_approved_amount=total_approved_amount+dtl['approvedamount']
                total_claimed_amount=total_claimed_amount+float(dtl['claimedamount'])


                previous_claim = ClaimRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=dtl['tourgid'], expensegid=dtl['expense_id'])
                tour_id=dtl['tourgid']



                if 'id' in dtl:
                    # claim_amount_check = validations.negative_amount(dtl['claimedamount'])

                    # edit_claim_status = validations.edit_claimstatus(tour_id)
                    # if edit_claim_status is False:
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.EDIT_STATUS)
                    #     return error_obj

                    # if claim_amount_check is False:
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.AMOUNT)
                    #     return error_obj
                    #

                    if len(previous_claim) != 0:
                        data = expreq.Misc_Request(dtl)
                        with transaction.atomic():
                            claimreq = ClaimRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=previous_claim[0].id).update(
                                                                   claimedamount=round(total_claimed_amount,2),
                                                                   approvedamount=round(total_approved_amount,2),
                                                                   requestercomment=data.get_requestercomment(),
                                                                   updated_by=user_id,status=1)
                            with transaction.atomic():
                                misc = Misc.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=data.get_id()).update(description=data.get_description(),
                                                                                    expreason = data.get_expreason(),
                                                                                    eligibleamount = data.get_eligibleamount(),
                                                                                    claimedamount = round(data.get_claimedamount(),2),
                                                                                    approvedamount = round(data.get_approvedamount(),2),
                                                                                    center = data.get_center(),
                                                                                    updated_by=user_id,status=1,updated_date=timezone.now())
                                transaction.on_commit(ClaimRequest)
                                transaction.on_commit(Misc)
                                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                    else:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        error_obj.set_description(ErrorDescription.NO_DATA)
                        return error_obj

                else:

                    data = expreq.Misc_Request(dtl)
                    # claim_amount_check = validations.negative_amount(dtl['claimedamount'])
                    # permission_check = validations.permisssion_check(tour_id, user_id)

                    # if permission_check is False:
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.INVALID)
                    #     return error_obj
                    # tour_status = validations.tour_status(tour_id)
                    # if tour_status is False:
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.TOUR_STATUS)
                    #     return error_obj
                    # if status is False:
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.CLAIM_STATUS)
                    #     return error_obj
                    # if claim_amount_check is False:
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.AMOUNT)
                    #     return error_obj
                    # misc_status = Misc.objects.using(self._current_app_schema()).filter(
                    #     tour_id=request_obj['data'][0]['tourgid']).update(status=0)

                    if len(previous_claim)==0:
                        with transaction.atomic():
                            claimreq = ClaimRequest.objects.using(self._current_app_schema()).create(tour_id = data.get_tourid(),
                                                        expensegid = data.get_expenseid(),
                                                        claimedamount =round(total_claimed_amount,2) ,
                                                        approvedamount = round(total_approved_amount,2),
                                                        requestercomment = data.get_requestercomment(),
                                                        status =1,
                                                        created_by=user_id,entity_id=self._entity_id())
                            claim_req_id = claimreq.id
                    else:
                        with transaction.atomic():
                            claimreq = ClaimRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=previous_claim[0].id).update(tour_id=data.get_tourid(),
                                                                   expensegid=data.get_expenseid(),
                                                                   claimedamount=round(total_claimed_amount,2),
                                                                   approvedamount=round(total_approved_amount,2),
                                                                   requestercomment=data.get_requestercomment(),
                                                                   status=1,
                                                                   created_by=user_id)
                            claim_req_id = previous_claim[0].id
                    self.initial_exp_approvedby(data.get_tourid(), data.get_requestercomment(),user_id)
                    with transaction.atomic():

                        misc = Misc.objects.using(self._current_app_schema()).create(tour_id = data.get_tourid(),
                                                            claimreq_id = claim_req_id,
                                                            description=data.get_description(),
                                                            expreason = data.get_expreason(),
                                                            vendorname = data.get_vendorname(),
                                                            vendortype = data.get_vendortype(),
                                                            vendorcode = data.get_vendorcode(),
                                                            bankgstno = data.get_bankgstno(),
                                                            vendorgstno = data.get_vendorgstno(),
                                                            center = data.get_center(),
                                                            igst = data.get_igst(),
                                                            cgst = data.get_cgst(),
                                                            sgst = data.get_sgst(),
                                                            eligibleamount = data.get_eligibleamount(),
                                                            claimedamount = round(data.get_claimedamount(),2),
                                                            approvedamount = round(data.get_approvedamount(),2),
                                                            status =1,
                                                            created_by=user_id,entity_id=self._entity_id())

                        transaction.on_commit(ClaimRequest)
                        transaction.on_commit(Misc)
                        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                self.update_claimtable_amount(6, tour_id, data.get_requestercomment(), request)

            # except Exception as e:
            #     print(e)
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(str(e))
            #     return error_obj
            success_obj.set_status(SuccessStatus.SUCCESS)
            return success_obj

    def get_misc_tour(self, tourid):
        expense = Misc.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=tourid, status=1).all()
        resp_list = NWisefinList()
        for exp in expense:
            req_data = expres.Misc_Response()
            req_data.set_id(exp.id)
            req_data.set_tourid(exp.tour_id)
            req_data.set_description(exp.description)
            req_data.set_approvedamount(exp.approvedamount)
            req_data.set_claimedamount(exp.claimedamount)
            req_data.set_claimreqid(exp.claimreq_id)
            req_data.set_eligibleamount(exp.eligibleamount)
            req_data.set_status(exp.status)
            common_service=Common_drop_down(self._scope())
            center=common_service.common_drop_down_get(exp.center,Expense_dropdown.misc_centre)
            req_data.set_center(center)
            expreason=common_service.common_drop_down_get(exp.expreason,Expense_dropdown.misc_reason)
            req_data.set_expreason(expreason)
            req_data.set_exp_name("Miscellaneous Charges")
            req_data.set_exp_id(6)
            resp_list.append(req_data)
        claim=ClaimRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=tourid,expensegid=6)
        if len(claim) != 0:
            resp_list.requestercomment=claim[0].requestercomment
            resp_list.approvercomment=claim[0].approvercomment
        return resp_list

    def delete_misc(self,id,request,employee_id):
        try:
            tourid = Misc.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=id).tour_id
            service = Validation(self._scope())
            permission = service.tour_maker_check(tourid, employee_id)
            if permission is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.VALID_USER)
                return error_obj
            delete = Misc.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=id).update(status=Status.DELETED)
            msg_obj = NWisefinSuccess()
            msg_obj.set_status(SuccessMessage.DELETE_MESSAGE)
            msg_obj.set_message({"id": id})
            self.update_claimtable_amount(6, tourid, None, request)
            return msg_obj

        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj

    @transaction.atomic
    def create_packingmoving(self,request_obj,user_id,request):
        logger.info('ta_ Packing_create- '+str(user_id)+str(request_obj))
        success_obj = NWisefinSuccess()
        total_claimed_amount = 0
        total_approved_amount = 0
        validations=Validation(self._scope())
        # try:
        tour_data = TourRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=request_obj['data'][0]['tourgid'])[0]
        if tour_data.reason==11:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.ONLY_LOCAL_DEPT)
            return error_obj
        validation_check = self.packingandmoving_validation(request_obj, user_id)

        try:
            if validation_check.code == 'UNEXPECTED_ERROR':
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID)
                return error_obj
        except:
            set_delete = True
            if 'mobile' in request_obj['data'][0]:
                if int(request_obj['data'][0]['mobile']) == 1:
                    set_delete = False
            if set_delete == True:
                packing_status = PackingMoving.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                    tour_id=request_obj['data'][0]['tourgid']).update(status=0)

            for dtl in request_obj['data']:
                data = Tol_amo_pkmo_req(dtl)
                service = Packing_moving_ser(self._scope())
                approved_amount = service.total_amount(data)
                dtl['eligibleamount'] = json.loads(approved_amount)["Eligible_amount"]
                dtl['eligtransamt'] = json.loads(approved_amount)["transportation_amount"]
                dtl['daysdrivereng'] = json.loads(approved_amount)["daysdrivereng"]
                dtl['driverbatta'] = json.loads(approved_amount)["driverbatta"]
                dtl['eligbreakagecharge'] = json.loads(approved_amount)["breakagecharge"]

                service=Tourno_details(self._scope())
                grade=service.grade_get_tourid(dtl['tourgid'])
                service=Packing_moving_ser(self._scope())
                maxtonnage_data = service.get_grade_elligibility(grade)
                dtl['maxeligton'] = maxtonnage_data[0].maxtonnage

                if dtl['eligibleamount'] > float(dtl['claimedamount']):
                    dtl['approvedamount'] = float(dtl['claimedamount'])
                else:
                    dtl['approvedamount'] = dtl['eligibleamount']
                total_approved_amount=total_approved_amount+dtl['approvedamount']
                total_claimed_amount=total_claimed_amount+float(dtl['claimedamount'])


                previous_claim = ClaimRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=dtl['tourgid'], expensegid=dtl['expense_id'])
                tour_id =dtl['tourgid']

                if 'id' in dtl:

                    # edit_claim_status = validations.edit_claimstatus(tour_id)
                    # if edit_claim_status is False:
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.EDIT_STATUS)
                    #     return error_obj

                    if len(previous_claim) != 0:
                        data = expreq.PackingMoving_Request(dtl)
                        # ttl_distance = validations.negative_amount(data.get_totaldisttrans())
                        # hill_distance = validations.negative_amount(data.get_distinhilly())
                        # tonage = validations.negative_amount(data.get_tonnagehhgood())
                        # max_tonage = validations.negative_amount(data.get_maxeligton())
                        # eli_transport =validations.negative_amount(data.get_eligtransamt())
                        # transport = validations.negative_amount(data.get_transchargesvehicle())
                        # travel_time =validations.negative_amount(data.get_traveltimeinhours())
                        # no_days_driver=validations.negative_amount(data.get_daysdrivereng())
                        # driver_battas =validations.negative_amount(data.get_driverbatta())
                        # octri =validations.negative_amount(data.get_octroivehicle())
                        # breakage =validations.negative_amount(data.get_breakagecharges())
                        # eligi_breakage =validations.negative_amount(data.get_eligbreakagecharge())
                        # claim_amt=validations.negative_amount(dtl['claimedamount'])
                        # if (ttl_distance and hill_distance and tonage and max_tonage and eli_transport and transport and travel_time and no_days_driver and driver_battas and octri \
                        #         and breakage and eligi_breakage and claim_amt) is False:
                        #     error_obj = NWisefinError()
                        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                        #     return error_obj
                        with transaction.atomic():
                            claimreq = ClaimRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=previous_claim[0].id).update(
                                                                   claimedamount=round(total_claimed_amount,2),
                                                                   approvedamount=round(total_approved_amount,2),
                                                                   requestercomment=data.get_requestercomment(),
                                                                   updated_by=user_id,status=1)
                            with transaction.atomic():
                                packingmvg = PackingMoving.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=data.get_id()).update(twowheelertrans=data.get_twowheelertrans(),
                                                                                    hhgoodstrans = data.get_hhgoodstrans(),
                                                                                    transtwowheelerby = data.get_transtwowheelerby(),
                                                                                    ibaappvendor = data.get_ibaappvendor(),
                                                                                    totaldisttrans = data.get_totaldisttrans(),
                                                                                    distinhilly = data.get_distinhilly(),
                                                                                    tonnagehhgood = data.get_tonnagehhgood(),
                                                                                    maxeligton = data.get_maxeligton(),
                                                                                    billedamthhgoodstrans = data.get_billedamthhgoodstrans(),
                                                                                    eligtransamt = data.get_eligtransamt(),
                                                                                    transchargesvehicle = data.get_transchargesvehicle(),
                                                                                    vehicletransbydriver = data.get_vehicletransbydriver(),
                                                                                    traveltimeinhours = data.get_traveltimeinhours(),
                                                                                    daysdrivereng = data.get_daysdrivereng(),
                                                                                    driverbatta = data.get_driverbatta(),
                                                                                    octroivehicle = data.get_octroivehicle(),
                                                                                    breakagecharges = data.get_breakagecharges(),
                                                                                    receiptlosses = data.get_receiptlosses(),
                                                                                    eligbreakagecharge = data.get_eligbreakagecharge(),
                                                                                    hsncode = data.get_hsncode(),
                                                                                    vendorname = data.get_vendorname(),
                                                                                    vendortype = data.get_vendortype(),
                                                                                    vendorcode = data.get_vendorcode(),
                                                                                    bankgstno = data.get_bankgstno(),
                                                                                    vendorgstno = data.get_vendorgstno(),
                                                                                    igst = data.get_igst(),
                                                                                    cgst = data.get_cgst(),
                                                                                    sgst = data.get_sgst(),
                                                                                    eligibleamount = data.get_eligibleamount(),
                                                                                    claimedamount = round(data.get_claimedamount(),2),
                                                                                    approvedamount = round(data.get_approvedamount(),2),
                                                                                    updated_by=user_id,status=1,updated_date=timezone.now())
                                transaction.on_commit(ClaimRequest)
                                transaction.on_commit(PackingMoving)
                                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                    else:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        error_obj.set_description(ErrorDescription.NO_DATA)
                        return error_obj

                else:
                    data = expreq.PackingMoving_Request(dtl)
                    # permission_check = validations.permisssion_check(tour_id, user_id)
                    # if permission_check is False:
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.INVALID)
                    #     return error_obj
                    # tour_status = validations.tour_status(tour_id)
                    # if tour_status is False:
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.TOUR_STATUS)
                    #     return error_obj
                    # if status is False:
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.CLAIM_STATUS)
                    #     return error_obj
                    # packing_status = PackingMoving.objects.using(self._current_app_schema()).filter(
                    #     tour_id=request_obj['data'][0]['tourgid']).update(status=0)

                    # ttl_distance = validations.negative_amount(data.get_totaldisttrans())
                    # hill_distance = validations.negative_amount(data.get_distinhilly())
                    # tonage = validations.negative_amount(data.get_tonnagehhgood())
                    # max_tonage = validations.negative_amount(data.get_maxeligton())
                    # eli_transport = validations.negative_amount(data.get_eligtransamt())
                    # transport = validations.negative_amount(data.get_transchargesvehicle())
                    # travel_time = validations.negative_amount(data.get_traveltimeinhours())
                    # no_days_driver = validations.negative_amount(data.get_daysdrivereng())
                    # driver_battas = validations.negative_amount(data.get_driverbatta())
                    # octri = validations.negative_amount(data.get_octroivehicle())
                    # breakage = validations.negative_amount(data.get_breakagecharges())
                    # eligi_breakage = validations.negative_amount(data.get_eligbreakagecharge())
                    # claim_amt = validations.negative_amount(dtl['claimedamount'])
                    # if (ttl_distance and hill_distance and tonage and max_tonage  and eli_transport and transport and travel_time and no_days_driver and driver_battas and octri \
                    #         and breakage and eligi_breakage and claim_amt) is False:
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                    #     return error_obj
                    if len(previous_claim) == 0:
                        with transaction.atomic():
                            claimreq = ClaimRequest.objects.using(self._current_app_schema()).create(tour_id = data.get_tourid(),
                                                        expensegid = data.get_expenseid(),
                                                        claimedamount =round(total_claimed_amount,2) ,
                                                        approvedamount = round(total_approved_amount,2),
                                                        requestercomment = data.get_requestercomment(),
                                                        status =1,
                                                        created_by=user_id,entity_id=self._entity_id())
                            claim_req_id = claimreq.id
                    else:
                        with transaction.atomic():
                            claimreq = ClaimRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=previous_claim[0].id).update(
                                tour_id=data.get_tourid(),
                                expensegid=data.get_expenseid(),
                                claimedamount=round(total_claimed_amount,2),
                                approvedamount=round(total_approved_amount,2),
                                requestercomment=data.get_requestercomment(),
                                status=1,
                                created_by=user_id)
                            claim_req_id = previous_claim[0].id
                    self.initial_exp_approvedby(data.get_tourid(), data.get_requestercomment(),user_id)
                    with transaction.atomic():
                        packingmvg = PackingMoving.objects.using(self._current_app_schema()).create(tour_id = data.get_tourid(),
                                                            claimreq_id = claim_req_id,
                                                            twowheelertrans=data.get_twowheelertrans(),
                                                            hhgoodstrans = data.get_hhgoodstrans(),
                                                            transtwowheelerby = data.get_transtwowheelerby(),
                                                            ibaappvendor = data.get_ibaappvendor(),
                                                            totaldisttrans = data.get_totaldisttrans(),
                                                            distinhilly = data.get_distinhilly(),
                                                            tonnagehhgood = data.get_tonnagehhgood(),
                                                            maxeligton = data.get_maxeligton(),
                                                            billedamthhgoodstrans = data.get_billedamthhgoodstrans(),
                                                            eligtransamt = data.get_eligtransamt(),
                                                            transchargesvehicle = data.get_transchargesvehicle(),
                                                            vehicletransbydriver = data.get_vehicletransbydriver(),
                                                            traveltimeinhours = data.get_traveltimeinhours(),
                                                            daysdrivereng = data.get_daysdrivereng(),
                                                            driverbatta = data.get_driverbatta(),
                                                            octroivehicle = data.get_octroivehicle(),
                                                            breakagecharges = data.get_breakagecharges(),
                                                            receiptlosses = data.get_receiptlosses(),
                                                            eligbreakagecharge = data.get_eligbreakagecharge(),
                                                            hsncode = data.get_hsncode(),
                                                            vendorname = data.get_vendorname(),
                                                            vendortype = data.get_vendortype(),
                                                            vendorcode = data.get_vendorcode(),
                                                            bankgstno = data.get_bankgstno(),
                                                            vendorgstno = data.get_vendorgstno(),
                                                            igst = data.get_igst(),
                                                            cgst = data.get_cgst(),
                                                            sgst = data.get_sgst(),
                                                            eligibleamount = data.get_eligibleamount(),
                                                            claimedamount = round(data.get_claimedamount(),2),
                                                            approvedamount = round(data.get_approvedamount(),2),
                                                            status = 1,
                                                            created_by=user_id,entity_id=self._entity_id())

                        transaction.on_commit(ClaimRequest)
                        transaction.on_commit(PackingMoving)
                        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)

                self.update_claimtable_amount(7, tour_id, data.get_requestercomment(), request)

            # except Exception as e:
            #     print(e)
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(str(e))
            #     return error_obj
            success_obj.set_status(SuccessStatus.SUCCESS)
            return success_obj

    def get_packingmoving_tour(self, tourid,request):
        expense = PackingMoving.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=tourid, status=1).all()
        resp_list = NWisefinList()
        for exp in expense:
            req_data = expres.PackingMoving_Response()
            req_data.set_id(exp.id)
            req_data.set_tourid(exp.tour_id)
            req_data.set_claimreqid(exp.claimreq_id)
            req_data.set_billedamthhgoodstrans(exp.billedamthhgoodstrans)
            req_data.set_breakagecharges(exp.breakagecharges)
            req_data.set_daysdrivereng(exp.daysdrivereng)
            req_data.set_distinhilly(exp.distinhilly)
            req_data.set_driverbatta(exp.driverbatta)
            req_data.set_eligbreakagecharge(exp.eligbreakagecharge)
            req_data.set_eligtransamt(exp.eligtransamt)
            # req_data.set_hhgoodstrans(exp.hhgoodstrans)
            service=TourExpense(self._scope())
            hhgoods_trans=service.yn_name_get(exp.hhgoodstrans)
            # req_data.set_hhgoodstrans_name(hhgoods_trans)
            commondropdown = Common_dropdown_Response()
            commondropdown.set_name(hhgoods_trans)
            commondropdown.set_value(exp.hhgoodstrans)
            req_data.set_hhgoodstrans(commondropdown)

            req_data.set_ibaappvendor(exp.ibaappvendor)
            req_data.set_maxeligton(exp.maxeligton)
            req_data.set_octroivehicle(exp.octroivehicle)
            # req_data.set_receiptloss(exp.receiptlosses)
            receipt_loss=service.yn_name_get(exp.receiptlosses)
            # req_data.set_receiptloss_name(receipt_loss)
            commondropdown = Common_dropdown_Response()
            commondropdown.set_name(receipt_loss)
            commondropdown.set_value(exp.receiptlosses)
            req_data.set_receipt_loss(commondropdown)

            req_data.set_tonnagehhgood(exp.tonnagehhgood)
            req_data.set_totaldisttrans(exp.totaldisttrans)
            req_data.set_transchargesvehicle(exp.transchargesvehicle)
            req_data.set_traveltime(exp.traveltimeinhours)
            # req_data.set_transtwowheelerby(exp.transtwowheelerby)
            # req_data.set_twowheelertrans(exp.twowheelertrans)
            two_wheeler_trans=service.yn_name_get(exp.twowheelertrans)
            # req_data.set_twowheelertrans_name(two_wheeler_trans)
            two_wheeler_transby=service.two_wheeler_trans(exp.transtwowheelerby)
            # req_data.set_transtwowheelerby_name(two_wheeler_transby)

            commondropdown = Common_dropdown_Response()
            commondropdown.set_name(two_wheeler_transby)
            commondropdown.set_value(exp.transtwowheelerby)
            req_data.set_transtwowheelerby(commondropdown)

            commondropdown = Common_dropdown_Response()
            commondropdown.set_name(two_wheeler_trans)
            commondropdown.set_value(exp.twowheelertrans)
            req_data.set_twowheelertrans(commondropdown)

            # req_data.set_vehicletransbydriver(exp.vehicletransbydriver)
            vehicletrans_bydriver=service.yn_name_get(exp.vehicletransbydriver)
            # req_data.set_vehicletransbydriver_name(vehicletrans_bydriver)
            commondropdown = Common_dropdown_Response()
            commondropdown.set_name(vehicletrans_bydriver)
            commondropdown.set_value(exp.vehicletransbydriver)
            req_data.set_vehicletransbydriver(commondropdown)

            req_data.set_claimedamount(exp.claimedamount)
            req_data.set_eligibleamount(exp.eligibleamount)
            req_data.set_approvedamount(exp.approvedamount)
            # req_data.set_hsncode(exp.hsncode)
            commondropdown_service=Common_drop_down(self._scope())
            hsn_data=commondropdown_service.hsn_percentage_get(request,exp.hsncode)
            if isinstance(hsn_data, NWisefinError):
                return hsn_data
            req_data.set_hsncode(hsn_data)
            req_data.set_vendorcode(exp.vendorcode)
            req_data.set_vendorgstno(exp.vendorgstno)
            req_data.set_bankgstno(exp.bankgstno)
            req_data.set_vendorname(exp.vendorname)
            req_data.set_vendortype(exp.vendortype)
            req_data.set_igst(exp.igst)
            req_data.set_sgst(exp.sgst)
            req_data.set_cgst(exp.cgst)
            req_data.set_status(exp.status)
            req_data.set_exp_name("Packaging/Freight")
            req_data.set_exp_id(7)
            resp_list.append(req_data)
        claim=ClaimRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=tourid,expensegid=7)
        if len(claim) != 0:
            resp_list.requestercomment=claim[0].requestercomment
            resp_list.approvercomment=claim[0].approvercomment
        return resp_list

    def delete_packing(self,id,request,employee_id):
        try:
            tourid = PackingMoving.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=id).tour_id
            service = Validation(self._scope())
            permission = service.tour_maker_check(tourid, employee_id)
            if permission is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.VALID_USER)
                return error_obj
            delete = PackingMoving.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=id).update(status=Status.DELETED)
            msg_obj = NWisefinSuccess()
            msg_obj.set_status(SuccessMessage.DELETE_MESSAGE)
            msg_obj.set_message({"id": id})
            self.update_claimtable_amount(7, tourid, None, request)
            return msg_obj

        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj

    @transaction.atomic
    def create_travel(self, request_obj, user_id, request):
        logger.info('ta_ Travel_create- '+str(user_id)+str(request_obj))
        success_obj = NWisefinSuccess()
        total_claimed_amount = 0
        tour_id = request_obj['data'][0]['tour_id']
        tour_data = TourRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                     id=tour_id)[0]
        if tour_data.reason==11:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.ONLY_LOCAL_CONV)
            return error_obj
        # if tour_data.reason==11:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.ONLY_LOCAL_DEPT)
        #     return error_obj
        #
        # validation_check = self.travel_validations(request_obj, user_id)
        #
        # try:
        #     if validation_check.code == 'UNEXPECTED_ERROR':
        #         error_obj = NWisefinError()
        #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #         error_obj.set_description(ErrorDescription.INVALID)
        #         return error_obj
        # except:
        validation_check = self.expense_validations(request_obj, user_id)
        if validation_check == True:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description("Please Check The Date")
            return error_obj
        else:
            pass

        tour_empid = tour_data.empgid
        if user_id != tour_empid:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.VALID_USER)
            return error_obj

        # status = validations.exp_claim_status(tour_id)
        # if status is False:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.CLAIM_STATUS)
        #     return error_obj

        set_delete = True
        if 'mobile' in request_obj['data'][0]:
            if int(request_obj['data'][0]['mobile']) == 1:
                set_delete = False
        if set_delete == True:
            travel_status = Travel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                    tour_id=tour_id).update(status=0)

        for dtl in request_obj['data']:
            # service = Tourno_details(self._scope())
            # grade = service.grade_get_tourid(dtl['tourid'])
            # service = Packing_moving_ser(self._scope())
            # travel_class = service.get_grade_elligibility(grade)
            # dtl['eligibletravel'] = travel_class[0].travelclass
            # total_claimed_amount = total_claimed_amount + float(dtl['claimedamount'])
            # total_approved_amount = total_approved_amount + float(dtl['totaltkttamt'])
            total_claimed_amount = total_claimed_amount + float(dtl['totaltkttamt'])

            # try:
            #     int(dtl['startdate'])
            #     millisecond = True
            # except:
            #     millisecond = False
            #
            # if millisecond is True:
            #     dtl['fromdate'] = str(datetime.fromtimestamp(int(dtl['fromdate']) / 1000.0))
            #     dtl['todate'] = str(datetime.fromtimestamp(int(dtl['todate']) / 1000.0))

            previous_claim = ClaimRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                           tour_id=dtl['tour_id'],
                                                                                           expensegid=dtl['expensegid'])
            tour_id = dtl['tour_id']
            if 'id' in dtl:
                maker = tamaker(self._scope())
                edit_check = maker.edit_validations(tour_id, App_type.CLAIM)
                if edit_check == False:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.CANT_EDIT_THIS_TOUR)
                    return error_obj
                if len(previous_claim) != 0:
                    data = expreq.Travel_Request(dtl)

                    with transaction.atomic():
                        claimreq = ClaimRequest.objects.using(self._current_app_schema()).filter(
                            entity_id=self._entity_id(), id=previous_claim[0].id).update(
                            claimedamount=round(total_claimed_amount, 2),
                            approvedamount=round(total_claimed_amount, 2),
                            requestercomment=data.get_requestercomment(),
                            updated_by=user_id, status=1)
                        with transaction.atomic():
                            travel = Travel.objects.using(self._current_app_schema()).filter(
                                entity_id=self._entity_id(), id=data.get_id()).update(entity_id=self._entity_id(),
                                                                                      traveltype=data.get_traveltype(),
                                                                                      fromdate=data.get_fromdate(),
                                                                                      fromplace=data.get_fromplace(),
                                                                                      todate=data.get_todate(),
                                                                                      toplace=data.get_toplace(),
                                                                                      remarks=data.get_remarks(),
                                                                                      billno=data.get_billno(),
                                                                                      vendorname=data.get_vendorname(),
                                                                                      totaltkttamt=data.get_totaltkttamt(),
                                                                                      approvedamount=data.get_totaltkttamt(),
                                                                                      tktby=data.get_tktby(),
                                                                                      actualmode=data.get_actualmode(),
                                                                                      travelclass=data.get_travelclass(),
                                                                                      eligiblemodeoftravel=data.get_eligiblemodeoftravel(),
                                                                                      highermodereason=data.get_highermodereason(),
                                                                                      prior_permission=data.get_prior_permission(),
                                                                                      updated_by=user_id, status=1,
                                                                                      updated_date=timezone.now())

                            if 'dependencies' in dtl:
                                for dep_data in dtl['dependencies']:
                                    dep_detail = expreq.Travel_Dep_Request(dep_data)
                                    with transaction.atomic():
                                        previous_claim = ClaimRequest.objects.using(self._current_app_schema()).filter(
                                            entity_id=self._entity_id(),
                                            tour_id=dtl['tourid'], expensegid=dtl['expenseid'])
                                        if dep_detail.id is None:
                                            dependencies = Traveldependent.objects.using(
                                                self._current_app_schema()).create(tour_id=data.get_tour_id(),
                                                                                   claimreq_id=previous_claim[0].id,
                                                                                   travel_id=data.get_id(),
                                                                                   empid=dep_detail.empid,
                                                                                   dependentid=dep_detail.dependentid,
                                                                                   dependentname=dep_detail.dependentname,
                                                                                   deprelation=dep_detail.deprelation,
                                                                                   isdepelig=1,
                                                                                   created_by=user_id,
                                                                                   entity_id=self._entity_id())
                                        else:
                                            dependencies = Traveldependent.objects.using(
                                                self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                   id=dep_detail.id).update(
                                                tour_id=data.get_tour_id(),
                                                claimreq_id=previous_claim[0].id,
                                                travel_id=data.get_id(),
                                                empid=dep_detail.empid,
                                                dependentid=dep_detail.dependentid,
                                                dependentname=dep_detail.dependentname,
                                                deprelation=dep_detail.deprelation,
                                                isdepelig=1,
                                                created_by=user_id)
                            # transaction.on_commit(ClaimRequest)
                            # transaction.on_commit(Travel)
                            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                else:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.NO_DATA)
                    return error_obj

            else:
                data = expreq.Travel_Request(dtl)

                if len(previous_claim) == 0:
                    with transaction.atomic():
                        claimreq = ClaimRequest.objects.using(self._current_app_schema()).create(
                            tour_id=data.get_tour_id(),
                            expensegid=data.get_expensegid(),
                            claimedamount=round(total_claimed_amount, 2),
                            approvedamount=round(total_claimed_amount, 2),
                            requestercomment=data.get_requestercomment(),
                            status=1,
                            created_by=user_id, entity_id=self._entity_id())
                        claim_req_id = claimreq.id
                else:
                    with transaction.atomic():
                        claimreq = ClaimRequest.objects.using(self._current_app_schema()).filter(
                            entity_id=self._entity_id(), id=previous_claim[0].id).update(
                            tour_id=data.get_tour_id(),
                            expensegid=data.get_expensegid(),
                            claimedamount=round(total_claimed_amount, 2),
                            approvedamount=round(total_claimed_amount, 2),
                            requestercomment=data.get_requestercomment(),
                            status=1,
                            created_by=user_id)
                        claim_req_id = previous_claim[0].id
                self.initial_exp_approvedby(data.get_tour_id(), data.get_requestercomment(),user_id)
                with transaction.atomic():
                    travel = Travel.objects.using(self._current_app_schema()).create(tour_id=data.get_tour_id(),
                                                                                     claimreqgid_id=claim_req_id,
                                                                                     traveltype=data.get_traveltype(),
                                                                                     fromdate=data.get_fromdate(),
                                                                                     fromplace=data.get_fromplace(),
                                                                                     todate=data.get_todate(),
                                                                                     toplace=data.get_toplace(),
                                                                                     remarks=data.get_remarks(),
                                                                                     vendorname=data.get_vendorname(),
                                                                                     billno=data.get_billno(),
                                                                                     totaltkttamt=data.get_totaltkttamt(),
                                                                                     approvedamount=data.get_totaltkttamt(),
                                                                                     tktby=data.get_tktby(),
                                                                                     actualmode=data.get_actualmode(),
                                                                                     travelclass=data.get_travelclass(),
                                                                                     eligiblemodeoftravel=data.get_eligiblemodeoftravel(),
                                                                                     highermodereason=data.get_highermodereason(),
                                                                                     prior_permission=data.get_prior_permission(),
                                                                                     status=1,
                                                                                     created_by=user_id,
                                                                                     entity_id=self._entity_id())

                    if 'dependencies' in dtl:
                        for dep_data in dtl['dependencies']:
                            dep_detail = expreq.Travel_Dep_Request(dep_data)
                            with transaction.atomic():
                                dependencies = Traveldependent.objects.using(self._current_app_schema()).create(
                                    tour_id=data.get_tour_id(),
                                    claimreq_id=claim_req_id,
                                    travel_id=travel.id,
                                    empid=dep_detail.empid,
                                    dependentid=dep_detail.dependentid,
                                    dependentname=dep_detail.dependentname,
                                    deprelation=dep_detail.deprelation,
                                    isdepelig=1,
                                    created_by=user_id, entity_id=self._entity_id())

                    # transaction.on_commit(Traveldependent)
                    # transaction.on_commit(ClaimRequest)
                    # transaction.on_commit(Travel)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            # self.update_claimtable_amount(1, tour_id, data.get_requestercomment(), request)

        success_obj.set_status(SuccessStatus.SUCCESS)
        return success_obj

    def get_travel_tour(self, tourid, request):
        # user_id = request.user.id
        # vysfinservice = ApiService(self._scope())
        # emp = vysfinservice.get_emp_id(request, user_id)
        # employee_id = emp['id']
        expense = Travel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), tour_id=tourid,
                                                                          status=1).all()
        resp_list = NWisefinList()
        for exp in expense:
            req_data = expres.Travel_Response()
            # commondropdown=Common_dropdown_Response()
            req_data.set_id(exp.id)
            req_data.set_tour_id(exp.tour_id)

            req_data.set_traveltype(exp.traveltype)
            req_data.set_fromdate(exp.fromdate)
            req_data.set_fromplace(exp.fromplace)
            req_data.set_todate(exp.todate)
            req_data.set_toplace(exp.toplace)
            req_data.set_remarks(exp.remarks)
            req_data.set_billno(exp.billno)
            req_data.set_totaltkttamt(exp.totaltkttamt)
            req_data.set_tktby(exp.tktby)
            req_data.set_approvedamount(exp.approvedamount)
            req_data.set_actualmode(exp.actualmode)
            req_data.set_travelclass(exp.travelclass)
            req_data.set_eligiblemodeoftravel(exp.eligiblemodeoftravel)
            req_data.set_highermodereason(exp.highermodereason)
            req_data.set_prior_permission(exp.prior_permission)

            # req_data.set_claimreqid(exp.claimreqgid_id)
            #
            # req_data.set_arrivaldate(exp.arrivaldate)
            #
            # req_data.set_depaturedate(exp.depaturedate)
            # req_data.set_depatureplace(exp.depatureplace)
            # req_data.set_dependentgid(exp.dependentgid)
            # req_data.set_eligibletravel(exp.eligibletravel)
            # req_data.set_highermodeopted(exp.highermodeopted)
            # req_data.set_highermodereasons(exp.highermodereasons)
            # req_data.set_noofdependents(exp.noofdependents)
            # req_data.set_placeofvisit(exp.placeofvisit)
            # # req_data.set_priorpermission(exp.priorpermission)
            # service=TourExpense(self._scope())
            # # req_data.set_priorpermission(exp.priorpermission)
            # prior_permission=service.yn_name_get(exp.priorpermission)
            # # req_data.set_priorpermission_name(prior_permission)
            # commondropdown.set_name(prior_permission)
            # commondropdown.set_value(exp.priorpermission)
            # req_data.set_priorpermission(commondropdown)
            # # req_data.set_tktbybank(exp.tktbybank)
            # tkt_bybank=service.yn_name_get(exp.tktbybank)
            # # req_data.set_tktbybank_name(tkt_bybank)
            #
            # common_service = Common_drop_down()
            # actual_travel = common_service.common_drop_down_get(exp.actualtravel, Expense_dropdown.travel_travelmode)
            # req_data.set_actualtravel(actual_travel)
            # if exp.actualtravel =="Road":
            #     common_service = Common_drop_down()
            #     classof_travel = common_service.common_drop_down_get(exp.classoftravel,
            #                                                         Expense_dropdown.travel_Road)
            #     req_data.set_classoftravel(classof_travel)
            # if exp.actualtravel =="Train":
            #     common_service = Common_drop_down()
            #     classof_travel = common_service.common_drop_down_get(exp.classoftravel,
            #                                                         Expense_dropdown.travel_Train)
            #     req_data.set_classoftravel(classof_travel)
            # if exp.actualtravel =="Air":
            #     common_service = Common_drop_down()
            #     classof_travel = common_service.common_drop_down_get(exp.classoftravel,
            #                                                          Expense_dropdown.travel_Air)
            #     req_data.set_classoftravel(classof_travel)
            # if exp.actualtravel =="Sea":
            #     common_service = Common_drop_down()
            #     classof_travel = common_service.common_drop_down_get(exp.classoftravel,
            #                                                          Expense_dropdown.travel_Sea)
            #     req_data.set_classoftravel(classof_travel)
            #
            # commondropdown=Common_dropdown_Response()
            # commondropdown.set_name(tkt_bybank)
            # commondropdown.set_value(exp.tktbybank)
            # req_data.set_tktbybank(commondropdown)
            # req_data.set_tktrefno(exp.tktrefno)
            # req_data.set_totaltkttamt(exp.totaltkttamt)
            # req_data.set_claimedamount(exp.claimedamount)
            # req_data.set_eligibleamount(exp.eligibleamount)
            # req_data.set_approvedamount(exp.approvedamount)
            # # req_data.set_hsncode(exp.hsncode)
            # commondropdown_service=Common_drop_down()
            # hsn_data=commondropdown_service.hsn_percentage_get(request,exp.hsncode)
            # if isinstance(hsn_data, NWisefinError):
            #     return hsn_data
            # req_data.set_hsncode(hsn_data)
            # req_data.set_vendorcode(exp.vendorcode)
            # req_data.set_vendorgstno(exp.vendorgstno)
            # req_data.set_bankgstno(exp.bankgstno)
            # req_data.set_vendortype(exp.vendortype)
            # req_data.set_igst(exp.igst)
            # req_data.set_sgst(exp.sgst)
            # req_data.set_cgst(exp.cgst)
            # req_data.set_status(exp.status)
            req_data.set_claimedamount(exp.totaltkttamt)
            req_data.set_vendorname(exp.vendorname)
            req_data.set_exp_name("Travelling Expenses")
            # req_data.set_exp_id(1)
            # dept_service=EmployeemappingData(self._scope())
            # dependencies=dept_service.get_travel_dependencies_id(exp.id,employee_id)
            # req_data.set_dependencies(dependencies.data)
            req_data.set_exp_id(1)
            resp_list.append(req_data)
        claim = ClaimRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                              tour_id=tourid, expensegid=1)
        if len(claim) != 0:
            resp_list.requestercomment = claim[0].requestercomment
            resp_list.approvercomment = claim[0].approvercomment
        return resp_list

    def delete_travel(self,id,request,employee_id):
        try:
            tourid = Travel.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=id).tour_id
            service = Validation(self._scope())
            permission = service.tour_maker_check(tourid, employee_id)
            if permission is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.VALID_USER)
                return error_obj
            delete = Travel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=id).update(status=Status.DELETED)
            msg_obj = NWisefinSuccess()
            msg_obj.set_status(SuccessMessage.DELETE_MESSAGE)
            msg_obj.set_message({"id": id})
            self.update_claimtable_amount(1, tourid, None, request)
            return msg_obj

        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj

    def exp_summary(self,employee_id,onb,vys_page,request_date,tour_no,request,status):
        cancel_check = [Status.DEFAULT, Status.REJECTED]
        if request_date != "":
            try:
                request_date = int(request_date)
                request_date = str(datetime.fromtimestamp(int(request_date) / 1000.0))
                request_date = (datetime.strptime(request_date[:10], '%Y-%m-%d')).date()
            except:
                request_date = (datetime.strptime(request_date, '%d-%b-%Y')).date()

        if status is not None:
            status=[status]
        else:
            status = [-1,1,2,3,4,5]



        if onb is None:
            Tour = TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour__empgid=employee_id,applevel=App_level.THIRD_LEVEL,
                                                                                  tour__tour_status=Status.APPROVED,tour__claim_status__in=status,request_type=(App_type.TOUR or App_type.tour),
                                                                                  tour__request_date__icontains=request_date,tour__id__icontains=tour_no,status=3,
                                                                                  tour__tour_cancel_status__in=cancel_check).all().order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]

        elif int(onb)==0:
            Tour = TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), tour__onbehalfof=employee_id, applevel=App_level.THIRD_LEVEL,
                                                                                  tour__tour_status=Status.APPROVED,tour__claim_status__in=status,status=3,
                                                                                  request_type=(App_type.TOUR or App_type.tour), tour__request_date__icontains=request_date, tour__id__icontains=tour_no,
                                                                                  tour__tour_cancel_status__in=cancel_check).all().order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]
        elif int(onb) > 0:
            Tour = TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), tour__empgid=onb, tour__onbehalfof=employee_id, tour__tour_status=Status.APPROVED,
                                                                                  tour__claim_status__in=status, applevel=App_level.THIRD_LEVEL,status=3,
                                                                                  request_type=(App_type.TOUR or App_type.tour), tour__request_date__icontains=request_date, tour__id__icontains=tour_no,
                                                                                  tour__tour_cancel_status__in=cancel_check).all().order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]
            # Tour = TourRequest.objects.using(self._current_app_schema()).filter(empgid=onb, onbehalfof=employee_id,tour_status=Status.APPROVED).all()

            # Tour = TourRequest.objects.using(self._current_app_schema()).filter(empgid=employee_id,tour_status=Status.APPROVED).all()
        resp_list = NWisefinList()
        if len(Tour)>0:
            for data in Tour:
                tour=data.tour
                req_data = TourMakerResponse()
                req_data.set_id(tour.id)
                # req_data.set_requestno(tour.requestno)
                req_data.set_requestdate(tour.request_date)
                req_data.set_startdate(tour.start_date)
                req_data.set_enddate(tour.end_date)
                req_data.set_empgid(tour.empgid)
                empdtl = ApiService(self._scope())
                employee = empdtl.employee_details_get(tour.empgid,request)
                req_data.set_employee_name(employee.full_name)
                approve=data.approvedby
                claim_approver=TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=tour.id,applevel__gte=1,request_type=App_type.CLAIM).last()

                if claim_approver is not None:
                    if claim_approver.approvedby==-1:
                        req_data.set_approvedby("ADMIN")
                        req_data.set_approver_code("ADMIN")
                        req_data.set_approvedby_id(data.approvedby)
                    else:
                        approvedby = empdtl.employee_details_get(claim_approver.approvedby,request)
                        req_data.set_approvedby(approvedby.full_name)
                        req_data.set_approver_code(approvedby.code)
                        req_data.set_approvedby_id(claim_approver.approvedby)

                    onb_approver_id = claim_approver.onbehalfof_approval
                    onb_approver = empdtl.employee_details_get(onb_approver_id, request)
                    req_data.set_onb_approvedby(onb_approver_id)
                    req_data.set_onb_approver_code(onb_approver.code)
                    req_data.set_onb_approver_name(onb_approver.full_name)

                else:
                    req_data.set_approvedby(None)
                    req_data.set_approver_code(None)
                    req_data.set_approvedby_id(None)

                    req_data.set_onb_approvedby(None)
                    req_data.set_onb_approver_code(None)
                    req_data.set_onb_approver_name(None)



                # code = empdtl.employee_code_get(tour.empgid)
                req_data.set_employee_code(employee.code)
                req_data.set_empdesignation(tour.empdesignation)
                req_data.set_empgrade(tour.empgrade)
                req_data.set_empbranchgid(tour.empbranchgid)
                branch = empdtl.get_branch_data(tour.empbranchgid,request)
                req_data.set_branch_name(branch.name)
                req_data.set_branch_code(branch.code)
                req_data.set_reason_id(tour.reason)
                detail = emp_dtl(self._scope())
                reason = detail.get_reason_name(tour.reason)
                req_data.set_reason(reason)
                if tour.onbehalfof > 0:
                    onbehalf = empdtl.employee_details_get(tour.onbehalfof,request)
                    req_data.set_onbehalfof(onbehalf.full_name)
                tour_status = status_get(tour.tour_status)
                # advance_status = status_get(tour.advance_status)
                claim_status = status_get(tour.claim_status)
                req_data.set_tour_status(tour_status)
                # req_data.set_advance_status(advance_status)
                req_data.set_claim_status(claim_status)
                req_data.set_tour_status_id(tour.tour_status)
                # req_data.set_advance_status_id(tour.advance_status)
                req_data.set_claim_status_id(tour.claim_status)
                max_lvl=TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), tour_id=tour.id, request_type=App_type.CLAIM).last()
                if max_lvl is None:
                    req_data.set_max_applevel(0)
                else:
                    req_data.set_max_applevel(max_lvl.applevel)
                date_relaxation=1
                date_relaxation_status=Date_relaxation.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=tour.id).last()
                if date_relaxation_status is not None:
                    date_relaxation=date_relaxation_status.status
                req_data.set_date_relaxation(date_relaxation)

                req_data.set_air_status(tour.air_status)
                req_data.set_train_status(tour.train_status)
                req_data.set_bus_status(tour.bus_status)
                req_data.set_cab_status(tour.cab_status)
                req_data.set_accomodation_status(tour.accomodation_status)
                diffdays = (time_function.ist_date() - tour.start_date.date()).days
                if diffdays == 0:
                    req_data.set_is_tour_started(True)
                else:
                    req_data.set_is_tour_started(bool(max(0, diffdays)))

                resp_list.append(req_data)
            vpage = NWisefinPaginator(Tour, vys_page.get_index(), 10)
            resp_list.set_pagination(vpage)
        return resp_list


    def approved_tour_cancel_summary(self,employee_id,onb,vys_page,request_date,tour_no,request):
        if request_date != "":
            try:
                request_date = int(request_date)
                request_date = str(datetime.fromtimestamp(int(request_date) / 1000.0))
                request_date = (datetime.strptime(request_date[:10], '%Y-%m-%d')).date()
            except:
                request_date = (datetime.strptime(request_date, '%d-%b-%Y')).date()

        if onb is None:

            Tour = TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), tour__empgid=employee_id,  tour__tour_status=Status.APPROVED, applevel=App_level.FIRST_LEVEL,
                                                                                  request_type=(App_type.TOUR or App_type.tour), status=Status.APPROVED, tour__request_date__icontains=request_date, tour__id__icontains=tour_no,
                                                                                  tour__tour_cancel_status=Status.DEFAULT, tour__claim_status=Status.DEFAULT
                                                                                  , tour__end_date__gte=datetime.now().date()-timedelta(days=30)
                                                                                  ).order_by('-id')
        elif int(onb) == 0:
            Tour = TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),  tour__onbehalfof=employee_id, tour__tour_status=Status.APPROVED, applevel=App_level.FIRST_LEVEL,
                                                                                  request_type=(App_type.TOUR or App_type.tour), status=Status.APPROVED, tour__request_date__icontains=request_date, tour__id__icontains=tour_no,
                                                                                  tour__tour_cancel_status=Status.DEFAULT, tour__claim_status=Status.DEFAULT
                                                                                  , tour__end_date__gte=datetime.now().date()-timedelta(days=30)
                                                                                  ).order_by('-id')
        else:
            Tour = TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), tour__empgid=onb,tour__onbehalfof=employee_id, applevel=App_level.FIRST_LEVEL,
                                                                                  tour__tour_status=Status.APPROVED,
                                                                                  request_type=(App_type.TOUR or App_type.tour), status=Status.APPROVED, tour__request_date__icontains=request_date, tour__id__icontains=tour_no,
                                                                                  tour__tour_cancel_status=Status.DEFAULT, tour__claim_status=Status.DEFAULT
                                                                                  , tour__end_date__gte=datetime.now().date()-timedelta(days=30)
                                                                                  ).all().order_by('-id')

        # unique_tour = []
        approvedby_id = []
        for data in Tour:
            if len(approvedby_id) <= vys_page.get_query_limit():
                # advance_approved=TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), request_type=App_type.ADVANCE, status=Status.APPROVED, tour_id=data.tour_id)
                # if len(advance_approved)==0:
                    # unique_tour.append(data.tour_id)
                    approvedby_id.append(data.id)
        Tour = TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), id__in=approvedby_id).all().order_by('-id')[
               vys_page.get_offset():vys_page.get_query_limit()]

        resp_list = NWisefinList()
        if len(Tour)>0:
            for data in Tour:
                tour=data.tour
                req_data = TourMakerResponse()
                req_data.set_id(tour.id)
                # req_data.set_requestno(tour.requestno)
                req_data.set_requestdate(tour.request_date)
                req_data.set_startdate(tour.start_date)
                req_data.set_enddate(tour.end_date)
                req_data.set_empgid(tour.empgid)
                empdtl = ApiService(self._scope())
                employee = empdtl.employee_details_get(tour.empgid,request)
                req_data.set_employee_name(employee.full_name)
                approve=data.approvedby
                if approve is not None:
                    approvedby = empdtl.employee_details_get(data.approvedby,request)
                    req_data.set_approvedby(approvedby.full_name)
                    req_data.set_approvedby_id(data.approvedby)
                # code = empdtl.employee_code_get(tour.empgid)
                req_data.set_employee_code(employee.code)
                req_data.set_empdesignation(tour.empdesignation)
                req_data.set_empgrade(tour.empgrade)
                req_data.set_empbranchgid(tour.empbranchgid)
                branch = empdtl.get_branch_data(tour.empbranchgid,request)
                req_data.set_branch_name(branch.name)
                req_data.set_branch_code(branch.code)
                req_data.set_reason_id(tour.reason)
                detail = emp_dtl(self._scope())
                reason = detail.get_reason_name(tour.reason)
                req_data.set_reason(reason)
                if tour.onbehalfof > 0:
                    onbehalf = empdtl.employee_details_get(tour.onbehalfof,request)
                    req_data.set_onbehalfof(onbehalf.full_name)
                tour_status = status_get(tour.tour_status)
                # advance_status = status_get(tour.advance_status)
                claim_status = status_get(tour.claim_status)
                req_data.set_tour_status(tour_status)
                # req_data.set_advance_status(advance_status)
                req_data.set_claim_status(claim_status)
                req_data.set_tour_status_id(tour.tour_status)
                # req_data.set_advance_status_id(tour.advance_status)
                req_data.set_claim_status_id(tour.claim_status)
                tour_approver_data=TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), request_type=App_type.TOUR, status=Status.APPROVED, applevel=App_level.FIRST_LEVEL, tour_id=tour.id).last()
                if tour_approver_data is not None:
                    tour_approvedby = empdtl.employee_details_get(tour_approver_data.approvedby, request)
                    req_data.set_tour_approvedby(tour_approvedby)
                resp_list.append(req_data)
            vpage = NWisefinPaginator(Tour, vys_page.get_index(), 10)
            resp_list.set_pagination(vpage)
        return resp_list


    def yn_name_get(self,no):
        if no==1:
            return "yes"
        elif no ==0:
            return "no"
        else:
            return no

    def two_wheeler_trans(self,no):
        if no==1:
            return "Railway"
        elif no ==0:
            return "Transport"
        else:
            return no

    def onward_return(self,no):
        if no==1:
            return "Onward"
        elif no ==0:
            return "Return"
        else:
            return no


    def delete_expense(self,tour_id,type):
        delete = ClaimRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=tour_id, expensegid=type).update(status=Status.DELETED)
        if type==1:
            delete = Travel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=tour_id).update(status=Status.DELETED)
            msg_obj = NWisefinSuccess()
            msg_obj.set_status(SuccessMessage.DELETE_MESSAGE)
            msg_obj.set_message({"tour_id": tour_id})
            return msg_obj
        elif type==2:
            delete = Dailydeim.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=tour_id).update(status=Status.DELETED)
            msg_obj = NWisefinSuccess()
            msg_obj.set_status(SuccessMessage.DELETE_MESSAGE)
            msg_obj.set_message({"tour_id": tour_id})
            return msg_obj
        elif type==3:
            delete = Incidental.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=tour_id).update(status=Status.DELETED)
            msg_obj = NWisefinSuccess()
            msg_obj.set_status(SuccessMessage.DELETE_MESSAGE)
            msg_obj.set_message({"tour_id": tour_id})
            return msg_obj
        elif type==4:
            delete = Localconveyence.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=tour_id).update(status=Status.DELETED)
            msg_obj = NWisefinSuccess()
            msg_obj.set_status(SuccessMessage.DELETE_MESSAGE)
            msg_obj.set_message({"tour_id": tour_id})
            return msg_obj
        elif type==5:
            delete = Lodging.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=tour_id).update(status=Status.DELETED)
            msg_obj = NWisefinSuccess()
            msg_obj.set_status(SuccessMessage.DELETE_MESSAGE)
            msg_obj.set_message({"tour_id": tour_id})
            return msg_obj
        elif type==6:
            delete = Misc.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=tour_id).update(status=Status.DELETED)
            msg_obj = NWisefinSuccess()
            msg_obj.set_status(SuccessMessage.DELETE_MESSAGE)
            msg_obj.set_message({"tour_id": tour_id})
            return msg_obj
        elif type==7:
            delete = PackingMoving.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=tour_id).update(status=Status.DELETED)
            msg_obj = NWisefinSuccess()
            msg_obj.set_status(SuccessMessage.DELETE_MESSAGE)
            msg_obj.set_message({"tour_id": tour_id})
            return msg_obj
        elif type==8:
            delete = Localdeputation.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=tour_id).update(status=Status.DELETED)
            msg_obj = NWisefinSuccess()
            msg_obj.set_status(SuccessMessage.DELETE_MESSAGE)
            msg_obj.set_message({"tour_id": tour_id})
            return msg_obj
        elif type==9:
            delete = associate.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=tour_id).update(status=Status.DELETED)
            msg_obj = NWisefinSuccess()
            msg_obj.set_status(SuccessMessage.DELETE_MESSAGE)
            msg_obj.set_message({"tour_id": tour_id})
            return msg_obj


    # def search_hsn(self, query, vys_page):
    #     if query is None:
    #         hsnlist = Hsn.objects.using(self._current_app_schema()).all().order_by('created_date')[
    #                   vys_page.get_offset():vys_page.get_query_limit()]
    #     else:
    #         hsnlist = Hsn.objects.using(self._current_app_schema()).filter(code__icontains=query).order_by('created_date')[
    #                   vys_page.get_offset():vys_page.get_query_limit()]
    #     hsn_list_data = NWisefinList()
    #     for hsn in hsnlist:
    #         hsn_res = HsnResponse()
    #         hsn_res.set_id(hsn.id)
    #         hsn_res.set_code(hsn.code)
    #         # hsn_res.set_description(hsn.description)
    #         # hsn_res.set_cgstrate(hsn.cgstrate)
    #         # hsn_res.set_sgstrate(hsn.sgstrate)
    #         # hsn_res.set_igstrate(hsn.igstrate)
    #         # hsn_res.set_cgstrate_id(hsn.cgstrate_id)
    #         # hsn_res.set_sgstrate_id(hsn.sgstrate_id)
    #         # hsn_res.set_igstrate_id(hsn.igstrate_id)
    #         hsn_list_data.append(hsn_res)
    #         vpage = NWisefinPaginator(hsnlist, vys_page.get_index(), 10)
    #         hsn_list_data.set_pagination(vpage)
    #     return hsn_list_data
    #
    # def bank_gst_get(self,gst,vys_page):
    #     resp_list = NWisefinList()
    #     gst_list = EmployeeBranch.objects.filter(Q(name__icontains=gst)|Q(gstin__icontains=gst)).all() [vys_page.get_offset():vys_page.get_query_limit()]
    #     for data in gst_list:
    #         req_data=Travel_Response()
    #         req_data.set_bankgstno(data.gstin)
    #         req_data.set_bank_name(data.name)
    #
    #         resp_list.append(req_data)
    #     vpage = NWisefinPaginator(gst_list, vys_page.get_index(), 10)
    #     resp_list.set_pagination(vpage)
    #
    #     return resp_list


    # def lodging_taxccbs_ser(self,userdata,user_id):
    #     Validation_ser=Validation()
    #
    #     approved_by=ApprovedBy.objects.using(self._current_app_schema()).filter(tour_id=userdata['tour_id'],applevel=App_level.SECOND_LEVEL,apptype=App_type.CLAIM).last()
    #
    #
    #     if approved_by is None:
    #         error_obj = NWisefinError()
    #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #         error_obj.set_description(ErrorDescription.INVALID)
    #         return error_obj
    #     approved_status = approved_by.status
    #     approver_id =approved_by.approvedby
    #
    #
    #     if approver_id !=user_id:
    #         error_obj = NWisefinError()
    #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #         error_obj.set_description(ErrorDescription.INVALID)
    #         return error_obj
    #     if approved_status != Status.PENDING:
    #         error_obj = NWisefinError()
    #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #         error_obj.set_description(ErrorDescription.INVALID)
    #         return error_obj
    #
    #     ccbs_data=Ccbs.objects.using(self._current_app_schema()).filter(tour_id=userdata['tour_id'],status=1)
    #     lodging_data=Lodging.objects.using(self._current_app_schema()).filter(tour_id=userdata['tour_id'],status=1)
    #     lod_data=0
    #     for lodging in lodging_data:
    #         lod_data+=lodging.taxonly
    #
    #     for ccbs in ccbs_data:
    #         ccbs_percentage=(lod_data*ccbs.percentage)/100+ccbs.amount
    #         ccbs_update=Ccbs.objects.using(self._current_app_schema()).filter(id=ccbs.id).update(amount=ccbs_percentage,updated_by=user_id,updated_date=today)
    #
    #     success_obj = NWisefinSuccess()
    #     success_obj.set_status(SuccessStatus.SUCCESS)
    #     success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
    #     return success_obj

    @transaction.atomic
    def create_associate(self, request_obj, user_id, request):
        logger.info('ta_ associate_create- ' + str(user_id) + str(request_obj))
        success_obj = NWisefinSuccess()
        total_claimed_amount = 0
        total_approved_amount = 0
        tour_id = request_obj['data'][0]['tour_id']
        tour_data = TourRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                 id=request_obj['data'][0]['tour_id'])[0]

        # if tour_data.reason == 11:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.ONLY_LOCAL_CONV)
        #     return error_obj

        validation_check = self.expense_validations(request_obj, user_id)
        if validation_check == True:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description("Please Check The Date")
            return error_obj
        else:
            pass

        tour_empid = tour_data.empgid
        if user_id != tour_empid:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.VALID_USER)
            return error_obj

        # status = validations.exp_claim_status(tour_id)
        # if status is False:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.CLAIM_STATUS)
        #     return error_obj

        set_delete = True
        if 'mobile' in request_obj['data'][0]:
            if int(request_obj['data'][0]['mobile']) == 1:
                set_delete = False
        if set_delete == True:
            A = associate.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                    tour_id=tour_id).update(status=0)

        for dtl in request_obj['data']:
            total_approved_amount = total_approved_amount + float(dtl['claimedamount'])
            total_claimed_amount = total_claimed_amount + float(dtl['claimedamount'])

            # try:
            #     int(dtl['startdate'])
            #     millisecond = True
            # except:
            #     millisecond = False
            #
            # if millisecond is True:
            #     dtl['fromdate'] = str(datetime.fromtimestamp(int(dtl['fromdate']) / 1000.0))
            #     dtl['todate'] = str(datetime.fromtimestamp(int(dtl['todate']) / 1000.0))

            previous_claim = ClaimRequest.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id(), tour_id=dtl['tour_id'], expensegid=dtl['expensegid'])
            tour_id = dtl['tour_id']

            if 'id' in dtl:
                maker = tamaker(self._scope())
                edit_check = maker.edit_validations(tour_id, App_type.CLAIM)
                if edit_check is False:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.CANT_EDIT_THIS_TOUR)
                    return error_obj
                if len(previous_claim) != 0:
                    data = expreq.associate_Request(dtl)
                    with transaction.atomic():
                        claimreq = ClaimRequest.objects.using(self._current_app_schema()).filter(
                            entity_id=self._entity_id(), id=previous_claim[0].id).update(
                            claimedamount=round(total_claimed_amount, 2),
                            approvedamount=round(total_claimed_amount, 2),
                            requestercomment=data.get_requestercomment(),
                            updated_by=user_id, status=1)
                        with transaction.atomic():
                            associate_exp = associate.objects.using(self._current_app_schema()).filter(
                                entity_id=self._entity_id(), id=data.get_id()).update(
                                description=data.get_description(),
                                expense=data.get_expense(),
                                fromdate=data.get_fromdate(),
                                todate=data.get_todate(),
                                remarks=data.get_remarks(),
                                billno=data.get_billno(),
                                claimedamount=round(
                                    data.get_claimedamount(), 2),
                                approvedamount=round(
                                    data.get_claimedamount(), 2),
                                updated_by=user_id, status=1, updated_date=timezone.now())
                            # transaction.on_commit(ClaimRequest)
                            # transaction.on_commit(associate_exp)
                            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                else:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.NO_DATA)
                    return error_obj

            else:

                data = expreq.associate_Request(dtl)

                if len(previous_claim) == 0:
                    with transaction.atomic():
                        claimreq = ClaimRequest.objects.using(self._current_app_schema()).create(
                            tour_id=data.get_tour_id(),
                            expensegid=data.get_expensegid(),
                            claimedamount=round(total_claimed_amount, 2),
                            approvedamount=round(total_claimed_amount, 2),
                            requestercomment=data.get_requestercomment(),
                            status=1,
                            created_by=user_id, entity_id=self._entity_id())
                        claim_req_id = claimreq.id
                else:
                    with transaction.atomic():
                        claimreq = ClaimRequest.objects.using(self._current_app_schema()).filter(
                            entity_id=self._entity_id(), id=previous_claim[0].id).update(tour_id=data.get_tour_id(),
                                                                                         expensegid=data.get_expensegid(),
                                                                                         claimedamount=round(
                                                                                             total_claimed_amount, 2),
                                                                                         approvedamount=round(
                                                                                             total_claimed_amount, 2),
                                                                                         requestercomment=data.get_requestercomment(),
                                                                                         status=1,
                                                                                         created_by=user_id)
                        claim_req_id = previous_claim[0].id
                self.initial_exp_approvedby(data.get_tour_id(), data.get_requestercomment(),user_id)
                with transaction.atomic():

                    associate_exp = associate.objects.using(self._current_app_schema()).create(
                        tour_id=data.get_tour_id(),
                        claimreq_id=claim_req_id,
                        description=data.get_description(),
                        expense=data.get_expense(),
                        fromdate=data.get_fromdate(),
                        todate=data.get_todate(),
                        remarks=data.get_remarks(),
                        billno=data.get_billno(),
                        claimedamount=round(data.get_claimedamount(), 2),
                        approvedamount=round(
                            data.get_claimedamount(), 2),
                        status=1,
                        created_by=user_id,
                        entity_id=self._entity_id())

                    # transaction.on_commit(ClaimRequest)
                    # transaction.on_commit(associate_exp)
                    success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            # self.update_claimtable_amount(6, tour_id, data.get_requestercomment(), request)

        success_obj.set_status(SuccessStatus.SUCCESS)
        return success_obj

    def get_associate_tour(self, tourid, request):
        user_id = request.user.id
        vysfinservice = ApiService(self._scope())
        emp = vysfinservice.get_emp_id(request, user_id)
        employee_id = emp['id']
        expense = associate.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), tour_id=tourid,
                                                                          status=1).all()
        resp_list = NWisefinList()
        for exp in expense:
            req_data = expres.associate_Response()
            req_data.set_id(exp.id)
            req_data.set_tour_id(exp.tour_id)
            req_data.set_exp_id(9)
            req_data.set_exp_name("Associated Expenses")
            req_data.set_description(exp.description)
            req_data.set_expense(exp.expense)
            req_data.set_fromdate(exp.fromdate)
            req_data.set_todate(exp.todate)
            req_data.set_remarks(exp.remarks)
            req_data.set_billno(exp.billno)
            req_data.set_claimedamount(exp.claimedamount)
            req_data.set_approvedamount(exp.approvedamount)
            resp_list.append(req_data)
        claim = ClaimRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                              tour_id=tourid, expensegid=1)
        if len(claim) != 0:
            resp_list.requestercomment = claim[0].requestercomment
            resp_list.approvercomment = claim[0].approvercomment
        return resp_list

    def delete_associate(self, id, request, employee_id):
        try:
            tourid = associate.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(), id=id).tour_id
            service = Validation(self._scope())
            permission = service.tour_maker_check(tourid, employee_id)
            if permission is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.VALID_USER)
                return error_obj
            delete = associate.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), id=id).update(
                status=Status.DELETED)
            msg_obj = NWisefinSuccess()
            msg_obj.set_status(SuccessMessage.DELETE_MESSAGE)
            msg_obj.set_message({"id": id})
            self.update_claimtable_amount(9, tourid, None, request)
            return msg_obj

        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj

# ------------------- 6/1/2022 inserted line  for rollback (for atomic transaction)-------------------------------------------------------------
    def daily_deim_validations(self,request_obj,request,user_id):
        total_claimed_amount = 0
        total_approved_amount = 0
        validations =Validation(self._scope())
        tourid = request_obj['data'][0]['tour_id']
        tour_data = TourRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=tourid)[0]
        tour_start_date = tour_data.start_date.date()
        tour_end_date = tour_data.end_date.date()
        scope = request.scope
        Tour_service = Tour_grade(scope)
        for dtl in request_obj['data']:
            tour_id = dtl['tour_id']
            data = expreq.Dailydeim_Request(dtl)
            # city_dropdown = self.dail_city_dropdown(tour_id, data.get_city(), EXPENSE_ID.DailyDiem)
            # if city_dropdown is False:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.DROPDOWN)
            #     return error_obj

            # approved_amount = Tour_service.dailydiem_eligible_amount(dtl,request)
            # dtl['syshours'] = json.loads(approved_amount)["sys_hours"]



            fromdate = datetime.strptime((dtl['fromdate'][:10]), '%Y-%m-%d').date()
            todate = datetime.strptime((dtl['todate'][:10]), '%Y-%m-%d').date()

            if tour_start_date > fromdate or tour_end_date < fromdate or tour_start_date > todate or tour_end_date < todate:
                return True
            else:
                return False
            # data = expreq.Dailydeim_Request(dtl)
            # date_check = validations.start_end_date_time(data.get_fromdate(), data.get_todate())
            # noof_leavedays = validations.negative_amount(data.get_isleave())
            # noof_hours = validations.negative_amount(data.get_noofhours())
            # claim_amount = validations.claim_negative_check(dtl['claimedamount'])
            #
            #
            # if (data.get_syshours()) < float(data.get_noofhours()):
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            #
            # isleave_cal= ((todate -fromdate).days)+1
            # if int(isleave_cal) < int(data.get_isleave()):
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # acc_bybank= self.expense_dropdown_validations(Expense_dropdown.yesno,data.get_accbybank())
            # boarding_bybank = self.expense_dropdown_validations(Expense_dropdown.yesno, data.get_boardingbybank())
            # declaration = self.expense_dropdown_validations(Expense_dropdown.yesno, data.get_declaration())
            #
            # if date_check is False:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.START_END_DATE)
            #     return error_obj
            # if noof_leavedays is False:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # if noof_hours is False:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # if claim_amount is False:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.AMOUNT)
            #     return error_obj
            # if (acc_bybank and boarding_bybank and declaration) is False:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.DROPDOWN)
            #     return error_obj
            # if (data.get_accbybank()=="1" or data.get_accbybank()==1) and (data.get_boardingbybank()=="1" or data.get_boardingbybank()==1):
            #     if (data.get_declaration() != "0" and data.get_declaration() !=None and data.get_declaration() !=0):
            #         error_obj = NWisefinError()
            #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #         error_obj.set_description(ErrorDescription.DROPDOWN)
            #         return error_obj
            #
            # permission_check = validations.permisssion_check(tour_id, user_id)
            # status = validations.exp_claim_status(tour_id)
            # if permission_check is False:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.INVALID)
            #     return error_obj
            # startdate_check = validations.tour_startdate_check(tour_id)
            # if startdate_check is False:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.INVALID)
            #     return error_obj
            # tour_status = validations.tour_status(tour_id)
            # if tour_status is False:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.TOUR_STATUS)
            #     return error_obj
            # if status is False:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.CLAIM_STATUS)
            #     return error_obj

    def travel_validations(self,request_obj,user_id):

        validations = Validation(self._scope())

        tourid = request_obj['data'][0]['tour_id']
        tour_data = TourRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=tourid)[0]
        tour_start_date = tour_data.start_date.date()
        tour_end_date = tour_data.end_date.date()
        for dtl in request_obj['data']:
            tour_id=dtl["tour_id"]
            data = expreq.Travel_Request(dtl)

            arrival_date = datetime.strptime((data.get_arrivaldate()[:10]), '%Y-%m-%d').date()
            depature_date = datetime.strptime((data.get_depaturedate()[:10]), '%Y-%m-%d').date()

            date_check = validations.start_end_date(data.get_depaturedate(), data.get_arrivaldate())
            amount_check = validations.claim_negative_check(data.get_totaltkttamt())
            claim_amt = validations.claim_negative_check(dtl['claimedamount'])

            mode_of_travel=self.expense_dropdown_validations(Expense_dropdown.travel_travelmode,data.get_actualtravel())
            if mode_of_travel is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.DROPDOWN)
                return error_obj

            class_oftrave=self.expense_travelmode_dropdown(data.get_actualtravel())
            class_oftravel=self.expense_dropdown_validations(class_oftrave,data.get_classoftravel())
            tktbybank=self.expense_dropdown_validations(Expense_dropdown.yesno,data.get_tktbybank())
            highermodereasons=self.expense_dropdown_validations(Expense_dropdown.yesno,data.get_highermodereasons())
            priorpermission=self.expense_dropdown_validations(Expense_dropdown.yesno,data.get_priorpermission())


            if (class_oftravel and tktbybank and highermodereasons and priorpermission) is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.DROPDOWN)
                return error_obj
            if data.get_tktbybank() == 1 or data.get_tktbybank() == str(1):
                if data.get_tktrefno() == 0 or data.get_tktrefno() == None or data.get_tktrefno() == "0":
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj
            elif data.get_tktbybank() == 0 or data.get_tktbybank() == str(0):
                if (data.get_tktrefno() != 0 and data.get_tktrefno() != None and data.get_tktrefno() != "0"):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj
            if data.get_priorpermission() == 1 or data.get_priorpermission() == str(1):
                if  data.get_highermodeopted() == 0 or  data.get_highermodeopted() == None or  data.get_highermodeopted() == "0":
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj
            elif data.get_priorpermission() == 0 or data.get_priorpermission() == str(0):
                if  (data.get_highermodeopted() != 0 and  data.get_highermodeopted() != None and  data.get_highermodeopted() != "0"):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj
            if data.get_placeofvisit() == "" or data.get_placeofvisit() == None or data.get_depatureplace() =="" or data.get_depatureplace()==None:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.DATA_ERROR)
                return error_obj

            if date_check is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.START_END_DATE)
                return error_obj
            if amount_check is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.AMOUNT)
                return error_obj
            if claim_amt is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.AMOUNT)
                return error_obj
            if data.get_noofdependents() == None:
                pass
            else:
                noof_ticket = validations.negative_amount(data.get_noofdependents())
                if noof_ticket is False:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj
            if tour_start_date > arrival_date or tour_end_date < arrival_date or tour_start_date > depature_date or tour_end_date < depature_date:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description("Please check the date")
                return error_obj
            expense_id = self.expense_id_validation(data.get_expenseid())
            if expense_id is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.AMOUNT)
                return error_obj
            if 'dependencies' in dtl:
                if len(dtl['dependencies']) != int(data.get_noofdependents()):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.DEPENDENCIES_COUNT)
                    return error_obj
            permission_check = validations.permisssion_check(tour_id, user_id)
            if permission_check is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID)
                return error_obj
            startdate_check = validations.tour_startdate_check(tour_id)
            if startdate_check is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID)
                return error_obj
            tour_status = validations.tour_status(tour_id)
            if tour_status is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.TOUR_STATUS)
                return error_obj

            status = validations.exp_claim_status(tour_id)
            if status is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.CLAIM_STATUS)
                return error_obj




    def incidental_validations(self,request_obj,user_id):

        validations = Validation(self._scope())
        # try:
        # tour_data = TourRequest.objects.using(self._current_app_schema()).filter(id=request_obj['data'][0]['tourid'])[0]
        for dtl in request_obj['data']:
            tour_id=dtl["tourid"]
            service=Tour_allowance(self._scope())
            req_obj = Allowancerequest(dtl)
            data = expreq.Incidental_Request(dtl)
            travel_hours = validations.claim_negative_check(data.get_travelhours())
            fareamount_check = validations.claim_negative_check(data.get_singlefare())

            mode_of_travel=self.expense_dropdown_validations(Expense_dropdown.incidental_travelmode,data.get_travel_mode())
            onward_return=self.expense_dropdown_validations(Expense_dropdown.yesno,data.get_samedayreturn())
            if (mode_of_travel and onward_return) is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.DROPDOWN)
                return error_obj
            if data.get_samedayreturn() == 1 or data.get_samedayreturn() =="1":
                if int(data.get_travelhours()) > 24:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.DROPDOWN)
                    return error_obj
            if data.get_samedayreturn() == 0 or data.get_samedayreturn() =="0":
                if int(data.get_travelhours()) < 24:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.DROPDOWN)
                    return error_obj



            if travel_hours is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            if fareamount_check is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.AMOUNT)
                return error_obj
            expense_id=self.expense_id_validation(data.get_expenseid())
            if expense_id is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.AMOUNT)
                return error_obj
            permission_check = validations.permisssion_check(tour_id, user_id)
            status = validations.exp_claim_status(tour_id)

            if permission_check is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID)
                return error_obj
            startdate_check = validations.tour_startdate_check(tour_id)
            if startdate_check is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID)
                return error_obj
            tour_status = validations.tour_status(tour_id)
            if tour_status is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.TOUR_STATUS)
                return error_obj
            if status is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.CLAIM_STATUS)
                return error_obj


    def lodging_validations(self,request_obj,user_id):
        validations = Validation(self._scope())
        tourid = request_obj['data'][0]['tour_id']
        tour_data = TourRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=tourid)[0]
        tour_start_date = tour_data.start_date.date()
        tour_end_date = tour_data.end_date.date()
        for dtl in request_obj['data']:
            tour_id=dtl["tourgid"]

            ckin_date = datetime.strptime((dtl['fromdate'][:10]), '%Y-%m-%d').date()
            ckout_date = datetime.strptime((dtl['todate'][:10]), '%Y-%m-%d').date()
            lo_out_date = datetime.strptime((dtl['lodgcheckoutdate'][:10]), '%Y-%m-%d').date()
            duration_days = ((lo_out_date - ckin_date).days) + 1

            if tour_start_date > ckin_date or tour_end_date < ckin_date or tour_start_date > ckout_date or tour_end_date < ckout_date \
                    or tour_start_date > lo_out_date or tour_end_date < lo_out_date:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description("Please check the date")
                return error_obj
            data = expreq.Lodging_Request(dtl)
            datetime_check = validations.start_end_date_time(data.get_checkindate(), data.get_checkoutdate())
            amount_check = validations.claim_negative_check(dtl['claimedamount'])
            tax_amount=validations.negative_amount(data.get_taxonly())
            city_dropdown=self.dail_city_dropdown(data.get_tourid(),data.get_city(),EXPENSE_ID.Lodging)
            if city_dropdown is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj

            centre_classfication =self.expense_dropdown_validations(Expense_dropdown.lodging_center,data.get_centreclassification())
            acc_bybank =self.expense_dropdown_validations(Expense_dropdown.yesno,data.get_accbybank())
            bill_available =self.expense_dropdown_validations(Expense_dropdown.yesno,data.get_billavailable())

            if (int(duration_days) < int(data.get_noofdays())):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj

            noof_days = validations.claim_negative_check(data.get_noofdays())
            if (datetime_check and  amount_check and noof_days and centre_classfication and acc_bybank and bill_available and tax_amount) is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            if  data.get_accbybank() == 1 or data.get_accbybank() == str(1):
                if data.get_acrefno() == 0 or data.get_acrefno() == None or data.get_acrefno() == "0":
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj
            if data.get_billavailable() == 1 or data.get_billavailable() == str(1):
                if data.get_billnumber() == 0 or data.get_billnumber()==None or  data.get_billnumber() == "0":
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj
            # if data.get_twowheelertrans() == 0 or data.get_twowheelertrans() == None or data.get_twowheelertrans() =="0":
            #     if (data.get_transtwowheelerby() == None or data.get_transtwowheelerby() == 1 or data.get_transtwowheelerby() == "1"):
            #         error_obj = NWisefinError()
            #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #         error_obj.set_description(ErrorDescription.INVALID_DATA)
            #         return error_obj
            # if data.get_twowheelertrans() == 0 or data.get_twowheelertrans() == None or data.get_twowheelertrans() =="0":
            #     if (data.get_transtwowheelerby() == 0  or data.get_transtwowheelerby() == "0"):
            #         error_obj = NWisefinError()
            #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #         error_obj.set_description(ErrorDescription.INVALID_DATA)
            #         return error_obj
            expense_id = self.expense_id_validation(data.get_expenseid())
            if expense_id is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.AMOUNT)
                return error_obj
            if data.get_placeofactualstay() == "" or data.get_placeofactualstay()==None:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.DATA_ERROR)
                return error_obj
            permission_check = validations.permisssion_check(tour_id, user_id)
            status = validations.exp_claim_status(tour_id)

            if permission_check is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID)
                return error_obj
            startdate_check = validations.tour_startdate_check(tour_id)
            if startdate_check is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID)
                return error_obj
            tour_status = validations.tour_status(tour_id)
            if tour_status is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.TOUR_STATUS)
                return error_obj
            if status is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.CLAIM_STATUS)
                return error_obj


            # if amount_check is False:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # if noof_days is False:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj

    def misc_validation(self,request_obj,user_id):
        validations = Validation(self._scope())
        expense_dropdown=Expense_dropdown()

        for dtl in request_obj['data']:
            data = expreq.Misc_Request(dtl)
            tour_id=dtl['tourgid']
            exp_reason=self.misc_dropdown(tour_id,data.get_expreason())
            if exp_reason is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.DROPDOWN)
                return error_obj
            if data.get_expreason() !="shifting":
                if (data.get_center() != 0) and  (data.get_center() != None) and (data.get_center() != "0"):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.DROPDOWN)
                    return error_obj
            elif data.get_expreason()=="shifting":
                expense_dropdown_centre=self.expense_dropdown_validations(expense_dropdown.misc_centre,data.get_center())
                if expense_dropdown_centre is False:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.DROPDOWN)
                    return error_obj
            claim_amount_check = validations.claim_negative_check(dtl['claimedamount'])
            if (claim_amount_check) is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.AMOUNT)
                return error_obj
            expense_id = self.expense_id_validation(data.get_expenseid())
            if expense_id is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.AMOUNT)
                return error_obj
            if data.get_description() == "" or data.get_description()==None:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.DATA_ERROR)
                return error_obj

            permission_check = validations.permisssion_check(tour_id, user_id)

            if permission_check is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID)
                return error_obj
            startdate_check = validations.tour_startdate_check(tour_id)
            if startdate_check is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID)
                return error_obj
            tour_status = validations.tour_status(tour_id)
            if tour_status is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.TOUR_STATUS)
                return error_obj
            status = validations.exp_claim_status(tour_id)
            if status is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.CLAIM_STATUS)
                return error_obj
    def packingandmoving_validation(self,request_obj,user_id):
        validations = Validation(self._scope())
        for dtl in request_obj['data']:
            tour_id =dtl['tourgid']
            data = expreq.PackingMoving_Request(dtl)
            ttl_distance = validations.claim_negative_check(data.get_totaldisttrans())
            hill_distance = validations.negative_amount(data.get_distinhilly())
            tonage = validations.negative_amount(data.get_tonnagehhgood())
            # max_tonage = validations.negative_amount(data.get_maxeligton())
            # eli_transport = validations.negative_amount(data.get_eligtransamt())
            transport = validations.negative_amount(data.get_transchargesvehicle())
            travel_time = validations.claim_negative_check(data.get_traveltimeinhours())
            no_days_driver = validations.negative_amount(data.get_daysdrivereng())
            driver_battas = validations.negative_amount(data.get_driverbatta())
            octri = validations.negative_amount(data.get_octroivehicle())
            breakage = validations.negative_amount(data.get_breakagecharges())
            # eligi_breakage = validations.negative_amount(data.get_eligbreakagecharge())
            claim_amt = validations.claim_negative_check(dtl['claimedamount'])
            trans_by_two=self.expense_dropdown_validations(Expense_dropdown.yesno,data.get_twowheelertrans())
            household=self.expense_dropdown_validations(Expense_dropdown.yesno,data.get_hhgoodstrans())

            driver=self.expense_dropdown_validations(Expense_dropdown.yesno,data.get_vehicletransbydriver())
            receipt_loss =self.expense_dropdown_validations(Expense_dropdown.yesno,data.get_receiptlosses())
            if float(data.get_totaldisttrans()) < float(data.get_distinhilly()):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj

            if (ttl_distance and hill_distance and tonage and transport and travel_time and no_days_driver and driver_battas and octri \
                    and breakage and claim_amt and trans_by_two and household and driver and receipt_loss) is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            if data.get_twowheelertrans() == 1 or data.get_twowheelertrans() == str(1):
                transtwowheelerby = self.expense_dropdown_validations(Expense_dropdown.yesno,
                                                                      data.get_transtwowheelerby())
                if transtwowheelerby is False:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj
            # if data.get_twowheelertrans() == 0 or data.get_twowheelertrans() == None or data.get_twowheelertrans() =="0":
            #     if (data.get_transtwowheelerby() != None and data.get_transtwowheelerby() != 0 and data.get_transtwowheelerby() != "0"):
            #         error_obj = NWisefinError()
            #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #         error_obj.set_description(ErrorDescription.INVALID_DATA)
            #         return error_obj
            expense_id = self.expense_id_validation(data.get_expenseid())
            if expense_id is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.AMOUNT)
                return error_obj
            if data.get_vehicletransbydriver()==0 or data.get_vehicletransbydriver()=="0":
                if (data.get_daysdrivereng() != 0 and data.get_daysdrivereng() != None and data.get_daysdrivereng()!="0"):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj
            if data.get_twowheelertrans() ==0 or data.get_twowheelertrans()==None or data.get_twowheelertrans()== "0":
                if (data.get_transchargesvehicle() == 1 or data.get_transchargesvehicle() == "1"):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj

            if data.get_vehicletransbydriver()==1 or data.get_vehicletransbydriver()=="1":
                if (data.get_daysdrivereng() == 0 or data.get_daysdrivereng() == None or data.get_daysdrivereng() =="0"):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj
            if  data.get_hhgoodstrans() == 0 or data.get_hhgoodstrans() == None or data.get_hhgoodstrans() == "0":
                if (data.get_billedamthhgoodstrans() != 0 and data.get_billedamthhgoodstrans() !=None and data.get_billedamthhgoodstrans() !="0"):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj
            if data.get_twowheelertrans() ==0 or data.get_twowheelertrans()==None or data.get_twowheelertrans()== "0":
                if (data.get_transchargesvehicle() != 0 and data.get_transchargesvehicle() !=None and data.get_transchargesvehicle()!= "0"):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj
            permission_check = validations.permisssion_check(tour_id, user_id)

            if permission_check is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID)
                return error_obj
            startdate_check = validations.tour_startdate_check(tour_id)
            if startdate_check is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID)
                return error_obj
            tour_status = validations.tour_status(tour_id)
            if tour_status is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.TOUR_STATUS)
                return error_obj
            status = validations.exp_claim_status(tour_id)
            if status is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.CLAIM_STATUS)
                return error_obj



    def localdeputation_validation(self,request_obj,user_id):
        validations = Validation(self._scope())

        tourid = request_obj['data'][0]['tourgid']
        tour_data = TourRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=tourid)[0]
        tour_start_date = tour_data.start_date.date()
        tour_end_date = tour_data.end_date.date()
        for dtl in request_obj['data']:
            tourid=dtl["tourgid"]

            data = Local_dept_res(dtl)

            start_date = datetime.strptime((data.startdate[:10]), '%Y-%m-%d').date()
            end_date = datetime.strptime((data.enddate[:10]), '%Y-%m-%d').date()
            data = expreq.Local_dept_req(dtl)
            expense_id = self.expense_id_validation(data.get_expenseid())
            city_dropdown=self.dail_city_dropdown(data.get_tourid(),data.get_visitcity(),EXPENSE_ID.LocalDeputation)
            if city_dropdown is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj

            if tour_start_date > start_date or tour_end_date < start_date or tour_start_date > end_date or tour_end_date < end_date:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description("Please check the date")
                return error_obj
            date_check = validations.start_end_date(data.get_fromdate(), data.get_todate())
            noof_days = validations.claim_negative_check(data.get_noofdays())
            noof_leavedays = validations.negative_amount(data.get_isleave())


            isleave_cal = ((end_date - start_date).days)+1
            if int(isleave_cal) < int(data.get_isleave()):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            # if int(noof_leavedays) > int(isleave_cal):
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj

            claim_amount = validations.claim_negative_check(dtl['claimedamount'])

            if (date_check and noof_days and noof_leavedays and claim_amount) is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            if expense_id is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            if data.get_visitcity() == "" or data.get_requestercomment() == "" or data.get_requestercomment()==None or  data.get_visitcity() == None:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.DATA_ERROR)
                return error_obj

            permission_check = validations.permisssion_check(tourid, user_id)
            if permission_check is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID)
                return error_obj
            startdate_check = validations.tour_startdate_check(tourid)
            if startdate_check is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID)
                return error_obj
            tour_status = validations.tour_status(tourid)
            if tour_status is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.TOUR_STATUS)
                return error_obj
            status = validations.exp_claim_status(tourid)
            if status is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.CLAIM_STATUS)
                return error_obj

    def local_conveyence_validations(self,request_obj,user_id):
        validations =Validation(self._scope())
        for dtl in request_obj['data']:
            tour_id=dtl["tourgid"]
            data = expreq.Localconveyence_Request(dtl)
            claim_amount_check = validations.claim_negative_check(dtl['claimedamount'])
            if claim_amount_check is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.AMOUNT)
                return error_obj
            mode_of_travel = self.expense_dropdown_validations(Expense_dropdown.conv_travelmode,
                                                               data.get_modeoftravel())
            if mode_of_travel is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.DROPDOWN)
                return error_obj

            modeoftravel = self.expense_localconv(data.get_modeoftravel())
            class_oftravel = self.expense_dropdown_validations(modeoftravel,data.get_subcatogory() )
            centre =self.expense_dropdown_validations(Expense_dropdown.conv_center,data.get_center())
            onward_return =self.expense_dropdown_validations(Expense_dropdown.conv_onward,data.get_onwardreturn())
            if (class_oftravel and centre and onward_return) is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.DROPDOWN)
                return error_obj
            expense_id = self.expense_id_validation(data.get_expenseid())
            if expense_id is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.AMOUNT)
                return error_obj

            if data.get_fromplace() == "" or data.get_fromplace()==None or data.get_toplace() == "" or data.get_toplace()==None or data.get_requestercomment() == "" or data.get_requestercomment()==None:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.DATA_ERROR)
                return error_obj
            permission_check = validations.permisssion_check(tour_id, user_id)
            status = validations.exp_claim_status(tour_id)
            startdate_check=validations.tour_startdate_check(tour_id)
            if startdate_check is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID)
                return error_obj

            if permission_check is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID)
                return error_obj
            tour_status = validations.tour_status(tour_id)
            if tour_status is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.TOUR_STATUS)
                return error_obj
            if status is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.CLAIM_STATUS)
                return error_obj


    # ------------------- 6/1/2022 inserted line  for rollback (for atomic transaction)--------------------------------------------------------

    #----------------------------8/1/2022 DROPDOWN Validations------------------------------------
    def expense_dropdown_validations(self,id,data):
        arr = []
        dropdown_values = Common_dropdown_details.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
            common_drop_down_id=id)
        for dtl in dropdown_values:
            arr.append(dtl.value)

        if str(data) not in arr:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return False
        else:
            return True
    def expense_travelmode_dropdown(self,data):

        dropdown_values = Common_dropdown_details.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
            value=data)
        for dtl in dropdown_values:
            if dtl.value == "Road":
                return Expense_dropdown.travel_Road
            if dtl.value == "Train":
                return Expense_dropdown.travel_Train
            if dtl.value == "Air":
                return Expense_dropdown.travel_Air
            if dtl.value =="Sea":
                return Expense_dropdown.travel_Sea
    def expense_localconv(self,data):
        dropdown_values = Common_dropdown_details.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
            value=data)
        for dtl in dropdown_values:
            if dtl.value == "Road":
                return Expense_dropdown.conv_road
            if dtl.value == "Train":
                return Expense_dropdown.conv_train

    def dail_city_dropdown(self,tour_id,city_name,expense_id):
        request_tab=TourRequest.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=tour_id)
        if expense_id ==8:
            employee_grade=request_tab.empdesignation
        else:
            employee_grade = request_tab.empgrade
        allowance_tab=ALLOWANCE_table.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),city=city_name,salarygrade=employee_grade,expense_id=expense_id)
        return bool(len(allowance_tab))

    def misc_dropdown(self,id,exp_reason):
        request_tab = TourRequest.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=id)
        tour_reason = request_tab.reason
        misc_reason=["breakage","tktcancel","others"]
        misc_shifting=["breakage","tktcancel","others","shifting"]
        if tour_reason == 7:
            if exp_reason not in misc_shifting:
                return False
            else:
                return True
        elif tour_reason != 7:
            if exp_reason not in misc_reason:
                return False
            else:
                return True
    def expense_id_validation(self,expense_id):
        exp_table=Expense.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=expense_id)
        if len(exp_table) ==0:
            return False
        else:
            return True

    def initial_exp_approvedby(self,tour_id,comment,login_id):
        first_expense=TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), tour_id=tour_id, request_type=App_type.CLAIM, applevel=App_level.ZERO_LEVEL,
                                                                                     status=Status.REQUESTED)
        if len(first_expense)==0:
            maker_id=(TourRequest.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=tour_id)).empgid
            TourRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=tour_id).update(entity_id=self._entity_id(),claim_status=Status.REQUESTED)
            TravelHistory.objects.using(self._current_app_schema()).create(tour_id=tour_id, request_type=App_type.CLAIM, approveddate=time_function.ist_time(),
                                                                           applevel=App_level.ZERO_LEVEL, approvedby=login_id,
                                                                           status=Status.REQUESTED, comment=comment, entity_id=self._entity_id())

    def update_claimtable_amount(self,expenseid,tourid,comment,request):
        total_claimedamount=0
        total_approvedamount=0

        expenseid=int(expenseid)
        if expenseid==1:
            exp_data=self.get_travel_tour(tourid,request)
        elif expenseid==2:
            exp_data=self.get_dailydeim_tour(tourid)
        elif expenseid==3:
            exp_data=self.get_incidental_tour(tourid)
        elif expenseid==4:
            exp_data=self.get_localconveyence_tour(tourid)
        elif expenseid==5:
            exp_data=self.get_lodging_tour(tourid,request)
        elif expenseid==6:
            exp_data=self.get_misc_tour(tourid)
        elif expenseid==7:
            exp_data=self.get_packingmoving_tour(tourid,request)
        elif expenseid==8:
            exp_data=self.get_deputation(tourid)
        elif expenseid==9:
            exp_data=self.get_associate_tour(tourid,request)

        for each_exp in exp_data.data:
            total_claimedamount+=int(each_exp.claimedamount)
            total_approvedamount+=int(each_exp.approvedamount)

        if comment is not None:
            ClaimRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=tourid,expensegid=expenseid).update(claimedamount=total_claimedamount,
                                                                                                      approvedamount=total_approvedamount,requestercomment=comment)
        else:
            ClaimRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=tourid,expensegid=expenseid).update(claimedamount=total_claimedamount,
                                                                                                      approvedamount=total_approvedamount)
        return

    def expense_validations(self,request_obj, user_id):
        validations = Validation(self._scope())
        tour_id = request_obj['data'][0]['tour_id']
        tour_data = TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id, entity_id=self._entity_id())[0]
        start_date = tour_data.start_date
        end_date = tour_data.end_date

        for dtl in request_obj['data']:
            validations = Validation(self._scope())
            tourid = request_obj['data'][0]['tour_id']
            tour_data = \
            TourRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), id=tourid)[0]
            tour_start_date = tour_data.start_date.date()
            tour_end_date = tour_data.end_date.date()
            for dtl in request_obj['data']:
                tour_id = dtl['tour_id']
                if 'fromdate' in dtl:
                    fromdate = datetime.strptime((dtl['fromdate'][:10]), '%Y-%m-%d').date()
                    if tour_start_date > fromdate or tour_end_date < fromdate:
                        return True
                if 'todate' in dtl:
                    todate = datetime.strptime((dtl['todate'][:10]), '%Y-%m-%d').date()
                    if tour_start_date > todate or tour_end_date < todate:
                        return True
                else:
                    return False
                # try:
                #     if dtl['expensegid'] == 2:
                #         daily_diem = [
                #             dtl['medicalexpense'] == '', dtl['medicalexpense'] == str, dtl['medicalexpense'] < 0,
                #             dtl['medicalexpense'] == None,
                #             dtl['foodallowance'] == '', dtl['foodallowance'] == str, dtl['foodallowance'] < 0,
                #             dtl['foodallowance'] == None,
                #             dtl["citytype"] == "" , dtl["citytype"] == int, dtl["citytype"] == float, dtl[
                #                 "citytype"] == None, dtl["visitcity"] == "", dtl["visitcity"] == int, dtl[
                #                 "visitcity"] == float,
                #             dtl["visitcity"] == None, dtl['boardingbyorganiser'] == '', dtl[
                #                 'boardingbyorganiser'] == int,
                #             dtl['boardingbyorganiser'] == float, dtl['boardingbyorganiser'] == None,
                #             dtl['noofhours'] == '', dtl['noofhours'] == str, dtl['noofhours'] < 0, dtl[
                #                 'noofhours'] == None,
                #             dtl['noofdays'] == '', dtl['noofdays'] == str, dtl['noofdays'] < 0, dtl[
                #                 'noofdays'] == None]
                #     elif dtl['expensegid'] == 4:
                #         local_cov = [
                #             dtl['claimedamount'] == "", dtl['claimedamount'] <= 0, dtl['claimedamount'] == None,
                #             dtl["modeoftravel"] == "" or dtl["modeoftravel"] == int or dtl["modeoftravel"] == float or
                #             dtl["modeoftravel"] == None or dtl['distance'] == '' or dtl['distance'] == str or dtl[
                #                 'distance'] < 0,
                #             dtl['distance'] == None,
                #             dtl["fromplace"] == "" or dtl["fromplace"] == int or dtl["fromplace"] == float or
                #             dtl["fromplace"] == None or
                #             dtl['toplace'] == '' or dtl['toplace'] == int or dtl['toplace'] == float or dtl[
                #                 'toplace'] == None]
                #     elif dtl['expensegid'] == 5:
                #         lodging = [
                #             dtl['claimedamount'] == "" or dtl['claimedamount'] <= 0 or dtl['claimedamount'] == None or
                #             dtl['Billamountexculdingtax'] == '' or dtl['Billamountexculdingtax'] == str,
                #             dtl['Billamountexculdingtax'] < 0 or
                #             dtl['Billamountexculdingtax'] == None or
                #             dtl['taxonly'] == '' or dtl['taxonly'] == str or dtl['taxonly'] < 0 or
                #             dtl['taxonly'] == None, dtl["Lodge_Homestay"] == "", dtl["Lodge_Homestay"] == int,
                #             dtl["Lodge_Homestay"] == float,
                #             dtl["Lodge_Homestay"] == None,
                #             dtl["city"] == "", dtl["city"] == int, dtl["city"] == float, dtl["city"] == None,
                #             dtl["metro_nonmetro"] == "", dtl["metro_nonmetro"] == int, dtl["metro_nonmetro"] == float,
                #             dtl["metro_nonmetro"] == None, dtl['noofdays'] == '', dtl['noofdays'] == str,
                #             dtl['noofdays'] < 0,
                #             dtl['noofdays'] == None
                #         ]
                #     elif dtl['expensegid'] == 1:
                #         travel = [
                #             dtl['claimedamount'] == "", dtl['claimedamount'] <= 0, dtl['claimedamount'] == None,
                #             dtl['totaltkttamt'] == '', dtl['totaltkttamt'] == str, dtl['totaltkttamt'] < 0,
                #             dtl['totaltkttamt'] == None, dtl["traveltype"] == "", dtl["traveltype"] == int,
                #             dtl["traveltype"] == float,
                #             dtl["traveltype"] == None,
                #             dtl["fromplace"] == "", dtl["fromplace"] == int, dtl["fromplace"] == float,
                #             dtl["fromplace"] == None,
                #             dtl["toplace"] == "", dtl["toplace"] == int, dtl["toplace"] == float,
                #             dtl["toplace"] == None,
                #             dtl["actualmode"] == "", dtl["actualmode"] == int, dtl["actualmode"] == float,
                #             dtl["actualmode"] == None,
                #             dtl["travelclass"] == "", dtl["travelclass"] == int, dtl["travelclass"] == float,
                #             dtl["travelclass"] == None
                #         ]
                #     elif dtl['expensegid'] == 9:
                #         associate = [
                #             dtl['claimedamount'] == "", dtl['claimedamount'] <= 0, dtl['claimedamount'] == None,
                #             dtl["description"] == "", dtl["description"] == int, dtl["description"] == float,
                #             dtl["description"] == None
                #         ]
                #     return True
                # except:
                #     return False