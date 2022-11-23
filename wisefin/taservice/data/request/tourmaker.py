import json
from taservice.util.ta_util import Status,Onbehalfof,App_type

class TourRequest:
    id = None
    requestdate = None
    empgid = None
    empdesignation = None
    empgrade = None
    empbranchgid = None
    reason = None
    permittedby = None
    startdate = None
    enddate = None
    durationdays = None
    ordernoremarks = None
    status = Status.REQUESTED
    onbehalfof = Onbehalfof.ZERO
    eligiblemodeoftravel = None
    apptype = App_type.TOUR
    approval = None
    opening_balance=0
    quantum_of_funds=0
    transfer_on_promotion=0
    sortterm_travel=None
    non_base_location=None


    def __init__(self, tour_obj):
        if 'id' in tour_obj:
            self.id = tour_obj['id']
        if 'requestdate' in tour_obj:
            self.requestdate = tour_obj['requestdate']
        if 'empgid' in tour_obj:
            self.empgid = tour_obj['empgid']
        if 'empdesignation' in tour_obj:
            self.empdesignation = tour_obj['empdesignation']
        if 'empgrade' in tour_obj:
            self.empgrade = tour_obj['empgrade']
        if 'empbranchgid' in tour_obj:
            self.empbranchgid = tour_obj['empbranchgid']
        if 'reason' in tour_obj:
            self.reason = tour_obj['reason']
        if 'permittedby' in tour_obj:
            self.permittedby = tour_obj['permittedby']
        if 'startdate' in tour_obj:
            self.startdate = tour_obj['startdate']
        if 'enddate' in tour_obj:
            self.enddate = tour_obj['enddate']
        if 'durationdays' in tour_obj:
            self.durationdays = tour_obj['durationdays']
        if 'ordernoremarks' in tour_obj:
            self.ordernoremarks = tour_obj['ordernoremarks']
        if 'sortterm_travel' in tour_obj:
            self.sortterm_travel = tour_obj['sortterm_travel']
        if 'eligiblemodeoftravel' in tour_obj:
            self.eligiblemodeoftravel = tour_obj['eligiblemodeoftravel']
        if 'onbehalfof' in tour_obj:
            self.onbehalfof = tour_obj['onbehalfof']
        if 'status' in tour_obj:
            self.status = tour_obj['status']
        if 'apptype' in tour_obj:
            self.apptype = tour_obj['apptype']
        if 'approval' in tour_obj:
            self.approval = tour_obj['approval']
        if 'opening_balance' in tour_obj:
            self.opening_balance = tour_obj['opening_balance']
        if 'quantum_of_funds' in tour_obj:
            self.quantum_of_funds = tour_obj['quantum_of_funds']
        if 'transfer_on_promotion' in tour_obj:
            self.transfer_on_promotion = tour_obj['transfer_on_promotion']
        if 'non_base_location' in tour_obj:
            self.non_base_location = tour_obj['non_base_location']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_requestdate(self, requestdate):
        self.requestdate = requestdate

    def set_empgid(self, empgid):
        self.empgid = empgid

    def set_empdesignation(self, empdesignation):
        self.empdesignation = empdesignation

    def set_empgrade(self, empgrade):
        self.empgrade = empgrade

    def set_empbranchgid(self, empbranchgid):
        self.empbranchgid = empbranchgid

    def set_reason(self, reason):
        self.reason = reason

    def set_permittedby(self, permittedby):
        self.permittedby = permittedby

    def set_startdate(self, startdate):
        self.startdate = startdate

    def set_enddate(self, enddate):
        self.enddate = enddate

    def set_durationdays(self, durationdays):
        self.durationdays = durationdays

    def set_ordernoremarks(self, ordernoremarks):
        self.ordernoremarks = ordernoremarks

    def set_eligiblemodeoftravel(self, eligiblemodeoftravel):
        self.eligiblemodeoftravel = eligiblemodeoftravel

    def set_onbehalfof(self, onbehalfof):
        self.onbehalfof = onbehalfof

    def set_status(self, status):
        self.status = status

    def set_approval(self, approval):
        self.approval = approval

    def set_apptype(self, apptype):
        self.apptype = apptype

    def set_opening_balance(self, opening_balance):
        self.opening_balance = opening_balance

    def set_quantum_of_funds(self, quantum_of_funds):
        self.quantum_of_funds = quantum_of_funds
    def set_transfer_on_promotion(self, transfer_on_promotion):
        self.transfer_on_promotion = transfer_on_promotion

    def get_id(self):
        return self.id

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

    def get_sortterm_travel(self):
        return self.sortterm_travel
    def get_non_base_location(self):
        return self.non_base_location

    def get_reason(self):
        return self.reason

    def get_permittedby(self):
        return self.permittedby

    def get_startdate(self):
        return self.startdate

    def get_enddate(self):
        return self.enddate

    def get_durationdays(self):
        return self.durationdays

    def get_ordernoremarks(self):
        return self.ordernoremarks

    def get_status(self):
        return self.status

    def get_eligiblemodeoftravel(self):
        return self.eligiblemodeoftravel

    def get_onbehalfof(self):
        if self.onbehalfof >0:
            return self.onbehalfof
        else:
            return 0

    def get_apptype(self):
        return self.apptype

    def get_approval(self):
        return self.approval

    def get_quantum_of_funds(self):
        return self.quantum_of_funds

    def get_opening_balance(self):
        return self.opening_balance
    def get_transfer_on_promotion(self):
        return self.transfer_on_promotion



