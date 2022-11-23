import json

class Claimreq_Response:
    id = None
    tourid = None
    expenseid = None
    expensename = None
    requestercomment = None
    approvercomment = None
    invoiceheadergid = None
    eligibleamount = None
    claimedamount = None
    approvedamount = None
    requestdate = None
    empgid = None
    employee_name = None
    approver_name = None
    onbehalfof = None
    status = 1
    reason =None
    approvercomment=None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_requestdate(self, requestdate):
        if requestdate is None:
            self.requestdate=requestdate
        else:
            self.requestdate = requestdate.strftime("%Y-%b-%d %H:%M")

    def set_tour_startdate(self,tour_startdate):
        if tour_startdate is None:
            self.tour_startdate=tour_startdate
        else:
            self.tour_startdate=tour_startdate.strftime("%d-%b-%Y")
    def set_tour_enddate(self,tour_enddate):
        if tour_enddate is None:
            self.tour_enddate=tour_enddate
        else:
            self.tour_enddate=tour_enddate.strftime("%d-%b-%Y")

    def set_empgid(self, empgid):
        self.empgid = empgid
    def set_employee_name(self, employee_name):
        self.employee_name = employee_name
    def set_employee_code(self, employee_code):
        self.employee_code = employee_code
    def set_approver_name(self, approver_name):
        self.approver_name = approver_name
    def set_approver_code(self, approver_code):
        self.approver_code = approver_code
    def set_forwarder_name(self, forwarder_name):
        self.forwarder_name = forwarder_name
    def set_forwarder_code(self, forwarder_code):
        self.forwarder_code = forwarder_code

    def set_onbehalfof(self, onbehalfof):
        self.onbehalfof = onbehalfof
    def set_designation(self, designation):
        self.designation = designation
    def set_emp_grade(self, emp_grade):
        self.emp_grade = emp_grade
    def set_branch_name(self, branch_name):
        self.branch_name = branch_name

    def set_tourid(self, tourid):
        self.tourid = tourid

    def set_expenseid(self, expenseid):
        self.expenseid = expenseid

    def set_expensename(self, expensename):
        self.expensename = expensename
    def set_expensecode(self, expensecode):
        self.expensecode = expensecode
    def set_client_entertainment(self, client_entertainment):
        self.client_entertainment = client_entertainment
    def set_file_count(self, file_count):
        self.file_count = file_count

    def set_requestercomment(self, requestercomment):
        self.requestercomment = requestercomment

    def set_approvercomment(self, approvercomment):
        self.approvercomment = approvercomment

    def set_invoiceheadergid(self, invoiceheadergid):
        self.invoiceheadergid = invoiceheadergid
    def set_crn_no(self, crn_no):
        self.crn_no = crn_no
    def set_payment_status(self, payment_status):
        self.payment_status = payment_status
    def set_reason(self,reason):
        self.reason =reason

    def set_status(self, status):
        self.status = status
    def set_status_id(self, status_id):
        self.status_id = status_id
    def set_claim_status(self, claim_status):
        self.claim_status = claim_status
    def set_claim_status_id(self, claim_status_id):
        self.claim_status_id = claim_status_id

    def set_eligibleamount(self, eligibleamount):
        self.eligibleamount = eligibleamount

    def set_claimedamount(self, claimedamount):
        self.claimedamount = claimedamount

    def set_approvedamount(self, approvedamount):
        self.approvedamount = approvedamount

    def get_id(self):
        return self.id

    def get_tourid(self):
        return self.tourid

    def get_expenseid(self):
        return self.expenseid

    def get_expensename(self):
        return self.expensename

    def get_requestercomment(self):
        return self.requestercomment

    def get_approvercomment(self):
        return self.approvercomment

    def get_invoiceheadergid(self):
        return self.invoiceheadergid

    def get_eligibleamount(self):
        return self.eligibleamount

    def get_claimedamount(self):
        return self.claimedamount

    def get_approvedamount(self):
        return self.approvedamount

    def get_status(self):
        return self.status


