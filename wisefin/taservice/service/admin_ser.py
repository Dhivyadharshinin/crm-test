from datetime import datetime

from django.db.models import Q, Max
from nwisefin.settings import logger
from taservice.data.response.tourmaker import TourMaker as TourMakerResponse
from taservice.util.ta_util import Timecalculation, App_level, Travel_requirements, Booking_status, \
    Requirements_booking_status, TourRequest_BookingStatus
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage

time_function=Timecalculation()
from taservice.data.response.touradvance import TourAdvanceResponse
from taservice.models import TravelHistory, ClaimRequest, AccomodationBookingDetails, TourDetail, CabMapping, \
    BusBookingDetails, TrainBookingDetails, AirBookingDetails, TourRequest, AccomodationBookingInfo, CabBookingInfo, \
    BusBookingInfo, TrainBookingInfo, AirBookingInfo
from taservice.service.emp_name_get import emp_dtl
from taservice.util.ta_util import Status, status_get, App_type, Filterapptype, Filterapplevel, Timecalculation
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.ta_api_service import ApiService
from utilityservice.service.threadlocal import NWisefinThread



class Admin(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)



    def admin_summary_tour(self,employee_id,vys_page,status,makerid,request_date,tour_no,request,booking_type,booking_status,branch_id):
        if request_date != "":
            try:
                request_date = int(request_date)
                request_date = str(datetime.fromtimestamp(int(request_date) / 1000.0))
                request_date = (datetime.strptime(request_date[:10], '%Y-%m-%d')).date()
            except:
                request_date = (datetime.strptime(request_date, '%d-%b-%Y')).date()
        status_check=[0,-2,2,-3,3,-4,4]

        apptype_data = [App_type.TOUR, App_type.TourCancel]
        if type == App_type.TourCancel:
            apptype_data = [App_type.TourCancel]
        condition = Q(request_type__in=apptype_data, tour__tour_status=status,
                      tour__request_date__icontains=request_date,applevel=3,
                      tour__id__icontains=tour_no, status=status, entity_id=self._entity_id())
        if makerid is not None:
            api_service=ApiService(self._scope())
            maker_id=api_service.get_emp_name(request,makerid)
            condition &= Q(tour__empgid__in=maker_id)
        if branch_id is not None:
            api_service=ApiService(self._scope())
            branch_id=api_service.get_emp_branchid(request,branch_id)
            condition &= Q(tour__empgid__in=branch_id)

        if booking_status==8:
            detail_id=[]
            error_obj = NWisefinError()
            if booking_type == Travel_requirements.accomodation or booking_type==0:
                acc_data=AccomodationBookingDetails.objects.using(self._current_app_schema()).filter(booking_status=Requirements_booking_status.cancel_requested,status=1)
                for each_data in acc_data:
                    detail_id.append(each_data.travel_detail_id)

            if booking_type == Travel_requirements.cab or booking_type==0:
                acc_data=CabMapping.objects.using(self._current_app_schema()).filter(booking_status=Requirements_booking_status.cancel_requested,status=1)
                for each_data in acc_data:
                    detail_id.append(each_data.travel_detail_id)

            if booking_type == Travel_requirements.bus or booking_type==0:
                acc_data=BusBookingDetails.objects.using(self._current_app_schema()).filter(booking_status=Requirements_booking_status.cancel_requested,status=1)
                for each_data in acc_data:
                    detail_id.append(each_data.travel_detail_id)

            if booking_type == Travel_requirements.train or booking_type==0:
                acc_data=TrainBookingDetails.objects.using(self._current_app_schema()).filter(booking_status=Requirements_booking_status.cancel_requested,status=1)
                for each_data in acc_data:
                    detail_id.append(each_data.travel_detail_id)

            if booking_type == Travel_requirements.air or booking_type==0:
                acc_data=AirBookingDetails.objects.using(self._current_app_schema()).filter(booking_status=Requirements_booking_status.cancel_requested,status=1)
                for each_data in acc_data:
                    detail_id.append(each_data.travel_detail_id)


            tour_id_array=[]
            for each_detail in detail_id:
                dtl_data = TourDetail.objects.using(self._current_app_schema()).filter(
                    id=each_detail, status=1)
                for each_data in dtl_data:
                    tour_id_array.append(each_data.tour_id)


            condition &= Q(tour__id__in=tour_id_array)



            # else:
            #     if int(booking_status) == -6:
            #         status_check = [0, -2, 2, -3, 3, -4, 4, 1, -1, -7, 7]
            #         condition &= Q(tour__air_status__in=status_check) | Q(tour__train_status__in=status_check) | Q(
            #             tour__bus_status__in=status_check) | Q(tour__cab_status__in=status_check) | Q(
            #             tour__accomodation_status__in=status_check)
            #     elif int(booking_status) == -5:
            #         status_check = [-2, 2, 0]
            #         condition &= Q(tour__air_status__in=status_check) | Q(tour__train_status__in=status_check) | Q(
            #             tour__bus_status__in=status_check) | Q(tour__cab_status__in=status_check) | Q(
            #             tour__accomodation_status__in=status_check)
            #
            #
            #     else:
            #         booking_status_array = [booking_status, abs(booking_status)]
            #         condition &= Q(
            #             Q(tour__air_status__in=booking_status_array) | Q(
            #                 tour__train_status__in=booking_status_array) | Q(
            #                 tour__bus_status__in=booking_status_array) | Q(
            #                 tour__cab_status__in=booking_status_array) | Q(
            #                 tour__accomodation_status__in=booking_status_array))
        else:

            if booking_type==Travel_requirements.accomodation:
                if booking_status is not None and int(booking_status) != -5 and int(booking_status) != -6:
                    booking_status_array=[booking_status,abs(booking_status)]
                    condition &= Q(tour__accomodation_status__in=booking_status_array)
                elif int(booking_status) == -5:
                    status_check = [-2, 2, 0]
                    condition &= Q(tour__accomodation_status__in=status_check)
                elif int(booking_status) == -6:
                    status_check = [0,-2,2,-3,3,-4,4,1,-1,-7,7]
                    condition &= Q(tour__accomodation_status__in=status_check)
                else:
                    condition &= Q(tour__accomodation_status__in=status_check)
            elif booking_type==Travel_requirements.cab:
                if booking_status is not None and int(booking_status) != -5 and int(booking_status) != -6:
                    booking_status_array=[booking_status,abs(booking_status)]
                    condition &= Q(tour__cab_status__in=booking_status_array)
                elif int(booking_status) == -5:
                    status_check = [-2, 2, 0]
                    condition &= Q(tour__cab_status__in=status_check)
                elif int(booking_status) == -6:
                    status_check = [0,-2,2,-3,3,-4,4,1,-1,-7,7]
                    condition &= Q(tour__cab_status__in=status_check)
                else:
                    condition &= Q(tour__cab_status__in=status_check)
            elif booking_type==Travel_requirements.bus:
                if booking_status is not None and int(booking_status) != -5 and int(booking_status) != -6:
                    booking_status_array=[booking_status,abs(booking_status)]
                    condition &= Q(tour__bus_status__in=booking_status_array)
                elif int(booking_status) == -5:
                    status_check = [-2, 2, 0]
                    condition &= Q(tour__bus_status__in=status_check)
                elif int(booking_status) == -6:
                    status_check = [0,-2,2,-3,3,-4,4,1,-1,-7,7]
                    condition &= Q(tour__bus_status__in=status_check)
                else:
                    condition &= Q(tour__bus_status__in=status_check)
            elif booking_type==Travel_requirements.train:
                if booking_status is not None and int(booking_status) != -5 and int(booking_status) != -6:
                    booking_status_array=[booking_status,abs(booking_status)]
                    condition &= Q(tour__train_status__in=booking_status_array)
                elif int(booking_status) == -5:
                    status_check = [-2, 2, 0]
                    condition &= Q(tour__train_status__in=status_check)
                elif int(booking_status) == -6:
                    status_check = [0,-2,2,-3,3,-4,4,1,-1,-7,7]
                    condition &= Q(tour__train_status__in=status_check)
                else:
                    condition &= Q(tour__train_status__in=status_check)
            elif booking_type==Travel_requirements.air:
                if booking_status is not None and int(booking_status) != -5 and int(booking_status) != -6:
                    booking_status_array=[booking_status,abs(booking_status)]
                    condition &= Q(tour__air_status__in=booking_status_array)
                elif int(booking_status) == -5:
                    status_check = [-2, 2, 0]
                    condition &= Q(tour__air_status__in=status_check)
                elif int(booking_status) == -6:
                    status_check = [0,-2,2,-3,3,-4,4,1,-1,-7,7]
                    condition &= Q(tour__air_status__in=status_check)
                else:
                    condition &= Q(tour__air_status__in=status_check)
            else:
                if int(booking_status) == -6:
                    status_check=[0,-2,2,-3,3,-4,4,1,-1,-7,7]
                    condition &=Q(tour__air_status__in=status_check) | Q(tour__train_status__in=status_check) | Q(
                            tour__bus_status__in=status_check) | Q(tour__cab_status__in=status_check) | Q(
                            tour__accomodation_status__in=status_check)
                elif int(booking_status) == -5:
                    status_check = [-2, 2,0]
                    condition &= Q(tour__air_status__in=status_check) | Q(tour__train_status__in=status_check) | Q(
                        tour__bus_status__in=status_check) | Q(tour__cab_status__in=status_check) | Q(
                        tour__accomodation_status__in=status_check)


                else:
                    booking_status_array = [booking_status, abs(booking_status)]
                    condition &= Q(
                        Q(tour__air_status__in=booking_status_array) | Q(tour__train_status__in=booking_status_array) | Q(
                            tour__bus_status__in=booking_status_array) | Q(tour__cab_status__in=booking_status_array) | Q(
                            tour__accomodation_status__in=booking_status_array))

        Tour_3 = TravelHistory.objects.using(self._current_app_schema()).filter(condition).values('tour').annotate(
            id=Max('id')).order_by('-tour_id')[
                 vys_page.get_offset():vys_page.get_query_limit()]
        arr_list = []
        for each_tour in Tour_3:
            arr_list.append(each_tour['id'])
        approverdata = TravelHistory.objects.using(self._current_app_schema()).filter(id__in=arr_list,
                                                                                          entity_id=self._entity_id()).order_by('-id')
        # elif type == App_type.CLAIM:
        #     condition = Q(approvedby=empid, request_type=type, applevel__gte=Status.REQUESTED,
        #                   tour__request_date__icontains=request_date,
        #                   tour__id__icontains=tour_no, status=status, entity_id=self._entity_id())
        #     if booking_type == Travel_requirements.accomodation:
        #         if booking_status is not None:
        #             condition &= Q(tour__accomodation_status=booking_status)
        #         else:
        #             condition &= Q(tour__accomodation_status__in=status_check)
        #     elif booking_type == Travel_requirements.cab:
        #         if booking_status is not None:
        #             condition &= Q(tour__cab_status=booking_status)
        #         else:
        #             condition &= Q(tour__cab_status__in=status_check)
        #     elif booking_type == Travel_requirements.bus:
        #         if booking_status is not None:
        #             condition &= Q(tour__bus_status=booking_status)
        #         else:
        #             condition &= Q(tour__bus_status__in=status_check)
        #     elif booking_type == Travel_requirements.train:
        #         if booking_status is not None:
        #             condition &= Q(tour__train_status=booking_status)
        #         else:
        #             condition &= Q(tour__train_status__in=status_check)
        #     elif booking_type == Travel_requirements.air:
        #         if booking_status is not None:
        #             condition &= Q(tour__air_status=booking_status)
        #         else:
        #             condition &= Q(tour__air_status__in=status_check)
        #     Tour_3 = TravelHistory.objects.using(self._current_app_schema()).filter(condition).values('tour').annotate(
        #         id=Max('id')).order_by('-tour_id')[
        #              vys_page.get_offset():vys_page.get_query_limit()]
        #     arr_list = []
        #     for each_tour in Tour_3:
        #         arr_list.append(each_tour['id'])
        #     approverdata = TravelHistory.objects.using(self._current_app_schema()).filter(id__in=arr_list,
        #                                                                                   entity_id=self._entity_id()).order_by(
        #         '-id')

        resp_list = NWisefinList()
        if len(approverdata) > 0:
            for apr in approverdata:
                # Tour = TourRequest.objects.using(self._current_app_schema()).get(id=apr.tour_id)
                Tour = apr.tour
                emp_id = Tour.empgid
                empdtl = ApiService(self._scope())
                detail = emp_dtl(self._scope())
                employee = empdtl.employee_details_get(emp_id, request)
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

                branch = empdtl.get_branch_data(Tour.empbranchgid, request)
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
                approver = empdtl.employee_details_get(apr.approvedby, request)
                tour_apr.set_approvedby(approver.full_name)
                tour_apr.set_approver_code(approver.code)
                tour_apr.set_approver_id(apr.approvedby)

                latest_data = TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=Tour.id,
                                                                                             entity_id=self._entity_id()).last()

                raised_by_data = TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=Tour.id,
                                                                                                request_type=type,
                                                                                                applevel=App_level.ZERO_LEVEL,
                                                                                                id__lt=apr.id,
                                                                                                entity_id=self._entity_id()).order_by("-id")
                if len(raised_by_data) != 0:
                    raised_by_data = raised_by_data[0]
                    # if raised_by_data.onbehalfof > 0:
                    #     onbehalfof = empdtl.employee_details_get(raised_by_data.onbehalfof ,request)
                    #     # tour_apr.set_onbehalfof(onbehalfof)
                    # else:
                    onbehalfof = empdtl.employee_details_get(raised_by_data.approvedby, request)
                    tour_apr.set_onbehalfof(onbehalfof)
                tour_apr.set_approveddate(apr.approveddate)
                tour_apr.set_apptype(latest_data.request_type)
                tour_apr.set_applevel(apr.applevel)
                tour_apr.set_appcomment(apr.comment)
                tour_apr.set_status(apr.status)
                status_name = status_get(latest_data.status)
                tour_apr.set_status_name(status_name)

                # if type=='TOUR' and Tour.tour_status==Status.FORWARDED:
                if type == App_type.TOUR:
                    Tour.tour_status = int(status)
                # elif type=='CLAIM' and Tour.claim_status==Status.FORWARDED:
                elif type == App_type.CLAIM:
                    Tour.claim_status = int(status)
                tour_status = status_get(Tour.tour_status)
                # advance_status = status_get(Tour.advance_status)
                claim_status = status_get(Tour.claim_status)
                tour_cancel_status = status_get(Tour.tour_cancel_status)
                # advance_cancel_status = status_get(Tour.advance_cancel_status)
                tour_apr.set_tour_status(tour_status)
                tour_apr.set_tour_cancel_status(tour_cancel_status)
                # tour_apr.set_advance_status(advance_status)
                # tour_apr.set_advance_cancel_status(advance_cancel_status)
                tour_apr.set_claim_status(claim_status)
                tour_apr.set_tour_cancel_status_id(Tour.tour_cancel_status)
                tour_apr.set_tour_status_id(Tour.tour_status)
                # tour_apr.set_advance_cancel_status_id(Tour.advance_cancel_status)
                # tour_apr.set_advance_status_id(Tour.advance_status)
                tour_apr.set_claim_status_id(Tour.claim_status)
                tour_apr.set_air_status_checker(Tour.air_status)
                tour_apr.set_train_status_checker(Tour.train_status)
                tour_apr.set_bus_status_checker(Tour.bus_status)
                tour_apr.set_cab_status_checker(Tour.cab_status)
                tour_apr.set_accomodation_status_checker(Tour.accomodation_status)

                # no_of_cancel_request_pending=0
                tour_dtl_array=[]

                tour_dtl_data=TourDetail.objects.using(self._current_app_schema()).filter(tour_id=Tour.id, status=1,
                                                                                          entity_id=self._entity_id())
                for each_dtl in tour_dtl_data:
                    tour_dtl_array.append(each_dtl.id)
                acc_cancel_pending=AccomodationBookingDetails.objects.using(self._current_app_schema()).filter(travel_detail_id__in=tour_dtl_array, status=1,
                                                                        entity_id=self._entity_id(),booking_status=Requirements_booking_status.cancel_requested)
                cab_cancel_pending=CabMapping.objects.using(self._current_app_schema()).filter(travel_detail_id__in=tour_dtl_array, status=1,
                                                                        entity_id=self._entity_id(),booking_status=Requirements_booking_status.cancel_requested)
                bus_cancel_pending=BusBookingDetails.objects.using(self._current_app_schema()).filter(travel_detail_id__in=tour_dtl_array, status=1,
                                                                        entity_id=self._entity_id(),booking_status=Requirements_booking_status.cancel_requested)
                train_cancel_pending=TrainBookingDetails.objects.using(self._current_app_schema()).filter(travel_detail_id__in=tour_dtl_array, status=1,
                                                                        entity_id=self._entity_id(),booking_status=Requirements_booking_status.cancel_requested)
                air_cancel_pending=AirBookingDetails.objects.using(self._current_app_schema()).filter(travel_detail_id__in=tour_dtl_array, status=1,
                                                                        entity_id=self._entity_id(),booking_status=Requirements_booking_status.cancel_requested)
                no_of_cancel_request_pending=len(acc_cancel_pending)+len(cab_cancel_pending)+len(bus_cancel_pending)+len(train_cancel_pending)+len(air_cancel_pending)
                tour_apr.set_no_of_cancel_request_pending(no_of_cancel_request_pending)

                if type == App_type.CLAIM:
                    claimed_amount = 0
                    claim = ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=Tour.id, status=1,
                                                                                          entity_id=self._entity_id())
                    for each_claim in claim:
                        claimed_amount += each_claim.claimedamount
                    tour_apr.set_claim_amount(claimed_amount)
                if emp_id==employee_id:
                    pass
                else:
                    resp_list.append(tour_apr)
            vpage = NWisefinPaginator(approverdata, vys_page.get_index(), 10)
            resp_list.set_pagination(vpage)
        return resp_list

    def admin_summary_expense(self, empid, type, vys_page, status, makerid, request_date, tour_no, request,branch_id):
        if request_date != "":
            try:
                request_date = int(request_date)
                request_date = str(datetime.fromtimestamp(int(request_date) / 1000.0))
                request_date = (datetime.strptime(request_date[:10], '%Y-%m-%d')).date()
            except:
                request_date = (datetime.strptime(request_date, '%d-%b-%Y')).date()


        # if type == App_type.CLAIM:
        condition = Q(approvedby=empid, request_type=App_type.CLAIM,
                      applevel=App_level.THIRD_LEVEL,
                      tour__request_date__icontains=request_date,
                      tour__id__icontains=tour_no,tour__tour_status=Status.APPROVED, status=status, entity_id=self._entity_id())
        if makerid is not None:
            condition &= Q(tour__empgid=makerid)
        Tour_3 = TravelHistory.objects.using(self._current_app_schema()).filter(condition).values('tour').annotate(
            id=Max('id')).order_by('-tour_id')[
                 vys_page.get_offset():vys_page.get_query_limit()]
        arr_list = []
        for each_tour in Tour_3:
            arr_list.append(each_tour['id'])
        approverdata = TravelHistory.objects.using(self._current_app_schema()).filter(id__in=arr_list,
                                                                                      entity_id=self._entity_id()).order_by('-id')


        resp_list = NWisefinList()
        if len(approverdata) > 0:
            for apr in approverdata:
                # Tour = TourRequest.objects.using(self._current_app_schema()).get(id=apr.tour_id)
                Tour = apr.tour
                emp_id = Tour.empgid
                empdtl = ApiService(self._scope())
                detail = emp_dtl(self._scope())
                employee = empdtl.employee_details_get(emp_id, request)
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

                branch = empdtl.get_branch_data(Tour.empbranchgid, request)
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
                approver = empdtl.employee_details_get(apr.approvedby, request)
                tour_apr.set_approvedby(approver.full_name)
                tour_apr.set_approver_code(approver.code)
                tour_apr.set_approver_id(apr.approvedby)
                raised_by_data = TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=Tour.id,
                                                                                                request_type=type,
                                                                                                applevel=App_level.ZERO_LEVEL,
                                                                                                id__lt=apr.id,
                                                                                                entity_id=self._entity_id()).order_by("-id")
                if len(raised_by_data) != 0:
                    raised_by_data = raised_by_data[0]
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
                if type == App_type.TOUR:
                    Tour.tour_status = int(status)
                # elif type=='CLAIM' and Tour.claim_status==Status.FORWARDED:
                elif type == App_type.CLAIM:
                    Tour.claim_status = int(status)
                tour_status = status_get(Tour.tour_status)
                # advance_status = status_get(Tour.advance_status)
                claim_status = status_get(Tour.claim_status)
                tour_cancel_status = status_get(Tour.tour_cancel_status)
                # advance_cancel_status = status_get(Tour.advance_cancel_status)
                tour_apr.set_tour_status(tour_status)
                tour_apr.set_tour_cancel_status(tour_cancel_status)
                # tour_apr.set_advance_status(advance_status)
                # tour_apr.set_advance_cancel_status(advance_cancel_status)
                tour_apr.set_claim_status(claim_status)
                tour_apr.set_tour_cancel_status_id(Tour.tour_cancel_status)
                tour_apr.set_tour_status_id(Tour.tour_status)
                # tour_apr.set_advance_cancel_status_id(Tour.advance_cancel_status)
                # tour_apr.set_advance_status_id(Tour.advance_status)
                tour_apr.set_claim_status_id(Tour.claim_status)
                tour_apr.set_air_status_checker(Tour.air_status)
                tour_apr.set_train_status_checker(Tour.train_status)
                tour_apr.set_bus_status_checker(Tour.bus_status)
                tour_apr.set_cab_status_checker(Tour.cab_status)
                tour_apr.set_accomodation_status_checker(Tour.accomodation_status)


                if type == App_type.CLAIM:
                    claimed_amount = 0
                    claim = ClaimRequest.objects.using(self._current_app_schema()).filter(tour_id=Tour.id, status=1,
                                                                                          entity_id=self._entity_id())
                    for each_claim in claim:
                        claimed_amount += each_claim.claimedamount
                    tour_apr.set_claim_amount(claimed_amount)

                resp_list.append(tour_apr)
            vpage = NWisefinPaginator(approverdata, vys_page.get_index(), 10)
            resp_list.set_pagination(vpage)
        return resp_list

    def admin_reserv(self,data,employee_id):
        logger.info('ta_ admin_reserv- ' + str(data) + str(employee_id))
        req_type=int(data["requirement_type"])
        req_id=int(data["requirement_id"])
        reserv_status=int(data["reserv_status"])
        # tour_id=int(data["tour_id"])
        # tour_data=TourRequest.objects.using(self._current_app_schema()).get(id=tour_id,entity_id=self._entity_id())
        error_obj = NWisefinError()

        if reserv_status==1:
            if req_type==Travel_requirements.accomodation:
                # if tour_data.accomodation_status !=TourRequest_BookingStatus.Not_Booked:
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.INVALID_BOOKING_STATUS_RESERV)
                #     return error_obj
                acc_data=AccomodationBookingInfo.objects.using(self._current_app_schema()).get(id=req_id,entity_id=self._entity_id())
                if acc_data.booking_status!=Requirements_booking_status.not_booked:
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_BOOKING_STATUS_RESERV)
                    return error_obj
                AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(id=req_id, entity_id=self._entity_id())\
                    .update(booking_status=Requirements_booking_status.in_progress,booked_by=employee_id)
                # TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id, entity_id=self._entity_id())\
                #     .update(accomodation_status=TourRequest_BookingStatus.Reserved,accomodation_booked_by=employee_id)
            elif req_type==Travel_requirements.cab:
                # if tour_data.cab_status !=TourRequest_BookingStatus.Not_Booked:
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.INVALID_BOOKING_STATUS_RESERV)
                #     return error_obj
                cab_data = CabBookingInfo.objects.using(self._current_app_schema()).get(id=req_id,
                                                                                                 entity_id=self._entity_id())
                if cab_data.booking_status != Requirements_booking_status.not_booked:
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_BOOKING_STATUS_RESERV)
                    return error_obj
                CabBookingInfo.objects.using(self._current_app_schema()).filter(id=req_id,
                                                                                         entity_id=self._entity_id()) \
                    .update(booking_status=Requirements_booking_status.in_progress, booked_by=employee_id)
                # TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id, entity_id=self._entity_id())\
                #     .update(cab_status=TourRequest_BookingStatus.Reserved,cab_booked_by=employee_id)
            elif req_type==Travel_requirements.bus:
                # if tour_data.bus_status !=TourRequest_BookingStatus.Not_Booked:
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.INVALID_BOOKING_STATUS_RESERV)
                #     return error_obj
                bus_data = BusBookingInfo.objects.using(self._current_app_schema()).get(id=req_id,
                                                                                        entity_id=self._entity_id())
                if bus_data.booking_status != Requirements_booking_status.not_booked:
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_BOOKING_STATUS_RESERV)
                    return error_obj
                BusBookingInfo.objects.using(self._current_app_schema()).filter(id=req_id,
                                                                                entity_id=self._entity_id()) \
                    .update(booking_status=Requirements_booking_status.in_progress, booked_by=employee_id)
                # TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id, entity_id=self._entity_id())\
                #     .update(bus_status=TourRequest_BookingStatus.Reserved,bus_booked_by=employee_id)
            elif req_type==Travel_requirements.train:
                # if tour_data.train_status !=TourRequest_BookingStatus.Not_Booked:
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.INVALID_BOOKING_STATUS_RESERV)
                #     return error_obj
                train_data = TrainBookingInfo.objects.using(self._current_app_schema()).get(id=req_id,
                                                                                        entity_id=self._entity_id())
                if train_data.booking_status != Requirements_booking_status.not_booked:
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_BOOKING_STATUS_RESERV)
                    return error_obj
                TrainBookingInfo.objects.using(self._current_app_schema()).filter(id=req_id,
                                                                                entity_id=self._entity_id()) \
                    .update(booking_status=Requirements_booking_status.in_progress, booked_by=employee_id)
                # TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id, entity_id=self._entity_id())\
                #     .update(train_status=TourRequest_BookingStatus.Reserved,train_booked_by=employee_id)
            elif req_type==Travel_requirements.air:
                # if tour_data.air_status !=TourRequest_BookingStatus.Not_Booked:
                #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                #     error_obj.set_description(ErrorDescription.INVALID_BOOKING_STATUS_RESERV)
                #     return error_obj
                air_data = AirBookingInfo.objects.using(self._current_app_schema()).get(id=req_id,
                                                                                        entity_id=self._entity_id())
                if air_data.booking_status != Requirements_booking_status.not_booked:
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_BOOKING_STATUS_RESERV)
                    return error_obj
                AirBookingInfo.objects.using(self._current_app_schema()).filter(id=req_id,
                                                                                entity_id=self._entity_id()) \
                    .update(booking_status=Requirements_booking_status.in_progress, booked_by=employee_id)
                # TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id, entity_id=self._entity_id())\
                #     .update(air_status=TourRequest_BookingStatus.Reserved,air_booked_by=employee_id)
            else:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
                return error_obj

        elif reserv_status==0:
            if req_type==Travel_requirements.accomodation:
                acc_data = AccomodationBookingInfo.objects.using(self._current_app_schema()).get(id=req_id,
                                                                                                 entity_id=self._entity_id())
                if acc_data.booking_status != Requirements_booking_status.in_progress:
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_BOOKING_STATUS_UNRESERV)
                    return error_obj
                if acc_data.booked_by !=employee_id:
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.THIS_BOOKING_IS_RESERVED)
                    return error_obj
                AccomodationBookingInfo.objects.using(self._current_app_schema()).filter(id=req_id,
                                                                                         entity_id=self._entity_id()) \
                    .update(booking_status=Requirements_booking_status.not_booked, booked_by=0)
            elif req_type==Travel_requirements.cab:
                cab_data = CabBookingInfo.objects.using(self._current_app_schema()).get(id=req_id,
                                                                                        entity_id=self._entity_id())
                if cab_data.booking_status != Requirements_booking_status.in_progress:
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_BOOKING_STATUS_UNRESERV)
                    return error_obj
                if cab_data.booked_by !=employee_id:
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.THIS_BOOKING_IS_RESERVED)
                    return error_obj
                CabBookingInfo.objects.using(self._current_app_schema()).filter(id=req_id,
                                                                                entity_id=self._entity_id()) \
                    .update(booking_status=Requirements_booking_status.not_booked, booked_by=0)
            elif req_type==Travel_requirements.bus:
                bus_data = BusBookingInfo.objects.using(self._current_app_schema()).get(id=req_id,
                                                                                        entity_id=self._entity_id())
                if bus_data.booking_status != Requirements_booking_status.in_progress:
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_BOOKING_STATUS_UNRESERV)
                    return error_obj
                if bus_data.booked_by != employee_id:
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.THIS_BOOKING_IS_RESERVED)
                    return error_obj
                BusBookingInfo.objects.using(self._current_app_schema()).filter(id=req_id,
                                                                                entity_id=self._entity_id()) \
                    .update(booking_status=Requirements_booking_status.not_booked, booked_by=0)
            elif req_type==Travel_requirements.train:
                train_data = TrainBookingInfo.objects.using(self._current_app_schema()).get(id=req_id,
                                                                                            entity_id=self._entity_id())
                if train_data.booking_status != Requirements_booking_status.in_progress:
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_BOOKING_STATUS_UNRESERV)
                    return error_obj
                if train_data.booked_by != employee_id:
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.THIS_BOOKING_IS_RESERVED)
                    return error_obj
                TrainBookingInfo.objects.using(self._current_app_schema()).filter(id=req_id,
                                                                                  entity_id=self._entity_id()) \
                    .update(booking_status=Requirements_booking_status.not_booked, booked_by=0)
            elif req_type==Travel_requirements.air:
                air_data = AirBookingInfo.objects.using(self._current_app_schema()).get(id=req_id,
                                                                                        entity_id=self._entity_id())
                if air_data.booking_status != Requirements_booking_status.in_progress:
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.INVALID_BOOKING_STATUS_UNRESERV)
                    return error_obj
                if air_data.booked_by != employee_id:
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(ErrorDescription.THIS_BOOKING_IS_RESERVED)
                    return error_obj
                AirBookingInfo.objects.using(self._current_app_schema()).filter(id=req_id,
                                                                                entity_id=self._entity_id()) \
                    .update(booking_status=Requirements_booking_status.not_booked, booked_by=0)
            else:
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
                return error_obj
        else:
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
            return error_obj
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj

    #
    # def admin_reserv(self,data,employee_id):
    #     logger.info('ta_ admin_reserv- ' + str(data) + str(employee_id))
    #     req_type=int(data["requirement_type"])
    #     reserv_status=int(data["reserv_status"])
    #     tour_id=int(data["tour_id"])
    #     tour_data=TourRequest.objects.using(self._current_app_schema()).get(id=tour_id,entity_id=self._entity_id())
    #     error_obj = NWisefinError()
    #
    #     if reserv_status==1:
    #         if req_type==Travel_requirements.accomodation:
    #             if tour_data.accomodation_status !=TourRequest_BookingStatus.Not_Booked:
    #                 error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #                 error_obj.set_description(ErrorDescription.INVALID_BOOKING_STATUS_RESERV)
    #                 return error_obj
    #             TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id, entity_id=self._entity_id())\
    #                 .update(accomodation_status=TourRequest_BookingStatus.Reserved,accomodation_booked_by=employee_id)
    #         elif req_type==Travel_requirements.cab:
    #             if tour_data.cab_status !=TourRequest_BookingStatus.Not_Booked:
    #                 error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #                 error_obj.set_description(ErrorDescription.INVALID_BOOKING_STATUS_RESERV)
    #                 return error_obj
    #             TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id, entity_id=self._entity_id())\
    #                 .update(cab_status=TourRequest_BookingStatus.Reserved,cab_booked_by=employee_id)
    #         elif req_type==Travel_requirements.bus:
    #             if tour_data.bus_status !=TourRequest_BookingStatus.Not_Booked:
    #                 error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #                 error_obj.set_description(ErrorDescription.INVALID_BOOKING_STATUS_RESERV)
    #                 return error_obj
    #             TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id, entity_id=self._entity_id())\
    #                 .update(bus_status=TourRequest_BookingStatus.Reserved,bus_booked_by=employee_id)
    #         elif req_type==Travel_requirements.train:
    #             if tour_data.train_status !=TourRequest_BookingStatus.Not_Booked:
    #                 error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #                 error_obj.set_description(ErrorDescription.INVALID_BOOKING_STATUS_RESERV)
    #                 return error_obj
    #             TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id, entity_id=self._entity_id())\
    #                 .update(train_status=TourRequest_BookingStatus.Reserved,train_booked_by=employee_id)
    #         elif req_type==Travel_requirements.air:
    #             if tour_data.air_status !=TourRequest_BookingStatus.Not_Booked:
    #                 error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #                 error_obj.set_description(ErrorDescription.INVALID_BOOKING_STATUS_RESERV)
    #                 return error_obj
    #             TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id, entity_id=self._entity_id())\
    #                 .update(air_status=TourRequest_BookingStatus.Reserved,air_booked_by=employee_id)
    #         else:
    #             error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #             error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
    #             return error_obj
    #
    #     elif reserv_status==0:
    #         if req_type==Travel_requirements.accomodation:
    #             if tour_data.accomodation_status >=0:
    #                 error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #                 error_obj.set_description(ErrorDescription.INVALID_BOOKING_STATUS_UNRESERV)
    #                 return error_obj
    #             TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id, entity_id=self._entity_id())\
    #                 .update(accomodation_status=TourRequest_BookingStatus.Not_Booked,accomodation_booked_by=0)
    #         elif req_type==Travel_requirements.cab:
    #             if tour_data.cab_status  >=0:
    #                 error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #                 error_obj.set_description(ErrorDescription.INVALID_BOOKING_STATUS_UNRESERV)
    #                 return error_obj
    #             TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id, entity_id=self._entity_id())\
    #                 .update(cab_status=TourRequest_BookingStatus.Not_Booked,cab_booked_by=0)
    #         elif req_type==Travel_requirements.bus:
    #             if tour_data.bus_status  >=0:
    #                 error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #                 error_obj.set_description(ErrorDescription.INVALID_BOOKING_STATUS_UNRESERV)
    #                 return error_obj
    #             TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id, entity_id=self._entity_id())\
    #                 .update(bus_status=TourRequest_BookingStatus.Not_Booked,bus_booked_by=0)
    #         elif req_type==Travel_requirements.train:
    #             if tour_data.train_status  >=0:
    #                 error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #                 error_obj.set_description(ErrorDescription.INVALID_BOOKING_STATUS_UNRESERV)
    #                 return error_obj
    #             TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id, entity_id=self._entity_id())\
    #                 .update(train_status=TourRequest_BookingStatus.Not_Booked,train_booked_by=0)
    #         elif req_type==Travel_requirements.air:
    #             if tour_data.air_status  >=0:
    #                 error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #                 error_obj.set_description(ErrorDescription.INVALID_BOOKING_STATUS_UNRESERV)
    #                 return error_obj
    #             TourRequest.objects.using(self._current_app_schema()).filter(id=tour_id, entity_id=self._entity_id())\
    #                 .update(air_status=TourRequest_BookingStatus.Not_Booked,air_booked_by=0)
    #         else:
    #             error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #             error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
    #             return error_obj
    #     else:
    #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #         error_obj.set_description(ErrorDescription.INVALID_DATA_TA)
    #         return error_obj
    #     success_obj = NWisefinSuccess()
    #     success_obj.set_status(SuccessStatus.SUCCESS)
    #     success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
    #     return success_obj

