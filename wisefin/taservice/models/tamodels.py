from django.db import models
from django.utils.timezone import now
from db.vsolvmodels import VsolvModels

class TourRequest(VsolvModels):
    travel_no = models.CharField(max_length=256, null=True, blank=True)
    empgid = models.IntegerField(default=-1)
    empdesignation = models.CharField(max_length=128)
    empgrade = models.CharField(max_length=128,null=True,blank=True)
    empbranchgid = models.IntegerField(default=1)
    reason = models.IntegerField(default=1)
    permittedby = models.IntegerField(default=1)
    durationdays = models.IntegerField(default=1)
    international_travel = models.IntegerField(default=0)
    week_end_travel = models.TextField(null=True, blank=True)
    remarks = models.CharField(max_length=256, null=True, blank=True)
    onbehalfof = models.IntegerField(null=True, blank=True)
    onbehalf_designation = models.CharField(max_length=128,null=True, blank=True)
    onbehalf_grade = models.CharField(max_length=128,null=True, blank=True)
    onbehalf_branchgid = models.IntegerField(null=True, blank=True)
    opening_balance = models.FloatField(null=True, blank=True)
    quantum_of_funds = models.FloatField(null=True, blank=True)
    tour_status = models.SmallIntegerField(default=1)
    advance_status = models.SmallIntegerField(default=-1)
    claim_status = models.SmallIntegerField(default=-1)
    transfer_on_promotion = models.SmallIntegerField(default=0)
    tour_cancel_status = models.SmallIntegerField(default=-1)
    advance_cancel_status = models.SmallIntegerField(default=-1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    request_date = models.DateTimeField(default=now)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    air_status = models.SmallIntegerField(default=0)
    train_status = models.SmallIntegerField(default=0)
    bus_status = models.SmallIntegerField(default=0)
    cab_status = models.SmallIntegerField(default=0)
    accomodation_status = models.SmallIntegerField(default=0)
    air_booked_by = models.SmallIntegerField(default=0)
    train_booked_by = models.SmallIntegerField(default=0)
    bus_booked_by = models.SmallIntegerField(default=0)
    cab_booked_by = models.SmallIntegerField(default=0)
    accomodation_booked_by = models.SmallIntegerField(default=0)
    sortterm_travel= models.SmallIntegerField(default=0,null=True,blank=True)
    non_base_location=models.CharField(max_length=128,null=True, blank=True)
    team = models.IntegerField(default=0)
    sub_team = models.IntegerField(default=0)

class Meta:
    db_table = 'TourRequest'

class TourReason(VsolvModels):
    code = models.CharField(max_length=128,unique=True)
    name = models.CharField(max_length=128)
    fileupload = models.SmallIntegerField(default=0)
    international_travel = models.SmallIntegerField(default=0)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Meta:
    db_table = 'TourReason'

class TravelHistory(VsolvModels):
    tour = models.ForeignKey(TourRequest,on_delete=models.CASCADE,null=True)
    approvedby = models.IntegerField(default=1)
    onbehalfof_approval = models.IntegerField(default=0)
    approveddate = models.DateTimeField(default=now)
    request_type = models.CharField(max_length=128)
    applevel = models.IntegerField(default=1)
    comment = models.CharField(max_length=500)
    status = models.SmallIntegerField(default=1)


class Meta:
    db_table = 'ApprovedBy'

class TourDetail(VsolvModels):
    tour = models.ForeignKey(TourRequest,on_delete=models.CASCADE,null=True)
    official = models.IntegerField(default=1)
    startdate = models.DateTimeField()
    enddate = models.DateTimeField()
    toplace = models.CharField(max_length=128,null=True,blank=True)
    client = models.IntegerField(default=0)
    client_mapping_data = models.IntegerField(default=0)
    client_name = models.CharField(max_length=512, null=True, blank=True)
    startingpoint = models.CharField(max_length=128)
    comments = models.CharField(max_length=128,null=True, blank=True)
    placeofvisit = models.CharField(max_length=128,null=True, blank=True)
    purposeofvisit = models.CharField(max_length=128)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    air_required = models.SmallIntegerField(default=0)
    train_required = models.SmallIntegerField(default=0)
    bus_required = models.SmallIntegerField(default=0)
    cab_required = models.SmallIntegerField(default=0)
    accomodation_required = models.SmallIntegerField(default=0)


class FrequentData(VsolvModels):
    from_place=models.CharField(max_length=128, null=True, blank=True)
    from_place_count=models.IntegerField(default=0)
    placeofvisit = models.CharField(max_length=128, null=True, blank=True)
    placeofvisit_count = models.IntegerField(default=0)
    client = models.IntegerField(null=True, blank=True)
    client_count = models.IntegerField(default=0)
    employee = models.IntegerField(default=0)
    status = models.IntegerField(default=1)
    latest_date = models.DateTimeField(null=True, blank=True)

class BookingHistory(VsolvModels):
    # tour = models.ForeignKey(TourRequest,on_delete=models.CASCADE,null=True)
    tourdetail = models.ForeignKey(TourDetail,on_delete=models.CASCADE,null=True)
    booking_needed = models.IntegerField(null=False, blank=False)
    reference_id = models.IntegerField(default=0)
    booking_status = models.IntegerField(default=0)
    booking_time = models.DateTimeField(default=now)
    comments = models.CharField(max_length=128,null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    ticket_amount = models.FloatField(null=True, blank=True)
    ticket_amount_personal = models.FloatField(null=True)
    official = models.IntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    cancel_reschedule = models.IntegerField(null=True, blank=True)
    cancel_reason = models.CharField(max_length=256,null=True, blank=True)
    refund_amount = models.FloatField(null=True, blank=True)
    refund_date = models.DateTimeField(null=True, blank=True)
    fare_difference = models.IntegerField(null=True, blank=True)
    cancelled_date = models.DateTimeField(null=True, blank=True)
    loss_of_cancelation=models.FloatField(null=True,blank=True)
    invoice_amount = models.FloatField(default=0)

class AccomodationBookingInfo(VsolvModels):
    checkin_time=models.DateTimeField()
    checkout_time=models.DateTimeField(null=True, blank=True)
    place_of_stay = models.CharField(max_length=128,null=True, blank=True)
    ref_no=models.CharField(max_length=128,null=True, blank=True)
    ref_type=models.CharField(max_length=128,null=True, blank=True)
    booking_status=models.IntegerField(default=0)
    booked_by = models.SmallIntegerField(default=0)
    # tour = models.ForeignKey(TourRequest, on_delete=models.CASCADE, null=True)
    travel_detail = models.ForeignKey(TourDetail, on_delete=models.CASCADE, null=True)
    # requirement = models.ForeignKey(TravelRequirements, on_delete=models.CASCADE, null=True)
    comments = models.CharField(max_length=128,null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class CabBookingInfo(VsolvModels):
    from_time=models.DateTimeField(null=True, blank=True)
    to_time=models.DateTimeField(null=True, blank=True)
    from_place = models.CharField(max_length=128, null=True, blank=True)
    to_place = models.CharField(max_length=128, null=True, blank=True)
    ref_no=models.CharField(max_length=128,null=True, blank=True)
    ref_type=models.CharField(max_length=128,null=True, blank=True)
    booking_status=models.IntegerField(default=0)
    travel_type_cab=models.IntegerField(default=0)
    booked_by = models.SmallIntegerField(default=0)
    # tour = models.ForeignKey(TourRequest, on_delete=models.CASCADE, null=True)
    travel_detail = models.ForeignKey(TourDetail, on_delete=models.CASCADE, null=True)
    # requirement = models.ForeignKey(TravelRequirements, on_delete=models.CASCADE, null=True)
    comments = models.CharField(max_length=128,null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class BusBookingInfo(VsolvModels):
    from_time=models.DateTimeField()
    to_time=models.DateTimeField(null=True, blank=True)
    from_place = models.CharField(max_length=128, null=True, blank=True)
    to_place = models.CharField(max_length=128, null=True, blank=True)
    ref_no=models.CharField(max_length=128,null=True, blank=True)
    ref_type=models.CharField(max_length=128,null=True, blank=True)
    booking_status=models.IntegerField(default=0)
    booked_by = models.SmallIntegerField(default=0)
    # tour = models.ForeignKey(TourRequest, on_delete=models.CASCADE, null=True)
    travel_detail = models.ForeignKey(TourDetail, on_delete=models.CASCADE, null=True)
    # requirement = models.ForeignKey(TravelRequirements, on_delete=models.CASCADE, null=True)
    comments = models.CharField(max_length=128,null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class TrainBookingInfo(VsolvModels):
    from_time=models.DateTimeField()
    to_time=models.DateTimeField(null=True, blank=True)
    from_place = models.CharField(max_length=128, null=True, blank=True)
    to_place = models.CharField(max_length=128, null=True, blank=True)
    ref_no=models.CharField(max_length=128,null=True, blank=True)
    ref_type=models.CharField(max_length=128,null=True, blank=True)
    pnr_no=models.CharField(max_length=128,null=True, blank=True)
    booking_status=models.IntegerField(default=0)
    booked_by = models.SmallIntegerField(default=0)
    # tour = models.ForeignKey(TourRequest, on_delete=models.CASCADE, null=True)
    travel_detail = models.ForeignKey(TourDetail, on_delete=models.CASCADE, null=True)
    # requirement = models.ForeignKey(TravelRequirements, on_delete=models.CASCADE, null=True)
    comments = models.CharField(max_length=128,null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class AirBookingInfo(VsolvModels):
    from_time=models.DateTimeField()
    to_time=models.DateTimeField(null=True, blank=True)
    from_place = models.CharField(max_length=128, null=True, blank=True)
    to_place = models.CharField(max_length=128, null=True, blank=True)
    ref_no=models.CharField(max_length=128,null=True, blank=True)
    ref_type=models.CharField(max_length=128,null=True, blank=True)
    boarding_no=models.CharField(max_length=128,null=True, blank=True)
    booking_status=models.IntegerField(default=0)
    booked_by = models.SmallIntegerField(default=0)
    # tour = models.ForeignKey(TourRequest, on_delete=models.CASCADE, null=True)
    travel_detail = models.ForeignKey(TourDetail, on_delete=models.CASCADE, null=True)
    # requirement = models.ForeignKey(TravelRequirements, on_delete=models.CASCADE, null=True)
    comments = models.CharField(max_length=128,null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class AccomodationBookingDetails(VsolvModels):
    checkin_time=models.DateTimeField()
    checkout_time=models.DateTimeField(null=True, blank=True)
    place_of_stay = models.CharField(max_length=128,null=True, blank=True)
    ref_no=models.CharField(max_length=128,null=True, blank=True)
    ref_type=models.CharField(max_length=128,null=True, blank=True)
    booking_status=models.IntegerField(default=0)
    # tour = models.ForeignKey(TourRequest, on_delete=models.CASCADE, null=True)
    travel_detail = models.ForeignKey(TourDetail, on_delete=models.CASCADE, null=True)
    # requirement = models.ForeignKey(TravelRequirements, on_delete=models.CASCADE, null=True)
    comments = models.CharField(max_length=128,null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    requirement_id = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    ticket_amount = models.FloatField(null=True)
    ticket_amount_personal = models.FloatField(null=True)
    official = models.IntegerField(default=1)
    vendor_name = models.CharField(max_length=128, null=True)
    ticket_no = models.CharField(max_length=128, null=True)
    class_of_stay = models.CharField(max_length=128, null=True)
    room_number = models.CharField(max_length=128, null=True)
    admin_paid = models.IntegerField(default=1)
    invoice_amount = models.FloatField(default=0)
    PNR=models.CharField(max_length=128, null=True,blank=True)
    cost_per_head=models.FloatField(null=True,blank=True)
    fare_quoted=models.FloatField(null=True,blank=True)
    difference_in_amount=models.FloatField(null=True,blank=True)
    issuance_type=models.CharField(max_length=128, null=True,blank=True)
    website=models.CharField(max_length=128, null=True,blank=True)
    utilised_status = models.IntegerField(default=1)
    noshow_reason = models.CharField(max_length=256,null=True, blank=True)
    booking_date = models.DateTimeField(default=now,null=True, blank=True)

class CabBookingDetails(VsolvModels):
    from_time=models.DateTimeField(null=True, blank=True)
    to_time=models.DateTimeField(null=True, blank=True)
    from_place = models.CharField(max_length=128, null=True, blank=True)
    to_place = models.CharField(max_length=128, null=True, blank=True)
    travel_type_cab = models.IntegerField(default=0)
    ref_no=models.CharField(max_length=128,null=True, blank=True)
    ref_type=models.CharField(max_length=128,null=True, blank=True)
    booking_status=models.IntegerField(default=0)
    # travel_detail = models.ForeignKey(TourDetail, on_delete=models.CASCADE, null=True)
    comments = models.CharField(max_length=128,null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    # requirement_id = models.IntegerField(null=True, blank=True)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    ticket_amount = models.FloatField(null=True)
    ticket_amount_personal = models.FloatField(null=True)
    official = models.IntegerField(default=1)
    cost_per_head = models.FloatField(null=True)
    booked_no = models.IntegerField(default=1)
    cancelled_no = models.IntegerField(default=0)
    vendor_name = models.CharField(max_length=128, null=True)
    ticket_no = models.CharField(max_length=128, null=True)
    class_of_travel = models.CharField(max_length=128, null=True)
    cab_number = models.CharField(max_length=128, null=True)
    PNR = models.CharField(max_length=128, null=True, blank=True)
    fare_quoted = models.FloatField(null=True, blank=True)
    difference_in_amount = models.FloatField(null=True, blank=True)
    issuance_type = models.CharField(max_length=128, null=True, blank=True)
    website = models.CharField(max_length=128, null=True, blank=True)
    booking_date = models.DateTimeField(default=now,null=True, blank=True)

class CabMapping(VsolvModels):
    BookingDetailId  = models.IntegerField(default=0)
    booking_status = models.IntegerField(default=0)
    booking_date = models.DateTimeField(default=now)
    travel_detail = models.ForeignKey(TourDetail, on_delete=models.CASCADE, null=True)
    requirement_id = models.IntegerField(null=True, blank=True)
    ticket_amount = models.FloatField(null=True)
    ticket_amount_personal = models.FloatField(null=True)
    official = models.IntegerField(default=1)
    status = models.SmallIntegerField(default=1)
    cancel_reschedule = models.IntegerField(null=True, blank=True)
    cancel_reason = models.CharField(max_length=256,null=True, blank=True)
    refund_amount = models.FloatField(null=True, blank=True)
    refund_date = models.DateTimeField(null=True, blank=True)
    fare_difference = models.IntegerField(null=True, blank=True)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    admin_paid = models.IntegerField(default=1)
    invoice_amount = models.FloatField(default=0)
    utilised_status = models.IntegerField(default=1)
    noshow_reason = models.CharField(max_length=256,null=True, blank=True)


class BusBookingDetails(VsolvModels):
    from_time=models.DateTimeField()
    to_time=models.DateTimeField(null=True, blank=True)
    from_place = models.CharField(max_length=128, null=True, blank=True)
    to_place = models.CharField(max_length=128, null=True, blank=True)
    ref_no=models.CharField(max_length=128,null=True, blank=True)
    ref_type=models.CharField(max_length=128,null=True, blank=True)
    booking_status=models.IntegerField(default=0)
    travel_detail = models.ForeignKey(TourDetail, on_delete=models.CASCADE, null=True)
    comments = models.CharField(max_length=128,null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    requirement_id = models.IntegerField(null=True, blank=True)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    ticket_amount = models.FloatField(null=True)
    ticket_amount_personal = models.FloatField(null=True)
    official = models.IntegerField(default=1)
    vendor_name = models.CharField(max_length=128, null=True)
    ticket_no = models.CharField(max_length=128, null=True)
    class_of_travel = models.CharField(max_length=128, null=True)
    bus_number = models.CharField(max_length=128, null=True)
    seat_number = models.CharField(max_length=128, null=True)
    admin_paid = models.IntegerField(default=1)
    invoice_amount = models.FloatField(default=0)
    PNR = models.CharField(max_length=128, null=True, blank=True)
    cost_per_head = models.FloatField(null=True, blank=True)
    fare_quoted = models.FloatField(null=True, blank=True)
    difference_in_amount = models.FloatField(null=True, blank=True)
    issuance_type = models.CharField(max_length=128, null=True, blank=True)
    website = models.CharField(max_length=128, null=True, blank=True)
    utilised_status = models.IntegerField(default=1)
    noshow_reason = models.CharField(max_length=256,null=True, blank=True)
    booking_date = models.DateTimeField(default=now, null=True, blank=True)


class TrainBookingDetails(VsolvModels):
    from_time=models.DateTimeField()
    to_time=models.DateTimeField(null=True, blank=True)
    from_place = models.CharField(max_length=128, null=True, blank=True)
    to_place = models.CharField(max_length=128, null=True, blank=True)
    ref_no=models.CharField(max_length=128,null=True, blank=True)
    ref_type=models.CharField(max_length=128,null=True, blank=True)
    pnr_no=models.CharField(max_length=128,null=True, blank=True)
    booking_status=models.IntegerField(default=0)
    travel_detail = models.ForeignKey(TourDetail, on_delete=models.CASCADE, null=True)
    comments = models.CharField(max_length=128,null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    requirement_id = models.IntegerField(null=True, blank=True)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    ticket_amount = models.FloatField(null=True)
    ticket_amount_personal = models.FloatField(null=True)
    official = models.IntegerField(default=1)
    vendor_name = models.CharField(max_length=128, null=True)
    ticket_no = models.CharField(max_length=128, null=True)
    class_of_travel = models.CharField(max_length=128, null=True)
    train_number = models.CharField(max_length=128, null=True)
    seat_number = models.CharField(max_length=128, null=True)
    admin_paid = models.IntegerField(default=1)
    invoice_amount = models.FloatField(default=0)
    PNR = models.CharField(max_length=128, null=True, blank=True)
    cost_per_head = models.FloatField(null=True, blank=True)
    fare_quoted = models.FloatField(null=True, blank=True)
    difference_in_amount = models.FloatField(null=True, blank=True)
    issuance_type = models.CharField(max_length=128, null=True, blank=True)
    website = models.CharField(max_length=128, null=True, blank=True)
    utilised_status = models.IntegerField(default=1)
    noshow_reason = models.CharField(max_length=256,null=True, blank=True)
    booking_date = models.DateTimeField(default=now, null=True, blank=True)

class AirBookingDetails(VsolvModels):
    from_time=models.DateTimeField()
    to_time=models.DateTimeField(null=True, blank=True)
    from_place = models.CharField(max_length=128, null=True, blank=True)
    to_place = models.CharField(max_length=128, null=True, blank=True)
    ref_no=models.CharField(max_length=128,null=True, blank=True)
    ref_type=models.CharField(max_length=128,null=True, blank=True)
    boarding_no=models.CharField(max_length=128,null=True, blank=True)
    booking_status=models.IntegerField(default=0)
    travel_detail = models.ForeignKey(TourDetail, on_delete=models.CASCADE, null=True)
    comments = models.CharField(max_length=128,null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    requirement_id = models.IntegerField(null=True, blank=True)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    ticket_amount = models.FloatField(null=True)
    ticket_amount_personal = models.FloatField(null=True)
    official = models.IntegerField(default=1)
    vendor_name = models.CharField(max_length=128, null=True)
    ticket_no = models.CharField(max_length=128, null=True)
    class_of_travel = models.CharField(max_length=128, null=True)
    flight_number = models.CharField(max_length=128, null=True)
    seat_number = models.CharField(max_length=128, null=True)
    admin_paid = models.IntegerField(default=1)
    invoice_amount = models.FloatField(default=0)
    PNR = models.CharField(max_length=128, null=True, blank=True)
    cost_per_head = models.FloatField(null=True, blank=True)
    fare_quoted = models.FloatField(null=True, blank=True)
    difference_in_amount = models.FloatField(null=True, blank=True)
    issuance_type = models.CharField(max_length=128, null=True, blank=True)
    website = models.CharField(max_length=128, null=True, blank=True)
    utilised_status = models.IntegerField(default=1)
    noshow_reason = models.CharField(max_length=256,null=True, blank=True)
    booking_date = models.DateTimeField(default=now, null=True, blank=True)

# class TravelDocument(VsolvModels):
#     code = models.CharField(max_length=128)
#     type = models.IntegerField(default=1)
#     file_id = models.CharField(max_length=256)
#     file_name = models.CharField(max_length=256)
#     description = models.CharField(max_length=512)
#     status = models.SmallIntegerField(default=1)
#     created_by = models.IntegerField(null=False, blank=False)
#     created_date = models.DateTimeField(default=now)
#     updated_by = models.IntegerField(null=True, blank=True)
#     updated_date = models.DateTimeField(null=True, blank=True)
#     tour = models.ForeignKey(TourRequest, on_delete=models.CASCADE)
#     reference_id = models.IntegerField(default=0)
    # detail = models.ForeignKey(TourDetail, on_delete=models.CASCADE)
    # requirement = models.ForeignKey(TravelRequirements, on_delete=models.CASCADE)

class InternationalTravel(VsolvModels):
    tour = models.ForeignKey(TourRequest, on_delete=models.CASCADE, null=True)
    approved_by=models.IntegerField(default=0)
    approved_date = models.DateTimeField(null=True, blank=True)
    insured=models.SmallIntegerField(default=0)
    insurance_no=models.CharField(max_length=512,null=True, blank=True)
    comments=models.CharField(max_length=128,null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Meta:
    db_table = 'TourDetail'

class TourAdvance(VsolvModels):
    tour = models.ForeignKey(TourRequest,on_delete=models.CASCADE,null=True)
    reason = models.CharField(max_length=128)
    reqamount = models.FloatField()
    appamount = models.FloatField()
    currency_type = models.IntegerField(default=1)
    invoiceheadergid = models.IntegerField(null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    adjustamount = models.FloatField(null=True, blank=True)
    ppx_headergid = models.IntegerField( null=True, blank=True)
    crnno = models.CharField(max_length=32, null=True, blank=True)
    debit_categorygid = models.IntegerField( null=True, blank=True)
    debit_subcategorygid = models.IntegerField( null=True, blank=True)


class Meta:
    db_table = 'TourAdvance'


class Currency(VsolvModels):
    code = models.CharField(max_length=128,unique=True)
    name = models.CharField(max_length=128)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class TourExpense(VsolvModels):
    code = models.CharField(max_length=128,unique=True)
    name = models.CharField(max_length=128)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Meta:
    db_table = 'TourExpense'

class ClaimRequest(VsolvModels):
    tour = models.ForeignKey(TourRequest, on_delete=models.CASCADE, null=True)
    expensegid = models.IntegerField()
    claimedamount = models.FloatField()
    approvedamount = models.FloatField()
    requestercomment = models.CharField(max_length=500)
    approvercomment = models.CharField(max_length=500)
    invoiceheadergid = models.IntegerField(null=True, blank=True)
    crn_no = models.CharField(max_length=128,null=True, blank=True)
    payment_status = models.IntegerField(default=0)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Meta:
    db_table = 'ClaimRequest'

class Dailydeim(VsolvModels):
    tour = models.ForeignKey(TourRequest, on_delete=models.CASCADE, null=True)
    claimreq = models.ForeignKey(ClaimRequest, on_delete=models.CASCADE, null=True)
    citytype = models.CharField(max_length=128, null=True, blank=True)
    visitcity = models.CharField(max_length=128, null=True, blank=True)
    fromdate = models.DateTimeField(null=True, blank=True)
    todate = models.DateTimeField(null=True, blank=True)
    boardingbyorganiser = models.CharField(max_length=128, null=True)
    billno = models.CharField(max_length=128, null=True)
    noofhours = models.IntegerField(null=True, blank=True)
    noofdays = models.SmallIntegerField(null=True, blank=True)
    eligibleamount = models.FloatField()
    foodallowance = models.FloatField(null=True, blank=True)
    medicalexpense = models.FloatField(null=True, blank=True)
    claimedamount = models.FloatField(null=True, blank=True)
    approvedamount = models.FloatField(null=True, blank=True)
    remarks = models.CharField(max_length=128, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Meta:
    db_table = 'Dailydeim'

class Incidental(VsolvModels):
    tour = models.ForeignKey(TourRequest, on_delete=models.CASCADE, null=True)
    claimreq = models.ForeignKey(ClaimRequest, on_delete=models.CASCADE, null=True)
    code = models.CharField(max_length=128)
    samedayreturn = models.SmallIntegerField(default=1)
    travelhours = models.FloatField()
    singlefare = models.FloatField()
    expenses = models.FloatField()
    vendorname = models.CharField(max_length=128,null=True, blank=True)
    vendortype = models.CharField(max_length=128,null=True, blank=True)
    vendorcode = models.CharField(max_length=128,null=True, blank=True)
    gstno = models.CharField(max_length=128,null=True, blank=True)
    gstrate = models.FloatField(null=True, blank=True)
    eligibleamount = models.FloatField()
    claimedamount = models.FloatField()
    approvedamount = models.FloatField()
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Meta:
    db_table = 'Incidental'

class Localdeputation(VsolvModels):
    tour = models.ForeignKey(TourRequest, on_delete=models.CASCADE, null=True)
    claimreq = models.ForeignKey(ClaimRequest, on_delete=models.CASCADE, null=True)
    visitcity = models.CharField(max_length=45)
    fromdate = models.DateTimeField()
    todate = models.DateTimeField()
    sysdays = models.IntegerField(default=0)
    noofdays = models.IntegerField(default=0)
    isleave = models.SmallIntegerField(default=0)
    eligibleamount = models.FloatField(default=0)
    claimedamount = models.FloatField(default=0)
    approvedamount = models.FloatField(default=0)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Localconveyence(VsolvModels):
    tour = models.ForeignKey(TourRequest, on_delete=models.CASCADE, null=True)
    claimreq = models.ForeignKey(ClaimRequest, on_delete=models.CASCADE, null=True)
    modeoftravel = models.CharField(max_length=128)
    fromplace = models.CharField(max_length=128)
    toplace = models.CharField(max_length=128)
    distance = models.CharField(max_length=128, null=True)
    billno = models.CharField(max_length=128, null=True)
    eligibleamount = models.FloatField()
    claimedamount = models.FloatField()
    approvedamount = models.FloatField(null=True, blank=True)
    fromdate = models.DateTimeField(null=True, blank=True)
    todate = models.DateTimeField(null=True, blank=True)
    remarks = models.CharField(max_length=128, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class Meta:
    db_table = 'Localconveyence'

class Lodging(VsolvModels):
    tour = models.ForeignKey(TourRequest, on_delete=models.CASCADE, null=True)
    claimreq = models.ForeignKey(ClaimRequest, on_delete=models.CASCADE, null=True)
    Lodge_Homestay = models.CharField(max_length=128, null=True)
    city = models.CharField(max_length=128, null=True)
    metro_nonmetro = models.CharField(max_length=128, null=True)
    fromdate = models.DateTimeField(null=True, blank=True)
    todate = models.DateTimeField(null=True, blank=True)
    billno = models.CharField(max_length=128, null=True)
    noofdays = models.IntegerField(null=True, blank=True)
    vendorname = models.CharField(max_length=128, null=True)
    eligibleamount = models.FloatField()
    Billamountexculdingtax = models.FloatField()
    taxonly = models.FloatField(null=True, blank=True)
    claimedamount = models.FloatField()
    approvedamount = models.FloatField(null=True, blank=True)
    remarks = models.CharField(max_length=128, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class Meta:
    db_table = 'Lodging'

class Misc(VsolvModels):
    tour = models.ForeignKey(TourRequest, on_delete=models.CASCADE, null=True)
    claimreq = models.ForeignKey(ClaimRequest, on_delete=models.CASCADE, null=True)
    description = models.CharField(max_length=128)
    center = models.CharField(max_length=128, null=True, blank=True)
    expreason = models.CharField(max_length=128)
    vendorname = models.CharField(max_length=128,null=True, blank=True)
    vendortype = models.CharField(max_length=128,null=True, blank=True)
    vendorcode = models.CharField(max_length=128,null=True, blank=True)
    bankgstno = models.CharField(max_length=128,null=True, blank=True)
    vendorgstno = models.CharField(max_length=128,null=True, blank=True)
    igst = models.FloatField(null=True, blank=True)
    cgst = models.FloatField(null=True, blank=True)
    sgst = models.FloatField(null=True, blank=True)
    eligibleamount = models.FloatField()
    claimedamount = models.FloatField()
    approvedamount = models.FloatField()
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Meta:
    db_table = 'Misc'

class PackingMoving(VsolvModels):
    tour = models.ForeignKey(TourRequest, on_delete=models.CASCADE, null=True)
    claimreq = models.ForeignKey(ClaimRequest, on_delete=models.CASCADE, null=True)
    twowheelertrans = models.SmallIntegerField(default=1)
    hhgoodstrans = models.SmallIntegerField(default=1)
    transtwowheelerby = models.SmallIntegerField(default=1)
    ibaappvendor = models.CharField(max_length=128,null=True, blank=True)
    totaldisttrans = models.FloatField()
    distinhilly = models.FloatField()
    tonnagehhgood = models.FloatField()
    maxeligton = models.FloatField()
    billedamthhgoodstrans = models.FloatField()
    eligtransamt = models.FloatField()
    transchargesvehicle = models.FloatField()
    vehicletransbydriver = models.SmallIntegerField(default=1)
    traveltimeinhours = models.FloatField()
    daysdrivereng = models.FloatField()
    driverbatta = models.FloatField()
    octroivehicle = models.FloatField()
    breakagecharges = models.FloatField()
    receiptlosses = models.SmallIntegerField(default=1)
    eligbreakagecharge = models.FloatField()
    hsncode = models.CharField(max_length=128,null=True, blank=True)
    vendorname = models.CharField(max_length=128,null=True, blank=True)
    vendortype = models.CharField(max_length=128,null=True, blank=True)
    vendorcode = models.CharField(max_length=128,null=True, blank=True)
    bankgstno = models.CharField(max_length=128,null=True, blank=True)
    vendorgstno = models.CharField(max_length=128,null=True, blank=True)
    igst = models.FloatField(null=True, blank=True)
    cgst = models.FloatField(null=True, blank=True)
    sgst = models.FloatField(null=True, blank=True)
    eligibleamount = models.FloatField()
    claimedamount = models.FloatField()
    approvedamount = models.FloatField()
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Meta:
    db_table = 'PackingMoving'

class Travel(VsolvModels):
    tour = models.ForeignKey(TourRequest, on_delete=models.CASCADE, null=True)
    claimreqgid = models.ForeignKey(ClaimRequest, on_delete=models.CASCADE, null=True)
    traveltype = models.CharField(max_length=128, null=True)
    fromdate = models.DateTimeField(null=True, blank=True)
    fromplace = models.CharField(max_length=128)
    todate = models.DateTimeField()
    toplace = models.CharField(max_length=128)
    billno = models.CharField(max_length=128, null=True)
    totaltkttamt = models.CharField(max_length=128, null=True, blank=True)
    approvedamount = models.FloatField(null=True, blank=True)
    vendorname = models.CharField(max_length=128, null=True)
    tktby = models.CharField(max_length=128, null=True, blank=True)
    actualmode = models.CharField(max_length=128)
    travelclass = models.CharField(max_length=128, null=True, blank=True)
    eligiblemodeoftravel = models.CharField(max_length=128)
    highermodereason = models.CharField(max_length=128)
    prior_permission = models.CharField(max_length=128, null=True)
    remarks = models.CharField(max_length=128, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class Meta:
    db_table = 'Travel'

class associate(VsolvModels):
    tour = models.ForeignKey(TourRequest, on_delete=models.CASCADE, null=True)
    claimreq = models.ForeignKey(ClaimRequest, on_delete=models.CASCADE, null=True)
    description = models.CharField(max_length=128, null=True, blank=True)
    expense = models.CharField(max_length=128, null=True, blank=True)
    # date = models.DateTimeField(null=True, blank=True)
    billno = models.CharField(max_length=128,null=True)
    claimedamount = models.FloatField()
    approvedamount = models.FloatField(null=True, blank=True)
    fromdate = models.DateTimeField(null=True, blank=True)
    todate = models.DateTimeField(null=True, blank=True)
    remarks = models.CharField(max_length=128, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class Meta:
    db_table = 'associate'

class TAScheduler(models.Model):
    tour_id = models.IntegerField()
    tran_id = models.IntegerField()
    tran_type = models.CharField(max_length=64, null=True, blank=True)
    tran_status = models.CharField(max_length=64, null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    created_by = models.IntegerField()
    is_send = models.BooleanField(default=False)
    mail_type = models.CharField(max_length=64, null=True, blank=True)
    flow_condition = models.IntegerField(null=True, blank=True)

class Common_dropdown(VsolvModels):
    name = models.CharField(max_length=128)
    status = models.CharField(max_length=1,default=1)
    entity = models.IntegerField()
    code = models.CharField(max_length=50)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Common_dropdown_details(VsolvModels):
    common_drop_down = models.ForeignKey(Common_dropdown, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    value = models.CharField(max_length=128,default=1)
    status = models.CharField(max_length=1,default=1)
    entity = models.IntegerField()
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)




class Holiday(VsolvModels):
    date = models.DateTimeField(null=True, blank=False)
    holidayname = models.CharField(max_length=128,null=False, blank=False)
    state = models.IntegerField(null=False, blank=False)
    status = models.SmallIntegerField(default=1)
    entity = models.IntegerField(null=True, blank=True)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Meta:
    db_table = 'Holiday'

class Employeemapping(VsolvModels):
    gid = models.AutoField(primary_key=True)
    designation = models.CharField(max_length=45,null=True, blank=True)
    grade = models.CharField(max_length=16,null=True, blank=True)
    orderno = models.IntegerField(null=True, blank=True)
    status = models.SmallIntegerField(default=1)


class Meta:
    db_table = 'Employeemapping'

class ApproverList(VsolvModels):
    employeeid= models.IntegerField(null=True, blank=True)
    branchid = models.IntegerField(null=True, blank=True)
    tourapprove = models.SmallIntegerField(default=0)
    advanceapprove = models.SmallIntegerField(default=0)
    expenseapprove = models.SmallIntegerField(default=0)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Meta:
    db_table = 'ApproverList'

class Allowance(VsolvModels):
    expense = models.ForeignKey(TourExpense, on_delete=models.CASCADE, null=True)
    salarygrade = models.CharField(max_length=16, null=True, blank=True)
    citytype = models.CharField(max_length=128, null=True, blank=True)
    city = models.CharField(max_length=45, null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)
    applicableto = models.CharField(max_length=16, null=True, blank=True)
    effectivefrom = models.DateTimeField(null=True, blank=True)
    effectiveto = models.DateTimeField(null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    entity = models.SmallIntegerField(null=True, blank=True)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class Meta:
    db_table = 'Allowance'

class Gradeeligibility(VsolvModels):
    grade = models.CharField(max_length=8, null=True, blank=True)
    gradelevel = models.CharField(max_length=32, null=True, blank=True)
    travelclass = models.CharField(max_length=45, null=True, blank=True)
    travelmode = models.CharField(max_length=16, null=True, blank=True)
    freight1000 = models.FloatField(default=0)
    freight1001 = models.FloatField(default=0)
    twowheller = models.PositiveSmallIntegerField(default=1)
    hillyregion = models.PositiveSmallIntegerField(default=1)
    tonnagefamily = models.PositiveIntegerField(default=0)
    maxtonnage = models.PositiveIntegerField(default=0)


class Meta:
    db_table = 'Gradeeligibility'

class Holidaydeim(VsolvModels):
    salarygrade = models.CharField(max_length=8)
    city = models.CharField(max_length=45)
    amount = models.FloatField(default=0)
    applicableto = models.CharField(max_length=16)
    status = models.SmallIntegerField(default=1)
    entity = models.SmallIntegerField(null=True)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Meta:
    db_table = 'Holidaydeim'

class Glmapping(VsolvModels):
    glno = models.IntegerField()
    gl_description = models.CharField(max_length=128)
    tourreason = models.CharField(max_length=45)
    gender = models.CharField(max_length=10)
    categorycode = models.IntegerField()
    category_description = models.CharField(max_length=128)
    subcategorycode = models.IntegerField()
    subcategory_description = models.CharField(max_length=128)
    status = models.IntegerField(default=1)
    entity = models.IntegerField()
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Meta:
    db_table = 'Glmapping'

# change apptype
class TourCancel(VsolvModels):
    tour = models.ForeignKey(TourRequest, on_delete=models.CASCADE, null=False,blank=False)
    type = models.CharField(max_length=128, null=False, blank=False)
    status = models.SmallIntegerField(null= True,blank=False)
    created_by = models.IntegerField(null=False,blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True,blank=True)
    updated_date = models.DateTimeField(null=True,blank=True)


class Meta:
    db_table ='TourCancel'
# class Document_type(VsolvModels):
#     code = models.CharField(max_length=128,null=True)
#     file_type = models.CharField(max_length=128,null=True)
#     file_name = models.CharField(max_length=256)
#     description = models.CharField(max_length=512)
#     status = models.SmallIntegerField(default=1)
#     created_by = models.IntegerField(null=False, blank=False)
#     created_date = models.DateTimeField(default=now)
#     updated_by = models.IntegerField(null=True, blank=True)
#     updated_date = models.DateTimeField(null=True, blank=True)

# class Booking_history(VsolvModels):
#     type = models.IntegerField()
#     booking_status=models.IntegerField()
#     ref_id=models.IntegerField()
#     comments=models.CharField(max_length=256,null=True)
#     traveldetails=models.ForeignKey(TourDetail,on_delete=models.CASCADE, null=True)
#     status = models.SmallIntegerField(default=1)
#     created_by = models.IntegerField()
#     created_date = models.DateTimeField(default=now)
#     updated_by = models.IntegerField(null=True, blank=True)
#     updated_date = models.DateTimeField(null=True, blank=True)

class TADocuments(VsolvModels):
    request = models.ForeignKey(TourRequest, on_delete=models.CASCADE)
    file_id = models.CharField(max_length=256, default=-1)
    file_name = models.CharField(max_length=256)
    gen_file_name = models.CharField(max_length=2048)
    ref_id = models.IntegerField(default=-1)
    ref_type = models.SmallIntegerField(default=-1)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

    # detail = models.ForeignKey(TourDetail, on_delete=models.CASCADE)
    # requirement = models.ForeignKey(TravelRequirements, on_delete=models.CASCADE)
    # doctype = models.ForeignKey(Document_type, on_delete=models.CASCADE)
    maker_or_admin=models.SmallIntegerField(default=0)
    detail = models.IntegerField(default=0)
    requirement_type = models.CharField(max_length=256,null=True, blank=True)
    requirement = models.IntegerField(default=0)

class Onbehalfof(VsolvModels):
    employeegid = models.IntegerField(null=True, blank=True)
    branchgid = models.IntegerField(null=True, blank=True)
    onbehalf_employeegid = models.IntegerField(null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Meta:
    db_table ='Onbehalfof'

class Ccbs(VsolvModels):
    tour = models.ForeignKey(TourRequest, on_delete=models.CASCADE, null=False,blank=False)
    requestid = models.IntegerField(null=True, blank=True)
    ccid = models.IntegerField(null=True, blank=True)
    bsid = models.IntegerField(null=True, blank=True)
    percentage = models.FloatField(null=True, blank=True)
    amount = models.FloatField(null=True, blank=True)
    ccbs_type = models.SmallIntegerField(default = 0)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class TransactionComments(VsolvModels):
    request = models.ForeignKey(TourRequest, on_delete=models.CASCADE)
    maker_id = models.IntegerField(default=-1)
    ref_type = models.SmallIntegerField(default=-1)
    viewer_id = models.CharField(default=-1,max_length=256,null=True,blank=True)
    comment = models.TextField(null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    type =  models.IntegerField(default=1)


class Meta:
    db_table = 'TransactionComments'

class Meta:
    db_table ='Ccbs'

class Date_relaxation(VsolvModels):
    tour = models.ForeignKey(TourRequest, on_delete=models.CASCADE, null=False,blank=False)
    status= models.SmallIntegerField(default = 0)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)



class Dependent(VsolvModels):
    depname = models.CharField(max_length=64)
    deprelation = models.CharField(max_length=32,null=True, blank=True)
    depempid= models.IntegerField(null=True, blank=True)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Traveldependent(VsolvModels):
    tour = models.ForeignKey(TourRequest, on_delete=models.CASCADE, null=True)
    claimreq = models.ForeignKey(ClaimRequest, on_delete=models.CASCADE, null=True)
    travel= models.ForeignKey(Travel, on_delete=models.CASCADE, null=True)
    empid= models.IntegerField()
    dependentid= models.IntegerField()
    dependentname= models.CharField(max_length=64)
    deprelation= models.CharField(max_length=32)
    isdepelig= models.SmallIntegerField(null=True, blank=True)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class Client(VsolvModels):
    name=models.CharField(max_length=256)
    code =models.CharField(max_length=256)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Ta_City(VsolvModels):
    code = models.CharField(max_length=8, null=True, blank=True)
    name = models.CharField(max_length=64)
    metro_non=models.IntegerField(null=True)
    state=models.CharField(max_length=64,null=True)
    state_type=models.CharField(max_length=64,null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class Client_mapping(VsolvModels):
    client_id = models.IntegerField()
    detail =  models.ForeignKey(TourDetail,on_delete=models.CASCADE,null=True)
    client_name = models.CharField(max_length=512, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class TravelEditHistory(VsolvModels):
    tour =  models.ForeignKey(TourRequest,on_delete=models.CASCADE,null=True)
    data = models.TextField(null=True, blank=True)
    ref_type = models.SmallIntegerField(default=1)
    action = models.SmallIntegerField(default=1)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