class Dailydeim_Response:
    id = None
    tour_id = None
    expensegid = None
    claimreqgid = None
    citytype = None
    visitcity = None
    fromdate = None
    todate = None
    billno = None
    foodallowance = None
    medicalexpense = None
    remarks =None
    noofhours = None
    noofdays = None
    boardingbyorganiser = None
    eligibleamount = None
    claimedamount = None
    approvedamount = None
    requestercomment = None
    status = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_tour_id(self, tour_id):
        self.tour_id = tour_id

    def set_expensegid(self, expensegid):
        self.expensegid = expensegid

    def set_claimreqgid(self, claimreqgid):
        self.claimreqgid = claimreqgid

    def set_citytype(self, citytype):
        self.citytype = citytype

    def set_foodallowance(self, foodallowance):
        self.foodallowance = foodallowance

    def set_medicalexpense(self, medicalexpense):
        self.medicalexpense = medicalexpense

    def set_visitcity(self, visitcity):
        self.visitcity = visitcity

    def set_fromdate(self, fromdate):
        if fromdate != None:
            fromdate = fromdate.strftime("%Y-%b-%d %H:%M")
            self.fromdate = fromdate
        else:
            self.fromdate = None

    def set_todate(self, todate):
        if todate != None:
            todate = todate.strftime("%Y-%b-%d %H:%M")
            self.todate = todate
        else:
            self.todate = None

    def set_billno(self, billno):
        self.billno = billno

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_noofhours(self, noofhours):
        self.noofhours = noofhours

    def set_noofdays(self, noofdays):
        self.noofdays = noofdays

    def set_boardingbyorganiser(self, boardingbyorganiser):
        self.boardingbyorganiser = boardingbyorganiser

    def set_eligibleamount(self, eligibleamount):
        self.eligibleamount = eligibleamount

    def set_claimedamount(self, claimedamount):
        self.claimedamount = claimedamount

    def set_approvedamount(self, approvedamount):
        self.approvedamount = approvedamount

    def set_status(self, status):
        self.status = status

    def set_requestercomment(self, requestercomment):
        self.requestercomment = requestercomment

    def set_exp_name(self, exp_name):
        self.exp_name = exp_name

    def set_exp_id(self, exp_id):
        self.exp_id = exp_id

    def get_id(self):
        return self.id

    def get_tour_id(self):
        return self.tour_id

    def get_expensegid(self):
        return self.expensegid

    def get_citytype(self):
        return self.citytype

    def get_visitcity(self):
        return self.visitcity

    def get_from_date(self):
        return self.from_date

    def get_to_date(self):
        return self.set_to_date

    def get_noofdays(self):
        return self.noofdays

    def get_noofhours(self):
        return self.noofhours

    def get_boardingbyorganiser(self):
        return self.boardingbyorganiser

    def get_eligibleamount(self):
        return self.eligibleamount

    def get_claimedamount(self):
        return self.claimedamount

    def get_approvedamount(self):
        return self.approvedamount

    def get_requestercomment(self):
        return self.requestercomment

    def get_status(self):
        return self.status