class TourDetailRequest:
    id = None
    startdate = None,
    enddate = None,
    startingpoint = None,
    placeofvisit = None,
    purposeofvisit = None
    official=1
    comments=None

    def __init__(self, tour_obj):
        if 'id' in tour_obj:
            self.id = tour_obj['id']
        if 'startdate' in tour_obj:
            self.startdate = tour_obj['startdate']
        if 'enddate' in tour_obj:
            self.enddate = tour_obj['enddate']
        if 'startingpoint' in tour_obj:
            self.startingpoint = tour_obj['startingpoint']
        if 'placeofvisit' in tour_obj:
            self.placeofvisit = tour_obj['placeofvisit']
        if 'purposeofvisit' in tour_obj:
            self.purposeofvisit = tour_obj['purposeofvisit']
        if 'official' in tour_obj:
            self.official = tour_obj['official']
        if 'comments' in tour_obj:
            self.comments = tour_obj['comments']


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def set_id(self, id):
        self.id = id
    def set_startdate(self, startdate):
        self.startdate = startdate
    def set_enddate(self, enddate):
        self.enddate = enddate
    def set_startingpoint(self, startingpoint):
        self.startingpoint = startingpoint
    def set_placeofvisit(self, placeofvisit):
        self.placeofvisit = placeofvisit
    def set_purposeofvisit(self, purposeofvisit):
        self.purposeofvisit = purposeofvisit


    def get_id(self):
        return self.id
    def get_startdate(self):
        return self.startdate
    def get_enddate(self):
        return self.enddate
    def get_startingpoint(self):
        return self.startingpoint
    def get_placeofvisit(self):
        return self.placeofvisit
    def get_purposeofvisit(self):
        return self.purposeofvisit
    def get_official(self):
        return self.official
    def get_comments(self):
        return self.comments

class Status_check:
    tour_status = None
    advance_status = None
    claim_status = None

    def __init__(self, tour_obj):
        if 'tour_status' in tour_obj:
            self.tour_status = tour_obj['tour_status']
        if 'advance_status' in tour_obj:
            self.advance_status = tour_obj['advance_status']
        if 'claim_status' in tour_obj:
            self.claim_status = tour_obj['claim_status']


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


    def get_tour_status(self):
        return self.tour_status
    def get_advance_status(self):
        return self.advance_status
    def get_claim_status(self):
        return self.claim_status

