import json
class Report_res:
    requestno= None
    requestdate= None
    empgid= None
    empdesignation= None
    empgrade=None
    empbranchgid=None
    reason=None
    permittedby=None
    startdate=None
    enddate=None
    durationdays=None
    eligiblemodeoftravel=None
    ordernoremarks=None
    onbehalfof=None
    advance_status=None
    claim_status=None
    tour_status=None
    starting_point=None
    place_of_visit=None
    purpose_of_visit=None
    employee=None
    tourno=None
    reqamount=None
    appamount=None
    invoiceheadergid=None
    status=None
    eligibleamount=None
    claimedamount=None
    approvedamount=None
    total_amount=None
    travel_amount=None
    dailydeim_amount=None
    incidental_amount=None
    local_amount=None
    lodging_amount=None
    misc_amount=None
    packing_amount=None
    pending_days=None
    approvedby=None
    advanceamount=None
    employee_name=None
    employee_code=None
    branch_name=None
    branch_code=None
    official=None
    client=None
    international_travel=None

    def set_employee_name(self,employee_name):
        self.employee_name=employee_name
    def set_employee_code(self,employee_code):
        self.employee_code=employee_code
    def set_client(self,client):
        self.client=client
    def set_international_travel(self,international_travel):
        self.international_travel=international_travel
    def set_requestno(self,requestno):
        self.requestno=requestno
    def set_tourid(self,tourid):
        self.tourid=tourid
    def set_requestdate(self,requestdate):
        if requestdate is None:
            self.requestdate=requestdate
        else:
            self.requestdate=requestdate.strftime("%d-%b-%Y")
            self.requestdate_ms =round(requestdate.timestamp() * 1000)
    def set_empgid(self,empgid):
        self.empgid=empgid
    def set_empdesignation(self,empdesignation):
        self.empdesignation=empdesignation
    def set_empgrade(self,empgrade):
        self.empgrade=empgrade
    def set_empbranchgid(self,empbranchgid):
        self.empbranchgid=empbranchgid
    def set_detail(self,detail):
        self.detail=detail
    def set_reason(self,reason):
        self.reason=reason
    def set_permittedby(self,permittedby):
        self.permittedby=permittedby
    def set_permittedby_name(self,permittedby_name):
        self.permittedby_name = permittedby_name

    def set_permittedby_code(self, permittedby_code):
        self.permittedby_code = permittedby_code

    def set_startdate(self,startdate):
        if startdate is None:
            self.startdate=startdate
        else:
            self.startdate=startdate.strftime("%d-%b-%Y")
            self.startdate_ms =round(startdate.timestamp() * 1000)
    def set_enddate(self,enddate):
        if enddate is None:
            self.enddate=enddate
        else:
            self.enddate=enddate.strftime("%d-%b-%Y")
            self.enddate_ms =round(enddate.timestamp() * 1000)

    def set_tour_startdate(self,tour_startdate):
        if tour_startdate is None:
            self.tour_startdate=tour_startdate
        else:
            self.tour_startdate=tour_startdate.strftime("%d-%b-%Y")
            self.tour_startdate_ms =round(tour_startdate.timestamp() * 1000)
    def set_tour_enddate(self,tour_enddate):
        if tour_enddate is None:
            self.tour_enddate=tour_enddate
        else:
            self.tour_enddate=tour_enddate.strftime("%d-%b-%Y")
            self.tour_enddate_ms =round(tour_enddate.timestamp() * 1000)
    def set_durationdays(self,durationdays):
        self.durationdays=durationdays
    def set_eligiblemodeoftravel(self,eligiblemodeoftravel):
        self.eligiblemodeoftravel=eligiblemodeoftravel
    def set_ordernoremarks(self,ordernoremarks):
        self.ordernoremarks=ordernoremarks
    def set_onbehalfof(self,onbehalfof):
        self.onbehalfof=onbehalfof
    def set_advance_status(self,advance_status):
        self.advance_status=advance_status
    def set_claim_status(self,claim_status):
        self.claim_status=claim_status
    def set_tour_status(self,tour_status):
        self.tour_status=tour_status
    def set_starting_point(self,starting_point):
        self.starting_point=starting_point
    def set_place_of_visit(self,place_of_visit):
        self.place_of_visit=place_of_visit
    def set_purpose_of_visit(self,purpose_of_visit):
        self.purpose_of_visit=purpose_of_visit
    def set_employee(self,employee):
        self.employee=employee
    def set_tourno(self,tourno):
        self.tourno=tourno
    def set_official(self,official):
        self.official=official
    def set_requirement(self,requirement):
        self.requirement=requirement
    def set_reqamount(self,reqamount):
        self.reqamount=reqamount
    def set_appamount(self,appamount):
        self.appamount=appamount
    def set_advanceamount(self,advanceamount):
        self.advanceamount=advanceamount
    def set_invoiceheadergid(self,invoiceheadergid):
        self.invoiceheadergid=invoiceheadergid
    def set_status(self,status):
        self.status=status
    def set_eligibleamount(self,eligibleamount):
        self.eligibleamount=eligibleamount
    def set_claimedamount(self,claimedamount):
        self.claimedamount=claimedamount
    def set_approvedamount(self,approvedamount):
        self.approvedamount=approvedamount
    def set_total_amount(self,total_amount):
        self.total_amount=total_amount
    def set_travel_amount(self,travel_amount):
        self.travel_amount=travel_amount
    def set_dailydeim_amount(self,dailydeim_amount):
        self.dailydeim_amount=dailydeim_amount
    def set_incidental_amount(self,incidental_amount):
        self.incidental_amount=incidental_amount
    def set_local_amount(self,local_amount):
        self.local_amount=local_amount
    def set_lodging_amount(self,lodging_amount):
        self.lodging_amount=lodging_amount
    def set_misc_amount(self,misc_amount):
        self.misc_amount=misc_amount
    def set_packing_amount(self,packing_amount):
        self.packing_amount=packing_amount
    def set_pending_days(self,pending_days):
        self.pending_days=pending_days
    def set_approvedby(self,approvedby):
        self.approvedby=approvedby

    def set_approvedby_name(self,approvedby_name):
        self.approvedby_name=approvedby_name
    def set_approvedby_code(self, approvedby_code):
        self.approvedby_code = approvedby_code

    def set_branch_name(self,branch_name):
        self.branch_name=branch_name
    def set_branch_code(self,branch_code):
        self.branch_code=branch_code
    def set_travel_no(self,travel_no):
        self.travel_no=travel_no
    def set_ccbs_data(self,ccbs_data):
        self.ccbs_data=ccbs_data
    def set_expense_name(self,expense_name):
        self.expense_name=expense_name
    def set_claimed_amount(self,claimed_amount):
        self.claimed_amount=claimed_amount
    def set_comment(self,comment):
        self.comment=comment

    one_two = None
    three_ten = None
    eleven_thirty = None
    thirtyone_sixty = None
    above_sixty = None
    branchgid=None
    def set_one_two(self,one_two):
        self.one_two=one_two
    def set_three_ten(self,three_ten):
        self.three_ten=three_ten
    def set_eleven_thirty(self,eleven_thirty):
        self.eleven_thirty=eleven_thirty
    def set_thirtyone_sixty(self,thirtyone_sixty):
        self.thirtyone_sixty=thirtyone_sixty
    def set_above_sixty(self,above_sixty):
        self.above_sixty=above_sixty



    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)