class Incidental_Response:
    id= None
    tourid = None
    claimreqid = None
    code = None
    samedayreturn = None
    travelhours = None
    singlefare = None
    expenses = None
    vendorname = None
    vendortype = None
    vendorcode = None
    gstno = None
    gstrate = None
    eligibleamount = None
    claimedamount = None
    approvedamount = None
    status = 1

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_tourid(self, tourid):
        self.tourid = tourid

    def set_claimreqid(self, claimreqid):
        self.claimreqid = claimreqid

    def set_travel_mode(self, code):
        self.travel_mode = code

    def set_samedayreturn(self, samedayreturn):
        self.same_day_return = samedayreturn

    def set_samedayreturn_name(self, samedayreturn_name):
        self.samedayreturn_name = samedayreturn_name

    def set_travelhours(self, travelhours):
        self.travel_hours = travelhours

    def set_singlefare(self, singlefare):
        self.single_fare = singlefare

    def set_expenses(self, expenses):
        self.expenses = expenses

    def set_vendorname(self, vendorname):
        self.vendorname = vendorname

    def set_vendortype(self, vendortype):
        self.vendortype = vendortype

    def set_vendorcode(self, vendorcode):
        self.vendorcode = vendorcode

    def set_gstno(self, gstno):
        self.gstno = gstno

    def set_status(self, status):
        self.status = status
    def set_exp_name(self, exp_name):
        self.exp_name = exp_name
    def set_exp_id(self, exp_id):
        self.exp_id = exp_id

    def set_gstrate(self, gstrate):
        self.gstrate = gstrate

    def set_eligibleamount(self, eligibleamount):
        self.eligibleamount = eligibleamount

    def set_claimedamount(self, claimedamount):
        self.claimedamount = claimedamount

    def set_approvedamount(self, approvedamount):
        self.approvedamount = approvedamount

    def get_id(self):
        return self.id

    def get_tourid(self):
        return self.tourid

    def get_claimreqid(self):
        return self.claimreqid

    def get_code(self):
        return self.code

    def get_samedayreturn(self):
        return self.samedayreturn

    def get_travelhours(self):
        return self.travelhours

    def get_singlefare(self):
        return self.singlefare

    def get_expenses(self):
        return self.expenses

    def get_vendorname(self):
        return self.vendorname

    def get_vendortype(self):
        return self.vendortype

    def get_vendorcode(self):
        return self.vendorcode

    def get_gstno(self):
        return self.gstno

    def get_gstrate(self):
        return self.gstrate

    def get_eligibleamount(self):
        return self.eligibleamount

    def get_claimedamount(self):
        return self.claimedamount

    def get_approvedamount(self):
        return self.approvedamount

    def get_status(self):
        return self.status

class Localconveyence_Response:
    id = None
    tour_id = None
    claimreqgid = None
    modeoftravel = None
    fromplace = None
    toplace = None
    distance = None
    fromdate = None
    todtae = None
    remarks = None
    billno = None
    eligibleamount = None
    claimedamount = None
    approvedamount = None
    status = None
    expenseid = None
    requestercomment = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_tour_id(self, tour_id):
        self.tour_id = tour_id

    def set_claimreqgid(self, claimreqgid):
        self.claimreqgid = claimreqgid
    def set_expensegid(self, expensegid):
        self.expensegid = expensegid

    def set_modeoftravel(self, modeoftravel):
        self.modeoftravel = modeoftravel

    def set_fromplace(self, fromplace):
        self.fromplace = fromplace

    def set_toplace(self, toplace):
        self.toplace = toplace

    def set_distance(self, distance):
        self.distance = distance

    def set_fromdate(self, fromdate):
        if fromdate != None:
            fromdate = fromdate.strftime("%Y-%b-%d %H:%M")
            self.fromdate = fromdate
        else:
            self.fromdate = None

    def set_todate(self, todate):
        if todate != None:
            todate = todate.strftime("%Y-%b-%d %H:%M")
            self.todate = todate
        else:
            self.todate = None

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_billno(self, billno):
        self.billno = billno

    def set_status(self, status):
        self.status = status

    def set_eligibleamount(self, eligibleamount):
        self.eligibleamount = eligibleamount

    def set_claimedamount(self, claimedamount):
        self.claimedamount = claimedamount

    def set_approvedamount(self, approvedamount):
        self.approvedamount = approvedamount

    def set_requestercomment(self, requestercomment):
        self.requestercomment = requestercomment

    def set_exp_name(self, exp_name):
        self.exp_name = exp_name

    def set_exp_id(self, exp_id):
        self.exp_id = exp_id

    def get_expenseid(self):
        return self.expenseid

    def get_requestercomment(self):
        return self.requestercomment

    def get_id(self):
        return self.id

    def get_tour_id(self):
        return self.tour_id

    def get_claimreqgid(self):
        return self.claimreqgid

    def get_expensegid(self):
        return self.expensegid

    def get_modeoftravel(self):
        return self.modeoftravel

    def get_fromplace(self):
        return self.fromplace

    def get_toplace(self):
        return self.toplace

    def get_distance(self):
        return self.distance

    def get_date(self):
        return self.date

    def get_eligibleamount(self):
        return self.eligibleamount

    def get_claimedamount(self):
        return self.claimedamount

    def get_approvedamount(self):
        return self.approvedamount

    def get_approvedamount(self):
        return self.approvedamount

    def get_status(self):
        return self.status

