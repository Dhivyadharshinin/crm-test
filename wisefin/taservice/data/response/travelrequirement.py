import json
class Cab_response:
    id = 1
    from_time = None
    to_time = None
    ref_no = None
    ref_type = None
    booking_status = None
    travel_detail =None
    requirement=None
    created_by=None
    created_date=None
    updated_by=None
    updated_date=None
    status=None
    entity_id=None


    employee_id=None

    ticket_amount = None
    ticket_amount_personal = None
    vendor_name = None
    ticket_no = None
    class_of_travel = None
    cab_number = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_tour_id(self, tour_id):
        self.tour_id = tour_id
    def set_client(self, client):
        self.client =client
    def set_empcode(self, empcode):
        self.empcode =empcode
    def set_empname(self, empname):
        self.empname =empname
    def set_from_place(self,from_place):
        self.from_place = from_place
    def set_to_place(self,to_place):
        self.to_place = to_place
    def set_entity_id(self,entity_id):
        self.entity_id=entity_id
    def set_booking_needed(self,booking_needed):
        self.booking_needed=booking_needed
    def set_approvedby(self,approved):
        self.approver=approved
    def set_pnr_no(self,pnr_no):
        self.pnr_no=pnr_no
    def set_tour_status(self,tour_status):
        self.tour_status=tour_status

    def set_from_time(self, from_time):
        if from_time is None:
            self.from_time = from_time
        else:
            self.from_time = from_time.strftime("%Y-%b-%d %H:%M:%S")
            self.from_time_ms =round(from_time.timestamp() * 1000)
    def set_from_date(self, from_date):
        if from_date is None:
            self.from_date = from_date
        else:
            self.from_date = from_date.strftime("%Y-%b-%d")
            # self.from_time_ms =round(from_time.timestamp() * 1000)
    def set_from_date_xl(self, from_date):
        if from_date is None:
            self.from_date_xl = from_date
        else:
            self.from_date_xl = from_date.strftime("%d-%b-%Y")
            # self.from_time_ms =round(from_time.timestamp() * 1000)
    def set_refund_date(self, refund_date):
        if refund_date is None:
            self.refund_date = refund_date
        else:
            self.refund_date = refund_date.strftime("%Y-%b-%d %H:%M:%S")
    def set_fromtime(self, from_time):
        if from_time is None:
            self.fromtime = from_time
        else:
            self.fromtime = from_time.strftime("%H:%M:%S")
    def set_to_time(self, to_time):
        if to_time is None:
            self.to_time = to_time
        else:
            self.to_time = to_time.strftime("%Y-%b-%d %H:%M:%S")
            self.to_time_ms =round(to_time.timestamp() * 1000)
    def set_totime(self, to_time):
        if to_time is None:
            self.totime = to_time
        else:
            self.totime = to_time.strftime("%H:%M:%S")
    def set_ref_no(self, ref_no):
        self.ref_no = ref_no
    def set_refund_amount(self, refund_amount):
        self.refund_amount = refund_amount
    def set_costper_head(self, costper_head):
        self.costper_head = costper_head
    def set_fare_quoted(self, fare_quoted):
        self.fare_quoted = fare_quoted
    def set_difference_in_amount(self, difference_in_amount):
        self.difference_inamount = difference_in_amount
    def set_issuance_type(self, issuance_type):
        self.issuance_type = issuance_type
    def set_loss_of_cancelation(self, loss_of_cancelation):
        self.loss_of_cancelation = loss_of_cancelation
    def set_cancelled_date(self, cancelled_date):
        if cancelled_date is None:
            self.cancelled_date = cancelled_date
        else:
            self.cancelled_date= cancelled_date.strftime("%Y-%b-%d %H:%M:%S")
    def set_website(self, website):
        self.website = website

    def set_ref_type(self, ref_type):
        self.ref_type = ref_type
    def set_file_detail(self, file_detail):
        self.file_detail = file_detail
    def set_cancel_reason(self, cancel_reason):
        self.cancel_reason = cancel_reason
    def set_weekend_travel(self, weekend_travel):
        self.weekend_travel = weekend_travel

    def set_booking_status(self, booking_status):
        self.booking_status = booking_status

    def set_travel_detail(self, travel_detail):
        self.travel_detail = travel_detail
    def set_purpose_ofvisit(self, purpose_ofvisit):
        self.purpose_ofvisit = purpose_ofvisit
    def set_requirement(self, requirment):
        self.requirement = requirment

    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_created_date(self, created_date):
        if created_date is None:
            self.created_date = created_date
        else:
            self.created_date = created_date.strftime("%Y-%b-%d %H:%M:%S")
            self.created_date_ms =round(created_date.timestamp() * 1000)
    def set_created_date_xl(self, created_date):
        if created_date is None:
            self.created_date_xl = created_date
        else:
            self.created_date_xl = created_date.strftime("%d-%b-%Y")
            self.created_date_ms =round(created_date.timestamp() * 1000)
    def set_created_time_xl(self, created_date):
        if created_date is None:
            self.created_time_xl = created_date
        else:
            self.created_time_xl = created_date.strftime("%H:%M:%S")
            self.created_time_ms =round(created_date.timestamp() * 1000)
    def set_request_date(self, request_date):
        if request_date is None:
            self.request_date = request_date
        else:
            self.request_date= request_date.strftime("%Y-%b-%d %H:%M:%S")
            self.request_date_ms =round(request_date.timestamp() * 1000)

    def set_request_date_xl(self, request_date):
        if request_date is None:
            self.request_date_xl = request_date
        else:
            self.request_date_xl= request_date.strftime("%d-%b-%Y %H:%M:%S")
            self.request_date_ms =round(request_date.timestamp() * 1000)

    def set_created_date_time(self, created_date):
        # created_date = created_date.strftime("%Y-%b-%d %H:%M:%S")
        self.created_date_time=created_date.timestamp()*1000

    def set_updated_by(self, updated_by):
        self.updated_by = updated_by
    def set_booked_by(self, booked_by):
        self.booked_by = booked_by

    def set_updated_date(self, updated_date):
        if updated_date is None:
            self.updated_date = updated_date
        else:
            self.updated_date = updated_date.strftime("%Y-%b-%d %H:%M:%S")
            self.updated_date_ms =round(updated_date.timestamp() * 1000)

    def set_status(self, status):
        self.status = status
    def set_team_name(self, team_name):
        self.team_name = team_name
    def set_domestic(self,domestic):
        self.domestic =domestic
    def set_comments(self, comments):
        self.comments = comments
    def set_cab_type(self, cab_type):
        self.cab_type = cab_type
    def set_travel_type_cab(self, travel_type_cab):
        if travel_type_cab==0:
            self.travel_type_cab = None
        self.travel_type_cab = travel_type_cab
    def set_travel_type_cab_value(self, travel_type_cab_value):
        self.travel_type_cab_value = travel_type_cab_value

    def set_ticket_amount(self,ticket_amount):
        if ticket_amount is None:
            self.ticket_amount = None
        else:
            self.ticket_amount=round(ticket_amount,2)
    def set_ticket_amount_personal(self,ticket_amount_personal):
        if ticket_amount_personal is None:
            self.ticket_amount_personal = None
        else:
            self.ticket_amount_personal = round(ticket_amount_personal,2)

    def set_cancel_data(self,cancel_data):
        self.cancel_data= cancel_data

    def set_vendor_name(self,vendor_name):
        self.vendor_name=vendor_name
    def set_ticket_no(self,ticket_no):
        self.ticket_no=ticket_no
    def set_class_of_travel(self,class_of_travel):
        self.class_of_travel=class_of_travel
    def set_cab_number(self,cab_number):
        self.cab_number=cab_number
    def set_difference_indays(self,set_difference_days):
        self.difference_indays=set_difference_days
    def set_personal_official(self,official):
        self.official=official

    def set_utilised_status(self,utilised_status):
        self.utilised_status=utilised_status
    def set_noshow_reason(self,noshow_reason):
        self.noshow_reason=noshow_reason
    def set_admin_paid(self,admin_paid):
        self.admin_paid=admin_paid

    def set_class_of_stay(self, class_of_stay):
        self.class_of_stay = class_of_stay

    def set_invoice_amount(self, invoice_amount):
        self.invoice_amount = invoice_amount

    def set_PNR(self, PNR):
        self.PNR = PNR

    def set_cost_per_head(self, cost_per_head):
        self.cost_per_head = cost_per_head

    def set_booking_date(self, booking_date):
        self.booking_date = booking_date.strftime("%Y-%b-%d %H:%M:%S")
        self.booking_date_ms = round(booking_date.timestamp() * 1000)
    def set_room_number(self, room_number):
        self.room_number = room_number


