import json
import traceback

import boto3
import pandas as pd
from django.conf import settings
from django.db import transaction
from django.db.models import Max, F, Min, Count
from django.http import HttpResponse
from django.utils import timezone
from django.db.models.query_utils import Q

from docservice.service.documentservice import DocumentsService
from docservice.util.docutil import DocModule
from taservice.data.request.cd_req import Cd_del_req
from taservice.data.response.cd_res import Cd_res
from taservice.data.response.doc_resp import TADocumentsResponse
from taservice.data.response.travelrequirement import AccomodationBooking_Response, Booking_req
from taservice.service.emp_name_get import emp_dtl, Tourno_details
from nwisefin.settings import logger
from taservice.service.ta_email import ta_email
from taservice.service.travelrequirement import Cab_requirement, Bus_requirement, Air_requirement, Train_requirement, \
    AccomodationBooking_requirement, Booking_requirement
from userservice.models import EmployeeDepartmentPermission, Department
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage

from taservice.models.tamodels import TourReason, TourDetail, Date_relaxation, TADocuments, TourAdvance, \
    TransactionComments, AccomodationBookingInfo, CabBookingInfo, BusBookingInfo, \
    TrainBookingInfo, AirBookingInfo, BookingHistory, InternationalTravel, Common_dropdown, Client, CabMapping, Ta_City, \
    FrequentData, TravelEditHistory
from taservice.models.tamodels import TourReason, TourDetail, TravelHistory, Date_relaxation, TADocuments, TourAdvance, \
    ClaimRequest, AccomodationBookingDetails, CabBookingDetails, AirBookingDetails, TrainBookingDetails, \
    BusBookingDetails,BookingHistory,Holiday,TourExpense
from taservice.models.tamodels import TourRequest as TourRequestmodel
from taservice.data.response.tourmaker import TourMaker as TourMakerResponse, Chatbox_response, Doc_response, \
    Travel_count
from utilityservice.data.response.nwisefinlist import NWisefinList
from taservice.service.tourapprovedby import TourApprovedby
from taservice.util.ta_util import App_level, Status, Filterapptype, status_get, App_type, Validation, Timecalculation, \
    Travel_requirements, Booking_status, TADocUtil, Remainder, EXPENSE_ID, Requirements_booking_status, \
    TourRequest_BookingStatus, Requirements_official
from datetime import datetime, timedelta
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator

# from utilityservice.service.dbutil import DataBase
from taservice.data.request.tourmaker import Chat_Box, Doc_type, Booking, TourDetailRequest
from utilityservice.permissions.util.dbutil import ModuleList, RoleList
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.ta_api_service import ApiService
from datetime import datetime, timedelta
from taservice.data.request.travelrequirement import Document_upload, No_show_req

# IST = pytz.timezone('Asia/Kolkata')
# datetime_ist = datetime.now(IST)
# today = datetime_ist.strftime('%Y-%m-%d %H:%M:%S')
#
# today_std=datetime.today()

time_function = Timecalculation()

