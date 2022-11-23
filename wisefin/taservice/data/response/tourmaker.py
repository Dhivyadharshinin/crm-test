import json

from taservice.util.ta_util import booking_status_get, travel_requirements_get


class TourMaker:
    id = None
    requestno = None
    requestdate = None
    empgid = None
    empdesignation = None
    empgrade = None
    empbranchgid = None
    stategid = None
    reason = None
    reasonname = None
    permittedby = None
    startdate = None
    enddate = None
    durationdays = None
    eligiblemodeoftravel = None
    ordernoremarks = None
    onbehalfof = None
    status = None
    placeofvisit = None
    startingpoint = None
    purposeofvisit = None
    tourid = None
    detail = []
    approve = []
    opening_balance=0
    quantum_of_funds=0
    employee_name=None
    employee_code=None
    branch_name=None
    branch_code=None
    is_tour_ended=None
    is_tour_started=None
    official=None
    non_base_location=None

    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_type(self, type):
        self.type = type
    def set_tourgid(self, tourgid):
        self.tourgid = tourgid
    def set_requestno(self, requestno):
        self.requestno = requestno
    def set_transfer_on_promotion(self, transfer_on_promotion):
        self.transfer_on_promotion = transfer_on_promotion
    def set_advance_amount(self, advance_amount):
        self.advance_amount = advance_amount
    def set_requestdate(self, requestdate):
        if requestdate is None:
            self.requestdate=requestdate
        else:
            # requestdate = requestdate.strftime("%d-%b-%Y")
            self.requestdate = requestdate.strftime("%d-%b-%Y")
            self.requestdate_ms =round(requestdate.timestamp() * 1000)
    def set_empgid(self, empgid):
        self.empgid = empgid
    def set_empdesignation(self, empdesignation):
        self.empdesignation = empdesignation
    def set_empgrade(self, empgrade):
        self.empgrade = empgrade
    def set_empbranchgid(self, empbranchgid):
        self.empbranchgid = empbranchgid
    def set_unread_message(self, unread_message):
        self.unread_message = unread_message
    def set_no_of_chats(self, no_of_chats):
        self.no_of_chats = no_of_chats
    def set_sortterm_travel(self, sortterm_travel):
        self.sortterm_travel = sortterm_travel
    def set_non_base_location(self,non_base_location):
        self.non_base_location = non_base_location
    def set_stategid(self, stategid):
        self.stategid = stategid
    def set_reason(self, reason):
        self.reason = reason
    def set_reason_id(self, reason_id):
        self.reason_id = reason_id
    def set_reason_data(self, reason,reason_id):
        self.reason_data = {"id":reason_id,"name":reason}
    def set_fileupload(self, fileupload):
        self.fileupload = fileupload
    def set_international(self, international):
        self.international_travel = international
    def set_reasonname(self, reasonname):
        self.reasonname = reasonname
    def set_permittedby(self, permittedby):
        self.permittedby = permittedby
    def set_permitted_by_data(self, permitted_by_data):
        self.permitted_by_data = permitted_by_data
    def set_permittedby_id(self, permittedby_id):
        self.permittedby_id = permittedby_id
    def set_permittedby_code(self, permittedby_code):
        self.permittedby_code = permittedby_code
    def set_startdate(self, startdate):
        if startdate is None:
            self.startdate = startdate
        else:
            self.startdate = startdate.strftime("%d-%b-%Y")
            self.startdate_ms =round(startdate.timestamp() * 1000)
    def set_enddate(self, enddate):
        if enddate is None:
            self.enddate=enddate
        else:
            self.enddate = enddate.strftime("%d-%b-%Y")
            self.enddate_ms =round(enddate.timestamp() * 1000)
    def set_branch_name(self,branch_name):
        self.branch_name=branch_name
    def set_branch_data_maker(self,branch_data_maker):
        self.branch_data_maker=branch_data_maker
    def set_approver_name(self,approver_name):
        self.approver_name=approver_name
    def set_branch_code(self,branch_code):
        self.branch_code=branch_code

    # def set_enddate(self, enddate):
    #     self.enddate = enddate.strftime("%d-%b-%Y")

    def set_durationdays(self, durationdays):
        self.durationdays = durationdays
    def set_official(self, official):
        self.official = official
    def set_eligiblemodeoftravel(self, eligiblemodeoftravel):
        self.eligiblemodeoftravel = eligiblemodeoftravel
    def set_ordernoremarks(self, ordernoremarks):
        self.ordernoremarks = ordernoremarks
    def set_onbehalfof(self, onbehalfof):
        self.onbehalfof = onbehalfof
    def set_onbehalfof_id(self, onbehalfof_id):
        self.onbehalfof_id = onbehalfof_id
    def set_onbehalfof_code(self, onbehalfof_code):
        self.onbehalfof_code = onbehalfof_code
    def set_status(self, status):
        self.status = status
    def set_status_name(self, status_name):
        self.status_name = status_name
    def set_tour_status(self, tour_status):
        self.tour_status = tour_status
    def set_advance_status(self, advance_status):
        self.advance_status = advance_status
    def set_tour_cancel_status(self, tour_cancel_status):
        self.tour_cancel_status = tour_cancel_status
    def set_advance_cancel_status(self, advance_cancel_status):
        self.advance_cancel_status = advance_cancel_status
    def set_claim_status(self, claim_status):
        self.claim_status = claim_status
    def set_tour_status_id(self, tour_status_id):
        self.tour_status_id = tour_status_id
    def set_advance_status_id(self, advance_status_id):
        self.advance_status_id = advance_status_id
    def set_tour_cancel_status_id(self, tour_cancel_status_id):
        self.tour_cancel_status_id = tour_cancel_status_id
    def set_advance_cancel_status_id(self, advance_cancel_status_id):
        self.advance_cancel_status_id = advance_cancel_status_id
    def set_claim_status_id(self, claim_status_id):
        self.claim_status_id = claim_status_id
    def set_claim_amount(self, claim_amount):
        self.claim_amount = claim_amount
    def set_tour_approvedby(self, tour_approvedby):
        self.tour_approvedby = tour_approvedby
    def set_total_advance(self, total_advance):
        self.total_advance = total_advance
    def set_adv_amount(self,adv_amount):
        self.adv_amount =adv_amount
    def set_code(self, code):
        self.code = code
    def set_name(self, name):
        self.name = name
    def set_tourid(self, tourid):
        self.tourid = tourid
    def set_approver_id(self, approver_id):
        self.approver_id = approver_id
    def set_onb_approver_id(self, onb_approver_id):
        self.onb_approver_id = onb_approver_id
    def set_file_required(self, file_required):
        self.file_required = file_required
    def set_date_relaxation(self, date_relaxation):
        self.date_relaxation = date_relaxation

    def set_startingpoint(self, startingpoint):
        self.startingpoint = startingpoint
    def set_placeofvisit(self, placeofvisit):
        self.placeofvisit = placeofvisit
    def set_purposeofvisit(self, purposeofvisit):
        self.purposeofvisit = purposeofvisit
    def set_approveddate(self, approveddate):
        if approveddate is None:
            self.approveddate = approveddate
        else:
            self.approveddate = approveddate.strftime("%d-%b-%Y")
            self.approveddate_ms =round(approveddate.timestamp() * 1000)
    def set_approvedby(self, approvedby):
        self.approvedby = approvedby
    def set_onb_approvedby(self, onb_approvedby):
        self.onb_approvedby = onb_approvedby
    def set_approvedby_code(self, approvedby_code):
        self.approvedby_code = approvedby_code
    def set_approver_code(self, approver_code):
        self.approver_code = approver_code
    def set_onb_approver_code(self, onb_approver_code):
        self.onb_approver_code = onb_approver_code
    def set_onb_approver_name(self, onb_approver_name):
        self.onb_approver_name = onb_approver_name
    def set_approvedby_id(self, approvedby_id):
        self.approvedby_id = approvedby_id
    def set_comment(self, comment):
        self.comment = comment
    def set_is_tour_ended(self, is_tour_ended):
        self.is_tour_ended = is_tour_ended
    def set_is_tour_started(self, is_tour_started):
        self.is_tour_started= is_tour_started
    def set_requested_amount(self, requested_amount):
        self.requested_amount = requested_amount
    def set_approved_amount(self, approved_amount):
        self.approved_amount = approved_amount
    def set_approver_branch_data(self, approver_branch_data):
        self.approver_branch_data = approver_branch_data
    def set_approver_branch_code(self, approver_branch_code):
        self.approver_branch_code = approver_branch_code
    def set_max_applevel(self, max_applevel):
        self.max_applevel = max_applevel
    def set_accomodation_booked_by(self, accomodation_booked_by):
        self.accomodation_booked_by = accomodation_booked_by
    def set_cab_booked_by(self, cab_booked_by):
        self.cab_booked_by = cab_booked_by
    def set_bus_booked_by(self, bus_booked_by):
        self.bus_booked_by = bus_booked_by
    def set_train_booked_by(self, train_booked_by):
        self.train_booked_by = train_booked_by
    def set_air_booked_by(self, air_booked_by):
        self.air_booked_by = air_booked_by

    def set_approver_data(self,id,name,code):
        response=TourMaker()
        response.set_id(id)
        response.set_name(name)
        response.set_code(code)
        self.approver_data=response

    def set_onb_approver_data(self,id,name,code):
        response=TourMaker()
        response.set_id(id)
        response.set_name(name)
        response.set_code(code)
        self.onb_approver_data=response

    def set_apptype(self, apptype):
        self.apptype = apptype
    def set_applevel(self, applevel):
        self.applevel = applevel
    def set_appcomment(self, appcomment):
        self.appcomment = appcomment
    def set_approve(self, approve):
        self.approve = approve
    def set_advance(self, advance):
        self.advance = advance
    def set_tc_maker(self, tc_maker):
        self.tc_maker = tc_maker
    def set_latest_applevel(self, latest_applevel):
        self.latest_applevel = latest_applevel
    def set_tc_onb(self, tc_onb):
        self.tc_onb = tc_onb
    def set_ac_maker(self, ac_maker):
        self.ac_maker = ac_maker
    def set_ac_onb(self, ac_onb):
        self.ac_onb = ac_onb
    def set_detail(self, detail):
        self.detail = detail
    def set_travel_details(self, travel_details):
        self.travel_details = travel_details
    def set_employee_name(self,employee_name):
        self.employee_name=employee_name
    def set_employee_code(self,employee_code):
        self.employee_code=employee_code
    def set_tour_cancel_approver_data(self,tour_cancel_approver_data):
        self.tour_cancel_approver_data=tour_cancel_approver_data
    def set_advance_cancel_approver_data(self,advance_cancel_approver_data):
        self.advance_cancel_approver_data=advance_cancel_approver_data
    def set_tour_cancel_comment(self,tour_cancel_comment):
        self.tour_cancel_comment=tour_cancel_comment
    def set_advance_cancel_comment(self,advance_cancel_comment):
        self.advance_cancel_comment=advance_cancel_comment
    def set_tour_cancel_approver_comment(self,tour_cancel_approver_comment):
        self.tour_cancel_approver_comment=tour_cancel_approver_comment
    def set_advance_cancel_approver_comment(self,advance_cancel_approver_comment):
        self.advance_cancel_approver_comment=advance_cancel_approver_comment
    def set_air_status(self, air_status):
        air_status=max(0,air_status)
        self.air_status_id = air_status
        air_status_name = booking_status_get(air_status)
        self.air_status_name = air_status_name
    def set_train_status(self, train_status):
        train_status=max(0,train_status)
        self.train_status_id = train_status
        train_status_name = booking_status_get(train_status)
        self.train_status_name = train_status_name
    def set_bus_status(self, bus_status):
        bus_status=max(0,bus_status)
        self.bus_status_id = bus_status
        bus_status_name = booking_status_get(bus_status)
        self.bus_status_name = bus_status_name
    def set_cab_status(self, cab_status):
        cab_status=max(0,cab_status)
        self.cab_status_id = cab_status
        cab_status_name = booking_status_get(cab_status)
        self.cab_status_name = cab_status_name
    def set_accomodation_status(self, accomodation_status):
        accomodation_status=max(0,accomodation_status)
        self.accomodation_status_id = accomodation_status
        accomodation_status_name = booking_status_get(accomodation_status)
        self.accomodation_status_name = accomodation_status_name


    def set_air_status_checker(self, air_status):
        self.air_status_id = air_status
        air_status_name = booking_status_get(air_status)
        self.air_status_name = air_status_name
    def set_train_status_checker(self, train_status):
        self.train_status_id = train_status
        train_status_name = booking_status_get(train_status)
        self.train_status_name = train_status_name
    def set_bus_status_checker(self, bus_status):
        self.bus_status_id = bus_status
        bus_status_name = booking_status_get(bus_status)
        self.bus_status_name = bus_status_name
    def set_cab_status_checker(self, cab_status):
        self.cab_status_id = cab_status
        cab_status_name = booking_status_get(cab_status)
        self.cab_status_name = cab_status_name
    def set_accomodation_status_checker(self, accomodation_status):
        self.accomodation_status_id = accomodation_status
        accomodation_status_name = booking_status_get(accomodation_status)
        self.accomodation_status_name = accomodation_status_name


    def set_toplace(self, toplace):
        self.toplace = toplace
    def set_no_of_cancel_request_pending(self, no_of_cancel_request_pending):
        self.no_of_cancel_request_pending = no_of_cancel_request_pending
    def set_client(self, client):
        self.client = client
    def set_other_client_name(self, other_client_name):
        self.other_client_name = other_client_name
    def set_booking_needed(self, booking_needed):
        self.booking_needed_id = booking_needed
        booking_needed_name=travel_requirements_get(booking_needed)
        self.booking_needed_name = booking_needed_name
    def set_booking_status(self, booking_status):
        self.booking_status = booking_status
    def set_air_required(self, air_required):
        self.air_required = air_required
    def set_train_required(self, train_required):
        self.train_required = train_required
    def set_bus_required(self, bus_required):
        self.bus_required = bus_required
    def set_cab_required(self, cab_required):
        self.cab_required = cab_required
    def set_accomodation_required(self, accomodation_required):
        self.accomodation_required = accomodation_required
    def set_requirement(self, requirement):
        self.requirement = requirement
    def set_tour_id(self, tour_id):
        self.tour_id = tour_id
    def set_detail_id(self, detail_id):
        self.detail_id = detail_id
    def set_comments(self, comments):
        self.comments = comments
    def set_cancel_reschedule(self, cancel_reschedule):
        self.cancel_reschedule = cancel_reschedule
    def set_cancel_reason(self, cancel_reason):
        self.cancel_reason = cancel_reason
    def set_refund_amount(self, refund_amount):
        self.refund_amount = refund_amount
    def set_refund_date(self, refund_date):
        self.refund_date = refund_date
    def set_fare_difference(self, fare_difference):
        self.fare_difference = fare_difference
    def set_total_claimed_amount(self, total_claimed_amount):
        self.total_claimed_amount = total_claimed_amount
    def set_total_booked_amount(self, total_booked_amount):
        self.total_booked_amount = total_booked_amount
    def set_latest_approval_tour(self, latest_approval_tour):
        self.latest_approval_tour = latest_approval_tour
    def set_latest_approval_tour_onb(self, latest_approval_tour_onb):
        self.latest_approval_tour_onb = latest_approval_tour_onb
    def set_latest_approval_tour_cancel(self, latest_approval_tour_cancel):
        self.latest_approval_tour_cancel = latest_approval_tour_cancel
    def set_latest_approval_tour_cancel_onb(self, latest_approval_tour_cancel_onb):
        self.latest_approval_tour_cancel_onb = latest_approval_tour_cancel_onb
    def set_latest_approval_claim(self, latest_approval_claim):
        self.latest_approval_claim = latest_approval_claim
    def set_latest_approval_claim_onb(self, latest_approval_claim_onb):
        self.latest_approval_claim_onb = latest_approval_claim_onb
    def set_team(self, team):
        self.team = team
    def set_sub_team(self, sub_team):
        self.sub_team = sub_team
    def set_data(self, data):
        self.data = data
    def set_ref_type(self, ref_type):
        self.ref_type = ref_type
    def set_history_data(self, history_data):
        self.history_data = history_data
    def set_action(self, action):
        self.action = action
    def set_created_by(self, created_by):
        self.created_by = created_by
    def set_entity_id(self, entity_id):
        self.entity_id = entity_id

    def get_id(self):
        return self.id
    def get_requestno(self):
        return self.requestno
    def get_requestdate(self):
        return self.requestdate
    def get_empgid(self):
        return self.empgid
    def get_empdesignation(self):
        return self.empdesignation
    def get_empgrade(self):
        return self.empgrade
    def get_empbranchgid(self):
        return self.empbranchgid
    def get_stategid(self):
        return self.stategid
    def get_reason(self):
        return self.reason
    def get_reasonname(self):
        return self.reasonname
    def get_permittedby(self):
        return self.permittedby
    def get_startdate(self):
        return self.startdate
    def get_enddate(self):
        return self.enddate
    def get_durationdays(self):
        return self.durationdays
    def get_eligiblemodeoftravel(self):
        return self.eligiblemodeoftravel
    def get_ordernoremarks(self):
        return self.ordernoremarks
    def get_onbehalfof(self):
        return self.onbehalfof
    def get_status(self):
        return self.status
    def get_code(self):
        return self.code
    def get_name(self):
        return self.name
    def get_startingpoint(self):
        return self.startingpoint
    def get_placeofvisit(self):
        return self.placeofvisit
    def get_purposeofvisit(self):
        return self.purposeofvisit
    def get_detail(self):
        return self.detail
    def get_approvedby(self):
        return self.approvedby
    def get_approveddate(self):
        return self.approveddate
    def get_apptype(self):
        return self.apptype
    def get_applevel(self):
        return self.applevel
    def get_appcomment(self):
        return self.appcomment
    def get_approve(self):
        return self.approve
    def get_tourid(self):
        return self.tourid
    def set_opening_balance(self,opening_balance):
        self.opening_balance=opening_balance
    def set_quantum_of_funds(self,quantum_of_funds):
        self.quantum_of_funds=quantum_of_funds
    def set_week_end_travel(self,week_end_travel):
        self.week_end_travel=week_end_travel