class Bus_response:
    id = 1
    from_time = None
    to_time = None
    ref_no = None
    ref_type = None
    booking_status = None
    travel_detail =None
    requirement=None
    created_by=None
    created_date=None
    updated_by=None
    updated_date=None
    status=None
    entity_id=None




    employee_id=None
    ticket_amount = None
    ticket_amount_personal=None

    vendor_name = None
    ticket_no = None
    class_of_travel = None
    bus_number = None
    seat_number = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_from_place(self,from_place):
        self.from_place = from_place
    def set_to_place(self,to_place):
        self.to_place = to_place
    def set_entity_id(self,entity_id):
        self.entity_id=entity_id

    def set_from_time(self, from_time):
        if from_time is None:
            self.from_time = from_time
        else:
            self.from_time = from_time.strftime("%Y-%b-%d %H:%M:%S")
            self.from_time_ms =round(from_time.timestamp() * 1000)
    def set_refund_date(self, refund_date):
        if refund_date is None:
            self.refund_date = refund_date
        else:
            self.refund_date = refund_date.strftime("%Y-%b-%d %H:%M:%S")


    def set_fromtime(self, from_time):
        if from_time is None:
            self.fromtime = from_time
        else:
            self.fromtime = from_time.strftime("%H:%M:%S")


    def set_booking_needed(self,booking_needed):
        self.booking_needed=booking_needed
    def set_pnr_no(self,pnr_no):
        self.pnr_no=pnr_no
    def set_refund_amount(self,refund_amount):
        self.refund_amount=refund_amount

    def set_to_time(self, to_time):
        if to_time is None:
            self.to_time = to_time
        else:
            self.to_time = to_time.strftime("%Y-%b-%d %H:%M:%S")
            self.to_time_ms =round(to_time.timestamp() * 1000)
    def set_totime(self, to_time):
        if to_time is None:
            self.totime = to_time
        else:
            self.totime = to_time.strftime("%H:%M:%S")

    def set_ref_no(self,ref_no):
        self.ref_no = ref_no

    def set_ref_type(self,ref_type):
        self.ref_type = ref_type
    def set_cancel_reason(self,cancel_reason):
        self.cancel_reason =cancel_reason
    def set_weekend_travel(self,weekend_travel):
        self.weekend_travel = weekend_travel
    def set_booking_status(self,booking_status):
        self.booking_status=booking_status

    def set_travel_detail(self, travel_detail):
        self.travel_detail = travel_detail
    def set_tour_id(self,tour_id):
        self.tour_id = tour_id

    def set_requirement(self,requirment):
        self.requirement= requirment

    def set_created_by(self,created_by):
        self.created_by = created_by

    def set_created_date(self, created_date):
        if created_date is None:
            self.created_date = created_date
        else:
            self.created_date = created_date.strftime("%Y-%b-%d %H:%M:%S")
            self.created_date_ms =round(created_date.timestamp() * 1000)

    def set_created_date_xl(self, created_date):
        if created_date is None:
            self.created_date_xl = created_date
        else:
            self.created_date_xl = created_date.strftime("%d-%b-%Y")
            self.created_date_ms =round(created_date.timestamp() * 1000)

    def set_created_time_xl(self, created_date):
        if created_date is None:
            self.created_time_xl = created_date
        else:
            self.created_time_xl = created_date.strftime("%H:%M:%S")
            self.created_time_ms =round(created_date.timestamp() * 1000)

    def set_created_date_time(self, created_date):
        # created_date = created_date.strftime("%Y-%b-%d %H:%M:%S")
        self.created_date_time=created_date.timestamp()*1000
    def set_booked_by(self, booked_by):
        self.booked_by = booked_by

    def set_updated_by(self,updated_by):
        self.updated_by = updated_by
    def set_empcode(self,empcode):
        self.empcode =empcode
    def set_empname(self,empname):
        self.empname = empname
    def set_team_name(self,team_name):
        self.team_name = team_name
    def set_domestic(self,domestic):
        self.domestic = domestic

    def set_updated_date(self, updated_date):
        if updated_date is None:
            self.updated_date = updated_date
        else:
            self.updated_date = updated_date.strftime("%Y-%b-%d %H:%M:%S")
            self.updated_date_ms =round(updated_date.timestamp() * 1000)

    def set_status(self,status):
        self.status=status
    def set_client(self,client):
        self.client=client
    def set_comments(self, comments):
        self.comments = comments
    def set_file_detail(self, file_detail):
        self.file_detail = file_detail
    def set_approvedby(self, approved):
        self.approver= approved

    def set_ticket_amount(self,ticket_amount):
        if ticket_amount is None:
            self.ticket_amount = None
        else:
            self.ticket_amount = round(ticket_amount, 2)
    def set_ticket_amount_personal(self,ticket_amount_personal):
        if ticket_amount_personal is None:
            self.ticket_amount_personal = None
        else:
            self.ticket_amount_personal = round(ticket_amount_personal, 2)

    def set_cancel_data(self,cancel_data):
        self.cancel_data = cancel_data
    def set_admin_paid(self,admin_paid):
        self.admin_paid = admin_paid

    def set_vendor_name(self,vendor_name):
        self.vendor_name = vendor_name
    def set_ticket_no(self,ticket_no):
        self.ticket_no = ticket_no
    def set_class_of_travel(self,class_of_travel):
        self.class_of_travel =class_of_travel
    def set_costper_head(self,costper_head):
        self.costper_head =costper_head
    def set_fare_quoted(self,fare_quoted):
        self.fare_quoted =fare_quoted
    def set_difference_in_amount(self,difference_in_amount):
        self.difference_inamount =difference_in_amount
    def set_issuance_type(self,issuance_type):
        self.issuance_type =issuance_type
    def set_website(self,website):
        self.website =website
    def set_loss_of_cancelation(self,loss_of_cancelation):
        self.loss_of_cancelation =loss_of_cancelation

    def set_cancelled_date(self, cancelled_date):
        if cancelled_date is None:
            self.cancelled_date = cancelled_date
        else:
            self.cancelled_date = cancelled_date.strftime("%Y-%b-%d %H:%M:%S")
    def set_bus_number(self,bus_number):
        self.bus_number =bus_number
    def set_tour_status(self,tour_status):
        self.tour_status =tour_status
    def set_seat_number(self,seat_number):
        self.seat_number =seat_number
    def set_difference_indays(self,difference_indays):
        self.difference_indays =difference_indays
    def set_request_date(self, request_date):
        if request_date is None:
            self.request_date = request_date
        else:
            self.request_date= request_date.strftime("%Y-%b-%d %H:%M:%S")
            self.request_date_ms =round(request_date.timestamp() * 1000)
    def set_purpose_ofvisit(self, purpose_ofvisit):
        self.purpose_ofvisit = purpose_ofvisit
    def set_personal_official(self, official):
        self.official = official

    def set_utilised_status(self,utilised_status):
        self.utilised_status=utilised_status
    def set_noshow_reason(self,noshow_reason):
        self.noshow_reason=noshow_reason
    def set_class_of_stay(self, class_of_stay):
        self.class_of_stay = class_of_stay

    def set_invoice_amount(self, invoice_amount):
        self.invoice_amount = invoice_amount

    def set_PNR(self, PNR):
        self.PNR = PNR

    def set_cost_per_head(self, cost_per_head):
        self.cost_per_head = cost_per_head

    def set_booking_date(self, booking_date):
        self.booking_date = booking_date.strftime("%Y-%b-%d %H:%M:%S")
        self.booking_date_ms = round(booking_date.timestamp() * 1000)
    def set_room_number(self, room_number):
        self.room_number = room_number