from utilityservice.service.threadlocal import NWisefinThread
@transaction.atomic
class TourMaker(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)
    @transaction.atomic
    def create_tour(self, request_obj, tour, user_id, request):
        # today_date=datetime.strptime((today[:10]), '%Y-%m-%d').date()

        # 13/1 file validations-Ste
        error_obj = NWisefinError()
        logger.info('ta_ Tour_create- ' + str(user_id) + str(request_obj))
        reason_id = int(request_obj['reason'])
        file_req = (TourReason.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),
                                                                             id=reason_id)).fileupload
        if file_req == 1:
            prev_files = 0
            if "id" in request_obj:
                prev_file_ck = TADocuments.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                            request_id=request_obj[
                                                                                                'id'], status=1)
                prev_files = len(prev_file_ck)
            if len(request.FILES) == 0 and prev_files == 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.FILE_REQUIRED)
                return error_obj


        # before_date = (time_function.ist_date() - timedelta(days=170))

        # after_date = (time_function.ist_date() + timedelta(days=90))

        # millisecond=False
        # if "millisecond" in request_obj:
        #     millisecond=True
        try:
            int(request_obj['startdate'])
            millisecond = True
        except:
            millisecond = False


        if millisecond is True:
            request_obj['startdate']=str(datetime.fromtimestamp(int(request_obj['startdate'])/1000.0))
            request_obj['enddate']=str(datetime.fromtimestamp(int(request_obj['enddate'])/1000.0))

            self.detail_millisecond(request_obj['detail'])

            # for i in range(len(request_obj['detail'])):
            #     for each_req in request_obj['detail'][i]['requirements']:

                    # tour_dtl_validation_ck = self.requirement_millisecond(each_req)

        start_date = request_obj['startdate']
        end_date = request_obj['enddate']

        # request_obj['week_end_travel']="weekend"

        onbehalfof_id = tour.onbehalfof
        if onbehalfof_id > 0:
            tour_utiliser=onbehalfof_id
        else:
            tour_utiliser=user_id

        if 'id' in request_obj:
            tour_edit_id=request_obj['id']
        else:
            tour_edit_id=None

        holiday_check = self.holidaycheck_weekend(start_date, end_date,tour_utiliser,tour_edit_id)
        if isinstance(holiday_check, NWisefinError):
            return holiday_check


        elif holiday_check.ongoing_tour==True:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.SAME_DAY_TOUR)
            return error_obj

        week_end_reason = None
        if len(json.loads(holiday_check.get())["data"])!=0:
            week_end_reason=request_obj['week_end_travel']
            if request_obj['week_end_travel'] is None:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.WEEDEND_TOUR_REASON)
                return error_obj


        startdate = datetime.strptime((start_date[:10]), '%Y-%m-%d').date()
        enddate = datetime.strptime((end_date[:10]), '%Y-%m-%d').date()

        # indian_date_time=time_function.ist_date()
        # if startdate<indian_date_time:
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.INVALID_DATE)
        #     return error_obj

        international_travel = [9, 10]
        # date_relax_startdate = before_date < startdate < after_date
        # date_relax_enddate = enddate < after_date
        api_service = ApiService(self._scope())
        rm_get = api_service.get_RM_ID(request, tour_utiliser)
        if rm_get ==None:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID_RM)
            return error_obj


        if reason_id==11:
            for each_dtl in request_obj['detail']:
                if each_dtl['requirements'] != None:
                    # for i in range(len(request_obj['detail'])):
                    for each_req in each_dtl['requirements']:
                        if int(each_req["booking_needed"])!=2:
                            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                            error_obj.set_description(ErrorDescription.ONLY_CAB_REQ)
                            return error_obj

        starting_point=request_obj['detail'][0]["startingpoint"]
        ending_point=request_obj['detail'][-1]["placeofvisit"]
        non_base_location=Booking_requirement(self._scope())
        base_location=non_base_location.employeeid_city(tour_utiliser,request)
        if starting_point.lower() == base_location.name.lower():
            non_base_reason=None
        else:
            non_base_reason=tour.get_non_base_location()
            if tour.get_non_base_location() is None:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.NON_BASE_LOCATION)
                return error_obj



        if 'id' in request_obj:

            sd_date = datetime.strptime(request_obj['startdate'][:10], '%Y-%m-%d')
            ed_date = datetime.strptime(request_obj['enddate'][:10], '%Y-%m-%d')

            dtl_first=request_obj['detail'][0]['startdate']
            dtl_last=request_obj['detail'][-1]['enddate']

            dtl_first_date=datetime.strptime(dtl_first[:10], '%Y-%m-%d')
            dtl_last_date=datetime.strptime(dtl_last[:10], '%Y-%m-%d')

            if dtl_first_date!=sd_date or dtl_last_date!=ed_date:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorMessage.INVALID_DATE_RANGE)
                return error_obj

            for j in range(len((request_obj['detail']))):
                if j!=0:
                    next_detail_start_date=datetime.strptime(request_obj['detail'][j]["startdate"][:10] , '%Y-%m-%d')

                    detail_end_date=datetime.strptime(request_obj['detail'][j-1]["enddate"][:10] , '%Y-%m-%d')

                    if (next_detail_start_date-detail_end_date).days>1:
                        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        error_obj.set_description(ErrorMessage.INVALID_DATE_RANGE)
                        return error_obj

            detail_id_arr=[]
            for each_detail in request_obj['detail']:
                if 'id' in each_detail:
                    detail_id_arr.append(each_detail['id'])

            prev_dtl_check=self.previous_dtl_check(request_obj['id'],sd_date,ed_date,detail_id_arr)
            if prev_dtl_check >0:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorMessage.DELETE_THE_PREVIOUS_DETAILS)
                return error_obj

            # RM
            request_obj['approval'] = rm_get
            # try:

            validation_service = Validation(self._scope())
            permission_check = validation_service.permisssion_check_type(request_obj['id'], user_id, App_type.TOUR, 0)
            if permission_check == False:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.VALID_USER)
                return error_obj

            # if date_relax_startdate is False:
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorMessage.INVALID_DATE)
            #     return error_obj
            # if date_relax_enddate is False:
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorMessage.INVALID_DATE)
            #     return error_obj
            tour_data = TourRequestmodel.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),
                                                                                       id=request_obj['id'])
            # if tour_data.tour_status ==Status.APPROVED:
            #     approved_tour_edit = True
            # else:
            #     approved_tour_edit = False
            #
            # if approved_tour_edit==False:
            edit_check=self.edit_validations(request_obj['id'],App_type.TOUR)
            if edit_check==False:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.CANT_EDIT_THIS_TOUR)
                return error_obj



            # if tour_data.tour_status == Status.DEFAULT or tour_data.tour_status == Status.REJECTED or tour_data.tour_status == Status.FORWARDED:
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.APPROVE_ERROR)
            #     return error_obj
            if tour_data.tour_status == Status.DEFAULT or tour_data.tour_status == Status.APPROVED or tour_data.tour_status == Status.REJECTED or tour_data.tour_status == Status.FORWARDED:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.APPROVE_ERROR)
                return error_obj
            # sd_date = datetime.strptime(tour.get_startdate()[:10], '%Y-%m-%d')
            # ed_date = datetime.strptime(tour.get_enddate()[:10], '%Y-%m-%d')
            sd_date = datetime.strptime(request_obj['startdate'][:10], '%Y-%m-%d')
            ed_date = datetime.strptime(request_obj['enddate'][:10], '%Y-%m-%d')
            duration_days = ((ed_date - sd_date).days) + 1
            if duration_days != request_obj['durationdays']:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.DURATION_DAYS)
                return error_obj
            if (sd_date - ed_date).days > 0:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorMessage.INVALID_DATE)
                return error_obj
            # if user_id==int(request_obj['permittedby']) or int(tour_data.empgid)==int(request_obj['permittedby'])or int(request_obj['permittedby'])==0:
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.PERMITTED_BY)
            #     return error_obj
            if user_id == int(request_obj['approval']) or int(tour_data.empgid) == int(request_obj['approval']) or int(
                    tour_data.onbehalfof) == int(request_obj['approval']) or int(request_obj['approval']) == 0:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.APPROVER)
                return error_obj
            validation_service = Validation(self._scope())
            # approver_check = validation_service.approver_validation(App_type.tour, request_obj['approval'], request)
            # if approver_check is False:
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.APPROVER_NOT_IN_LIST)
            #     return error_obj
            if int(request_obj['reason']) == 0 or int(request_obj['reason']) > 11:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.REASON)
                return error_obj
            if 'opening_balance' and 'quantum_of_funds' not in request_obj:
                request_obj['opening_balance'] = 0
                request_obj['quantum_of_funds'] = 0
            if reason_id != 2:
                request_obj['opening_balance'] = 0
                request_obj['quantum_of_funds'] = 0
            if 'transfer_on_promotion' not in request_obj:
                request_obj['transfer_on_promotion'] = 0
            transfer_except = [6, 7, 8]
            if reason_id not in transfer_except:
                request_obj['transfer_on_promotion'] = 0

            if reason_id  in international_travel:
                request_obj['international_travel'] = 1
            else:
                request_obj['international_travel'] = 0
            # remarks=request_obj['ordernoremarks']
            # if 'ordernoremarks' not in request_obj or request_obj['ordernoremarks']=="":
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.COMMENT)
            #     return error_obj

            tour_dtl_validation_ck = self.tour_detail_validation(request_obj['detail'], request_obj['startdate'],
                                                                 request_obj['enddate'], request_obj['id'])
            if isinstance(tour_dtl_validation_ck, NWisefinError):
                return tour_dtl_validation_ck
            for j in range(len((request_obj['detail']))):

                if 'id' in request_obj['detail'][j]:
                    each_dtl_start_date=request_obj['detail'][j]['startdate']
                    each_dtl_end_date=request_obj['detail'][j]['enddate']
                    each_dtl_start_date=datetime.strptime(each_dtl_start_date[:10], '%Y-%m-%d')
                    each_dtl_end_date=datetime.strptime(each_dtl_end_date[:10], '%Y-%m-%d')
                    exclude_arr=[]
                    detail_id=request_obj['detail'][j]['id']
                    if (request_obj['detail'])[j]['requirements'] == None:
                        prev_accommodation_check = self.prev_accommodation_check(detail_id, each_dtl_start_date,
                                                                                 each_dtl_end_date, exclude_arr)
                        prev_cab_check = self.prev_cab_check(detail_id, each_dtl_start_date, each_dtl_end_date,
                                                             exclude_arr)
                        prev_bus_check = self.prev_bus_check(detail_id, each_dtl_start_date, each_dtl_end_date,
                                                             exclude_arr)
                        prev_train_check = self.prev_train_check(detail_id, each_dtl_start_date,
                                                                 each_dtl_end_date, exclude_arr)
                        prev_air_check = self.prev_air_check(detail_id, each_dtl_start_date, each_dtl_end_date,
                                                             exclude_arr)
                        if prev_accommodation_check or prev_cab_check or prev_bus_check or prev_train_check or prev_air_check > 0:
                            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                            error_obj.set_description(ErrorMessage.DELETE_THE_PREVIOUS_REQUIREMENTS)
                            return error_obj
                        # if len(prev_req) > 0:
                        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        #     error_obj.set_description(ErrorMessage.DELETE_THE_PREVIOUS_DETAILS)
                        #     return error_obj
                    else:
                        acc_exclude_arr = []
                        cab_exclude_arr = []
                        bus_exclude_arr = []
                        train_exclude_arr = []
                        air_exclude_arr = []
                        for each_req in request_obj['detail'][j]['requirements']:
                            booking_needed=int(each_req["booking_needed"])
                            if booking_needed==Travel_requirements.accomodation:
                                if 'id' in each_req:
                                    acc_exclude_arr.append(each_req['id'])
                            elif booking_needed==Travel_requirements.cab:
                                if 'id' in each_req:
                                    cab_exclude_arr.append(each_req['id'])
                            elif booking_needed==Travel_requirements.bus:
                                if 'id' in each_req:
                                    bus_exclude_arr.append(each_req['id'])
                            elif booking_needed==Travel_requirements.train:
                                if 'id' in each_req:
                                    train_exclude_arr.append(each_req['id'])
                            elif booking_needed==Travel_requirements.air:
                                if 'id' in each_req:
                                    air_exclude_arr.append(each_req['id'])

                        prev_accommodation_check = self.prev_accommodation_check(detail_id, each_dtl_start_date, each_dtl_end_date,acc_exclude_arr)
                        prev_cab_check = self.prev_cab_check(detail_id, each_dtl_start_date, each_dtl_end_date,cab_exclude_arr)
                        prev_bus_check = self.prev_bus_check(detail_id, each_dtl_start_date, each_dtl_end_date,bus_exclude_arr)
                        prev_train_check = self.prev_train_check(detail_id, each_dtl_start_date, each_dtl_end_date,train_exclude_arr)
                        prev_air_check = self.prev_air_check(detail_id, each_dtl_start_date, each_dtl_end_date,air_exclude_arr)
                        if (prev_accommodation_check) or (prev_cab_check) or (prev_bus_check) or (prev_train_check) or (prev_air_check)  > 0:
                            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                            error_obj.set_description(ErrorMessage.DELETE_THE_PREVIOUS_REQUIREMENTS)
                            return error_obj



                if (request_obj['detail'])[j]['requirements'] != None:
                    # for i in range(len(request_obj['detail'])):
                    for each_req in request_obj['detail'][j]['requirements']:


                        # if approved_tour_edit==True:
                        #     booked_req=self.booked_req_edit_check(each_req)
                        #     if booked_req!=True:
                        #         return booked_req



                        tour_dtl_validation_ck = self.requirement_validation_edit(each_req, request_obj['detail'][j]['startdate'],
                                                                             request_obj['detail'][j]['enddate'])
                        if isinstance(tour_dtl_validation_ck, NWisefinError):
                            return tour_dtl_validation_ck

                    req_id_validation = self.req_id_validation(request_obj['detail'])
                    if req_id_validation != True:
                        return req_id_validation


            if 'international_travel' not in request_obj:
                request_obj['international_travel'] = 0

            Tourrequest = TourRequestmodel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                            id=request_obj[
                                                                                                'id']).update(
                reason=request_obj['reason'],
                permittedby=0,
                international_travel=request_obj['international_travel'],
                start_date=request_obj['startdate'][0:10],
                end_date=request_obj['enddate'][0:10],
                week_end_travel=week_end_reason,
                durationdays=duration_days,
                remarks=tour.get_ordernoremarks(),
                opening_balance=request_obj['opening_balance'],
                quantum_of_funds=request_obj['quantum_of_funds'],
                transfer_on_promotion=request_obj['transfer_on_promotion'],
                # sortterm_travel=request_obj['sortterm_travel'],
                sortterm_travel=tour.get_sortterm_travel(),
                updated_date=timezone.now(),
                updated_by=user_id,
                non_base_location=non_base_reason)
            detail = request_obj['detail']
            # set_delete = True
            # if 'mobile' in request_obj:
            #     if int(request_obj['mobile']) == 1:
            #         set_delete = False
            # if set_delete == True:
                # delete_pre_detail=TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=request_obj['id']).update(status=0)


            # if detail == []:
            #     transaction.set_rollback(True)
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorMessage.INVALID_DATA)
            #     return error_obj


            # if int(request_obj['international_travel']) == 1:
            #     prev_inter_trv = InternationalTravel.objects.using(self._current_app_schema()).filter(
            #         tour_id=request_obj['id'], entity_id=self._entity_id()).last()
            #     if prev_inter_trv is None:
            #         InternationalTravel.objects.using(self._current_app_schema()).create(
            #             tour=request_obj['id'],
            #             created_by=user_id,
            #         )
            #     else:
            #         InternationalTravel.objects.using(self._current_app_schema()).filter(id=prev_inter_trv.id,
            #                                                                              entity_id=self._entity_id()).update(
            #             status=1)
            # else:
            #     prev_inter_trv = InternationalTravel.objects.using(self._current_app_schema()).filter(
            #         tour_id=request_obj['id'], entity_id=self._entity_id()).last()
            #     if prev_inter_trv is not None:
            #         InternationalTravel.objects.using(self._current_app_schema()).filter(tour_id=request_obj['id'],
            #                                                                              entity_id=self._entity_id()).update(
            #             status=0)

            # startdate = startdate[:10]
            sdate = startdate
            if (time_function.ist_date() - sdate).days >= 90:
                prev_dr=Date_relaxation.objects.using(self._current_app_schema()).filter(tour_id=request_obj['id'])
                if len(prev_dr)==0:
                    Date_relaxation.objects.using(self._current_app_schema()).create(tour_id=request_obj['id'], status=0,created_by=user_id,entity_id=self._entity_id())
                else:
                    Date_relaxation.objects.using(self._current_app_schema()).filter(tour_id=request_obj['id']).update(
                                                                                     status=0, created_by=user_id,
                                                                                     entity_id=self._entity_id())
            else:
                Date_relaxation.objects.using(self._current_app_schema()).filter(tour_id=request_obj['id']).update(
                    status=1, created_by=user_id,
                    entity_id=self._entity_id())



            for dtl in detail:
                # for dtl in detail:
                # dtl_sdate = datetime.strptime(dtl['startdate'][:10], '%Y-%m-%d')
                # dtl_edate = datetime.strptime(dtl['enddate'][:10], '%Y-%m-%d')
                #
                # if sd_date > dtl_sdate or ed_date < dtl_edate:
                #     transaction.set_rollback(True)
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorMessage.INVALID_DATE)
                #     return error_obj

                client_value = api_service.get_client(request, dtl['client'])
                if client_value.client_name == "OTHERS":
                    client_name = dtl['other_client_name']
                else:
                    client_name = None


                if 'id' in dtl:

                    # dtl_tour_id=(TourDetail.objects.using(self._current_app_schema()).get(id=dtl['id'])).tour_id
                    # if dtl_tour_id!=int(request_obj['id']):
                    #     # transaction.set_rollback(True)
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.INVALID_ID)
                    #     return error_obj

                    # if dtl['startingpoint']=="" or dtl['placeofvisit']=="" or dtl['purposeofvisit']=="":
                    #     transaction.set_rollback(True)
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                    #     return error_obj
                    req=TourDetailRequest(dtl)

                    Tourdetaildata = TourDetail.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=dtl['id']).update(startdate=dtl['startdate'][0:10],
                                                                          enddate=dtl['enddate'][0:10],
                                                                          startingpoint=dtl['startingpoint'],
                                                                          placeofvisit=dtl['placeofvisit'],
                                                                          purposeofvisit=dtl['purposeofvisit'],
                                                                          toplace=None,
                                                                          client=dtl['client'],
                                                                          client_name=client_name,
                                                                          official=req.get_official(),
                                                                          comments=req.get_comments(),
                                                                          # booking_needed=dtl['booking_needed'],
                                                                          updated_date=timezone.now(),
                                                                          updated_by=user_id,
                                                                          status=1)

                    # travel_req = self.insert_travel_requirements(dtl['requirements'],
                    #                                              Tourdetaildata.id, user_id)
                    if dtl['requirements']!=None:
                        for each_requirement in dtl['requirements']:
                            req_type = int(each_requirement['booking_needed'])
                            if req_type == Travel_requirements.accomodation:
                                accomodation_service = AccomodationBooking_requirement(self._scope())
                                accomodation_service.accomadation_data(each_requirement, user_id, dtl['id'])
                            elif req_type == Travel_requirements.cab:
                                cab_service = Cab_requirement(self._scope())
                                cab_service.cab_data(each_requirement, user_id, dtl['id'])
                            elif req_type == Travel_requirements.bus:
                                bus_service = Bus_requirement(self._scope())
                                bus_service.insert_bus_data(each_requirement, user_id, dtl['id'])
                            elif req_type == Travel_requirements.train:
                                train_service = Train_requirement(self._scope())
                                train_service.Train_data(each_requirement, user_id, dtl['id'])
                            elif req_type == Travel_requirements.air:
                                air_service = Air_requirement(self._scope())
                                air_service.Air_data(each_requirement, user_id, dtl['id'])
                            else:
                                error_obj = NWisefinError()
                                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                                error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
                                return error_obj

                        air_required = bool(len(AirBookingInfo.objects.using(self._current_app_schema()).filter(
                            travel_detail_id=dtl['id'], status=1)))
                        train_required = bool(len(TrainBookingInfo.objects.using(self._current_app_schema()).filter(
                            travel_detail_id=dtl['id'], status=1, entity_id=self._entity_id())))
                        bus_required = bool(len(BusBookingInfo.objects.using(self._current_app_schema()).filter(
                            travel_detail_id=dtl['id'], status=1, entity_id=self._entity_id())))
                        cab_required = bool(len(CabBookingInfo.objects.using(self._current_app_schema()).filter(
                            travel_detail_id=dtl['id'], status=1, entity_id=self._entity_id())))
                        accomodation_required = bool(
                            len(AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(
                                travel_detail_id=dtl['id'], status=1, entity_id=self._entity_id())))

                        Tourdetaildata = TourDetail.objects.using(self._current_app_schema()).filter( entity_id=self._entity_id(),
                            id=dtl['id']).update(air_required=air_required,
                                                 train_required=train_required,
                                                 bus_required=bus_required,
                                                 cab_required=cab_required,
                                                 accomodation_required=accomodation_required
                                                 )

                else:

                    # if dtl['startingpoint']=="" or dtl['placeofvisit']=="" or dtl['purposeofvisit']=="":
                    #     transaction.set_rollback(True)
                    #     error_obj = NWisefinError()
                    #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                    #     return error_obj
                    req=TourDetailRequest(dtl)
                    Tourdetaildata = TourDetail.objects.using(self._current_app_schema()).create(
                        tour_id=request_obj['id'],
                        startdate=dtl['startdate'][0:10],
                        enddate=dtl['enddate'][0:10],
                        startingpoint=dtl['startingpoint'],
                        placeofvisit=dtl['placeofvisit'],
                        purposeofvisit=dtl['purposeofvisit'],
                        toplace=None,
                        client=dtl['client'],
                        client_name=client_name,
                        official=req.get_official(),
                        comments=req.get_comments(),
                        # comments=dtl['comments'],
                        # booking_needed=dtl['booking_needed'],
                        created_date=timezone.now(),
                        created_by=user_id, entity_id=self._entity_id())

                    # travel_req = self.insert_travel_requirements(dtl['requirements'],
                    #                                              Tourdetaildata.id, user_id)
                    if dtl['requirements']!=None:
                        for each_requirement in dtl['requirements']:
                            req_type = int(each_requirement['booking_needed'])
                            if req_type == Travel_requirements.accomodation:
                                accomodation_service = AccomodationBooking_requirement(self._scope())
                                accomodation_service.accomadation_data(each_requirement, user_id, Tourdetaildata.id)
                            elif req_type == Travel_requirements.cab:
                                cab_service = Cab_requirement(self._scope())
                                cab_service.cab_data(each_requirement, user_id, Tourdetaildata.id)
                            elif req_type == Travel_requirements.bus:
                                bus_service = Bus_requirement(self._scope())
                                bus_service.insert_bus_data(each_requirement, user_id, Tourdetaildata.id)
                            elif req_type == Travel_requirements.train:
                                train_service = Train_requirement(self._scope())
                                train_service.Train_data(each_requirement, user_id, Tourdetaildata.id)
                            elif req_type == Travel_requirements.air:
                                air_service = Air_requirement(self._scope())
                                air_service.Air_data(each_requirement, user_id, Tourdetaildata.id)
                            else:
                                error_obj = NWisefinError()
                                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                                error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
                                return error_obj

                        air_required = bool(len(AirBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                            travel_detail_id=Tourdetaildata.id, status=1)))
                        train_required = bool(len(TrainBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                            travel_detail_id=Tourdetaildata.id, status=1)))
                        bus_required = bool(len(BusBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                            travel_detail_id=Tourdetaildata.id, status=1)))
                        cab_required = bool(len(CabBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                            travel_detail_id=Tourdetaildata.id, status=1)))
                        accomodation_required = bool(
                            len(AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                travel_detail_id=Tourdetaildata.id, status=1)))

                        Tourdetaildata = TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                            id=Tourdetaildata.id).update(air_required=air_required,
                                                         train_required=train_required,entity_id=self._entity_id(),
                                                         bus_required=bus_required,
                                                         cab_required=cab_required,
                                                         accomodation_required=accomodation_required
                                                         )

            travel_detail = TourDetail.objects.using(self._current_app_schema()).filter(tour_id=request_obj['id'],entity_id=self._entity_id(),
                                                                                        status=1)
            detail_array = []
            for each_dtl in travel_detail:
                detail_array.append(each_dtl.id)


            rm_approved_tour_edit=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=request_obj['id'],status=Status.APPROVED,
                                                                                    applevel=App_level.FIRST_LEVEL,entity_id=self._entity_id())


            if len(rm_approved_tour_edit)==0:
                air_required_travel = not bool(
                    len(AirBookingInfo.objects.using(self._current_app_schema()).filter(travel_detail_id__in=detail_array,entity_id=self._entity_id(),
                                                                                        status=1)))
                train_required_travel = not bool(len(TrainBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                    travel_detail_id__in=detail_array, status=1)))
                bus_required_travel = not bool(
                    len(BusBookingInfo.objects.using(self._current_app_schema()).filter(travel_detail_id__in=detail_array,entity_id=self._entity_id(),
                                                                                        status=1)))
                cab_required_travel = not bool(
                    len(CabBookingInfo.objects.using(self._current_app_schema()).filter(travel_detail_id__in=detail_array,entity_id=self._entity_id(),
                                                                                        status=1)))
                accomodation_required_travel = not bool(
                    len(AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                        travel_detail_id__in=detail_array, status=1)))

                TourRequestmodel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=request_obj['id']).update(
                    air_status=air_required_travel,
                    train_status=train_required_travel,
                    bus_status=bus_required_travel,entity_id=self._entity_id(),
                    cab_status=cab_required_travel,
                    accomodation_status=accomodation_required_travel
                )

            else:
                air_required_travel =len(AirBookingInfo.objects.using(self._current_app_schema()).filter(travel_detail_id__in=detail_array,entity_id=self._entity_id(),
                                                                                        booking_status=TourRequest_BookingStatus.Not_Booked,status=1))
                train_required_travel = len(TrainBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                    travel_detail_id__in=detail_array, status=1,booking_status=TourRequest_BookingStatus.Not_Booked))
                bus_required_travel = len(BusBookingInfo.objects.using(self._current_app_schema()).filter(travel_detail_id__in=detail_array,entity_id=self._entity_id(),
                                                                                        booking_status=TourRequest_BookingStatus.Not_Booked,status=1))
                cab_required_travel = len(CabBookingInfo.objects.using(self._current_app_schema()).filter(travel_detail_id__in=detail_array,entity_id=self._entity_id(),
                                                                                        booking_status=TourRequest_BookingStatus.Not_Booked,status=1))
                accomodation_required_travel =len(AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                        travel_detail_id__in=detail_array, status=1,booking_status=TourRequest_BookingStatus.Not_Booked))


                if air_required_travel>0:
                    TourRequestmodel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=request_obj['id']).update(
                        air_status=TourRequest_BookingStatus.Not_Booked)
                if train_required_travel > 0:
                    TourRequestmodel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=request_obj['id']).update(
                        train_status=TourRequest_BookingStatus.Not_Booked)
                if bus_required_travel > 0:
                    TourRequestmodel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=request_obj['id']).update(
                        bus_status=TourRequest_BookingStatus.Not_Booked)
                if cab_required_travel > 0:
                    TourRequestmodel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=request_obj['id']).update(
                        cab_status=TourRequest_BookingStatus.Not_Booked)
                if accomodation_required_travel > 0:
                    TourRequestmodel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=request_obj['id']).update(
                        accomodation_status=TourRequest_BookingStatus.Not_Booked)

            approve = TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                     tour_id=request_obj['id'],
                                                                                     request_type=(
                                                                                                 App_type.TOUR or App_type.tour)).last()
            if approve is not None:
                if approve.status == Status.RETURNED:
                    TravelHistory.objects.using(self._current_app_schema()).create(tour_id=request_obj['id'],
                                                                                   approvedby=request_obj['approval'],
                                                                                   applevel=App_level.FIRST_LEVEL,
                                                                                   request_type=App_type.TOUR,
                                                                                   comment="", status=2,
                                                                                   approveddate=time_function.ist_time(),
                                                                                   entity_id=self._entity_id())
                    TourRequestmodel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                      id=request_obj['id']).update(
                        tour_status=Status.PENDING, updated_date=time_function.standard_time())
                # elif approved_tour_edit==True:
                #     TravelHistory.objects.using(self._current_app_schema()).create(tour_id=request_obj['id'],
                #                                                                    approvedby=request_obj['approval'],
                #                                                                    applevel=App_level.FIRST_LEVEL,
                #                                                                    request_type=App_type.TOUR,
                #                                                                    comment="", status=2,
                #                                                                    approveddate=time_function.ist_time(),
                #                                                                    entity_id=self._entity_id())
                #     TourRequestmodel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                #                                                                       id=request_obj['id']).update(
                #         tour_status=Status.PENDING, updated_date=time_function.standard_time())
                else:
                    approver_update = \
                        TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                       tour_id=request_obj['id'],
                                                                                       request_type=App_type.TOUR,
                                                                                       applevel=App_level.FIRST_LEVEL).order_by(
                            '-id')[0]

                    TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                   id=approver_update.id).update(
                        approvedby=request_obj['approval'], approveddate=time_function.ist_time())

                    TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                   request_type=App_type.TOUR,
                                                                                   status=Status.REQUESTED,
                                                                                   tour_id=request_obj['id']).update(
                        comment=tour.get_ordernoremarks(), approveddate=time_function.ist_time())

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
            # except TourRequestmodel.DoesNotExist:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            #     error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
            #     return error_obj
            # except:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj


            data = self.get_tour(request_obj['id'], request)
            data=json.dumps(data, default=lambda o: o.__dict__)
            self.edit_history(data, request_obj['id'], 2, user_id)

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(request_obj['id'])
            return success_obj
            # success_obj = NWisefinSuccess()
            # success_obj.set_status(SuccessStatus.SUCCESS)
            # success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            # return request_obj['id']
        else:
            # try:
            # RM
            request_obj['approval'] = rm_get
            # tour.approval=5
            error_obj = NWisefinError()
            # sd_date = datetime.strptime(tour.get_startdate()[:10], '%Y-%m-%d')
            # ed_date = datetime.strptime(tour.get_enddate()[:10], '%Y-%m-%d')
            sd_date = datetime.strptime(request_obj['startdate'][:10], '%Y-%m-%d')
            ed_date = datetime.strptime(request_obj['enddate'][:10], '%Y-%m-%d')

            dtl_first=request_obj['detail'][0]['startdate']
            dtl_last=request_obj['detail'][-1]['enddate']

            dtl_first_date=datetime.strptime(dtl_first[:10], '%Y-%m-%d')
            dtl_last_date=datetime.strptime(dtl_last[:10], '%Y-%m-%d')

            if dtl_first_date!=sd_date or dtl_last_date!=ed_date:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorMessage.INVALID_DATE_RANGE)
                return error_obj

            for j in range(len((request_obj['detail']))):
                if j!=0:
                    next_detail_start_date=datetime.strptime(request_obj['detail'][j]["startdate"][:10] , '%Y-%m-%d')

                    detail_end_date=datetime.strptime(request_obj['detail'][j-1]["enddate"][:10] , '%Y-%m-%d')

                    if (next_detail_start_date-detail_end_date).days>1:
                        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        error_obj.set_description(ErrorMessage.INVALID_DATE_RANGE)
                        return error_obj




            if (sd_date - ed_date).days > 0:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorMessage.INVALID_DATE)
                return error_obj
            # ist_date=time_function.ist_time()
            # ist_date=datetime.strptime(ist_date, '%Y-%m-%d %H:%M:%S').date()
            # if dtl_sdate.date()<ist_date:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorMessage.INVALID_REQUIREMET_TIME)
            #     return error_obj
            duration_days = (ed_date - sd_date).days
            # sortterm_travel = tour.get_sortterm_travel()
            if int(duration_days)>2 and tour.get_sortterm_travel()==1:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.SHORT_TERM_TRAVEL)
                return error_obj

            # if date_relax_startdate is False:
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorMessage.INVALID_DATE)
            #     return error_obj
            # if date_relax_enddate is False:
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorMessage.INVALID_DATE)
            #     return error_obj
            # onbehalf_obj = Onbehalfrequest(request_obj)
            onbehalf_designation =None
            onbehalf_grade = None
            onbehalf_branchgid = None
            onbehalfof_id = tour.onbehalfof
            if onbehalfof_id > 0:
                if int(onbehalfof_id) == user_id:
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.IN_VALID_ONB)
                    return error_obj
                tour_emp = onbehalfof_id
                tour.onbehalfof = user_id
                api_service=ApiService(self._scope())
                onbehalfof_details=api_service.employee_details_get(tour_emp,request)
                onbehalf_designation = onbehalfof_details.designation
                onbehalf_grade = onbehalfof_details.grade
                onbehalf_branchgid = onbehalfof_details.employee_branch_id


            else:
                tour_emp = user_id

            # if tour.onbehalfof==int(request_obj['permittedby']) or tour_emp==int(request_obj['permittedby']) or int(request_obj['permittedby']) ==0:
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.PERMITTED_BY)
            #     return error_obj
            if tour.onbehalfof == int(request_obj['approval']) or tour_emp == int(request_obj['approval']) or int(
                    request_obj['approval']) == 0:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.APPROVER)
                return error_obj
            validation_service = Validation(self._scope())
            # approver_check=validation_service.approver_validation( App_type.tour,  request_obj['approval'], request)
            # if approver_check is False:
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.APPROVER_NOT_IN_LIST)
            #     return error_obj
            if int(request_obj['reason']) == 0 or int(request_obj['reason']) > 11:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.REASON)
                return error_obj
            scope = request.scope
            emp_ser = TourMaker(scope)
            tour = emp_ser.emp_details_get(tour_emp, tour, request)
            if isinstance(tour, NWisefinError):
                return tour

            requestdate = tour.get_requestdate()
            empgid = tour_emp
            empdesignation = tour.get_empdesignation()
            empgrade = tour.get_empgrade()
            empbranchgid = tour.get_empbranchgid()
            reason = tour.get_reason()
            permittedby = tour.get_permittedby()
            startdate = request_obj['startdate']
            enddate = request_obj['enddate']
            durationdays = tour.get_durationdays()
            ordernoremarks = tour.get_ordernoremarks()
            # status = tour.get_status()
            # eligible_travel_service = Tourno_details(self._scope())
            # eligible_travel = eligible_travel_service.emp_elig_travel(empgrade)
            # eligiblemodeoftravel = eligible_travel.travelclass
            onbehalfof = tour.onbehalfof
            rm_get = api_service.get_RM_ID(request, tour_emp)
            if rm_get == None:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_RM)
                return error_obj
            # request_obj['approvedby'] = rm_get
            approval = rm_get
            apptype = tour.get_apptype()

            # if ordernoremarks is None or ordernoremarks == "":
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.COMMENT)
            #     return error_obj

            duration_days_check = ((ed_date - sd_date).days) + 1
            if duration_days_check != durationdays:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.DURATION_DAYS)
                return error_obj

            emp_dtl_service = ApiService(self._scope())
            bank_account_check = emp_dtl_service.emp_all_details(empgid, request).accountnumber
            if bank_account_check is None:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.NO_BANK_ACCOUNT)
                return error_obj

            quantum_of_funds = tour.get_quantum_of_funds()
            opening_balance = tour.get_opening_balance()
            transfer_on_promotion = tour.get_transfer_on_promotion()
            if reason_id != 2:
                opening_balance = 0
                quantum_of_funds = 0
            transfer_except = [6, 7, 8]
            if reason_id not in transfer_except:
                transfer_on_promotion=0
            if reason_id  in international_travel:
                request_obj['international_travel'] = 1
            else:
                request_obj['international_travel'] = 0

            tour_dtl_validation_ck = self.tour_detail_validation(request_obj['detail'], startdate, enddate, None)
            if isinstance(tour_dtl_validation_ck, NWisefinError):
                return tour_dtl_validation_ck
            for j in range(len((request_obj['detail']))):
                if request_obj['detail'][j]['requirements'] != None:
                    # for i in range(len(request_obj['detail'])):
                    for each_req in request_obj['detail'][j]['requirements']:


                        tour_dtl_validation_ck = self.requirement_validation_create(each_req, request_obj['detail'][j]['startdate'],
                                                                             request_obj['detail'][j]['enddate'])
                        if isinstance(tour_dtl_validation_ck, NWisefinError):
                            return tour_dtl_validation_ck
                    req_id_validation = self.req_id_validation(request_obj['detail'])
                    if req_id_validation != True:
                        return req_id_validation

            # with transaction.atomic():
            if transfer_on_promotion == 1:
                if tour.emp_grade1 is not None:
                    empgrade = tour.emp_grade1
            if 'international_travel' not in request_obj:
                request_obj['international_travel'] = 0
            Tourrequest = TourRequestmodel.objects.using(self._current_app_schema()).create(
                request_date=time_function.ist_time(),
                empgid=empgid,
                empdesignation=empdesignation,
                international_travel=request_obj['international_travel'],
                empgrade=empgrade,
                empbranchgid=empbranchgid,
                reason=reason,
                permittedby=0,
                start_date=startdate[0:10],
                end_date=enddate[0:10],
                week_end_travel=week_end_reason,
                durationdays=duration_days_check,
                remarks=tour.get_ordernoremarks(),
                tour_status=Status.PENDING,
                # sortterm_travel=request_obj['sortterm_travel'],
                # eligiblemodeoftravel=eligiblemodeoftravel,
                onbehalfof=onbehalfof,
                opening_balance=opening_balance,
                transfer_on_promotion=transfer_on_promotion,
                quantum_of_funds=quantum_of_funds,
                sortterm_travel=tour.get_sortterm_travel(),
                non_base_location=non_base_reason,
                created_by=user_id, entity_id=self._entity_id(),onbehalf_designation = onbehalf_designation,
                onbehalf_grade = onbehalf_grade,
                team = tour.team,
                sub_team = tour.sub_team,
                onbehalf_branchgid =onbehalf_branchgid)

        # resp_list = TourMaker()
        # resp_list.set_requestdate(Tourrequest.requestdate)
        # resp_list.set_empgid(Tourrequest.empgid)
        # return resp_list
    #
            Request_last_id = Tourrequest.id
            # TourRequestmodel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=Request_last_id).update(requestno=Request_last_id)

            startdate = startdate[:10]
            sdate = datetime.strptime(startdate, "%Y-%m-%d").date()
            if (time_function.ist_date() - sdate).days >= 90:
                # tourid = TourRequestmodel.objects.using(self._current_app_schema()).all().count()
                # tourid = TourRequestmodel.objects.using(self._current_app_schema()).latest('id').id
                Date_relaxation.objects.using(self._current_app_schema()).create(tour_id=Request_last_id, status=0,created_by=user_id,entity_id=self._entity_id())

            # self.international_travel(request_obj,user_id)


            # if int(request_obj['international_travel']) == 1:
            #     InternationalTravel.objects.using(self._current_app_schema()).create(
            #         tour_id=Request_last_id,
            #         created_by=user_id,
            #         entity_id=self._entity_id()
            #     )

            detail = request_obj['detail']
            # if detail==[]:
            #     transaction.set_rollback(True)
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorMessage.INVALID_DATA)
            #     return error_obj
            # with transaction.atomic():
            for dtl in detail:
                #     dtl_sdate=datetime.strptime(dtl['startdate'][:10], '%Y-%m-%d')
                #     dtl_edate=datetime.strptime(dtl['enddate'][:10], '%Y-%m-%d')


                # if sd_date>dtl_sdate or ed_date<dtl_edate or dtl_edate<dtl_sdate:
                #     transaction.set_rollback(True)
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorMessage.INVALID_DATE)
                #     return error_obj

                # if dtl['startingpoint'] == "" or dtl['placeofvisit'] == "" or dtl['purposeofvisit'] == "":
                #     transaction.set_rollback(True)
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                #     return error_obj
                req=TourDetailRequest(dtl)

                client_value = api_service.get_client(request, dtl['client'])
                if client_value.client_name == "OTHERS":
                    client_name = dtl['other_client_name']
                else:
                    client_name = None

                Tourdetaildata = TourDetail.objects.using(self._current_app_schema()).create(tour_id=Request_last_id,
                                                                                             startdate=dtl['startdate'][0:10],
                                                                                             enddate=dtl['enddate'][0:10],
                                                                                             startingpoint=dtl[
                                                                                                 'startingpoint'],
                                                                                             placeofvisit=dtl[
                                                                                                 'placeofvisit'],
                                                                                             purposeofvisit=dtl[
                                                                                                 'purposeofvisit'],
                                                                                             toplace=None,
                                                                                             client=dtl['client'],
                                                                                             client_name=client_name,
                                                                                             official=req.get_official(),
                                                                                             comments=req.get_comments(),
                                                                                             # booking_needed=dtl['booking_needed'],
                                                                                             created_by=user_id,
                                                                                             entity_id=self._entity_id())
                # travel_req=self.insert_travel_requirements( dtl['requirements'],  Tourdetaildata.id, user_id)
                if dtl['requirements'] != None:
                    for each_requirement in dtl['requirements']:
                        req_type = int(each_requirement['booking_needed'])
                        if req_type == Travel_requirements.accomodation:
                            accomodation_service = AccomodationBooking_requirement(self._scope())
                            accomodation_service.accomadation_data(each_requirement, user_id, Tourdetaildata.id)
                        elif req_type == Travel_requirements.cab:
                            cab_service = Cab_requirement(self._scope())
                            cab_service.cab_data(each_requirement, user_id, Tourdetaildata.id)
                        elif req_type == Travel_requirements.bus:
                            bus_service = Bus_requirement(self._scope())
                            bus_service.insert_bus_data(each_requirement, user_id, Tourdetaildata.id)
                        elif req_type == Travel_requirements.train:
                            train_service = Train_requirement(self._scope())
                            train_service.Train_data(each_requirement, user_id, Tourdetaildata.id)
                        elif req_type == Travel_requirements.air:
                            air_service = Air_requirement(self._scope())
                            air_service.Air_data(each_requirement, user_id, Tourdetaildata.id)
                        else:
                            error_obj = NWisefinError()
                            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                            error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
                            return error_obj

                air_required = bool(len(AirBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                    travel_detail_id=Tourdetaildata.id, status=1)))
                train_required = bool(len(TrainBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                    travel_detail_id=Tourdetaildata.id, status=1)))
                bus_required = bool(len(BusBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                    travel_detail_id=Tourdetaildata.id, status=1)))
                cab_required = bool(len(CabBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                    travel_detail_id=Tourdetaildata.id, status=1)))
                accomodation_required = bool(
                    len(AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                        travel_detail_id=Tourdetaildata.id, status=1)))

                Tourdetaildata = TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                    id=Tourdetaildata.id).update(air_required=air_required,
                                                 train_required=train_required,
                                                 bus_required=bus_required,entity_id=self._entity_id(),
                                                 cab_required=cab_required,
                                                 accomodation_required=accomodation_required
                                                 )

            travel_detail = TourDetail.objects.using(self._current_app_schema()).filter(tour_id=Request_last_id,entity_id=self._entity_id(),
                                                                                        status=1)
            detail_array = []
            for each_dtl in travel_detail:
                detail_array.append(each_dtl.id)
            # air_required_travel=1
            # train_required_travel=1
            # bus_required_travel=1
            # cab_required_travel=1
            # accomodation_required_travel=1



            air_required_travel = not bool(
                len(AirBookingInfo.objects.using(self._current_app_schema()).filter(travel_detail_id__in=detail_array,entity_id=self._entity_id(),
                                                                                    status=1)))
            train_required_travel = not bool(len(TrainBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                travel_detail_id__in=detail_array, status=1)))
            bus_required_travel = not bool(
                len(BusBookingInfo.objects.using(self._current_app_schema()).filter(travel_detail_id__in=detail_array,entity_id=self._entity_id(),
                                                                                    status=1)))
            cab_required_travel = not bool(
                len(CabBookingInfo.objects.using(self._current_app_schema()).filter(travel_detail_id__in=detail_array,entity_id=self._entity_id(),
                                                                                    status=1)))
            accomodation_required_travel = not bool(
                len(AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                    travel_detail_id__in=detail_array, status=1)))

            TourRequestmodel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=Request_last_id).update(
                air_status=air_required_travel,
                train_status=train_required_travel,
                bus_status=bus_required_travel,entity_id=self._entity_id(),
                cab_status=cab_required_travel,
                accomodation_status=accomodation_required_travel
            )

            data = {"tourgid": Request_last_id,
                    "approvedby": user_id,
                    "approveddate": time_function.ist_time(),
                    "apptype": apptype,
                    "applevel": App_level.ZERO_LEVEL,
                    "appcomment": ordernoremarks,
                    "status": Status.REQUESTED}

            req = TourApprovedby.insert_approvedby(self, data, request)
            d = json.loads(req.get())
            if d.get('status') == "success":
                # try:

                data = {"tourgid": Request_last_id,
                        "approvedby": approval,
                        "approveddate": time_function.ist_time(),
                        "apptype": apptype,
                        "applevel": App_level.FIRST_LEVEL,
                        "appcomment": "",
                        "status": Status.PENDING}

                approve = TourApprovedby.insert_approvedby(self, data, request)
                e = json.loads(approve.get())
                if e.get('status') == "success":
                    transaction.on_commit(TourRequestmodel)
                    transaction.on_commit(TourDetail)
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
            #     error_obj.set_description(str(error))
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

            mail_service=ta_email(scope)
            mail_service.mail_data( Request_last_id)



            data=self.get_tour(Request_last_id, request)
            data=json.dumps(data, default=lambda o: o.__dict__)
            self.edit_history(data,Request_last_id,1,user_id)

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(Tourrequest.id)
            return success_obj


    def booked_req_edit_check(self,requirements):
        if "id" in requirements:

            req_type= requirements['booking_needed']
            if int(req_type)==1:
                req_data=AccomodationBookingInfo.objects.using(self._current_app_schema()).get(id=requirements['id'])
                if req_data.booking_status==Requirements_booking_status.booked or req_data.booking_status==Requirements_booking_status.cancelled:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.CANT_EDIT_BOOKED_CANCELLED_REQ)
                    return error_obj
            elif int(req_type)==2:
                req_data=CabBookingInfo.objects.using(self._current_app_schema()).get(id=requirements['id'])
                if req_data.booking_status==Requirements_booking_status.booked or req_data.booking_status==Requirements_booking_status.cancelled:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.CANT_EDIT_BOOKED_CANCELLED_REQ)
                    return error_obj
            elif int(req_type)==3:
                req_data=BusBookingInfo.objects.using(self._current_app_schema()).get(id=requirements['id'])
                if req_data.booking_status==Requirements_booking_status.booked or req_data.booking_status==Requirements_booking_status.cancelled:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.CANT_EDIT_BOOKED_CANCELLED_REQ)
                    return error_obj
            elif int(req_type)==4:
                req_data=TrainBookingInfo.objects.using(self._current_app_schema()).get(id=requirements['id'])
                if req_data.booking_status==Requirements_booking_status.booked or req_data.booking_status==Requirements_booking_status.cancelled:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.CANT_EDIT_BOOKED_CANCELLED_REQ)
                    return error_obj
            elif int(req_type)==5:
                req_data=AirBookingInfo.objects.using(self._current_app_schema()).get(id=requirements['id'])
                if req_data.booking_status==Requirements_booking_status.booked or req_data.booking_status==Requirements_booking_status.cancelled:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.CANT_EDIT_BOOKED_CANCELLED_REQ)
                    return error_obj
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
                return error_obj

            return True





    def previous_dtl_check(self,tourid,sd_date,ed_date,detail_id_arr):

        # day_count=ed_date-sd_date
        # prev_dtl=0
        # for single_date in (sd_date + timedelta(n) for n in range(day_count.days)):
        #     data1= TourDetail.objects.using(self._current_app_schema()).filter(tour_id=tourid,status=1,startdate__lte=single_date).exclude(id__in=detail_id_arr)
        #     data2= TourDetail.objects.using(self._current_app_schema()).filter(tour_id=tourid,status=1,enddate__gte=single_date).exclude(id__in=detail_id_arr)
        #     prev_dtl+=len(data1)+len(data2)
        # return prev_dtl


        data1= TourDetail.objects.using(self._current_app_schema()).filter(tour_id=tourid,status=1,startdate__lt=sd_date).exclude(id__in=detail_id_arr)
        data2= TourDetail.objects.using(self._current_app_schema()).filter(tour_id=tourid,status=1,enddate__gt=ed_date).exclude(id__in=detail_id_arr)
        #
        # data3= TourDetail.objects.using(self._current_app_schema()).filter(tour_id=tourid,status=1,startdate__gte=ed_date,enddate__lte=ed_date).exclude(id__in=detail_id_arr)
        # data4= TourDetail.objects.using(self._current_app_schema()).filter(tour_id=tourid,status=1,startdate__lte=ed_date,enddate__gte=ed_date).exclude(id__in=detail_id_arr)
        return len(data1)+len(data2)

    def prev_accommodation_check(self,detail_id, each_dtl_start_date, each_dtl_end_date,acc_exclude_arr):
        data1=AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(travel_detail_id=detail_id,status=1,
                                                                                       checkin_time__lt=each_dtl_start_date).exclude(id__in=acc_exclude_arr)
        data2=AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(travel_detail_id=detail_id,status=1,
                                                                                       checkout_time__gt=each_dtl_end_date).exclude(id__in=acc_exclude_arr)
        return len(data1) + len(data2)


    def prev_cab_check(self,detail_id, each_dtl_start_date, each_dtl_end_date,acc_exclude_arr):
        data1=CabBookingInfo.objects.using(self._current_app_schema()).filter(travel_detail_id=detail_id,status=1,
                                                                                       from_time__lt=each_dtl_start_date).exclude(id__in=acc_exclude_arr)
        data2=CabBookingInfo.objects.using(self._current_app_schema()).filter(travel_detail_id=detail_id,status=1,
                                                                                       to_time__gt=each_dtl_end_date).exclude(id__in=acc_exclude_arr)
        return len(data1) + len(data2)


    def prev_bus_check(self,detail_id, each_dtl_start_date, each_dtl_end_date,acc_exclude_arr):
        data1=BusBookingInfo.objects.using(self._current_app_schema()).filter(travel_detail_id=detail_id,status=1,
                                                                                       from_time__lt=each_dtl_start_date).exclude(id__in=acc_exclude_arr)
        data2=BusBookingInfo.objects.using(self._current_app_schema()).filter(travel_detail_id=detail_id,status=1,
                                                                                       to_time__gt=each_dtl_end_date).exclude(id__in=acc_exclude_arr)
        return len(data1) + len(data2)


    def prev_train_check(self,detail_id, each_dtl_start_date, each_dtl_end_date,acc_exclude_arr):
        data1=TrainBookingInfo.objects.using(self._current_app_schema()).filter(travel_detail_id=detail_id,status=1,
                                                                                       from_time__lt=each_dtl_start_date).exclude(id__in=acc_exclude_arr)
        data2=TrainBookingInfo.objects.using(self._current_app_schema()).filter(travel_detail_id=detail_id,status=1,
                                                                                       to_time__gt=each_dtl_end_date).exclude(id__in=acc_exclude_arr)
        return len(data1) + len(data2)


    def prev_air_check(self,detail_id, each_dtl_start_date, each_dtl_end_date,acc_exclude_arr):
        data1=AirBookingInfo.objects.using(self._current_app_schema()).filter(travel_detail_id=detail_id,status=1,
                                                                                       from_time__lt=each_dtl_start_date).exclude(id__in=acc_exclude_arr)
        data2=AirBookingInfo.objects.using(self._current_app_schema()).filter(travel_detail_id=detail_id,status=1,
                                                                                       to_time__gt=each_dtl_end_date).exclude(id__in=acc_exclude_arr)
        return len(data1) + len(data2)



    def detail_millisecond(self,detail):
        for each_detail in detail:
            each_detail['startdate'] = str(datetime.fromtimestamp(int(each_detail['startdate']) / 1000.0))
            each_detail['enddate'] = str(datetime.fromtimestamp(int(each_detail['enddate']) / 1000.0))
            for each_req in each_detail['requirements']:
                if 'from_time' in each_req:
                    each_req['from_time'] = str(datetime.fromtimestamp(int(each_req['from_time']) / 1000.0))
                if 'checkin_time' in each_req:
                    each_req['checkin_time'] = str(datetime.fromtimestamp(int(each_req['checkin_time']) / 1000.0))
                if 'to_time' in each_req:
                    each_req['to_time'] = str(datetime.fromtimestamp(int(each_req['to_time']) / 1000.0))
                if 'checkout_time' in each_req:
                    each_req['checkout_time'] = str(datetime.fromtimestamp(int(each_req['checkout_time']) / 1000.0))

    # def requirement_millisecond(self,detail):
    #     for each_detail in detail:
    #         each_detail['from_time'] = datetime.fromtimestamp(int(each_detail['from_time']) / 1000.0)
    #         # each_detail['enddate'] = datetime.fromtimestamp(int(each_detail['enddate']) / 1000.0)
    #
    #         if 'to_time' in each_detail:
    #             each_detail['to_time'] = datetime.fromtimestamp(int(each_detail['to_time']) / 1000.0)
    #         if 'checkout_time' in each_detail:
    #             each_detail['checkout_time'] = datetime.fromtimestamp(int(each_detail['checkout_time']) / 1000.0)
    #             # each_detail['enddate'] = datetime.fromtimestamp(int(each_detail['enddate']) / 1000.0)
    #
    #             # dtl_edate=datetime.strptime(req_array['to_time'][:10], '%Y-%m-%d')
    #             # dtl_edate_time=datetime.strptime(req_array['to_time'], '%Y-%m-%d %H:%M:%S')




    def insert_booking_data(self, data, detailid, emp_id):
        # for each_data in data_array:
        each_data = Booking(data)
        if each_data.id is not None:
            BookingHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                            id=each_data.id).update(
                booking_status=each_data.booking_status,
                booking_time=datetime.now(),
                comments=each_data.comments,
                cancel_reschedule=each_data.cancel_reschedule,
                cancel_reason=each_data.cancel_reason,
                refund_amount=each_data.refund_amount,
                ticket_amount=each_data.ticket_amount,
                refund_date=each_data.refund_date,
                fare_difference=each_data.fare_difference,
                updated_by=emp_id,
                updated_date=datetime.now(),
                entity_id=self._entity_id())
        else:
            BookingHistory.objects.using(self._current_app_schema()).create(
                tourdetail_id=detailid,
                booking_needed=each_data.booking_needed,
                reference_id=each_data.reference_id,
                booking_status=each_data.booking_status,
                booking_time=datetime.now(),
                comments=each_data.comments,
                cancel_reschedule=each_data.cancel_reschedule,
                cancel_reason=each_data.cancel_reason,
                refund_amount=each_data.refund_amount,
                ticket_amount=each_data.ticket_amount,
                refund_date=each_data.refund_date,
                fare_difference=each_data.fare_difference,
                created_by=emp_id,
                entity_id=self._entity_id())
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj

    # def delete_travel_requirement(self,id,employee_id,tour_id):
    #     req_data=TravelRequirements.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),
    #                                                                         id=id)
    #     if int(tour_id)!=req_data.tour_id:
    #         error_obj = NWisefinError()
    #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #         error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
    #         return error_obj
    #     tour_detail_id=req_data.tourdetail_id
    #
    #     TravelRequirements.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
    #                                                                         id=id).update(status=0,updated_by=employee_id,updated_date=time_function.standard_time())
    #     air_required = bool(
    #         len(TravelRequirements.objects.using(self._current_app_schema()).filter(tourdetail_id=tour_detail_id,
    #                                                                                 booking_needed=Travel_requirements.air,status=1)))
    #     train_required = bool(
    #         len(TravelRequirements.objects.using(self._current_app_schema()).filter(tourdetail_id=tour_detail_id,
    #                                                                                 booking_needed=Travel_requirements.train,status=1)))
    #     bus_required = bool(
    #         len(TravelRequirements.objects.using(self._current_app_schema()).filter(tourdetail_id=tour_detail_id,
    #                                                                                 booking_needed=Travel_requirements.bus,status=1)))
    #     cab_required = bool(
    #         len(TravelRequirements.objects.using(self._current_app_schema()).filter(tourdetail_id=tour_detail_id,
    #                                                                                 booking_needed=Travel_requirements.cab,status=1)))
    #     accomodation_required = bool(
    #         len(TravelRequirements.objects.using(self._current_app_schema()).filter(tourdetail_id=tour_detail_id,
    #                                                                                 booking_needed=Travel_requirements.accomodation,status=1)))
    #
    #     Tourdetaildata = TourDetail.objects.using(self._current_app_schema()).filter(id=tour_detail_id).update(
    #         air_required=air_required,
    #         train_required=train_required,
    #         bus_required=bus_required,
    #         cab_required=cab_required,
    #         accomodation_required=accomodation_required
    #         )
    #     success_obj = NWisefinSuccess()
    #     success_obj.set_status(SuccessStatus.SUCCESS)
    #     success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
    #     return success_obj

    def tour_detail_validation(self, dtl_array, start_date, end_date, tour_id):
        try:
            if dtl_array == []:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorMessage.INVALID_DATE)
                return error_obj
        #     if 'to_time' in req_array and req_array['to_time'] is not None:
        #         dtl_edate=datetime.strptime(req_array['to_time'][:10], '%Y-%m-%d')
        #         dtl_edate_time=datetime.strptime(req_array['to_time'], '%Y-%m-%d %H:%M:%S')
        #         if  ed_date < dtl_edate or dtl_edate_time <= dtl_sdate_time:
        #             error_obj = NWisefinError()
        #             error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #             error_obj.set_description(ErrorMessage.INVALID_DATE)
        #             return error_obj
        #
        #     success_obj = NWisefinSuccess()
        #     success_obj.set_status(SuccessStatus.SUCCESS)
        #     return success_obj
        # except:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
        #     return error_obj


            for dtl in dtl_array:
                if tour_id is not None:
                    if "id" in dtl:
                        dtl_tour_id = (
                            TourDetail.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),
                                                                                     id=dtl['id'])).tour_id
                        if dtl_tour_id != int(tour_id):
                            # transaction.set_rollback(True)
                            error_obj = NWisefinError()
                            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                            error_obj.set_description(ErrorDescription.INVALID_ID)
                            return error_obj
                if dtl['startingpoint'] == "" or dtl['placeofvisit'] == "" or dtl['purposeofvisit'] == "":
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_DATA)
                    return error_obj

                if "client" in dtl:
                    if int(dtl['client'])<=0:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        error_obj.set_description(ErrorDescription.INVALID_CLIENT)
                        return error_obj
                else:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_CLIENT)
                    return error_obj

                api_service = ApiService(self._scope())
                client_value = api_service.get_client(None, dtl['client'])
                if client_value.client_name == "OTHERS":
                    client_name = dtl['other_client_name']
                    if client_name is None:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        error_obj.set_description(ErrorDescription.INVALID_OTHER_CLIENT_NAME)
                        return error_obj


                sd_date = datetime.strptime(start_date[:10], '%Y-%m-%d')
                ed_date = datetime.strptime(end_date[:10], '%Y-%m-%d')

                dtl_sdate = datetime.strptime(dtl['startdate'][:10], '%Y-%m-%d')
                dtl_edate = datetime.strptime(dtl['enddate'][:10], '%Y-%m-%d')
                if sd_date > dtl_sdate or ed_date < dtl_edate or dtl_edate < dtl_sdate:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorMessage.INVALID_DATE)
                    return error_obj
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            return success_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
            exc = traceback.format_exc()
            logger.info('ta_ tour_detail_validation- ' + str(e) + str(tour_id)+ str(exc))
            return error_obj

    def requirement_validation_edit(self,req_array,start_date,end_date):
        try:
            # if req_array == []:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorMessage.INVALID_DATA)
            #     return error_obj

    # def requirement_validation_create(self,req_array,start_date,end_date):
    #     try:
    #         # if req_array == []:
    #         #     error_obj = NWisefinError()
    #         #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #         #     error_obj.set_description(ErrorMessage.INVALID_DATA)
    #         #     return error_obj


            # for dtl in req_array:
            # if tour_id is not None:
            #     if "id" in req_array:
            #         dtl_tour_id = (TourDetail.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=req_array['id'])).tour_id
            #         if dtl_tour_id != int(tour_id):
            #             # transaction.set_rollback(True)
            #             error_obj = NWisefinError()
            #             error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #             error_obj.set_description(ErrorDescription.INVALID_ID)
            #             return error_obj
            # if dtl['startingpoint'] == "" or dtl['placeofvisit'] == "" or dtl['purposeofvisit'] == "":
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj

            if int(req_array['booking_needed'])==2:
                if type(int(req_array['travel_type_cab']))!=int:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_CAB_TYPE)
                    return error_obj

            if int(req_array['booking_needed'])==2 and int(req_array['travel_type_cab'])== 1 and req_array['from_time']==None:
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                return success_obj



            sd_date=datetime.strptime(start_date[:10], '%Y-%m-%d')
            ed_date=datetime.strptime(end_date[:10], '%Y-%m-%d')

            if int(req_array['booking_needed'])==1:
                req_array['from_time']=req_array['checkin_time']
                if 'checkout_time' in req_array:
                    req_array['to_time']=req_array['checkout_time']

            dtl_sdate=datetime.strptime(req_array['from_time'][:10], '%Y-%m-%d')
            dtl_sdate_time=datetime.strptime(req_array['from_time'], '%Y-%m-%d %H:%M:%S')
            # dtl_edate=datetime.strptime(req_array['enddate'][:10], '%Y-%m-%d')
            # if sd_date > dtl_sdate or ed_date < dtl_edate or dtl_edate < dtl_sdate:
            if sd_date > dtl_sdate:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_DATE)
                return error_obj
            if ed_date < dtl_sdate:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_DATE)
                return error_obj
            if 'to_time' in req_array and req_array['to_time'] is not None:
                dtl_edate=datetime.strptime(req_array['to_time'][:10], '%Y-%m-%d')
                dtl_edate_time=datetime.strptime(req_array['to_time'], '%Y-%m-%d %H:%M:%S')
                if  ed_date < dtl_edate or dtl_edate_time <= dtl_sdate_time:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorMessage.INVALID_DATE)
                    return error_obj
                if 'id' not in req_array:
                    ist_date = time_function.ist_date()
                    if dtl_edate.date() < ist_date:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        error_obj.set_description(ErrorDescription.INVALID_REQUIREMET_TIME)
                        return error_obj

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            return success_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
            exc=traceback.format_exc()
            logger.info('ta_ requirement_validation_edit- ' + str(e)+str(exc))
            return error_obj

    def requirement_validation_create(self,req_array,start_date,end_date):
        try:
            # if req_array == []:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorMessage.INVALID_DATA)
            #     return error_obj


            # for dtl in req_array:
            # if tour_id is not None:
            #     if "id" in req_array:
            #         dtl_tour_id = (TourDetail.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=req_array['id'])).tour_id
            #         if dtl_tour_id != int(tour_id):
            #             # transaction.set_rollback(True)
            #             error_obj = NWisefinError()
            #             error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #             error_obj.set_description(ErrorDescription.INVALID_ID)
            #             return error_obj
            # if dtl['startingpoint'] == "" or dtl['placeofvisit'] == "" or dtl['purposeofvisit'] == "":
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj


            if int(req_array['booking_needed'])==2:
                if type(int(req_array['travel_type_cab']))!=int:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_CAB_TYPE)
                    return error_obj


            if int(req_array['booking_needed'])==2 and int(req_array['travel_type_cab'])== 1 and req_array['from_time']==None:
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                return success_obj


            sd_date=datetime.strptime(start_date[:10], '%Y-%m-%d')
            ed_date=datetime.strptime(end_date[:10], '%Y-%m-%d')

            if int(req_array['booking_needed'])==1:
                req_array['from_time']=req_array['checkin_time']
                if 'checkout_time' in req_array:
                    req_array['to_time']=req_array['checkout_time']

            dtl_sdate=datetime.strptime(req_array['from_time'][:10], '%Y-%m-%d')
            dtl_sdate_time=datetime.strptime(req_array['from_time'], '%Y-%m-%d %H:%M:%S')
            # dtl_edate=datetime.strptime(req_array['enddate'][:10], '%Y-%m-%d')
            # if sd_date > dtl_sdate or ed_date < dtl_edate or dtl_edate < dtl_sdate:
            if sd_date > dtl_sdate:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_DATE)
                return error_obj
            ist_date=time_function.ist_date()
            if dtl_sdate.date()<ist_date:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_REQUIREMENT_TIME)
                return error_obj
            if 'to_time' in req_array and req_array['to_time'] is not None:
                dtl_edate=datetime.strptime(req_array['to_time'][:10], '%Y-%m-%d')
                dtl_edate_time=datetime.strptime(req_array['to_time'], '%Y-%m-%d %H:%M:%S')
                if  ed_date < dtl_edate or dtl_edate_time <= dtl_sdate_time:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_DATE)
                    return error_obj
                if dtl_edate.date() < ist_date:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_REQUIREMENT_TIME)
                    return error_obj

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            return success_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
            exc = traceback.format_exc()
            logger.info('ta_ requirement_validation_create- ' + str(e) + str(exc))
            return error_obj

    def req_id_validation(self,data_array):
        for each_data in data_array:
            if each_data['requirements']!=None:
                if 'id' in each_data:
                    for each_req in each_data['requirements']:
                        if 'id' in each_req:
                            each_req['booking_needed']=int(each_req['booking_needed'])
                            if each_req['booking_needed']==Travel_requirements.accomodation:
                                acc_service=AccomodationBooking_requirement(self._scope())
                                acc_data=acc_service.get_accomadation(each_req['id'])
                                detail_id=acc_data.data[0].travel_detail
                                if detail_id!=each_data['id']:
                                    error_obj = NWisefinError()
                                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                                    error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
                                    return error_obj
                            elif each_req['booking_needed']==Travel_requirements.cab:
                                cab_service=Cab_requirement(self._scope())
                                cab_data=cab_service.get_cab(each_req['id'])
                                detail_id=cab_data.data[0].travel_detail
                                if detail_id!=each_data['id']:
                                    error_obj = NWisefinError()
                                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                                    error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
                                    return error_obj
                            elif each_req['booking_needed']==Travel_requirements.bus:
                                bus_service=Bus_requirement(self._scope())
                                bus_data=bus_service.get_Bus(each_req['id'])
                                detail_id=bus_data.data[0].travel_detail
                                if detail_id!=each_data['id']:
                                    error_obj = NWisefinError()
                                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                                    error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
                                    return error_obj
                            elif each_req['booking_needed']==Travel_requirements.train:
                                train_service=Train_requirement(self._scope())
                                train_data=train_service.get_Train(each_req['id'])
                                detail_id=train_data.data[0].travel_detail
                                if detail_id!=each_data['id']:
                                    error_obj = NWisefinError()
                                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                                    error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
                                    return error_obj
                            elif each_req['booking_needed']==Travel_requirements.air:
                                air_service=Air_requirement(self._scope())
                                air_data=air_service.get_Air(each_req['id'])
                                detail_id=air_data.data[0].travel_detail
                                if detail_id!=each_data['id']:
                                    error_obj = NWisefinError()
                                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                                    error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
                                    return error_obj
                            else:
                                error_obj = NWisefinError()
                                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                                error_obj.set_description(ErrorDescription.INVALID_REQUIREMENT_ID)
                                return error_obj
                else:
                    for each_req in each_data['requirements']:
                        if 'id' in each_req:
                            error_obj = NWisefinError()
                            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                            error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
                            return error_obj
        return True


    def emp_details_get(self, empid, tour, request):
        employee_apicall = ApiService(self._scope())
        emp = employee_apicall.employee_details_get(empid, request)
        team_data = employee_apicall.emp_teamid_get(empid, request)
        if isinstance(team_data, NWisefinError):
            return team_data
        # emp = Employee.objects.get(id = empid)
        # tour.onbehalfof = emp.id
        # tour.empgid = emp.id
        # emp = emp[0]
        tour.empdesignation = emp.designation
        tour.empgrade = emp.grade
        tour.empbranchgid = emp.employee_branch_id
        tour.team = team_data.team
        tour.sub_team = team_data.sub_team
        # if emp.designation == None:
        #     tour.empdesignation = "OFFICER"
        # if emp.grade == None:
        #     tour.empgrade = "S3"
        # if emp.employee_branch_id == None:
        #     tour.empbranchgid = "471"

        emp_all_details = employee_apicall.emp_all_details(empid, request)
        tour.emp_grade1 = emp_all_details.grade1
        return tour


        # emp = Employee.objects.get(id = empid)
        # # tour.onbehalfof = emp.id
        # # tour.empgid = emp.id
        # tour.empdesignation = emp.designation
        # tour.empgrade = emp.grade
        # tour.empbranchgid = emp.employee_branch_id
        # if emp.designation== None:
        #     tour.empdesignation="OFFICER"
        # if emp.grade== None:
        #     tour.empgrade="S3"
        # if emp.employee_branch_id== None:
        #     tour.empbranchgid="471"
        #
        # # emp_grade1 = Employee.objects.get(id= empid)
        # tour.emp_grade1 = emp.grade1
        # return tour

    # def get_alltour(self, loginemp, onb, vys_page, request_date, tour_no, request):
    #     if request_date != "":
    #         request_date = (datetime.strptime(request_date, '%d-%b-%Y')).date()
    #     if int(onb) > 0:
    #         Tour = TourRequestmodel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
    #                                                                                  empgid=onb, onbehalfof=loginemp,
    #                                                                                  request_date__icontains=request_date,
    #                                                                                  id__icontains=tour_no).all().order_by(
    #             '-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
    #     else:
    #         Tour = TourRequestmodel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
    #                                                                                  empgid=loginemp,
    #                                                                                  request_date__icontains=request_date,
    #                                                                                  id__icontains=tour_no).all().order_by(
    #             '-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
    #
    #     resp_list = NWisefinList()
    #     if len(Tour) > 0:
    #         for tour in Tour:
    #             # reason = TourReason.objects.using(self._current_app_schema()).filter(id=tour.reason)
    #             req_data = TourMakerResponse()
    #             req_data.set_id(tour.id)
    #             # req_data.set_requestno(tour.requestno)
    #             req_data.set_requestdate(tour.request_date)
    #             req_data.set_permittedby_id(tour.permittedby)
    #             req_data.set_empgid(tour.empgid)
    #             empdtl = ApiService(self._scope())
    #             permitted = empdtl.employee_details_get(tour.permittedby, request)
    #             req_data.set_permittedby(permitted.full_name)
    #             employee = empdtl.employee_details_get(tour.empgid, request)
    #             req_data.set_employee_name(employee.full_name)
    #             # code=empdtl.employee_code_get(tour.empgid)
    #             req_data.set_employee_code(employee.code)
    #             req_data.set_empdesignation(tour.empdesignation)
    #             req_data.set_transfer_on_promotion(tour.transfer_on_promotion)
    #             req_data.set_empgrade(tour.empgrade)
    #             req_data.set_empbranchgid(tour.empbranchgid)
    #
    #             approver = TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
    #                                                                                       tour_id=tour.id,
    #                                                                                       request_type=(
    #                                                                                                   App_type.tour or App_type.TOUR),
    #                                                                                       applevel=1).last()
    #             if approver is not None:
    #                 approver_id = approver.approvedby
    #                 approver = empdtl.employee_details_get(approver_id, request)
    #                 # approver_code=empdtl.employee_code_get(approver_id)
    #                 # req_data.set_approver_name(approver_name)
    #                 req_data.set_approver_data(approver_id, approver.full_name, approver.code)
    #             else:
    #                 req_data.set_approver_data(None, None, None)
    #
    #             branch = empdtl.get_branch_data(tour.empbranchgid, request)
    #             req_data.set_branch_name(branch.name)
    #             # brcode = empdtl.get_branch_code(tour.empbranchgid)
    #             req_data.set_branch_code(branch.code)
    #             detail = emp_dtl(self._scope())
    #             reason = detail.get_reason_name(tour.reason)
    #             req_data.set_reason(reason)
    #             req_data.set_reason_id(tour.reason)
    #             req_data.set_quantum_of_funds(tour.quantum_of_funds)
    #             req_data.set_opening_balance(tour.opening_balance)
    #             # req_data.set_reasonname(reason[0].name)
    #             req_data.set_startdate(tour.start_date)
    #             req_data.set_enddate(tour.end_date)
    #             req_data.set_ordernoremarks(tour.remarks)
    #             if tour.onbehalfof > 0:
    #                 onbehalf = empdtl.employee_details_get(tour.onbehalfof, request)
    #                 req_data.set_onbehalfof(onbehalf.full_name)
    #             tour_status = status_get(tour.tour_status)
    #             # advance_status=status_get(tour.advance_status)
    #             claim_status = status_get(tour.claim_status)
    #             req_data.set_tour_status(tour_status)
    #             # req_data.set_advance_status(advance_status)
    #             req_data.set_claim_status(claim_status)
    #             req_data.set_tour_status_id(tour.tour_status)
    #             # req_data.set_advance_status_id(tour.advance_status)
    #             req_data.set_claim_status_id(tour.claim_status)
    #             # req_data.set_air_status(tour.air_status)
    #             # req_data.set_train_status(tour.train_status)
    #             # req_data.set_bus_status(tour.bus_status)
    #             # req_data.set_cab_status(tour.cab_status)
    #             # req_data.set_accomodation_status(tour.accomodation_status)
    #             diffdays = (time_function.ist_date() - tour.end_date.date()).days
    #             req_data.set_is_tour_ended(bool(max(0, diffdays)))
    #             resp_list.append(req_data)
    #         vpage = NWisefinPaginator(Tour, vys_page.get_index(), 10)
    #         resp_list.set_pagination(vpage)
    #     return resp_list

    def nac_get_alltour(self, loginemp, onb, vys_page, request_date, tour_no, request,status,apptype):
        if request_date != "":
            try:
                request_date=int(request_date)
                request_date = str(datetime.fromtimestamp(int(request_date)/1000.0))
                request_date = (datetime.strptime(request_date[:10], '%Y-%m-%d')).date()
            except:
                request_date = (datetime.strptime(request_date, '%d-%b-%Y')).date()

        if apptype is None:
            app_type = [App_type.TOUR, App_type.TourCancel]
        else:
            app_type=[apptype]
        if onb is None:
            condition = Q(tour__empgid=loginemp, tour__request_date__icontains=request_date, tour__id__icontains=tour_no,
                          request_type__in=app_type, status=1, entity_id=self._entity_id())
        elif int(onb) == 0:
            condition = Q(tour__onbehalfof=loginemp, tour__request_date__icontains=request_date,
                          tour__id__icontains=tour_no, request_type__in=app_type, status=1, entity_id=self._entity_id())
        else:
            condition = Q(tour__empgid=onb, tour__onbehalfof=loginemp, tour__request_date__icontains=request_date,
                          tour__id__icontains=tour_no, request_type__in=app_type, status=1, entity_id=self._entity_id())
            # Tour=ApprovedBy.objects.using(DataBase.TA_DB).filter(approvedby=onb, onbehalfof=loginemp,tour__request_date__icontains=request_date,
            #                                                      tour__id__icontains=tour_no,request_type=App_type.TOUR).all().order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]

            # Tour = ApprovedBy.objects.using(DataBase.TA_DB).filter(approvedby=loginemp,
            #                                                        tour__request_date__icontains=request_date,
            #                                                        tour__id__icontains=tour_no,request_type=App_type.TOUR).all().order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]

        if apptype==App_type.TourCancel:
            if status is not None:
                condition &= Q(tour__tour_cancel_status=status)
        else:
            if status is not None:
                condition &= Q(tour__tour_status=status)

        Tour_3 = TravelHistory.objects.using(self._current_app_schema()).filter(condition).values('tour').annotate(
            id=Max('id')).order_by('-tour_id')[
                 vys_page.get_offset():vys_page.get_query_limit()]
        arr_list = []
        for each_tour in Tour_3:
            arr_list.append(each_tour['id'])
        Tour = TravelHistory.objects.using(self._current_app_schema()).filter(id__in=arr_list,
                                                                              entity_id=self._entity_id()).order_by(
            '-tour_id')

        # if int(onb) > 0:
        #     Tour = TourRequestmodel.objects.using(self._current_app_schema()).filter(empgid=onb, onbehalfof=loginemp,request_date__icontains=request_date,id__icontains=tour_no).all().order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        # else:
        #     Tour = TourRequestmodel.objects.using(self._current_app_schema()).filter(empgid=loginemp,request_date__icontains=request_date,id__icontains=tour_no).all().order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]

        resp_list = NWisefinList()
        if len(Tour) > 0:
            for each_tour in Tour:
                # reason = TourReason.objects.using(self._current_app_schema()).filter(id=tour.reason)
                req_data = TourMakerResponse()
                tour = each_tour.tour
                req_data.set_id(tour.id)
                # req_data.set_requestno(tour.requestno)
                req_data.set_apptype(each_tour.request_type)
                req_data.set_requestdate(tour.request_date)
                req_data.set_permittedby_id(tour.permittedby)
                req_data.set_empgid(tour.empgid)
                empdtl = ApiService(self._scope())
                permitted = empdtl.employee_details_get(tour.permittedby, request)
                req_data.set_permittedby(permitted.full_name)
                employee = empdtl.employee_details_get(tour.empgid, request)
                req_data.set_employee_name(employee.full_name)
                # code=empdtl.employee_code_get(tour.empgid)
                req_data.set_employee_code(employee.code)
                req_data.set_empdesignation(tour.empdesignation)
                req_data.set_transfer_on_promotion(tour.transfer_on_promotion)
                req_data.set_empgrade(tour.empgrade)
                req_data.set_empbranchgid(tour.empbranchgid)

                req_data.set_air_status(tour.air_status)
                req_data.set_train_status(tour.train_status)
                req_data.set_bus_status(tour.bus_status)
                req_data.set_cab_status(tour.cab_status)
                req_data.set_accomodation_status(tour.accomodation_status)

                approver = TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tour.id,
                                                                                          request_type=(App_type.tour or App_type.TOUR),
                                                                                          applevel=1,entity_id=self._entity_id()).last()
                latest_tour = TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tour.id,
                                                                                          request_type=App_type.TOUR,
                                                                                          entity_id=self._entity_id()).last()
                latest_applevel=latest_tour.applevel
                if approver is not None:
                    approver_id = approver.approvedby
                    approver_data = empdtl.employee_details_get(approver_id, request)
                    # approver_code=empdtl.employee_code_get(approver_id)
                    # req_data.set_approver_name(approver_name)
                    req_data.set_approver_data(approver_id, approver_data.full_name, approver_data.code)
                    onb_approver_id = approver.onbehalfof_approval
                else:
                    req_data.set_approver_data(None, None, None)
                    onb_approver_id = 0


                approver = empdtl.employee_details_get(onb_approver_id, request)
                req_data.set_onb_approver_data(onb_approver_id, approver.full_name, approver.code)

                # approver_id = approver.approvedby
                # approver = empdtl.employee_details_get(approver_id, request)
                # approver_code=empdtl.employee_code_get(approver_id)
                # req_data.set_approver_name(approver_name)
                # req_data.set_onb_approver_data(approver_id, approver.full_name, approver.code)

                branch = empdtl.get_branch_data(tour.empbranchgid, request)
                req_data.set_branch_name(branch.name)
                # brcode = empdtl.get_branch_code(tour.empbranchgid)
                req_data.set_branch_code(branch.code)
                detail = emp_dtl(self._scope())
                reason = detail.get_reason_name(tour.reason)
                req_data.set_reason(reason)
                req_data.set_reason_id(tour.reason)
                req_data.set_quantum_of_funds(tour.quantum_of_funds)
                req_data.set_opening_balance(tour.opening_balance)
                # req_data.set_reasonname(reason[0].name)
                req_data.set_startdate(tour.start_date)
                req_data.set_enddate(tour.end_date)
                req_data.set_ordernoremarks(tour.remarks)
                if tour.onbehalfof > 0:
                    onbehalf = empdtl.employee_details_get(tour.onbehalfof, request)
                    req_data.set_onbehalfof(onbehalf.full_name)
                    req_data.set_onbehalfof_id(tour.onbehalfof)
                    req_data.set_onbehalfof_code(onbehalf.code)
                tour_status = status_get(tour.tour_status)
                tour_cancel_status = status_get(tour.tour_cancel_status)
                # advance_status = status_get(tour.advance_status)
                claim_status = status_get(tour.claim_status)
                req_data.set_tour_status(tour_status)
                req_data.set_tour_cancel_status(tour_cancel_status)
                # req_data.set_advance_status(advance_status)
                req_data.set_claim_status(claim_status)
                req_data.set_tour_status_id(tour.tour_status)
                req_data.set_tour_cancel_status_id(tour.tour_cancel_status)
                # req_data.set_advance_status_id(tour.advance_status)
                req_data.set_claim_status_id(tour.claim_status)
                diffdays = (time_function.ist_date() - tour.end_date.date()).days
                req_data.set_is_tour_ended(bool(max(0, diffdays)))
                req_data.set_latest_applevel(latest_applevel)
                resp_list.append(req_data)
            vpage = NWisefinPaginator(Tour, vys_page.get_index(), 10)
            resp_list.set_pagination(vpage)
        return resp_list

    def all_tour_report(self,  emp_id, vys_page, request_date, tour_no, request,start_date,end_date):
        if request_date==None:
            request_date=''
        if tour_no==None:
            tour_no=''
        if request_date != "":
            try:
                request_date=int(request_date)
                request_date = str(datetime.fromtimestamp(int(request_date)/1000.0))
                request_date = (datetime.strptime(request_date[:10], '%Y-%m-%d')).date()
            except:
                request_date = (datetime.strptime(request_date, '%d-%b-%Y')).date()

        app_type = [App_type.TOUR, App_type.TourCancel]
        # if onb is None:
        condition = Q( tour__request_date__icontains=request_date, tour__id__icontains=tour_no,
                      request_type__in=app_type, status=1, entity_id=self._entity_id())


        if start_date != None:
            try:
                start_date=int(start_date)
                start_date = str(datetime.fromtimestamp(int(start_date)/1000.0))
                start_date = (datetime.strptime(start_date[:10], '%Y-%m-%d')).date()
            except:
                start_date = (datetime.strptime(start_date, '%d-%b-%Y')).date()

            condition &=Q(tour__start_date__gte=start_date)

        if end_date != None:
            try:
                end_date=int(end_date)
                end_date = str(datetime.fromtimestamp(int(end_date)/1000.0))
                end_date = (datetime.strptime(end_date[:10], '%Y-%m-%d')).date()
            except:
                end_date = (datetime.strptime(end_date, '%d-%b-%Y')).date()

            condition &= Q(tour__end_date__lte=end_date)

        if emp_id is not None:
            condition &= Q(tour__empgid=emp_id)

        # elif int(onb) == 0:
        #     condition = Q(tour__onbehalfof=loginemp, tour__request_date__icontains=request_date,
        #                   tour__id__icontains=tour_no, request_type__in=app_type, status=1, entity_id=self._entity_id())
        # else:
        #     condition = Q(tour__empgid=onb, tour__onbehalfof=loginemp, tour__request_date__icontains=request_date,
        #                   tour__id__icontains=tour_no, request_type__in=app_type, status=1, entity_id=self._entity_id())
            # Tour=ApprovedBy.objects.using(DataBase.TA_DB).filter(approvedby=onb, onbehalfof=loginemp,tour__request_date__icontains=request_date,
            #                                                      tour__id__icontains=tour_no,request_type=App_type.TOUR).all().order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]

            # Tour = ApprovedBy.objects.using(DataBase.TA_DB).filter(approvedby=loginemp,
            #                                                        tour__request_date__icontains=request_date,
            #                                                        tour__id__icontains=tour_no,request_type=App_type.TOUR).all().order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]

        if vys_page is not None:
            Tour_3 = TravelHistory.objects.using(self._current_app_schema()).filter(condition).values('tour').annotate(
                id=Max('id')).order_by('-tour_id')[
                     vys_page.get_offset():vys_page.get_query_limit()]
        else:
            Tour_3 = TravelHistory.objects.using(self._current_app_schema()).filter(condition).values('tour').annotate(
                id=Max('id')).order_by('-tour_id')
        arr_list = []
        for each_tour in Tour_3:
            arr_list.append(each_tour['id'])
        Tour = TravelHistory.objects.using(self._current_app_schema()).filter(id__in=arr_list,
                                                                              entity_id=self._entity_id()).order_by(
            '-tour_id')

        # if int(onb) > 0:
        #     Tour = TourRequestmodel.objects.using(self._current_app_schema()).filter(empgid=onb, onbehalfof=loginemp,request_date__icontains=request_date,id__icontains=tour_no).all().order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        # else:
        #     Tour = TourRequestmodel.objects.using(self._current_app_schema()).filter(empgid=loginemp,request_date__icontains=request_date,id__icontains=tour_no).all().order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]

        resp_list = NWisefinList()
        if len(Tour) > 0:
            for each_tour in Tour:
                # reason = TourReason.objects.using(self._current_app_schema()).filter(id=tour.reason)
                req_data = TourMakerResponse()
                tour = each_tour.tour
                req_data.set_id(tour.id)
                # req_data.set_requestno(tour.requestno)
                req_data.set_apptype(each_tour.request_type)
                req_data.set_requestdate(tour.request_date)
                req_data.set_permittedby_id(tour.permittedby)
                req_data.set_empgid(tour.empgid)
                empdtl = ApiService(self._scope())
                permitted = empdtl.employee_details_get(tour.permittedby, request)
                req_data.set_permittedby(permitted.full_name)
                employee = empdtl.employee_details_get(tour.empgid, request)
                req_data.set_employee_name(employee.full_name)
                # code=empdtl.employee_code_get(tour.empgid)
                req_data.set_employee_code(employee.code)
                req_data.set_empdesignation(tour.empdesignation)
                req_data.set_transfer_on_promotion(tour.transfer_on_promotion)
                req_data.set_empgrade(tour.empgrade)
                req_data.set_empbranchgid(tour.empbranchgid)

                req_data.set_air_status(tour.air_status)
                req_data.set_train_status(tour.train_status)
                req_data.set_bus_status(tour.bus_status)
                req_data.set_cab_status(tour.cab_status)
                req_data.set_accomodation_status(tour.accomodation_status)

                approver = TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tour.id,
                                                                                          request_type=(App_type.tour or App_type.TOUR),
                                                                                          applevel=1,entity_id=self._entity_id()).last()
                latest_tour = TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tour.id,
                                                                                          request_type__in=app_type,
                                                                                          entity_id=self._entity_id()).last()
                latest_applevel=latest_tour.applevel
                if approver is not None:
                    approver_id = approver.approvedby
                    approver_data = empdtl.employee_details_get(approver_id, request)
                    # approver_code=empdtl.employee_code_get(approver_id)
                    # req_data.set_approver_name(approver_name)
                    req_data.set_approver_data(approver_id, approver_data.full_name, approver_data.code)
                    onb_approver_id = approver.onbehalfof_approval
                else:
                    req_data.set_approver_data(None, None, None)
                    onb_approver_id=0


                approver = empdtl.employee_details_get(onb_approver_id, request)
                # approver_code=empdtl.employee_code_get(approver_id)
                # req_data.set_approver_name(approver_name)
                req_data.set_onb_approver_data(onb_approver_id, approver.full_name, approver.code)

                branch = empdtl.get_branch_data(tour.empbranchgid, request)
                req_data.set_branch_name(branch.name)
                # brcode = empdtl.get_branch_code(tour.empbranchgid)
                req_data.set_branch_code(branch.code)
                detail = emp_dtl(self._scope())
                reason = detail.get_reason_name(tour.reason)
                req_data.set_reason(reason)
                req_data.set_reason_id(tour.reason)
                req_data.set_quantum_of_funds(tour.quantum_of_funds)
                req_data.set_opening_balance(tour.opening_balance)
                # req_data.set_reasonname(reason[0].name)
                req_data.set_startdate(tour.start_date)
                req_data.set_enddate(tour.end_date)
                req_data.set_ordernoremarks(tour.remarks)
                if tour.onbehalfof > 0:
                    onbehalf = empdtl.employee_details_get(tour.onbehalfof, request)
                    req_data.set_onbehalfof(onbehalf.full_name)
                tour_status = status_get(tour.tour_status)
                tour_cancel_status = status_get(tour.tour_cancel_status)
                # advance_status = status_get(tour.advance_status)
                claim_status = status_get(tour.claim_status)
                req_data.set_tour_status(tour_status)
                req_data.set_tour_cancel_status(tour_cancel_status)
                # req_data.set_advance_status(advance_status)
                req_data.set_claim_status(claim_status)
                req_data.set_tour_status_id(tour.tour_status)
                req_data.set_tour_cancel_status_id(tour.tour_cancel_status)
                # req_data.set_advance_status_id(tour.advance_status)
                req_data.set_claim_status_id(tour.claim_status)
                diffdays = (time_function.ist_date() - tour.end_date.date()).days
                req_data.set_is_tour_ended(bool(max(0, diffdays)))
                req_data.set_latest_applevel(latest_applevel)

                total_claimed_amount=0
                claimed_amount=ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=tour.id,status=1)
                for each_amount in claimed_amount:
                    total_claimed_amount+=each_amount.claimedamount
                req_data.set_total_claimed_amount(total_claimed_amount)

                dtl_array = []
                travel_detail = TourDetail.objects.using(self._current_app_schema()).filter(tour_id=tour.id,
                                                                                               status=1)
                for each_dtl in travel_detail:
                    dtl_array.append(each_dtl.id)
                total_booked_amount=0
                booked_amount=BookingHistory.objects.using(self._current_app_schema()).filter(tourdetail_id__in=dtl_array,status=1)
                for each_amount in booked_amount:
                    if each_amount.ticket_amount is not None:
                        total_booked_amount+=each_amount.ticket_amount
                req_data.set_total_booked_amount(total_booked_amount)

                latest_approval_tour=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tour.id,
                                                                                          request_type__in=App_type.TOUR,
                                                                                          entity_id=self._entity_id()).last()
                latest_approval_tour_cancel=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tour.id,
                                                                                          request_type__in=App_type.TourCancel,
                                                                                          entity_id=self._entity_id()).last()
                latest_approval_claim=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tour.id,
                                                                                          request_type__in=App_type.CLAIM,
                                                                                          entity_id=self._entity_id()).last()
                if latest_approval_tour is not None:
                    latest_approval_tour = empdtl.employee_details_get(latest_approval_tour.approvedby, request)
                    latest_approval_tour_onb = empdtl.employee_details_get(latest_approval_tour.onbehalfof_approval, request)
                else:
                    latest_approval_tour = empdtl.employee_details_get(0, request)
                    latest_approval_tour_onb = empdtl.employee_details_get(0, request)
                req_data.set_latest_approval_tour(latest_approval_tour)
                req_data.set_latest_approval_tour_onb(latest_approval_tour_onb)

                if latest_approval_tour_cancel is not None:
                    latest_approval_tour_cancel = empdtl.employee_details_get(latest_approval_tour.approvedby, request)
                    latest_approval_tour_cancel_onb = empdtl.employee_details_get(latest_approval_tour.onbehalfof_approval, request)
                else:
                    latest_approval_tour_cancel = empdtl.employee_details_get(0, request)
                    latest_approval_tour_cancel_onb = empdtl.employee_details_get(0, request)
                req_data.set_latest_approval_tour_cancel(latest_approval_tour_cancel)
                req_data.set_latest_approval_tour_cancel_onb(latest_approval_tour_cancel_onb)

                if latest_approval_claim is not None:
                    latest_approval_claim = empdtl.employee_details_get(latest_approval_claim.approvedby, request)
                    latest_approval_claim_onb = empdtl.employee_details_get(latest_approval_claim.onbehalfof_approval, request)
                else:
                    latest_approval_claim = empdtl.employee_details_get(0, request)
                    latest_approval_claim_onb = empdtl.employee_details_get(0, request)
                req_data.set_latest_approval_claim(latest_approval_claim)
                req_data.set_latest_approval_claim_onb(latest_approval_claim_onb)

                team_data=empdtl.emp_team_get(tour.empgid,request)
                req_data.set_team(team_data['team'])
                req_data.set_sub_team(team_data['sub_team'])

                resp_list.append(req_data)
            if vys_page != None:
                vpage = NWisefinPaginator(Tour, vys_page.get_index(), 10)
                resp_list.set_pagination(vpage)
        return resp_list




    def all_tour_report_download(self,  empid, vys_page, request_date, tour_no, request,start_date,end_date):
        # service=Report_ser(self._scope())
        # if all_report is not None:
        #     data=service.get_all_tour_report(tourno,empgid,request)
        # else:
        data=self.all_tour_report(  empid, vys_page, request_date, tour_no, request,start_date,end_date)
        exldata=json.dumps(data, default=lambda o: o.__dict__)
        response_data = pd.read_json(json.dumps(json.loads(exldata)['data']))
        XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response = HttpResponse(content_type=XLSX_MIME)
        response['Content-Disposition'] = 'attachment; filename="Tour_Report.xlsx"'
        writer = pd.ExcelWriter(response, engine='xlsxwriter')
        final_df = response_data[['id','empgid','employee_name','employee_code','team','sub_team','empbranchgid','branch_name','branch_code',
                                  'reason','requestdate','startdate',
                                  'enddate','tour_status','tour_cancel_status','claim_status','accomodation_status_name','cab_status_name','bus_status_name',
                                  'train_status_name','air_status_name']]
        final_df.columns = ['Tour No','Employee id','Employe Name','Employee Code','Team','Sub Team','BranchID','Branch Name','Branch Code',
                            'Tour Reason','Request Date','Start date','End date','Tour status','Tour cancel status',
                            'Claim status','Accomodation status','Cab status','Bus status','Train status','Air status']

        final_df.to_excel(writer, index=False)
        writer.save()
        return HttpResponse(response)


    # claim_amount
    # booked_amount
    # no of req
    # latest_approver

    def get_tour(self, tour_id, request):
        tour = TourRequestmodel.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(), id=tour_id)
        tourdetail = TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                 tour_id=tour_id, status=1).order_by("startdate")
        approve = TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                 tour_id=tour_id,
                                                                                 request_type=Filterapptype.tour).all()
        req_data = TourMakerResponse()
        # reason = TourReason.objects.using(self._current_app_schema()).filter(id=tour.reason)
        req_data.set_id(tour.id)
        req_data.set_transfer_on_promotion(tour.transfer_on_promotion)
        # req_data.set_requestno(tour.requestno)
        req_data.set_requestdate(tour.request_date)
        req_data.set_empgid(tour.empgid)
        empdtl = ApiService(self._scope())
        employee = empdtl.employee_details_get(tour.empgid, request)
        req_data.set_employee_name(employee.full_name)
        # code = empdtl.employee_code_get(tour.empgid)
        req_data.set_employee_code(employee.code)
        req_data.set_empdesignation(tour.empdesignation)
        req_data.set_empgrade(tour.empgrade)
        req_data.set_empbranchgid(tour.empbranchgid)
        req_data.set_sortterm_travel(tour.sortterm_travel)
        req_data.set_non_base_location(tour.non_base_location)

        branch = empdtl.get_branch_data(tour.empbranchgid, request)
        req_data.set_branch_data_maker(branch)
        req_data.set_branch_name(branch.name)
        # brcode = empdtl.get_branch_code(tour.empbranchgid)
        req_data.set_branch_code(branch.code)
        detail = emp_dtl(self._scope())
        reason = detail.get_reason_name(tour.reason)
        req_data.set_reason(reason)
        req_data.set_reason_id(tour.reason)
        req_data.set_reason_data(reason, tour.reason)
        file_required = detail.is_file_required(tour.reason)
        req_data.set_file_required(file_required)
        req_data.set_durationdays(tour.durationdays)
        permittedby = empdtl.employee_details_get(tour.permittedby, request)
        # permittedby_code = empdtl.employee_code_get(tour.permittedby)
        req_data.set_permittedby_id(tour.permittedby)
        req_data.set_permittedby_code(permittedby.code)
        req_data.set_permittedby(permittedby.full_name)
        req_data.set_permitted_by_data(permittedby)
        # req_data.set_reasonname(reason[0].name)

        tour_approver = TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                       tour_id=tour_id, request_type=(
                        App_type.tour or App_type.TOUR), applevel=App_level.FIRST_LEVEL).last()
        if tour_approver is not None:
            tour_app = tour_approver.approvedby
            approvedby = empdtl.employee_details_get(tour_app, request)
            # tour_approver_code = empdtl.employee_code_get(tour_app)
            req_data.set_approver_data(tour_app, approvedby.full_name, approvedby.code)

            ta_api_service = ApiService(self._scope())
            approver_branch_data = ta_api_service.get_branch_data_empid([tour_app], request)
            req_data.set_approver_branch_data(approver_branch_data)

        req_data.set_startdate(tour.start_date)
        req_data.set_enddate(tour.end_date)
        diffdays = (time_function.ist_date() - tour.end_date.date()).days
        req_data.set_is_tour_ended(bool(max(0, diffdays)))
        req_data.set_quantum_of_funds(tour.quantum_of_funds)
        req_data.set_opening_balance(tour.opening_balance)
        req_data.set_ordernoremarks(tour.remarks)
        req_data.set_week_end_travel(tour.week_end_travel)
        if tour.onbehalfof > 0:
            onbehalfof = empdtl.employee_details_get(tour.onbehalfof, request)
            req_data.set_onbehalfof(onbehalfof)
        tour_status = status_get(tour.tour_status)
        advance_status = status_get(tour.advance_status)
        claim_status = status_get(tour.claim_status)
        tour_cancel_status = status_get(tour.tour_cancel_status)
        advance_cancel_status = status_get(tour.advance_cancel_status)
        req_data.set_tour_status(tour_status)
        req_data.set_advance_status(advance_status)
        req_data.set_claim_status(claim_status)
        req_data.set_tour_cancel_status(tour_cancel_status)
        req_data.set_advance_cancel_status(advance_cancel_status)
        req_data.set_tour_status_id(tour.tour_status)
        req_data.set_advance_status_id(tour.advance_status)
        req_data.set_claim_status_id(tour.claim_status)
        req_data.set_tour_cancel_status_id(tour.tour_cancel_status)
        req_data.set_advance_cancel_status_id(tour.advance_cancel_status)
        air_booked_by = empdtl.employee_details_get(tour.air_booked_by, request)
        req_data.set_air_booked_by(air_booked_by)
        train_booked_by = empdtl.employee_details_get(tour.train_booked_by, request)
        req_data.set_train_booked_by(train_booked_by)
        bus_booked_by = empdtl.employee_details_get(tour.bus_booked_by, request)
        req_data.set_bus_booked_by(bus_booked_by)
        cab_booked_by = empdtl.employee_details_get(tour.cab_booked_by, request)
        req_data.set_cab_booked_by(cab_booked_by)
        accomodation_booked_by = empdtl.employee_details_get(tour.accomodation_booked_by, request)
        req_data.set_accomodation_booked_by(accomodation_booked_by)

        if tour.empgid == request.employee_id or tour.onbehalfof == request.employee_id:
            req_data.set_air_status(tour.air_status)
            req_data.set_train_status(tour.train_status)
            req_data.set_bus_status(tour.bus_status)
            req_data.set_cab_status(tour.cab_status)
            req_data.set_accomodation_status(tour.accomodation_status)
        else:
            req_data.set_air_status_checker(tour.air_status)
            req_data.set_train_status_checker(tour.train_status)
            req_data.set_bus_status_checker(tour.bus_status)
            req_data.set_cab_status_checker(tour.cab_status)
            req_data.set_accomodation_status_checker(tour.accomodation_status)

        dtl_list = []
        for dtl in tourdetail:
            tourdtl = TourMakerResponse()
            tourdtl.set_id(dtl.id)
            tourdtl.set_startingpoint(dtl.startingpoint)
            tourdtl.set_placeofvisit(dtl.placeofvisit)
            tourdtl.set_purposeofvisit(dtl.purposeofvisit)
            tourdtl.set_startdate(dtl.startdate)
            tourdtl.set_enddate(dtl.enddate)
            tourdtl.set_status(dtl.status)

            # if dtl.official==0:
            #     tourdtl.set_official("Personal")
            # elif dtl.official==1:
            #     tourdtl.set_official("Official")
            # else:
            tourdtl.set_official(dtl.official)
            tourdtl.set_toplace(dtl.toplace)
            # tourdtl.set_client(dtl.client)
            client_data=empdtl.get_client( request, dtl.client)
            tourdtl.set_client(client_data)
            tourdtl.set_other_client_name(dtl.client_name)
            tourdtl.set_air_required(dtl.air_required)
            tourdtl.set_train_required(dtl.train_required)
            tourdtl.set_bus_required(dtl.bus_required)
            tourdtl.set_cab_required(dtl.cab_required)
            tourdtl.set_accomodation_required(dtl.accomodation_required)
            # requirements=TravelRequirements.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tourdetail_id=dtl.id,status=1)
            # trv_req = []
            # for each_requirements in requirements:
            #     travel_requirements = TourMakerResponse()
            #     travel_requirements.set_id(each_requirements.id)
            #     # travel_requirements.set_tour_id(each_requirements.tour_id)
            #     travel_requirements.set_detail_id(each_requirements.tourdetail_id)
            #     travel_requirements.set_booking_needed(each_requirements.booking_needed)
            #     travel_requirements.set_booking_status(each_requirements.booking_status)
            #     travel_requirements.set_comments(each_requirements.comments)
            #     travel_requirements.set_cancel_reschedule(each_requirements.cancel_reschedule)
            #     travel_requirements.set_cancel_reason(each_requirements.cancel_reason)
            #     travel_requirements.set_refund_amount(each_requirements.refund_amount)
            #     travel_requirements.set_refund_date(each_requirements.refund_date)
            #     travel_requirements.set_fare_difference(each_requirements.fare_difference)
            #     trv_req.append(json.loads(travel_requirements.get()))
            # tourdtl.set_travel_details(trv_req)

            requirement = self.get_all_requirements(dtl.id,request)

            tourdtl.set_requirement(requirement)

            dtl_list.append(json.loads(tourdtl.get()))
        req_data.set_detail(dtl_list)
        apr_list = []
        for apr in approve:
            tour_apr = TourMakerResponse()
            tour_apr.set_id(apr.id)
            tour_apr.set_approvedby_id(apr.approvedby)
            approvedby = empdtl.employee_details_get(apr.approvedby, request)
            # approver_code=empdtl.employee_code_get(apr.approvedby)
            tour_apr.set_approver_code(approvedby.code)
            tour_apr.set_approvedby(approvedby.full_name)
            # tour_apr.set_onbehalfof(apr.onbehalfof)
            tour_apr.set_approveddate(apr.approveddate)
            tour_apr.set_apptype(apr.request_type)
            tour_apr.set_applevel(apr.applevel)
            tour_apr.set_appcomment(apr.comment)
            tour_apr.set_status(apr.status)
            ta_api_service = ApiService(self._scope())
            approver_branch_data = ta_api_service.get_branch_data_empid([apr.approvedby], request)
            tour_apr.set_approver_branch_data(approver_branch_data['branch_name'])
            tour_apr.set_approver_branch_code(approver_branch_data['branch_code'])
            apr_list.append(json.loads(tour_apr.get()))
        req_data.set_approve(apr_list)
        tour_cancel = TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                     request_type=App_type.TourCancel,
                                                                                     tour_id=tour_id,
                                                                                     applevel=App_level.FIRST_LEVEL).last()
        # adv_cancel=TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), request_type=App_type.AdvanceCancel, tour_id=tour_id, applevel=App_level.FIRST_LEVEL).last()
        tour_cancel_maker = TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                           request_type=App_type.TourCancel,
                                                                                           tour_id=tour_id,
                                                                                           applevel=App_level.ZERO_LEVEL).last()
        # adv_cancel_maker=TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), request_type=App_type.AdvanceCancel, tour_id=tour_id, applevel=App_level.ZERO_LEVEL).last()
        if tour_cancel is not None:
            ta_api_service = ApiService(self._scope())
            tour_cancel_data = ta_api_service.get_branch_data_empid([tour_cancel.approvedby], request)
            req_data.set_tour_cancel_approver_data(tour_cancel_data)
            req_data.set_tour_cancel_comment(tour_cancel_maker.comment)
            req_data.set_tour_cancel_approver_comment(tour_cancel.comment)
            tour_cancel_maker_data = empdtl.employee_details_get(tour_cancel_maker.approvedby, request)
            req_data.set_tc_maker(tour_cancel_maker_data)
            # if tour_cancel_maker.onbehalfof > 0:
            #     tour_cancel_maker_data_onb= empdtl.employee_details_get(tour_cancel_maker.onbehalfof, request)
            #     req_data.set_tc_onb(tour_cancel_maker_data_onb)
        # if adv_cancel is not None:
        #     ta_api_service = ApiService(self._scope())
        #     advance_cancel_data = ta_api_service.get_branch_data_empid([adv_cancel.approvedby], request)
        #     req_data.set_advance_cancel_approver_data(advance_cancel_data)
        #     req_data.set_advance_cancel_comment(adv_cancel_maker.comment)
        #     req_data.set_advance_cancel_approver_comment(adv_cancel.comment)
        #     adv_cancel_maker_data= empdtl.employee_details_get(adv_cancel_maker.approvedby, request)
        #     req_data.set_ac_maker(adv_cancel_maker_data)
        #     if adv_cancel_maker.onbehalfof>0:
        #         adv_cancel_maker_data_onb= empdtl.employee_details_get(adv_cancel_maker.onbehalfof, request)
        #         req_data.set_ac_onb(adv_cancel_maker_data_onb)
        return req_data

    # def delete_tour(self,id):
    #     try:
    #         delete = TourRequestmodel.objects.using(self._current_app_schema()).filter(id=id).update(tour_status=Status.DELETED)
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

    # def tourid_data(self,empid,tour_id):
    #     tour = TourRequestmodel.objects.using(self._current_app_schema()).get(id=tour_id, empgid=empid)
    #     tourdetail = TourDetail.objects.using(self._current_app_schema()).filter(tour_id=tour.id).all()
    #     approve = ApprovedBy.objects.using(self._current_app_schema()).filter(tour_id=tour.id,request_type=Filterapptype.tour).all()
    #     req_data = TourMakerResponse()
    #     # reason = TourReason.objects.using(self._current_app_schema()).filter(id=tour.reason)
    #     req_data.set_id(tour.id)
    #     req_data.set_requestno(tour.requestno)
    #     req_data.set_requestdate(tour.requestdate)
    #     req_data.set_empgid(tour.empgid)
    #     empdtl = emp_dtl()
    #     name = empdtl.employee_name_get(tour.empgid)
    #     req_data.set_employee_name(name)
    #     code = empdtl.employee_code_get(tour.empgid)
    #     req_data.set_employee_code(code)
    #     req_data.set_empdesignation(tour.empdesignation)
    #     req_data.set_empgrade(tour.empgrade)
    #     req_data.set_empbranchgid(tour.empbranchgid)
    #
    #     branch = empdtl.get_branch_name(tour.empbranchgid)
    #     req_data.set_branch_name(branch)
    #     brcode = empdtl.get_branch_code(tour.empbranchgid)
    #     req_data.set_branch_code(brcode)
    #
    #     reason = empdtl.get_reason_name(tour.reason)
    #     req_data.set_reason(reason)
    #     req_data.set_reason_id(tour.reason)
    #     # req_data.set_reasonname(reason[0].name)
    #     req_data.set_startdate(tour.startdate)
    #     req_data.set_quantum_of_funds(tour.quantum_of_funds)
    #     req_data.set_opening_balance(tour.opening_balance)
    #     req_data.set_ordernoremarks(tour.ordernoremarks)
    #     if tour.onbehalfof >0:
    #         onbehalfof = empdtl.employee_name_get(tour.onbehalfof)
    #         req_data.set_onbehalfof(onbehalfof)
    #     tour_status = status_get(tour.tour_status)
    #     advance_status = status_get(tour.advance_status)
    #     claim_status = status_get(tour.claim_status)
    #     req_data.set_tour_status(tour_status)
    #     req_data.set_advance_status(advance_status)
    #     req_data.set_claim_status(claim_status)
    #     req_data.set_tour_status_id(tour.tour_status)
    #     req_data.set_advance_status_id(tour.advance_status)
    #     req_data.set_claim_status_id(tour.claim_status)
    #     dtl_list = []
    #     for dtl in tourdetail:
    #         tourdtl = TourMakerResponse()
    #         tourdtl.set_id(dtl.id)
    #         tourdtl.set_startingpoint(dtl.startingpoint)
    #         tourdtl.set_placeofvisit(dtl.placeofvisit)
    #         tourdtl.set_purposeofvisit(dtl.purposeofvisit)
    #         tourdtl.set_startdate(dtl.startdate)
    #         tourdtl.set_enddate(dtl.enddate)
    #         tourdtl.set_status(dtl.status)
    #         dtl_list.append(json.loads(tourdtl.get()))
    #     req_data.set_detail(dtl_list)
    #     apr_list = []
    #     for apr in approve:
    #         tour_apr = TourMakerResponse()
    #         tour_apr.set_id(apr.id)
    #         approvedby=empdtl.employee_name_get(apr.approvedby)
    #         tour_apr.set_approvedby(approvedby)
    #         tour_apr.set_onbehalfof(apr.onbehalfof)
    #         tour_apr.set_approveddate(apr.approveddate)
    #         tour_apr.set_apptype(apr.apptype)
    #         tour_apr.set_applevel(apr.applevel)
    #         tour_apr.set_appcomment(apr.appcomment)
    #         tour_apr.set_status(apr.status)
    #         apr_list.append(json.loads(tour_apr.get()))
    #     req_data.set_approve(apr_list)
    #     return req_data

    def get_tourreason(self, reason,vys_page):
        # if reason == None:
        #     reason=""
        Reason = TourReason.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                             name__icontains=reason,status=1)[
                          vys_page.get_offset():vys_page.get_query_limit()]
        resp_list = NWisefinList()
        for reason in Reason:
            req_data = TourMakerResponse()
            req_data.set_id(reason.id)
            req_data.set_code(reason.code)
            req_data.set_name(reason.name)
            req_data.set_fileupload(reason.fileupload)
            req_data.set_international(reason.international_travel)
            req_data.set_status(reason.status)
            resp_list.append(req_data)
        vpage = NWisefinPaginator(Reason, vys_page.get_index(), 10)
        resp_list.set_pagination(vpage)
        return resp_list
        # return resp_list

    def insert_tourreason(self, request_obj, empid):
        if 'id' in request_obj:
            try:
                reasondata = TourReason.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                         id=request_obj['id']).update(
                    code=request_obj['code'],
                    name=request_obj['name'],
                    status=1,
                    fileupload=request_obj['fileupload'],
                    international_travel=request_obj['international_travel'],
                    updated_by=empid)


            except Exception as e:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(str(e))
                return error_obj
            # except IntegrityError as error:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except TourRequestmodel.DoesNotExist:
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
            try:
                reasondata = TourReason.objects.using(self._current_app_schema()).create(
                    code=request_obj['code'],
                    name=request_obj['name'],
                    status=1,
                    fileupload=request_obj['fileupload'],
                    international_travel=request_obj['international_travel'],
                    created_by=empid, entity_id=self._entity_id())
                reason_id = reasondata.id
                reasondata.code = "TY00" + str(reason_id)
                reasondata.save()


            except Exception as e:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(str(e))
                return error_obj
            # except IntegrityError as error:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            return success_obj

    def update_claim_status(self, id):
        # try:
        Tourrequest = TourRequestmodel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                        id=id).update(
            claim_status=Status.PENDING)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

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


    # def update_advance_status(self,id):
    #     # try:
    #     Tourrequest = TourRequestmodel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=id).update(advance_status=Status.PENDING)
    #     success_obj = NWisefinSuccess()
    #     success_obj.set_status(SuccessStatus.SUCCESS)
    #     success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
    #     return success_obj

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

    def fetch_documents(self, refid, type):
        if type == 0:
            documents = TADocuments.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                     ref_id=refid, status=1)
        else:
            documents = TADocuments.objects.using(self._current_app_schema()).filter(
                Q(entity_id=self._entity_id(), ref_id=refid, status=1, ref_type=type) | Q(ref_id=refid, status=1,
                                                                                          ref_type=3))
        resp_list = []
        for doc in documents:
            doc_resp = TADocumentsResponse()
            doc_resp.set_id(doc.file_id)
            doc_resp.set_file_name(doc.file_name)
            doc_resp.set_ref_id(doc.ref_id)
            doc_resp.set_ref_type(doc.ref_type)
            doc_resp.set_gen_file_name(doc.gen_file_name)
            s3_client = boto3.client('s3', 'ap-south-1')
            response = s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': settings.BUCKET_NAME_FOR_ASSETS,
                                                                'Key': doc.gen_file_name},
                                                        ExpiresIn=None)
            doc_resp.set_url(response)
            resp_list.append(doc_resp)
        return resp_list

    def delete_document(self, file_id, employee_id):
        tour_id = (TADocuments.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),
                                                                             file_id=file_id)).tour_id
        service = Validation(self._scope())
        permission = service.tour_maker_check(tour_id, employee_id)
        if permission is False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.VALID_USER)
            return error_obj
        TADocuments.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                     file_id=file_id).update(status=0)
        msg_obj = NWisefinSuccess()
        msg_obj.set_status(SuccessMessage.DELETE_MESSAGE)
        msg_obj.set_message({"id": file_id})
        return msg_obj

    def tour_status(self, loginemp, type, get_status, request):
        tourdata = TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                  approvedby=loginemp)
        resp_list = NWisefinList()
        for tour_data in tourdata:
            if get_status != None:
                if type == App_type.tour:
                    Tour = TourRequestmodel.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=tour_data.tour_id, tour_status=get_status)
                # elif type==App_type.advance:
                #     Tour = TourRequestmodel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=tour_data.tour_id, advance_status=get_status)
                elif type == App_type.claim:
                    Tour = TourRequestmodel.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=tour_data.tour_id, claim_status=get_status)
            elif get_status == None:
                if type == App_type.tour:
                    Tour = TourRequestmodel.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=tour_data.tour_id)
                elif type == App_type.advance:
                    Tour = TourRequestmodel.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=tour_data.tour_id)
                elif type == App_type.claim:
                    Tour = TourRequestmodel.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=tour_data.tour_id)

            for tour in Tour:
                req_data = TourMakerResponse()
                tour_advance = TourAdvance.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                            tour_id=tour.id)
                adv_amt = 0
                for advance in tour_advance:
                    adv_amt += advance.appamount
                req_data.set_advance_amount(adv_amt)

                req_data.set_id(tour.id)
                # req_data.set_requestno(tour.requestno)
                req_data.set_requestdate(tour.request_date)
                req_data.set_empgid(tour.empgid)
                empdtl = ApiService(self._scope())
                employee = empdtl.employee_details_get(tour.empgid, request)
                req_data.set_employee_name(employee.full_name)
                # code=empdtl.employee_code_get(tour.empgid)
                req_data.set_employee_code(employee.code)
                approvedby = empdtl.employee_details_get(loginemp, request)
                req_data.set_approvedby(approvedby.full_name)
                req_data.set_empdesignation(tour.empdesignation)
                req_data.set_empgrade(tour.empgrade)
                req_data.set_empbranchgid(tour.empbranchgid)

                branch = empdtl.get_branch_data(tour.empbranchgid, request)
                req_data.set_branch_name(branch.name)
                # brcode = empdtl.get_branch_code(tour.empbranchgid)
                req_data.set_branch_code(branch.code)
                detail = emp_dtl(self._scope())
                reason = detail.get_reason_name(tour.reason)
                req_data.set_reason(reason)
                req_data.set_reason_id(tour.reason)
                req_data.set_quantum_of_funds(tour.quantum_of_funds)
                req_data.set_opening_balance(tour.opening_balance)
                req_data.set_startdate(tour.start_date)
                req_data.set_ordernoremarks(tour.remarks)
                req_data.set_onbehalfof(tour.onbehalfof)
                tour_status = status_get(tour.tour_status)
                req_data.set_tour_status(tour_status)
                # advance_status=status_get(tour.advance_status)
                # req_data.set_advance_status(advance_status)
                claim_status = status_get(tour.claim_status)
                req_data.set_claim_status(claim_status)
                resp_list.append(req_data)
        return resp_list

    def ongoing_tour(self, loginemp, onb, vys_page, requestno, requestdate, request):
        # ongoing= TourRequestmodel.objects.using(self._current_app_schema()).get(empgid=emp_id,startdate__gte=today, enddate__lte=today)

        if onb is not None:
            Tour = TourRequestmodel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                     empgid=onb,
                                                                                     start_date__lte=time_function.ist_date(),
                                                                                     end_date__gte=time_function.ist_date(),
                                                                                     onbehalfof=loginemp).all().order_by(
                '-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        else:
            Tour = TourRequestmodel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                     empgid=loginemp,
                                                                                     start_date__lte=time_function.ist_date(),
                                                                                     end_date__gte=time_function.ist_date()).all().order_by(
                '-created_date')[vys_page.get_offset():vys_page.get_query_limit()]

        resp_list = NWisefinList()
        if len(Tour) > 0:
            for tour in Tour:
                # reason = TourReason.objects.using(self._current_app_schema()).filter(id=tour.reason)
                req_data = TourMakerResponse()
                req_data.set_id(tour.id)
                # req_data.set_requestno(tour.requestno)
                req_data.set_requestdate(tour.request_date)
                req_data.set_empgid(tour.empgid)
                empdtl = ApiService(self._scope())
                employee = empdtl.employee_details_get(tour.empgid, request)
                req_data.set_employee_name(employee.full_name)
                # code=empdtl.employee_code_get(tour.empgid)
                req_data.set_employee_code(employee.code)
                req_data.set_empdesignation(tour.empdesignation)
                req_data.set_transfer_on_promotion(tour.transfer_on_promotion)
                req_data.set_empgrade(tour.empgrade)
                req_data.set_empbranchgid(tour.empbranchgid)

                approver = TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                          tour_id=tour.id,
                                                                                          request_type=(
                                                                                                      App_type.tour or App_type.TOUR),
                                                                                          applevel=1).last()
                if approver is not None:
                    approver_id = approver.approvedby
                    approver = empdtl.employee_details_get(approver_id, request)
                    # approver_code=empdtl.employee_code_get(approver_id)
                    # req_data.set_approver_name(approver_name)
                    req_data.set_approver_data(approver_id, approver.full_name, approver.code)

                branch = empdtl.get_branch_data(tour.empbranchgid, request)
                req_data.set_branch_name(branch.name)
                # brcode = empdtl.get_branch_code(tour.empbranchgid)
                req_data.set_branch_code(branch.code)
                detail = emp_dtl(self._scope())
                reason = detail.get_reason_name(tour.reason)
                req_data.set_reason(reason)
                req_data.set_reason_id(tour.reason)
                req_data.set_quantum_of_funds(tour.quantum_of_funds)
                req_data.set_opening_balance(tour.opening_balance)
                # req_data.set_reasonname(reason[0].name)
                req_data.set_startdate(tour.start_date)
                req_data.set_enddate(tour.end_date)
                req_data.set_ordernoremarks(tour.remarks)
                if tour.onbehalfof > 0:
                    onbehalf = empdtl.employee_details_get(tour.onbehalfof, request)
                    req_data.set_onbehalfof(onbehalf.full_name)
                tour_status = status_get(tour.tour_status)
                # advance_status=status_get(tour.advance_status)
                claim_status = status_get(tour.claim_status)
                req_data.set_tour_status(tour_status)
                # req_data.set_advance_status(advance_status)
                req_data.set_claim_status(claim_status)
                req_data.set_tour_status_id(tour.tour_status)
                # req_data.set_advance_status_id(tour.advance_status)
                req_data.set_claim_status_id(tour.claim_status)
                resp_list.append(req_data)
            vpage = NWisefinPaginator(Tour, vys_page.get_index(), 10)
            resp_list.set_pagination(vpage)
        return resp_list

    def forward_data_get(self, emp_id, apptype, vys_page, request):
        resp_list = NWisefinList()
        forward_data = TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                      approvedby=emp_id, applevel=2,
                                                                                      request_type=apptype).all().order_by(
            '-id')[vys_page.get_offset():vys_page.get_query_limit()]
        for data in forward_data:
            req_data = TourMakerResponse()
            tour = data.tour
            req_data.set_id(tour.id)
            # req_data.set_requestno(tour.requestno)
            req_data.set_requestdate(tour.request_date)
            req_data.set_empgid(tour.empgid)
            empdtl = ApiService(self._scope())
            employee = empdtl.employee_details_get(tour.empgid, request)
            req_data.set_employee_name(employee.full_name)
            # code = empdtl.employee_code_get(tour.empgid)
            req_data.set_employee_code(employee.code)
            req_data.set_empdesignation(tour.empdesignation)
            req_data.set_transfer_on_promotion(tour.transfer_on_promotion)
            req_data.set_empgrade(tour.empgrade)
            req_data.set_empbranchgid(tour.empbranchgid)

            approver_id = data.approvedby
            approver = empdtl.employee_details_get(approver_id, request)
            # approver_code = empdtl.employee_code_get(approver_id)
            # req_data.set_approver_name(approver_name)
            req_data.set_approver_data(approver_id, approver.full_name, approver.code)

            branch = empdtl.get_branch_data(tour.empbranchgid, request)
            req_data.set_branch_name(branch.name)
            # brcode = empdtl.get_branch_code(tour.empbranchgid)
            req_data.set_branch_code(branch.code)
            detail = emp_dtl(self._scope())
            reason = detail.get_reason_name(tour.reason)
            req_data.set_reason(reason)
            req_data.set_reason_id(tour.reason)
            req_data.set_quantum_of_funds(tour.quantum_of_funds)
            req_data.set_opening_balance(tour.opening_balance)
            # req_data.set_reasonname(reason[0].name)
            req_data.set_startdate(tour.start_date)
            req_data.set_enddate(tour.end_date)
            req_data.set_ordernoremarks(tour.remarks)
            if tour.onbehalfof > 0:
                onbehalf = empdtl.employee_details_get(tour.onbehalfof, request)
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
            resp_list.append(req_data)
        vpage = NWisefinPaginator(forward_data, vys_page.get_index(), 10)
        resp_list.set_pagination(vpage)

        return resp_list

    # def employee_details_get(self,empid):
    #     emp = Employee.objects.get(id = empid)
    #     req_data = TourMakerResponse()
    #     req_data.set_empgid(emp.id)
    #     req_data.set_employee_name(emp.full_name)
    #     req_data.set_employee_code(emp.code)
    #     req_data.set_empdesignation(emp.designation)
    #     req_data.set_empgrade(emp.grade)
    #     req_data.set_empbranchgid(emp.employee_branch_id)
    #     return req_data

    def change_approver(self, approver_data, request, employee_id):
        error_obj = NWisefinError()
        validation_service = Validation(self._scope())
        logger.info('ta_ Change_approver- ' + str(employee_id) + str(approver_data))
        if approver_data["comment"] == "" or approver_data["comment"] is None:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.COMMENT)
            return error_obj
        if int(approver_data["approver"]) == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorMessage.INVALID_DATA)
            return error_obj
        approved_by_data = TravelHistory.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),
                                                                                       id=approver_data["id"])
        if approved_by_data.status != Status.PENDING:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.NOT_PENDING)
            return error_obj
        if approved_by_data.approvedby == employee_id:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID)
            return error_obj
        if approved_by_data.applevel == App_level.THIRD_LEVEL:
            maker = TravelHistory.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),
                                                                                request_type=App_type.TOUR,
                                                                                applevel=App_level.ZERO_LEVEL,
                                                                                tour_id=approved_by_data.tour_id)
            if employee_id == maker.approvedby:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.MAKER_FORWARDER)
                return error_obj
        status = TourRequestmodel.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),
                                                                                id=approved_by_data.tour_id)
        # comment update validation
        comment = TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                 id__lt=approver_data["id"],
                                                                                 tour_id=approver_data["tour_id"],
                                                                                 request_type=approved_by_data.request_type).last()
        if comment.approvedby != employee_id or comment.approvedby != employee_id:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.CANT_UPDATE_MAKER_COMMENT)
            return error_obj
        if approved_by_data.request_type == App_type.TOUR:
            if status.tour_status == Status.DEFAULT or status.tour_status == Status.APPROVED or status.tour_status == Status.REJECTED or \
                    status.tour_status == Status.RETURNED:
                # if status.tour_status!=Status.PENDING :
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.NOT_PENDING)
                return error_obj
            # approver_check = validation_service.approver_validation(App_type.tour, approver_data["approver"], request)
            # if approver_check is False:
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.APPROVER_NOT_IN_LIST)
            #     return error_obj
        elif approved_by_data.request_type == App_type.CLAIM:
            if status.claim_status != Status.PENDING:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.NOT_PENDING)
                return error_obj
            # approver_check = validation_service.approver_validation(App_type.expense, approver_data["approver"],
            #                                                         request)
            # if approver_check is False:
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.APPROVER_NOT_IN_LIST)
            #     return error_obj
        elif approved_by_data.request_type == App_type.TourCancel:
            if status.tour_cancel_status != Status.PENDING:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.NOT_PENDING)
                return error_obj
            # approver_check = validation_service.approver_validation(App_type.tour, approver_data["approver"], request)
            # if approver_check is False:
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.APPROVER_NOT_IN_LIST)
            #     return error_obj
            # elif approved_by_data.request_type==App_type.AdvanceCancel:
            #     if status.advance_cancel_status!=Status.PENDING:
            #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #         error_obj.set_description(ErrorDescription.NOT_PENDING)
            #         return error_obj
            # approver_check = validation_service.approver_validation(App_type.advance, approver_data["approver"],
            #                                                         request)
            # if approver_check is False:
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.APPROVER_NOT_IN_LIST)
            #     return error_obj

        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorMessage.INVALID_DATA)
            return error_obj
        TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), id=comment.id).update(
            comment=approver_data["comment"])
        TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), id=approver_data["id"]).update(approvedby=approver_data["approver"])
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj

    # def change_maker_comment(self,approver_data):
    #     request_type=(approver_data['apptype']).upper()
    #     status = TourRequestmodel.objects.using(self._current_app_schema()).get(id=approver_data['tour_id'])
    #     if apptype == App_type.CLAIM:
    #         if status.claim_status != Status.PENDING:
    #             error_obj = NWisefinError()
    #             error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #             error_obj.set_description(ErrorDescription.NOT_PENDING)
    #             return error_obj
    #     elif apptype == App_type.TourCancel.upper():
    #         if status.tour_cancel_status != Status.PENDING:
    #             error_obj = NWisefinError()
    #             error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #             error_obj.set_description(ErrorDescription.NOT_PENDING)
    #             return error_obj
    #     elif apptype == App_type.AdvanceCancel.upper():
    #         if status.advance_cancel_status != Status.PENDING:
    #             error_obj = NWisefinError()
    #             error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #             error_obj.set_description(ErrorDescription.NOT_PENDING)
    #             return error_obj
    #     else:
    #         error_obj = NWisefinError()
    #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #         error_obj.set_description(ErrorMessage.INVALID_DATA)
    #         return error_obj
    #     approved_by_data=ApprovedBy.objects.using(self._current_app_schema()).filter(tour_id=approver_data['tour_id'],applevel=App_level.ZERO_LEVEL,
    #                                                     request_type=approver_data['apptype'],status=Status.REQUESTED).last()
    #     ApprovedBy.objects.using(self._current_app_schema()).filter(id=approved_by_data.id).update(appcomment=approver_data["comment"])
    #     success_obj = NWisefinSuccess()
    #     success_obj.set_status(SuccessStatus.SUCCESS)
    #     success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
    #     return success_obj
    def delete_tour_details(self,id,employee_id,request):
        logger.info(str(id) +'ta_ delete_tour_details- ' +  str(employee_id))
        time_function=Timecalculation()
        detail_data = TourDetail.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),
                                                                                     id=id)
        tour_details = TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=detail_data.tour_id )
        if len(tour_details)==1:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.CANT_DELETE_LAST_ITENARY)
            return error_obj


        booked_req_delete_validation=self.booked_req_delete_validation(id)
        if booked_req_delete_validation==False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.CANT_DELETE_BOOKED_REQ)
            return error_obj


        details_delete=TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=id).update(status=0 ,updated_by=employee_id,updated_date=time_function.standard_time())
        detail_id=id
        tour_id=detail_data.tour.id
        tour_detail_array = []
        dtl_data=TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), tour=tour_id)
        for each_dtl in dtl_data:
            tour_detail_array.append(each_dtl.id)


        AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(), travel_detail_id=detail_id).update(status=0)
        accomodation_len = AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(), travel_detail_id__in=tour_detail_array, status=1)
        if len(accomodation_len) == 0:
            TourRequestmodel.objects.using(self._current_app_schema()).filter(id=tour_id).update(accomodation_status=1)

        CabBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(), travel_detail_id=detail_id).update(status=0)
        cab_len = CabBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(), travel_detail_id__in=tour_detail_array, status=1)
        if len(cab_len) == 0:
            TourRequestmodel.objects.using(self._current_app_schema()).filter(id=tour_id).update(cab_status=1)

        BusBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(), travel_detail_id=detail_id).update(status=0)
        bus_len = BusBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(), travel_detail_id__in=tour_detail_array, status=1)
        if len(bus_len) == 0:
            TourRequestmodel.objects.using(self._current_app_schema()).filter(id=tour_id).update(bus_status=1)

        TrainBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(), travel_detail_id=detail_id).update(status=0)
        train_len = TrainBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(), travel_detail_id__in=tour_detail_array, status=1)
        if len(train_len) == 0:
            TourRequestmodel.objects.using(self._current_app_schema()).filter(id=tour_id).update(train_status=1)

        AirBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(), travel_detail_id=detail_id).update(status=0)
        air_len = AirBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(), travel_detail_id__in=tour_detail_array, status=1)
        if len(air_len) == 0:
            TourRequestmodel.objects.using(self._current_app_schema()).filter(id=tour_id).update(air_status=1)


        data = self.get_tour(tour_id, request)
        data=json.dumps(data, default=lambda o: o.__dict__)
        self.edit_history(data, tour_id, 3, employee_id)




        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj


    def booked_req_delete_validation(self,detail_id):

        booked_data_acc=AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(), travel_detail_id=detail_id,booking_status = Requirements_booking_status.booked)

        booked_data_cab=CabBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(), travel_detail_id=detail_id,booking_status = Requirements_booking_status.booked)

        booked_data_bus=BusBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(), travel_detail_id=detail_id,booking_status = Requirements_booking_status.booked)

        booked_data_train=TrainBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(), travel_detail_id=detail_id,booking_status = Requirements_booking_status.booked)

        booked_data_air=AirBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(), travel_detail_id=detail_id,booking_status = Requirements_booking_status.booked)
        if len(booked_data_acc) or len(booked_data_cab) or len(booked_data_bus) or len(booked_data_train) or len(booked_data_air)> 0:
            return False
        else:
            return True




    def tourid_get_detail_id(self,detail_id):
        data=TourDetail.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=detail_id)
        return data.tour_id

    def request_comment_chat(self,request,body_data,employee_id):

        data = Chat_Box(body_data)
        logger.info('ta_ request_comment_chat- ' + str(employee_id) + str(body_data))
        time=Timecalculation()
        ist=time.ist_time()

        if data.get_id() is not None:
            employeeid = TransactionComments.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=data.get_id())
            if employee_id == employeeid.maker_id:
                requester_comment = TransactionComments.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                    id=data.get_id()).update(request_id=data.get_request(), maker_id=employee_id,
                                             ref_type=data.get_ref_type(), viewer_id=employee_id,
                                             comment=data.get_comment(), type=data.get_type(), status=1,entity_id=self._entity_id(),
                                             updated_by=employee_id, updated_date=ist)
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                return success_obj
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.COMMENT)
                return error_obj
        else:
            requester_comment = TransactionComments.objects.using(self._current_app_schema()).create(
                request_id=data.get_request(), maker_id=employee_id, ref_type=data.get_ref_type(),
                viewer_id=employee_id, comment=data.get_comment(), type=data.get_type(), status=1,
                created_by=employee_id, created_date=ist, entity_id=self._entity_id())
            request_table=TourRequestmodel.objects.using(self._current_app_schema()).get(id=data.get_request())
            # travel_his=TravelHistory.objects.using(self._current_app_schema()).get(tour_id=data.get_request(),applevel=App_level.FIRST_LEVEL)
            #
            # if int(request_table.empgid)!=int(employee_id):
            #     #admin=236
            #     # RM=travel_his.approvedby
            #     pass

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            return success_obj

    def  chats(self, tourid, employee_id, vys_page, request):
        resp_list = NWisefinList()
        # array=[employee_id,approver_id]
        # maker_id__in=array,approver_id__in=array
        chats_get = TransactionComments.objects.using(self._current_app_schema()).filter(status=1, request_id=tourid,
                                                                                         entity_id=self._entity_id()).order_by("-id")
        emp_name = ApiService(self._scope())
        arr=[]
        for datas in chats_get:
            b= (datas.viewer_id.split(','))
            if str(employee_id) not in b:
                arr.append(datas.id)
        chats_get = TransactionComments.objects.using(self._current_app_schema()).filter(request_id=tourid,
                                                                                         entity_id=self._entity_id()).order_by(
            "-id")[
                    vys_page.get_offset():vys_page.get_query_limit()]
        for data in chats_get:
            emp_name_get = emp_name.employee_details_get(data.maker_id, request)
            req_data = Chatbox_response()
            req_data.set_chatid(data.id)
            req_data.set_id(data.request_id)
            req_data.set_employee_name(emp_name_get.full_name)
            req_data.set_employee_code(emp_name_get.code)
            # req_data.set_type(data.type)
            req_data.set_maker_id(data.maker_id)
            # req_data.set_ref_type(data.ref_type)
            # req_data.set_approver_id(data.approver_id)

            is_maker = 0
            if data.maker_id == employee_id:
                is_maker = 1
            req_data.set_is_maker(is_maker)
            req_data.set_created_date(data.created_date)
            req_data.set_updated_date(data.updated_date)
            if data.status==0:
                req_data.set_status(data.status)
                req_data.set_comment("THIS MESSAGE WAS DELETED")
            else:
                req_data.set_status(data.status)
                req_data.set_comment(data.comment)
            req_data.set_tour_status(data.request.tour_status)
            req_data.set_unread_message(len(arr))
            resp_list.append(req_data)
        vpage = NWisefinPaginator(chats_get, vys_page.get_index(), 10)
        resp_list.set_pagination(vpage)

        return resp_list
    def chat_view(self,request,tour_id,employeeid):
        try:
            chats_get = TransactionComments.objects.using(self._current_app_schema()).filter(status=1, request_id=tour_id,
                                                                                             entity_id=self._entity_id())
            emp_name = ApiService(self._scope())
            arr = []
            for datas in chats_get:
                b = (datas.viewer_id.split(','))
                if str(employeeid) not in b:
                    arr.append(datas.id)
                    chat_up=TransactionComments.objects.using(self._current_app_schema()).filter(id=datas.id,entity_id=self._entity_id()).update(viewer_id=str(datas.viewer_id)+","+str(employeeid))
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            return success_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj

    def chat_summary(self,request,employeeid,option,created_pending,vys_page):
        arr = []
        resp_list=NWisefinList()
        module_permission = ApiService(self._scope())
        condition=Q(entity_id=self._entity_id(),status=1)
        # if created_pending=="createdbyme":
        #     condition&=~Q(maker_id=employeeid)
        #     condition&=Q(request__empgid=employeeid)
        module_permission = ApiService(self._scope())
        role_arr = module_permission.employee_modulerole_get(employeeid, ModuleList.Ta_eclaim, request)
        ceo_get = module_permission.onb_permission(request, employeeid)

        if RoleList.admin in role_arr:
            # emp_arr = module_permission.get_rm_emp(request, employeeid)
            condition &= Q(request__tour_status__in=[Status.APPROVED])
            condition &= ~Q(request__claim_status__in=[Status.APPROVED])
            condition &= ~Q(maker_id=employeeid)
            # condition &= Q(request__empgid=employeeid)
        elif (json.loads(ceo_get))["ceo"]==True:
            condition &= ~Q(maker_id=employeeid)
            condition &= ~Q(request__claim_status__in=[Status.APPROVED])
            condition &= Q(request__empgid=employeeid)| Q(request__reason__in=[9,10])
        else:
            emp_arr=module_permission.get_rm_emp(request,employeeid)
            condition&=Q(request__tour_status__in = [Status.PENDING, Status.REQUESTED, Status.RETURNED, Status.DEFAULT,Status.APPROVED])
            condition&=~Q(request__claim_status__in=[Status.APPROVED])
            condition&=~Q(maker_id=employeeid)
            emp_arr.append(employeeid)
            condition&=Q(request__empgid__in=emp_arr)


        module_permission=ApiService(self._scope())
        role_arr = module_permission.employee_modulerole_get(employeeid, ModuleList.Ta_eclaim, request)
        # ceo_get = module_permission.onb_permission(request, employee_id)
        # if RoleList.admin not in role_arr:


        tour_req=TransactionComments.objects.using(self._current_app_schema()).filter(condition).values('request_id').annotate(id=Max('id')).order_by("-id")
        print(tour_req)
        from utilityservice.data.response.nwisefinpage import NWisefinPage
        new_arr=[]

        for i in tour_req:
            chat_sum = self.chats(i["request_id"], employeeid,NWisefinPage(1, 1), request)
            if len(json.loads(chat_sum.get())["data"])!=0:
                if json.loads(chat_sum.get())["data"][0]["unread_message"]!=0:
                    new_arr.append(json.loads(chat_sum.get())["data"][0]["chatid"])
                    arr.append(json.loads(chat_sum.get())["data"][0]["unread_message"])
        dict = {}

        tour_req=TransactionComments.objects.using(self._current_app_schema()).filter(id__in=new_arr).values('request_id').order_by("-id")[vys_page.get_offset():vys_page.get_query_limit()]
        arr=arr[vys_page.get_offset():vys_page.get_query_limit()]
        if len(arr)!=0 and len(arr)>10:
            arr.pop()
        vpage = NWisefinPaginator(tour_req, vys_page.get_index(), 10)
        resp_list.set_pagination(vpage)
        for data in tour_req:

            chat_sum=self.chats(data["request_id"], employeeid,NWisefinPage(1,1), request)
            dict["Tour id"] = data["request_id"]
            if len(json.loads(chat_sum.get())["data"])!=0:
                dict["Chats"] = json.loads(chat_sum.get())["data"][0]
            else:
                dict["Chats"] = json.loads(chat_sum.get())["data"]
            dict["no_of_chats"]=len(arr)
            dict["no_of_unreadmessage"]=sum(arr)
            resp_list.append(json.loads(json.dumps(dict)))

        vpage = NWisefinPaginator(tour_req, vys_page.get_index(), 10)
        resp_list.set_pagination(vpage)
        return resp_list


    def dele_chat(self, employeeid, tour_id, chatid):
        try:
            dele_chat = TransactionComments.objects.using(self._current_app_schema()).filter(id=chatid, request=tour_id,entity_id=self._entity_id(),
                                                                                             maker_id=employeeid).update(
                status=0)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj
    def undo_chat_box(self, employeeid, tour_id, chatid,request):
        try:
            update_status = TransactionComments.objects.using(self._current_app_schema()).filter(id=chatid, request=tour_id,entity_id=self._entity_id(),
                                                                                             maker_id=employeeid).update(
                status=1)
            undo_chat_box = TransactionComments.objects.using(self._current_app_schema()).get(id=chatid,
                                                                                              request=tour_id,
                                                                                              entity_id=self._entity_id(),
                                                                                              maker_id=employeeid)
            resp_list = NWisefinList()
            emp_name = ApiService(self._scope())
            emp_name_get = emp_name.employee_details_get(undo_chat_box.maker_id, request)
            req_data = Chatbox_response()
            req_data.set_chatid(undo_chat_box.id)
            req_data.set_id(undo_chat_box.request_id)
            req_data.set_employee_name(emp_name_get.full_name)
            req_data.set_employee_code(emp_name_get.code)
            # req_data.set_type(data.type)
            req_data.set_maker_id(undo_chat_box.maker_id)
            # req_data.set_ref_type(data.ref_type)
            # req_data.set_approver_id(data.approver_id)

            is_maker = 0
            if undo_chat_box.maker_id == employeeid:
                is_maker = 1
            req_data.set_is_maker(is_maker)
            req_data.set_created_date(undo_chat_box.created_date)
            req_data.set_updated_date(undo_chat_box.updated_date)
            if undo_chat_box.status == 0:
                req_data.set_status(undo_chat_box.status)
                req_data.set_comment("THIS MESSAGE IS DELETED")
            else:
                req_data.set_status(undo_chat_box.status)
                req_data.set_comment(undo_chat_box.comment)
            req_data.set_tour_status(undo_chat_box.request.tour_status)
            # req_data.set_unread_message(len(arr))
            resp_list.append(req_data)



            return resp_list

        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj
    def approvedby_empget(self, tour_id):
        try:
            approvedby_get = TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=tour_id)
            resp_list = NWisefinList()
            for data in approvedby_get:
                req_data = Chatbox_response()
                req_data.set_approveredby_id(data.approvedby)
                resp_list.append(req_data)
            return resp_list
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj

    # def insert_doc(self, data_body, employee_id):
    #     data = Doc_type(data_body)
    #     if data.get_id() is None:
    #         insert_doc = Document_type.objects.using(self._current_app_schema()).create(file_type=data.get_file_type(),
    #                                                                                     file_name=data.get_file_name(),
    #                                                                                     description=data.get_description(),
    #                                                                                     entity_id=self._entity_id(),
    #                                                                                     created_by=employee_id,
    #                                                                                     created_date=datetime.now())
    #         get_id = insert_doc.id
    #         code = "DOC0" + str(get_id)
    #         update_code = Document_type.objects.using(self._current_app_schema()).filter(id=get_id).update(code=code)
    #         success_obj = NWisefinSuccess()
    #         success_obj.set_status(SuccessStatus.SUCCESS)
    #         success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
    #         return success_obj
    #     else:
    #         update_doc = Document_type.objects.using(self._current_app_schema()).filter(id=data.get_id()).update(
    #             file_type=data.get_file_type(), file_name=data.get_file_name(), description=data.get_description(),
    #             entity_id=self._entity_id(), updated_by=employee_id, updated_date=datetime.now())
    #         success_obj = NWisefinSuccess()
    #         success_obj.set_status(SuccessStatus.SUCCESS)
    #         success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
    #         return success_obj

    # def insert_tadoc(self, request, data):
    #     try:
    #         vysfinservice = ApiService(self._scope())
    #         employee_id = request.employee_id
    #         # tour_id = data['tour_id']
    #         # is_maker = data['is_maker']
    #         # ref_type = data['ref_type']
    #         # detail_id = data['detail_id']
    #         # requirement_type = data['requirement_type']
    #         # requirement_id = data['requirement_id']
    #
    #         req_data=Document_upload(data)
    #         tour_id=req_data.get_tour_id()
    #         detail_id=0
    #         is_maker=0
    #         reqirement=0
    #
    #         if req_data.get_tour_id() ==None:
    #             detailid_get=None
    #             if req_data.get_requirement_type() == Travel_requirements.accomodation:
    #                 detailid_get = AccomodationBookingDetails.objects.using(self._current_app_schema()).get(
    #                     entity_id=self._entity_id(), id=req_data.get_requirement_id())
    #
    #             elif req_data.get_requirement_type() == Travel_requirements.cab:
    #                 detailid_get = CabBookingDetails.objects.using(self._current_app_schema()).get(
    #                     entity_id=self._entity_id(), id=req_data.get_requirement_id())
    #             elif req_data.get_requirement_type()== Travel_requirements.bus:
    #                 detailid_get = BusBookingDetails.objects.using(self._current_app_schema()).get(
    #                     entity_id=self._entity_id(), id=req_data.get_requirement_id())
    #             elif req_data.get_requirement_type() == Travel_requirements.train:
    #                 detailid_get = TrainBookingDetails.objects.using(self._current_app_schema()).get(
    #                     entity_id=self._entity_id(), id=req_data.get_requirement_id())
    #             elif req_data.get_requirement_type() == Travel_requirements.air:
    #                 detailid_get = AirBookingDetails.objects.using(self._current_app_schema()).get(
    #                     entity_id=self._entity_id(), id=req_data.get_requirement_id())
    #             detail_id = detailid_get.travel_detail_id
    #             tour_id=detailid_get.travel_detail.tour.id
    #             is_maker=1
    #             reqirement=req_data.get_requirement_id()
    #
    #         if req_data.get_ref_type()==TADocUtil.CLAIM:
    #             is_maker=0
    #             reqirement = req_data.get_requirement_id()
    #             # if req_data.get_requirement_type()==EXPENSE_ID.Travelling:
    #             #     reqirement=req_data.get_requirement_id()
    #             # elif req_data.get_requirement_type()==EXPENSE_ID.AssociatedExpense:
    #             #     reqirement=req_data.get_requirement_id()
    #             # elif req_data.get_requirement_type()==EXPENSE_ID.Lodging:
    #             #     reqirement=req_data.get_requirement_id()
    #             # elif req_data.get_requirement_type()==EXPENSE_ID.DailyDiem:
    #             #     reqirement=req_data.get_requirement_id()
    #             # elif req_data.get_requirement_type()==EXPENSE_ID.LocalConveyance:
    #             #     reqirement=req_data.get_requirement_id()
    #             # else:
    #             #     requirement_type=
    #
    #
    #
    #         if len(request.FILES) != 0:
    #             docmodule_obj = DocModule()
    #             params = {}
    #             params['module'] = docmodule_obj.TA
    #             params['ref_id'] = tour_id
    #             params['ref_type'] = docmodule_obj.TA
    #
    #             doc_module = docmodule_obj.TA
    #
    #             response_obj = vysfinservice.ta_doc_upload(request, params)
    #             docmnts_json = response_obj.get()
    #             docmnts_json = json.loads(docmnts_json)
    #             for doc_data in docmnts_json['data']:
    #                 ta_doc = TADocuments.objects.using(self._current_app_schema()).create(file_id=doc_data['id'],
    #                                                                                       entity_id=self._entity_id(),
    #                                                                                       ref_id=tour_id,
    #                                                                                       request_id=tour_id,
    #                                                                                       ref_type=req_data.get_ref_type(),
    #                                                                                       file_name=doc_data['file_name'],
    #                                                                                       gen_file_name=doc_data[
    #                                                                                           'gen_file_name'],
    #                                                                                       maker_or_admin=is_maker,
    #                                                                                       created_by=employee_id,
    #                                                                                       detail=detail_id,
    #                                                                                       requirement_type=req_data.get_requirement_type(),
    #                                                                                       requirement=reqirement)
    #                 # ta_doc.file_id = doc_data['id']
    #                 # ta_doc.ref_id = tour_id
    #                 # ta_doc.request_id = tour_id
    #                 # ta_doc.ref_type = ref_type
    #                 # ta_doc.file_name = doc_data['file_name']
    #                 # ta_doc.gen_file_name = doc_data['gen_file_name']
    #                 # ta_doc.maker_or_admin = is_maker
    #                 # ta_doc.created_by = employee_id
    #                 # ta_doc.detail = detail_id
    #                 # ta_doc.requirement_type = requirement_type
    #                 # ta_doc.requirement = requirement_id
    #                 # ta_doc.save()
    #             success_obj = NWisefinSuccess()
    #             success_obj.set_status(SuccessStatus.SUCCESS)
    #             success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
    #             return success_obj
    #     except Exception as e:
    #         error_obj = NWisefinError()
    #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #         error_obj.set_description(str(e))
    #         return error_obj
    #
    # def fetch_tadoc(self, request, tour_id, id, requirement_type, requirment,ref_type):
    #     employee_id = request.employee_id
    #     resp_list = NWisefinList()
    #     doc_table=None
    #     if tour_id==None and id==None:
    #         doc_table = TADocuments.objects.using(self._current_app_schema()).filter(requirement_type=requirement_type,
    #                                                                              requirement=requirment,ref_type=ref_type)
    #     elif id!=None:
    #         doc_table=TADocuments.objects.using(self._current_app_schema()).filter(id=id)
    #     elif tour_id!=None:
    #         doc_table = TADocuments.objects.using(self._current_app_schema()).filter(request=tour_id,
    #                                                                                  ref_type=ref_type)
    #     if len(doc_table) >1:
    #         for data in doc_table:
    #             req_data = Doc_response()
    #             req_data.set_id(data.id)
    #             req_data.set_file_type(data.file_id)
    #             req_data.set_file_name(data.file_name)
    #             resp_list.append(req_data)
    #
    #         return resp_list.get()
    #
    #     if doc_table != None:
    #         doc_table=doc_table.last()
    #
    #         doc_service = DocumentsService(self._scope())
    #         file_id = doc_table.file_id
    #
    #         resp_obj = doc_service.doc_download(file_id, employee_id)
    #         return resp_obj
    #     else:
    #         error_obj = NWisefinError()
    #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #         error_obj.set_description(ErrorDescription.INVALID_DOC_ID)
    #         return error_obj.get()
    # def document_view(self,request,tour_id,id,requirement_type,requirment,ref_type):
    #     doc_get=self.fetch_tadoc(request, tour_id, id, requirement_type, requirment,ref_type)
    #     doc_service = DocumentsService(self._scope())
    #     # file_id = doc_get.file_id
    #     excel="xlsx"
    #     doc_view=doc_service.file_view_extention(excel,doc_get)
    #     return doc_view
    #     # resp_obj = doc_service.doc_download(file_id, employee_id)
    # def doc_particularget(self,id,employee_id):
    #     doc_table=None
    #     if id!=None:
    #         doc_table=TADocuments.objects.using(self._current_app_schema()).get(id=id)
    #     doc_service = DocumentsService(self._scope())
    #     file_id = doc_table.file_id
    #
    #     resp_obj = doc_service.doc_download(file_id, employee_id)
    #     return resp_obj
    # def doc_particular_del(self,id,employee_id):
    #     try:
    #         if id!=None:
    #             doc_table=TADocuments.objects.using(self._current_app_schema()).filter(id=id).update(status=0)
    #
    #         # resp_obj = doc_service.doc_download(file_id, employee_id)
    #         success_obj = NWisefinSuccess()
    #         success_obj.set_status(SuccessStatus.SUCCESS)
    #         success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
    #         return success_obj
    #     except Exception as e:
    #         error_obj = NWisefinError()
    #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #         error_obj.set_description(str(e))
    #         return error_obj


    # def get_doc(self, file_name, vys_page):
    #     resp_list = NWisefinList()
    #     if file_name == None:
    #         fetch_doc = Document_type.objects.using(self._current_app_schema()).all()[
    #                     vys_page.get_offset():vys_page.get_query_limit()]
    #     else:
    #         fetch_doc = Document_type.objects.using(self._current_app_schema()).filter(file_name__icontains=file_name)[
    #                     vys_page.get_offset():vys_page.get_query_limit()]
    #     for data in fetch_doc:
    #         req_data = Doc_response()
    #         req_data.set_id(data.id)
    #         req_data.set_file_type(data.file_type)
    #         req_data.set_file_name(data.file_name)
    #         req_data.set_description(data.description)
    #         req_data.set_created_date(data.created_date)
    #         req_data.set_updated_date(data.updated_date)
    #         resp_list.append(req_data)
    #     vpage = NWisefinPaginator(fetch_doc, vys_page.get_index(), 10)
    #     resp_list.set_pagination(vpage)
    #
    #     return resp_list

    # def dele_doc_type(self, file_type):
    #     try:
    #         dele_chat = Document_type.objects.using(self._current_app_schema()).filter(file_type=file_type).update(
    #             status=0)
    #         success_obj = NWisefinSuccess()
    #         success_obj.set_status(SuccessStatus.SUCCESS)
    #         success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
    #         return success_obj
    #
    #     except Exception as e:
    #         error_obj = NWisefinError()
    #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #         error_obj.set_description(str(e))
    #         return error_obj

    def holidaycheck_weekend(self, start_date,end_date,employeeid,tour_id):
        # start_date = data["start_date"]
        # end_date = data["end_date"]
        # arr=[]
        start_date=self.millisec_conversion(start_date)
        end_date=self.millisec_conversion(end_date)
        start_date = datetime.strptime(start_date[:10], '%Y-%m-%d')
        end_date = datetime.strptime(end_date[:10], '%Y-%m-%d')
        error_obj = NWisefinError()
        if start_date > end_date:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.START_END_DATE)
            return error_obj
        if employeeid is None:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID_EMP_ID)
            return error_obj
        if int(employeeid)==0:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID_EMP_ID)
            return error_obj
        delta = end_date - start_date
        resp_list = NWisefinList()
        for i in range(delta.days + 1):
            day = (start_date + timedelta(days=i))
            # arr.append(day.strftime('%A'))
            req_data = Doc_response()

            if day.strftime('%A') == "Sunday" or day.strftime('%A') == "Saturday":
                date = day.strftime('%A')
                req_data.set_weekend_date(day)
                req_data.set_weekend_day(date)
                req_data.set_weekend_date_ms(round(day.timestamp() * 1000))
                resp_list.append(req_data)
            holiday=Holiday.objects.using(self._current_app_schema()).filter(date=day,status=1)
            if len(holiday)!=0:
                for i in holiday:
                    req_data.set_holdiay(i.date)
                    req_data.set_holdiay_name(i.holidayname)
                    resp_list.data.append(req_data)


        if tour_id is None:
            tourstatus = [Status.PENDING, Status.APPROVED, Status.RETURNED]
            tourcanstatus = [Status.DEFAULT, Status.PENDING, Status.REJECTED]

            prev_tour_end1=TourRequestmodel.objects.using(self._current_app_schema()).filter(empgid=employeeid,start_date__lt=start_date,
                                                                                             end_date__gt=start_date,tour_status__in=tourstatus
                                                                                           ,tour_cancel_status__in=tourcanstatus)
            prev_tour_end2=TourRequestmodel.objects.using(self._current_app_schema()).filter(empgid=employeeid,start_date__lt=end_date,
                                                                                             end_date__gt=end_date,tour_status__in=tourstatus
                                                                                           ,tour_cancel_status__in=tourcanstatus)

            prev_tour=len(prev_tour_end1)+len(prev_tour_end2)
            if prev_tour==0:
                prev_tour = TourRequestmodel.objects.using(self._current_app_schema()).filter(empgid=employeeid,
                                                                                                   start_date__gt=start_date,
                                                                                                   end_date__lt=end_date,
                                                                                                   tour_status__in=tourstatus,
                                                                                                   tour_cancel_status__in=tourcanstatus)
                if len(prev_tour)==0:
                    prev_tour_1 = TourRequestmodel.objects.using(self._current_app_schema()).filter(empgid=employeeid,
                                                                                                       start_date=start_date,
                                                                                                       end_date__lt=end_date,
                                                                                                       tour_status__in=tourstatus,
                                                                                                       tour_cancel_status__in=tourcanstatus).exclude(durationdays=1)
                    prev_tour_2 = TourRequestmodel.objects.using(self._current_app_schema()).filter(empgid=employeeid,
                                                                                                       start_date__gt=start_date,
                                                                                                       end_date=end_date,
                                                                                                       tour_status__in=tourstatus,
                                                                                                       tour_cancel_status__in=tourcanstatus).exclude(durationdays=1)
                    prev_tour=len(prev_tour_1)+len(prev_tour_2)
                    if prev_tour==0:
                        if start_date!=end_date:
                            prev_tour = TourRequestmodel.objects.using(self._current_app_schema()).filter(
                                empgid=employeeid,
                                start_date=start_date,
                                end_date=end_date,
                                tour_status__in=tourstatus,
                                tour_cancel_status__in=tourcanstatus)
                            prev_tour=len(prev_tour)


                else:
                    prev_tour=len(prev_tour)


        else:
            tourstatus = [Status.PENDING, Status.APPROVED, Status.RETURNED]
            tourcanstatus = [Status.DEFAULT, Status.PENDING, Status.REJECTED]

            prev_tour_end1 = TourRequestmodel.objects.using(self._current_app_schema()).filter(empgid=employeeid,
                                                                                               start_date__lt=start_date,
                                                                                               end_date__gt=start_date,
                                                                                               tour_status__in=tourstatus
                                                                                               ,
                                                                                               tour_cancel_status__in=tourcanstatus).exclude(id=tour_id)
            prev_tour_end2 = TourRequestmodel.objects.using(self._current_app_schema()).filter(empgid=employeeid,
                                                                                               start_date__lt=end_date,
                                                                                               end_date__gt=end_date,
                                                                                               tour_status__in=tourstatus
                                                                                               ,
                                                                                               tour_cancel_status__in=tourcanstatus).exclude(id=tour_id)

            prev_tour = len(prev_tour_end1) + len(prev_tour_end2)
            if prev_tour == 0:
                prev_tour = TourRequestmodel.objects.using(self._current_app_schema()).filter(empgid=employeeid,
                                                                                              start_date__gt=start_date,
                                                                                              end_date__lt=end_date,
                                                                                              tour_status__in=tourstatus,
                                                                                              tour_cancel_status__in=tourcanstatus).exclude(id=tour_id)
                if len(prev_tour) == 0:
                    prev_tour_1 = TourRequestmodel.objects.using(self._current_app_schema()).filter(empgid=employeeid,
                                                                                                    start_date=start_date,
                                                                                                    end_date__lt=end_date,
                                                                                                    tour_status__in=tourstatus,
                                                                                                    tour_cancel_status__in=tourcanstatus).exclude(Q(id=tour_id)|Q(durationdays=1))
                    prev_tour_2 = TourRequestmodel.objects.using(self._current_app_schema()).filter(empgid=employeeid,
                                                                                                    start_date__gt=start_date,
                                                                                                    end_date=end_date,
                                                                                                    tour_status__in=tourstatus,
                                                                                                    tour_cancel_status__in=tourcanstatus).exclude(Q(id=tour_id)|Q(durationdays=1))
                    prev_tour = len(prev_tour_1) + len(prev_tour_2)
                    if prev_tour == 0:
                        if start_date != end_date:
                            prev_tour = TourRequestmodel.objects.using(self._current_app_schema()).filter(
                                empgid=employeeid,
                                start_date=start_date,
                                end_date=end_date,
                                tour_status__in=tourstatus,
                                tour_cancel_status__in=tourcanstatus).exclude(id=tour_id)
                            prev_tour = len(prev_tour)


                else:
                    prev_tour = len(prev_tour)

        len_prev_tour = bool((prev_tour))
        resp_list.ongoing_tour=len_prev_tour

        date_relaxation_required=False
        # startdate = startdate[:10]
        # sdate = datetime.strptime(startdate, "%Y-%m-%d").date()
        if (time_function.ist_date() - start_date.date()).days >= 90:
            date_relaxation_required=True
        resp_list.date_relaxation_required=date_relaxation_required
        return resp_list
        # print(arr)
        #
        # if weekend_check in arr:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.DATA_ERROR)
        #     return error_obj
        # else:
        #     success_obj = NWisefinSuccess()
        #     success_obj.set_status(SuccessStatus.SUCCESS)
        #     success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        #     return success_obj
    def millisec_conversion(self,date):
        try:
            date = str(datetime.fromtimestamp(int(date) / 1000.0))
        except:
            pass
        return date
    def emp_alltravel_count(self, employee_id, vys_page):
        resp_list = NWisefinList()
        req_data = Travel_count()
        if employee_id != None:
            tour_req = TourRequestmodel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),empgid=employee_id).values(
                "id").count()
            req_data.set_count(tour_req)
            req_data.set_employee(employee_id)
            resp_list.append(req_data)
        else:
            tour_req = TourRequestmodel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).all().values(
                "id").count()
            req_data.set_count(tour_req)
            resp_list.append(req_data)
        return resp_list

    def total_claim_count(self, employee_id, vys_page):
        resp_list = NWisefinList()
        req_data = Travel_count()
        if employee_id != None:
            tour_req = TourRequestmodel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),empgid=employee_id).values(
                "id")
            req_data.set_employee(employee_id)
        else:
            tour_req = TourRequestmodel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id).all().values(
                "id")
        tour_req_count = tour_req.count()
        req_data.set_count(tour_req_count)
        claim_amount = 0
        approved_amount = 0
        for i in tour_req:
            amount_count = ClaimRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=i["id"])
            for amt_count in amount_count:
                claim_amount += amt_count.claimedamount
                approved_amount += amt_count.approvedamount


                req_data.set_claimed_amount(claim_amount)
                req_data.set_approved_amount(approved_amount)
        resp_list.append(req_data)
        return resp_list

    def alltravelget_date(self, start_date, end_date, vys_page):
        resp_list = NWisefinList()
        req_data = Travel_count()
        tour_req = 0
        if start_date != None and end_date != None:
            tour_req = TourRequestmodel.objects.using(self._current_app_schema()).filter(start_date__gte=start_date,entity_id=self._entity_id(),
                                                                                         end_date__lte=end_date).values(
                "id").count()
        if end_date == None:
            tour_req = TourRequestmodel.objects.using(self._current_app_schema()).filter(start_date__gte=start_date,entity_id=self._entity_id(),
                                                                                         end_date__lte=datetime.now()).values(
                "id").count()
        req_data.set_count(tour_req)
        resp_list.append(req_data)
        return resp_list

    def allclaimget_date(self, start_date, end_date, vys_page):
        resp_list = NWisefinList()
        req_data = Travel_count()
        tour_req = 0
        if start_date != None and end_date != None:
            tour_req = TourRequestmodel.objects.using(self._current_app_schema()).filter(start_date__gte=start_date,entity_id=self._entity_id(),
                                                                                         end_date__lte=end_date).values(
                "id")
        if end_date == None:
            tour_req = TourRequestmodel.objects.using(self._current_app_schema()).filter(start_date__gte=start_date,entity_id=self._entity_id(),
                                                                                         end_date__lte=datetime.now()).values(
                "id")
        tour_req_count = tour_req.count()
        req_data.set_count(tour_req_count)
        claim_amount = 0
        approved_amount = 0
        for i in tour_req:
            amount_count = ClaimRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=i["id"])
            for amt_count in amount_count:
                claim_amount += amt_count.claimedamount
                approved_amount += amt_count.approvedamount

                req_data.set_claimed_amount(claim_amount)
                req_data.set_approved_amount(approved_amount)
        resp_list.append(req_data)
        return resp_list

    # def booking(self, data, employee_id):
    #     # sets= set()
    #     for each_dict in data:
    #         each_data = Booking(each_dict)
    #         if each_data.booking_needed == Travel_requirements.accomodation:
    #             detailid_get=AccomodationBookingInfo.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=each_data.reference_id)
    #
    #         elif each_data.booking_needed == Travel_requirements.cab:
    #             detailid_get = CabBookingInfo.objects.using(self._current_app_schema()).get(
    #                 entity_id=self._entity_id(), id=each_data.reference_id)
    #         elif each_data.booking_needed == Travel_requirements.bus:
    #             detailid_get = BusBookingInfo.objects.using(self._current_app_schema()).get(
    #                 entity_id=self._entity_id(), id=each_data.reference_id)
    #         elif each_data.booking_needed == Travel_requirements.train:
    #             detailid_get = TrainBookingInfo.objects.using(self._current_app_schema()).get(
    #                 entity_id=self._entity_id(), id=each_data.reference_id)
    #         elif each_data.booking_needed == Travel_requirements.air:
    #             detailid_get = TrainBookingInfo.objects.using(self._current_app_schema()).get(
    #                 entity_id=self._entity_id(), id=each_data.reference_id)
    #         else:
    #             detailid_get=0
    #
    #         tour_dtl_id = TourDetail.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),
    #                                                                                     id=detailid_get.travel_detail_id)
    #         tourreq_id=tour_dtl_id.tour_id
    #         # tourreq_id = TourRequestmodel.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),
    #         #                                                                             id=detailid_get.travel_detail_id)
    #         # sets.add(tourreq_id)
    #         tour_id=tourreq_id
    #         detail_id=detailid_get.travel_detail_id
    #     booking_val = self.booking_validations(tour_id, employee_id, detail_id, data)
    #     if booking_val is False:
    #         error_obj = NWisefinError()
    #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #         error_obj.set_description(ErrorDescription.BOOKING)
    #         return error_obj
    #
    #
    #
    #     insert_booking = self.insert_booking_data(data, detail_id, employee_id)
    #     tour_dtl_arr = []
    #     dtl_data = TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
    #                                                                            tour_id=tour_id)
    #
    #     for each_data in dtl_data:
    #         tour_dtl_arr.append(each_data.id)
    #     for each_dict in data:
    #         each_data = Booking(each_dict)
    #         if each_data.booking_needed == Travel_requirements.accomodation:
    #             self.book_accomodation(each_data, tour_dtl_arr, tour_id)
    #         elif each_data.booking_needed == Travel_requirements.cab:
    #             self.book_cab(each_data, tour_dtl_arr, tour_id)
    #         elif each_data.booking_needed == Travel_requirements.bus:
    #             self.book_bus(each_data, tour_dtl_arr, tour_id)
    #         elif each_data.booking_needed == Travel_requirements.train:
    #             self.book_train(each_data, tour_dtl_arr, tour_id)
    #         elif each_data.booking_needed == Travel_requirements.air:
    #             self.book_air(each_data, tour_dtl_arr, tour_id)
    #     success_obj = NWisefinSuccess()
    #     success_obj.set_status(SuccessStatus.SUCCESS)
    #     success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
    #     return success_obj




    def get_all_requirements(self, detail_id,request):
        requirement = []
        cab_service = Cab_requirement(self._scope())
        cab_data = cab_service.cab_detail_get(detail_id,request)
        for each_data in cab_data.data:
            requirement.append(each_data)
        bus_service = Bus_requirement(self._scope())
        bus_data = bus_service.bus_details_get(detail_id,request)
        for each_data in bus_data.data:
            requirement.append(each_data)
        train_service = Train_requirement(self._scope())
        train_data = train_service.train_details_get(detail_id,request)
        for each_data in train_data.data:
            requirement.append(each_data)
        air_service = Air_requirement(self._scope())
        air_data = air_service.air_details_get(detail_id,request)
        for each_data in air_data.data:
            requirement.append(each_data)
        accomodation_service = AccomodationBooking_requirement(self._scope())
        accomodation_data = accomodation_service.accomadation_details_get(detail_id,request)
        for each_data in accomodation_data.data:
            requirement.append(each_data)
        if len(requirement) > 0:
            # sorted_requiremnets
            requirement = sorted(requirement, key=lambda d: d.created_date_time)
        return requirement
    def get_all_adminrequirements(self, detail_id,request,booking_type,all_report,vys_page,from_date,to_date,tour_id):
        if booking_type==Travel_requirements.cab:

            cab_service = Cab_requirement(self._scope())
            cab_data = cab_service.fetch_cab_admin(detail_id,request,all_report,vys_page,from_date,to_date,tour_id)
            return cab_data
        elif booking_type==Travel_requirements.bus:
            bus_service = Bus_requirement(self._scope())
            bus_data = bus_service.fetch_Bus_admin(detail_id,request,all_report,vys_page,from_date,to_date,tour_id)
            return bus_data
        elif booking_type==Travel_requirements.train:
            train_service = Train_requirement(self._scope())
            train_data = train_service.fetch_Train_admin(detail_id,request,all_report,vys_page,from_date,to_date,tour_id)
            return train_data
        elif booking_type==Travel_requirements.air:
            air_service = Air_requirement(self._scope())
            air_data = air_service.fetch_Air_admin(detail_id,request,all_report,vys_page,from_date,to_date,tour_id)
            return air_data
        elif booking_type==Travel_requirements.accomodation:
            accomodation_service = AccomodationBooking_requirement(self._scope())
            accomodation_data = accomodation_service.fetch_accomadation_admin(detail_id,request,all_report,vys_page,from_date,to_date,tour_id)
            return accomodation_data

    def short_term_travel(self,vys_page,request_date,tour_no,request):
        if request_date != "":
            try:
                request_date=int(request_date)
                request_date = str(datetime.fromtimestamp(int(request_date)/1000.0))
                request_date = (datetime.strptime(request_date[:10], '%Y-%m-%d')).date()
            except:
                request_date = (datetime.strptime(request_date, '%d-%b-%Y')).date()
        Tour = TourRequestmodel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),request_date__icontains=request_date,id__icontains=tour_no).all().order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]

        resp_list = NWisefinList()
        if len(Tour)>0:
            for tour in Tour:
                if (tour.end_date.date()-tour.start_date.date()).days<=2:
                    req_data = TourMakerResponse()
                    req_data.set_id(tour.id)
                    req_data.set_requestdate(tour.request_date)
                    req_data.set_permittedby_id(tour.permittedby)
                    req_data.set_empgid(tour.empgid)
                    empdtl=ApiService(self._scope())
                    permitted=empdtl.employee_details_get(tour.permittedby,request)
                    req_data.set_permittedby(permitted.full_name)
                    employee=empdtl.employee_details_get(tour.empgid,request)
                    req_data.set_employee_name(employee.full_name)
                    req_data.set_employee_code(employee.code)
                    req_data.set_empdesignation(tour.empdesignation)
                    req_data.set_transfer_on_promotion(tour.transfer_on_promotion)
                    req_data.set_empgrade(tour.empgrade)
                    req_data.set_empbranchgid(tour.empbranchgid)

                    approver=TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(), tour_id=tour.id, request_type=(App_type.tour or App_type.TOUR), applevel=1).last()
                    if approver is not None:
                        approver_id=approver.approvedby
                        approver=empdtl.employee_details_get(approver_id,request)
                        req_data.set_approver_data(approver_id, approver.full_name, approver.code)
                    else:
                        req_data.set_approver_data(None, None, None)
                    branch = empdtl.get_branch_data(tour.empbranchgid,request)
                    req_data.set_branch_name(branch.name)
                    req_data.set_branch_code(branch.code)
                    detail=emp_dtl(self._scope())
                    reason = detail.get_reason_name(tour.reason)
                    req_data.set_reason(reason)
                    req_data.set_reason_id(tour.reason)
                    req_data.set_quantum_of_funds(tour.quantum_of_funds)
                    req_data.set_opening_balance(tour.opening_balance)
                    req_data.set_startdate(tour.start_date)
                    req_data.set_enddate(tour.end_date)
                    req_data.set_ordernoremarks(tour.remarks)
                    if tour.onbehalfof > 0:
                        onbehalf = empdtl.employee_details_get(tour.onbehalfof,request)
                        req_data.set_onbehalfof(onbehalf.full_name)
                    # tour_status=status_get(tour.tour_status)
                    # claim_status=status_get(tour.claim_status)
                    # req_data.set_tour_status(tour_status)
                    # req_data.set_claim_status(claim_status)
                    # req_data.set_tour_status_id(tour.tour_status)
                    # req_data.set_claim_status_id(tour.claim_status)
                    diffdays = (time_function.ist_date() - tour.end_date.date()).days
                    req_data.set_is_tour_ended(bool(max(0, diffdays)))
                    resp_list.append(req_data)
                vpage = NWisefinPaginator(Tour, vys_page.get_index(), 10)
                resp_list.set_pagination(vpage)
        return resp_list
    def daterelaxation_popup(self, request, vys_page):
        # end_date=datetime.strptime(end_date[:10], '%Y-%m-%d')
        #
        # today_date=datetime.today()
        # duration_days=(today_date-end_date).days
        # print(duration_days)
        # if int(duration_days) >31:
        #     return True
        # else:
        #     return False
        remainder=Remainder()
        common_dropdown=Common_dropdown.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),name=remainder.first_remainder)

        today = datetime.today() - timedelta(days=int(common_dropdown.code))
        # today_date=(today, '%Y-%m-%d')

        travel_req = TourRequestmodel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                       end_date__date=today,
                                                                                       tour_status=Status.APPROVED,
                                                                                       claim_status=Status.DEFAULT)[
                     vys_page.get_offset():vys_page.get_query_limit()]
        resp_list = NWisefinList()

        api_service = ApiService(self._scope())
        for dtl in travel_req:
            rep_list = TourMakerResponse()
            rep_list.set_tour_id(dtl.id)
            if dtl.onbehalfof == 0:
                emp_id = api_service.employee_details_get(dtl.empgid, request)
                rep_list.set_empgid(dtl.empgid)
            else:
                emp_id = api_service.employee_details_get(dtl.onbehalfof, request)
                rep_list.set_empgid(dtl.onbehalfof)
            rep_list.set_employee_name(emp_id.full_name)
            resp_list.append(rep_list)
        vpage = NWisefinPaginator(travel_req, vys_page.get_index(), 10)
        resp_list.set_pagination(vpage)
        return resp_list

    def popup_nine_days(self, request, vys_page):
        # end_date=datetime.strptime(end_date[:10], '%Y-%m-%d')
        #
        # today_date=datetime.today()
        # duration_days=(today_date-end_date).days
        # print(duration_days)
        # if int(duration_days) >31:
        #     return True
        # else:
        #     return False
        remainder=Remainder()

        common_dropdown=Common_dropdown.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),name=remainder.second_remainder)

        today = datetime.today() - timedelta(days=int(common_dropdown.code))
        travel_req = TourRequestmodel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                       end_date__date=today,
                                                                                       tour_status=Status.APPROVED,
                                                                                       claim_status=Status.DEFAULT)[
                     vys_page.get_offset():vys_page.get_query_limit()]
        resp_list = NWisefinList()

        api_service = ApiService(self._scope())
        for dtl in travel_req:
            rep_list = TourMakerResponse()
            rep_list.set_tour_id(dtl.id)
            if dtl.onbehalfof == 0:
                emp_id = api_service.employee_details_get(dtl.empgid, request)
                rep_list.set_empgid(dtl.empgid)
            else:
                emp_id = api_service.employee_details_get(dtl.onbehalfof, request)
                rep_list.set_empgid(dtl.empgid)

            rep_list.set_employee_name(emp_id.full_name)
            resp_list.append(rep_list)
        vpage = NWisefinPaginator(travel_req, vys_page.get_index(), 10)
        resp_list.set_pagination(vpage)
        return resp_list

    def insert_client(self, request, employee_id):
        try:
            request_client = Cd_del_req(request)
            if request_client.get_id() != None:
                client_create = Client.objects.using(self._current_app_schema()).filter(
                    id=request_client.get_id()).update(
                    name=request_client.get_name(), code=request_client.get_code(), updated_by=employee_id,
                    updated_date=datetime.now(),entity_id=self._entity_id())
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                return success_obj

            else:
                client_create = Client.objects.using(self._current_app_schema()).create(
                    name=request_client.get_name(), code=request_client.get_code(), created_by=employee_id,
                    created_date=datetime.now(),entity_id=self._entity_id())

                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                return success_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj
    def fetch_client(self,request,vys_page):
        fetch_client=Client.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),status=1)[vys_page.get_offset():vys_page.get_query_limit()]
        resp_list = NWisefinList()

        for dtl in fetch_client:
            res_list = Cd_res()
            res_list.set_id(dtl.id)
            res_list.set_name(dtl.name)
            res_list.set_code(dtl.code)
            resp_list.append(res_list)
        vpage = NWisefinPaginator(fetch_client, vys_page.get_index(), 10)
        resp_list.set_pagination(vpage)
        return resp_list


    def get_client(self,request,id):
        try:
            fetch_client=Client.objects.using(self._current_app_schema()).get(id=id,entity_id=self._entity_id(),status=1)
            resp_list = NWisefinList()
            res_list=Cd_res()

            res_list.set_id(fetch_client.id)
            res_list.set_name(fetch_client.name)
            res_list.set_code(fetch_client.code)
            resp_list.append(res_list)
            return resp_list

        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj


    def delete_client(self,request,id):
        fetch_client=Client.objects.using(self._current_app_schema()).filter(id=id,entity_id=self._entity_id()).update(status=0)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj



    def get_all_booked_details(self,tour_id):
        dtl_array=[]
        dtl_data = TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                               tour_id=tour_id)
        for each_dtl in dtl_data:
            dtl_array.append(each_dtl.id)

        booking_history = BookingHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                               tourdetail__in=dtl_array)
        resp_list = NWisefinList()
        for eachdata in booking_history:
            temp = Booking_req()
            temp.set_id(eachdata.id)
            temp.set_tourdetail(eachdata.tourdetail_id)
            temp.set_booking_needed(eachdata.booking_needed)
            temp.set_reference_id(eachdata.reference_id)
            temp.set_booking_status(eachdata.booking_status)
            temp.set_booking_time(eachdata.booking_time)
            temp.set_comments(eachdata.comments)
            temp.set_status(eachdata.status)
            temp.set_ticket_amount(eachdata.ticket_amount)
            temp.set_cancel_reschedule(eachdata.cancel_reschedule)
            temp.set_cancel_reasone(eachdata.cancel_reason)
            temp.set_refund_amount(eachdata.refund_amount)
            temp.set_refund_date(eachdata.refund_date)
            temp.set_fare_difference(eachdata.fare_difference)
            resp_list.append(temp)
        return resp_list
    def edit_validations(self,tour_id,apptype):
        travel_his=TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=tour_id,request_type=apptype).last()
        if travel_his.applevel==App_level.FIRST_LEVEL and travel_his.status==Status.APPROVED:
            return False
        elif travel_his.applevel==App_level.SECOND_LEVEL and travel_his.status==Status.PENDING:
            return False
        elif travel_his.applevel==App_level.THIRD_LEVEL and travel_his.status==Status.APPROVED:
            return False
        elif travel_his.applevel==App_level.THIRD_LEVEL and travel_his.status==Status.PENDING:
            return False
        else:
            return True
    # def amount_popup(self,claim_amount,eligible_amount):
    #     if int(claim_amount)>int(eligible_amount):
    #         error_obj = NWisefinError()
    #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #         error_obj.set_description(ErrorDescription.ELIGIBLE_AMOUNT)
    #         return error_obj
    #     else:
    #         return True


    # def personal_official(self,data,employee_id):
    #     logger.info('ta_ personal_official- ' + str(data) + str(employee_id))
    #     if int(data['type'])==0:
    #         error_obj = NWisefinError()
    #         detailid=data['id']
    #         dtl_data = TourDetail.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=detailid)
    #
    #         approver_data = TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),request_type=App_type.TOUR,
    #                                                                                tour_id=dtl_data.tour_id).last()
    #         if approver_data.applevel!=App_level.THIRD_LEVEL:
    #             error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #             error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
    #             return error_obj
    #         # if approver_data.approvedby!=employee_id:
    #         #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #         #     error_obj.set_description(ErrorDescription.INVALID_APPROVER_ID)
    #         #     return error_obj
    #
    #         dtl_data = TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
    #                                                                                id=data['id']).update(official=data['official'])
    #
    #         AccomodationBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
    #                                                                        travel_detail_id=detailid).update(admin_paid=data['official'])
    #         CabMapping.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
    #                                                                        travel_detail_id=detailid).update(admin_paid=data['official'])
    #         BusBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
    #                                                                        travel_detail_id=detailid).update(admin_paid=data['official'])
    #         TrainBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
    #                                                                        travel_detail_id=detailid).update(admin_paid=data['official'])
    #         AirBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
    #                                                                        travel_detail_id=detailid).update(admin_paid=data['official'])
    #
    #     else:
    #         requirement_type=int(data['type'])
    #         requirement_id=int(data['id'])
    #         if requirement_type==Travel_requirements.accomodation:
    #             AccomodationBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
    #                                                                                         requirement_id=requirement_id).update(admin_paid=data['official'])
    #         elif requirement_type==Travel_requirements.cab:
    #             CabMapping.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
    #                                                                                         requirement_id=requirement_id).update(admin_paid=data['official'])
    #         elif requirement_type==Travel_requirements.bus:
    #             BusBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
    #                                                                                         requirement_id=requirement_id).update(admin_paid=data['official'])
    #         elif requirement_type==Travel_requirements.train:
    #             TrainBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
    #                                                                                         requirement_id=requirement_id).update(admin_paid=data['official'])
    #         elif requirement_type==Travel_requirements.air:
    #             AirBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
    #                                                                                         requirement_id=requirement_id).update(admin_paid=data['official'])
    #         else:
    #             error_obj = NWisefinError()
    #             error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #             error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
    #             return error_obj
    #
    #
    #     success_obj = NWisefinSuccess()
    #     success_obj.set_status(SuccessStatus.SUCCESS)
    #     success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
    #     return success_obj


    def personal_official (self,data,employee_id):
        error_obj = NWisefinError()
        logger.info('ta_ personal_official- ' + str(data) + str(employee_id))
        official=int(data['official'])
        if int(data['type'])==0:

            detailid=data['id']

            requirement_type = int(data['type'])
            if official==Requirements_official.personal:
                dtl_data = TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                       id=data['id']).update(official=official)

                AccomodationBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                               travel_detail_id=detailid).update(ticket_amount=0,
                                                                                                                 official=official)
                CabMapping.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                               travel_detail_id=detailid).update(ticket_amount=0,
                                                                                                                 official=official)
                BusBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                               travel_detail_id=detailid).update(ticket_amount=0,
                                                                                                                 official=official)
                TrainBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                               travel_detail_id=detailid).update(ticket_amount=0,
                                                                                                                 official=official)
                AirBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                               travel_detail_id=detailid).update(ticket_amount=0,
                                                                                                                 official=official)
                BookingHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                               tourdetail_id=detailid).update(ticket_amount=0)

            elif official==Requirements_official.official:
                dtl_data = TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                       id=data['id']).update(official=official)

                AccomodationBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                               travel_detail_id=detailid).update(ticket_amount_personal=0,
                                                                                                                 official=official)
                CabMapping.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                               travel_detail_id=detailid).update(ticket_amount_personal=0,
                                                                                                                 official=official)
                BusBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                               travel_detail_id=detailid).update(ticket_amount_personal=0,
                                                                                                                 official=official)
                TrainBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                               travel_detail_id=detailid).update(ticket_amount_personal=0,
                                                                                                                 official=official)
                AirBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                               travel_detail_id=detailid).update(ticket_amount_personal=0,
                                                                                                                 official=official)
                BookingHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                               tourdetail_id=detailid).update(ticket_amount_personal=0)

            elif official==Requirements_official.personal_official:
                dtl_data = TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                       id=data['id']).update(official=official)

                AccomodationBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                               travel_detail_id=detailid).update(official=official)
                CabMapping.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                               travel_detail_id=detailid).update(official=official)
                BusBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                               travel_detail_id=detailid).update(official=official)
                TrainBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                               travel_detail_id=detailid).update(official=official)
                AirBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                               travel_detail_id=detailid).update(official=official)
            else:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
                return error_obj

        else:
            requirement_type=int(data['type'])
            requirement_id=int(data['id'])

            dtl_data = TourDetail.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),
                                                                                   id=data['id'])
            if dtl_data.official==Requirements_official.personal or dtl_data.official==Requirements_official.official:
                if official!=dtl_data.official:
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_OFFICIAL_STATUS)
                    return error_obj
            elif dtl_data.official!=Requirements_official.personal_official:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
                return error_obj



            if requirement_type==Travel_requirements.accomodation:
                AccomodationBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                            requirement_id=requirement_id).update(official=official)
            elif requirement_type==Travel_requirements.cab:
                CabMapping.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                            requirement_id=requirement_id).update(official=official)
            elif requirement_type==Travel_requirements.bus:
                BusBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                            requirement_id=requirement_id).update(official=official)
            elif requirement_type==Travel_requirements.train:
                TrainBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                            requirement_id=requirement_id).update(official=official)
            elif requirement_type==Travel_requirements.air:
                AirBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                            requirement_id=requirement_id).update(official=official)
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
                return error_obj


        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj

    def city_dropdown(self,request,city_name,vys_page):
        api_service=ApiService(self._scope())
        city_dropdown=api_service.city_dropdown(request,city_name,vys_page)
        return city_dropdown

    def no_show(self,data,employee_id):
        logger.info('ta_ no_show- ' + str(data) + str(employee_id))
        obj=No_show_req(data)
        requirement_type = obj.requirement_type
        requirement_id = obj.requirement_id
        if requirement_type == Travel_requirements.accomodation:
            AccomodationBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                        requirement_id=requirement_id).update(
                utilised_status=obj.no_show_status)
        elif requirement_type == Travel_requirements.cab:
            CabMapping.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                        requirement_id=requirement_id).update(
                utilised_status=obj.no_show_status)
        elif requirement_type == Travel_requirements.bus:
            BusBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                               requirement_id=requirement_id).update(
                utilised_status=obj.no_show_status)
        elif requirement_type == Travel_requirements.train:
            TrainBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                 requirement_id=requirement_id).update(
                utilised_status=obj.no_show_status)
        elif requirement_type == Travel_requirements.air:
            AirBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                               requirement_id=requirement_id).update(
                utilised_status=obj.no_show_status)
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
            return error_obj

    # def money_conversion(self,request,amount):
    #     from forex_python.converter import CurrencyRates
    #     c = CurrencyRates()
    #     dollar = c.get_rate("USD", "INR")
    #     inr=float(amount)*float(dollar)
    #     print(inr)
    #     return inr


    def city_insert(self,request,data,emp_id):
        try:
            if "id" in data:
                city_insert = Ta_City.objects.using(self._current_app_schema()).filter(id=data["id"]).update(name=data["name"],
                                                                                       status=1,
                                                                                       updated_by=emp_id,
                                                                                       updated_date=datetime.now(),metro_non=data["metro_non"],state_type=data["state_type"],state=data["state"],entity_id=self._entity_id())

            else:
                filt=Ta_City.objects.using(self._current_app_schema()).filter(name=data["name"])
                if len(filt)==0:
                    city_insert=Ta_City.objects.using(self._current_app_schema()).create(name=data["name"],status=1,created_by=emp_id,created_date=datetime.now(),metro_non=data["metro_non"],state_type=data["state_type"],state=data["state"],entity_id=self._entity_id())
                    city_id=city_insert.id
                    city_insert.code="CY00"+str(city_id)
                    city_insert.save()
                else:
                    city_insert = Ta_City.objects.using(self._current_app_schema()).filter(name=data["name"]).update(
                        name=data["name"],
                        status=1,
                        updated_by=emp_id,
                        updated_date=datetime.now(), metro_non=data["metro_non"], state_type=data["state_type"],
                        state=data["state"], entity_id=self._entity_id())


            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj
    def city_get(self,request,city_name,vys_page):
        if city_name!=None:
            city_filter=Ta_City.objects.using(self._current_app_schema()).filter(name__icontains=city_name,status=1)[vys_page.get_offset():vys_page.get_query_limit()]
        else:
            city_filter = Ta_City.objects.using(self._current_app_schema()).filter(status=1)[
                          vys_page.get_offset():vys_page.get_query_limit()]
        resp_list=NWisefinList()
        for i in city_filter:
            res_list = Cd_res()
            res_list.set_id(i.id)
            res_list.set_name(i.name)
            res_list.set_state_type(i.state_type)
            res_list.set_state(i.state)
            res_list.set_metro_non(i.metro_non)
            # res_list.set_code(i.code)
            # res_list.set_status(i.status)
            resp_list.append(res_list)
        vpage = NWisefinPaginator(city_filter, vys_page.get_index(), 10)
        resp_list.set_pagination(vpage)
        return resp_list

    def state_dropdown(self,request,state_name,vys_page):
        if state_name!=None:
            state_filter=Ta_City.objects.using(self._current_app_schema()).filter(state__icontains=state_name,status=1).values("state").annotate(id=Min("id"))[vys_page.get_offset():vys_page.get_query_limit()]
        else:
            state_filter = Ta_City.objects.using(self._current_app_schema()).filter(status=1).values("state").annotate(id=Min("id"))[vys_page.get_offset():vys_page.get_query_limit()]

        resp_list=NWisefinList()
        for i in state_filter:
            res_list = Cd_res()
            # res_list.set_id(i.id)
            res_list.set_state(i["state"])
            # res_list.set_code(i.code)
            # res_list.set_status(i.status)
            resp_list.append(res_list)
        vpage = NWisefinPaginator(state_filter, vys_page.get_index(), 10)
        resp_list.set_pagination(vpage)
        return resp_list
    def citytype_dropdown(self,request,state_name,vys_page):
        if state_name!=None:
            state_filter=Ta_City.objects.using(self._current_app_schema()).filter(state_type__icontains=state_name,status=1).values("state_type").annotate(id=Min("id"))[vys_page.get_offset():vys_page.get_query_limit()]
        else:
            state_filter = Ta_City.objects.using(self._current_app_schema()).filter(status=1).values("state_type").annotate(id=Min("id"))[vys_page.get_offset():vys_page.get_query_limit()]

        resp_list=NWisefinList()
        for i in state_filter:
            res_list = Cd_res()
            # res_list.set_id(i.id)
            res_list.set_state(i["state_type"])
            # res_list.set_code(i.code)
            # res_list.set_status(i.status)
            resp_list.append(res_list)
        vpage = NWisefinPaginator(state_filter, vys_page.get_index(), 10)
        resp_list.set_pagination(vpage)
        return resp_list
    def branch_dropdown(self,request,branch,vys_page):
        api_service = ApiService(self._scope())
        emp_branch = api_service.emp_branch(request, branch, vys_page)

        return emp_branch
    def city_delete(self,request,id):
        try:
            city_insert = Ta_City.objects.using(self._current_app_schema()).filter(id=id).update(status=0)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj


    def city_file(self,file_data,employee):
        try:
            for data in file_data:
                city_filter = Ta_City.objects.using(self._current_app_schema()).filter(name__icontains=data["District"],
                                                                                       status=1)
                if data["Metro/Non-metro"]=="Non-Metro":
                    metro=1
                else:
                    metro=0
                if len(city_filter)!=0:
                    city_insert = Ta_City.objects.using(self._current_app_schema()).filter(name=data["District"],entity_id=self._entity_id()).update(name=data["District"],
                                                                                           status=1,
                                                                                           updated_by=employee,
                                                                                           updated_date=datetime.now(),state_type=data["State Type"],state=data["State"],metro_non=metro)

                else:
                    city_insert=Ta_City.objects.using(self._current_app_schema()).create(name=data["District"],status=1,created_by=employee,created_date=datetime.now(),entity_id=self._entity_id(),state_type=data["State Type"],state=data["State"],metro_non=metro)
                    city_id=city_insert.id
                    city_insert.code="CY00"+str(city_id)
                    city_insert.save()

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            return success_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj

    def holiday_file(self,file_data,employee):
        try:
            from taservice.service.holiday import HolidayData
            holiday_create=HolidayData(self._scope())
            servic=holiday_create.create_holiday(file_data,employee)
            if isinstance(servic, NWisefinError):
                return servic
            else:
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                return success_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj


    def tourreason_delete(self,request,id):
        try:
            city_insert = TourReason.objects.using(self._current_app_schema()).filter(id=id).update(status=0)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj
    def expense_delete(self,request,id):
        try:
            exp_dele = TourExpense.objects.using(self._current_app_schema()).filter(id=id).update(status=0)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj

    def tour_expense_insert(self, request,data,employee_id):
        try:
            if "id" in data:
                exp_insert = TourExpense.objects.using(self._current_app_schema()).filter(id=data["id"]).update(name=data["name"], status=1,
                                                                                          updated_by=employee_id,
                                                                                          updated_date=datetime.now())
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                return success_obj
            else:
                exp_insert=TourExpense.objects.using(self._current_app_schema()).create(code=data["code"],name=data["name"],status=1,created_by=employee_id,created_date=datetime.now())
                # city_id = exp_insert.id
                # exp_insert.code = "CY00" + str(city_id)
                # exp_insert.save()
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
                return success_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj
    def tour_expense_get(self,request,city_name,vys_page):
        if city_name==None:
            expense=TourExpense.objects.using(self._current_app_schema()).filter(status=1)[
                          vys_page.get_offset():vys_page.get_query_limit()]
        else:
            expense = TourExpense.objects.using(self._current_app_schema()).filter(status=1,name__icontains=city_name)[
                      vys_page.get_offset():vys_page.get_query_limit()]
        resp_list = NWisefinList()
        for data in expense:
            res_list = Cd_res()
            res_list.set_id(data.id)
            res_list.set_name(data.name)
            res_list.set_code(data.code)
            resp_list.append(res_list)
        vpage = NWisefinPaginator(expense, vys_page.get_index(), 10)
        resp_list.set_pagination(vpage)
        return resp_list

    def frequent_city(self,request,employee,vys_page,from_place,city_name):
        frequent_city_exclude = []
        if from_place==None:
            frequent_city=TourDetail.objects.using(self._current_app_schema()).filter(tour__empgid=employee).values('startingpoint').annotate(count
                                                                = Count('startingpoint')).order_by('-count')[:3]
            for each_city in frequent_city:
                frequent_city_exclude.append(each_city['startingpoint'])
        else:
            if from_place=='""' or from_place=="''":
                frequent_city=TourDetail.objects.using(self._current_app_schema()).filter(tour__empgid=employee).values('placeofvisit').annotate(count
                                                                    = Count('placeofvisit')).order_by('-count')[:3]
            else:
                frequent_city=TourDetail.objects.using(self._current_app_schema()).filter(tour__empgid=employee,startingpoint=from_place).values('placeofvisit').annotate(count
                                                                    = Count('placeofvisit')).order_by('-count')[:3]
            for each_city in frequent_city:
                frequent_city_exclude.append(each_city['placeofvisit'])




        if city_name != None:
            city_filter = Ta_City.objects.using(self._current_app_schema()).filter(name__icontains=city_name,
                                                                            status=1).values('name')[
                          vys_page.get_offset():vys_page.get_query_limit()]
        else:
            city_filter = Ta_City.objects.using(self._current_app_schema()).filter(status=1).exclude(name__in=frequent_city_exclude).values('name')[
                          max(0,vys_page.get_offset()-len(frequent_city)):vys_page.get_query_limit()-len(frequent_city)]
        resp_list = NWisefinList()
        if vys_page.index==1 and city_name is None:
            for each_data in frequent_city:
                if from_place == None:
                    each_data['name'] = each_data['startingpoint']
                    resp_list.append(each_data)
                else:
                    each_data['name'] = each_data['placeofvisit']
                    resp_list.append(each_data)
        for i in city_filter:
            resp_list.append(i)
        vpage = NWisefinPaginator(city_filter, vys_page.get_index(), 10)
        resp_list.set_pagination(vpage)
        return resp_list


    def frequent_city_2(self,request,employee,vys_page,from_place,city_name):
        frequent_city_exclude = []
        if from_place=='1':
            frequent_city=FrequentData.objects.using(self._current_app_schema()).filter(employee=employee).exclude(from_place_count=0).values(
                'from_place').order_by("-latest_date",'-from_place_count')[:3]
            for each_city in frequent_city:
                frequent_city_exclude.append(each_city['from_place'])
        else:
            frequent_city=FrequentData.objects.using(self._current_app_schema()).filter(employee=employee).exclude(placeofvisit_count=0).values(
                'placeofvisit').order_by("-latest_date",'-placeofvisit_count')[:3]

            for each_city in frequent_city:
                frequent_city_exclude.append(each_city['placeofvisit'])




        if city_name != None:
            city_filter = Ta_City.objects.using(self._current_app_schema()).filter(name__icontains=city_name,
                                                                            status=1).values('name')[
                          vys_page.get_offset():vys_page.get_query_limit()]
        else:
            city_filter = Ta_City.objects.using(self._current_app_schema()).filter(status=1).exclude(name__in=frequent_city_exclude).values('name')[
                          max(0,vys_page.get_offset()-len(frequent_city)):vys_page.get_query_limit()]
        resp_list = NWisefinList()
        if vys_page.index==1 and city_name is None:
            for each_data in frequent_city:
                if from_place == '1':
                    each_data['name'] = each_data['from_place']
                    resp_list.append(each_data)
                else:
                    each_data['name'] = each_data['placeofvisit']
                    resp_list.append(each_data)
        for i in city_filter:
            resp_list.append(i)
        vpage = NWisefinPaginator(city_filter, vys_page.get_index(), 10)
        while len(resp_list.data)>vpage.limit:
            resp_list.set_pagination(vpage)
        resp_list.set_pagination(vpage)
        return resp_list



    def frequent_client(self,request,employee,vys_page,query):

        frequent_client_data=None
        if vys_page.index == 1 and query is None:
            frequent_city=TourDetail.objects.using(self._current_app_schema()).filter(tour__empgid=employee).values('client').annotate(count
                                                                = Count('client')).order_by('-count')[:3]

        # if query != None:
        #     city_filter = Ta_City.objects.using(self._current_app_schema()).filter(name__icontains=query,
        #                                                                     status=1).values('name')[
        #                   vys_page.get_offset():vys_page.get_query_limit()]
        # else:
        #     city_filter = Ta_City.objects.using(self._current_app_schema()).filter(status=1).values('name')[
        #                   max(0,vys_page.get_offset()-len(frequent_city)):vys_page.get_query_limit()-len(frequent_city)]


            frequent_client_data=[]
            for each_client in frequent_city:
                frequent_client_data.append(each_client['client'])
        api_service = ApiService(self._scope())
        all_client=api_service.frequent_clientlist_ta(vys_page,query,frequent_client_data)
        return all_client


    def frequent_client_2(self,request,employee,vys_page,query):

        frequent_client_data=None
        if vys_page.index == 1 and query is None:
            frequent_city=FrequentData.objects.using(self._current_app_schema()).filter(employee=employee).exclude(client_count=0).values(
                'client').order_by("-latest_date",'-client_count')[:3]

            frequent_client_data=[]
            for each_client in frequent_city:
                frequent_client_data.append(each_client['client'])
        api_service = ApiService(self._scope())
        all_client=api_service.frequent_clientlist_ta(vys_page,query,frequent_client_data)
        return all_client


    def frequent_data_insert(self):
        past_data=FrequentData.objects.using(self._current_app_schema()).filter()
        if len(past_data)==0:
            frequent_data=TourDetail.objects.using(self._current_app_schema()).filter(tour__tour_status=3)
            for each_data in frequent_data:
                service=TourApprovedby(self._scope())
                service.insert_frequent_data(each_data.tour.id)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
            return error_obj


    def team_update(self):
        past_data=TourRequestmodel.objects.using(self._current_app_schema()).filter(Q(team=0) | Q(sub_team=0))
        for each in past_data:

            emp_dept = EmployeeDepartmentPermission.objects.using("default").filter(
                employee_id=each.empgid).order_by("department_id")
            if len(emp_dept)==0:
                team_name = 0
                sub_team_name = 0
            else:

                team = Department.objects.using("default").get(id=(emp_dept.first()).department_id)
                sub_team = Department.objects.using("default").get(id=(emp_dept.last()).department_id)
                team_name = team.id
                sub_team_name = sub_team.id

            TourRequestmodel.objects.using(self._current_app_schema()).filter(id=each.id).update(team=team_name,sub_team=sub_team_name)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj
        # else:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
        #     return error_obj


    def edit_history(self,data,tour_id,action,emp_id):
        TravelEditHistory.objects.using(self._current_app_schema()).create(tour_id=tour_id,data=data,action=action,created_by=emp_id)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj


    def edit_history_get(self,tour_id,action):
        condition=Q(tour_id=tour_id)
        if action!=0:
            condition&= Q(action=action)
        history_data=TravelEditHistory.objects.using(self._current_app_schema()).filter(condition)
        arr = NWisefinList()
        for each_history in history_data:
            his_data = TourMakerResponse()
            his_data.set_id(each_history.id)
            his_data.set_tour_id(each_history.tour_id)
            his_data.set_history_data(json.loads(each_history.data))
            his_data.set_ref_type(each_history.ref_type)
            his_data.set_action(each_history.action)
            his_data.set_status(each_history.status)
            his_data.set_created_by(each_history.created_by)
            his_data.set_entity_id(each_history.entity_id)
            arr.append(his_data)
        return arr









