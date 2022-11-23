import json

from taservice.util.ta_util import Travel_requirements


class Cab_request:
    id =None
    from_time = None
    to_time = None
    from_place = None
    to_place = None
    ref_no = None
    ref_type = None
    booking_status = None
    travel_detail = None
    requirement = None
    created_by = None
    created_date = None
    updated_by = None
    updated_date = None
    status=None
    comments=None
    detail_id=None
    booking_needed_id=Travel_requirements.cab

    employee_id=None
    requirement_id=None

    ticket_amount = 0
    ticket_amount_personal = 0
    official = 1
    vendor_name = None
    ticket_no =None
    class_of_travel =None
    cab_number = None

    checkin_time=None
    checkout_time=None
    place_of_stay=None
    cancel_reschedule=None
    cancel_reason=None
    refund_amount=None
    refund_date=None
    fare_difference=None
    cancelled_date=None
    loss_of_cancelation=None
    admin_paid=1
    PNR = None
    fare_quoted = None
    issuance_type = None
    website = None
    travel_type_cab = 0

    def __init__(self,data):
        if 'id' in data:
            self.id = data['id']
        if 'PNR' in data:
            self.PNR = data['PNR']
        if 'fare_quoted' in data:
            self.fare_quoted = data['fare_quoted']
        if 'issuance_type' in data:
            self.issuance_type = data['issuance_type']
        if 'website' in data:
            self.website = data['website']
        if 'from_place' in data:
            self.from_place = data['from_place']
        if 'to_place' in data:
            self.to_place = data['to_place']
        if 'from_time' in data:
            self.from_time = data['from_time']
        if 'to_time' in data:
            self.to_time = data['to_time']
        if 'ref_no' in data:
            self.ref_no = data['ref_no']
        if 'ref_type' in data:
            self.ref_type = data['ref_type']
        if 'booking_status' in data:
            self.booking_status = data['booking_status']
        if 'travel_detail' in data:
            self.tour = data['travel_detail']
        if 'requirement' in data:
            self.requirement = data['requirement']
        if 'created_by' in data:
            self.created_by = data['created_by']
        if 'created_date' in data:
            self.created_date = data['created_date']
        if 'updated_by' in data:
            self.updated_by = data['updated_by']
        if 'updated_date' in data:
            self.updated_date = data['updated_date']
        if 'comments' in data:
            self.comments = data['comments']
        if 'detail_id' in data:
            self.detail_id = data['detail_id']
        if 'ticket_amount' in data:
            self.ticket_amount = data['ticket_amount']
        if 'ticket_amount_personal' in data:
            self.ticket_amount_personal = data['ticket_amount_personal']
        if 'official' in data:
            self.official = data['official']
        if 'requirement_id' in data:
            self.requirement_id = data['requirement_id']
        if 'vendor_name' in data:
            self.vendor_name = data['vendor_name']
        if 'ticket_no' in data:
            self.ticket_no = data['ticket_no']
        if 'class_of_travel' in data:
            self.class_of_travel = data['class_of_travel']
        if 'cab_number' in data:
            self.cab_number = data['cab_number']
        if 'cancel_reschedule' in data:
            self.cancel_reschedule = data['cancel_reschedule']
        if 'cancel_reason' in data:
            self.cancel_reason = data['cancel_reason']
        if 'fare_difference' in data:
            self.fare_difference = data['fare_difference']
        if 'cancelled_date' in data:
            self.cancelled_date = data['cancelled_date']
        if 'loss_of_cancelation' in data:
            self.loss_of_cancelation = data['loss_of_cancelation']
        if 'refund_amount' in data:
            self.refund_amount = data['refund_amount']
        if 'refund_date' in data:
            self.refund_date = data['refund_date']
        if 'admin_paid' in data:
            self.admin_paid = data['admin_paid']
        if 'travel_type_cab' in data:
            self.travel_type_cab = data['travel_type_cab']


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_from_time(self, from_time):
        self.from_time = from_time

    def set_to_time(self, to_time):
        self.to_time = to_time

    def set_ref_no(self, ref_no):
        self.ref_no = ref_no

    def set_ref_type(self, ref_type):
        self.ref_type = ref_type

    def set_booking_status(self, booking_status):
        self.booking_status = booking_status

    def set_travel_detail(self, travel_detail):
        self.travel_detail = travel_detail

    def set_requirement(self, requirment):
        self.requirement = requirment

    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_created_date(self, created_date):
        self.created_date = created_date

    def set_updated_by(self, updated_by):
        self.updated_by = updated_by

    def set_updated_date(self, updated_date):
        self.updated_date = updated_date

    def set_employee_id(self,employee_id):
        self.employee_id=employee_id
    def set_status(self,status):
        self.status=status

    def set_ticket_amount(self,ticket_amount):
        self.ticket_amount = ticket_amount

    def get_id(self):
        return self.id

    def get_from_time(self):
        return self.from_time

    def get_to_time(self):
        return self.to_time

    def get_ref_no(self):
        return self.ref_no

    def get_ref_type(self):
        return self.ref_type
    def get_admin_paid(self):
        return self.admin_paid

    def get_booking_status(self):
        return self.booking_status
    def get_detail_id(self):
        return self.detail_id

    def get_travel_detail(self):
        return self.travel_detail

    def get_requirement(self):
        return self.requirement

    def get_created_by(self):
        return self.created_by

    def get_created_date(self):
        return self.created_date

    def get_updated_by(self):
        return self.updated_by

    def get_updated_date(self):
        return self.updated_date
    def get_status(self):
        return self.status

    def get_employee_id(self):
        return self.employee_id

    def get_from_place(self):
        return self.from_place
    def get_to_place(self):
        return self.to_place
    def get_comments(self):
        return self.comments

    def get_ticket_amount(self):
        return self.ticket_amount
    def get_requirement_id(self):
        return self.requirement_id

    def get_vendor_name(self):
        return self.vendor_name
    def get_ticket_no(self):
        return self.ticket_no
    def get_class_of_travel(self):
        return self.class_of_travel
    def get_cab_number(self):
        return self.cab_number
    def get_cancel_reschedule(self):
        return self.cancel_reschedule
    def get_cancel_reason(self):
        return self.cancel_reason
    def get_refund_date(self):
        return self.refund_date
    def get_refund_amount(self):
        return self.refund_amount
    def get_fare_difference(self):
        return self.fare_difference
    def get_cancelled_date(self):
        return self.cancelled_date
    def get_loss_of_cancelation(self):
        return self.loss_of_cancelation