class Air_response:
    id = 1
    from_time = None
    to_time = None
    ref_no = None
    ref_type = None
    booking_status = None
    travel_detail =None
    requirement=None
    created_by=None
    created_date=None
    updated_by=None
    updated_date=None
    status=None
    boarding_no=None
    entity_id=None
    tour_id=None
    employee_id=None
    employee_code=None
    vendor_name = None
    ticket_no = None
    class_of_travel = None
    flight_number = None
    seat_number = None




    employee_name=None

    ticket_amount = None
    ticket_amount_personal=None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_from_place(self,from_place):
        self.from_place = from_place
    def set_to_place(self,to_place):
        self.to_place = to_place
    def set_entity_id(self,entity_id):
        self.entity_id=entity_id
    def set_refund_amount(self,refund_amount):
        self.refund_amount=refund_amount
    def set_approvedby(self,approver):
        self.approver=approver
    def set_booking_detailid(self,booking_detailid):
        self.booking_detailid=booking_detailid

    def set_from_time(self, from_time):
        if from_time is None:
            self.from_time = from_time
        else:
            self.from_time = from_time.strftime("%Y-%b-%d %H:%M:%S")
            self.from_time_ms =round(from_time.timestamp() * 1000)
    def set_from_time_xl(self, from_time):
        if from_time is None:
            self.fromtime_xl = from_time
        else:
            self.fromtime_xl = from_time.strftime("%d-%b-%Y %H:%M:%S")
            self.from_time_ms =round(from_time.timestamp() * 1000)
    def set_refund_date(self, refund_date):
        if refund_date is None:
            self.refund_date =refund_date
        else:
            self.refund_date = refund_date.strftime("%Y-%b-%d %H:%M:%S")

    def set_refund_date_xl(self, refund_date):
        if refund_date is None:
            self.refund_date_xl =refund_date
        else:
            self.refund_date_xl = refund_date.strftime("%d-%b-%Y %H:%M:%S")


    def set_fromtime(self, from_time):
        if from_time is None:
            self.fromtime = from_time
        else:
            self.fromtime = from_time.strftime("%H:%M:%S")


    def set_to_time(self, to_time):
        if to_time is None:
            self.to_time = to_time
        else:
            self.to_time = to_time.strftime("%Y-%b-%d %H:%M:%S")
            self.to_time_ms =round(to_time.timestamp() * 1000)
    def set_totime(self, to_time):
        if to_time is None:
            self.totime = to_time
        else:
            self.totime = to_time.strftime("%H:%M:%S")



    def set_boarding_no(self,boarding_no):
        self.boarding_no=boarding_no
    def set_domestic(self,domestic):
        self.domestic=domestic

    def set_ref_no(self, ref_no):
        self.ref_no = ref_no
    def set_file_detail(self, file_detail):
        self.file_detail = file_detail

    def set_ref_type(self, ref_type):
        self.ref_type = ref_type

    def set_booking_status(self, booking_status):
        self.booking_status = booking_status

    def set_travel_detail(self, travel_detail):
        self.travel_detail = travel_detail
    def set_tour_id(self, tour_id):
        self.tour_id = tour_id
    def set_tour_status(self, tour_status):
        self.tour_status = tour_status
    def set_employee_id(self, employee_id):
        self.employee_id = employee_id
    def set_employee_code(self, employee_code):
        self.employee_code = employee_code
    def set_employee_name(self, employee_name):
        self.employee_name= employee_name

    def set_requirement(self, requirment):
        self.requirement = requirment

    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_created_date(self, created_date):
        if created_date is None:
            self.created_date = created_date
        else:
            self.created_date = created_date.strftime("%Y-%b-%d %H:%M:%S")
            self.created_date_ms =round(created_date.timestamp() * 1000)
    def set_created_date_xl(self, created_date):
        if created_date is None:
            self.created_date_xl = created_date
        else:
            self.created_date_xl = created_date.strftime("%d-%b-%Y")
            self.created_date_ms =round(created_date.timestamp() * 1000)
    def set_created_time_xl(self, created_date):
        if created_date is None:
            self.created_time_xl = created_date
        else:
            self.created_time_xl = created_date.strftime("%H:%M:%S")
            self.created_date_ms =round(created_date.timestamp() * 1000)
    def set_request_date(self, request_date):
        if request_date is None:
            self.request_date = request_date
        else:
            self.request_date= request_date.strftime("%Y-%b-%d %H:%M:%S")
            self.request_date_ms =round(request_date.timestamp() * 1000)

    def set_request_date_xl(self, request_date):
        if request_date is None:
            self.request_date_xl = request_date
        else:
            self.request_date_xl= request_date.strftime("%d-%b-%Y %H:%M:%S")
            self.request_date_ms =round(request_date.timestamp() * 1000)

    def set_created_date_time(self, created_date):
        # created_date = created_date.strftime("%Y-%b-%d %H:%M:%S")
        self.created_date_time=created_date.timestamp()*1000
    def set_booked_by(self, booked_by):
        self.booked_by = booked_by

    def set_updated_by(self, updated_by):
        self.updated_by = updated_by
    def set_costper_head(self, costper_head):
        self.costper_head = costper_head

    def set_fare_quoted(self, fare_quoted):
        self.fare_quoted = fare_quoted

    def set_difference_in_amount(self, difference_inamount):
        self.difference_inamount = difference_inamount
    def set_loss_of_cancelation(self, loss_of_cancelation):
        self.loss_of_cancelation = loss_of_cancelation
    def set_cancelled_date(self, cancelled_date):
        if cancelled_date is None:
            self.cancelled_date = cancelled_date
        else:
            self.cancelled_date= cancelled_date.strftime("%Y-%b-%d %H:%M:%S")
    def set_cancelled_date_xl(self, cancelled_date):
        if cancelled_date is None:
            self.cancelled_date_xl = cancelled_date
        else:
            self.cancelled_date_xl= cancelled_date.strftime("%d-%b-%Y %H:%M:%S")
    def set_issuance_type(self, issuance_type):
        self.issuance_type = issuance_type

    def set_website(self, website):
        self.website = website

    def set_updated_date(self, updated_date):
        if updated_date is None:
            self.updated_date = updated_date
        else:
            self.updated_date = updated_date.strftime("%Y-%b-%d %H:%M:%S")
            self.updated_date_ms =round(updated_date.timestamp() * 1000)

    def set_status(self, status):
        self.status = status
    def set_client(self,client):
        self.client =client
    def set_empcode(self, empcode):
        self.empcode = empcode
    def set_empname(self, empname):
        self.empname = empname

    def set_booking_needed(self,booking_needed):
        self.booking_needed=booking_needed
    def set_pnr_no(self,pnr_no):
        self.pnr_no=pnr_no
    def set_comments(self, comments):
        self.comments = comments
    def set_personal_official(self, official):
        self.official = official

    def set_ticket_amount(self,ticket_amount):
        if ticket_amount is None:
            self.ticket_amount = None
        else:
            self.ticket_amount = round(ticket_amount, 2)
    def set_ticket_amount_personal(self,ticket_amount_personal):
        if ticket_amount_personal is None:
            self.ticket_amount_personal = None
        else:
            self.ticket_amount_personal = round(ticket_amount_personal, 2)
    def set_cancel_data(self,cancel_data):
        self.cancel_data = cancel_data
    def set_vendor_name(self,vendor_name):
        self.vendor_name=vendor_name
    def set_purpose_ofvisit(self, purpose_ofvisit):
        self.purpose_ofvisit = purpose_ofvisit
    def set_ticket_no(self,ticket_no):
        self.ticket_no=ticket_no
    def set_class_of_travel(self,class_of_travel):
        self.class_of_travel=class_of_travel
    def set_flight_number(self,flight_number):
        self.flight_number=flight_number
    def set_cancel_reason(self,cancel_reason):
        self.cancel_reason=cancel_reason
    def set_team_name(self,team_name):
        self.team_name=team_name
    def set_weekend_travel(self,weekend_travel):
        self.weekend_travel=weekend_travel
    def set_seat_number(self,seat_number):
        self.seat_number=seat_number
    def set_difference_indays(self,difference_indays):
        self.difference_indays=difference_indays

    def set_utilised_status(self,utilised_status):
        self.utilised_status=utilised_status
    def set_noshow_reason(self,noshow_reason):
        self.noshow_reason=noshow_reason
    def set_admin_paid(self,admin_paid):
        self.admin_paid=admin_paid

    def set_class_of_stay(self, class_of_stay):
        self.class_of_stay = class_of_stay

    def set_invoice_amount(self, invoice_amount):
        self.invoice_amount = invoice_amount

    def set_PNR(self, PNR):
        self.PNR = PNR

    def set_cost_per_head(self, cost_per_head):
        self.cost_per_head = cost_per_head

    def set_booking_date(self, booking_date):
        self.booking_date = booking_date.strftime("%Y-%b-%d %H:%M:%S")
        self.booking_date_ms = round(booking_date.timestamp() * 1000)

