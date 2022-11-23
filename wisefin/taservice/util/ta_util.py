import pytz
import requests
from django.db import transaction

from nwisefin.settings import SERVER_IP
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
# from utilityservice.data.response.dbutil import DataBase
from taservice.models import TravelHistory, TourRequest, ClaimRequest, Common_dropdown_details, TourDetail
from utilityservice.service.applicationconstants import ApplicationNamespace

class TADocUtil:
    REF_TYPE_REQUEST = 1
    REF_TYPE_TRANSACTION = 2
    REF_TYPE_COMMENT = 3
    TOUR=1
    CLAIM=2
    BOOKING=3
class Is_Maker:
    MAKER=0
    ADMIN=1

class Status:
    DEFAULT=-1
    DELETED=0
    REQUESTED=1
    PENDING=2
    APPROVED=3
    REJECTED=4
    RETURNED=5
    FORWARDED=6
    # REQUEST=1
class Module:
    Expense="Expense"
    Travel="Travel"
    Ta_eclaim="TA e-Claim"
class Status_adv:
    # DELETED=0
    # REQUESTED=1
    PENDING=0
    APPROVED=1 #approved and paid
    REJECTED=2
    # RETURNED=5
    # PAYMENT=6 #approved not paid


class TAStatus:
    advance="advance"
    tour="tour"
    claim="claim"
    tourcancel="TourCancel"
    advancecancel="AdvanceCancel"
    expensecancel="expenseCancel"

class Travel_requirements:
    accomodation= 1
    cab= 2
    bus= 3
    train= 4
    air= 5
    accomodation_1= "accomodation"
    cab_2= "cab"
    bus_3= "bus"
    train_4= "train"
    air_5= "air"
# class official:
#     Personal=0
#     Official=1

def travel_requirements_get(type):
    type=int(type)
    if (type == 1):
        return Travel_requirements.accomodation_1
    if (type == 2):
        return Travel_requirements.cab_2
    if (type == 3):
        return Travel_requirements.bus_3
    if (type == 4):
        return Travel_requirements.train_4
    if (type == 5):
        return Travel_requirements.air_5


def status_get(type):
    if (type == -1):
        return Status_set.negative_one
    if (type == 0):
        return Status_set.zero
    if (type == 1):
        return Status_set.one
    elif (type == 2):
        return Status_set.two
    elif (type == 3):
        return Status_set.three
    elif (type == 4):
        return Status_set.four
    elif (type == 5):
        return Status_set.five
    elif (type == 6):
        return Status_set.six

def booking_status_get(type):
    if (type == -2):
        return Booking_status.negative_two
    if (type == -3):
        return Booking_status.negative_three
    if (type == -4):
        return Booking_status.negative_four
    if (type == 0):
        return Booking_status.zero
    if (type == 1):
        return Booking_status.one
    elif (type == 2):
        return Booking_status.two
    elif (type == 3):
        return Booking_status.three
    elif (type == 4):
        return Booking_status.four
    elif (type == 7):
        return Booking_status.seven
    elif (type == -1):
        return Booking_status.negative_one

def adv_status_get(type):
    if (type == 0):
        return Adv_Status_set.zero
    elif (type == 1):
        return Adv_Status_set.one
    elif (type == 2):
        return Adv_Status_set.two
    else:
        return type


class Status_set:
    negative_one="DEFAULT"
    zero="DELETED"
    one='REQUESTED'
    two='PENDING'
    three='APPROVED'
    four='REJECTED'
    five='RETURNED'
    six='FORWARDED'

class Booking_status:
    negative_one="RESERVED"
    negative_two="IN PROGRESS"
    negative_three="BOOKED"
    negative_four="CANCELLED"
    zero="NOT BOOKED"
    one='NOT APPLICABLE'
    two='IN PROGRESS'
    three='BOOKED'
    four='CANCELLED'
    seven='REJECTED'
    int_3=3

class TourRequest_BookingStatus:
    Inprogress=-2
    Reserved=-1
    Not_Booked=0
    Not_applicable=1
    Booked=3
    Cancelled=4
    Rejected=7

class Requirements_booking_status:
    not_booked=0
    in_progress=-1
    cancel_requested=2
    booked=3
    cancelled=4
    rejected=5


class Requirements_official:
    personal=0
    official=1
    personal_official=2


class Adv_Status_set:
    zero='PENDING'
    one='APPROVED'
    two='REJECTED'