class Lodging_Response:
    id = None
    tour_id = None
    claimreqgid = None
    Lodge_Homestay = None
    metro_nonmetro = None
    fromdate = None
    todate = None
    billno =None
    remarks = None
    vendorname = None
    noofdays = None
    city = None
    eligibleamount = None
    Billamountexculdingtax = None
    approvedamount = None
    taxonly = None
    claimedamount = None
    status = None
    expensegid = None
    requestercomment = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_tour_id(self, tour_id):
        self.tour_id = tour_id

    def set_claimreqgid(self, claimreqgid):
        self.claimreqgid = claimreqgid

    def set_Lodge_Homestay(self, Lodge_Homestay):
        self.Lodge_Homestay = Lodge_Homestay

    def set_metro_nonmetro(self, metro_nonmetro):
        self.metro_nonmetro = metro_nonmetro

    def set_fromdate(self, fromdate):
        if fromdate != None:
            fromdate = fromdate.strftime("%Y-%b-%d %H:%M")
            self.fromdate = fromdate
        else:
            self.fromdate = None

    def set_todate(self, todate):
        if todate != None:
            todate = todate.strftime("%Y-%b-%d %H:%M")
            self.todate = todate
        else:
            self.todate = None

    def set_billno(self, billno):
        self.billno = billno

    def set_vendorname(self, vendorname):
        self.vendorname = vendorname

    def set_city(self, city):
        self.city = city

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_noofdays(self, noofdays):
        self.noofdays = noofdays

    def set_eligibleamount(self, eligibleamount):
        self.eligibleamount = eligibleamount

    def set_approvedamount(self, approvedamount):
        self.approvedamount = approvedamount

    def set_Billamountexculdingtax(self, Billamountexculdingtax):
        self.Billamountexculdingtax = Billamountexculdingtax

    def set_taxonly(self, taxonly):
        self.taxonly = taxonly

    def set_claimedamount(self, claimedamount):
        self.claimedamount = claimedamount

    def set_exp_name(self, exp_name):
        self.exp_name = exp_name

    def set_exp_id(self, exp_id):
        self.exp_id = exp_id

    def set_status(self, status):
        self.status = status

    def set_expensegid(self, expensegid):
        self.expensegid = expensegid

    def set_requestercomment(self, requestercomment):
        self.requestercomment = requestercomment

    def get_expensegid(self):
        return self.expensegid

    def get_requestercomment(self):
        return self.requestercomment

    def get_id(self):
        return self.id

    def get_tour_id(self):
        return self.tour_id

    def get_claimreqgid(self):
        return self.claimreqgid

    def get_Lodge_Homestay(self):
        return self.Lodge_Homestay

    def get_vendorname(self):
        return self.vendorname

    def get_metro_nonmetro(self):
        return self.metro_nonmetro

    def get_from_date(self):
        return self.from_date

    def get_to_date(self):
        return self.to_date

    def get_noofdays(self):
        return self.noofdays

    def get_eligibleamount(self):
        return self.eligibleamount

    def get_approvedamount(self):
        return self.approvedamount

    def get_Billamountexculdingtax(self):
        return self.Billamountexculdingtax

    def get_taxonly(self):
        return self.taxonly

    def get_claimedamount(self):
        return self.claimedamount

    def get_status(self):
        return self.status