class Train_response:
    id = 1
    from_time = None
    to_time = None
    ref_no = None
    ref_type = None
    booking_status = None
    travel_detail =None
    requirement=None
    created_by=None
    created_date=None
    updated_by=None
    updated_date=None
    status=None
    pnr_no=None
    employee_id=None
    entity_id=None
    ticket_amount = None
    ticket_amount_personal = None

    vendor_name = None
    ticket_no = None
    class_of_travel = None
    train_number = None
    seat_number = None



    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_entity_id(self,entity_id):
        self.entity_id=entity_id

    def set_fromtime(self, from_time):
        if from_time is None:
            self.fromtime = from_time
        else:
            self.fromtime = from_time.strftime("%H:%M:%S")

    def set_from_time(self, from_time):
        if from_time is None:
            self.from_time = from_time
        else:
            self.from_time = from_time.strftime("%Y-%b-%d %H:%M:%S")
            self.from_time_ms =round(from_time.timestamp() * 1000)
    def set_refund_date(self, refund_date):
        if refund_date is None:
            self.refund_date = refund_date
        else:
            self.refund_date = refund_date.strftime("%Y-%b-%d %H:%M:%S")

    def set_to_time(self, to_time):
        if to_time is None:
            self.to_time = to_time
        else:
            self.to_time = to_time.strftime("%Y-%b-%d %H:%M:%S")
            self.to_time_ms =round(to_time.timestamp() * 1000)
    def set_totime(self, to_time):
        if to_time is None:
            self.totime = to_time
        else:
            self.totime = to_time.strftime("%H:%M:%S")


    def set_ref_no(self,ref_no):
        self.ref_no = ref_no
    def set_file_detail(self,file_detail):
        self.file_detail = file_detail
    def set_approvedby(self,approved):
        self.approver = approved
    def set_refund_amount(self,refund_amount):
        self.refund_amount= refund_amount

    def set_ref_type(self,ref_type):
        self.ref_type = ref_type
    def set_from_place(self,from_place):
        self.from_place = from_place
    def set_to_place(self,to_place):
        self.to_place = to_place
    def set_pnr_no(self,pnr_no):
        self.pnr_no=pnr_no
    def set_booking_status(self,booking_status):
        self.booking_status=booking_status
    def set_cancel_reason(self,cancel_reason):
        self.cancel_reason=cancel_reason
    def set_weekend_travel(self,weekend_travel):
        self.weekend_travel=weekend_travel
    def set_travel_detail(self,travel_detail):
        self.travel_detail=travel_detail
    def set_tour_id(self,travel_detail):
        self.tour_id=travel_detail

    def set_requirement(self,requirment):
        self.requirement= requirment

    def set_created_by(self,created_by):
        self.created_by = created_by
    def set_costper_head(self,costper_head):
        self.costper_head = costper_head
    def set_tour_status(self,tour_status):
        self.tour_status = tour_status
    def set_fare_quoted(self,fare_quoted):
        self.fare_quoted = fare_quoted
    def set_difference_in_amount(self,difference_inamount):
        self.difference_inamount = difference_inamount
    def set_issuance_type(self,issuance_type):
        self.issuance_type = issuance_type
    def set_website(self,website):
        self.website = website
    def set_loss_of_cancelation(self,loss_of_cancelation):
        self.loss_of_cancelation = loss_of_cancelation
    def set_cancelled_date(self, cancelled_date):
        if cancelled_date is None:
            self.cancelled_date = cancelled_date
        else:
            self.cancelled_date= cancelled_date.strftime("%Y-%b-%d %H:%M:%S")
    def set_created_date(self, created_date):
        if created_date is None:
            self.created_date = created_date
        else:
            self.created_date = created_date.strftime("%Y-%b-%d %H:%M:%S")
            self.created_date_ms =round(created_date.timestamp() * 1000)

    def set_created_date_xl(self, created_date):
        if created_date is None:
            self.created_date_xl = created_date
        else:
            self.created_date_xl = created_date.strftime("%d-%b-%Y")
            self.created_date_ms =round(created_date.timestamp() * 1000)

    def set_created_time_xl(self, created_date):
        if created_date is None:
            self.created_time_xl = created_date
        else:
            self.created_time_xl = created_date.strftime("%H:%M:%S")
            self.created_time_ms =round(created_date.timestamp() * 1000)

    def set_created_date_time(self, created_date):
        # created_date = created_date.strftime("%Y-%b-%d %H:%M:%S")
        self.created_date_time=created_date.timestamp()*1000
    def set_booked_by(self, booked_by):
        self.booked_by = booked_by

    def set_updated_by(self,updated_by):
        self.updated_by = updated_by
    def set_empcode(self,empcode):
        self.empcode =empcode
    def set_empname(self,empname):
        self.empname = empname
    def set_domestic(self,domestic):
        self.domestic =domestic

    def set_updated_date(self, updated_date):
        if updated_date is None:
            self.updated_date = updated_date
        else:
            self.updated_date = updated_date.strftime("%Y-%b-%d %H:%M:%S")
            self.updated_date_ms =round(updated_date.timestamp() * 1000)

    def set_status(self,status):
        self.status=status

    def set_booking_needed(self,booking_needed):
        self.booking_needed=booking_needed
    def set_comments(self, comments):
        self.comments = comments

    def set_ticket_amount(self,ticket_amount):
        if ticket_amount is None:
            self.ticket_amount = None
        else:
            self.ticket_amount = round(ticket_amount, 2)
    def set_ticket_amount_personal(self,ticket_amount_personal):
        if ticket_amount_personal is None:
            self.ticket_amount_personal = None
        else:
            self.ticket_amount_personal = round(ticket_amount_personal, 2)
    def set_team_name(self,team_name):
        self.team_name = team_name

    def set_cancel_data(self,cancel_data):
        self.cancel_data= cancel_data
    def set_admin_paid(self,admin_paid):
        self.admin_paid= admin_paid

    def set_vendor_name(self,vendor_name):
        self.vendor_name=vendor_name
    def set_client(self,client):
        self.client=client
    def set_ticket_no(self,ticket_no):
        self.ticket_no=ticket_no
    def set_class_of_travel(self,class_of_travel):
        self.class_of_travel=class_of_travel
    def set_train_number(self,train_number):
        self.train_number=train_number
    def set_seat_number(self,seat_number):
        self.seat_number=seat_number
    def set_difference_indays(self,difference_indays):
        self.difference_indays=difference_indays
    def set_request_date(self, request_date):
        if request_date is None:
            self.request_date = request_date
        else:
            self.request_date= request_date.strftime("%Y-%b-%d %H:%M:%S")
            self.request_date_ms =round(request_date.timestamp() * 1000)
    def set_purpose_ofvisit(self, purpose_ofvisit):
        self.purpose_ofvisit = purpose_ofvisit
    def set_personal_official(self, official):
        self.official = official

    def set_utilised_status(self,utilised_status):
        self.utilised_status=utilised_status
    def set_noshow_reason(self,noshow_reason):
        self.noshow_reason=noshow_reason

    def set_class_of_stay(self,class_of_stay):
        self.class_of_stay=class_of_stay
    def set_invoice_amount(self,invoice_amount):
        self.invoice_amount=invoice_amount
    def set_PNR(self,PNR):
        self.PNR=PNR
    def set_cost_per_head(self,cost_per_head):
        self.cost_per_head=cost_per_head
    def set_booking_date(self,booking_date):
        self.booking_date = booking_date.strftime("%Y-%b-%d %H:%M:%S")
        self.booking_date_ms = round(booking_date.timestamp() * 1000)