class Bus_request:
    id =None
    from_time = None
    to_time = None
    from_place = None
    to_place = None
    ref_no = None
    ref_type = None
    booking_status = None
    travel_detail = None
    requirement = None
    created_by = None
    created_date = None
    updated_by = None
    updated_date = None
    status=None
    comments=None
    detail_id=None
    booking_needed_id=Travel_requirements.bus

    employee_id=None
    ticket_amount = 0
    ticket_amount_personal = 0
    official = 1
    requirement_id = None

    vendor_name = None
    ticket_no = None
    class_of_travel = None
    bus_number = None
    seat_number = None
    PNR = None
    fare_quoted = None
    issuance_type = None
    website = None

    checkin_time=None
    checkout_time=None
    place_of_stay=None
    admin_paid = 1


    def __init__(self,data):
        if 'id' in data:
            self.id = data['id']
        if 'from_place' in data:
            self.from_place = data['from_place']
        if 'PNR' in data:
            self.PNR = data['PNR']
        if 'fare_quoted' in data:
            self.fare_quoted = data['fare_quoted']
        if 'issuance_type' in data:
            self.issuance_type = data['issuance_type']
        if 'website' in data:
            self.website = data['website']
        if 'to_place' in data:
            self.to_place = data['to_place']
        if 'from_time' in data:
            self.from_time = data['from_time']
        if 'to_time' in data:
            self.to_time = data['to_time']
        if 'ref_no' in data:
            self.ref_no = data['ref_no']
        if 'ref_type' in data:
            self.ref_type = data['ref_type']
        if 'booking_status' in data:
            self.booking_status = data['booking_status']
        if 'travel_detail' in data:
            self.travel_detail = data['travel_detail']
        if 'requirement' in data:
            self.requirement = data['requirement']
        if 'created_by' in data:
            self.created_by = data['created_by']
        if 'created_date' in data:
            self.created_date = data['created_date']
        if 'updated_by' in data:
            self.updated_by = data['updated_by']
        if 'updated_date' in data:
            self.updated_date = data['updated_date']
        if 'comments' in data:
            self.comments = data['comments']
        if 'detail_id' in data:
            self.detail_id = data['detail_id']
        if 'ticket_amount' in data:
            self.ticket_amount = data['ticket_amount']
        if 'ticket_amount_personal' in data:
            self.ticket_amount_personal = data['ticket_amount_personal']
        if 'official' in data:
            self.official = data['official']
        if 'requirement_id' in data:
            self.requirement_id = data['requirement_id']
        if 'vendor_name' in data:
            self.vendor_name = data['vendor_name']
        if 'ticket_no' in data:
            self.ticket_no = data['ticket_no']
        if 'class_of_travel' in data:
            self.class_of_travel = data['class_of_travel']
        if 'bus_number' in data:
            self.bus_number = data['bus_number']
        if 'seat_number' in data:
            self.seat_number = data['seat_number']
        if 'admin_paid' in data:
            self.admin_paid = data['admin_paid']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_from_time(self, from_time):
        self.from_time = from_time

    def set_to_time(self, to_time):
        self.to_time = to_time

    def set_ref_no(self, ref_no):
        self.ref_no = ref_no

    def set_ref_type(self, ref_type):
        self.ref_type = ref_type

    def set_booking_status(self, booking_status):
        self.booking_status = booking_status

    def set_tour(self, tour):
        self.tour = tour

    def set_requirement(self, requirment):
        self.requirement = requirment

    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_created_date(self, created_date):
        self.created_date = created_date

    def set_updated_by(self, updated_by):
        self.updated_by = updated_by

    def set_updated_date(self, updated_date):
        self.updated_date = updated_date

    def set_employee_id(self,employee_id):
        self.employee_id=employee_id
    def set_status(self,status):
        self.status=status

    def set_ticket_amount(self,ticket_amount):
        self.ticket_amount = ticket_amount

    def get_id(self):
        return self.id

    def get_from_time(self):
        return self.from_time

    def get_to_time(self):
        return self.to_time

    def get_ref_no(self):
        return self.ref_no

    def get_ref_type(self):
        return self.ref_type

    def get_booking_status(self):
        return self.booking_status

    def get_travel_detail(self):
        return self.travel_detail

    def get_requirement(self):
        return self.requirement

    def get_created_by(self):
        return self.created_by
    def get_detail_id(self):
        return self.detail_id

    def get_created_date(self):
        return self.created_date

    def get_updated_by(self):
        return self.updated_by

    def get_updated_date(self):
        return self.updated_date
    def get_status(self):
        return self.status

    def get_employee_id(self):
        return self.employee_id


    def get_from_place(self):
        return self.from_place
    def get_to_place(self):
        return self.to_place
    def get_comments(self):
        return self.comments

    def get_ticket_amount(self):
        return self.ticket_amount
    def get_requirement_id(self):
        return self.requirement_id
    def get_vendor_name(self):
        return self.vendor_name
    def get_ticket_no(self):
        return self.ticket_no
    def get_class_of_travel(self):
        return self.class_of_travel
    def get_bus_number(self):
        return self.bus_number
    def get_seat_number(self):
        return self.seat_number