class Misc_Response:
    id= None
    tourid = None
    claimreqid = None
    description = None
    expreason = None
    vendorname = None
    vendortype = None
    vendorcode = None
    bankgstno = None
    vendorgstno = None
    igst = None
    cgst = None
    sgst = None
    eligibleamount = None
    claimedamount = None
    approvedamount = None
    status = 1

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_tourid(self, tourid):
        self.tourgid = tourid

    def set_claimreqid(self, claimreqid):
        self.claimreqid = claimreqid

    def set_description(self, description):
        self.description = description

    def set_expreason(self, expreason):
        self.expreason = expreason

    def set_vendorname(self, vendorname):
        self.vendorname = vendorname

    def set_vendortype(self, vendortype):
        self.vendortype = vendortype

    def set_vendorcode(self, vendorcode):
        self.vendorcode = vendorcode

    def set_bankgstno(self, bankgstno):
        self.bankgstno = bankgstno

    def set_vendorgstno(self, vendorgstno):
        self.vendorgstno = vendorgstno

    def set_status(self, status):
        self.status = status
    def set_center(self, center):
        self.center = center
    def set_exp_name(self, exp_name):
        self.exp_name = exp_name
    def set_exp_id(self, exp_id):
        self.exp_id = exp_id

    def set_igst(self, igst):
        self.igst = igst

    def set_cgst(self, cgst):
        self.cgst = cgst

    def set_sgst(self, sgst):
        self.sgst = sgst

    def set_eligibleamount(self, eligibleamount):
        self.eligibleamount = eligibleamount

    def set_claimedamount(self, claimedamount):
        self.claimedamount = claimedamount

    def set_approvedamount(self, approvedamount):
        self.approvedamount = approvedamount

    def get_id(self):
        return self.id

    def get_tourid(self):
        return self.tourid

    def get_claimreqid(self):
        return self.claimreqid

    def get_description(self):
        return self.description

    def get_expreason(self):
        return self.expreason

    def get_vendorname(self):
        return self.vendorname

    def get_vendortype(self):
        return self.vendortype

    def get_vendorcode(self):
        return self.vendorcode

    def get_bankgstno(self):
        return self.bankgstno

    def get_vendorgstno(self):
        return self.vendorgstno

    def get_igst(self):
        return self.igst

    def get_cgst(self):
        return self.cgst

    def get_sgst(self):
        return self.sgst

    def get_eligibleamount(self):
        return self.eligibleamount

    def get_claimedamount(self):
        return self.claimedamount

    def get_approvedamount(self):
        return self.approvedamount

    def get_status(self):
        return self.status