class Chatbox_response:
    id =None
    request = None
    maker_id = None
    ref_type = None
    approver_id = None
    comment = None
    created_date=None
    updated_date=None
    approved_by=None
    is_maker=None
    employee_name=None
    code=None
    unread_message=0
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


    def set_id(self, id):
        self.travel_id = id
    def set_chatid(self, chatid):
        self.chatid = chatid
    def set_employee_name(self, name):
        self.employee_name = name
    def set_employee_code(self, code):
        self.code = code


    def set_request(self, request):
        self.request = request

    def set_maker_id(self, maker_id):
        self.maker_id = maker_id

    def set_ref_type(self, ref_type):
        self.ref_type = ref_type

    def set_approver_id(self, approver_id):
        self.approver_id = approver_id

    def set_approveredby_id(self, approveredby_id):
        self.employee_id = approveredby_id

    def set_comment(self, comment):
        self.comment = comment

    def set_type(self, type):
        self.type = type
    def set_unread_message(self,unread_message):
        self.unread_message = unread_message
    def set_tour_status(self,tour_status):
        self.tour_status = tour_status
    def set_is_maker(self, ismaker):
        self.ismaker = ismaker
    def set_status(self, status):
        self.status = status
    def set_created_date(self,created_date):
        if created_date is None:
            self.created_date=created_date
        else:
            self.created_date=created_date.strftime("%d-%b-%Y %H:%M:%S")
            self.created_date_ms =round(created_date.timestamp() * 1000)
    def set_updated_date(self,updated_date):
        if updated_date is None:
            self.updated_date=updated_date
        else:
            self.updated_date=updated_date.strftime("%d-%b-%Y")
            self.updated_date_ms =round(updated_date.timestamp() * 1000)