class Summary_status:
    one="Pending"
    two="Advance created"
    three="Advance approved"
    four="Claim creted"
    five="Claim approved"

def tour_summary_status(type):
    if (type == 1):
        return Summary_status.one
    elif (type == 2):
        return Summary_status.two
    elif (type == 3):
        return Summary_status.three
class Claim_status:
    one = "CLAIM REQUESTED"
    two ="CLAIM CREATED"
    three ="ClAIM APPROVED"
    four = 'CLAIM REJECTED'
    five = 'CLAIM RETURNED'

def claim_summary_status(type):
    if (type == 1):
        return Claim_status.one
    elif (type == 2):
        return Claim_status.two
    elif (type == 3):
        return Claim_status.three
    elif (type == 4):
        return Claim_status.four
    elif (type == 5):
        return Claim_status.five
class Remainder:
    first_remainder="first_remainder"
    second_remainder="second_remainder"


class App_type:
    TOUR= "TOUR"
    ADVANCE= "ADVANCE"
    CLAIM="CLAIM"
    TourCancel="TourCancel"
    AdvanceCancel="AdvanceCancel"
    tour= "tour"
    advance= "advance"
    claim="claim"
    expense="expense"
    TRAVEL = "TRAVEL"
    REQUIRMENTS="Requirements"


class App_level:
    ZERO_LEVEL=0
    FIRST_LEVEL=1
    SECOND_LEVEL=2
    THIRD_LEVEL=3
class Admin:
    ADMIN=-1
    CEO=-2
class Onbehalfof:
    ZERO=0

class Filterstatus:
    one=1
    two=2


class Filterapptype:
    advance="ADVANCE"
    type="TYPE"
    tour="TOUR"
    claim="CLAIM"

class Filterapplevel:
    zero=0
    one=1

class Ccbs_utils:
    advance=1
    expense=2

#------REFERRED FROM COMMONDROP TABLE ID:------

class Expense_dropdown:
    yesno=1
    travel_travelmode=5
    travel_Road =6
    travel_Train =7
    travel_Air =8
    travel_Sea =9
    incidental_travelmode=10
    conv_travelmode =11
    conv_train=12
    conv_road=13
    conv_center=14
    conv_onward=15
    lodging_center=16
    misc_centre=17
    packing_twowheeler=18
    misc_reason=19

class EXPENSE_ID:
    Travelling=1
    DailyDiem=2
    Incidental=3
    LocalConveyance=4
    Lodging=5
    MiscellaneousCharges=6
    PackagingFreight=7
    LocalDeputation=8
    AssociatedExpense=9


class No_show_status:
    utilised=1
    not_utilised=0
    no_show_requested=-1
    no_show_rejected=2
    no_show_approved=3

class Common_data:
    onbehalf="onbehalf"