class Air_request:
    id =None
    from_time = None
    to_time = None
    from_place = None
    to_place = None
    ref_no = None
    ref_type = None
    booking_status = None
    travel_detail = None
    requirement = None
    created_by = None
    created_date = None
    updated_by = None
    updated_date = None
    status=None
    comments=None
    boarding_no=None
    detail_id=None
    booking_needed_id=Travel_requirements.air

    employee_id=None
    PNR = None
    fare_quoted = None
    issuance_type = None
    website = None

    ticket_amount = 0
    ticket_amount_personal = 0
    official = 1
    requirement_id = None
    vendor_name = None
    ticket_no = None
    class_of_travel = None
    flight_number = None
    seat_number = None

    checkin_time=None
    checkout_time=None
    place_of_stay=None
    admin_paid=1

    def __init__(self,data):
        if 'id' in data:
            self.id = data['id']
        if 'PNR' in data:
            self.PNR = data['PNR']
        if 'fare_quoted' in data:
            self.fare_quoted = data['fare_quoted']
        if 'issuance_type' in data:
            self.issuance_type = data['issuance_type']
        if 'website' in data:
            self.website = data['website']
        if 'from_place' in data:
            self.from_place = data['from_place']
        if 'to_place' in data:
            self.to_place = data['to_place']
        if 'from_time' in data:
            self.from_time = data['from_time']
        if 'to_time' in data:
            self.to_time = data['to_time']
        if 'ref_no' in data:
            self.ref_no = data['ref_no']
        if 'ref_type' in data:
            self.ref_type = data['ref_type']
        if 'booking_status' in data:
            self.booking_status = data['booking_status']
        if 'travel_detail' in data:
            self.travel_detail = data['travel_detail']
        if 'requirement' in data:
            self.requirement = data['requirement']
        if 'created_by' in data:
            self.created_by = data['created_by']
        if 'created_date' in data:
            self.created_date = data['created_date']
        if 'updated_by' in data:
            self.updated_by = data['updated_by']
        if 'updated_date' in data:
            self.updated_date = data['updated_date']
        if 'boarding_no' in data:
            self.boarding_no=data['boarding_no']
        if 'comments' in data:
            self.comments=data['comments']
        if 'detail_id' in data:
            self.detail_id=data['detail_id']

        if 'ticket_amount' in data:
            self.ticket_amount = data['ticket_amount']
        if 'ticket_amount_personal' in data:
            self.ticket_amount_personal = data['ticket_amount_personal']
        if 'official' in data:
            self.official = data['official']
        if 'requirement_id' in data:
            self.requirement_id = data['requirement_id']
        if 'vendor_name' in data:
            self.vendor_name = data['vendor_name']
        if 'ticket_no' in data:
            self.ticket_no = data['ticket_no']
        if 'class_of_travel' in data:
            self.class_of_travel = data['class_of_travel']
        if 'flight_number' in data:
            self.flight_number = data['flight_number']
        if 'seat_number' in data:
            self.seat_number = data['seat_number']
        if 'admin_paid' in data:
            self.admin_paid = data['admin_paid']
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_from_time(self, from_time):
        self.from_time = from_time

    def set_boarding_no(self, boarding_no):
        self.boarding_no = boarding_no

    def set_to_time(self, to_time):
        self.to_time = to_time

    def set_ref_no(self, ref_no):
        self.ref_no = ref_no

    def set_ref_type(self, ref_type):
        self.ref_type = ref_type

    def set_booking_status(self, booking_status):
        self.booking_status = booking_status

    def set_travel_detail(self, travel_detail):
        self.travel_detail = travel_detail

    def set_requirement(self, requirment):
        self.requirement = requirment

    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_created_date(self, created_date):
        self.created_date = created_date

    def set_updated_by(self, updated_by):
        self.updated_by = updated_by

    def set_updated_date(self, updated_date):
        self.updated_date = updated_date

    def set_employee_id(self,employee_id):
        self.employee_id=employee_id
    def set_status(self,status):
        self.status=status

    def set_ticket_amount(self,ticket_amount):
        self.ticket_amount = ticket_amount

    def get_id(self):
        return self.id

    def get_from_time(self):
        return self.from_time

    def get_to_time(self):
        return self.to_time

    def get_ref_no(self):
        return self.ref_no

    def get_ref_type(self):
        return self.ref_type

    def get_booking_status(self):
        return self.booking_status

    def get_travel_detail(self):
        return self.travel_detail

    def get_requirement(self):
        return self.requirement

    def get_created_by(self):
        return self.created_by

    def get_created_date(self):
        return self.created_date

    def get_updated_by(self):
        return self.updated_by

    def get_boarding_no(self):
        return self.boarding_no

    def get_updated_date(self):
        return self.updated_date
    def get_status(self):
        return self.status

    def get_employee_id(self):
        return self.employee_id


    def get_from_place(self):
        return self.from_place
    def get_comments(self):
        return self.comments
    def get_to_place(self):
        return self.to_place
    def get_detail_id(self):
        return self.detail_id

    def get_ticket_amount(self):
        return self.ticket_amount
    def get_requirement_id(self):
        return self.requirement_id
    def get_vendor_name(self):
        return self.vendor_name
    def get_ticket_no(self):
        return self.ticket_no
    def get_class_of_travel(self):
        return self.class_of_travel
    def get_flight_number(self):
        return self.flight_number
    def get_seat_number(self):
        return self.seat_number