class AccomodationBooking_Response:
    checkin_time=None
    checkout_time=None
    check_intime=None
    check_outtime=None
    ref_no=None
    ref_type=None
    booking_status=None
    travel_detail =None
    requirement_id =None
    status =None
    created_by =None
    created_date =None
    updated_by = None
    updated_date = None
    ticket_amount = None
    ticket_amount_personal = None
    vendor_name = None
    ticket_no = None
    class_of_stay = None
    room_number = None
    refund_date=None
    refund_amount=None
    from_place=None
    to_place=None
    official=None
    client=None
    empname=None
    empcode=None
    domestic=None


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_entity_id(self,entity_id):
        self.entity_id=entity_id
    def set_approvedby(self,approved):
        self.approver=approved

    def set_checkin_time(self, checkin_time):
        if checkin_time is None:
            self.checkin_time = checkin_time
        else:
            self.checkin_time = checkin_time.strftime("%Y-%b-%d %H:%M:%S")
            self.checkin_time_ms =round(checkin_time.timestamp() * 1000)
    def set_admincheckin_time(self, checkin_time):
        if checkin_time is None:
            self.from_time = checkin_time
        else:
            self.from_time = checkin_time.strftime("%Y-%b-%d %H:%M:%S")
            self.checkin_time_ms =round(checkin_time.timestamp() * 1000)
    def set_check_intime(self, checkin_time):
        if checkin_time is None:
            self.fromtime = checkin_time
        else:
            self.fromtime = checkin_time.strftime("%H:%M:%S")

    def set_checkout_time(self, checkout_time):
        if checkout_time is None:
            self.checkout_time = checkout_time
        else:
            self.checkout_time = checkout_time.strftime("%Y-%b-%d %H:%M:%S")
            self.checkout_time_ms =round(checkout_time.timestamp() * 1000)

    def set_check_intime_xl(self, checkin_time):
        if checkin_time is None:
            self.fromtime_xl = checkin_time
        else:
            self.fromtime_xl = checkin_time.strftime("%d-%b-%Y %H:%M:%S")

    def set_checkout_time_xl(self, checkout_time):
        if checkout_time is None:
            self.totime_xl = checkout_time
        else:
            self.totime_xl = checkout_time.strftime("%d-%b-%Y %H:%M:%S")
            self.checkout_time_ms =round(checkout_time.timestamp() * 1000)

    def set_admincheckout_time(self, checkout_time):
        if checkout_time is None:
            self.to_time = checkout_time
        else:
            self.to_time = checkout_time.strftime("%Y-%b-%d %H:%M:%S")
            self.checkout_time_ms =round(checkout_time.timestamp() * 1000)

    def set_check_outtime(self, checkout_time):
        if checkout_time is None:
            self.totime = checkout_time
        else:
            self.totime = checkout_time.strftime("%H:%M:%S")

    def set_ref_no(self,ref_no):
        self.ref_no = ref_no
    def set_place_of_stay(self,place_of_stay):
        self.place_of_stay = place_of_stay
    def set_from_place(self,from_place):
        self.from_place = from_place
    def set_to_place(self,to_place):
        self.to_place = to_place
    def set_tour_status(self,tour_status):
        self.tour_status = tour_status

    def set_ref_type(self,ref_type):
        self.ref_type = ref_type
    def set_file_detail(self,file_detail):
        self.file_detail = file_detail

    def set_booking_status(self,booking_status):
        self.booking_status=booking_status
    def set_travel_detail(self,travel_detail):
        self.travel_detail=travel_detail
    def set_tour_id(self,tour_id):
        self.tour_id=tour_id
    def set_request_date(self, request_date):
        if request_date is None:
            self.request_date = request_date
        else:
            self.request_date= request_date.strftime("%Y-%b-%d %H:%M:%S")
            self.request_date_ms =round(request_date.timestamp() * 1000)
    def set_request_date_xl(self, request_date):
        if request_date is None:
            self.request_date_xl = request_date
        else:
            self.request_date_xl= request_date.strftime("%d-%b-%Y %H:%M:%S")
            self.request_date_ms =round(request_date.timestamp() * 1000)
    def set_purpose_ofvisit(self, purpose_ofvisit):
        self.purpose_ofvisit = purpose_ofvisit
    def set_requirement_id(self,requirment_id):
        self.requirement_id= requirment_id

    def set_created_by(self,created_by):
        self.created_by = created_by
    def set_team_name(self,team_name):
        self.team_name = team_name
    def set_personal_official(self,official):
        self.official = official

    def set_created_date(self, created_date):
        if created_date is None:
            self.created_date = created_date
        else:
            self.created_date = created_date.strftime("%Y-%b-%d %H:%M:%S")
            self.created_date_ms =round(created_date.timestamp() * 1000)
    def set_created_date_xl(self, created_date):
        if created_date is None:
            self.created_date_xl = created_date
        else:
            self.created_date_xl = created_date.strftime("%d-%b-%Y")
            self.created_date_ms =round(created_date.timestamp() * 1000)
    def set_created_time_xl(self, created_date):
        if created_date is None:
            self.created_time_xl = created_date
        else:
            self.created_time_xl = created_date.strftime("%H:%M:%S")
            self.created_date_ms =round(created_date.timestamp() * 1000)
    def set_refund_date(self, refund_date):
        if refund_date is None:
            self.refund_date = refund_date
        else:
            self.refund_date = refund_date.strftime("%Y-%b-%d %H:%M:%S")
    def set_refund_amount(self,refund_amount):
        self.refund_amount = refund_amount

    def set_created_date_time(self, created_date):
        # created_date = created_date.c("%Y-%b-%d %H:%M:%S")
        self.created_date_time=created_date.timestamp()*1000
    def set_booked_by(self, booked_by):
        self.booked_by = booked_by

    def set_updated_by(self,updated_by):
        self.updated_by = updated_by
    def set_costper_head(self,costper_head):
        self.costper_head = costper_head
    def set_fare_quoted(self,fare_quoted):
        self.fare_quoted = fare_quoted
    def set_difference_in_amount(self,difference_inamount):
        self.difference_inamount = difference_inamount
    def set_issuance_type(self,issuance_type):
        self.issuance_type = issuance_type
    def set_loss_of_cancelation(self,loss_of_cancelation):
        self.loss_of_cancelation = loss_of_cancelation
    def set_website(self,website):
        self.website = website
    def set_cancelled_date(self, cancelled_date):
        if cancelled_date is None:
            self.cancelled_date = cancelled_date
        else:
            self.cancelled_date= cancelled_date.strftime("%Y-%b-%d %H:%M:%S")

    def set_updated_date(self, updated_date):
        if updated_date is None:
            self.updated_date = updated_date
        else:
            self.updated_date = updated_date.strftime("%Y-%b-%d %H:%M:%S")
            self.updated_date_ms =round(updated_date.timestamp() * 1000)

    def set_status(self,status):
        self.status=status
    def set_utilised_status(self,utilised_status):
        self.utilised_status=utilised_status
    def set_noshow_reason(self,noshow_reason):
        self.noshow_reason=noshow_reason
    def set_client(self,client):
        self.client=client
    def set_empcode(self,empcode):
        self.empcode=empcode
    def set_empname(self,empname):
        self.empname=empname

    def set_booking_needed(self,booking_needed):
        self.booking_needed=booking_needed
    def set_pnr_no(self,pnr_no):
        self.pnr_no=pnr_no
    def set_comments(self, comments):
        self.comments = comments
    def set_costper_head(self, costper_head):
        self.costper_head = costper_head

    def set_ticket_amount(self, ticket_amount):
        if ticket_amount is None:
            self.ticket_amount = None
        else:
            self.ticket_amount = round(ticket_amount, 2)
    def set_ticket_amount_personal(self, ticket_amount_personal):
        if ticket_amount_personal is None:
            self.ticket_amount_personal = None
        else:
            self.ticket_amount_personal = round(ticket_amount_personal, 2)
    def set_cancelled_data(self, cancelled_data):
        self.cancelled_data = cancelled_data
    def set_admin_paid(self, admin_paid):
        self.admin_paid = admin_paid
    def set_domestic(self, domestic):
        self.domestic=domestic

    def set_room_number(self,room_number):
        self.room_number = room_number
    def set_cancel_reason(self,cancel_reason):
        self.cancel_reason = cancel_reason
    def set_weekend_travel(self,weekend_travel):
        self.weekend_travel = weekend_travel

    def set_classof_stay(self,class_of_stay):
        self.class_of_travel=class_of_stay

    def set_ticket_no(self,ticket_no):
        self.ticket_no=ticket_no

    def set_vendor_name(self,vendor_name):
        self.vendor_name=vendor_name
    def set_difference_indays(self,difference_indays):
        self.difference_indays=difference_indays
    def set_class_of_stay(self,class_of_stay):
        self.class_of_stay=class_of_stay
    def set_invoice_amount(self,invoice_amount):
        self.invoice_amount=invoice_amount
    def set_PNR(self,PNR):
        self.PNR=PNR
    def set_cost_per_head(self,cost_per_head):
        self.cost_per_head=cost_per_head

    def set_booking_date(self, booking_date):
        self.booking_date = booking_date.strftime("%Y-%b-%d %H:%M:%S")
        self.booking_date_ms = round(booking_date.timestamp() * 1000)