from datetime import datetime
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.service.threadlocal import NWisefinThread
class Validation(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)
    def start_end_date(self,startdate,enddate):
        sd_date = datetime.strptime(startdate[:10], '%Y-%m-%d')
        ed_date = datetime.strptime(enddate[:10], '%Y-%m-%d')
        if (sd_date - ed_date).days > 0:
            return False
        else:
            return True

    def start_end_time(self,starttime,endtime):
        sd_time = datetime.strptime(starttime[:8], '%H:%M:%S')
        ed_time = datetime.strptime(endtime[:8], '%H:%M:%S')
        if sd_time>ed_time:
            return False
        else:
            return True

    def start_end_date_time(self,startdate,enddate):
        sd_date = datetime.strptime(startdate[:19], '%Y-%m-%d %H:%M:%S')
        ed_date = datetime.strptime(enddate[:19], '%Y-%m-%d %H:%M:%S')
        if sd_date>ed_date:
            return False
        else:
            return True

    def negative_amount(self,amount):
        if amount is None:
            return True
        if float(amount)<0:
            return False
        else:
            return True

    def claim_negative_check(self,amount):
        if amount is None:
            return True
        if float(amount)<=0:
            return False
        else:
            return True

    def permisssion_check(self,tourid,empid):
        approver_list = []
        tour_data=TourRequest.objects.using(self._current_app_schema()).get(id=tourid)
        approver_data=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tourid)
        approver_list.append(tour_data.empgid)
        for approver in approver_data:
            approver_list.append(approver.approvedby)
        if tour_data.onbehalfof>0:
            approver_list.append(tour_data.onbehalfof)
        if empid not in approver_list:
            return False
        else:
            return True
    def tour_startdate_check(self,tourid):
        tour_req_table=TourRequest.objects.using(self._current_app_schema()).get(id=tourid)
        time_function=Timecalculation()
        diffdays = (time_function.ist_date() - tour_req_table.start_date.date()).days
        if diffdays == 0:
            return True
        else:
            return bool(max(0, diffdays))

    def tour_maker_check(self,tourid,empid):
        maker=TourRequest.objects.using(self._current_app_schema()).filter(id=tourid)[0]
        maker_list=[]
        maker_list.append(maker.empgid)
        maker_list.append(maker.onbehalfof)
        if empid not in maker_list:
            return False
        else:
            return True

    def tour_maker_only_check(self,tourid,empid):
        maker=TourRequest.objects.using(self._current_app_schema()).get(id=tourid)
        if empid != maker.empgid:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID_MAKER)
            return error_obj
        else:
            return True

    def permisssion_check_type(self,tourid,empid,type,app_lvl):
        # approver=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tourid, request_type=type, applevel=app_lvl)
        maker=TourRequest.objects.using(self._current_app_schema()).filter(id=tourid).last()
        approver_list=[]
        # for app in approver:
            # approver_list.append(app.approvedby)
        approver_list.append(maker.empgid)
        approver_list.append(maker.onbehalfof)
            # approver_list.append(app.onbehalfof)
        if empid not in approver_list:
            return False
        else:
            return True

    def advance_datecheck(self,startdate):
        stdate=datetime.strptime(str(startdate)[:10], '%Y-%m-%d')
        if stdate.date()<datetime.today().date():
            return False
        else:
            return True

    def claim_datecheck(self,enddate):
        e_date=datetime.strptime(enddate[:10], '%Y-%m-%d')
        if e_date<datetime.today():
            return False
        else:
            return True

    def ccbs_validation(self,amount,ccbs_data,tourgid):
        total_percentage = 0
        ccbs_amount = 0
        error_obj = NWisefinError()
        for ccbs in ccbs_data:
            total_percentage+=float(ccbs['percentage'])
            ccbs_amount+=float(ccbs['amount'])
            if ccbs['tourgid'] is None or ccbs['ccid'] is None or ccbs['bsid'] is None or float(ccbs['percentage'])<=0 or float(ccbs['amount'])<=0:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_CCBS)
                return error_obj
            if int(ccbs['tourgid']) != int(tourgid):
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_TOURID)
                return error_obj
        if round(total_percentage)!=100:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.PERCENTAGE_ERROR)
            return error_obj
        if amount=="EXP":
            amount=0
            claim_amount=ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=tourgid,status=1).values("claimedamount")
            for amount_data in claim_amount:
                amount+=amount_data['claimedamount']
            if round(float(amount),2) != round(ccbs_amount,2):
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.AMOUNT_ERROR)
                return error_obj
            else:
                return True

        if round(float(amount),2)!=round(ccbs_amount,2):
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.AMOUNT_ERROR)
            return error_obj
        else:
            return True

    def higher_approve_amount(self,claimed_amount,approved_amount):
        if float(approved_amount)>round(float(claimed_amount),2):
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.HIGHER_APPROVE_AMOUNT)
            return error_obj
        else:
            return True

    def empty_array_check(self,array):
        if array==[]:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj
        else:
            return True

    @transaction.atomic
    def exp_claim_status(self,tourgid):
        tour_req_claim_status=TourRequest.objects.using(self._current_app_schema()).filter(id=tourgid)[0].claim_status
        if tour_req_claim_status==Status.APPROVED or tour_req_claim_status==Status.REJECTED or tour_req_claim_status==Status.FORWARDED or tour_req_claim_status==Status.PENDING :
            return False
        if tour_req_claim_status==Status.RETURNED or tour_req_claim_status==Status.DEFAULT or tour_req_claim_status==Status.REQUESTED :
            return True


    def tour_status(self,tour_id):
        tour_req_id = TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id)[0].tour_status
        if tour_req_id == Status.REJECTED or tour_req_id == Status.FORWARDED or \
                tour_req_id == Status.DEFAULT or tour_req_id == Status.RETURNED or tour_req_id == Status.PENDING:
            return False
        if tour_req_id == Status.APPROVED:
            return True
    #tour_status for delete
    def tour_status_del(self,tour_id):
        tour_req_id = TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id)[0].tour_status
        if tour_req_id == Status.REJECTED or tour_req_id == Status.FORWARDED  \
                 or tour_req_id == Status.RETURNED or tour_req_id == Status.APPROVED :
            return False
        if tour_req_id == Status.DEFAULT or tour_req_id == Status.RETURNED or tour_req_id == Status.PENDING :
            return True
    # def edit_claimstatus(self,tour_id):
    #     tour_req_claim_status = TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id)[0].claim_status
    #     if tour_req_claim_status == Status.REJECTED or tour_req_claim_status == Status.FORWARDED or \
    #             tour_req_claim_status == Status.APPROVED or tour_req_claim_status == Status.PENDING:
    #         return False
    #     if tour_req_claim_status == Status.RETURNED or Status.DEFAULT:
    #         return True


    # def approver_validation(self, type,approver,request):
    #     from utilityservice.service.ta_api_service import ApiService
    #     from taservice.service.branch_emp_ser import Branch_emp_ser
    #     approver_except=[0]
    #     tourid=None
    #     empdtl = ApiService(self._scope())
    #     approver = empdtl.emp_all_details(int(approver), request)
    #     approver_code=approver.code
    #     branch=approver.employee_branch_id
    #     service=Branch_emp_ser(self._scope())
    #     approver=service.branch_approver_get( type, branch, str(approver_code).lower(), approver_except, request, tourid)
    #     return bool(len(approver))

        

    def emp_str_validation(self,request_obj):
        for check in request_obj['data']:
            if check() == "":
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.DATA_ERROR)
                return error_obj

    def fileexe_validation(self,extension):
        if extension in ['txt', 'doc', 'pdf', 'ppt', 'pot', 'pps', 'pptx', 'odt', 'odg', 'odp', 'ods', 'docx', 'docm',
                         'dotx', 'dotm', 'docb',
                         'xlsx', 'xls', 'xlt', 'xlm', 'xlsm', 'xltx', 'xltm', 'jpg', 'jpeg', 'tiff', 'tif', 'png',
                         'JPG', 'JPEG', 'PNG', 'PDF']:
            return True
        else:
            return False

    def exel_file_validation(self,extension):
        if extension in ['xlsx', 'xls', 'xlt', 'xlm', 'xlsm', 'xltx', 'xltm']:
            return True
        else:
            return False