class Train_request:

    id =None
    from_time = None
    to_time = None
    from_place = None
    to_place = None
    ref_no = None
    ref_type = None
    booking_status = None
    travel_detail = None
    requirement = None
    created_by = None
    created_date = None
    updated_by = None
    updated_date = None
    status=None
    pnr_no=None
    comments=None
    detail_id=None
    requirement_id=None
    booking_needed_id=Travel_requirements.train

    employee_id=None

    ticket_amount = 0
    ticket_amount_personal = 0
    official = 1
    vendor_name = None
    ticket_no = None
    class_of_travel = None
    train_number = None
    seat_number = None

    PNR = None
    fare_quoted = None
    issuance_type = None
    website = None
    checkin_time=None
    checkout_time=None
    place_of_stay=None
    admin_paid = 1


    def __init__(self,data):
        if 'id' in data:
            self.id = data['id']
        if 'PNR' in data:
            self.PNR = data['PNR']
        if 'fare_quoted' in data:
            self.fare_quoted = data['fare_quoted']
        if 'issuance_type' in data:
            self.issuance_type = data['issuance_type']
        if 'website' in data:
            self.website = data['website']
        if 'from_time' in data:
            self.from_time = data['from_time']
        if 'from_place' in data:
            self.from_place = data['from_place']
        if 'to_place' in data:
            self.to_place = data['to_place']
        if 'to_time' in data:
            self.to_time = data['to_time']
        if 'ref_no' in data:
            self.ref_no = data['ref_no']
        if 'ref_type' in data:
            self.ref_type = data['ref_type']
        if 'booking_status' in data:
            self.booking_status = data['booking_status']
        if 'travel_detail' in data:
            self.travel_detail = data['travel_detail']
        if 'requirement' in data:
            self.requirement = data['requirement']
        if 'created_by' in data:
            self.created_by = data['created_by']
        if 'created_date' in data:
            self.created_date = data['created_date']
        if 'updated_by' in data:
            self.updated_by = data['updated_by']
        if 'updated_date' in data:
            self.updated_date = data['updated_date']
        if 'pnr_no' in data:
            self.pnr_no=data['pnr_no']
        if 'comments' in data:
            self.comments=data['comments']
        if 'detail_id' in data:
            self.detail_id=data['detail_id']
        if 'ticket_amount' in data:
            self.ticket_amount = data['ticket_amount']
        if 'ticket_amount_personal' in data:
            self.ticket_amount_personal = data['ticket_amount_personal']
        if 'official' in data:
            self.official = data['official']
        if 'requirement_id' in data:
            self.requirement_id = data['requirement_id']

        if 'vendor_name' in data:
            self.vendor_name = data['vendor_name']
        if 'ticket_no' in data:
            self.ticket_no = data['ticket_no']
        if 'class_of_travel' in data:
            self.class_of_travel = data['class_of_travel']
        if 'train_number' in data:
            self.train_number = data['train_number']
        if 'seat_number' in data:
            self.seat_number = data['seat_number']
        if 'admin_paid' in data:
            self.admin_paid = data['admin_paid']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_from_time(self, from_time):
        self.from_time = from_time

    def set_to_time(self, to_time):
        self.to_time = to_time

    def set_ref_no(self, ref_no):
        self.ref_no = ref_no
    def set_pnr_no(self,pnr_no):
        self.pnr_no=pnr_no
    def set_ref_type(self, ref_type):
        self.ref_type = ref_type

    def set_booking_status(self, booking_status):
        self.booking_status = booking_status

    def set_travel_detail(self, travel_detail):
        self.travel_detail = travel_detail

    def set_requirement(self, requirment):
        self.requirement = requirment

    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_created_date(self, created_date):
        self.created_date = created_date

    def set_updated_by(self, updated_by):
        self.updated_by = updated_by

    def set_updated_date(self, updated_date):
        self.updated_date = updated_date

    def set_employee_id(self,employee_id):
        self.employee_id=employee_id
    def set_status(self,status):
        self.status=status

    def set_ticket_amount(self,ticket_amount):
        self.ticket_amount = ticket_amount

    def get_id(self):
        return self.id

    def get_from_time(self):
        return self.from_time

    def get_to_time(self):
        return self.to_time

    def get_ref_no(self):
        return self.ref_no

    def get_ref_type(self):
        return self.ref_type
    def get_from_place(self):
        return self.from_place
    def get_to_place(self):
        return self.to_place

    def get_booking_status(self):
        return self.booking_status

    def get_travel_detail(self):
        return self.travel_detail

    def get_requirement(self):
        return self.requirement
    def get_pnr_no(self):
        return self.pnr_no

    def get_created_by(self):
        return self.created_by

    def get_created_date(self):
        return self.created_date

    def get_updated_by(self):
        return self.updated_by

    def get_updated_date(self):
        return self.updated_date
    def get_status(self):
        return self.status

    def get_employee_id(self):
        return self.employee_id
    def get_comments(self):
        return self.comments
    def get_detail_id(self):
        return self.detail_id
    def get_ticket_amount(self):
        return self.ticket_amount
    def get_requirement_id(self):
        return self.requirement_id
    def get_vendor_name(self):
        return self.vendor_name
    def get_ticket_no(self):
        return self.ticket_no
    def get_class_of_travel(self):
        return self.class_of_travel
    def get_train_number(self):
        return self.train_number
    def get_seat_number(self):
        return self.seat_number