class Booking_req:
    checkin_time=None
    checkout_time=None
    ref_no=None
    ref_type=None
    booking_status=None
    travel_detail =None
    requirement_id =None
    status =None
    created_by =None
    created_date =None
    updated_by = None
    updated_date = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_tourdetail(self,tourdetail):
        self.tourdetail=tourdetail

    def set_checkin_time(self, checkin_time):
        if checkin_time is None:
            self.checkin_time = checkin_time
        else:
            self.checkin_time = checkin_time.strftime("%Y-%b-%d %H:%M:%S")
            self.checkin_time_ms =round(checkin_time.timestamp() * 1000)

    def set_checkout_time(self, checkout_time):
        if checkout_time is None:
            self.checkout_time = checkout_time
        else:
            self.checkout_time = checkout_time.strftime("%Y-%b-%d %H:%M:%S")
            self.checkout_time_ms =round(checkout_time.timestamp() * 1000)

    def set_ref_no(self,ref_no):
        self.ref_no = ref_no
    def set_place_of_stay(self,place_of_stay):
        self.place_of_stay = place_of_stay

    def set_ref_type(self,ref_type):
        self.ref_type = ref_type

    def set_booking_status(self,booking_status):
        self.booking_status=booking_status
    def set_travel_detail(self,travel_detail):
        self.travel_detail=travel_detail

    def set_requirement_id(self,requirment_id):
        self.requirement_id= requirment_id

    def set_created_by(self,created_by):
        self.created_by = created_by

    def set_created_date(self, created_date):
        if created_date is None:
            self.created_date = created_date
        else:
            self.created_date = created_date.strftime("%Y-%b-%d %H:%M:%S")
            self.created_date_ms =round(created_date.timestamp() * 1000)

    def set_created_date_time(self, created_date):
        # created_date = created_date.strftime("%Y-%b-%d %H:%M:%S")
        self.created_date_time=created_date.timestamp()*1000

    def set_updated_by(self,updated_by):
        self.updated_by = updated_by

    def set_updated_date(self, updated_date):
        if updated_date is None:
            self.updated_date = updated_date
        else:
            self.updated_date = updated_date.strftime("%Y-%b-%d %H:%M:%S")
            self.updated_date_ms =round(updated_date.timestamp() * 1000)

    def set_status(self,status):
        self.status=status

    def set_booking_needed(self,booking_needed):
        self.booking_needed=booking_needed
    def set_comments(self, comments):
        self.comments = comments
    def set_reference_id(self, reference_id):
        self.reference_id = reference_id
    def set_booking_time(self, booking_time):
        if booking_time is None:
            self.booking_time = booking_time
        else:
            self.booking_time = booking_time.strftime("%Y-%b-%d %H:%M:%S")
            self.booking_time_ms =round(booking_time.timestamp() * 1000)
    def set_ticket_amount(self, ticket_amount):
        if ticket_amount is None:
            self.ticket_amount = None
        else:
            self.ticket_amount = round(ticket_amount, 2)
    def set_ticket_amount_personal(self,ticket_amount_personal):
        if ticket_amount_personal is None:
            self.ticket_amount_personal = None
        else:
            self.ticket_amount_personal = round(ticket_amount_personal, 2)
    def set_cancel_reschedule(self, cancel_reschedule):
        self.cancel_reschedule = cancel_reschedule
    def set_cancel_reasone(self, cancel_reasone):
        self.cancel_reasone = cancel_reasone
    def set_refund_amount(self, refund_amount):
        self.refund_amount = refund_amount
    def set_refund_date(self, refund_date):
        if refund_date is None:
            self.refund_date = refund_date
        else:
            self.refund_date = refund_date.strftime("%Y-%b-%d %H:%M:%S")
            self.refund_date_ms =round(refund_date.timestamp() * 1000)
    def set_fare_difference(self, fare_difference):
        self.fare_difference = fare_difference

    def set_utilised_status(self, utilised_status):
        self.utilised_status = utilised_status

    def set_noshow_reason(self, noshow_reason):
        self.noshow_reason = noshow_reason