class Common_drop_down(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)


    def common_drop_down_get(self,value,exp_id):

        cd_details=Common_dropdown_details.objects.using(self._current_app_schema()).filter(value=value,status=1,common_drop_down_id=exp_id)
        if len(cd_details)!=0:
            name=cd_details[0].name
        else:
            name=None
        return {"name":name,"value":value}

    def hsn_percentage_get(self,request,hsn_code):
        token = request.headers['Authorization']
        headers = {"content-type": "application/json", "Authorization": "" + token + ""}
        # hsn_get_url = 'http://143.110.244.51:8000/mstserv/get_hsn_ta'
        hsn_get_url = SERVER_IP+'/mstserv/search_hsn'
        if hsn_code==None or hsn_code=='':
            hsn_code='0'
        params="query="+hsn_code
        resp = requests.get(hsn_get_url, params=params, headers=headers, verify=False)
        results = resp.content.decode("utf-8")
        if resp.status_code==200:
            results = json.loads(results)
            return results
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(json.loads(results))
            return error_obj


class DocModule:
    TA = 8

import json
class DictObj:
    def get(self,dict1):
        if isinstance(dict1,str):
            dict1=json.loads(dict1)
        self.__dict__.update(dict1)
        return self.__dict__
    def get_obj(self,dict1):
        self.__dict__.update(dict1)
        return self
class Timecalculation:
    def ist_time(self):
        IST = pytz.timezone('Asia/Kolkata')
        datetime_ist = datetime.now(IST)
        today = datetime_ist.strftime('%Y-%m-%d %H:%M:%S')
        return today
    def ist_date(self):
        IST = pytz.timezone('Asia/Kolkata')
        datetime_ist = datetime.now(IST)
        today = datetime_ist.strftime('%Y-%m-%d %H:%M:%S')
        today_date = datetime.strptime((today[:10]), '%Y-%m-%d').date()
        return today_date
    def standard_time(self):
        today_std = datetime.today()

    def ist_time_format(self):
        IST = pytz.timezone('Asia/Kolkata')
        datetime_ist = datetime.now(IST)
        return datetime_ist.today()

class metro_non:
    metro=0
    non_metro=1

    metro_var="Metro"
    non_metro_var="Non Metro"