class AccomodationBooking_Request:
    id=None
    checkin_time=None
    checkout_time=None
    place_of_stay=None
    ref_no=None
    ref_type=None
    booking_status=None
    travel_detail =None
    requirement =None
    status =None
    created_by =None
    created_date =None
    updated_by = None
    updated_date = None
    comments = None
    detail_id = None
    ticket_amount = 0
    ticket_amount_personal = 0
    official = 1
    requirement_id = None
    vendor_name = None
    ticket_no = None
    class_of_stay = None
    room_number = None
    booking_needed_id=Travel_requirements.accomodation
    from_time = None
    to_time = None
    from_place = None
    to_place = None
    admin_paid = 1
    PNR = None
    fare_quoted = None
    issuance_type = None
    website = None


    def __init__(self,data):
        if 'id' in data:
            self.id = data['id']
        if 'checkin_time' in data:
            self.checkin_time = data['checkin_time']
        if 'PNR' in data:
            self.PNR = data['PNR']
        if 'fare_quoted' in data:
            self.fare_quoted = data['fare_quoted']
        if 'issuance_type' in data:
            self.issuance_type = data['issuance_type']
        if 'website' in data:
            self.website = data['website']
        if 'place_of_stay' in data:
            self.place_of_stay = data['place_of_stay']
        if 'checkout_time' in data:
            self.checkout_time = data['checkout_time']
        if 'ref_no' in data:
            self.ref_no = data['ref_no']
        if 'ref_type' in data:
            self.ref_type = data['ref_type']
        if 'booking_status' in data:
            self.booking_status = data['booking_status']
        if 'travel_detail' in data:
            self.travel_detail = data['travel_detail']
        if 'requirement' in data:
            self.requirement = data['requirement']
        if 'created_by' in data:
            self.created_by = data['created_by']
        if 'created_date' in data:
            self.created_date = data['created_date']
        if 'updated_by' in data:
            self.updated_by = data['updated_by']
        if 'updated_date' in data:
            self.updated_date = data['updated_date']
        if 'comments' in data:
            self.comments = data['comments']
        if 'detail_id' in data:
            self.detail_id = data['detail_id']
        if 'ticket_amount' in data:
            self.ticket_amount = data['ticket_amount']
        if 'ticket_amount_personal' in data:
            self.ticket_amount_personal = data['ticket_amount_personal']
        if 'official' in data:
            self.official = data['official']
        if 'requirement_id' in data:
            self.requirement_id = data['requirement_id']
        if 'vendor_name' in data:
            self.vendor_name=data['vendor_name']
        if 'ticket_no' in data:
            self.ticket_no=data['ticket_no']
        if 'class_of_stay' in data:
            self.class_of_stay=data['class_of_stay']
        if 'room_number' in data:
            self.room_number=data['room_number']
        if 'admin_paid' in data:
            self.admin_paid = data['admin_paid']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)




    def set_id(self, id):
        self.id = id
    def set_entity_id(self,entity_id):
        self.entity_id=entity_id

    def set_checkin_time(self, checkin_time):
        if checkin_time is None:
            self.checkin_time = checkin_time
        else:
            self.checkin_time = checkin_time.strftime("%d-%b-%Y")

    def set_checkout_time(self, checkout_time):
        if checkout_time is None:
            self.checkout_time = checkout_time
        else:
            self.checkout_time = checkout_time.strftime("%d-%b-%Y")

    def set_ref_no(self,ref_no):
        self.ref_no = ref_no

    def set_ref_type(self,ref_type):
        self.ref_type = ref_type

    def set_booking_status(self,booking_status):
        self.booking_status=booking_status
    def set_travel_detail(self,travel_detail):
        self.travel_detail=travel_detail

    def set_requirement(self,requirment):
        self.requirement= requirment

    def set_created_by(self,created_by):
        self.created_by = created_by

    def set_created_date(self, created_date):
        if created_date is None:
            self.created_date = created_date
        else:
            self.created_date = created_date.strftime("%d-%b-%Y")

    def set_updated_by(self,updated_by):
        self.updated_by = updated_by

    def set_updated_date(self, updated_date):
        if updated_date is None:
            self.updated_date = updated_date
        else:
            self.updated_date = updated_date.strftime("%d-%b-%Y")

    def set_status(self,status):
        self.status=status

    def set_ticket_amount(self, ticket_amount):
        self.ticket_amount = ticket_amount

    def get_id(self):
        return self.id

    def get_checkin_time(self):
        return self.checkin_time

    def get_checkout_time(self):
        return self.checkout_time

    def get_ref_no(self):
        return self.ref_no

    def get_ref_type(self):
        return self.ref_type
    def get_place_of_stay(self):
        return self.place_of_stay

    def get_booking_status(self):
        return self.booking_status

    def get_travel_detail(self):
        return self.travel_detail

    def get_requirement(self):
        return self.requirement


    def get_created_by(self):
        return self.created_by

    def get_created_date(self):
        return self.created_date

    def get_updated_by(self):
        return self.updated_by

    def get_updated_date(self):
        return self.updated_date

    def get_status(self):
        return self.status

    def get_comments(self):
        return self.comments
    def get_detail_id(self):
        return self.detail_id

    def get_ticket_amount(self):
        return self.ticket_amount
    def get_requirement_id(self):
        return self.requirement_id

    def get_room_number(self):
        return self.room_number
    def get_classof_stay(self):
        return self.class_of_stay
    def get_ticket_no(self):
        return self.ticket_no
    def get_vendor_name(self):
        return self.vendor_name