class Doc_response:
    id =None
    code = None
    file_type = None
    file_name = None
    description = None
    created_date = None
    updated_date = None
    approved_by = None
    week_end=None
    weekend_day=None
    file_id=None
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def set_id(self, id):
        self.id = id
    def set_file_type(self,file_type):
        self.file_type=file_type
    def set_file_id(self,file_id):
        self.file_id=file_id
    def set_file_name(self,file_name):
        self.file_name=file_name
    def set_description(self,description):
        self.description=description
    def set_ref_type(self, ref_type):
        self.ref_type = ref_type
    def set_maker_or_admin(self,maker_or_admin):
        self.maker_or_admin=maker_or_admin
    def set_detail(self,detail):
        self.detail=detail
    def set_requirement_type(self,requirement_type):
        self.requirement_type=requirement_type
    def set_requirement(self,requirement):
        self.requirement=requirement
    def set_created_date(self,created_date):
        if created_date is None:
            self.created_date=created_date
        else:
            self.created_date=created_date.strftime("%d-%b-%Y")
            self.created_date_ms =round(created_date.timestamp() * 1000)
    def set_updated_date(self,updated_date):
        if updated_date is None:
            self.updated_date=updated_date
        else:
            self.updated_date=updated_date.strftime("%d-%b-%Y")
            self.updated_date_ms =round(updated_date.timestamp() * 1000)
    def set_weekend_date(self,week_end):
        if week_end is None:
            self.week_end=week_end
        else:
            self.week_end=week_end.strftime("%d-%b-%Y")
    def set_weekend_day(self,weekend_day):
        self.weekend_day=weekend_day
    def set_weekend_date_ms(self,weekend_day_ms):
        self.weekend_day_ms=weekend_day_ms
    def set_holdiay(self,holiday):
        if holiday is None:
            self.holiday=holiday
        else:
            self.holiday=holiday.strftime("%d-%b-%Y")
    def set_holdiay_name(self,holiday_name):
        self.holiday_name=holiday_name

class Travel_count:
    count=None
    employee=None
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def set_count(self, count):
        self.travel_count = count
    def set_employee(self, employee_id):
        self.employee_id = employee_id
    def set_claim_count(self, claim_count):
        self.total_claimreq_count = claim_count
    def set_claimed_amount(self, claimed_amount):
        self.total_claimed_amount = claimed_amount
    def set_approved_amount(self, approved_amount):
        self.total_approved_amount = approved_amount