class All_requirement:
    accommodation=None
    cab=None
    bus=None
    train=None
    air=None
    travel_detail =None
    requirement_id =None
    status =None
    created_by =None
    created_date =None
    updated_by = None
    updated_date = None
    cancel_reschedule = None
    cancel_reason = None
    refund_amount = None
    refund_date = None
    fare_difference = None
    cancelled_date = None
    loss_of_cancelation = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_accommodation(self, accommodation):
        self.accommodation = accommodation
    def set_cab(self, cab):
        self.cab = cab
    def set_bus(self, bus):
        self.bus = bus
    def set_train(self, train):
        self.train = train
    def set_air(self, air):
        self.air = air
    def set_cancelled_data(self, cancelled_data):
        self.cancelled_data = cancelled_data
    def set_tourdetail(self,tourdetail):
        self.tourdetail=tourdetail

    def set_checkin_time(self, checkin_time):
        if checkin_time is None:
            self.checkin_time = checkin_time
        else:
            self.checkin_time = checkin_time.strftime("%Y-%b-%d %H:%M:%S")
            self.checkin_time_ms =round(checkin_time.timestamp() * 1000)

    def set_checkout_time(self, checkout_time):
        if checkout_time is None:
            self.checkout_time = checkout_time
        else:
            self.checkout_time = checkout_time.strftime("%Y-%b-%d %H:%M:%S")
            self.checkout_time_ms =round(checkout_time.timestamp() * 1000)
    def set_cancelled_date(self, cancelled_date):
        if cancelled_date is None:
            self.cancelled_date = cancelled_date
        else:
            self.cancelled_date = cancelled_date.strftime("%Y-%b-%d %H:%M:%S")
    # def set_refund_date(self, refund_date):
    #     if refund_date is None:
    #         self.refund_date = refund_date
    #     else:
    #         self.refund_date = refund_date.strftime("%Y-%b-%d %H:%M:%S")

    def set_ref_no(self,ref_no):
        self.ref_no = ref_no
    def set_place_of_stay(self,place_of_stay):
        self.place_of_stay = place_of_stay

    def set_ref_type(self,ref_type):
        self.ref_type = ref_type

    def set_booking_status(self,booking_status):
        self.booking_status=booking_status
    def set_travel_detail(self,travel_detail):
        self.travel_detail=travel_detail

    def set_requirement_id(self,requirment_id):
        self.requirement_id= requirment_id

    def set_created_by(self,created_by):
        self.created_by = created_by

    def set_created_date(self, created_date):
        if created_date is None:
            self.created_date = created_date
        else:
            self.created_date = created_date.strftime("%Y-%b-%d %H:%M:%S")
            self.created_date_ms =round(created_date.timestamp() * 1000)

    def set_created_date_time(self, created_date):
        # created_date = created_date.strftime("%Y-%b-%d %H:%M:%S")
        self.created_date_time=created_date.timestamp()*1000

    def set_updated_by(self,updated_by):
        self.updated_by = updated_by

    def set_updated_date(self, updated_date):
        if updated_date is None:
            self.updated_date = updated_date
        else:
            self.updated_date = updated_date.strftime("%Y-%b-%d %H:%M:%S")
            self.updated_date_ms =round(updated_date.timestamp() * 1000)

    def set_status(self,status):
        self.status=status

    def set_booking_needed(self,booking_needed):
        self.booking_needed=booking_needed
    def set_comments(self, comments):
        self.comments = comments
    def set_reference_id(self, reference_id):
        self.reference_id = reference_id
    def set_booking_time(self, booking_time):
        if booking_time is None:
            self.booking_time = booking_time
        else:
            self.booking_time = booking_time.strftime("%Y-%b-%d %H:%M:%S")
            self.booking_time_ms =round(booking_time.timestamp() * 1000)
    def set_ticket_amount(self, ticket_amount):
        if ticket_amount is None:
            self.ticket_amount = None
        else:
            self.ticket_amount = round(ticket_amount, 2)
    def set_ticket_amount_personal(self,ticket_amount_personal):
        if ticket_amount_personal is None:
            self.ticket_amount_personal = None
        else:
            self.ticket_amount_personal = round(ticket_amount_personal, 2)
    def set_cancel_reschedule(self, cancel_reschedule):
        self.cancel_reschedule = cancel_reschedule
    def set_cancel_reasone(self, cancel_reasone):
        self.cancel_reasone = cancel_reasone
    def set_refund_amount(self, refund_amount):
        self.refund_amount = refund_amount
    def set_refund_date(self, refund_date):
        if refund_date is None:
            self.refund_date = refund_date
        else:
            self.refund_date = refund_date.strftime("%Y-%b-%d %H:%M:%S")
            self.refund_date_ms =round(refund_date.timestamp() * 1000)
    def set_fare_difference(self, fare_difference):
        self.fare_difference = fare_difference
    def set_cancel_reason(self, cancel_reason):
        self.cancel_reason = cancel_reason
    def set_loss_of_cancelation(self, loss_of_cancelation):
        self.loss_of_cancelation= loss_of_cancelation