class PackingMoving_Response:
    id= None
    tourid = None
    claimreqid = None
    twowheelertrans = None
    hhgoodstrans = None
    transtwowheelerby = None
    ibaappvendor = None
    totaldisttrans = None
    distinhilly = None
    tonnagehhgood = None
    maxeligton = None
    billedamthhgoodstrans = None
    eligtransamt = None
    transchargesvehicle = None
    vehicletransbydriver = None
    traveltimeinhours = None
    daysdrivereng = None
    driverbatta = None
    octroivehicle = None
    breakagecharges = None
    receiptlosses = None
    eligbreakagecharge = None
    hsncode = None
    vendorname = None
    vendortype = None
    vendorcode = None
    bankgstno = None
    vendorgstno = None
    igst = None
    cgst = None
    sgst = None
    eligibleamount = None
    claimedamount = None
    approvedamount = None
    status = 1

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_tourid(self, tourid):
        self.tourgid = tourid

    def set_claimreqid(self, claimreqid):
        self.claimreqid = claimreqid

    def set_twowheelertrans(self, twowheelertrans):
        self.twowheelertrans = twowheelertrans
    def set_twowheelertrans_name(self, twowheelertrans_name):
        self.twowheelertrans_name = twowheelertrans_name

    def set_hhgoodstrans(self, hhgoodstrans):
        self.hhgoodstrans = hhgoodstrans
    def set_hhgoodstrans_name(self, hhgoodstrans_name):
        self.hhgoodstrans_name = hhgoodstrans_name

    def set_transtwowheelerby(self, transtwowheelerby):
        self.transtwowheelerby = transtwowheelerby
    def set_transtwowheelerby_name(self, transtwowheelerby_name):
        self.transtwowheelerby_name = transtwowheelerby_name

    def set_ibaappvendor(self, ibaappvendor):
        self.ibaappvendor = ibaappvendor

    def set_totaldisttrans(self, totaldisttrans):
        self.totaldisttrans = totaldisttrans

    def set_distinhilly(self, distinhilly):
        self.distinhilly = distinhilly

    def set_tonnagehhgood(self, tonnagehhgood):
        self.tonnagehhgood = tonnagehhgood

    def set_maxeligton(self, maxeligton):
        self.maxeligton = maxeligton

    def set_billedamthhgoodstrans(self, billedamthhgoodstrans):
        self.billedamthhgoodstrans = billedamthhgoodstrans

    def set_eligtransamt(self, eligtransamt):
        self.eligtransamt = eligtransamt

    def set_transchargesvehicle(self, transchargesvehicle):
        self.transchargesvehicle = transchargesvehicle

    def set_vehicletransbydriver(self, vehicletransbydriver):
        self.vehicletransbydriver = vehicletransbydriver
    def set_vehicletransbydriver_name(self, vehicletransbydriver_name):
        self.vehicletransbydriver_name = vehicletransbydriver_name

    def set_traveltime(self, traveltime):
        self.traveltime = traveltime

    def set_daysdrivereng(self, daysdrivereng):
        self.daysdrivereng = daysdrivereng

    def set_driverbatta(self, driverbatta):
        self.driverbatta = driverbatta

    def set_octroivehicle(self, octroivehicle):
        self.octroivehicle = octroivehicle

    def set_breakagecharges(self, breakagecharges):
        self.breakagecharges = breakagecharges

    # def set_receiptloss(self, receiptlosses):
    #     self.receipt_losses = receiptlosses
    def set_receipt_loss(self, receipt_loss):
        self.receipt_loss = receipt_loss
    def set_receiptloss_name(self, receiptlosses_name):
        self.receipt_losses_name = receiptlosses_name

    def set_eligbreakagecharge(self, eligbreakagecharge):
        self.eligbreakagecharge = eligbreakagecharge

    def set_hsncode(self, hsncode):
        self.hsncode = hsncode
    def set_hsn_data(self, hsn_data):
        self.hsn_data = hsn_data

    def set_vendorname(self, vendorname):
        self.vendorname = vendorname

    def set_vendortype(self, vendortype):
        self.vendortype = vendortype

    def set_vendorcode(self, vendorcode):
        self.vendorcode = vendorcode

    def set_bankgstno(self, bankgstno):
        self.bankgstno = bankgstno

    def set_vendorgstno(self, vendorgstno):
        self.vendorgstno = vendorgstno

    def set_status(self, status):
        self.status = status
    def set_exp_name(self, exp_name):
        self.exp_name = exp_name
    def set_exp_id(self, exp_id):
        self.exp_id = exp_id

    def set_igst(self, igst):
        self.igst = igst

    def set_cgst(self, cgst):
        self.cgst = cgst

    def set_sgst(self, sgst):
        self.sgst = sgst

    def set_eligibleamount(self, eligibleamount):
        self.eligibleamount = eligibleamount

    def set_claimedamount(self, claimedamount):
        self.claimedamount = claimedamount

    def set_approvedamount(self, approvedamount):
        self.approvedamount = approvedamount

    def get_id(self):
        return self.id

    def get_tourid(self):
        return self.tourid

    def get_claimreqid(self):
        return self.claimreqid

    def get_twowheelertrans(self):
        return self.twowheelertrans

    def get_hhgoodstrans(self):
        return self.hhgoodstrans

    def get_transtwowheelerby(self):
        return self.transtwowheelerby

    def get_ibaappvendor(self):
        return self.ibaappvendor

    def get_totaldisttrans(self):
        return self.totaldisttrans

    def get_distinhilly(self):
        return self.distinhilly

    def get_tonnagehhgood(self):
        return self.tonnagehhgood

    def get_maxeligton(self):
        return self.maxeligton

    def get_billedamthhgoodstrans(self):
        return self.billedamthhgoodstrans

    def get_eligtransamt(self):
        return self.eligtransamt

    def get_transchargesvehicle(self):
        return self.transchargesvehicle

    def get_vehicletransbydriver(self):
        return self.vehicletransbydriver

    def get_traveltimeinhours(self):
        return self.traveltimeinhours

    def get_daysdrivereng(self):
        return self.daysdrivereng

    def get_driverbatta(self):
        return self.daysdrivereng

    def get_octroivehicle(self):
        return self.daysdrivereng

    def get_breakagecharges(self):
        return self.daysdrivereng

    def get_receiptlosses(self):
        return self.daysdrivereng

    def get_eligbreakagecharge(self):
        return self.daysdrivereng

    def get_hsncode(self):
        return self.daysdrivereng

    def get_vendorname(self):
        return self.vendorname

    def get_vendortype(self):
        return self.vendortype

    def get_vendorcode(self):
        return self.vendorcode

    def get_bankgstno(self):
        return self.bankgstno

    def get_vendorgstno(self):
        return self.vendorgstno

    def get_igst(self):
        return self.igst

    def get_cgst(self):
        return self.cgst

    def get_sgst(self):
        return self.sgst

    def get_eligibleamount(self):
        return self.eligibleamount

    def get_claimedamount(self):
        return self.claimedamount

    def get_approvedamount(self):
        return self.approvedamount

    def get_status(self):
        return self.status