class Chat_Box:
    id =None
    request = None
    maker_id = None
    ref_type = 1
    RM_id=None
    approver_id = None
    comment = None
    type=1
    def __init__(self, tour_obj):
        if 'id' in tour_obj:
            self.id = tour_obj['id']
        if 'request' in tour_obj:
            self.request = tour_obj['request']
        if 'maker_id' in tour_obj:
            self.maker_id = tour_obj['maker_id']
        if 'ref_type' in tour_obj:
            self.ref_type = tour_obj['ref_type']
        if 'approver_id' in tour_obj:
            self.approver_id = tour_obj['approver_id']
        if 'comment' in tour_obj:
            self.comment = tour_obj['comment']
        if 'type' in tour_obj:
            self.type = tour_obj['type']
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def get_id(self):
        return self.id
    def get_request(self):
        return self.request
    def get_maker_id(self):
        return self.maker_id
    def get_ref_type(self):
        return self.ref_type
    def get_approver_id(self):
        return self.approver_id
    def get_comment(self):
        return self.comment
    def get_type(self):
        return self.type

class Doc_type:
    id=None
    code = None
    file_type = None
    file_name = None
    description = None
    def __init__(self, tour_obj):
        if 'id' in tour_obj:
            self.id = tour_obj['id']
        if 'file_type' in tour_obj:
            self.file_type=tour_obj["file_type"]
        if "file_name" in tour_obj:
            self.file_name=tour_obj["file_name"]
        if "description" in tour_obj:
            self.description=tour_obj["description"]
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def get_id(self):
        return self.id
    def get_file_type(self):
        return self.file_type
    def get_file_name(self):
        return self.file_name
    def get_description(self):
        return self.description

class Booking:
    id = None
    booking_id = None
    type = None
    file_type = None
    file_name = None
    description = None
    booking_status = None
    booking_id= None
    comments = None
    cancel_reschedule = None
    cancel_reason = None
    refund_amount = None
    refund_date = None
    fare_difference = None
    booking_needed = None
    reference_id = None
    requirement_id = None
    ticket_amount = None
    ticket_amount_personal = None
    official = 1
    travel_detail = None
    cab_mapping_id = None
    admin_paid=1

    def __init__(self, tour_obj):
        if 'id' in tour_obj:
            self.id = tour_obj['id']
        if 'booking_id' in tour_obj:
            self.booking_id = tour_obj['booking_id']
        if 'type' in tour_obj:
            self.type = tour_obj["type"]
        if 'file_type' in tour_obj:
            self.file_type = tour_obj["file_type"]
        if "file_name" in tour_obj:
            self.file_name = tour_obj["file_name"]
        if "description" in tour_obj:
            self.description = tour_obj["description"]
        if 'booking_status' in tour_obj:
            self.booking_status = tour_obj['booking_status']
        if 'comments' in tour_obj:
            self.comments = tour_obj["comments"]
        if 'cancel_reschedule' in tour_obj:
            self.cancel_reschedule = tour_obj["cancel_reschedule"]
        if "cancel_reason" in tour_obj:
            self.cancel_reason = tour_obj["cancel_reason"]
        if "refund_amount" in tour_obj:
            self.refund_amount = tour_obj["refund_amount"]
        if 'fare_difference' in tour_obj:
            self.fare_difference = tour_obj['fare_difference']
        if 'booking_needed' in tour_obj:
            self.booking_needed = tour_obj["booking_needed"]
        if 'booking_id' in tour_obj:
            self.booking_id = tour_obj["booking_id"]
        if 'reference_id' in tour_obj:
            self.reference_id = tour_obj["reference_id"]
        if 'requirement_id' in tour_obj:
            self.requirement_id = tour_obj["requirement_id"]
        if 'ticket_amount' in tour_obj:
            self.ticket_amount = tour_obj["ticket_amount"]
        if 'ticket_amount_personal' in tour_obj:
            self.ticket_amount_personal = tour_obj["ticket_amount_personal"]
        if 'official' in tour_obj:
            self.official = tour_obj["official"]
        if 'travel_detail' in tour_obj:
            self.travel_detail = tour_obj["travel_detail"]
        if 'cab_mapping_id' in tour_obj:
            self.cab_mapping_id = tour_obj["cab_mapping_id"]
        if 'admin_paid' in tour_obj:
            self.admin_paid = tour_obj["admin_paid"]

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

