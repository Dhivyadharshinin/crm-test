import json
import traceback
from datetime import datetime, timedelta

import numpy as np
from django.db.models import Q
import pandas as pd

from docservice.service.documentservice import DocumentsService
from nwisefin.settings import logger
from taservice.data.request.tourmaker import Booking
from taservice.data.response.tourmaker import Doc_response
from taservice.models.tamodels import BusBookingInfo, CabBookingInfo, AirBookingInfo, TrainBookingInfo, \
    AccomodationBookingInfo, CabBookingDetails, BusBookingDetails, AirBookingDetails, TrainBookingDetails, \
    AccomodationBookingDetails, TourRequest, TourDetail, TravelHistory, BookingHistory, CabMapping,TADocuments

# AirMapping,TrainMapping
from taservice.data.request.travelrequirement import Cab_request, Bus_request, Train_request, Air_request, \
    AccomodationBooking_Request
# from taservice.service.tourmaker import TourMaker
from taservice.service.ta_email import ta_email
from taservice.util.ta_util import App_type, Filterstatus, Travel_requirements, Validation, Status, App_level, \
    Timecalculation, TADocUtil, DocModule, TourRequest_BookingStatus, Requirements_booking_status, Requirements_official
from taservice.data.response.travelrequirement import Cab_response, Bus_response, Air_response, Train_response, \
    AccomodationBooking_Response, All_requirement
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.data.response.nwisefinlist  import NWisefinList
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.ta_api_service import ApiService
time_function=Timecalculation()

class Cab_requirement(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)



    def cab_data(self,data,employee_id,detail_id):
        obj = Cab_request(data)

        if not obj.get_id() is None:
            cab_data=CabBookingInfo.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=obj.get_id())
            if cab_data.booking_status not in [Requirements_booking_status.booked,Requirements_booking_status.cancelled]:
                allowance = CabBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=obj.get_id()).update(
                    from_time=obj.get_from_time(),
                    to_time=obj.get_to_time(),
                    from_place=obj.get_from_place(),
                    to_place=obj.get_to_place(),
                    ref_no=obj.get_ref_no(),
                    ref_type=obj.get_ref_type(),
                    comments=obj.get_comments(),
                    travel_type_cab=obj.travel_type_cab,
                    updated_by=employee_id,
                    updated_date=datetime.now())
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj



        else:
            allowance =CabBookingInfo.objects.using(self._current_app_schema()).create(
                from_time=obj.get_from_time(),
                to_time=obj.get_to_time(),
                from_place=obj.get_from_place(),
                to_place=obj.get_to_place(),
                ref_no=obj.get_ref_no(),
                ref_type=obj.get_ref_type(),
                comments=obj.get_comments(),
                travel_detail_id=detail_id,
                travel_type_cab=obj.travel_type_cab,
                created_by=employee_id,
                created_date=datetime.now(),
                entity_id=self._entity_id())
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            return success_obj



    def get_cab(self,id):
        obje = CabBookingInfo.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=id)
        resp_list = NWisefinList()
        temp = Cab_response()
        temp.set_id(obje.id)
        temp.set_from_time(obje.from_time)
        temp.set_to_time(obje.to_time)
        temp.set_from_place(obje.from_place)
        temp.set_to_place(obje.to_place)
        temp.set_ref_no(obje.ref_no)
        temp.set_ref_type(obje.ref_type)
        temp.set_travel_detail(obje.travel_detail_id)
        temp.set_booking_status(obje.booking_status)
        temp.set_comments(obje.comments)
        temp.set_created_by(obje.created_by)
        temp.set_created_date(obje.created_date)
        temp.set_updated_by(obje.updated_by)
        temp.set_updated_date(obje.updated_date)
        temp.set_status(obje.status)
        resp_list.append(temp)
        return resp_list



    def fetch_cab(self):
        cab_data = CabBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),status=1).all()
        resp_list = NWisefinList()
        for eachdata in cab_data:
            temp = Cab_response()
            temp.set_id(eachdata.id)
            temp.set_from_time(eachdata.from_time)
            temp.set_to_time(eachdata.to_time)
            temp.set_from_place(eachdata.from_place)
            temp.set_to_place(eachdata.to_place)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            # temp.set_travel_detail(eachdata.travel_detail)
            temp.set_booking_status(eachdata.booking_status)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_comments(eachdata.comments)
            temp.set_created_by(eachdata.created_by)
            temp.set_created_date(eachdata.created_date)
            temp.set_updated_by(eachdata.updated_by)
            temp.set_updated_date(eachdata.updated_date)
            temp.set_status(eachdata.status)

            resp_list.append(temp)
        return resp_list


    def cab_detail_get(self,detail_id,request):
        cab_data = CabBookingInfo.objects.using(self._current_app_schema()).filter(travel_detail_id=detail_id,entity_id=self._entity_id(),status=1).all()
        resp_list = NWisefinList()
        for eachdata in cab_data:
            temp = Cab_response()
            temp.set_id(eachdata.id)
            temp.set_booking_needed(Travel_requirements.cab)
            temp.set_from_time(eachdata.from_time)
            temp.set_to_time(eachdata.to_time)
            temp.set_from_place(eachdata.from_place)
            temp.set_to_place(eachdata.to_place)
            temp.set_ref_no(eachdata.ref_no)
            # from taservice.service.tourmaker import TourMaker as tour_maker
            tour_maker=Booking_requirement(self._scope())
            doc_get=tour_maker.fetch_tadoc(request, None, None, Travel_requirements.cab, eachdata.id,1)
            data=json.loads(doc_get)
            details=[]
            if "data" in data:
                details=data["data"]
            temp.set_file_detail(details)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_comments(eachdata.comments)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_booking_status(eachdata.booking_status)
            temp.set_status(eachdata.status)
            temp.set_travel_type_cab(eachdata.travel_type_cab)
            cab_type_name=self.get_cab_type_name(eachdata.travel_type_cab)
            temp.set_travel_type_cab_value(cab_type_name)
            temp.set_created_date_time(eachdata.created_date)
            api_service = ApiService(self._scope())
            booked_by = api_service.employee_details_get(eachdata.booked_by, request)
            temp.set_booked_by(booked_by)

            resp_list.append(temp)
        return resp_list

    def get_cab_type_name(self,no):
        if no==1:
            return "Airport / Station transfers"
        elif no ==2:
            return "Local usage / Disposal"
        elif no ==3:
            return "Outstation travel"
        else:
            return None


    def Cab_delete(self, id):
        try:
            resp_obj = CabBookingInfo.objects.using(self._current_app_schema()).filter(id=id, entity_id=self._entity_id()).update(status=0)
            # return resp_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj




    def cab_data_admin(self,request,data,employee_id):
        obj = Cab_request(data)
        booking_service = Booking_requirement(self._scope())
        obj=booking_service.millisecond_conversion(obj)
        # validations = booking_service.admin_booking_vali(data)
        # if validations == False:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.BOOKING)
        #     return error_obj
        try:
            # cab_data = CabBookingInfo.objects.using(self._current_app_schema()).get(id=obj.get_requirement_id())
            # detail_id=cab_data.travel_detail_id
            # tour_id=cab_data.travel_detail.tour.id
            data['booking_needed'] = Travel_requirements.cab
            bookinghistory_id=None
            no_of_booking = len(obj.get_requirement_id())

            # booking_service=Booking_requirement(self._scope())
            #
            # booking_val = booking_service.booking_validations(tour_id, employee_id, detail_id, obj)
            # booking_val = booking_service.booking_validations(tour_id, employee_id, detail_id, obj)
            # if isinstance(booking_val, NWisefinError):
            #     return booking_val
            # if int(obj.booking_needed_id) == 2 and int(obj.travel_type_cab) == 1:
            #     if obj.comments == None:
            #         error_obj = NWisefinError()
            #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #         error_obj.set_description(ErrorDescription.COMMENT_CAB)
            #         return error_obj
            if  obj.get_from_place() == None:
                error_obj=NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_BOOKING_DATA)
                return error_obj
            for i in range(no_of_booking):

                cab_data = CabBookingInfo.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=obj.requirement_id[i])
                detail_id=cab_data.travel_detail_id
                tour_id=cab_data.travel_detail.tour.id
                obj.official = cab_data.travel_detail.official
                booking_val = booking_service.booking_validations(tour_id, employee_id, detail_id, obj)
                if isinstance(booking_val, NWisefinError):
                    return booking_val
                if  cab_data.booking_status == TourRequest_BookingStatus.Reserved:
                    if cab_data.booked_by!=employee_id:
                        error_obj=NWisefinError()
                        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        error_obj.set_description(ErrorDescription.THIS_BOOKING_IS_RESERVED)
                        return error_obj
            Tour_service = Booking_requirement(self._scope())
            for i in range(len(data['requirement_id'])):
                if len(request.FILES) != 0:
                    params = {}
                    params['requirement_type'] = Travel_requirements.cab
                    params['requirement_id'] = data['requirement_id'][i]
                    params['ref_type'] = TADocUtil.TOUR
                    doc_serv = Tour_service.insert_tadoc(request, params)
                    print(params)
                    if isinstance(doc_serv, NWisefinError):
                        return doc_serv

                bookinghistory_get = CabMapping.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(),
                    requirement_id=data['requirement_id'][i])
                if len(bookinghistory_get) != 0:
                    bookinghistoryid = bookinghistory_get.last()
                    bookinghistory_id = bookinghistoryid.BookingDetailId
                    admin_booking_id = bookinghistory_id
            cost_per_head=obj.get_ticket_amount()/no_of_booking
            if  bookinghistory_id is not None:
                allowance = CabBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=bookinghistory_id).update(
                    from_time=obj.get_from_time(),
                    to_time=obj.get_to_time(),
                    from_place=obj.get_from_place(),
                    to_place=obj.get_to_place(),
                    ref_no=obj.get_ref_no(),
                    ref_type=obj.get_ref_type(),
                    booking_status=obj.get_booking_status(),
                    cost_per_head=cost_per_head,
                    booked_no=no_of_booking,
                    # travel_detail_id=detail_id,
                    comments=obj.get_comments(),
                    updated_by=employee_id,
                    updated_date=datetime.now(),
                    # requirement_id=obj.get_requirement_id(),
                    ticket_amount = obj.get_ticket_amount(),
                    ticket_amount_personal = obj.ticket_amount_personal,
                    official = obj.official,
                    vendor_name=obj.get_vendor_name(),
                    ticket_no=obj.get_ticket_no(),
                    class_of_travel=obj.get_class_of_travel(),
                    PNR=obj.PNR,
                    fare_quoted=obj.fare_quoted,
                    issuance_type=obj.issuance_type,
                    website=obj.website,
                    travel_type_cab=obj.travel_type_cab,
                    booking_date=datetime.now(),
                    cab_number=obj.get_cab_number())




            else:
                allowance =CabBookingDetails.objects.using(self._current_app_schema()).create(
                    from_time=obj.get_from_time(),
                    to_time=obj.get_to_time(),
                    from_place=obj.get_from_place(),
                    to_place=obj.get_to_place(),
                    ref_no=obj.get_ref_no(),
                    ref_type=obj.get_ref_type(),
                    comments=obj.get_comments(),
                    booking_status=obj.get_booking_status(),
                    cost_per_head=cost_per_head,
                    booked_no=no_of_booking,
                    # travel_detail_id=detail_id,
                    # requirement_id=obj.get_requirement_id(),
                    created_by=employee_id,
                    created_date=datetime.now(),
                    entity_id=self._entity_id(),
                    ticket_amount = obj.get_ticket_amount(),
                    ticket_amount_personal = obj.ticket_amount_personal,
                    official = obj.official,
                    vendor_name=obj.get_vendor_name(),
                    ticket_no=obj.get_ticket_no(),
                    class_of_travel=obj.get_class_of_travel(),
                    PNR=obj.PNR,
                    fare_quoted=obj.fare_quoted,
                    issuance_type=obj.issuance_type,
                    website=obj.website,
                    travel_type_cab=obj.travel_type_cab,
                    booking_date=datetime.now(),
                    cab_number=obj.get_cab_number())

                admin_booking_id=allowance.id

            for i in range(no_of_booking):

                cab_data = CabBookingInfo.objects.using(self._current_app_schema()).get(id=obj.requirement_id[i])
                detail_id=cab_data.travel_detail_id
                tour_id=cab_data.travel_detail.tour.id

                booking_service.insert_booking_data_cab(data, detail_id, employee_id,obj.requirement_id[i])

                booking_service.insert_cab_mapping(data, detail_id, employee_id,obj.requirement_id[i],admin_booking_id)

                tour_dtl_arr = []
                dtl_data = TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                       tour_id=tour_id)
                for each_data in dtl_data:
                    tour_dtl_arr.append(each_data.id)
                booking_service.book_cab_multiple(obj, tour_dtl_arr, tour_id,obj.requirement_id[i])

                # bookinghistory_get = CabBookingDetails.objects.using(self._current_app_schema()).filter(
                #     entity_id=self._entity_id(),
                #     requirement_id=obj.requirement_id)
                # if len(bookinghistory_get) != 0:
                #     bookinghistoryid = bookinghistory_get.last()
                #     bookinghistory_id = bookinghistoryid.id

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            return success_obj

        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            exc=traceback.format_exc()
            logger.info('ta_ cab_data_admin- ' + str(e)+str(exc))
            return error_obj

    def get_cab_admin(self,id):

        obje = CabBookingDetails.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=id)
        resp_list = NWisefinList()

        temp = Cab_response()
        temp.set_id(obje.id)
        temp.set_from_time(obje.from_time)
        temp.set_to_time(obje.to_time)
        temp.set_from_place(obje.from_place)
        temp.set_to_place(obje.to_place)
        temp.set_ref_no(obje.ref_no)
        temp.set_ref_type(obje.ref_type)
        temp.set_travel_detail(obje.travel_detail_id)
        temp.set_booking_status(obje.booking_status)
        temp.set_comments(obje.comments)
        temp.set_created_by(obje.created_by)
        temp.set_created_date(obje.created_date)
        temp.set_updated_by(obje.updated_by)
        temp.set_updated_date(obje.updated_date)
        temp.set_status(obje.status)
        temp.set_ticket_amount(obje.ticket_amount)
        temp.set_vendor_name(obje.vendor_name)
        temp.set_ticket_no(obje.ticket_no)
        temp.set_class_of_travel(obje.class_of_travel)
        temp.set_cab_number(obje.cab_number)
        resp_list.append(temp)
        return resp_list


    def fetch_cab_admin(self,detail_array,request,all_report,vys_page,from_date,to_date,tour_id):
        condition = Q(entity_id=self._entity_id(), status=1)
        # condition &= ~Q(travel_detail_id=None, requirement_id=None)
        # if tour_id != None:
        #     condition&=Q(travel_detail_id__tour__id=tour_id)
        if from_date != None and to_date != None:
            from_date = datetime.strptime(from_date[:11], "%d-%b-%Y")
            to_date = datetime.strptime(to_date[:11], "%d-%b-%Y")
            to_date = to_date + timedelta(days=1)
            condition &= Q(booking_date__range=[from_date, to_date])

        elif from_date == None and to_date != None:
            to_date = datetime.strptime(to_date[:11], "%d-%b-%Y")
            condition &= Q(booking_date__lte=to_date)

        elif from_date != None and to_date == None:
            from_date = datetime.strptime(from_date[:11], "%d-%b-%Y")
            condition &= Q(booking_date__gte=from_date)
        if all_report==None:
            if detail_array is None:
                cab_data = CabMapping.objects.using(self._current_app_schema()).filter(condition).all().order_by("-booking_date")[vys_page.get_offset():vys_page.get_query_limit()]
            else:
                condition &=Q(travel_detail_id__in = detail_array)
                cab_data = CabMapping.objects.using(self._current_app_schema()).filter(condition).all().order_by("-booking_date")[vys_page.get_offset():vys_page.get_query_limit()]
        else:
            if detail_array is None:
                cab_data = CabMapping.objects.using(self._current_app_schema()).filter(condition).all().order_by("booking_date").values("travel_detail__tour__id","travel_detail__tour__request_date","booking_date","travel_detail__tour__empgid",
                                                                                                                               "travel_detail__purposeofvisit","travel_detail__client","travel_detail__tour__tour_status","travel_detail__tour__week_end_travel","BookingDetailId","id","requirement_id","travel_detail__official")
            else:
                condition &=Q(travel_detail_id__in=detail_array)
                cab_data = CabMapping.objects.using(self._current_app_schema()).filter(condition).all().order_by("booking_date").values("travel_detail__tour__id","travel_detail__tour__request_date","booking_date","travel_detail__tour__empgid",
                                                                                                                               "travel_detail__purposeofvisit","travel_detail__client","travel_detail__tour__tour_status","travel_detail__tour__week_end_travel","BookingDetailId","id","requirement_id","travel_detail__official")
            cab_mapping_frame=pd.DataFrame(cab_data)
            cab_det_arr=cab_mapping_frame["BookingDetailId"].tolist()
            requirement_id_arr=cab_mapping_frame["requirement_id"].tolist()
            cab_details1 = CabBookingDetails.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id(), status=1, id__in=cab_det_arr).values("from_time","to_time","id","from_place","to_place","comments","vendor_name")
            cab_details_frame=pd.DataFrame(cab_details1)
            cab_info1 = CabBookingInfo.objects.using(self._current_app_schema()).filter(id__in=requirement_id_arr).values("travel_type_cab","id")
            cab_info_frame=pd.DataFrame(cab_info1)
            personal_official = {0: "Personal", 1: "Official",2:"Official/Personal"}
            status = {-1: "TRAVEL DEFAULT",
                      0: "TRAVEL DELETED",
                      1: "TRAVEL REQUESTED",
                      2: "TRAVEL PENDING",
                      3: "TRAVEL APPROVED",
                      4: "TRAVEL REJECTED",
                      5: "TRAVEL RETURNED",
                      6: "TRAVEL FORWARDED"}
            cab_type={0:None,1:"Airport / Station transfers",2:"Local usage / Disposal",3:"Outstation travel"}
            final_out = cab_mapping_frame.replace(
                {'travel_detail__tour__tour_status': status,
                 "travel_detail__official": personal_official})
            cab_info2 = cab_info_frame.replace(
                {"travel_type_cab": cab_type})
            cab_details_frame.rename(columns={'id': 'BookingDetailId'},
                                       inplace=True)
            cab_info2.rename(columns={'id': 'requirement_id'},
                                       inplace=True)

            final_out1=final_out.merge(cab_details_frame,on='BookingDetailId',how='left')
            final_out2=final_out1.merge(cab_info2,on='requirement_id',how='left')
            whole_emp_arr=final_out2["travel_detail__tour__empgid"].tolist()
            api_service = ApiService(self._scope())
            emp_det = api_service.employee_details_arr(whole_emp_arr, request)
            emp_frame = pd.DataFrame(emp_det)
            emp_frame.rename(columns={'id': 'travel_detail__tour__empgid'}, inplace=True)
            emp_team_ = api_service.emp_team_arr(whole_emp_arr, request)
            team_frame = pd.DataFrame(emp_team_)
            team_frame1 = team_frame.drop_duplicates(keep='first', subset=['employee_id'])
            team_frame1.rename(
                columns={'employee_id': 'travel_detail__tour__empgid'},
                inplace=True)
            final_out3=final_out2.merge(emp_frame,on='travel_detail__tour__empgid',how='left')
            final_out4=final_out3.merge(team_frame1,on='travel_detail__tour__empgid',how='left')

            final_out4['travel_detail__tour__request_date'] = final_out4['travel_detail__tour__request_date'].apply(
                lambda a: pd.to_datetime(a, errors='coerce').strftime('%d-%b-%Y %H:%M:%S'))
            final_out4['booking date'] = final_out4['booking_date'].apply(
                lambda a: pd.to_datetime(a, errors='coerce').strftime('%d-%b-%Y')if a is not None else None)
            final_out4['from_time'] = final_out4['from_time'].apply(
                lambda a: pd.to_datetime(a, errors='coerce').strftime('%d-%b-%Y')if a is not None else None)
            final_out4['booking time'] = final_out4['booking_date'].apply(
                lambda a: pd.to_datetime(a, errors='coerce').strftime('%H:%M:%S')if a is not None else None)
            final_out4['to_time'] = final_out4['to_time'].apply(
                lambda a: pd.to_datetime(a, errors='coerce').strftime('%H:%M:%S')if a is not None else None)
            client_arr = final_out4["travel_detail__client"].tolist()
            api_service = ApiService(self._scope())
            client_data = api_service.get_client_arr(request, client_arr)
            client_data_frame = pd.DataFrame(client_data)
            client_data_frame.rename(
                columns={'id': 'travel_detail__client'},
                inplace=True)
            final_out5 = final_out4.merge(client_data_frame, on='travel_detail__client', how='left')
            return final_out5

        resp_list = NWisefinList()
        for eachdata in cab_data:
            cab_details=CabBookingDetails.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),status=1,id=eachdata.BookingDetailId)
            booking_table=BookingHistory.objects.using(self._current_app_schema()).filter(reference_id=eachdata.requirement_id,booking_needed=Travel_requirements.cab).last()
            cab_info=CabBookingInfo.objects.using(self._current_app_schema()).get(id=eachdata.requirement_id)
            temp = Cab_response()
            temp.set_id(eachdata.id)
            temp.set_refund_date(booking_table.refund_date)
            temp.set_refund_amount(booking_table.refund_amount)
            temp.set_from_time(cab_details.from_time)
            temp.set_from_date(cab_details.from_time)
            temp.set_from_date_xl(cab_details.from_time)
            temp.set_to_time(cab_details.to_time)
            temp.set_fromtime(cab_details.from_time)
            temp.set_totime(cab_details.to_time)
            temp.set_from_place(cab_details.from_place)
            temp.set_to_place(cab_details.to_place)
            temp.set_ref_no(cab_details.ref_no)
            temp.set_ref_type(cab_details.ref_type)
            temp.set_cancel_reason(booking_table.cancel_reason)
            temp.set_weekend_travel(eachdata.travel_detail.tour.week_end_travel)
            temp.set_travel_detail(eachdata.travel_detail_id)
            if int(eachdata.booking_status)==3:
                temp.set_booking_status("BOOKED")
            elif int(eachdata.booking_status)==2:
                temp.set_booking_status("BOOKING CANCEL REQUESTED")
            elif int(eachdata.booking_status)==4:
                temp.set_booking_status("BOOKING CANCELLED")
            elif int(eachdata.booking_status)==7:
                temp.set_booking_status("BOOKING REJECTED")
            else:
                temp.set_booking_status(None)
            temp.set_comments(cab_details.comments)
            if cab_info.travel_type_cab==1:
                temp.set_cab_type("Airport / Station transfers")
            elif cab_info.travel_type_cab==2:
                temp.set_cab_type("Local usage / Disposal")
            elif cab_info.travel_type_cab==3:
                temp.set_cab_type("Outstation travel")
            else:
                temp.set_cab_type(None)

            temp.set_created_by(eachdata.created_by)
            temp.set_created_date(eachdata.booking_date)
            temp.set_created_date_xl(eachdata.booking_date)
            temp.set_created_time_xl(eachdata.booking_date)
            temp.set_updated_by(eachdata.updated_by)
            temp.set_updated_date(eachdata.updated_date)
            temp.set_request_date(eachdata.travel_detail.tour.request_date)
            temp.set_request_date_xl(eachdata.travel_detail.tour.request_date)
            emp=eachdata.travel_detail.tour.empgid
            api_service=ApiService(self._scope())
            get_team=api_service.emp_team_get(emp,request)
            temp.set_team_name(get_team["team"])
            domestic=eachdata.travel_detail.tour.international_travel
            if domestic==0:
                domestic_trave="Domestic"
            elif domestic==1:
                domestic_trave="International"
            temp.set_domestic(domestic_trave)
            temp.set_status(eachdata.status)
            temp.set_ticket_amount(eachdata.ticket_amount)
            temp.set_ticket_amount_personal(eachdata.ticket_amount_personal)
            temp.set_vendor_name(cab_details.vendor_name)
            temp.set_ticket_no(cab_details.ticket_no)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_purpose_ofvisit(eachdata.travel_detail.purposeofvisit)
            temp.set_tour_id(eachdata.travel_detail.tour.id)
            temp.set_costper_head(cab_details.cost_per_head)
            client_data=api_service.get_client( request, eachdata.travel_detail.client)
            temp.set_client(client_data.client_name)

            emp_get=api_service.employee_details_get(eachdata.travel_detail.tour.empgid,request)
            trav=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=eachdata.travel_detail.tour.id,applevel=App_level.FIRST_LEVEL,status=Status.APPROVED,request_type=App_type.TOUR).last()
            appr=0
            if trav.onbehalfof_approval!=0:
                appr=trav.onbehalfof_approval
            else:
                appr=trav.approvedby
            if appr!=0:
                approver_get = api_service.employee_details_get(appr, request)
                temp.set_approvedby(approver_get.full_name)
                temp.set_empcode(emp_get.code)
                temp.set_empname(emp_get.full_name)
            else:
                temp.set_approvedby(None)
                temp.set_empcode(None)
                temp.set_empname(None)
            from_time = cab_details.from_time
            created_date = cab_details.created_date
            if from_time!=None:
                duration_days = ((created_date-from_time).days)
            else:
                duration_days=None
            temp.set_difference_indays(duration_days)
            temp.set_class_of_travel(cab_details.class_of_travel)
            personal=eachdata.travel_detail.official
            if int(personal)==1:
                temp.set_personal_official("Official")
            elif int(personal)==0:
                temp.set_personal_official("Personal")
            elif int(personal)==2:
                temp.set_personal_official("Official/Personal")
            else:
                temp.set_personal_official(None)


            temp.set_cab_number(cab_details.cab_number)
            temp.set_booking_needed("CAB BOOKING")
            temp.set_pnr_no(cab_details.PNR)
            status = eachdata.travel_detail.tour.tour_status
            if status == 3:
                temp.set_tour_status("TRAVEL APPROVED")
            temp.set_costper_head(cab_details.cost_per_head)
            temp.set_fare_quoted(cab_details.fare_quoted)
            temp.set_difference_in_amount(cab_details.difference_in_amount)
            temp.set_issuance_type(cab_details.issuance_type)
            temp.set_loss_of_cancelation(booking_table.loss_of_cancelation)
            temp.set_website(cab_details.website)
            temp.set_cancelled_date(booking_table.cancelled_date)
            if all_report == None:
                resp_list.append(temp)
                vpage = NWisefinPaginator(cab_data, vys_page.get_index(), 10)
                resp_list.set_pagination(vpage)
            else:
                resp_list.append(temp)
        return resp_list

    def fetch_cab_admin_req(self,requirement_id):
        mapping_data=CabMapping.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                           requirement_id=requirement_id,
                                                                           status=1).last()

        cab_data = CabBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=
                                                                                      self._entity_id(),id=mapping_data.BookingDetailId,status=1).all()
        booking_his = BookingHistory.objects.using(self._current_app_schema()).filter(reference_id=requirement_id,entity_id=self._entity_id(),
                                                                                      booking_needed=Travel_requirements.cab).last()
        resp_list = NWisefinList()
        temp1 = All_requirement()
        cancel_detail = []
        if booking_his.booking_status == 4:
            temp1.set_cancelled_date(booking_his.cancelled_date)
            temp1.set_refund_date(booking_his.refund_date)
            temp1.set_cancel_reschedule(booking_his.cancel_reschedule)
            temp1.set_cancel_reason(booking_his.cancel_reason)
            temp1.set_refund_amount(booking_his.refund_amount)
            temp1.set_fare_difference(booking_his.fare_difference)
            temp1.set_loss_of_cancelation(booking_his.loss_of_cancelation)
            cancel_detail.append(temp1)
        for eachdata in cab_data:
            temp = Cab_response()
            temp.set_id(eachdata.id)
            temp.set_from_time(eachdata.from_time)
            temp.set_to_time(eachdata.to_time)
            temp.set_from_place(eachdata.from_place)
            temp.set_to_place(eachdata.to_place)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_travel_detail(mapping_data.travel_detail_id)
            temp.set_booking_status(eachdata.booking_status)
            temp.set_comments(eachdata.comments)
            temp.set_created_by(eachdata.created_by)
            temp.set_created_date(eachdata.created_date)
            temp.set_updated_by(eachdata.updated_by)
            temp.set_updated_date(eachdata.updated_date)
            temp.set_status(eachdata.status)
            temp.set_ticket_amount(mapping_data.ticket_amount)
            temp.set_ticket_amount_personal(mapping_data.ticket_amount_personal)
            temp.set_utilised_status(mapping_data.utilised_status)
            temp.set_noshow_reason(mapping_data.noshow_reason)
            temp.set_admin_paid(mapping_data.admin_paid)
            temp.set_vendor_name(eachdata.vendor_name)
            temp.set_ticket_no(eachdata.ticket_no)
            temp.set_class_of_travel(eachdata.class_of_travel)
            temp.set_PNR(eachdata.PNR)
            temp.set_cab_number(eachdata.cab_number)
            temp.set_cost_per_head(eachdata.cost_per_head)
            temp.set_fare_quoted(eachdata.fare_quoted)
            temp.set_difference_in_amount(eachdata.difference_in_amount)
            temp.set_issuance_type(eachdata.issuance_type)
            temp.set_website(eachdata.website)
            temp.set_booking_date(eachdata.booking_date)
            temp.set_cancel_data(cancel_detail)
            temp.set_travel_type_cab(eachdata.travel_type_cab)
            cab_type_name=self.get_cab_type_name(eachdata.travel_type_cab)
            temp.set_travel_type_cab_value(cab_type_name)
            resp_list.append(temp)
        return resp_list

    def cab_detail_get_admin(self,detail_id):
        mapping_data = CabMapping.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),travel_detail__in=detail_id,
                                                                                   status=1)
        # mapping_id=[]
        resp_list = NWisefinList()
        for each_mapping in mapping_data:
            # mapping_id.append(each_mapping.BookingDetailId)
            eachdata = CabBookingDetails.objects.using(self._current_app_schema()).get(id=each_mapping.BookingDetailId,entity_id=self._entity_id(),status=1)

        # for eachdata in cab_data:
            temp = Cab_response()
            temp.set_id(eachdata.id)
            temp.set_booking_needed(Travel_requirements.cab)
            temp.set_from_time(eachdata.from_time)
            temp.set_to_time(eachdata.to_time)
            temp.set_from_place(eachdata.from_place)
            temp.set_to_place(eachdata.to_place)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_comments(eachdata.comments)
            temp.set_travel_detail(each_mapping.travel_detail_id)
            temp.set_booking_status(eachdata.booking_status)
            temp.set_status(eachdata.status)
            temp.set_created_date_time(eachdata.created_date)
            temp.set_ticket_amount(each_mapping.ticket_amount)
            temp.set_ticket_amount_personal(each_mapping.ticket_amount_personal)
            temp.set_vendor_name(eachdata.vendor_name)
            temp.set_ticket_no(eachdata.ticket_no)
            temp.set_class_of_travel(eachdata.class_of_travel)
            temp.set_cab_number(eachdata.cab_number)
            temp.set_utilised_status(each_mapping.utilised_status)
            temp.set_noshow_reason(each_mapping.noshow_reason)
            temp.set_admin_paid(each_mapping.admin_paid)
            temp.set_vendor_name(eachdata.vendor_name)
            temp.set_ticket_no(eachdata.ticket_no)
            temp.set_class_of_travel(eachdata.class_of_travel)
            temp.set_PNR(eachdata.PNR)
            temp.set_cab_number(eachdata.cab_number)
            temp.set_cost_per_head(eachdata.cost_per_head)
            temp.set_fare_quoted(eachdata.fare_quoted)
            temp.set_difference_in_amount(eachdata.difference_in_amount)
            temp.set_issuance_type(eachdata.issuance_type)
            temp.set_website(eachdata.website)
            temp.set_booking_date(eachdata.booking_date)
            temp.set_travel_type_cab(eachdata.travel_type_cab)
            cab_type_name=self.get_cab_type_name(eachdata.travel_type_cab)
            temp.set_travel_type_cab_value(cab_type_name)
            resp_list.append(temp)
        return resp_list

    def cab_detail_get_admin_ecf(self,detail_id,admin_paid):
        mapping_data = CabMapping.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),travel_detail__in=detail_id,
                                                                                   status=1,admin_paid=admin_paid)
        # mapping_id=[]
        resp_list = NWisefinList()
        for each_mapping in mapping_data:
            # mapping_id.append(each_mapping.BookingDetailId)
            eachdata = CabBookingDetails.objects.using(self._current_app_schema()).get(id=each_mapping.BookingDetailId,entity_id=self._entity_id(),status=1)

        # for eachdata in cab_data:
            temp = Cab_response()
            temp.set_id(eachdata.id)
            temp.set_booking_needed(Travel_requirements.cab)
            temp.set_from_time(eachdata.from_time)
            temp.set_to_time(eachdata.to_time)
            temp.set_from_place(eachdata.from_place)
            temp.set_to_place(eachdata.to_place)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_comments(eachdata.comments)
            temp.set_travel_detail(each_mapping.travel_detail_id)
            temp.set_booking_status(eachdata.booking_status)
            temp.set_status(eachdata.status)
            temp.set_created_date_time(eachdata.created_date)
            temp.set_ticket_amount(eachdata.ticket_amount)
            temp.set_vendor_name(eachdata.vendor_name)
            temp.set_ticket_no(eachdata.ticket_no)
            temp.set_class_of_travel(eachdata.class_of_travel)
            temp.set_cab_number(eachdata.cab_number)
            resp_list.append(temp)
        return resp_list


    def Cab_delete_admin(self, id):
        try:
            resp_obj = CabBookingDetails.objects.using(self._current_app_schema()).filter(id=id, entity_id=self._entity_id()).update(status=0)
            # return resp_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj



class Bus_requirement(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)



    def insert_bus_data(self,data,employee_id,detail_id):
        obj = Bus_request(data)

        if not obj.get_id() is None:
            # try:
            acc_data=BusBookingInfo.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=obj.get_id())
            if acc_data.booking_status not in [Requirements_booking_status.booked,Requirements_booking_status.cancelled]:
                allowance = BusBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=obj.get_id()).update(
                    from_time=obj.get_from_time(),
                    to_time=obj.get_to_time(),
                    from_place=obj.get_from_place(),
                    to_place=obj.get_to_place(),
                    ref_no=obj.get_ref_no(),
                    ref_type=obj.get_ref_type(),
                    comments=obj.get_comments(),
                    updated_by=employee_id,updated_date=datetime.now())
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj


        else:
            allowance = BusBookingInfo.objects.using(self._current_app_schema()).create(
                from_time=obj.get_from_time(),
                to_time=obj.get_to_time(),
                from_place=obj.get_from_place(),
                to_place=obj.get_to_place(),
                ref_no=obj.get_ref_no(),
                ref_type=obj.get_ref_type(),
                comments=obj.get_comments(),
                travel_detail_id=detail_id,
                created_by=employee_id,
                created_date=datetime.now(),entity_id=self._entity_id())
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            return success_obj



    def get_Bus(self,id):
        condition = Q(status=Filterstatus.one, id=id, entity_id=self._entity_id())
        obje= BusBookingInfo.objects.using(self._current_app_schema()).get(condition)
        resp_list = NWisefinList()
        temp = Bus_response()
        temp.set_id(obje.id)
        temp.set_from_time(obje.from_time)
        temp.set_to_time(obje.to_time)
        temp.set_from_place(obje.from_place)
        temp.set_to_place(obje.to_place)
        temp.set_comments(obje.comments)
        temp.set_ref_no(obje.ref_no)
        temp.set_ref_type(obje.ref_type)
        temp.set_travel_detail(obje.travel_detail_id)
        temp.set_booking_status(obje.booking_status)
        temp.set_status(obje.status)
        temp.set_created_date(obje.created_date)
        resp_list.append(temp)
        return resp_list

    def fetch_Bus(self):
        obje = BusBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),status=1).all()
        resp_list = NWisefinList()
        for eachdata in obje:
            temp = Bus_response()
            temp.set_id(eachdata.id)
            temp.set_from_time(eachdata.from_time)
            temp.set_to_time(eachdata.to_time)
            temp.set_from_place(eachdata.from_place)
            temp.set_to_place(eachdata.to_place)
            temp.set_comments(eachdata.comments)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_booking_status(eachdata.booking_status)
            temp.set_created_by(eachdata.created_by)
            temp.set_created_date(eachdata.created_date)
            temp.set_updated_by(eachdata.updated_by)
            temp.set_updated_date(eachdata.updated_date)
            temp.set_status(eachdata.status)
            resp_list.append(temp)
        return resp_list


    def bus_details_get(self,detail_id,request):
        obje = BusBookingInfo.objects.using(self._current_app_schema()).filter(travel_detail_id=detail_id,entity_id=self._entity_id(),status=1).all()
        resp_list = NWisefinList()
        for eachdata in obje:
            temp = Bus_response()
            temp.set_id(eachdata.id)
            temp.set_booking_needed(Travel_requirements.bus)
            temp.set_from_time(eachdata.from_time)
            temp.set_to_time(eachdata.to_time)
            temp.set_from_place(eachdata.from_place)
            temp.set_to_place(eachdata.to_place)
            tour_maker = Booking_requirement(self._scope())
            doc_get = tour_maker.fetch_tadoc(request, None, None, Travel_requirements.bus, eachdata.id, 1)
            data = json.loads(doc_get)
            details = []
            if "data" in data:
                details = data["data"]
            temp.set_file_detail(details)
            temp.set_comments(eachdata.comments)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_booking_status(eachdata.booking_status)
            temp.set_status(eachdata.status)
            temp.set_created_date_time(eachdata.created_date)
            api_service = ApiService(self._scope())
            booked_by = api_service.employee_details_get(eachdata.booked_by, request)
            temp.set_booked_by(booked_by)
            resp_list.append(temp)
        return resp_list


    def bus_delete(self, id):
        try:
            resp_obj = BusBookingInfo.objects.using(self._current_app_schema()).filter(id=id, entity_id=self._entity_id()).update(status=0)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj



    def insert_bus_data_admin(self,request,data,employee_id):
        obj = Bus_request(data)
        booking_service = Booking_requirement(self._scope())
        obj = booking_service.millisecond_conversion(obj)
        # booking_service = Booking_requirement(self._scope())
        # validations = booking_service.admin_booking_vali(data)
        # if validations == False:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.BOOKING)
        #     return error_obj
        try:
            bus_data = BusBookingInfo.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=obj.get_requirement_id())
            detail_id=bus_data.travel_detail_id
            obj.official=bus_data.travel_detail.official
            tour_id = bus_data.travel_detail.tour.id

            # booking_service = Booking_requirement(self._scope())
            data['booking_needed']=Travel_requirements.bus

            booking_val = booking_service.booking_validations(tour_id, employee_id, detail_id, obj)
            if isinstance(booking_val, NWisefinError):
                return booking_val
            if  bus_data.booking_status == TourRequest_BookingStatus.Reserved:
                if bus_data.booked_by!=employee_id:
                    error_obj=NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.THIS_BOOKING_IS_RESERVED)
                    return error_obj
            if  obj.get_from_place() == None:
                error_obj=NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_BOOKING_DATA)
                return error_obj
            if obj.get_ticket_amount() == None:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_BOOKING_DATA)
                return error_obj

            booking_data=booking_service.insert_booking_data(data, detail_id, employee_id)
            tour_dtl_arr = []
            dtl_data = TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                   tour_id=tour_id)
            for each_data in dtl_data:
                tour_dtl_arr.append(each_data.id)
            booking_service.book_bus(obj, tour_dtl_arr, tour_id)
            bookinghistory_id = None

            bookinghistory_get = BusBookingDetails.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id(),
                requirement_id=obj.requirement_id)
            if len(bookinghistory_get) != 0:
                bookinghistoryid = bookinghistory_get.last()
                bookinghistory_id = bookinghistoryid.id
            Tour_service =  Booking_requirement(self._scope())
            if len(request.FILES) != 0:
                params={}
                params['requirement_type']=Travel_requirements.bus
                params['requirement_id']=obj.get_requirement_id()
                params['ref_type']=TADocUtil.TOUR
                doc_serv=Tour_service.insert_tadoc(request,params)
                if isinstance(doc_serv, NWisefinError):
                    return doc_serv



            if not bookinghistory_id is None:
                # try:
                allowance = BusBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=bookinghistory_id).update(
                    from_time=obj.get_from_time(),
                    to_time=obj.get_to_time(),
                    from_place=obj.get_from_place(),
                    to_place=obj.get_to_place(),
                    ref_no=obj.get_ref_no(),
                    ref_type=obj.get_ref_type(),
                    travel_detail_id=detail_id,
                    booking_status=obj.get_booking_status(),
                    comments=obj.get_comments(),
                    requirement_id=obj.get_requirement_id(),
                    updated_by=employee_id,updated_date=datetime.now(),
                    ticket_amount_personal = obj.ticket_amount_personal,
                    official = obj.official,
                    ticket_amount = obj.get_ticket_amount(),
                    vendor_name=obj.get_vendor_name(),
                    ticket_no=obj.get_ticket_no(),
                    admin_paid=obj.admin_paid,
                    class_of_travel=obj.class_of_travel,
                    bus_number=obj.get_bus_number(),
                    PNR=obj.PNR,
                    fare_quoted=obj.fare_quoted,
                    issuance_type=obj.issuance_type,
                    website=obj.website,
                    booking_date=datetime.now(),
                    seat_number=obj.get_seat_number())
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                return success_obj


            else:
                allowance = BusBookingDetails.objects.using(self._current_app_schema()).create(
                    from_time=obj.get_from_time(),
                    to_time=obj.get_to_time(),
                    from_place=obj.get_from_place(),
                    to_place=obj.get_to_place(),
                    ref_no=obj.get_ref_no(),
                    ref_type=obj.get_ref_type(),
                    comments=obj.get_comments(),
                    booking_status=obj.get_booking_status(),
                    travel_detail_id=detail_id,
                    created_by=employee_id,
                    requirement_id=obj.get_requirement_id(),
                    created_date=datetime.now(),entity_id=self._entity_id(),
                    ticket_amount=obj.get_ticket_amount(),vendor_name=obj.get_vendor_name(),
                    ticket_amount_personal = obj.ticket_amount_personal,
                    official = obj.official,
                    ticket_no=obj.get_ticket_no(),
                    bus_number=obj.get_bus_number(),
                    admin_paid=obj.admin_paid,
                    class_of_travel=obj.class_of_travel,
                    PNR=obj.PNR,
                    fare_quoted=obj.fare_quoted,
                    issuance_type=obj.issuance_type,
                    website=obj.website,
                    booking_date=datetime.now(),
                    seat_number=obj.get_seat_number())
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                return success_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            exc=traceback.format_exc()
            logger.info('ta_ insert_bus_data_admin- ' + str(e)+str(exc))
            return error_obj


    def get_Bus_admin(self,id):
        condition = Q(status=Filterstatus.one, id=id, entity_id=self._entity_id())
        obje= BusBookingDetails.objects.using(self._current_app_schema()).get(condition)
        resp_list = NWisefinList()
        temp = Bus_response()
        temp.set_id(obje.id)
        temp.set_from_time(obje.from_time)
        temp.set_to_time(obje.to_time)
        temp.set_from_place(obje.from_place)
        temp.set_to_place(obje.to_place)
        temp.set_comments(obje.comments)
        temp.set_ref_no(obje.ref_no)
        temp.set_ref_type(obje.ref_type)
        temp.set_travel_detail(obje.travel_detail_id)
        temp.set_booking_status(obje.booking_status)
        temp.set_status(obje.status)
        temp.set_created_date(obje.created_date)
        temp.set_ticket_amount(obje.ticket_amount)
        temp.set_vendor_name(obje.vendor_name)
        temp.set_class_of_travel(obje.class_of_travel)
        temp.set_ticket_no(obje.ticket_no)
        temp.set_bus_number(obje.bus_number)
        temp.set_seat_number(obje.seat_number)
        resp_list.append(temp)
        return resp_list

    def fetch_Bus_admin(self,detail_array,request,all_report,vys_page,from_date,to_date,tour_id):
        condition = Q(entity_id=self._entity_id(), status=1)
        condition &= ~Q(travel_detail_id=None, requirement_id=None)
        if tour_id != None:
            condition &= Q(travel_detail_id__tour__id=tour_id)
        if from_date != None and to_date != None:
            from_date = datetime.strptime(from_date[:11], "%d-%b-%Y")
            to_date = datetime.strptime(to_date[:11], "%d-%b-%Y")
            to_date = to_date + timedelta(days=1)
            condition &= Q(booking_date__range=[from_date, to_date])

        elif from_date == None and to_date != None:
            to_date = datetime.strptime(to_date[:11], "%d-%b-%Y")
            condition &= Q(booking_date__lte=to_date)

        elif from_date != None and to_date == None:
            from_date = datetime.strptime(from_date[:11], "%d-%b-%Y")
            condition &= Q(booking_date__gte=from_date)
        if all_report == None:
            if detail_array is None:
                obje = BusBookingDetails.objects.using(self._current_app_schema()).filter(condition).all().order_by("-booking_date")
            else:
                condition &=Q(travel_detail_id__in=detail_array)
                obje = BusBookingDetails.objects.using(self._current_app_schema()).filter(condition).all().order_by("-booking_date")[
                           vys_page.get_offset():vys_page.get_query_limit()]
        else:
            if detail_array is None:
                obje = BusBookingDetails.objects.using(self._current_app_schema()).filter(condition).all().order_by("booking_date")
            else:
                condition &=Q(travel_detail_id__in=detail_array)

                obje = BusBookingDetails.objects.using(self._current_app_schema()).filter(condition).all().order_by("booking_date")
        resp_list = NWisefinList()
        for eachdata in obje:
            booking_table = BookingHistory.objects.using(self._current_app_schema()).filter(
                reference_id=eachdata.requirement_id, booking_needed=Travel_requirements.bus).last()
            temp = Bus_response()
            temp.set_id(eachdata.id)
            temp.set_refund_date(booking_table.refund_date)
            temp.set_refund_amount(booking_table.refund_amount)
            temp.set_from_time(eachdata.from_time)
            temp.set_to_time(eachdata.to_time)
            temp.set_fromtime(eachdata.from_time)
            temp.set_totime(eachdata.to_time)
            temp.set_from_place(eachdata.from_place)
            temp.set_to_place(eachdata.to_place)
            temp.set_comments(eachdata.comments)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_cancel_reason(booking_table.cancel_reason)
            temp.set_weekend_travel(eachdata.travel_detail.tour.week_end_travel)
            temp.set_travel_detail(eachdata.travel_detail_id)
            if int(eachdata.booking_status) == 3:
                temp.set_booking_status("BOOKED")
            elif int(eachdata.booking_status) == 2:
                temp.set_booking_status("BOOKING CANCEL REQUESTED")
            elif int(eachdata.booking_status) == 4:
                temp.set_booking_status("BOOKING CANCELLED")
            elif int(eachdata.booking_status)==7:
                temp.set_booking_status("BOOKING REJECTED")
            else:
                temp.set_booking_status(None)
            temp.set_created_by(eachdata.created_by)
            temp.set_created_date(eachdata.booking_date)
            temp.set_created_date_xl(eachdata.booking_date)
            temp.set_created_time_xl(eachdata.booking_date)
            temp.set_updated_by(eachdata.updated_by)
            api_service = ApiService(self._scope())
            emp_get = api_service.employee_details_get(eachdata.travel_detail.tour.empgid,request)
            approver_get = api_service.employee_details_get(booking_table.created_by, request)
            temp.set_approvedby(approver_get.full_name)
            temp.set_empcode(emp_get.code)
            temp.set_empname(emp_get.full_name)
            emp = eachdata.travel_detail.tour.empgid
            api_service = ApiService(self._scope())
            get_team = api_service.emp_team_get(emp, request)
            temp.set_team_name(get_team["team"])
            domestic = eachdata.travel_detail.tour.international_travel
            if domestic == 0:
                domestic_trave = "Domestic"
            elif domestic == 1:
                domestic_trave = "International"
            temp.set_domestic(domestic_trave)
            temp.set_updated_date(eachdata.updated_date)
            temp.set_status(eachdata.status)
            # client_name = Client.objects.using(self._current_app_schema()).get(id=eachdata.travel_detail.client)
            # temp.set_client(client_name.name)

            client_data=api_service.get_client( request, eachdata.travel_detail.client)
            temp.set_client(client_data.client_name)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_tour_id(eachdata.travel_detail.tour.id)
            temp.set_ticket_amount(eachdata.ticket_amount)
            temp.set_ticket_amount_personal(eachdata.ticket_amount_personal)
            temp.set_vendor_name(eachdata.vendor_name)
            temp.set_class_of_travel(eachdata.class_of_travel)
            status=eachdata.travel_detail.tour.tour_status
            if status==3:
                temp.set_tour_status("TRAVEL APPROVED")
            temp.set_ticket_no(eachdata.ticket_no)
            temp.set_bus_number(eachdata.bus_number)
            temp.set_costper_head(eachdata.ticket_amount)
            temp.set_request_date(eachdata.travel_detail.tour.request_date)
            temp.set_purpose_ofvisit(eachdata.travel_detail.purposeofvisit)
            personal = eachdata.travel_detail.official
            if int(personal) == 1:
                temp.set_personal_official("Official")
            elif int(personal) == 0:
                temp.set_personal_official("Personal")
            elif int(personal)==2:
                temp.set_personal_official("Official/Personal")
            else:
                temp.set_personal_official(None)
            from_time = eachdata.from_time
            created_date = eachdata.created_date
            # startdate = datetime.strptime((from_time[:10]), '%Y-%b-%d').date()
            # enddate = datetime.strptime((created_date[:10]), '%Y-%b-%d').date()
            duration_days = ((created_date-from_time).days)
            temp.set_difference_indays(duration_days)
            temp.set_seat_number(eachdata.seat_number)
            temp.set_booking_needed("BUS BOOKING")
            temp.set_pnr_no(eachdata.PNR)
            temp.set_costper_head(eachdata.cost_per_head)
            temp.set_fare_quoted(eachdata.fare_quoted)
            temp.set_difference_in_amount(eachdata.difference_in_amount)
            temp.set_issuance_type(eachdata.issuance_type)
            temp.set_website(eachdata.website)
            temp.set_cancelled_date(booking_table.cancelled_date)
            temp.set_loss_of_cancelation(booking_table.loss_of_cancelation)
            if all_report == None:
                resp_list.append(temp)
                vpage = NWisefinPaginator(obje, vys_page.get_index(), 10)
                resp_list.set_pagination(vpage)
            else:
                resp_list.append(temp)

        return resp_list

    def fetch_Bus_admin_req(self,requirement_id):
        obje = BusBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),requirement_id=requirement_id,status=1).all()
        resp_list = NWisefinList()
        booking_his = BookingHistory.objects.using(self._current_app_schema()).filter(reference_id=requirement_id,entity_id=self._entity_id(),
                                                                                      booking_needed=Travel_requirements.bus).last()
        resp_list = NWisefinList()
        temp1 = All_requirement()
        cancel_detail = []
        if booking_his.booking_status == 4:
            temp1.set_cancelled_date(booking_his.cancelled_date)
            temp1.set_refund_date(booking_his.refund_date)
            temp1.set_cancel_reschedule(booking_his.cancel_reschedule)
            temp1.set_cancel_reason(booking_his.cancel_reason)
            temp1.set_refund_amount(booking_his.refund_amount)
            temp1.set_fare_difference(booking_his.fare_difference)
            temp1.set_loss_of_cancelation(booking_his.loss_of_cancelation)
            cancel_detail.append(temp1)
        for eachdata in obje:
            temp = Bus_response()
            temp.set_id(eachdata.id)
            temp.set_from_time(eachdata.from_time)
            temp.set_to_time(eachdata.to_time)
            temp.set_from_place(eachdata.from_place)
            temp.set_to_place(eachdata.to_place)
            temp.set_comments(eachdata.comments)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_booking_status(eachdata.booking_status)
            temp.set_created_by(eachdata.created_by)
            temp.set_created_date(eachdata.created_date)
            temp.set_updated_by(eachdata.updated_by)
            temp.set_updated_date(eachdata.updated_date)
            temp.set_status(eachdata.status)
            temp.set_ticket_amount(eachdata.ticket_amount)
            temp.set_ticket_amount_personal(eachdata.ticket_amount_personal)
            temp.set_utilised_status(eachdata.utilised_status)
            temp.set_noshow_reason(eachdata.noshow_reason)
            temp.set_cancel_data(cancel_detail)
            temp.set_admin_paid(eachdata.admin_paid)
            temp.set_vendor_name(eachdata.vendor_name)
            temp.set_ticket_no(eachdata.ticket_no)
            temp.set_class_of_travel(eachdata.class_of_travel)
            temp.set_bus_number(eachdata.bus_number)
            temp.set_seat_number(eachdata.seat_number)
            temp.set_PNR(eachdata.PNR)
            temp.set_cost_per_head(eachdata.cost_per_head)
            temp.set_fare_quoted(eachdata.fare_quoted)
            temp.set_difference_in_amount(eachdata.difference_in_amount)
            temp.set_issuance_type(eachdata.issuance_type)
            temp.set_website(eachdata.website)
            temp.set_booking_date(eachdata.booking_date)
            resp_list.append(temp)
        return resp_list

    def bus_details_get_admin(self,detail_id):
        obje = BusBookingDetails.objects.using(self._current_app_schema()).filter(travel_detail_id__in=detail_id,entity_id=self._entity_id(),status=1).all()
        resp_list = NWisefinList()
        for eachdata in obje:
            temp = Bus_response()
            temp.set_id(eachdata.id)
            temp.set_booking_needed(Travel_requirements.bus)
            temp.set_from_time(eachdata.from_time)
            temp.set_to_time(eachdata.to_time)
            temp.set_from_place(eachdata.from_place)
            temp.set_to_place(eachdata.to_place)
            temp.set_comments(eachdata.comments)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_booking_status(eachdata.booking_status)
            temp.set_status(eachdata.status)
            temp.set_created_date_time(eachdata.created_date)
            temp.set_ticket_amount(eachdata.ticket_amount)
            temp.set_ticket_amount_personal(eachdata.ticket_amount_personal)
            temp.set_vendor_name(eachdata.vendor_name)
            temp.set_class_of_travel(eachdata.class_of_travel)
            temp.set_ticket_no(eachdata.ticket_no)
            temp.set_bus_number(eachdata.bus_number)
            temp.set_seat_number(eachdata.seat_number)
            temp.set_utilised_status(eachdata.utilised_status)
            temp.set_noshow_reason(eachdata.noshow_reason)
            temp.set_admin_paid(eachdata.admin_paid)
            temp.set_vendor_name(eachdata.vendor_name)
            temp.set_ticket_no(eachdata.ticket_no)
            temp.set_class_of_travel(eachdata.class_of_travel)
            temp.set_bus_number(eachdata.bus_number)
            temp.set_seat_number(eachdata.seat_number)
            temp.set_PNR(eachdata.PNR)
            temp.set_cost_per_head(eachdata.cost_per_head)
            temp.set_fare_quoted(eachdata.fare_quoted)
            temp.set_difference_in_amount(eachdata.difference_in_amount)
            temp.set_issuance_type(eachdata.issuance_type)
            temp.set_website(eachdata.website)
            temp.set_booking_date(eachdata.booking_date)
            resp_list.append(temp)
        return resp_list



    def bus_details_get_admin_ecf(self,detail_id,admin_paid):
        obje = BusBookingDetails.objects.using(self._current_app_schema()).filter(travel_detail_id__in=detail_id,entity_id=self._entity_id(),
                                                                                  status=1,admin_paid=admin_paid).all()
        resp_list = NWisefinList()
        for eachdata in obje:
            temp = Bus_response()
            temp.set_id(eachdata.id)
            temp.set_booking_needed(Travel_requirements.bus)
            temp.set_from_time(eachdata.from_time)
            temp.set_to_time(eachdata.to_time)
            temp.set_from_place(eachdata.from_place)
            temp.set_to_place(eachdata.to_place)
            temp.set_comments(eachdata.comments)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_booking_status(eachdata.booking_status)
            temp.set_status(eachdata.status)
            temp.set_created_date_time(eachdata.created_date)
            temp.set_ticket_amount(eachdata.ticket_amount)
            temp.set_vendor_name(eachdata.vendor_name)
            temp.set_class_of_travel(eachdata.class_of_travel)
            temp.set_ticket_no(eachdata.ticket_no)
            temp.set_bus_number(eachdata.bus_number)
            temp.set_seat_number(eachdata.seat_number)
            resp_list.append(temp)
        return resp_list


    def bus_delete_admin(self, id):
        try:
            resp_obj = BusBookingDetails.objects.using(self._current_app_schema()).filter(id=id, entity_id=self._entity_id()).update(status=0)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj



class Air_requirement(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)



    def Air_data(self,data,employee_id,detail_id):
        obj = Air_request(data)

        if not obj.get_id() is None:
            air_data=AirBookingInfo.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=obj.get_id())
            if air_data.booking_status not in [Requirements_booking_status.booked,Requirements_booking_status.cancelled]:
                allowance = AirBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=obj.get_id()).update(
                    from_time=obj.get_from_time(),
                    to_time=obj.get_to_time(),
                    ref_no=obj.get_ref_no(),
                    ref_type=obj.get_ref_type(),
                    from_place=obj.get_from_place(),
                    to_place=obj.get_to_place(),
                    comments=obj.get_comments(),
                    boarding_no=obj.get_boarding_no(),
                    updated_by=employee_id,entity_id=self._entity_id(),
                    updated_date=datetime.now())

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj


        else:
            # try:
            allowance = AirBookingInfo.objects.using(self._current_app_schema()).create(
                from_time=obj.get_from_time(),
                to_time=obj.get_to_time(),
                ref_no=obj.get_ref_no(),
                ref_type=obj.get_ref_type(),
                from_place=obj.get_from_place(),
                to_place=obj.get_to_place(),
                comments=obj.get_comments(),
                boarding_no=obj.get_boarding_no(),
                travel_detail_id=detail_id,
                created_by=employee_id,
                created_date=datetime.now(),entity_id=self._entity_id())

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            return success_obj



    def get_Air(self,id):
        condition = Q(status=Filterstatus.one, id=id, entity_id=self._entity_id())
        obje = AirBookingInfo.objects.using(self._current_app_schema()).get(condition)
        resp_list = NWisefinList()
        temp = Air_response()
        temp.set_id(obje.id)
        temp.set_from_time(obje.from_time)
        temp.set_to_time(obje.to_time)
        temp.set_from_place(obje.from_place)
        temp.set_to_place(obje.to_place)
        temp.set_ref_no(obje.ref_no)
        temp.set_ref_type(obje.ref_type)
        temp.set_travel_detail(obje.travel_detail_id)
        temp.set_booking_status(obje.booking_status)
        temp.set_comments(obje.comments)
        temp.set_boarding_no(obje.boarding_no)
        temp.set_created_by(obje.created_by)
        temp.set_created_date(obje.created_date)
        temp.set_updated_by(obje.updated_by)
        temp.set_updated_date(obje.updated_date)
        temp.set_status(obje.status)
        resp_list.append(temp)
        return resp_list


    def fetch_Air(self):
        obje = AirBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),status=1).all()
        resp_list = NWisefinList()
        resp_list = NWisefinList()
        for eachdata in obje:
            temp = Air_response()
            temp.set_id(eachdata.id)
            temp.set_from_time(eachdata.from_time)
            temp.set_to_time(eachdata.to_time)
            temp.set_from_place(eachdata.from_place)
            temp.set_to_place(eachdata.to_place)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_booking_status(eachdata.booking_status)
            temp.set_comments(eachdata.comments)
            temp.set_boarding_no(eachdata.boarding_no)
            temp.set_created_by(eachdata.created_by)
            temp.set_created_date(eachdata.created_date)
            temp.set_updated_by(eachdata.updated_by)
            temp.set_updated_date(eachdata.updated_date)
            temp.set_status(eachdata.status)
            resp_list.append(temp)
        return resp_list
    def sameday_booking(self,request,from_time,from_place,to_place,booking_type):
        # if booking_type == Travel_requirements.accomodation:
        #     accomodation_data = AccomodationBookingInfo.objects.using(self._current_app_schema()).get(
        #         entity_id=self._entity_id(), id=id)
        # booking_data=0
        resp_list = NWisefinList()
        if int(booking_type) == Travel_requirements.cab:
            condition=Q(entity_id=self._entity_id())
            condition&=Q(from_time=from_time)
            condition&=~Q(from_time=None)
            condition&=Q(from_place=from_place,to_place=to_place)
            condition&=~Q(from_place=None,to_place=None)
            booking_data = CabBookingInfo.objects.using(self._current_app_schema()).filter(condition)

        elif int(booking_type) == Travel_requirements.bus:
            booking_data = BusBookingInfo.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id(),from_time=from_time,from_place=from_place,to_place=to_place)

        elif int(booking_type) == Travel_requirements.train:
            booking_data = TrainBookingInfo.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id(),from_time=from_time,from_place=from_place,to_place=to_place)

        elif int(booking_type) == Travel_requirements.air:
            booking_data = AirBookingInfo.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id(),from_time=from_time,from_place=from_place,to_place=to_place)

        for data in booking_data:
            temp = Air_response()
            # if int(booking_type) == Travel_requirements.cab and data.booking_status!=0:
            #     cab_tab=CabMapping.objects.using(self._current_app_schema()).filter(requirement_id=data.id,entity_id=self._entity_id(),status=1).last()
            #     temp.set_booking_detailid(cab_tab.BookingDetailId)


            detail_id = data.travel_detail_id
            tour_id = data.travel_detail.tour.id
            emp_code=TourRequest.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=tour_id)
            api_service = ApiService(self._scope())
            emp_id = api_service.employee_details_get(emp_code.empgid, request)
            temp = Air_response()
            temp.set_id(data.id)
            temp.set_from_time(data.from_time)
            temp.set_to_time(data.to_time)
            temp.set_from_place(data.from_place)
            temp.set_to_place(data.to_place)
            temp.set_travel_detail(detail_id)
            temp.set_tour_id(tour_id)
            temp.set_employee_name(emp_id.full_name)
            temp.set_employee_code(emp_id.code)
            temp.set_booking_status(data.booking_status)
            resp_list.append(temp)
        return resp_list



    def air_details_get(self,detail_id,request):
        obje = AirBookingInfo.objects.using(self._current_app_schema()).filter(travel_detail_id=detail_id,entity_id=self._entity_id(),status=1).all()
        resp_list = NWisefinList()
        for eachdata in obje:
            temp = Air_response()
            temp.set_id(eachdata.id)
            temp.set_booking_needed(Travel_requirements.air)
            temp.set_from_time(eachdata.from_time)
            temp.set_to_time(eachdata.to_time)
            temp.set_from_place(eachdata.from_place)
            temp.set_to_place(eachdata.to_place)
            temp.set_comments(eachdata.comments)
            temp.set_boarding_no(eachdata.boarding_no)
            tour_maker = Booking_requirement(self._scope())
            doc_get = tour_maker.fetch_tadoc(request, None, None, Travel_requirements.air, eachdata.id, 1)
            data = json.loads(doc_get)
            details = []
            if "data" in data:
                details = data["data"]
            temp.set_file_detail(details)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_booking_status(eachdata.booking_status)
            temp.set_status(eachdata.status)
            temp.set_created_date_time(eachdata.created_date)
            api_service = ApiService(self._scope())
            booked_by = api_service.employee_details_get(eachdata.booked_by, request)
            temp.set_booked_by(booked_by)
            resp_list.append(temp)
        return resp_list


    def Air_delete(self, id):
        try:
            resp_obj = AirBookingInfo.objects.using(self._current_app_schema()).filter(id=id, entity_id=self._entity_id()).update(status=0)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj


    def Air_data_admin(self,request,data,employee_id):
        obj = Air_request(data)
        booking_service = Booking_requirement(self._scope())
        obj = booking_service.millisecond_conversion(obj)
        # booking_service = Booking_requirement(self._scope())
        # validations = booking_service.admin_booking_vali(data)
        # if validations == False:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.BOOKING)
        #     return error_obj
        try:
            air_data = AirBookingInfo.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=obj.get_requirement_id())
            detail_id=air_data.travel_detail_id
            tour_id = air_data.travel_detail.tour.id
            obj.official=air_data.travel_detail.official
            data['booking_needed'] = Travel_requirements.air

            # booking_service = Booking_requirement(self._scope())

            booking_val = booking_service.booking_validations(tour_id, employee_id, detail_id, obj)
            if isinstance(booking_val, NWisefinError):
                return booking_val
            if  air_data.booking_status == TourRequest_BookingStatus.Reserved:
                if air_data.booked_by!=employee_id:
                    error_obj=NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.THIS_BOOKING_IS_RESERVED)
                    return error_obj
            if  obj.get_from_place() == None:
                error_obj=NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_BOOKING_DATA)
                return error_obj
            if obj.get_ticket_amount() == None:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_BOOKING_DATA)
                return error_obj

            booking_service.insert_booking_data(data, detail_id, employee_id)
            tour_dtl_arr = []
            dtl_data = TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                   tour_id=tour_id)
            for each_data in dtl_data:
                tour_dtl_arr.append(each_data.id)
            booking_service.book_air(obj, tour_dtl_arr, tour_id)
            bookinghistory_id = None

            bookinghistory_get = AirBookingDetails.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id(),
                requirement_id=obj.requirement_id)
            if len(bookinghistory_get) != 0:
                bookinghistoryid = bookinghistory_get.last()
                bookinghistory_id = bookinghistoryid.id
            Tour_service = Booking_requirement(self._scope())
            if len(request.FILES) != 0:
                params = {}
                params['requirement_type'] = Travel_requirements.air
                params['requirement_id'] = obj.get_requirement_id()
                params['ref_type'] = TADocUtil.TOUR
                doc_serv = Tour_service.insert_tadoc(request, params)
                if isinstance(doc_serv, NWisefinError):
                    return doc_serv


            if not bookinghistory_id is None:
                allowance = AirBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=bookinghistory_id).update(
                    from_time=obj.get_from_time(),
                    to_time=obj.get_to_time(),
                    ref_no=obj.get_ref_no(),
                    ref_type=obj.get_ref_type(),
                    from_place=obj.get_from_place(),
                    to_place=obj.get_to_place(),
                    comments=obj.get_comments(),
                    requirement_id=obj.get_requirement_id(),
                    booking_status=obj.get_booking_status(),
                    travel_detail_id=detail_id,
                    boarding_no=obj.get_boarding_no(),
                    updated_by=employee_id,
                    updated_date=datetime.now(),
                    ticket_amount=obj.get_ticket_amount(),vendor_name=obj.get_vendor_name(),
                    ticket_amount_personal = obj.ticket_amount_personal,
                    official = obj.official,
                    ticket_no=obj.get_ticket_no(),
                    class_of_travel=obj.get_class_of_travel(),
                    admin_paid=obj.admin_paid,
                    flight_number=obj.get_flight_number(),
                    PNR=obj.PNR,
                    fare_quoted=obj.fare_quoted,
                    issuance_type=obj.issuance_type,
                    website=obj.website,
                    booking_date=datetime.now(),
                    seat_number=obj.get_seat_number())

                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                return success_obj



            else:
                allowance = AirBookingDetails.objects.using(self._current_app_schema()).create(
                    from_time=obj.get_from_time(),
                    to_time=obj.get_to_time(),
                    ref_no=obj.get_ref_no(),
                    ref_type=obj.get_ref_type(),
                    from_place=obj.get_from_place(),
                    to_place=obj.get_to_place(),
                    comments=obj.get_comments(),
                    requirement_id=obj.get_requirement_id(),
                    booking_status=obj.get_booking_status(),
                    boarding_no=obj.get_boarding_no(),
                    travel_detail_id=detail_id,
                    created_by=employee_id,
                    created_date=datetime.now(),entity_id=self._entity_id(),
                    ticket_amount=obj.get_ticket_amount(),vendor_name=obj.get_vendor_name(),
                    ticket_amount_personal = obj.ticket_amount_personal,
                    official = obj.official,
                    ticket_no=obj.get_ticket_no(),
                    class_of_travel=obj.get_class_of_travel(),
                    flight_number=obj.get_flight_number(),
                    admin_paid=obj.admin_paid,
                    PNR=obj.PNR,
                    fare_quoted=obj.fare_quoted,
                    issuance_type=obj.issuance_type,
                    website=obj.website,
                    booking_date=datetime.now(),
                    seat_number=obj.get_seat_number())

                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                return success_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            exc=traceback.format_exc()
            logger.info('ta_ Air_data_admin- ' + str(e)+str(exc))
            return error_obj


    def get_Air_admin(self,id):

        condition = Q(status=Filterstatus.one, id=id, entity_id=self._entity_id())
        obje = AirBookingDetails.objects.using(self._current_app_schema()).get(condition)
        resp_list = NWisefinList()
        temp = Air_response()
        temp.set_id(obje.id)
        temp.set_from_time(obje.from_time)
        temp.set_to_time(obje.to_time)
        temp.set_from_place(obje.from_place)
        temp.set_to_place(obje.to_place)
        temp.set_ref_no(obje.ref_no)
        temp.set_boarding_no(obje.boarding_no)
        temp.set_ref_type(obje.ref_type)
        temp.set_travel_detail(obje.travel_detail_id)
        temp.set_booking_status(obje.booking_status)
        temp.set_comments(obje.comments)
        temp.set_created_by(obje.created_by)
        temp.set_created_date(obje.created_date)
        temp.set_updated_by(obje.updated_by)
        temp.set_updated_date(obje.updated_date)
        temp.set_status(obje.status)
        temp.set_ticket_amount(obje.ticket_amount)
        temp.set_vendor_name(obje.vendor_name)
        temp.set_ticket_no(obje.ticket_no)
        temp.set_class_of_travel(obje.class_of_travel)
        temp.set_flight_number(obje.flight_number)
        temp.set_seat_number(obje.seat_number)

        resp_list.append(temp)
        return resp_list

    def fetch_Air_admin(self,detail_array,request,all_report,vys_page,from_date1,to_date1,tour_id):
        condition = Q(entity_id=self._entity_id(), status=1)
        # condition &=~Q(travel_detail_id=None)
        # condition &=~Q(requirement_id=None)
        # if tour_id != None:
        #     condition&=Q(travel_detail_id__tour__id=tour_id)
        if from_date1 != None and to_date1 != None:
            from_date1 = datetime.strptime(from_date1[:11], "%d-%b-%Y")
            to_date1 = datetime.strptime(to_date1[:11], "%d-%b-%Y")
            to_date1 = to_date1 + timedelta(days=1)
            condition &= Q(booking_date__range=[from_date1, to_date1])
            # condition &= Q(booking_date__gte=from_date1)&Q(booking_date__lte=to_date1)

        elif from_date1 == None and to_date1 != None:
            to_date1 = datetime.strptime(to_date1[:11], "%d-%b-%Y")
            condition &= Q(booking_date__lte=to_date1)

        elif from_date1 != None and to_date1 == None:
            from_date1 = datetime.strptime(from_date1[:11], "%d-%b-%Y")
            condition &= Q(booking_date__gte=from_date1)
        if all_report == None:
            if detail_array is None:
                obje = AirBookingDetails.objects.using(self._current_app_schema()).filter(condition).all().order_by("-booking_date")[
                       vys_page.get_offset():vys_page.get_query_limit()]
            else:
                condition &=Q(travel_detail_id__in=detail_array)

                obje = AirBookingDetails.objects.using(self._current_app_schema()).filter(condition).all().order_by("-booking_date")[
                       vys_page.get_offset():vys_page.get_query_limit()]
        else:
            if detail_array is None:
                obje = AirBookingDetails.objects.using(self._current_app_schema()).filter(condition).all().order_by("booking_date").values("travel_detail__tour_id","booking_date","travel_detail__tour__empgid","travel_detail__purposeofvisit","travel_detail__client","travel_detail__tour__tour_status","travel_detail__tour__international_travel","from_place","to_place","from_time","to_time","vendor_name","PNR","ticket_amount","ticket_amount_personal","travel_detail__tour__week_end_travel","website","issuance_type","ticket_no","booking_status","travel_detail__official","comments","ref_no","requirement_id","id")
            else:
                condition &=Q(travel_detail_id__in=detail_array)

                obje = AirBookingDetails.objects.using(self._current_app_schema()).filter(condition).all().order_by("booking_date").values("travel_detail__tour_id","booking_date","travel_detail__tour__empgid","travel_detail__purposeofvisit","travel_detail__client","travel_detail__tour__tour_status","travel_detail__tour__international_travel","from_place","to_place","from_time","to_time","vendor_name","PNR","ticket_amount","ticket_amount_personal","travel_detail__tour__week_end_travel","website","issuance_type","ticket_no","booking_status","travel_detail__official","comments","ref_no","requirement_id","id")

            details_frame=pd.DataFrame(obje)
            # details_frame=details_frame.replace(to_replace=[None], value=pd.NaT)
            tour_arr=details_frame["travel_detail__tour_id"].tolist()
            requirement_arr=details_frame["requirement_id"].tolist()
            booking_tab_fil = BookingHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                            reference_id__in=requirement_arr,
                                                                                            booking_needed=Travel_requirements.air).values("refund_date","refund_amount","cancel_reason","loss_of_cancelation","cancelled_date","id","reference_id")
            booking_table_frame=pd.DataFrame(booking_tab_fil)
            trav = TravelHistory.objects.using(self._current_app_schema()).filter(
                tour_id__in=tour_arr, applevel=App_level.FIRST_LEVEL, status=Status.APPROVED,
                request_type=App_type.TOUR).values("onbehalfof_approval","approvedby","id","tour_id")

            travel_history_frame1=pd.DataFrame(trav)
            travel_history_frame = travel_history_frame1.drop_duplicates(keep='last', subset=['tour_id'])
            new_travel_history_frame=travel_history_frame.fillna(0).replace([0], [travel_history_frame["approvedby"]])
            emp_arr=details_frame["travel_detail__tour__empgid"].tolist()
            appr_arr=new_travel_history_frame["onbehalfof_approval"].tolist()
            whole_emp_arr=emp_arr+appr_arr
            api_ser=ApiService(self._scope())
            emp_det=api_ser.employee_details_arr(whole_emp_arr,request)
            emp_frame=pd.DataFrame(emp_det)
            emp_frame.rename(columns={'id': 'empgid'}, inplace=True)
            new_travel_history_frame.rename(columns={'onbehalfof_approval': 'empgid'}, inplace=True)
            details_frame.rename(columns={'travel_detail__tour__empgid': 'empgid'}, inplace=True)
            approver_name_frame=new_travel_history_frame.merge(emp_frame,on='empgid', how='left')
            approver_name_frame.rename(columns={'full_name': 'Approval Full name','code':'Approver code'}, inplace=True)
            approver_name_frame.drop("approvedby", axis=1, inplace=True)
            employee_name_frame = details_frame.merge(emp_frame, on='empgid', how='left')
            employee_name_frame.rename(columns={'full_name': 'Maker Full name', 'code': 'Maker code','travel_detail__tour_id':'tour_id'},
                                       inplace=True)
            final_out = employee_name_frame.merge(approver_name_frame, on='tour_id', how='left')
            final_out.rename(
                columns={'requirement_id':'reference_id'},
                inplace=True)
            final_out1=final_out.merge(booking_table_frame,on='reference_id', how='left')
            client_arr = final_out1["travel_detail__client"].tolist()
            api_service = ApiService(self._scope())
            client_data = api_service.get_client_arr(request,client_arr)
            client_data_frame=pd.DataFrame(client_data)
            client_data_frame.rename(
                columns={'id': 'travel_detail__client'},
                inplace=True)
            final_out2=final_out1.merge(client_data_frame,on='travel_detail__client',how='left')
            emp_team_=api_service.emp_team_arr(emp_arr,request)
            team_frame=pd.DataFrame(emp_team_)
            team_frame1=team_frame.drop_duplicates(keep='first',subset=['employee_id'])
            team_frame1.rename(
                columns={'employee_id': 'empgid'},
                inplace=True)
            final_out2.rename(
                columns={'empgid_x': 'empgid','empgid_y': 'Approver id'},
                inplace=True)
            final_out3=final_out2.merge(team_frame1,on='empgid',how='left')
            status={ -1:"Travel DEFAULT",
             0:"TRAVEL DELETED",
             1:"TRAVEL REQUESTED",
             2:"TRAVEL PENDING",
             3:"TRAVEL APPROVED",
             4:"TRAVEL REJECTED" ,
             5:"TRAVEL RETURNED",
             6:"TRAVEL FORWARDED"}
            booking_status={3:"BOOKED",2:"BOOKING CANCEL REQUESTED",4:"BOOKING CANCELLED",7:"BOOKING REJECTED"}
            inter_domes={0:"Domestic",1:"International"}
            personal_official={0:"Personal",1:"Official"}
            final_out5=final_out3.replace({'travel_detail__tour__tour_status':status,'booking_status':booking_status,"travel_detail__tour__international_travel":inter_domes,"travel_detail__official":personal_official})
            # final_out5['booking_date'].replace([None], np.nan, inplace=True)
            # final_out5['from_time'].replace([None], np.nan, inplace=True)
            # final_out5['to_time'].replace([None], np.nan, inplace=True)
            # final_out5['refund_date'].replace([None], np.nan, inplace=True)
            # final_out5['cancelled_date'].replace([None], np.NAN, inplace=True)

            final_out5["difference_in_days"]=final_out5["booking_date"]-final_out5["from_time"]
            final_out5['booking date'] = final_out5['booking_date'].apply(lambda a: pd.to_datetime(a,errors='coerce').strftime('%d-%b-%Y'))
            final_out5['booking time'] = final_out5['booking_date'].apply(lambda a: pd.to_datetime(a,errors='coerce').strftime('%H:%M:%S'))
            final_out5['from time'] = final_out5['from_time'].apply(lambda a: pd.to_datetime(a,errors='coerce').strftime('%H:%M:%S') if a is not None else None)
            final_out5['from_time'] = final_out5['from_time'].apply(lambda a: pd.to_datetime(a,errors='coerce').strftime('%d-%b-%Y') if a is not None else None)
            final_out5['to time'] = final_out5['to_time'].apply(lambda a:  pd.to_datetime(a,errors='coerce').strftime('%H:%M:%S') if a is not None else None)
            final_out5['to_time'] = final_out5['to_time'].apply(lambda a:  pd.to_datetime(a,errors='coerce').strftime('%d-%b-%Y') if a is not None else None)
            final_out5['refund_date'] = final_out5['refund_date'].apply(lambda a: pd.to_datetime(a,errors='coerce').strftime('%d-%b-%Y') if a is not None else None)
            final_out5['cancelled_date'] = final_out5['cancelled_date'].apply(lambda a: pd.to_datetime(a,errors='coerce').strftime('%d-%b-%Y') if a is not None else None)
            return final_out5

        resp_list = NWisefinList()
        for eachdata in obje:
            booking_table = BookingHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                reference_id=eachdata.requirement_id, booking_needed=Travel_requirements.air).last()
            temp = Air_response()
            temp.set_id(eachdata.id)
            temp.set_refund_date(booking_table.refund_date)
            temp.set_refund_date_xl(booking_table.refund_date)
            temp.set_refund_amount(booking_table.refund_amount)
            temp.set_from_time(eachdata.from_time)
            temp.set_from_time_xl(eachdata.from_time)
            temp.set_to_time(eachdata.to_time)
            temp.set_fromtime(eachdata.from_time)
            temp.set_totime(eachdata.to_time)
            temp.set_from_place(eachdata.from_place)
            temp.set_to_place(eachdata.to_place)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_travel_detail(eachdata.travel_detail_id)
            if int(eachdata.booking_status) == 3:
                temp.set_booking_status("BOOKED")
            elif int(eachdata.booking_status) == 2:
                temp.set_booking_status("BOOKING CANCEL REQUESTED")
            elif int(eachdata.booking_status) == 4:
                temp.set_booking_status("BOOKING CANCELLED")
            elif int(eachdata.booking_status)==7:
                temp.set_booking_status("BOOKING REJECTED")
            else:
                temp.set_booking_status(None)
            temp.set_comments(eachdata.comments)
            temp.set_boarding_no(eachdata.boarding_no)
            domestic = eachdata.travel_detail.tour.international_travel
            if domestic == 0:
                domestic_trave = "Domestic"
            elif domestic == 1:
                domestic_trave = "International"
            temp.set_domestic(domestic_trave)
            temp.set_created_by(eachdata.created_by)
            temp.set_created_date(eachdata.booking_date)
            temp.set_created_date_xl(eachdata.booking_date)
            temp.set_created_time_xl(eachdata.booking_date)
            temp.set_updated_by(eachdata.updated_by)
            temp.set_updated_date(eachdata.updated_date)
            temp.set_costper_head(eachdata.ticket_amount)
            temp.set_status(eachdata.status)
            # client_name = Client.objects.using(self._current_app_schema()).get(id=eachdata.travel_detail.client)
            # temp.set_client(client_name.name)
            api_service = ApiService(self._scope())
            client_data=api_service.get_client(request, eachdata.travel_detail.client)
            temp.set_client(client_data.client_name)
            emp_get = api_service.employee_details_get(eachdata.travel_detail.tour.empgid,request)
            trav = TravelHistory.objects.using(self._current_app_schema()).filter(
                tour_id=eachdata.travel_detail.tour.id, applevel=App_level.FIRST_LEVEL, status=Status.APPROVED,
                request_type=App_type.TOUR).last()
            appr = 0
            if trav.onbehalfof_approval != 0:
                appr = trav.onbehalfof_approval
            else:
                appr = trav.approvedby
            if appr != 0:
                approver_get = api_service.employee_details_get(appr, request)
                temp.set_approvedby(approver_get.full_name)
                temp.set_empcode(emp_get.code)
                temp.set_empname(emp_get.full_name)
            else:
                # approver_get = api_service.employee_details_get(appr, request)
                temp.set_approvedby(None)
                temp.set_empcode(None)
                temp.set_empname(None)
            temp.set_ticket_amount(eachdata.ticket_amount)
            temp.set_ticket_amount_personal(eachdata.ticket_amount_personal)
            temp.set_vendor_name(eachdata.vendor_name)
            temp.set_purpose_ofvisit(eachdata.travel_detail.purposeofvisit)
            temp.set_ticket_no(eachdata.ticket_no)
            temp.set_class_of_travel(eachdata.class_of_travel)
            temp.set_flight_number(eachdata.flight_number)
            temp.set_cancel_reason(booking_table.cancel_reason)
            emp = eachdata.travel_detail.tour.empgid
            api_service = ApiService(self._scope())
            get_team = api_service.emp_team_get(emp, request)
            temp.set_team_name(get_team["team"])
            temp.set_weekend_travel(eachdata.travel_detail.tour.week_end_travel)
            temp.set_seat_number(eachdata.seat_number)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_tour_id(eachdata.travel_detail.tour.id)
            personal = eachdata.travel_detail.official
            if int(personal) == 1:
                temp.set_personal_official("Official")
            elif int(personal) == 0:
                temp.set_personal_official("Personal")
            elif int(personal)==2:
                temp.set_personal_official("Official/Personal")
            else:
                temp.set_personal_official(None)
            status = eachdata.travel_detail.tour.tour_status
            if status == 3:
                temp.set_tour_status("TRAVEL APPROVED")
            from_time = eachdata.from_time
            created_date = eachdata.created_date
            temp.set_request_date(eachdata.travel_detail.tour.request_date)
            temp.set_request_date_xl(eachdata.travel_detail.tour.request_date)
            # startdate = datetime.strptime((from_time[:10]), '%Y-%b-%d').date()
            # enddate = datetime.strptime((created_date[:10]), '%Y-%b-%d').date()
            duration_days = ((created_date - from_time).days)
            temp.set_difference_indays(duration_days)
            temp.set_booking_needed("AIR BOOKING")
            temp.set_pnr_no(eachdata.PNR)
            temp.set_costper_head(eachdata.cost_per_head)
            temp.set_fare_quoted(eachdata.fare_quoted)
            temp.set_difference_in_amount(eachdata.difference_in_amount)
            temp.set_issuance_type(eachdata.issuance_type)
            temp.set_loss_of_cancelation(booking_table.loss_of_cancelation)
            temp.set_cancelled_date(booking_table.cancelled_date)
            temp.set_cancelled_date_xl(booking_table.cancelled_date)
            temp.set_website(eachdata.website)
            if all_report == None:
                resp_list.append(temp)
                vpage = NWisefinPaginator(obje, vys_page.get_index(), 10)
                resp_list.set_pagination(vpage)
            else:
                resp_list.append(temp)
        return resp_list

    def fetch_Air_admin_req(self,requirement_id):
        obje = AirBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),requirement_id=requirement_id,status=1).all()
        resp_list = NWisefinList()
        booking_his = BookingHistory.objects.using(self._current_app_schema()).filter(reference_id=requirement_id,entity_id=self._entity_id(),
                                                                                      booking_needed=Travel_requirements.air).last()
        resp_list = NWisefinList()
        temp1 = All_requirement()
        cancel_detail = []
        if booking_his.booking_status == 4:
            temp1.set_cancelled_date(booking_his.cancelled_date)
            temp1.set_refund_date(booking_his.refund_date)
            temp1.set_cancel_reschedule(booking_his.cancel_reschedule)
            temp1.set_cancel_reason(booking_his.cancel_reason)
            temp1.set_refund_amount(booking_his.refund_amount)
            temp1.set_fare_difference(booking_his.fare_difference)
            temp1.set_loss_of_cancelation(booking_his.loss_of_cancelation)
            cancel_detail.append(temp1)
        for eachdata in obje:
            temp = Air_response()
            temp.set_id(eachdata.id)
            temp.set_from_time(eachdata.from_time)
            temp.set_to_time(eachdata.to_time)
            temp.set_from_place(eachdata.from_place)
            temp.set_to_place(eachdata.to_place)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_booking_status(eachdata.booking_status)
            temp.set_comments(eachdata.comments)
            temp.set_boarding_no(eachdata.boarding_no)
            temp.set_created_by(eachdata.created_by)
            temp.set_created_date(eachdata.created_date)
            temp.set_updated_by(eachdata.updated_by)
            temp.set_updated_date(eachdata.updated_date)
            temp.set_status(eachdata.status)
            temp.set_ticket_amount(eachdata.ticket_amount)
            temp.set_ticket_amount_personal(eachdata.ticket_amount_personal)
            temp.set_cancel_data(cancel_detail)
            temp.set_utilised_status(eachdata.utilised_status)
            temp.set_noshow_reason(eachdata.noshow_reason)
            temp.set_admin_paid(eachdata.admin_paid)

            temp.set_vendor_name(eachdata.vendor_name)
            temp.set_invoice_amount(eachdata.invoice_amount)
            temp.set_ticket_no(eachdata.ticket_no)
            temp.set_class_of_travel(eachdata.class_of_travel)
            temp.set_flight_number(eachdata.flight_number)
            temp.set_PNR(eachdata.PNR)
            temp.set_cost_per_head(eachdata.cost_per_head)
            temp.set_fare_quoted(eachdata.fare_quoted)
            temp.set_difference_in_amount(eachdata.difference_in_amount)
            temp.set_issuance_type(eachdata.issuance_type)
            temp.set_website(eachdata.website)
            temp.set_booking_date(eachdata.booking_date)
            temp.set_seat_number(eachdata.seat_number)
            resp_list.append(temp)
        return resp_list

    def air_details_get_admin(self,detail_id):
        obje = AirBookingDetails.objects.using(self._current_app_schema()).filter(travel_detail_id__in=detail_id,entity_id=self._entity_id(),status=1).all()
        resp_list = NWisefinList()
        for eachdata in obje:
            temp = Air_response()
            temp.set_id(eachdata.id)
            temp.set_booking_needed(Travel_requirements.air)
            temp.set_from_time(eachdata.from_time)
            temp.set_to_time(eachdata.to_time)
            temp.set_from_place(eachdata.from_place)
            temp.set_to_place(eachdata.to_place)
            temp.set_comments(eachdata.comments)
            temp.set_boarding_no(eachdata.boarding_no)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_booking_status(eachdata.booking_status)
            temp.set_status(eachdata.status)
            temp.set_created_date_time(eachdata.created_date)
            temp.set_ticket_amount(eachdata.ticket_amount)
            temp.set_ticket_amount_personal(eachdata.ticket_amount_personal)
            temp.set_vendor_name(eachdata.vendor_name)
            temp.set_ticket_no(eachdata.ticket_no)
            temp.set_class_of_travel(eachdata.class_of_travel)
            temp.set_flight_number(eachdata.flight_number)
            temp.set_seat_number(eachdata.seat_number)
            temp.set_utilised_status(eachdata.utilised_status)
            temp.set_noshow_reason(eachdata.noshow_reason)
            temp.set_admin_paid(eachdata.admin_paid)

            temp.set_vendor_name(eachdata.vendor_name)
            temp.set_invoice_amount(eachdata.invoice_amount)
            temp.set_ticket_no(eachdata.ticket_no)
            temp.set_class_of_travel(eachdata.class_of_travel)
            temp.set_flight_number(eachdata.flight_number)
            temp.set_PNR(eachdata.PNR)
            temp.set_cost_per_head(eachdata.cost_per_head)
            temp.set_fare_quoted(eachdata.fare_quoted)
            temp.set_difference_in_amount(eachdata.difference_in_amount)
            temp.set_issuance_type(eachdata.issuance_type)
            temp.set_website(eachdata.website)
            temp.set_booking_date(eachdata.booking_date)
            temp.set_seat_number(eachdata.seat_number)
            resp_list.append(temp)
        return resp_list


    def air_details_get_admin_ecf(self,detail_id,admin_paid):
        obje = AirBookingDetails.objects.using(self._current_app_schema()).filter(travel_detail_id__in=detail_id,entity_id=self._entity_id()
                                                                                  ,status=1,admin_paid=admin_paid).all()
        resp_list = NWisefinList()
        for eachdata in obje:
            temp = Air_response()
            temp.set_id(eachdata.id)
            temp.set_booking_needed(Travel_requirements.air)
            temp.set_from_time(eachdata.from_time)
            temp.set_to_time(eachdata.to_time)
            temp.set_from_place(eachdata.from_place)
            temp.set_to_place(eachdata.to_place)
            temp.set_comments(eachdata.comments)
            temp.set_boarding_no(eachdata.boarding_no)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_booking_status(eachdata.booking_status)
            temp.set_status(eachdata.status)
            temp.set_created_date_time(eachdata.created_date)
            temp.set_ticket_amount(eachdata.ticket_amount)
            temp.set_vendor_name(eachdata.vendor_name)
            temp.set_ticket_no(eachdata.ticket_no)
            temp.set_class_of_travel(eachdata.class_of_travel)
            temp.set_flight_number(eachdata.flight_number)
            temp.set_seat_number(eachdata.seat_number)
            resp_list.append(temp)
        return resp_list

    def Air_delete_admin(self, id):
        try:
            resp_obj = AirBookingDetails.objects.using(self._current_app_schema()).filter(id=id, entity_id=self._entity_id()).update(status=0)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj

class Train_requirement(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)



    def Train_data(self,data,employee_id,detail_id):
        obj = Train_request(data)

        if not obj.get_id() is None:
            # try:
            train_data=TrainBookingInfo.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=obj.get_id())
            if train_data.booking_status not in [Requirements_booking_status.booked,Requirements_booking_status.cancelled]:
                allowance = TrainBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=obj.get_id()).update(
                    from_time=obj.get_from_time(),
                    to_time=obj.get_to_time(),
                    ref_no=obj.get_ref_no(),
                    ref_type=obj.get_ref_type(),
                    from_place=obj.get_from_place(),
                    to_place=obj.get_to_place(),
                    comments=obj.get_comments(),
                    pnr_no=obj.get_pnr_no(),
                    updated_by=employee_id,
                    updated_date=datetime.now())
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj



        else:
            # try:
            allowance = TrainBookingInfo.objects.using(self._current_app_schema()).create(
                from_time=obj.get_from_time(),
                to_time=obj.get_to_time(),
                from_place=obj.get_from_place(),
                to_place=obj.get_to_place(),
                ref_no=obj.get_ref_no(),
                ref_type=obj.get_ref_type(),
                comments=obj.get_comments(),
                pnr_no=obj.get_pnr_no(),
                travel_detail_id=detail_id,
                created_by=employee_id,
                created_date=datetime.now(),entity_id=self._entity_id())
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            return success_obj



    def get_Train(self,id):
        # try:
        condition = Q(status=Filterstatus.one, id=id, entity_id=self._entity_id())
        obje = TrainBookingInfo.objects.using(self._current_app_schema()).get(condition)
        resp_list = NWisefinList()
        temp = Train_response()
        temp.set_id(obje.id)
        temp.set_from_time(obje.from_time)
        temp.set_to_time(obje.to_time)
        temp.set_from_place(obje.from_place)
        temp.set_to_place(obje.to_place)
        temp.set_ref_no(obje.ref_no)
        temp.set_ref_type(obje.ref_type)
        temp.set_travel_detail(obje.travel_detail_id)
        temp.set_booking_status(obje.booking_status)
        temp.set_comments(obje.comments)
        temp.set_created_by(obje.created_by)
        temp.set_created_date(obje.created_date)
        temp.set_updated_by(obje.updated_by)
        temp.set_updated_date(obje.updated_date)
        temp.set_status(obje.status)
        resp_list.append(temp)
        return resp_list



    def fetch_Train(self):
        obje = TrainBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),status=1).all()
        resp_list = NWisefinList()
        for eachdata in obje:
            temp =Train_response()
            temp.set_id(eachdata.id)
            temp.set_from_time(eachdata.from_time)
            temp.set_to_time(eachdata.to_time)
            temp.set_from_place(eachdata.from_place)
            temp.set_to_place(eachdata.to_place)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_booking_status(eachdata.booking_status)
            temp.set_comments(eachdata.comments)
            temp.set_created_by(eachdata.created_by)
            temp.set_created_date(eachdata.created_date)
            temp.set_updated_by(eachdata.updated_by)
            temp.set_updated_date(eachdata.updated_date)
            temp.set_status(eachdata.status)
            resp_list.append(temp)
        return resp_list


    def train_details_get(self,detail_id,request):
        obje = TrainBookingInfo.objects.using(self._current_app_schema()).filter(travel_detail_id=detail_id,entity_id=self._entity_id(),status=1).all()
        resp_list = NWisefinList()
        for eachdata in obje:
            temp =Train_response()
            temp.set_id(eachdata.id)
            temp.set_booking_needed(Travel_requirements.train)
            temp.set_from_time(eachdata.from_time)
            temp.set_to_time(eachdata.to_time)
            temp.set_from_place(eachdata.from_place)
            temp.set_to_place(eachdata.to_place)
            temp.set_comments(eachdata.comments)
            tour_maker = Booking_requirement(self._scope())
            doc_get = tour_maker.fetch_tadoc(request, None, None, Travel_requirements.train, eachdata.id, 1)
            data = json.loads(doc_get)
            details = []
            if "data" in data:
                details = data["data"]
            temp.set_file_detail(details)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_booking_status(eachdata.booking_status)
            temp.set_status(eachdata.status)
            temp.set_created_date_time(eachdata.created_date)
            api_service = ApiService(self._scope())
            booked_by = api_service.employee_details_get(eachdata.booked_by, request)
            temp.set_booked_by(booked_by)
            resp_list.append(temp)
        return resp_list

    def train_delete(self, id):
        try:
            resp_obj = TrainBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=id).update(status=0)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj


    def Train_data_admin(self,request,data,employee_id):
        obj = Train_request(data)
        booking_service = Booking_requirement(self._scope())
        obj = booking_service.millisecond_conversion(obj)
        # validations = booking_service.admin_booking_vali(data)
        # if validations == False:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.BOOKING)
        #     return error_obj
        try:

            train_data = TrainBookingInfo.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=obj.get_requirement_id())
            detail_id=train_data.travel_detail_id
            obj.official = train_data.travel_detail.official

            tour_id = train_data.travel_detail.tour.id
            data['booking_needed'] = Travel_requirements.train

            # booking_service = Booking_requirement(self._scope())

            booking_val = booking_service.booking_validations(tour_id, employee_id, detail_id, obj)
            if isinstance(booking_val, NWisefinError):
                return booking_val
            if  train_data.booking_status == TourRequest_BookingStatus.Reserved:
                if train_data.booked_by!=employee_id:
                    error_obj=NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.THIS_BOOKING_IS_RESERVED)
                    return error_obj
            if obj.get_from_place() == None:
                error_obj=NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_BOOKING_DATA)
                return error_obj
            if obj.get_ticket_amount() == None:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_BOOKING_DATA)
                return error_obj

            booking_service.insert_booking_data(data, detail_id, employee_id)
            tour_dtl_arr = []
            dtl_data = TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                   tour_id=tour_id)
            for each_data in dtl_data:
                tour_dtl_arr.append(each_data.id)
            booking_service.book_train(obj, tour_dtl_arr, tour_id)
            bookinghistory_id = None

            bookinghistory_get = TrainBookingDetails.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id(),
                requirement_id=obj.requirement_id)
            if len(bookinghistory_get) != 0:
                bookinghistoryid = bookinghistory_get.last()
                bookinghistory_id = bookinghistoryid.id
            Tour_service = Booking_requirement(self._scope())
            if len(request.FILES) != 0:
                params = {}
                params['requirement_type'] = Travel_requirements.train
                params['requirement_id'] = obj.get_requirement_id()
                params['ref_type'] = TADocUtil.TOUR
                doc_serv = Tour_service.insert_tadoc(request, params)
                if isinstance(doc_serv, NWisefinError):
                    return doc_serv

            if not bookinghistory_id is None:
                allowance = TrainBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=bookinghistory_id).update(
                    from_time=obj.get_from_time(),
                    to_time=obj.get_to_time(),
                    ref_no=obj.get_ref_no(),
                    ref_type=obj.get_ref_type(),
                    booking_status=obj.get_booking_status(),
                    from_place=obj.get_from_place(),
                    to_place=obj.get_to_place(),
                    comments=obj.get_comments(),
                    pnr_no=obj.get_pnr_no(),
                    requirement_id=obj.get_requirement_id(),
                    travel_detail_id=detail_id,
                    updated_by=employee_id,
                    updated_date=datetime.now(),
                    ticket_amount=obj.get_ticket_amount(),
                    ticket_amount_personal = obj.ticket_amount_personal,
                    official = obj.official,
                    vendor_name=obj.get_vendor_name(),
                    ticket_no=obj.get_ticket_no(),
                    class_of_travel=obj.get_class_of_travel(),
                    train_number=obj.get_train_number(),
                    admin_paid=obj.admin_paid,
                    PNR=obj.PNR,
                    fare_quoted=obj.fare_quoted,
                    issuance_type=obj.issuance_type,
                    website=obj.website,
                    booking_date=datetime.now(),
                    seat_number=obj.get_seat_number())
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                return success_obj


            else:
                allowance = TrainBookingDetails.objects.using(self._current_app_schema()).create(
                    from_time=obj.get_from_time(),
                    to_time=obj.get_to_time(),
                    from_place=obj.get_from_place(),
                    to_place=obj.get_to_place(),
                    booking_status=obj.get_booking_status(),
                    ref_no=obj.get_ref_no(),
                    ref_type=obj.get_ref_type(),
                    comments=obj.get_comments(),
                    pnr_no=obj.get_pnr_no(),
                    requirement_id=obj.get_requirement_id(),
                    travel_detail_id=detail_id,
                    created_by=employee_id,
                    created_date=datetime.now(),entity_id=self._entity_id(),
                    ticket_amount=obj.get_ticket_amount(),vendor_name=obj.get_vendor_name(),
                    ticket_amount_personal = obj.ticket_amount_personal,
                    official = obj.official,
                    ticket_no=obj.get_ticket_no(),
                    class_of_travel=obj.get_class_of_travel(),
                    train_number=obj.get_train_number(),
                    admin_paid=obj.admin_paid,
                    PNR=obj.PNR,
                    fare_quoted=obj.fare_quoted,
                    issuance_type=obj.issuance_type,
                    website=obj.website,
                    booking_date=datetime.now(),
                    seat_number=obj.get_seat_number())
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                return success_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            exc=traceback.format_exc()
            logger.info('ta_ Train_data_admin- ' + str(e)+str(exc))
            return error_obj


    def get_Train_admin(self,id):
        condition = Q(status=Filterstatus.one, id=id, entity_id=self._entity_id())
        obje = TrainBookingDetails.objects.using(self._current_app_schema()).get(condition)
        resp_list = NWisefinList()
        temp = Train_response()
        temp.set_id(obje.id)
        temp.set_from_time(obje.from_time)
        temp.set_to_time(obje.to_time)
        temp.set_from_place(obje.from_place)
        temp.set_to_place(obje.to_place)
        temp.set_ref_no(obje.ref_no)
        temp.set_ref_type(obje.ref_type)
        temp.set_travel_detail(obje.travel_detail_id)
        temp.set_booking_status(obje.booking_status)
        temp.set_comments(obje.comments)
        temp.set_created_by(obje.created_by)
        temp.set_created_date(obje.created_date)
        temp.set_updated_by(obje.updated_by)
        temp.set_updated_date(obje.updated_date)
        temp.set_status(obje.status)
        temp.set_ticket_amount(obje.ticket_amount)
        temp.set_vendor_name(obje.vendor_name)
        temp.set_ticket_no(obje.ticket_no)
        temp.set_class_of_travel(obje.class_of_travel)
        temp.set_train_number(obje.train_number)
        temp.set_seat_number(obje.seat_number)
        resp_list.append(temp)
        return resp_list



    def fetch_Train_admin(self,detail_array,request,all_report,vys_page,from_date,to_date,tour_id):
        condition = Q(entity_id=self._entity_id(), status=1)
        condition &= ~Q(travel_detail_id=None, requirement_id=None)
        if tour_id != None:
            condition &= Q(travel_detail_id__tour__id=tour_id)
        if from_date != None and to_date != None:
            from_date = datetime.strptime(from_date[:11], "%d-%b-%Y")
            to_date = datetime.strptime(to_date[:11], "%d-%b-%Y")
            to_date = to_date + timedelta(days=1)
            condition &= Q(booking_date__range=[from_date, to_date])

        elif from_date == None and to_date != None:
            to_date = datetime.strptime(to_date[:11], "%d-%b-%Y")
            condition &= Q(booking_date__lte=to_date)

        elif from_date != None and to_date == None:
            from_date = datetime.strptime(from_date[:11], "%d-%b-%Y")
            condition &= Q(booking_date__gte=from_date)
        if all_report == None:
            if detail_array is None:
                obje = TrainBookingDetails.objects.using(self._current_app_schema()).filter(condition).all().order_by("-booking_date")
            else:
                condition &=Q(travel_detail_id__in=detail_array)
                obje = TrainBookingDetails.objects.using(self._current_app_schema()).filter(condition).all().order_by("-booking_date")[
                       vys_page.get_offset():vys_page.get_query_limit()]
        else:
            if detail_array is None:
                obje = TrainBookingDetails.objects.using(self._current_app_schema()).filter(condition).all().order_by("booking_date")
            else:
                condition &=Q(travel_detail_id__in=detail_array)
                obje = TrainBookingDetails.objects.using(self._current_app_schema()).filter(condition).all().order_by("booking_date")
        resp_list = NWisefinList()
        for eachdata in obje:
            booking_table = BookingHistory.objects.using(self._current_app_schema()).filter(
                reference_id=eachdata.requirement_id, booking_needed=Travel_requirements.train).last()
            temp =Train_response()
            temp.set_id(eachdata.id)
            temp.set_refund_date(booking_table.refund_date)
            temp.set_refund_amount(booking_table.refund_amount)
            temp.set_from_time(eachdata.from_time)
            temp.set_to_time(eachdata.to_time)
            temp.set_fromtime(eachdata.from_time)
            temp.set_totime(eachdata.to_time)
            temp.set_from_place(eachdata.from_place)
            temp.set_to_place(eachdata.to_place)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_travel_detail(eachdata.travel_detail_id)
            if int(eachdata.booking_status) == 3:
                temp.set_booking_status("BOOKED")
            elif int(eachdata.booking_status) == 2:
                temp.set_booking_status("BOOKING CANCEL REQUESTED")
            elif int(eachdata.booking_status) == 4:
                temp.set_booking_status("BOOKING CANCELLED")
            elif int(eachdata.booking_status)==7:
                temp.set_booking_status("BOOKING REJECTED")
            else:
                temp.set_booking_status(None)
            temp.set_cancel_reason(booking_table.cancel_reason)
            temp.set_weekend_travel(eachdata.travel_detail.tour.week_end_travel)
            temp.set_comments(eachdata.comments)
            temp.set_created_by(eachdata.created_by)
            temp.set_created_date(eachdata.booking_date)
            temp.set_created_date_xl(eachdata.booking_date)
            temp.set_created_time_xl(eachdata.booking_date)
            temp.set_costper_head(eachdata.ticket_amount)
            temp.set_updated_by(eachdata.updated_by)
            domestic = eachdata.travel_detail.tour.international_travel
            if domestic == 0:
                domestic_trave = "Domestic"
            elif domestic == 1:
                domestic_trave = "International"
            temp.set_domestic(domestic_trave)
            api_service = ApiService(self._scope())
            emp_get = api_service.employee_details_get(eachdata.travel_detail.tour.empgid,request)
            approver_get = api_service.employee_details_get(booking_table.created_by, request)
            temp.set_approvedby(approver_get.full_name)
            temp.set_empcode(emp_get.code)
            temp.set_empname(emp_get.full_name)
            temp.set_updated_date(eachdata.updated_date)
            temp.set_status(eachdata.status)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_tour_id(eachdata.travel_detail.tour.id)
            temp.set_ticket_amount(eachdata.ticket_amount)
            temp.set_ticket_amount_personal(eachdata.ticket_amount_personal)
            emp = eachdata.travel_detail.tour.empgid
            api_service = ApiService(self._scope())
            get_team = api_service.emp_team_get(emp, request)
            temp.set_team_name(get_team["team"])
            temp.set_vendor_name(eachdata.vendor_name)
            # client_name = Client.objects.using(self._current_app_schema()).get(id=eachdata.travel_detail.client)
            # temp.set_client(client_name.name)
            client_data=api_service.get_client( request, eachdata.travel_detail.client)
            temp.set_client(client_data.client_name)
            from_time = eachdata.from_time
            created_date = eachdata.created_date
            temp.set_request_date(eachdata.travel_detail.tour.request_date)
            temp.set_purpose_ofvisit(eachdata.travel_detail.purposeofvisit)
            # startdate = datetime.strptime((from_time[:10]), '%Y-%b-%d').date()
            # enddate = datetime.strptime((created_date[:10]), '%Y-%b-%d').date()
            duration_days = ((created_date-from_time).days)
            temp.set_difference_indays(duration_days)
            temp.set_ticket_no(eachdata.ticket_no)
            temp.set_class_of_travel(eachdata.class_of_travel)
            temp.set_train_number(eachdata.train_number)
            temp.set_seat_number(eachdata.seat_number)
            personal = eachdata.travel_detail.official
            if int(personal) == 1:
                temp.set_personal_official("Official")
            elif int(personal) == 0:
                temp.set_personal_official("Personal")
            elif int(personal)==2:
                temp.set_personal_official("Official/Personal")
            else:
                temp.set_personal_official(None)

            temp.set_booking_needed("TRAIN BOOKING")
            temp.set_pnr_no(eachdata.PNR)
            status = eachdata.travel_detail.tour.tour_status
            if status == 3:
                temp.set_tour_status("TRAVEL APPROVED")
            temp.set_costper_head(eachdata.cost_per_head)
            temp.set_fare_quoted(eachdata.fare_quoted)
            temp.set_difference_in_amount(eachdata.difference_in_amount)
            temp.set_issuance_type(eachdata.issuance_type)
            temp.set_website(eachdata.website)
            temp.set_cancelled_date(booking_table.cancelled_date)
            temp.set_loss_of_cancelation(booking_table.loss_of_cancelation)
            if all_report == None:
                resp_list.append(temp)
                vpage = NWisefinPaginator(obje, vys_page.get_index(), 10)
                resp_list.set_pagination(vpage)
            else:
                resp_list.append(temp)
        return resp_list


    def fetch_Train_admin_req(self,requirement_id):
        obje = TrainBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),requirement_id=requirement_id,status=1).all()
        resp_list = NWisefinList()
        booking_his = BookingHistory.objects.using(self._current_app_schema()).filter(reference_id=requirement_id,entity_id=self._entity_id(),
                                                                                      booking_needed=Travel_requirements.train).last()
        resp_list = NWisefinList()
        temp1 = All_requirement()
        cancel_detail = []
        if booking_his.booking_status == 4:
            temp1.set_cancelled_date(booking_his.cancelled_date)
            temp1.set_refund_date(booking_his.refund_date)
            temp1.set_cancel_reschedule(booking_his.cancel_reschedule)
            temp1.set_cancel_reason(booking_his.cancel_reason)
            temp1.set_refund_amount(booking_his.refund_amount)
            temp1.set_fare_difference(booking_his.fare_difference)
            temp1.set_loss_of_cancelation(booking_his.loss_of_cancelation)
            cancel_detail.append(temp1)
        for eachdata in obje:
            temp =Train_response()
            temp.set_id(eachdata.id)
            temp.set_from_time(eachdata.from_time)
            temp.set_to_time(eachdata.to_time)
            temp.set_from_place(eachdata.from_place)
            temp.set_to_place(eachdata.to_place)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_booking_status(eachdata.booking_status)
            temp.set_comments(eachdata.comments)
            temp.set_created_by(eachdata.created_by)
            temp.set_created_date(eachdata.created_date)
            temp.set_updated_by(eachdata.updated_by)
            temp.set_updated_date(eachdata.updated_date)
            temp.set_status(eachdata.status)
            temp.set_ticket_amount(eachdata.ticket_amount)
            temp.set_ticket_amount_personal(eachdata.ticket_amount_personal)
            temp.set_utilised_status(eachdata.utilised_status)
            temp.set_noshow_reason(eachdata.noshow_reason)
            temp.set_cancel_data(cancel_detail)
            temp.set_admin_paid(eachdata.admin_paid)
            temp.set_vendor_name(eachdata.vendor_name)
            temp.set_ticket_no(eachdata.ticket_no)
            temp.set_class_of_travel(eachdata.class_of_travel)
            temp.set_PNR(eachdata.PNR)
            temp.set_train_number(eachdata.train_number)
            temp.set_seat_number(eachdata.seat_number)
            temp.set_cost_per_head(eachdata.cost_per_head)
            temp.set_fare_quoted(eachdata.fare_quoted)
            temp.set_difference_in_amount(eachdata.difference_in_amount)
            temp.set_issuance_type(eachdata.issuance_type)
            temp.set_website(eachdata.website)
            temp.set_booking_date(eachdata.booking_date)
            resp_list.append(temp)
        return resp_list


    def train_details_get_admin(self,detail_id):
        obje = TrainBookingDetails.objects.using(self._current_app_schema()).filter(travel_detail_id__in=detail_id,entity_id=self._entity_id(),status=1).all()
        resp_list = NWisefinList()
        for eachdata in obje:
            temp =Train_response()
            temp.set_id(eachdata.id)
            temp.set_booking_needed(Travel_requirements.train)
            temp.set_from_time(eachdata.from_time)
            temp.set_to_time(eachdata.to_time)
            temp.set_from_place(eachdata.from_place)
            temp.set_to_place(eachdata.to_place)
            temp.set_comments(eachdata.comments)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_booking_status(eachdata.booking_status)
            temp.set_status(eachdata.status)
            temp.set_created_date_time(eachdata.created_date)
            temp.set_ticket_amount(eachdata.ticket_amount)
            temp.set_ticket_amount_personal(eachdata.ticket_amount_personal)
            temp.set_vendor_name(eachdata.vendor_name)
            temp.set_ticket_no(eachdata.ticket_no)
            temp.set_class_of_travel(eachdata.class_of_travel)
            temp.set_train_number(eachdata.train_number)
            temp.set_seat_number(eachdata.seat_number)
            temp.set_utilised_status(eachdata.utilised_status)
            temp.set_noshow_reason(eachdata.noshow_reason)
            temp.set_admin_paid(eachdata.admin_paid)
            temp.set_vendor_name(eachdata.vendor_name)
            temp.set_ticket_no(eachdata.ticket_no)
            temp.set_class_of_travel(eachdata.class_of_travel)
            temp.set_PNR(eachdata.PNR)
            temp.set_train_number(eachdata.train_number)
            temp.set_seat_number(eachdata.seat_number)
            temp.set_cost_per_head(eachdata.cost_per_head)
            temp.set_fare_quoted(eachdata.fare_quoted)
            temp.set_difference_in_amount(eachdata.difference_in_amount)
            temp.set_issuance_type(eachdata.issuance_type)
            temp.set_website(eachdata.website)
            temp.set_booking_date(eachdata.booking_date)
            resp_list.append(temp)
        return resp_list


    def train_details_get_admin_ecf(self,detail_id,admin_paid):
        obje = TrainBookingDetails.objects.using(self._current_app_schema()).filter(travel_detail_id__in=detail_id,entity_id=self._entity_id()
                                                                                    ,status=1,admin_paid=admin_paid).all()
        resp_list = NWisefinList()
        for eachdata in obje:
            temp =Train_response()
            temp.set_id(eachdata.id)
            temp.set_booking_needed(Travel_requirements.train)
            temp.set_from_time(eachdata.from_time)
            temp.set_to_time(eachdata.to_time)
            temp.set_from_place(eachdata.from_place)
            temp.set_to_place(eachdata.to_place)
            temp.set_comments(eachdata.comments)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_booking_status(eachdata.booking_status)
            temp.set_status(eachdata.status)
            temp.set_created_date_time(eachdata.created_date)
            temp.set_ticket_amount(eachdata.ticket_amount)
            temp.set_vendor_name(eachdata.vendor_name)
            temp.set_ticket_no(eachdata.ticket_no)
            temp.set_class_of_travel(eachdata.class_of_travel)
            temp.set_train_number(eachdata.train_number)
            temp.set_seat_number(eachdata.seat_number)
            resp_list.append(temp)
        return resp_list

    def train_delete_admin(self, id):
        try:
            resp_obj = TrainBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=id).update(status=0)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj

class AccomodationBooking_requirement(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)


    def accomadation_data(self,data,employee_id,detail_id):

        obj = AccomodationBooking_Request(data)
        if not obj.get_id() is None:
            acc_data=AccomodationBookingInfo.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=obj.get_id())
            if acc_data.booking_status not in [Requirements_booking_status.booked,Requirements_booking_status.cancelled]:
                allowance = AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=obj.get_id()).update(
                checkin_time=obj.get_checkin_time(),
                checkout_time=obj.get_checkout_time(),
                place_of_stay=obj.get_place_of_stay(),
                ref_no=obj.get_ref_no(),
                ref_type=obj.get_ref_type(),
                comments=obj.get_comments(),
                updated_by=employee_id,
                updated_date=datetime.now())

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj



        else:
            allowance = AccomodationBookingInfo.objects.using(self._current_app_schema()).create(
                checkin_time=obj.get_checkin_time(),
                checkout_time=obj.get_checkout_time(),
                place_of_stay=obj.get_place_of_stay(),
                ref_no=obj.get_ref_no(),
                ref_type=obj.get_ref_type(),
                comments=obj.get_comments(),
                travel_detail_id=detail_id,
                created_by=employee_id,
                created_date=datetime.now(),entity_id=self._entity_id())
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            return success_obj



    def get_accomadation(self,id):
        condition = Q(status=Filterstatus.one, id=id, entity_id=self._entity_id())
        obje = AccomodationBookingInfo.objects.using(self._current_app_schema()).get(condition)
        resp_list = NWisefinList()
        temp = AccomodationBooking_Response()
        temp.set_id(obje.id)
        temp.set_checkin_time(obje.checkin_time)
        temp.set_checkout_time(obje.checkout_time)
        temp.set_place_of_stay(obje.place_of_stay)
        temp.set_ref_no(obje.ref_no)
        temp.set_ref_type(obje.ref_type)
        temp.set_comments(obje.comments)
        temp.set_travel_detail(obje.travel_detail_id)
        temp.set_booking_status(obje.booking_status)
        temp.set_created_by(obje.created_by)
        temp.set_created_date(obje.created_date)
        temp.set_updated_by(obje.updated_by)
        temp.set_updated_date(obje.updated_date)
        temp.set_status(obje.status)
        resp_list.append(temp)
        return resp_list



    def fetch_accomadation(self):
        obje = AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),status=1).all()
        resp_list = NWisefinList()
        for eachdata in obje:
            temp =AccomodationBooking_Response()
            temp.set_id(eachdata.id)
            temp.set_checkin_time(eachdata.checkin_time)
            temp.set_checkout_time(eachdata.checkout_time)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_comments(eachdata.comments)
            temp.set_place_of_stay(eachdata.place_of_stay)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_booking_status(eachdata.booking_status)
            temp.set_created_by(eachdata.created_by)
            temp.set_created_date(eachdata.created_date)
            temp.set_updated_by(eachdata.updated_by)
            temp.set_updated_date(eachdata.updated_date)
            temp.set_status(eachdata.status)
            resp_list.append(temp)
        return resp_list

    def accomadation_details_get(self,detail_id,request):
        obje = AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(travel_detail_id=detail_id,entity_id=self._entity_id(),status=1).all()
        resp_list = NWisefinList()
        for eachdata in obje:
            temp =AccomodationBooking_Response()
            temp.set_id(eachdata.id)
            temp.set_booking_needed(Travel_requirements.accomodation)
            temp.set_checkin_time(eachdata.checkin_time)
            temp.set_checkout_time(eachdata.checkout_time)
            temp.set_place_of_stay(eachdata.place_of_stay)
            temp.set_comments(eachdata.comments)
            temp.set_ref_no(eachdata.ref_no)
            tour_maker = Booking_requirement(self._scope())
            doc_get = tour_maker.fetch_tadoc(request, None, None, Travel_requirements.accomodation, eachdata.id, 1)
            data = json.loads(doc_get)
            details = []
            if "data" in data:
                details = data["data"]
            temp.set_file_detail(details)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_booking_status(eachdata.booking_status)
            temp.set_status(eachdata.status)
            temp.set_created_date_time(eachdata.created_date)
            api_service = ApiService(self._scope())
            booked_by = api_service.employee_details_get(eachdata.booked_by, request)
            temp.set_booked_by(booked_by)
            resp_list.append(temp)
        return resp_list

    def accomadation_delete(self, id):
        try:
            resp_obj = AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=id).update(status=0)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj



    def accomadation_data_admin(self,request,data,employee_id):
        booking_service = Booking_requirement(self._scope())
        obj = AccomodationBooking_Request(data)
        obj = booking_service.millisecond_conversion(obj)
        # booking_service = Booking_requirement(self._scope())
        # validations = booking_service.admin_booking_vali(data)
        # if validations == False:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.INVALID_PLACE_OF_STAY)
        #     return error_obj
        if obj.get_place_of_stay() == None:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.BOOKING)
            return error_obj
        try:
            acc_data = AccomodationBookingInfo.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=obj.get_requirement_id())
            detail_id=acc_data.travel_detail_id
            data['booking_needed'] = Travel_requirements.accomodation
            tour_id = acc_data.travel_detail.tour.id
            obj.official = acc_data.travel_detail.official



            booking_val = booking_service.booking_validations(tour_id, employee_id, detail_id, obj)
            if isinstance(booking_val, NWisefinError):
                return booking_val
            if  acc_data.booking_status == TourRequest_BookingStatus.Reserved:
                if acc_data.booked_by!=employee_id:
                    error_obj=NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.THIS_BOOKING_IS_RESERVED)
                    return error_obj
            if obj.get_ticket_amount() == None:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_BOOKING_DATA)
                return error_obj
            booking_service.insert_booking_data(data, detail_id, employee_id)
            tour_dtl_arr = []
            dtl_data = TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                   tour_id=tour_id)
            for each_data in dtl_data:
                tour_dtl_arr.append(each_data.id)
            booking_service.book_accomodation(obj, tour_dtl_arr, tour_id)

            bookinghistory_get = AccomodationBookingDetails.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id(),
                requirement_id=obj.requirement_id)
            bookinghistory_id=None
            if len(bookinghistory_get) != 0:
                bookinghistoryid = bookinghistory_get.last()
                bookinghistory_id = bookinghistoryid.id
            Tour_service = Booking_requirement(self._scope())
            if len(request.FILES) != 0:
                params = {}
                params['requirement_type'] = Travel_requirements.accomodation
                params['requirement_id'] = obj.get_requirement_id()
                params['ref_type'] = TADocUtil.TOUR
                doc_serv = Tour_service.insert_tadoc(request, params)
                if isinstance(doc_serv, NWisefinError):
                    return doc_serv

            if not bookinghistory_id is None:
                allowance = AccomodationBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=bookinghistory_id).update(
                checkin_time=obj.get_checkin_time(),
                checkout_time=obj.get_checkout_time(),
                place_of_stay=obj.get_place_of_stay(),
                booking_status=obj.get_booking_status(),
                ref_no=obj.get_ref_no(),
                ref_type=obj.get_ref_type(),
                comments=obj.get_comments(),
                travel_detail_id=detail_id,
                updated_by=employee_id,
                requirement_id=obj.get_requirement_id(),
                updated_date=datetime.now(),
                ticket_amount=obj.get_ticket_amount(),
                ticket_amount_personal = obj.ticket_amount_personal,
                official = obj.official,
                vendor_name=obj.get_vendor_name(),
                ticket_no=obj.get_ticket_no(),
                class_of_stay=obj.get_classof_stay(),
                admin_paid=obj.admin_paid,
                PNR=obj.PNR,
                fare_quoted=obj.fare_quoted,
                issuance_type=obj.issuance_type,
                website=obj.website,
                booking_date=datetime.now(),
                room_number=obj.get_room_number())

                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                return success_obj


            else:
                allowance = AccomodationBookingDetails.objects.using(self._current_app_schema()).create(
                    checkin_time=obj.get_checkin_time(),
                    checkout_time=obj.get_checkout_time(),
                    place_of_stay=obj.get_place_of_stay(),
                    ref_no=obj.get_ref_no(),
                    ref_type=obj.get_ref_type(),
                    booking_status=obj.get_booking_status(),
                    comments=obj.get_comments(),
                    travel_detail_id=detail_id,
                    created_by=employee_id,
                    requirement_id=obj.get_requirement_id(),
                    created_date=datetime.now(),entity_id=self._entity_id(),
                    ticket_amount=obj.get_ticket_amount(),vendor_name=obj.get_vendor_name(),
                    ticket_amount_personal = obj.ticket_amount_personal,
                    official = obj.official,
                    ticket_no=obj.get_ticket_no(),
                    class_of_stay=obj.get_classof_stay(),
                    admin_paid=obj.admin_paid,
                    PNR=obj.PNR,
                    fare_quoted=obj.fare_quoted,
                    issuance_type=obj.issuance_type,
                    website=obj.website,
                    booking_date=datetime.now(),
                    room_number=obj.get_room_number())
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                return success_obj

        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj

    def get_accomadation_admin(self,id):
        condition = Q(status=Filterstatus.one, id=id, entity_id=self._entity_id())
        obje = AccomodationBookingDetails.objects.using(self._current_app_schema()).get(condition)
        resp_list = NWisefinList()
        temp = AccomodationBooking_Response()
        temp.set_id(obje.id)
        temp.set_checkin_time(obje.checkin_time)
        temp.set_checkout_time(obje.checkout_time)
        temp.set_place_of_stay(obje.place_of_stay)
        temp.set_ref_no(obje.ref_no)
        temp.set_ref_type(obje.ref_type)
        temp.set_comments(obje.comments)
        temp.set_travel_detail(obje.travel_detail_id)
        temp.set_booking_status(obje.booking_status)
        temp.set_created_by(obje.created_by)
        temp.set_created_date(obje.created_date)
        temp.set_updated_by(obje.updated_by)
        temp.set_updated_date(obje.updated_date)
        temp.set_status(obje.status)
        temp.set_ticket_amount(obje.ticket_amount)
        temp.set_classof_stay(obje.class_of_stay)
        temp.set_room_number(obje.room_number)
        temp.set_ticket_no(obje.ticket_no)
        temp.set_vendor_name(obje.vendor_name)

        resp_list.append(temp)
        return resp_list


    def fetch_accomadation_admin(self,detail_array,request,all_report,vys_page,from_date,to_date,tour_id):
        condition = Q(entity_id=self._entity_id(), status=1)
        # condition &= ~Q(travel_detail_id=None, requirement_id=None)
        # if tour_id != None:
        #     condition&=Q(travel_detail_id__tour__id=tour_id)

        if from_date != None and to_date != None:
            from_date = datetime.strptime(from_date[:11], "%d-%b-%Y")
            to_date = datetime.strptime(to_date[:11], "%d-%b-%Y")
            to_date = to_date + timedelta(days=1)
            condition &= Q(booking_date__range=[from_date, to_date])

        elif from_date == None and to_date != None:
            to_date = datetime.strptime(to_date[:11], "%d-%b-%Y")
            condition &= Q(booking_date__lte=to_date)

        elif from_date != None and to_date == None:
            from_date = datetime.strptime(from_date[:11], "%d-%b-%Y")
            condition &= Q(booking_date__gte=from_date)
        if all_report == None:
            if detail_array is None:
                obje = AccomodationBookingDetails.objects.using(self._current_app_schema()).filter(condition).all().order_by("-booking_date")
            else:
                condition &=Q(travel_detail_id__in=detail_array)
                obje = AccomodationBookingDetails.objects.using(self._current_app_schema()).filter(condition).all().order_by("-booking_date")[
                       vys_page.get_offset():vys_page.get_query_limit()]
        else:
            if detail_array is None:
                obje = AccomodationBookingDetails.objects.using(self._current_app_schema()).filter(condition).all().order_by("booking_date").values("travel_detail__tour__id","travel_detail__tour__request_date","booking_date","travel_detail__tour__empgid","travel_detail__purposeofvisit","travel_detail__client","travel_detail__tour__tour_status","travel_detail__tour__international_travel","place_of_stay","checkin_time","checkout_time","travel_detail__official","comments")
            else:
                condition &=Q(travel_detail_id__in=detail_array)

                obje = AccomodationBookingDetails.objects.using(self._current_app_schema()).filter(condition).all().order_by("booking_date").values("travel_detail__tour__id","travel_detail__tour__request_date","booking_date","travel_detail__tour__empgid","travel_detail__purposeofvisit","travel_detail__client","travel_detail__tour__tour_status","travel_detail__tour__international_travel","place_of_stay","checkin_time","checkout_time","travel_detail__official","comments")
            acc_details_frame=pd.DataFrame(obje)
            whole_emp_arr = acc_details_frame["travel_detail__tour__empgid"].tolist()
            api_service = ApiService(self._scope())
            emp_det = api_service.employee_details_arr(whole_emp_arr, request)
            emp_frame = pd.DataFrame(emp_det)
            emp_frame.rename(columns={'id': 'travel_detail__tour__empgid'}, inplace=True)
            emp_team_ = api_service.emp_team_arr(whole_emp_arr, request)
            team_frame = pd.DataFrame(emp_team_)
            team_frame1 = team_frame.drop_duplicates(keep='first', subset=['employee_id'])
            team_frame1.rename(
                columns={'employee_id': 'travel_detail__tour__empgid'},
                inplace=True)
            final_out = acc_details_frame.merge(emp_frame, on='travel_detail__tour__empgid', how='left')
            final_out1 = final_out.merge(team_frame1, on='travel_detail__tour__empgid', how='left')
            client_arr = final_out1["travel_detail__client"].tolist()
            api_service = ApiService(self._scope())
            client_data = api_service.get_client_arr(request, client_arr)
            client_data_frame = pd.DataFrame(client_data)
            client_data_frame.rename(
                columns={'id': 'travel_detail__client'},
                inplace=True)
            final_out2 = final_out1.merge(client_data_frame, on='travel_detail__client', how='left')
            personal_official = {0: "Personal", 1: "Official", 2: "Official/Personal"}
            inter_domes = {0: "Domestic", 1: "International"}
            status = {-1: "TRAVEL DEFAULT",
                      0: "TRAVEL DELETED",
                      1: "TRAVEL REQUESTED",
                      2: "TRAVEL PENDING",
                      3: "TRAVEL APPROVED",
                      4: "TRAVEL REJECTED",
                      5: "TRAVEL RETURNED",
                      6: "TRAVEL FORWARDED"}
            final_out3 = final_out2.replace(
                {"travel_detail__official": personal_official,"travel_detail__tour__tour_status":status,"travel_detail__tour__international_travel":inter_domes})
            final_out3['booking date'] = final_out3['booking_date'].apply(
                lambda a: pd.to_datetime(a, errors='coerce').strftime('%d-%b-%Y'))
            final_out3['request_date'] = final_out3['travel_detail__tour__request_date'].apply(
                lambda a: pd.to_datetime(a, errors='coerce').strftime('%d-%b-%Y') if a is not None else None)
            final_out3['booking time'] = final_out3['booking_date'].apply(
                lambda a: pd.to_datetime(a, errors='coerce').strftime('%H:%M:%S') if a is not None else None)
            final_out3['checkin time'] = final_out3['checkin_time'].apply(
                lambda a: pd.to_datetime(a, errors='coerce').strftime('%H:%M:%S') if a is not None else None)
            final_out3['checkout_time'] = final_out3['checkout_time'].apply(
                lambda a: pd.to_datetime(a, errors='coerce').strftime('%H:%M:%S') if a is not None else None)
            final_out3["difference_in_days"] = final_out3["booking_date"] - final_out3["checkin_time"]

            return final_out3

        resp_list = NWisefinList()
        for eachdata in obje:
            booking_table = BookingHistory.objects.using(self._current_app_schema()).filter(
                reference_id=eachdata.requirement_id, booking_needed=Travel_requirements.accomodation).last()
            temp =AccomodationBooking_Response()
            temp.set_id(eachdata.id)
            temp.set_admincheckin_time(eachdata.checkin_time)
            temp.set_approvedby(booking_table.created_by)
            temp.set_admincheckout_time(eachdata.checkout_time)
            temp.set_check_intime(eachdata.checkin_time)
            temp.set_check_outtime(eachdata.checkout_time)
            temp.set_check_intime_xl(eachdata.checkin_time)
            temp.set_checkout_time_xl(eachdata.checkout_time)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_comments(eachdata.comments)
            temp.set_place_of_stay(eachdata.place_of_stay)
            temp.set_from_place(eachdata.place_of_stay)
            temp.set_to_place(eachdata.place_of_stay)
            temp.set_travel_detail(eachdata.travel_detail_id)
            if int(eachdata.booking_status) == 3:
                temp.set_booking_status("BOOKED")
            elif int(eachdata.booking_status) == 2:
                temp.set_booking_status("BOOKING CANCEL REQUESTED")
            elif int(eachdata.booking_status) == 4:
                temp.set_booking_status("BOOKING CANCELLED")
            elif int(eachdata.booking_status)==7:
                temp.set_booking_status("BOOKING REJECTED")
            else:
                temp.set_booking_status(None)
            status = eachdata.travel_detail.tour.tour_status
            if status == 3:
                temp.set_tour_status("TRAVEL APPROVED")
            temp.set_refund_date(booking_table.refund_date)
            temp.set_refund_amount(booking_table.refund_amount)
            temp.set_created_by(eachdata.created_by)
            temp.set_created_date(eachdata.booking_date)
            temp.set_created_date_xl(eachdata.booking_date)
            temp.set_created_time_xl(eachdata.booking_date)
            temp.set_updated_by(eachdata.updated_by)
            temp.set_costper_head(eachdata.ticket_amount)
            emp = eachdata.travel_detail.tour.empgid
            api_service = ApiService(self._scope())
            get_team = api_service.emp_team_get(emp, request)
            temp.set_team_name(get_team["team"])
            temp.set_updated_date(eachdata.updated_date)
            temp.set_status(eachdata.status)
            temp.set_purpose_ofvisit(eachdata.travel_detail.purposeofvisit)
            api_service = ApiService(self._scope())
            emp_get = api_service.employee_details_get(eachdata.travel_detail.tour.empgid,request)
            trav = TravelHistory.objects.using(self._current_app_schema()).filter(
                tour_id=eachdata.travel_detail.tour.id, applevel=App_level.FIRST_LEVEL, status=Status.APPROVED,
                request_type=App_type.TOUR).last()
            appr = 0
            if trav.onbehalfof_approval != 0:
                appr = trav.onbehalfof_approval
            else:
                appr = trav.approvedby
            if appr != 0:
                approver_get = api_service.employee_details_get(appr, request)
                temp.set_approvedby(approver_get.full_name)
                temp.set_empcode(emp_get.code)
                temp.set_empname(emp_get.full_name)
            else:
                # approver_get = api_service.employee_details_get(appr, request)
                temp.set_approvedby(None)
                temp.set_empcode(None)
                temp.set_empname(None)
            # client_name = Client.objects.using(self._current_app_schema()).get(id=eachdata.travel_detail.client)
            # temp.set_client(client_name.name)
            client_data=api_service.get_client( request, eachdata.travel_detail.client)
            temp.set_client(client_data.client_name)
            temp.set_empname(emp_get.full_name)
            domestic = eachdata.travel_detail.tour.international_travel
            if domestic == 0:
                domestic_trave = "Domestic"
            elif domestic == 1:
                domestic_trave = "International"
            temp.set_domestic(domestic_trave)
            temp.set_ticket_amount(eachdata.ticket_amount)
            temp.set_ticket_amount_personal(eachdata.ticket_amount_personal)
            temp.set_classof_stay(eachdata.class_of_stay)
            temp.set_room_number(eachdata.room_number)
            temp.set_cancel_reason(booking_table.cancel_reason)
            temp.set_weekend_travel(eachdata.travel_detail.tour.week_end_travel)
            temp.set_ticket_no(eachdata.ticket_no)
            temp.set_vendor_name(eachdata.vendor_name)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_tour_id(eachdata.travel_detail.tour.id)
            temp.set_request_date(eachdata.travel_detail.tour.request_date)
            temp.set_request_date_xl(eachdata.travel_detail.tour.request_date)
            from_time = eachdata.checkin_time
            created_date = eachdata.created_date
            # startdate = datetime.strptime((from_time[:10]), '%Y-%b-%d').date()
            # enddate = datetime.strptime((created_date[:10]), '%Y-%b-%d').date()
            duration_days = ((created_date-from_time).days)
            temp.set_difference_indays(duration_days)
            personal = eachdata.travel_detail.official
            if int(personal) == 1:
                temp.set_personal_official("Official")
            elif int(personal) == 0:
                temp.set_personal_official("Personal")
            elif int(personal)==2:
                temp.set_personal_official("Official/Personal")
            else:
                temp.set_personal_official(None)
            temp.set_booking_needed("ACCOMENDATION BOOKING")
            temp.set_pnr_no(eachdata.PNR)
            temp.set_costper_head(eachdata.cost_per_head)
            temp.set_fare_quoted(eachdata.fare_quoted)
            temp.set_difference_in_amount(eachdata.difference_in_amount)
            temp.set_issuance_type(eachdata.issuance_type)
            temp.set_loss_of_cancelation(booking_table.loss_of_cancelation)
            temp.set_cancelled_date(booking_table.cancelled_date)
            temp.set_website(eachdata.website)
            if all_report == None:
                resp_list.append(temp)
                vpage = NWisefinPaginator(obje, vys_page.get_index(), 10)
                resp_list.set_pagination(vpage)
            else:
                resp_list.append(temp)
        return resp_list


    def fetch_accomadation_admin_req(self,requirement_id):
        obje = AccomodationBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),requirement_id=requirement_id,status=1).all()
        booking_his = BookingHistory.objects.using(self._current_app_schema()).filter(reference_id=requirement_id,
                                                                                      booking_needed=Travel_requirements.accomodation).last()
        resp_list = NWisefinList()
        temp1 = All_requirement()
        cancel_detail = []
        if booking_his.booking_status == 4:
            temp1.set_cancelled_date(booking_his.cancelled_date)
            temp1.set_refund_date(booking_his.refund_date)
            temp1.set_cancel_reschedule(booking_his.cancel_reschedule)
            temp1.set_cancel_reason(booking_his.cancel_reason)
            temp1.set_refund_amount(booking_his.refund_amount)
            temp1.set_fare_difference(booking_his.fare_difference)
            temp1.set_loss_of_cancelation(booking_his.loss_of_cancelation)
            cancel_detail.append(temp1)
        for eachdata in obje:
            temp =AccomodationBooking_Response()
            temp.set_id(eachdata.id)
            temp.set_checkin_time(eachdata.checkin_time)
            temp.set_checkout_time(eachdata.checkout_time)
            temp.set_check_intime(eachdata.checkin_time)
            temp.set_check_outtime(eachdata.checkout_time)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_comments(eachdata.comments)
            temp.set_place_of_stay(eachdata.place_of_stay)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_booking_status(eachdata.booking_status)
            temp.set_created_by(eachdata.created_by)
            temp.set_created_date(eachdata.created_date)
            temp.set_updated_by(eachdata.updated_by)
            temp.set_updated_date(eachdata.updated_date)
            temp.set_status(eachdata.status)
            temp.set_utilised_status(eachdata.utilised_status)
            temp.set_noshow_reason(eachdata.noshow_reason)
            temp.set_ticket_amount(eachdata.ticket_amount)
            temp.set_ticket_amount_personal(eachdata.ticket_amount_personal)
            temp.set_cancelled_data(cancel_detail)
            temp.set_admin_paid(eachdata.admin_paid)
            temp.set_vendor_name(eachdata.vendor_name)
            temp.set_ticket_no(eachdata.ticket_no)
            temp.set_class_of_stay(eachdata.class_of_stay)
            temp.set_room_number(eachdata.room_number)
            temp.set_PNR(eachdata.PNR)
            temp.set_cost_per_head(eachdata.cost_per_head)
            temp.set_fare_quoted(eachdata.fare_quoted)
            temp.set_difference_in_amount(eachdata.difference_in_amount)
            temp.set_issuance_type(eachdata.issuance_type)
            temp.set_website(eachdata.website)
            temp.set_booking_date(eachdata.booking_date)
            resp_list.append(temp)
        return resp_list


    def accomadation_details_get_admin(self,detail_id):
        obje = AccomodationBookingDetails.objects.using(self._current_app_schema()).filter(travel_detail_id__in=detail_id,entity_id=self._entity_id(),status=1).all()
        resp_list = NWisefinList()
        for eachdata in obje:
            temp =AccomodationBooking_Response()
            temp.set_id(eachdata.id)
            temp.set_booking_needed(Travel_requirements.accomodation)
            temp.set_checkin_time(eachdata.checkin_time)
            temp.set_checkout_time(eachdata.checkout_time)
            temp.set_place_of_stay(eachdata.place_of_stay)
            temp.set_comments(eachdata.comments)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_booking_status(eachdata.booking_status)
            temp.set_status(eachdata.status)
            temp.set_created_date_time(eachdata.created_date)
            temp.set_ticket_amount(eachdata.ticket_amount)
            temp.set_ticket_amount_personal(eachdata.ticket_amount_personal)
            temp.set_classof_stay(eachdata.class_of_stay)
            temp.set_room_number(eachdata.room_number)
            temp.set_ticket_no(eachdata.ticket_no)
            temp.set_vendor_name(eachdata.vendor_name)
            temp.set_utilised_status(eachdata.utilised_status)
            temp.set_noshow_reason(eachdata.noshow_reason)
            temp.set_admin_paid(eachdata.admin_paid)
            temp.set_vendor_name(eachdata.vendor_name)
            temp.set_ticket_no(eachdata.ticket_no)
            temp.set_class_of_stay(eachdata.class_of_stay)
            temp.set_room_number(eachdata.room_number)
            temp.set_PNR(eachdata.PNR)
            temp.set_cost_per_head(eachdata.cost_per_head)
            temp.set_fare_quoted(eachdata.fare_quoted)
            temp.set_difference_in_amount(eachdata.difference_in_amount)
            temp.set_issuance_type(eachdata.issuance_type)
            temp.set_website(eachdata.website)
            temp.set_booking_date(eachdata.booking_date)

            resp_list.append(temp)
        return resp_list

    def accomadation_details_get_admin_ecf(self,detail_id,admin_paid):
        obje = AccomodationBookingDetails.objects.using(self._current_app_schema()).filter(travel_detail_id__in=detail_id,entity_id=self._entity_id(),status=1,
                                                                                           admin_paid=admin_paid).all()
        resp_list = NWisefinList()
        for eachdata in obje:
            temp =AccomodationBooking_Response()
            temp.set_id(eachdata.id)
            temp.set_booking_needed(Travel_requirements.accomodation)
            temp.set_checkin_time(eachdata.checkin_time)
            temp.set_checkout_time(eachdata.checkout_time)
            temp.set_place_of_stay(eachdata.place_of_stay)
            temp.set_comments(eachdata.comments)
            temp.set_ref_no(eachdata.ref_no)
            temp.set_ref_type(eachdata.ref_type)
            temp.set_travel_detail(eachdata.travel_detail_id)
            temp.set_booking_status(eachdata.booking_status)
            temp.set_status(eachdata.status)
            temp.set_created_date_time(eachdata.created_date)
            temp.set_ticket_amount(eachdata.ticket_amount)
            temp.set_classof_stay(eachdata.class_of_stay)
            temp.set_room_number(eachdata.room_number)
            temp.set_ticket_no(eachdata.ticket_no)
            temp.set_vendor_name(eachdata.vendor_name)

            resp_list.append(temp)
        return resp_list

    def accomadation_delete_admin(self, id):
        try:
            resp_obj = AccomodationBookingDetails.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=id).update(status=0)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj

    def req_delete_validation(self,type,id,user_id):
        error_obj = NWisefinError()
        type=int(type)
        detail_id=0
        if type==Travel_requirements.accomodation:
            accomodation_data=AccomodationBookingInfo.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=id)
            detail_id=accomodation_data.travel_detail_id
        elif type==Travel_requirements.cab:
            accomodation_data=CabBookingInfo.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=id)
            detail_id=accomodation_data.travel_detail_id
        elif type==Travel_requirements.bus:
            accomodation_data=BusBookingInfo.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=id)
            detail_id=accomodation_data.travel_detail_id
        elif type==Travel_requirements.train:
            accomodation_data=TrainBookingInfo.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=id)
            detail_id=accomodation_data.travel_detail_id
        elif type==Travel_requirements.air:
            accomodation_data=AirBookingInfo.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=id)
            detail_id=accomodation_data.travel_detail_id
        else:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
            return error_obj, detail_id


        if accomodation_data.booking_status == Requirements_booking_status.booked:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.CANT_DELETE_BOOKED_REQ)
            return error_obj,detail_id

        # dtl_count_ck=self.check_req_count(detail_id)
        # if dtl_count_ck is False:
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.CANT_DELETE_LAST_ITENARY)
        #     return error_obj,detail_id

        tour_data = TourDetail.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(), id=detail_id)
        tour_id = tour_data.tour_id
        validation_service = Validation(self._scope())
        permission_check = validation_service.permisssion_check_type(tour_id, user_id, App_type.TOUR, 0)
        if permission_check == False:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.VALID_USER)
            return error_obj,detail_id
        tour_data = TourRequest.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),
                                                                                   id=tour_id)
        if tour_data.tour_status == Status.DEFAULT or tour_data.tour_status == Status.APPROVED or tour_data.tour_status == Status.REJECTED or tour_data.tour_status == Status.FORWARDED:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.APPROVE_ERROR)
            return error_obj,detail_id
        return True,detail_id

    # def check_req_count(self,tour_detail_id):
    #     req_count=TourDetail.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=tour_detail_id)
    #     if req_count.air_required==0 and req_count.train_required==0 and req_count.bus_required==0 and req_count.cab_required==0 and req_count.accomodation_required==0:
    #         return False
    #     else:
    #         return True


    def delete_travel_requirements(self,type,id,emp_id,request):
        from taservice.service.tourmaker import TourMaker
        logger.info('ta_ delete_travel_requirements- ' + str(type) + str(id)+ str(emp_id))
        validation,detail_id=self.req_delete_validation(type,id,emp_id)
        if validation is True:
            tour_data = TourDetail.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),
                                                                                 id=detail_id)
            tour_id = tour_data.tour_id
            if type == Travel_requirements.accomodation:
                delete=self.accomadation_delete(id)
                accomodation_len = AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(), travel_detail_id=detail_id, status=1)
                if len(accomodation_len) == 0:
                    TourDetail.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=detail_id).update(accomodation_required=0)
                    TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id).update(accomodation_status=1)
            elif type == Travel_requirements.cab:
                service=Cab_requirement(self._scope())
                delete=service.Cab_delete(id)
                cab_len = CabBookingInfo.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(), travel_detail_id=detail_id, status=1)
                if len(cab_len) == 0:
                    TourDetail.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=detail_id).update(cab_required=0)
                    TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id).update(cab_status=1)
            elif type == Travel_requirements.bus:
                service=Bus_requirement(self._scope())
                delete=service.bus_delete(id)
                bus_len = BusBookingInfo.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(), travel_detail_id=detail_id, status=1)
                if len(bus_len) == 0:
                    TourDetail.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=detail_id).update(bus_required=0)
                    TourRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=tour_id).update(bus_status=1)
            elif type == Travel_requirements.train:
                service=Train_requirement(self._scope())
                delete=service.train_delete(id)
                train_len = TrainBookingInfo.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(), travel_detail_id=detail_id, status=1)
                if len(train_len) == 0:
                    TourDetail.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=detail_id).update(train_required=0)
                    TourRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=tour_id).update(train_status=1)
            elif type == Travel_requirements.air:
                service=Air_requirement(self._scope())
                delete=service.Air_delete(id)
                air_len = AirBookingInfo.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(), travel_detail_id=detail_id, status=1)
                if len(air_len) == 0:
                    TourDetail.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=detail_id).update(air_required=0)
                    TourRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=tour_id).update(air_status=1)


            travel=TourMaker(request.scope)
            data = travel.get_tour(tour_id, request)
            data=json.dumps(data, default=lambda o: o.__dict__)
            travel.edit_history(data, tour_id, 3, emp_id)

            return delete
        else:
            return validation



    def get_requirements_admin(self,req_id,type,tour_id,detail_id):
        if type==Travel_requirements.accomodation:
            service=AccomodationBooking_requirement(self._scope())
            data=service.fetch_accomadation_admin_req( req_id)
        elif type==Travel_requirements.cab:
            service = Cab_requirement(self._scope())
            data=service.fetch_cab_admin_req( req_id)
        elif type==Travel_requirements.bus:
            service = Bus_requirement(self._scope())
            data=service.fetch_Bus_admin_req( req_id)
        elif type==Travel_requirements.train:
            service = Train_requirement(self._scope())
            data=service.fetch_Train_admin_req( req_id)
        elif type==Travel_requirements.air:
            service = Air_requirement(self._scope())
            data=service.fetch_Air_admin_req(req_id)
        elif type == 0:

            if tour_id is not None:
                tour_dtl_arr = []
                dtl_data = TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                       tour_id=tour_id)
                for each_data in dtl_data:
                    tour_dtl_arr.append(each_data.id)
                    detail_id=tour_dtl_arr

            elif detail_id is not None:
                detail_id=[detail_id]

            resp_list = NWisefinList()
            temp = All_requirement()
            acc_service=AccomodationBooking_requirement(self._scope())
            acc_data=acc_service.accomadation_details_get_admin( detail_id)
            cab_service = Cab_requirement(self._scope())
            cab_data=cab_service.cab_detail_get_admin( detail_id)
            bus_service = Bus_requirement(self._scope())
            bus_data=bus_service.bus_details_get_admin( detail_id)
            train_service = Train_requirement(self._scope())
            train_data=train_service.train_details_get_admin( detail_id)
            air_service = Air_requirement(self._scope())
            air_data=air_service.air_details_get_admin(detail_id)

            temp.set_accommodation(acc_data)
            temp.set_cab(cab_data)
            temp.set_bus(bus_data)
            temp.set_train(train_data)
            temp.set_air(air_data)

            resp_list.append(temp)
            data= resp_list


        return data



    def get_requirements_admin_ecf(self,req_id,type,tour_id,detail_id,admin_paid):
        if type == 0:

            if tour_id is not None:
                tour_dtl_arr = []
                dtl_data = TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                       tour_id=tour_id)
                for each_data in dtl_data:
                    tour_dtl_arr.append(each_data.id)
                    detail_id=tour_dtl_arr

            # elif detail_id is not None:
            #     detail_id=[detail_id]

            resp_list = NWisefinList()
            temp = All_requirement()
            acc_service=AccomodationBooking_requirement(self._scope())
            acc_data=acc_service.accomadation_details_get_admin_ecf( detail_id,admin_paid)
            cab_service = Cab_requirement(self._scope())
            cab_data=cab_service.cab_detail_get_admin_ecf( detail_id,admin_paid)
            bus_service = Bus_requirement(self._scope())
            bus_data=bus_service.bus_details_get_admin_ecf( detail_id,admin_paid)
            train_service = Train_requirement(self._scope())
            train_data=train_service.train_details_get_admin_ecf( detail_id,admin_paid)
            air_service = Air_requirement(self._scope())
            air_data=air_service.air_details_get_admin_ecf(detail_id,admin_paid)

            temp.set_accommodation(acc_data)
            temp.set_cab(cab_data)
            temp.set_bus(bus_data)
            temp.set_train(train_data)
            temp.set_air(air_data)

            resp_list.append(temp)
            data= resp_list


        return data