class Travel_Response:
    id = None
    tour_id = None
    claimreqgid = None
    traveltype = None
    fromdate = None
    fromplace = None
    todate = None
    toplace = None
    remarks =None
    totaltkttamt = None
    vendorname = None
    tktby = None
    approvedamount = None
    claimedamount = None
    actualmode = None
    travelclass = None
    eligiblemodeoftravel = None
    highermodereason = None
    prior_permission = None
    status = None
    expensegid = None
    requestercomment = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_tour_id(self, tour_id):
        self.tour_id = tour_id

    def set_claimreqgid(self, claimreqgid):
        self.claimreqgid = claimreqgid

    def set_traveltype(self, traveltype):
        self.traveltype = traveltype

    def set_fromdate(self, fromdate):
        if fromdate != None:
            fromdate = fromdate.strftime("%Y-%b-%d %H:%M")
            self.fromdate = fromdate
        else:
            self.fromdate = None

    def set_todate(self, todate):
        if todate != None:
            todate = todate.strftime("%Y-%b-%d %H:%M")
            self.todate = todate
        else:
            self.todate = None

    def set_claimedamount(self, claimedamount):
        self.claimedamount = claimedamount

    def set_fromplace(self, fromplace):
        self.fromplace = fromplace

    def set_vendorname(self, vendorname):
        self.vendorname = vendorname

    def set_toplace(self, toplace):
        self.toplace = toplace

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_billno(self, billno):
        self.billno = billno

    def set_totaltkttamt(self, totaltkttamt):
        self.totaltkttamt = totaltkttamt

    def set_tktby(self, tktby):
        self.tktby = tktby

    def set_approvedamount(self, approvedamount):
        self.approvedamount = approvedamount

    def set_actualmode(self, actualmode):
        self.actualmode = actualmode

    def set_travelclass(self, travelclass):
        self.travelclass = travelclass

    def set_eligiblemodeoftravel(self, eligiblemodeoftravel):
        self.eligiblemodeoftravel = eligiblemodeoftravel

    def set_highermodereason(self, highermodereason):
        self.highermodereason = highermodereason

    def set_prior_permission(self, prior_permission):
        self.prior_permission = prior_permission

    def set_status(self, status):
        self.status = status

    def set_expensegid(self, expensegid):
        self.expensegid = expensegid

    def set_requestercomment(self, requestercomment):
        self.requestercomment = requestercomment

    def set_exp_name(self, exp_name):
        self.exp_name = exp_name

    def set_exp_id(self, exp_id):
        self.exp_id = exp_id

    def get_expensegid(self):
        return self.expensegid

    def get_requestercomment(self):
        return self.requestercomment

    def get_id(self):
        return self.id

    def get_tour_id(self):
        return self.tour_id

    def get_claimreqgid(self):
        return self.claimreqgid

    def get_traveltype(self):
        return self.traveltype

    def get_fromdate(self):
        return self.fromdate

    def get_fromplace(self):
        return self.fromplace

    def get_todate(self):
        return self.todate

    def get_vendorname(self):
        return self.vendorname

    def get_toplace(self):
        return self.toplace

    def get_remarks(self):
        return self.remarks

    def get_totaltkttamt(self):
        return self.totaltkttamt

    def set_claimedamount(self, claimedamount):
        self.claimedamount = claimedamount

    def get_approvedamount(self):
        return self.approvedamount

    def get_tktby(self):
        return self.tktby

    def get_actualmode(self):
        return self.actualmode

    def get_travelclass(self):
        return self.travelclass

    def get_eligiblemodeoftravel(self):
        return self.eligiblemodeoftravel

    def get_highermodereason(self):
        return self.highermodereason

    def get_prior_permission(self):
        return self.prior_permission

    def get_status(self):
        return self.status