class Document_upload:
    tour_id = None
    ref_type = None
    travel_detail = None
    requirement_id = 0
    requirement_type = None

    def __init__(self, data):
        if 'tour_id' in data:
            self.tour_id = data['tour_id']
        # if 'ref_no' in data:
        #     self.ref_no = data['ref_no']
        if 'ref_type' in data:
            self.ref_type = data['ref_type']
        if 'requirement_type' in data:
            self.requirement_type = data['requirement_type']
        if 'requirement_id' in data:
            self.requirement_id = data['requirement_id']

        # if 'booking_status' in data:
        #     self.booking_status = data['booking_status']

    def get_tour_id(self):
        return self.tour_id

    # def get_ref_no(self):
    #     return self.ref_no

    def get_ref_type(self):
        return self.ref_type

    def get_requirement_type(self):
        return self.requirement_type

    def get_requirement_id(self):
        return self.requirement_id

    # def get_requirement(self):
    #     return self.requirement

class No_show_req:
    tour_id = None
    travel_detail_id = None
    requirement_id = 0
    requirement_type = None
    no_show_status = None

    def __init__(self, data):
        if 'tour_id' in data:
            self.tour_id = data['tour_id']
        if 'travel_detail_id' in data:
            self.travel_detail_id = data['travel_detail_id']
        if 'requirement_id' in data:
            self.requirement_id = data['requirement_id']
        if 'requirement_type' in data:
            self.requirement_type = data['requirement_type']
        if 'no_show_status' in data:
            self.no_show_status = data['no_show_status']