class Booking_requirement(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)


    # def booking(self, data, employee_id):
    #     for each_data in data:
    #         each_data = Booking(each_data)
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
    #             detailid_get = AirBookingInfo.objects.using(self._current_app_schema()).get(
    #                 entity_id=self._entity_id(), id=each_data.reference_id)
    #         detail_id=detailid_get.travel_detail_id
    #         tour_id=detailid_get.travel_detail.tour_id
    #
    #         booking_val = self.booking_validations(tour_id, employee_id, detail_id, data)
    #         if booking_val is False:
    #             error_obj = NWisefinError()
    #             error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #             error_obj.set_description(ErrorDescription.BOOKING)
    #             return error_obj
    #
    #         for each_data in data:
    #             insert_booking = self.insert_booking_data(each_data, detail_id, employee_id)
    #         tour_dtl_arr = []
    #         dtl_data = TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
    #                                                                                tour_id=tour_id)
    #         for each_data in dtl_data:
    #             tour_dtl_arr.append(each_data.id)
    #         for each_dict in data:
    #             each_data = Booking(each_dict)
    #             if each_data.booking_needed == Travel_requirements.accomodation:
    #                 self.book_accomodation(each_data, tour_dtl_arr, tour_id)
    #             elif each_data.booking_needed == Travel_requirements.cab:
    #                 self.book_cab(each_data, tour_dtl_arr, tour_id)
    #             elif each_data.booking_needed == Travel_requirements.bus:
    #                 self.book_bus(each_data, tour_dtl_arr, tour_id)
    #             elif each_data.booking_needed == Travel_requirements.train:
    #                 self.book_train(each_data, tour_dtl_arr, tour_id)
    #             elif each_data.booking_needed == Travel_requirements.air:
    #                 self.book_air(each_data, tour_dtl_arr, tour_id)
    #     success_obj = NWisefinSuccess()
    #     success_obj.set_status(SuccessStatus.SUCCESS)
    #     success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
    #     return success_obj


    def book_accomodation(self,each_data,tour_dtl_arr,tour_id):
        accomodation_status = AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(),
            id=each_data.requirement_id).last()
        if accomodation_status.booking_status == 0 or accomodation_status.booking_status == -1:
            book_check=[0,-1,2]
            AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=each_data.requirement_id).update(booking_status=each_data.booking_status)
            not_booked=AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),travel_detail__in=tour_dtl_arr,status=1,
                                                                                  booking_status__in=book_check)
            book_status= len(not_booked)
            bk_status = -2
            if book_status==0:
                bk_status=each_data.booking_status
            self.update_travel_bookin_status(Travel_requirements.accomodation, tour_id, bk_status)
    def book_cab(self,each_data,tour_dtl_arr,tour_id):
        booking_status = CabBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(),
            id=each_data.requirement_id).last()
        if booking_status.booking_status == 0 or booking_status.booking_status == -1:
            book_check=[0,-1,2]
            CabBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=each_data.requirement_id).update(booking_status=each_data.booking_status)
            not_booked=CabBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),travel_detail__in=tour_dtl_arr,status=1,
                                                                                  booking_status__in=book_check)
            book_status= len(not_booked)
            bk_status = -2
            if book_status==0:
                bk_status=each_data.booking_status
            self.update_travel_bookin_status(Travel_requirements.cab, tour_id, bk_status)
    def book_cab_multiple(self,each_data,tour_dtl_arr,tour_id,requirement_id):
        booking_status = CabBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(),
            id=requirement_id).last()
        if booking_status.booking_status == 0 or booking_status.booking_status == -1:
            book_check=[0,-1,2]
            CabBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=requirement_id).update(booking_status=each_data.booking_status)
            not_booked=CabBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),travel_detail__in=tour_dtl_arr,status=1,
                                                                                  booking_status__in=book_check)
            book_status= len(not_booked)
            bk_status = -2
            if book_status==0:
                bk_status=each_data.booking_status
            self.update_travel_bookin_status(Travel_requirements.cab, tour_id, bk_status)
    def book_bus(self,each_data,tour_dtl_arr,tour_id):
        booking_status = BusBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(),
            id=each_data.requirement_id).last()
        if booking_status.booking_status == 0 or booking_status.booking_status == -1:
            book_check=[0,-1,2]
            BusBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=each_data.requirement_id).update(booking_status=each_data.booking_status)
            not_booked=BusBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),travel_detail__in=tour_dtl_arr,status=1,
                                                                                  booking_status__in=book_check)
            book_status= len(not_booked)
            bk_status = -2
            if book_status==0:
                bk_status=each_data.booking_status
            self.update_travel_bookin_status(Travel_requirements.bus, tour_id, bk_status)
    def book_train(self,each_data,tour_dtl_arr,tour_id):
        booking_status = TrainBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(),
            id=each_data.requirement_id).last()
        if booking_status.booking_status == 0 or booking_status.booking_status == -1:
            book_check=[0,-1,2]
            TrainBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=each_data.requirement_id).update(booking_status=each_data.booking_status)
            not_booked=TrainBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),travel_detail__in=tour_dtl_arr,status=1,
                                                                                  booking_status__in=book_check)
            book_status= len(not_booked)
            bk_status = -2
            if book_status==0:
                bk_status=each_data.booking_status
            self.update_travel_bookin_status(Travel_requirements.train, tour_id, bk_status)
    def book_air(self,each_data,tour_dtl_arr,tour_id):
        booking_status = AirBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(),
            id=each_data.requirement_id).last()
        if booking_status.booking_status == 0 or booking_status.booking_status == -1:

            book_check=[0,-1,2]
            AirBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=each_data.requirement_id).update(booking_status=each_data.booking_status)
            not_booked=AirBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),travel_detail__in=tour_dtl_arr,status=1,
                                                                                  booking_status__in=book_check)
            book_status= len(not_booked)
            bk_status = -2
            if book_status==0:
                bk_status=each_data.booking_status
            self.update_travel_bookin_status(Travel_requirements.air, tour_id, bk_status)

    def update_travel_bookin_status(self, type, tourid, bk_status):
        if type == Travel_requirements.accomodation:
            TourRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                              id=tourid).update(
                accomodation_status=bk_status)
        elif type == Travel_requirements.cab:
            TourRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                              id=tourid).update(cab_status=bk_status)
        elif type == Travel_requirements.bus:
            TourRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                              id=tourid).update(bus_status=bk_status)
        elif type == Travel_requirements.train:
            TourRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                              id=tourid).update(train_status=bk_status)
        elif type == Travel_requirements.air:
            TourRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                              id=tourid).update(air_status=bk_status)

    def booking_validations(self,tour_id,employee_id,detail_id,data):

        error_obj = NWisefinError()

        per_ofc=TourDetail.objects.using(self._current_app_schema()).get(id=detail_id)
        per_ofc_status=per_ofc.official

        if data.ticket_amount < 0:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID_TICKET_AMOUNT)
            return error_obj
        if data.ticket_amount_personal < 0:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.PERSONAL_AMOUNT_LESS_THAN_ZERO)
            return error_obj

        if per_ofc_status==Requirements_official.personal:
            if data.ticket_amount!=0:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_OFFICIAL_COST)
                return error_obj
        elif per_ofc_status==Requirements_official.official:
            if data.ticket_amount_personal!=0:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_PERSONAL_COST)
                return error_obj


        booking_status_array=[3,4]
        if data.booking_status == None:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID_BOOKING_DATA)
            return error_obj
        if int(data.booking_status) not in booking_status_array:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.BOOKING_BOOKING_STATUS)
            return error_obj
        travel_his=TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=tour_id,applevel=App_level.THIRD_LEVEL,request_type=App_type.TOUR)
        if len(travel_his)==0:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
            return error_obj
        approved=travel_his.last()
        # if employee_id !=approved.approvedby:
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.APPROVER)
        #     return error_obj
        travel_req = TourRequest.objects.using(self._current_app_schema()).get(id=tour_id)

        travel_cancel = TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                    tour_id=tour_id,status__in=[2,3],
                                                                                    request_type=App_type.TourCancel)
        if len(travel_cancel) != 0:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.CANCEL_SUBMITTED)
            return error_obj

        if travel_req.tour_status!=Status.APPROVED:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.TOUR_NOT_APPROVED)
            return error_obj
        # today = datetime.today().date()


        # ist_date_service=Timecalculation()
        # today = ist_date_service.ist_date()
        # tour_end_date = (travel_req.end_date).date()
        # if today > tour_end_date:
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.BOOKING_TOUR_ENDED)
        #     return error_obj

        if int(data.booking_needed_id) == 2 and int(data.travel_type_cab) == 1 and data.from_time == None:
            return True


        if data.from_time is not None:
            if travel_req.start_date.date()>  datetime.strptime(data.from_time, '%Y-%m-%d %H:%M:%S').date():
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.BOOKING_DATE_TOUR_RANGE)
                return error_obj
            # if datetime.strptime(data.from_time, '%Y-%m-%d %H:%M:%S').date()<  today:
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.BOOKING_PAST_DATE)
            #     return error_obj

        if data.checkin_time is not None:
            if travel_req.start_date.date()>  datetime.strptime(data.checkin_time, '%Y-%m-%d %H:%M:%S').date():
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.BOOKING_DATE_TOUR_RANGE)
                return error_obj
            # if datetime.strptime(data.checkin_time, '%Y-%m-%d %H:%M:%S').date()< today:
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.BOOKING_PAST_DATE)
            #     return error_obj

        if data.to_time is not None:
            if travel_req.end_date.date()<  datetime.strptime(data.to_time, '%Y-%m-%d %H:%M:%S').date():
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.BOOKING_DATE_TOUR_RANGE)
                return error_obj
            if datetime.strptime(data.to_time, '%Y-%m-%d %H:%M:%S')<=  datetime.strptime(data.from_time, '%Y-%m-%d %H:%M:%S'):
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.BOOKING_INVALID_DATE)
                return error_obj

        if data.checkout_time is not None:
            if travel_req.end_date.date()<  datetime.strptime(data.checkout_time, '%Y-%m-%d %H:%M:%S').date():
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.BOOKING_DATE_TOUR_RANGE)
                return error_obj
            if datetime.strptime(data.checkout_time, '%Y-%m-%d %H:%M:%S')<=  datetime.strptime(data.checkin_time, '%Y-%m-%d %H:%M:%S'):
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.BOOKING_INVALID_DATE)
                return error_obj
            # obj = Cab_request(data)
            # if data.ticket_amount == None or data.from_place == None or data.booking_status == None:
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.INVALID_BOOKING_DATA)
            #     return error_obj
        return True
        # travel_his=TravelHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),tour_id=tour_id,applevel=App_level.THIRD_LEVEL,request_type=App_type.TOUR)
        # if len(travel_his)==0:
        #     return False
        # approved=travel_his.last()
        # if employee_id !=approved.approvedby:
        #     return False
        # travel_req = TourRequest.objects.using(self._current_app_schema()).get(id=tour_id)
        # today = datetime.today().date()
        # tour_end_date = (travel_req.end_date).date()
        # if today >= tour_end_date:
        #     return False
        # return True

    def insert_booking_data(self, data, detailid, emp_id):
        # for each_data in data_array:
        each_data = Booking(data)
        bookinghistory_id=None

        bookinghistory_get= BookingHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                            reference_id=each_data.requirement_id,booking_needed=each_data.booking_needed)
        if len(bookinghistory_get)!=0:
            bookinghistoryid=bookinghistory_get.last()
            bookinghistory_id=bookinghistoryid.id
        if bookinghistory_id is not None:
            BookingHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                            reference_id=each_data.requirement_id,booking_needed=each_data.booking_needed).update(
                booking_status=each_data.booking_status,
                booking_time=datetime.now(),
                comments=each_data.comments,
                cancel_reschedule=each_data.cancel_reschedule,
                cancel_reason=each_data.cancel_reason,
                refund_amount=each_data.refund_amount,
                ticket_amount=each_data.ticket_amount,
                ticket_amount_personal = each_data.ticket_amount_personal,
                official = each_data.official,
                refund_date=each_data.refund_date,
                fare_difference=each_data.fare_difference,
                updated_by=emp_id,
                updated_date=datetime.now(),
                entity_id=self._entity_id())
        else:
            BookingHistory.objects.using(self._current_app_schema()).create(
                tourdetail_id=detailid,
                booking_needed=each_data.booking_needed,
                reference_id=each_data.requirement_id,
                booking_status=each_data.booking_status,
                booking_time=datetime.now(),
                comments=each_data.comments,
                cancel_reschedule=each_data.cancel_reschedule,
                cancel_reason=each_data.cancel_reason,
                refund_amount=each_data.refund_amount,
                ticket_amount=each_data.ticket_amount,
                ticket_amount_personal = each_data.ticket_amount_personal,
                official = each_data.official,
                refund_date=each_data.refund_date,
                fare_difference=each_data.fare_difference,
                created_by=emp_id,
                entity_id=self._entity_id())
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj


    def insert_booking_data_cab(self, data, detailid, emp_id,requirement_id):
        # for each_data in data_array:
        each_data = Booking(data)
        bookinghistory_id=None

        bookinghistory_get= BookingHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                            reference_id=requirement_id,booking_needed=each_data.booking_needed)
        if len(bookinghistory_get)!=0:
            bookinghistoryid=bookinghistory_get.last()
            bookinghistory_id=bookinghistoryid.id
        if bookinghistory_id is not None:
            BookingHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                            reference_id=requirement_id,booking_needed=each_data.booking_needed).update(
                booking_status=each_data.booking_status,
                booking_time=datetime.now(),
                comments=each_data.comments,
                cancel_reschedule=each_data.cancel_reschedule,
                cancel_reason=each_data.cancel_reason,
                refund_amount=each_data.refund_amount,
                ticket_amount=each_data.ticket_amount,
                ticket_amount_personal = each_data.ticket_amount_personal,
                official = each_data.official,
                refund_date=each_data.refund_date,
                fare_difference=each_data.fare_difference,
                updated_by=emp_id,
                updated_date=datetime.now(),
                entity_id=self._entity_id())
        else:
            BookingHistory.objects.using(self._current_app_schema()).create(
                tourdetail_id=detailid,
                booking_needed=each_data.booking_needed,
                reference_id=requirement_id,
                booking_status=each_data.booking_status,
                booking_time=datetime.now(),
                comments=each_data.comments,
                cancel_reschedule=each_data.cancel_reschedule,
                cancel_reason=each_data.cancel_reason,
                refund_amount=each_data.refund_amount,
                ticket_amount=each_data.ticket_amount,
                ticket_amount_personal = each_data.ticket_amount_personal,
                official = each_data.official,
                refund_date=each_data.refund_date,
                fare_difference=each_data.fare_difference,
                created_by=emp_id,
                entity_id=self._entity_id())
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj


    def insert_cab_mapping(self, data, detailid, emp_id,requirement_id,BookingDetailId):
        bookinghistory_id = None

        bookinghistory_get = CabMapping.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(),
            requirement_id=requirement_id)
        if len(bookinghistory_get) != 0:
            bookinghistoryid = bookinghistory_get.last()
            bookinghistory_id = bookinghistoryid.id
        each_data = Booking(data)
        if bookinghistory_id is not None:
            CabMapping.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),requirement_id=requirement_id).update(
                BookingDetailId=BookingDetailId,
                booking_status=each_data.booking_status,
                booking_date=datetime.now(),
                travel_detail_id=detailid,
                requirement_id=requirement_id,
                cancel_reschedule=each_data.cancel_reschedule,
                cancel_reason=each_data.cancel_reason,
                refund_amount=each_data.refund_amount,
                ticket_amount=each_data.ticket_amount,
                ticket_amount_personal = each_data.ticket_amount_personal,
                official = each_data.official,
                refund_date=each_data.refund_date,
                admin_paid=each_data.admin_paid,
                fare_difference=each_data.fare_difference,
                updated_by=emp_id,
                updated_date=datetime.now(),
                entity_id=self._entity_id())
        else:
            CabMapping.objects.using(self._current_app_schema()).create(
                BookingDetailId=BookingDetailId,
                booking_status=each_data.booking_status,
                booking_date=datetime.now(),
                travel_detail_id=detailid,
                requirement_id=requirement_id,
                cancel_reschedule=each_data.cancel_reschedule,
                cancel_reason=each_data.cancel_reason,
                refund_amount=each_data.refund_amount,
                ticket_amount=each_data.ticket_amount,
                ticket_amount_personal = each_data.ticket_amount_personal,
                official = each_data.official,
                refund_date=each_data.refund_date,
                fare_difference=each_data.fare_difference,
                created_by=emp_id,
                admin_paid=each_data.admin_paid,
                created_date=datetime.now(),
                entity_id=self._entity_id())
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def millisecond_conversion(self,obj):
        try:
            if obj.from_time is not None:
                obj.from_time = str(datetime.fromtimestamp(int(obj.from_time) / 1000.0))
            if obj.checkin_time is not None:
                obj.checkin_time = str(datetime.fromtimestamp(int(obj.checkin_time) / 1000.0))
            if obj.to_time is not None:
                obj.to_time = str(datetime.fromtimestamp(int(obj.to_time) / 1000.0))
            if obj.checkout_time is not None:
                obj.checkout_time = str(datetime.fromtimestamp(int(obj.checkout_time) / 1000.0))
        except:
            pass
        return obj
    def admin_booking_vali(self,data):
        obj = Cab_request(data)
        if obj.get_ticket_amount()==None or obj.get_from_place()==None or obj.get_booking_status()==None:
            return False
        else:
            return True

    def cancel_request(self,booking_type,requirement_id,employee_id):
        logger.info('ta_ cancel_approve- ' + str(booking_type) + str(requirement_id) + str(employee_id))
        booking_data = 0
        resp_list = NWisefinList()
        booking_status = [2, 4]
        try:
            if int(booking_type) == Travel_requirements.accomodation:
                try:
                    booking_detail = AccomodationBookingDetails.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), requirement_id=requirement_id, booking_status=3)
                    booking_info= AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=requirement_id, booking_status=3)
                    if len(booking_detail)==0 or len(booking_info)==0:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        error_obj.set_description(ErrorDescription.CANCEL_REQUIREMENT)
                        return error_obj
                    booking_data = AccomodationBookingDetails.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(),requirement_id=requirement_id,booking_status=3).update(booking_status=2)
                    booking_data = AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(),id=requirement_id,booking_status=3).update(booking_status=2)
                except Exception as e:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.CANCEL_REQUIREMENT)
                    exc=traceback.format_exc()
                    logger.info('ta_ cancel_request- ' + str(e)+str(exc))
                    return error_obj


            elif int(booking_type) == Travel_requirements.bus:
                try:
                    booking_detail = BusBookingDetails.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), requirement_id=requirement_id, booking_status=3)
                    booking_info = BusBookingInfo.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=requirement_id, booking_status=3)
                    if len(booking_detail)==0 or len(booking_info) == 0:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        error_obj.set_description(ErrorDescription.CANCEL_REQUIREMENT)
                        return error_obj
                    booking_data = BusBookingDetails.objects.using(self._current_app_schema()).filter(requirement_id=requirement_id,entity_id=self._entity_id(),booking_status=3).update(booking_status=2)
                    booking_data = BusBookingInfo.objects.using(self._current_app_schema()).filter(id=requirement_id,entity_id=self._entity_id(),booking_status=3).update(booking_status=2)
                except Exception as e:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.CANCEL_REQUIREMENT)
                    exc=traceback.format_exc()
                    logger.info('ta_ cancel_request- ' + str(e)+str(exc))
                    return error_obj
            elif int(booking_type) == Travel_requirements.train:
                try:
                    booking_detail = TrainBookingDetails.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), requirement_id=requirement_id, booking_status=3)
                    booking_info =TrainBookingInfo.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=requirement_id, booking_status=3)
                    if len(booking_detail)==0 or len(booking_info) == 0:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        error_obj.set_description(ErrorDescription.CANCEL_REQUIREMENT)
                        return error_obj
                    booking_data = TrainBookingDetails.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(),requirement_id=requirement_id,booking_status=3).update(booking_status=2)
                    booking_data = TrainBookingInfo.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(),id=requirement_id,booking_status=3).update(booking_status=2)
                except Exception as e:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.CANCEL_REQUIREMENT)
                    exc=traceback.format_exc()
                    logger.info('ta_ cancel_request- ' + str(e)+str(exc))
                    return error_obj
                # booking_data = CabMapping.objects.using(self._current_app_schema()).filter(
                #     entity_id=self._entity_id(), requirement_id=requirement_id, booking_status__in=booking_status).last()
                # booking_detailid = booking_data.BookingDetailId
                # detail = CabBookingDetails.objects.using(self._current_app_schema()).get(
                #     entity_id=self._entity_id(),id=booking_detailid)
                #
                # booking_data_update = CabMapping.objects.using(self._current_app_schema()).filter(
                #     entity_id=self._entity_id(),requirement_id=requirement_id,booking_status__in=booking_status).update(booking_status=4)
                #
                #
                #
                # booked_no=int(detail.booked_no)-1
                # cancelled_no=int(detail.cancelled_no)+1
                # detail_table=CabBookingDetails.objects.using(self._current_app_schema()).filter(
                #     entity_id=self._entity_id(),id=booking_detailid).update(booked_no=booked_no,cancelled_no=cancelled_no)

            elif int(booking_type) == Travel_requirements.air:
                try:
                    booking_detail = AirBookingDetails.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), requirement_id=requirement_id, booking_status=3)
                    booking_info = AirBookingInfo.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=requirement_id, booking_status=3)
                    if len(booking_detail)==0 or len(booking_info) == 0:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        error_obj.set_description(ErrorDescription.CANCEL_REQUIREMENT)
                        return error_obj
                    booking_data = AirBookingDetails.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(),requirement_id=requirement_id,booking_status=3).update(booking_status=2)
                    booking_data = AirBookingInfo.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(),id=requirement_id,booking_status=3).update(booking_status=2)
                except Exception as e:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.CANCEL_REQUIREMENT)
                    exc=traceback.format_exc()
                    logger.info('ta_ cancel_request- ' + str(e)+str(exc))
                    return error_obj

            elif int(booking_type) == Travel_requirements.cab:
                try:
                    booking_detail = CabMapping.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), requirement_id=requirement_id, booking_status=3)
                    booking_info = CabBookingInfo.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(), id=requirement_id, booking_status=3)
                    if len(booking_detail)==0 or len(booking_info) == 0:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                        error_obj.set_description(ErrorDescription.CANCEL_REQUIREMENT)
                        return error_obj
                    # booking_data = CabBookingDetails.objects.using(self._current_app_schema()).filter(
                    #     entity_id=self._entity_id(),requirement_id=requirement_id,booking_status=3).update(booking_status=2)
                    booking_data = CabMapping.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(),requirement_id=requirement_id,booking_status=3).update(booking_status=2)
                    booking_data = CabBookingInfo.objects.using(self._current_app_schema()).filter(
                        entity_id=self._entity_id(),id=requirement_id,booking_status=3).update(booking_status=2)
                    # booking_data = CabMapping.objects.using(self._current_app_schema()).filter(
                    #     entity_id=self._entity_id(),requirement_id=requirement_id,booking_status=3).update(booking_status=2)
                except Exception as e:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.CANCEL_REQUIREMENT)
                    exc=traceback.format_exc()
                    logger.info('ta_ cancel_request- ' + str(e)+str(exc))
                    return error_obj

            booking_history=BookingHistory.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(),reference_id=requirement_id,booking_status=3,booking_needed=int(booking_type)).update(booking_status=2)

            service=ta_email(self._scope())
            service.cancellation_report(int(requirement_id), int(booking_type))

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj



        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj

    def cancel_approve(self,data):
        logger.info('ta_ cancel_approve- '  + str(data) )
        requirement_id=data["requirement_id"]
        booking_type=data["booking_type"]

        obj = Cab_request(data)
        booking_data = 0
        resp_list = NWisefinList()
        booking_status=[2,3,4]
        try:

            amt_data = BookingHistory.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                reference_id=requirement_id, booking_status__in=booking_status,booking_needed=int(booking_type)).last()

            if amt_data.ticket_amount_personal is None:
                amt_data.ticket_amount_personal=0
            if amt_data.ticket_amount is None:
                amt_data.ticket_amount=0
            if obj.get_refund_amount() <0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_TICKET_AMOUNT)
                return error_obj
            if obj.get_loss_of_cancelation() <0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_TICKET_AMOUNT)
                return error_obj
            if round(amt_data.ticket_amount+ amt_data.ticket_amount_personal)!=round(obj.get_refund_amount()+obj.get_loss_of_cancelation()):
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.AMOUNT)
                return error_obj


            if int(booking_type) == Travel_requirements.accomodation:
                booking_detail = AccomodationBookingDetails.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(), requirement_id=requirement_id, booking_status__in=booking_status)
                booking_info = AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(), id=requirement_id, booking_status__in=booking_status)
                if len(booking_detail) == 0 or len(booking_info) == 0:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.CANCEL_REQUIREMENT)
                    return error_obj
                vali = booking_info.last()
                det_vali = booking_detail.last()
                from_time = datetime.strftime(vali.checkin_time, '%Y-%m-%d %H:%M:%S')
                from_time_s = datetime.strftime(det_vali.checkin_time, '%Y-%m-%d %H:%M:%S')
                # if datetime.strptime(from_time, '%Y-%m-%d %H:%M:%S').date() < datetime.now().date() or datetime.strptime(from_time_s,
                #                                                                                             '%Y-%m-%d %H:%M:%S').date() < datetime.now().date():
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.CANCEL_REQUIREMENT)
                #     return error_obj


                booking_data = AccomodationBookingDetails.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id(),requirement_id=requirement_id,booking_status__in=booking_status).update(booking_status=4)
                booking_data = AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id(),id=requirement_id,booking_status__in=booking_status).update(booking_status=4)
                detail = AccomodationBookingDetails.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(), requirement_id=requirement_id).last()
                detail_id = detail.travel_detail_id
                tour_id = detail.travel_detail.tour.id
                tour_dtl_arr = []
                dtl_data = TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                       tour_id=tour_id)
                for each_data in dtl_data:
                    tour_dtl_arr.append(each_data.id)
                self.cancelbook_accomodation(tour_dtl_arr,tour_id)
            elif int(booking_type) == Travel_requirements.bus:
                booking_detail = BusBookingDetails.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(), requirement_id=requirement_id, booking_status__in=booking_status)
                booking_info = BusBookingInfo.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(), id=requirement_id, booking_status__in=booking_status)
                vali = self.cancel_booking_validation(booking_detail, booking_info)
                if isinstance(vali, NWisefinError):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(vali.description)
                    return error_obj


                booking_data = BusBookingDetails.objects.using(self._current_app_schema()).filter(requirement_id=requirement_id,entity_id=self._entity_id(),booking_status__in=booking_status).update(booking_status=4)
                booking_data = BusBookingInfo.objects.using(self._current_app_schema()).filter(id=requirement_id,entity_id=self._entity_id(),booking_status__in=booking_status).update(booking_status=4)
                detail = BusBookingDetails.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(), requirement_id=requirement_id).last()
                detail_id = detail.travel_detail_id
                tour_id = detail.travel_detail.tour.id
                tour_dtl_arr = []
                dtl_data = TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                       tour_id=tour_id)
                for each_data in dtl_data:
                    tour_dtl_arr.append(each_data.id)
                self.cancelbook_bus(tour_dtl_arr,tour_id)
            elif int(booking_type) == Travel_requirements.train:
                booking_detail =TrainBookingDetails.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(), requirement_id=requirement_id, booking_status__in=booking_status)
                booking_info = TrainBookingInfo.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(), id=requirement_id, booking_status__in=booking_status)
                vali=self.cancel_booking_validation(booking_detail,booking_info)
                if isinstance(vali, NWisefinError):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(vali.description)
                    return error_obj

                booking_data = TrainBookingDetails.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(),requirement_id=requirement_id,booking_status__in=booking_status).update(booking_status=4)
                booking_data = TrainBookingInfo.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(),id=requirement_id,booking_status__in=booking_status).update(booking_status=4)
                detail = TrainBookingDetails.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(), requirement_id=requirement_id).last()
                detail_id = detail.travel_detail_id
                tour_id = detail.travel_detail.tour.id
                tour_dtl_arr = []
                dtl_data = TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                       tour_id=tour_id)
                for each_data in dtl_data:
                    tour_dtl_arr.append(each_data.id)
                self.cancelbook_train(tour_dtl_arr, tour_id)

            elif int(booking_type) == Travel_requirements.air:
                booking_detail = AirBookingDetails.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(), requirement_id=requirement_id, booking_status__in=booking_status)
                booking_info = AirBookingInfo.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(), id=requirement_id, booking_status__in=booking_status)
                vali=self.cancel_booking_validation(booking_detail,booking_info)
                if isinstance(vali, NWisefinError):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(vali.description)
                    return error_obj
                booking_data = AirBookingDetails.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(),requirement_id=requirement_id,booking_status__in=booking_status).update(booking_status=4)
                booking_data = AirBookingInfo.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(),id=requirement_id,booking_status__in=booking_status).update(booking_status=4)
                detail = AirBookingDetails.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(), requirement_id=requirement_id).last()
                detail_id = detail.travel_detail_id
                tour_id = detail.travel_detail.tour.id
                tour_dtl_arr = []
                dtl_data = TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                       tour_id=tour_id)
                for each_data in dtl_data:
                    tour_dtl_arr.append(each_data.id)
                self.cancelbook_air(tour_dtl_arr, tour_id)

            elif int(booking_type) == Travel_requirements.cab:
                booking_detail = CabMapping.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(), requirement_id=requirement_id, booking_status__in=booking_status)
                booking_info = CabBookingInfo.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(), id=requirement_id, booking_status__in=booking_status)
                vali=self.cancel_booking_validation(booking_detail,booking_info)
                if isinstance(vali, NWisefinError):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(vali.description)
                    return error_obj

                booking_data = CabMapping.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(), requirement_id=requirement_id,
                    booking_status__in=booking_status).last()
                booking_detailid = booking_data.BookingDetailId
                detail = CabBookingDetails.objects.using(self._current_app_schema()).get(
                    entity_id=self._entity_id(), id=booking_detailid)

                booking_data_update = CabMapping.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(), requirement_id=requirement_id,
                    booking_status__in=booking_status).update(booking_status=4)
                booking_data_update = CabBookingInfo.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(), id=requirement_id, booking_status__in=booking_status).update(
                    booking_status=4)

                booked_no = int(detail.booked_no) - 1
                cancelled_no = int(detail.cancelled_no) + 1
                detail_table = CabBookingDetails.objects.using(self._current_app_schema()).filter(
                    entity_id=self._entity_id(), id=booking_detailid).update(booked_no=booked_no,
                                                                             cancelled_no=cancelled_no)

                # booking_data = CabBookingInfo.objects.using(self._current_app_schema()).filter(
                #     entity_id=self._entity_id(),id=requirement_id,booking_status__in=booking_status).update(booking_status=4)
                # booking_data = CabBookingDetails.objects.using(self._current_app_schema()).filter(
                #     entity_id=self._entity_id(), requirement_id=requirement_id, booking_status__in=booking_status).update(
                #     booking_status=4)

                detail_id = booking_data.travel_detail_id
                tour_id = booking_data.travel_detail.tour.id
                tour_dtl_arr = []
                dtl_data = TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                       tour_id=tour_id)
                for each_data in dtl_data:
                    tour_dtl_arr.append(each_data.id)
                self.cancelbook_cab(tour_dtl_arr, tour_id)

            booking_history = BookingHistory.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id(), reference_id=requirement_id, booking_status__in=booking_status,booking_needed=int(booking_type)).update(
                booking_status=4, cancel_reschedule=obj.get_cancel_reschedule(), cancel_reason=obj.get_cancel_reason(),
                refund_amount=obj.get_refund_amount(), refund_date=obj.get_refund_date(),
                fare_difference=obj.get_fare_difference(), cancelled_date=obj.get_cancelled_date(),
                loss_of_cancelation=obj.get_loss_of_cancelation())
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            return success_obj


        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            exc=traceback.format_exc()
            logger.info('ta_ cancel_approve- ' + str(e)+str(exc))
            return error_obj




    def cancelbook_accomodation(self,tour_dtl_arr,tour_id):
        book_check=[0,-1,2,3]
        not_booked=AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),travel_detail__in=tour_dtl_arr,status=1,booking_status__in=book_check)
        book_status= len(not_booked)

        if book_status==0:
            bk_status=4
            self.update_travel_bookin_status(Travel_requirements.accomodation, tour_id, bk_status)
    def cancelbook_cab(self,tour_dtl_arr,tour_id):
        book_check = [0,-1,2,3]
        not_booked = CabBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(), travel_detail__in=tour_dtl_arr, status=1, booking_status__in=book_check)
        book_status = len(not_booked)

        if book_status == 0:
            bk_status = 4
            self.update_travel_bookin_status(Travel_requirements.cab, tour_id, bk_status)
    def cancelbook_bus(self,tour_dtl_arr,tour_id):
        book_check = [0,-1,2,3]
        not_booked = BusBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(), travel_detail__in=tour_dtl_arr, status=1, booking_status__in=book_check)
        book_status = len(not_booked)

        if book_status == 0:
            bk_status = 4
            self.update_travel_bookin_status(Travel_requirements.bus, tour_id, bk_status)
    def cancelbook_train(self,tour_dtl_arr,tour_id):
        book_check = [0,-1,2,3]
        not_booked = TrainBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(), travel_detail__in=tour_dtl_arr, status=1, booking_status__in=book_check)
        book_status = len(not_booked)

        if book_status == 0:
            bk_status = 4
            self.update_travel_bookin_status(Travel_requirements.train, tour_id, bk_status)
    def cancelbook_air(self,tour_dtl_arr,tour_id):
        book_check = [0,-1,2,3]
        not_booked = AirBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(), travel_detail__in=tour_dtl_arr, status=1, booking_status__in=book_check)
        book_status = len(not_booked)

        if book_status == 0:
            bk_status = 4
            self.update_travel_bookin_status(Travel_requirements.air, tour_id, bk_status)

    def reject_requirement(self,data):
        data.requirement_type=int(data.requirement_type)

        if data.requirement_type==Travel_requirements.accomodation:
            AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()
                                                                                     ,id=data.requirement_id).update(booking_status=Requirements_booking_status.rejected)
            booking_data=AccomodationBookingInfo.objects.using(self._current_app_schema()).get(entity_id=self._entity_id()
                                                                                     , id=data.requirement_id)
            tour_dtl_arr=self.get_dtl_array(booking_data)
            tour_id = booking_data.travel_detail.tour.id
            self.reject_accomodation(tour_dtl_arr,tour_id)
        elif data.requirement_type==Travel_requirements.cab:
            CabBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()
                                                                                     ,id=data.requirement_id).update(booking_status=Requirements_booking_status.rejected)
            booking_data=CabBookingInfo.objects.using(self._current_app_schema()).get(entity_id=self._entity_id()
                                                                                     , id=data.requirement_id)
            tour_dtl_arr=self.get_dtl_array(booking_data)
            tour_id = booking_data.travel_detail.tour.id
            self.reject_cab(tour_dtl_arr,tour_id)
        elif data.requirement_type==Travel_requirements.bus:
            BusBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()
                                                                                     ,id=data.requirement_id).update(booking_status=Requirements_booking_status.rejected)
            booking_data=BusBookingInfo.objects.using(self._current_app_schema()).get(entity_id=self._entity_id()
                                                                                     , id=data.requirement_id)
            tour_dtl_arr=self.get_dtl_array(booking_data)
            tour_id = booking_data.travel_detail.tour.id
            self.reject_bus(tour_dtl_arr,tour_id)
        elif data.requirement_type==Travel_requirements.train:
            TrainBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()
                                                                                     ,id=data.requirement_id).update(booking_status=Requirements_booking_status.rejected)
            booking_data=TrainBookingInfo.objects.using(self._current_app_schema()).get(entity_id=self._entity_id()
                                                                                     , id=data.requirement_id)
            tour_dtl_arr=self.get_dtl_array(booking_data)
            tour_id = booking_data.travel_detail.tour.id
            self.reject_train(tour_dtl_arr,tour_id)
        elif data.requirement_type==Travel_requirements.air:
            AirBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()
                                                                                     ,id=data.requirement_id).update(booking_status=Requirements_booking_status.rejected)
            booking_data=AirBookingInfo.objects.using(self._current_app_schema()).get(entity_id=self._entity_id()
                                                                                     , id=data.requirement_id)
            tour_dtl_arr=self.get_dtl_array(booking_data)
            tour_id = booking_data.travel_detail.tour.id
            self.reject_air(tour_dtl_arr,tour_id)
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
            return error_obj

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj



    def get_dtl_array(self,booking_data):
        tour_id = booking_data.travel_detail.tour.id
        tour_dtl_arr = []
        dtl_data = TourDetail.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                               tour_id=tour_id)
        for each_data in dtl_data:
            tour_dtl_arr.append(each_data.id)
        return tour_dtl_arr




    def reject_accomodation(self,tour_dtl_arr,tour_id):
        book_check=[0,-1,2]
        not_booked=AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),travel_detail__in=tour_dtl_arr,status=1,booking_status__in=book_check)
        if len(not_booked) == 0:
            booked_count = AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id(), travel_detail__in=tour_dtl_arr, status=1,
                booking_status=Requirements_booking_status.booked)

            if len(booked_count) > 0:
                bk_status = 3
            else:
                bk_status = 7
        else:
            bk_status = -2
        self.update_travel_bookin_status(Travel_requirements.accomodation, tour_id, bk_status)

        # tour_data=TourRequest.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),
        #                                                              id=tour_id)
        # if book_status!=0 and tour_data.accomodation_status==TourRequest_BookingStatus.Not_Booked:
        #     bk_status = 7
        #     self.update_travel_bookin_status(Travel_requirements.accomodation, tour_id, bk_status)


    def reject_cab(self,tour_dtl_arr,tour_id):
        book_check = [0,-1,2]
        not_booked = CabBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(), travel_detail__in=tour_dtl_arr, status=1, booking_status__in=book_check)
        if len(not_booked) == 0:
            booked_count = CabBookingInfo.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id(), travel_detail__in=tour_dtl_arr, status=1,
                booking_status=Requirements_booking_status.booked)

            if len(booked_count) > 0:
                bk_status = 3
            else:
                bk_status = 7
        else:
            bk_status = -2
        self.update_travel_bookin_status(Travel_requirements.cab, tour_id, bk_status)

        # tour_data=TourRequest.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),
        #                                                              id=tour_id)
        # if book_status!=0 and tour_data.cab_status==TourRequest_BookingStatus.Not_Booked:
        #     bk_status = 7
        #     self.update_travel_bookin_status(Travel_requirements.cab, tour_id, bk_status)


    def reject_bus(self,tour_dtl_arr,tour_id):
        book_check = [0,-1,2]
        not_booked = BusBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(), travel_detail__in=tour_dtl_arr, status=1, booking_status__in=book_check)
        if len(not_booked) == 0:
            booked_count = BusBookingInfo.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id(), travel_detail__in=tour_dtl_arr, status=1,
                booking_status=Requirements_booking_status.booked)

            if len(booked_count) > 0:
                bk_status = 3
            else:
                bk_status = 7
        else:
            bk_status = -2
        self.update_travel_bookin_status(Travel_requirements.bus, tour_id, bk_status)

        # tour_data=TourRequest.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),
        #                                                              id=tour_id)
        # if book_status!=0 and tour_data.bus_status==TourRequest_BookingStatus.Not_Booked:
        #     bk_status = 7
        #     self.update_travel_bookin_status(Travel_requirements.bus, tour_id, bk_status)


    def reject_train(self,tour_dtl_arr,tour_id):
        book_check = [0,-1,2]
        not_booked = TrainBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(), travel_detail__in=tour_dtl_arr, status=1, booking_status__in=book_check)

        if len(not_booked) == 0:
            booked_count = TrainBookingInfo.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id(), travel_detail__in=tour_dtl_arr, status=1,
                booking_status=Requirements_booking_status.booked)

            if len(booked_count) > 0:
                bk_status = 3
            else:
                bk_status = 7
        else :
            bk_status=-2
        self.update_travel_bookin_status(Travel_requirements.train, tour_id, bk_status)

        # tour_data=TourRequest.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),
        #                                                              id=tour_id)
        # if book_status!=0 and tour_data.train_status==TourRequest_BookingStatus.Not_Booked:
        #     bk_status = 7
        #     self.update_travel_bookin_status(Travel_requirements.train, tour_id, bk_status)


    def reject_air(self,tour_dtl_arr,tour_id):
        book_check = [0,-1,2]
        not_booked = AirBookingInfo.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id(), travel_detail__in=tour_dtl_arr, status=1, booking_status__in=book_check)
        if len(not_booked) == 0:
            booked_count = AirBookingInfo.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id(), travel_detail__in=tour_dtl_arr, status=1,
                booking_status=Requirements_booking_status.booked)

            if len(booked_count) > 0:
                bk_status = 3
            else:
                bk_status = 7
        else:
            bk_status = -2
        self.update_travel_bookin_status(Travel_requirements.air, tour_id, bk_status)

        # tour_data=TourRequest.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),
        #                                                              id=tour_id)
        # if book_status!=0 and tour_data.air_status==TourRequest_BookingStatus.Not_Booked:
        #     bk_status = 7
        #     self.update_travel_bookin_status(Travel_requirements.air, tour_id, bk_status)


    def employeeid_city(self,employeeid,request):
        api_service=ApiService(self._scope())
        branch_get=api_service.employee_details_get(employeeid,request)
        branch_data=api_service.get_branch_data(branch_get.employee_branch_id,request)
        city_get=api_service.get_address_data(branch_data.address_id,request)
        city_name=api_service.city_name(city_get.city_id,request)
        return city_name

    def insert_tadoc(self, request, data):
        try:
            logger.info('ta_ insert_tadoc- '  + str(data))
            vysfinservice = ApiService(self._scope())
            employee_id = request.employee_id
            # tour_id = data['tour_id']
            # is_maker = data['is_maker']
            # ref_type = data['ref_type']
            # detail_id = data['detail_id']
            # requirement_type = data['requirement_type']
            # requirement_id = data['requirement_id']
            from taservice.data.request.travelrequirement import Document_upload
            req_data=Document_upload(data)
            tour_id=req_data.get_tour_id()
            detail_id=0
            is_maker=0
            reqirement=0

            if req_data.get_tour_id() ==None:
                detailid_get=None
                if req_data.get_requirement_type() == Travel_requirements.accomodation:
                    detailid_get = AccomodationBookingInfo.objects.using(self._current_app_schema()).get(
                        entity_id=self._entity_id(), id=req_data.get_requirement_id())

                elif req_data.get_requirement_type() == Travel_requirements.cab:
                    detailid_get = CabBookingInfo.objects.using(self._current_app_schema()).get(
                        entity_id=self._entity_id(), id=req_data.get_requirement_id())
                elif req_data.get_requirement_type()== Travel_requirements.bus:
                    detailid_get = BusBookingInfo.objects.using(self._current_app_schema()).get(
                        entity_id=self._entity_id(), id=req_data.get_requirement_id())
                elif req_data.get_requirement_type() == Travel_requirements.train:
                    detailid_get = TrainBookingInfo.objects.using(self._current_app_schema()).get(
                        entity_id=self._entity_id(), id=req_data.get_requirement_id())
                elif req_data.get_requirement_type() == Travel_requirements.air:
                    detailid_get = AirBookingInfo.objects.using(self._current_app_schema()).get(
                        entity_id=self._entity_id(), id=req_data.get_requirement_id())
                detail_id = detailid_get.travel_detail_id
                tour_id=detailid_get.travel_detail.tour.id
                is_maker=1
                reqirement=req_data.get_requirement_id()

            if req_data.get_ref_type()==TADocUtil.CLAIM:
                is_maker=0
                # reqirement = req_data.get_requirement_id()
                # if req_data.get_requirement_type()==EXPENSE_ID.Travelling:
                #     reqirement=req_data.get_requirement_id()
                # elif req_data.get_requirement_type()==EXPENSE_ID.AssociatedExpense:
                #     reqirement=req_data.get_requirement_id()
                # elif req_data.get_requirement_type()==EXPENSE_ID.Lodging:
                #     reqirement=req_data.get_requirement_id()
                # elif req_data.get_requirement_type()==EXPENSE_ID.DailyDiem:
                #     reqirement=req_data.get_requirement_id()
                # elif req_data.get_requirement_type()==EXPENSE_ID.LocalConveyance:
                #     reqirement=req_data.get_requirement_id()
                # else:
                #     requirement_type=



            if len(request.FILES) != 0:
                docmodule_obj = DocModule()
                params = {}
                params['module'] = docmodule_obj.TA
                params['ref_id'] = tour_id
                params['ref_type'] = docmodule_obj.TA

                doc_module = docmodule_obj.TA

                response_obj = vysfinservice.ta_doc_upload(request, params)
                file_nameee=request.FILES.get('file').name
                print(file_nameee)
                docmnts_json = response_obj.get()
                docmnts_json = json.loads(docmnts_json)
                for doc_data in docmnts_json['data']:
                    ta_doc = TADocuments.objects.using(self._current_app_schema()).create(file_id=doc_data['id'],
                                                                                          entity_id=self._entity_id(),
                                                                                          ref_id=tour_id,
                                                                                          request_id=tour_id,
                                                                                          ref_type=req_data.get_ref_type(),
                                                                                          file_name=doc_data['file_name'],
                                                                                          gen_file_name=doc_data[
                                                                                              'gen_file_name'],
                                                                                          maker_or_admin=is_maker,
                                                                                          created_by=employee_id,
                                                                                          detail=detail_id,
                                                                                          requirement_type=req_data.get_requirement_type(),
                                                                                          requirement=reqirement)
                    # ta_doc.file_id = doc_data['id']
                    # ta_doc.ref_id = tour_id
                    # ta_doc.request_id = tour_id
                    # ta_doc.ref_type = ref_type
                    # ta_doc.file_name = doc_data['file_name']
                    # ta_doc.gen_file_name = doc_data['gen_file_name']
                    # ta_doc.maker_or_admin = is_maker
                    # ta_doc.created_by = employee_id
                    # ta_doc.detail = detail_id
                    # ta_doc.requirement_type = requirement_type
                    # ta_doc.requirement = requirement_id
                    # ta_doc.save()
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                return success_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            exc=traceback.format_exc()
            logger.info('ta_ insert_tadoc- ' + str(e)+str(exc))
            return error_obj

    def fetch_tadoc(self, request, tour_id, id, requirement_type, requirment,ref_type):
        employee_id = request.employee_id
        resp_list = NWisefinList()
        doc_table=None
        if tour_id==None and id==None:
            doc_table = TADocuments.objects.using(self._current_app_schema()).filter(requirement_type=requirement_type,entity_id=self._entity_id(),
                                                                                 requirement=int(requirment),ref_type=int(ref_type),status=1)
        # elif id!=None:
        #     doc_table=TADocuments.objects.using(self._current_app_schema()).filter(id=id)
        elif tour_id!=None and int(ref_type)== TADocUtil.TOUR:
            doc_table = TADocuments.objects.using(self._current_app_schema()).filter(request=tour_id,entity_id=self._entity_id(),
                                                                                     ref_type=int(ref_type),requirement=0,requirement_type=None,status=1)
        elif tour_id!=None and int(ref_type)==TADocUtil.CLAIM:
            doc_table = TADocuments.objects.using(self._current_app_schema()).filter(request=tour_id,entity_id=self._entity_id(),
                                                                                     ref_type=int(ref_type),
                                                                                     requirement_type=requirement_type,status=1)
        # elif tour_id!=None and int(ref_type)==TADocUtil.BOOKING:
        #     doc_table = TADocuments.objects.using(self._current_app_schema()).filter(request=tour_id,entity_id=self._entity_id(),
        #                                                                              ref_type=int(ref_type),
        #                                                                              requirement_type=requirement_type,status=1)

        if len(doc_table) >0:
            for data in doc_table:
                req_data = Doc_response()
                req_data.set_id(data.id)
                req_data.set_file_type(data.file_id)
                req_data.set_file_name(data.file_name)
                resp_list.append(req_data)

            return resp_list.get()

        # if doc_table != None:
        #     doc_table=doc_table.last()
        #
        #     doc_service = DocumentsService(self._scope())
        #     file_id = doc_table.file_id
        #
        #     resp_obj = doc_service.doc_download(file_id, employee_id)
        #     return resp_obj
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.NO_FILE_TA)
            return error_obj.get()


    def fetch_tadoc_AP(self, request, tour_id):
        employee_id = request.employee_id
        resp_list = NWisefinList()
        doc_table=None
        # if tour_id==None and id==None:
        #     doc_table = TADocuments.objects.using(self._current_app_schema()).filter(requirement_type=requirement_type,entity_id=self._entity_id(),
        #                                                                          requirement=int(requirment),ref_type=int(ref_type),status=1)
        # # elif id!=None:
        # #     doc_table=TADocuments.objects.using(self._current_app_schema()).filter(id=id)
        # elif tour_id!=None and int(ref_type)== TADocUtil.TOUR:
        #     doc_table = TADocuments.objects.using(self._current_app_schema()).filter(request=tour_id,entity_id=self._entity_id(),
        #                                                                              ref_type=int(ref_type),requirement=0,requirement_type=None,status=1)
        # elif tour_id!=None and int(ref_type)==TADocUtil.CLAIM:
        doc_table = TADocuments.objects.using(self._current_app_schema()).filter(request=tour_id,entity_id=self._entity_id(),
                                                                                 # ref_type=int(ref_type),requirement_type=requirement_type,
                                                                                 status=1)
        # elif tour_id!=None and int(ref_type)==TADocUtil.BOOKING:
        #     doc_table = TADocuments.objects.using(self._current_app_schema()).filter(request=tour_id,entity_id=self._entity_id(),
        #                                                                              ref_type=int(ref_type),
        #                                                                              requirement_type=requirement_type,status=1)

        if len(doc_table) >0:
            for data in doc_table:
                req_data = Doc_response()
                req_data.set_id(data.id)
                req_data.set_file_id(data.file_id)
                req_data.set_file_name(data.file_name)
                req_data.set_ref_type(data.ref_type)
                req_data.set_maker_or_admin(data.maker_or_admin)
                req_data.set_detail(data.detail)
                req_data.set_requirement_type(data.requirement_type)
                req_data.set_requirement(data.requirement)
                resp_list.append(req_data)

            return resp_list.get()

        # if doc_table != None:
        #     doc_table=doc_table.last()
        #
        #     doc_service = DocumentsService(self._scope())
        #     file_id = doc_table.file_id
        #
        #     resp_obj = doc_service.doc_download(file_id, employee_id)
        #     return resp_obj
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.NO_FILE_TA)
            return error_obj.get()



    def document_view(self,request,id,doc_option):
        # doc_get=self.fetch_tadoc(request, tour_id, id, requirement_type, requirment,ref_type)
        # doc_service = DocumentsService(self._scope())
        # file_id = doc_get.file_id
        employee_id=request.employee_id
        doc_table=0
        if id != None:
            doc_table = TADocuments.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=id,status=1)
        if doc_table==0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID_DOC_ID)
            return error_obj.get()

        # file_nam=doc_table.file_name
        # contentType=file_nam.split('.')[-1]
        if doc_option == "download":

            doc_service = DocumentsService(self._scope())
            file_id = doc_table.file_id

            resp_obj = doc_service.doc_download(file_id, employee_id)
            return resp_obj
        # if contentType == 'pdf' or contentType == 'PDF':
        #     response = HttpResponse(doc_get, content_type='application/pdf')
        #     response['Content-Disposition'] = 'inline; filename="{}"'.format(file_nam)
        # elif contentType == 'JPEG' or contentType == 'jpeg' or contentType == 'jpg' or contentType == 'JPG':
        #     response = HttpResponse(doc_get, content_type='image/jpeg')
        #     response['Content-Disposition'] = 'inline; filename="{}"'.format(file_nam)
        # elif contentType == 'png' or contentType == 'PNG':
        #     response = HttpResponse(doc_get, content_type='image/png')
        #     response['Content-Disposition'] = 'inline; filename="{}"'.format(file_nam)
        # else:
        #     response = StreamingHttpResponse(doc_get, content_type='application/octet-stream')
        #     response['Content-Disposition'] = 'inline; filename="{}"'.format(file_nam)
        if doc_option == "view":
            doc_service = DocumentsService(self._scope())

            file_id = doc_table.file_id
            file_nam = doc_table.file_name
            contentType = file_nam.split('.')[-1]

            resp_obj = doc_service.doc_download(file_id, employee_id)
            doc_view=doc_service.file_view_extention(contentType,resp_obj)
            return doc_view
        # resp_obj = doc_service.doc_download(file_id, employee_id)
    def doc_particularget(self,id,employee_id):
        doc_table=None
        if id!=None:
            doc_table=TADocuments.objects.using(self._current_app_schema()).get(entity_id=self._entity_id(),id=id)
        doc_service = DocumentsService(self._scope())
        file_id = doc_table.file_id

        resp_obj = doc_service.doc_download(file_id, employee_id)
        return resp_obj
    def doc_particular_del(self,id,employee_id):
        try:
            if id!=None:
                doc_table=TADocuments.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),id=id).update(status=0)

            # resp_obj = doc_service.doc_download(file_id, employee_id)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj
    def cancel_booking_validation(self,booking_detail,booking_info):
        if len(booking_detail) == 0 or len(booking_info) == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.CANCEL_REQUIREMENT)
            return error_obj
        return  True
        # vali = booking_info.last()
        # det_vali = booking_detail.last()
        # from_time=datetime.strftime(vali.from_time, '%Y-%m-%d %H:%M:%S')
        # from_time_s=datetime.strftime(det_vali.from_time, '%Y-%m-%d %H:%M:%S')
        # if  datetime.strptime(from_time,'%Y-%m-%d %H:%M:%S')< datetime.now() or  datetime.strptime(from_time_s,'%Y-%m-%d %H:%M:%S')< datetime.now() :
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        #     error_obj.set_description(ErrorDescription.CANCEL_REQUIREMENT)
        #     return error_obj