class associate_Response:
    id = None
    tour_id = None
    claimreqgid = None
    description = None
    expense = None
    billno = None
    fromdate = None
    todate = None
    remarks = None
    claimedamount = None
    approvedamount = None
    expensegid = None
    status = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_tour_id(self, tour_id):
        self.tour_id = tour_id

    def set_claimreqgid(self, claimreqgid):
        self.claimreqgid = claimreqgid

    def set_expensegid(self, expensegid):
        self.expensegid = expensegid

    def set_description(self, description):
        self.description = description

    def set_expense(self, expense):
        self.expense = expense

    def set_fromdate(self, fromdate):
        if fromdate != None:
            fromdate = fromdate.strftime("%Y-%b-%d %H:%M")
            self.fromdate = fromdate
        else:
            self.fromdate = None

    def set_todate(self, todate):
        if todate != None:
            todate = todate.strftime("%Y-%b-%d %H:%M")
            self.todate = todate
        else:
            self.todatee = None

    def set_billno(self, billno):
        self.billno = billno

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_requestercomment(self, requestercomment):
        self.requestercomment = requestercomment

    def set_claimedamount(self, claimedamount):
        self.claimedamount = claimedamount

    def set_approvedamount(self, approvedamount):
        self.approvedamount = approvedamount

    def set_status(self, status):
        self.status = status

    def set_exp_name(self, exp_name):
        self.exp_name = exp_name

    def set_exp_id(self, exp_id):
        self.exp_id = exp_id

    def get_expensegid(self):
        return self.expensegid

    def get_requestercomment(self):
        return self.requestercomment

    def get_id(self):
        return self.id

    def get_tour_id(self):
        return self.tour_id

    def get_claimreq_id(self):
        return self.claimreq_id

    def get_description(self):
        return self.description

    def get_expense(self):
        return self.expense

    def get_date(self):
        return self.date

    def get_billno(self):
        return self.billno

    def get_claimedamount(self):
        return self.claimedamount

    def get_approvedamount(self):
        return self.approvedamount

    def get_status(self):
        return self.status



#commit
class Common_dropdown_Response:
    name= None
    value = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_name(self, name):
        self.name = name

    def set_value(self, value):
        self.value = value