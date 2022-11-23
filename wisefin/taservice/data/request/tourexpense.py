import json
from taservice.util.ta_util import Status


class Dailydeim_Request:
    id = None
    tour_id = None
    expensegid = None
    claimreqgid = None
    citytype = None
    visitcity = None
    fromdate = None
    todate = None
    billno = None
    remarks = None
    noofhours = None
    noofdays = None
    boardingbyorganiser = None
    eligibleamount = None
    claimedamount = None
    approvedamount = None
    requestercomment = None
    status = None

    def __init__(self, tour_obj):
        if 'id' in tour_obj:
            self.id = tour_obj['id']
        if 'tour_id' in tour_obj:
            self.tour_id = tour_obj['tour_id']
        if 'expensegid' in tour_obj:
            self.expensegid = tour_obj['expensegid']
        if 'claimreqgid' in tour_obj:
            self.claimreqgid = tour_obj['claimreqgid']
        if 'citytype' in tour_obj:
            self.citytype = tour_obj['citytype']
        if 'visitcity' in tour_obj:
            self.visitcity = tour_obj['visitcity']
        if 'fromdate' in tour_obj:
            self.fromdate = tour_obj['fromdate']
        if 'todate' in tour_obj:
            self.todate = tour_obj['todate']
        if 'medicalexpense' in tour_obj:
            self.medicalexpense = tour_obj['medicalexpense']
        if 'foodallowance' in tour_obj:
            self.foodallowance = tour_obj['foodallowance']
        if 'billno' in tour_obj:
            self.billno = tour_obj['billno']
        if 'remarks' in tour_obj:
            self.remarks = tour_obj['remarks']
        if 'noofhours' in tour_obj:
            self.noofhours = tour_obj['noofhours']
        if 'noofdays' in tour_obj:
            self.noofdays = tour_obj['noofdays']
        if 'boardingbyorganiser' in tour_obj:
            self.boardingbyorganiser = tour_obj['boardingbyorganiser']
        if 'eligibleamount' in tour_obj:
            self.eligibleamount = tour_obj['eligibleamount']
        if 'claimedamount' in tour_obj:
            self.claimedamount = tour_obj['claimedamount']
        if 'approvedamount' in tour_obj:
            self.approvedamount = tour_obj['approvedamount']
        if 'requestercomment' in tour_obj:
            self.requestercomment = tour_obj['requestercomment']
        if 'status' in tour_obj:
            self.status = tour_obj['status']

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

    def set_visitcity(self, visitcity):
        self.visitcity = visitcity

    def set_citytype(self, citytype):
        self.citytype = citytype

    def set_billno(self, billno):
        self.billno = billno

    def set_foodallowance(self, foodallowance):
        self.foodallowance = foodallowance

    def set_medicalexpense(self, medicalexpense):
        self.medicalexpense = medicalexpense

    def set_fromdate(self, fromdate):
        self.fromdate = fromdate

    def set_todate(self, todate):
        self.todate = todate

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

    def get_id(self):
        return self.id

    def get_tour_id(self):
        return self.tour_id

    def get_expensegid(self):
        return self.expensegid

    def get_billno(self):
        return self.billno

    def get_citytype(self):
        return self.citytype

    def get_visitcity(self):
        return self.visitcity

    def get_fromdate(self):
        return self.fromdate

    def get_todate(self):
        return self.todate

    def get_billno(self):
        return self.billno

    def get_foodallowance(self):
        return self.foodallowance

    def get_medicalexpense(self):
        return self.medicalexpense

    def get_remarks(self):
        return self.remarks

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


class Local_dept_req:
    id= None
    tourid = None
    expenseid = None
    claimreqgid = None
    visitcity =None
    fromdate = None
    todate = None
    sysdays = None
    noofdays = None
    isleave = None
    accbybank = None
    boardingbybank = None
    declaration = None
    vendorname = None
    vendortype = None
    vendorcode = None
    gstno = None
    gstrate = None
    eligibleamount = None
    claimedamount = None
    approvedamount = None
    requestercomment = None
    status = Status.REQUESTED


    def __init__(self, tour_obj):
        if 'id' in tour_obj:
            self.id = tour_obj['id']
        if 'tourgid' in tour_obj:
            self.tourid = tour_obj['tourgid']
        if 'expense_id' in tour_obj:
            self.expenseid = tour_obj['expense_id']
        if 'claimreqgid' in tour_obj:
            self.claimreqgid = tour_obj['claimreqgid']
        if 'city' in tour_obj:
            self.visitcity = tour_obj['city']
        if 'startdate' in tour_obj:
            self.fromdate = tour_obj['startdate']
        if 'enddate' in tour_obj:
            self.todate = tour_obj['enddate']
        if 'sysdays' in tour_obj:
            self.sysdays = tour_obj['sysdays']
        if 'no_of_days' in tour_obj:
            self.noofdays = tour_obj['no_of_days']
        if 'leave' in tour_obj:
            self.isleave = tour_obj['leave']
        if 'accbybank' in tour_obj:
            self.accbybank = tour_obj['accbybank']
        if 'boardingbybank' in tour_obj:
            self.boardingbybank = tour_obj['boardingbybank']
        if 'declaration' in tour_obj:
            self.declaration = tour_obj['declaration']
        if 'vendorname' in tour_obj:
            self.vendorname = tour_obj['vendorname']
        if 'vendortype' in tour_obj:
            self.vendortype = tour_obj['vendortype']
        if 'vendorcode' in tour_obj:
            self.vendorcode = tour_obj['vendorcode']
        if 'gstno' in tour_obj:
            self.gstno = tour_obj['gstno']
        if 'gstrate' in tour_obj:
            self.gstrate = tour_obj['gstrate']
        if 'eligibleamount' in tour_obj:
            self.eligibleamount = tour_obj['eligibleamount']
        if 'claimedamount' in tour_obj:
            self.claimedamount = tour_obj['claimedamount']
        if 'approvedamount' in tour_obj:
            self.approvedamount = tour_obj['approvedamount']
        if 'requestercomment' in tour_obj:
            self.requestercomment = tour_obj['requestercomment']
        if 'status' in tour_obj:
            self.status = tour_obj['status']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_tourid(self, tourid):
        self.tourid = tourid

    def set_expenseid(self, expenseid):
        self.expenseid = expenseid

    def set_claimreqgid(self, claimreqgid):
        self.claimreqgid = claimreqgid

    def set_visitcity(self, visitcity):
        self.visitcity = visitcity

    def set_fromdate(self, fromdate):
        self.fromdate = fromdate

    def set_todate(self, todate):
        self.todate = todate

    def set_syshours(self, syshours):
        self.syshours = syshours

    def set_noofhours(self, noofhours):
        self.noofhours = noofhours

    def set_isleave(self, isleave):
        self.isleave = isleave

    def set_accbybank(self, accbybank):
        self.accbybank = accbybank

    def set_boardingbybank(self, boardingbybank):
        self.boardingbybank = boardingbybank

    def set_declaration(self, declaration):
        self.declaration = declaration

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

    def set_gstrate(self, gstrate):
        self.gstrate = gstrate

    def set_eligibleamount(self, eligibleamount):
        self.eligibleamount = eligibleamount

    def set_claimedamount(self, claimedamount):
        self.claimedamount = claimedamount

    def set_approvedamount(self, approvedamount):
        self.approvedamount = approvedamount

    def set_requestercomment(self, requestercomment):
        self.requestercomment = requestercomment

    def get_id(self):
        return self.id

    def get_tourid(self):
        return self.tourid

    def get_expenseid(self):
        return self.expenseid

    def get_claimreqgid(self):
        return self.claimreqgid

    def get_visitcity(self):
        return self.visitcity

    def get_fromdate(self):
        return self.fromdate

    def get_todate(self):
        return self.todate

    def get_sysdays(self):
        return self.sysdays

    def get_noofdays(self):
        return self.noofdays

    def get_isleave(self):
        return self.isleave

    def get_accbybank(self):
        return self.accbybank

    def get_boardingbybank(self):
        return self.boardingbybank

    def get_declaration(self):
        return self.declaration

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

    def get_requestercomment(self):
        return self.requestercomment

    def get_status(self):
        return self.status

class Incidental_Request:
    id= None
    tourid = None
    claimreqgid = None
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
    status = Status.REQUESTED
    expenseid = None
    requestercomment = None

    def __init__(self, tour_obj):
        if 'id' in tour_obj:
            self.id = tour_obj['id']
        if 'tourid' in tour_obj:
            self.tourid = tour_obj['tourid']
        if 'claimreqgid' in tour_obj:
            self.claimreqgid = tour_obj['claimreqgid']
        if 'code' in tour_obj:
            self.code = tour_obj['code']
        if 'travel_mode' in tour_obj:
            self.travel_mode = tour_obj['travel_mode']
        if 'same_day_return' in tour_obj:
            self.samedayreturn = tour_obj['same_day_return']
        if 'travel_hours' in tour_obj:
            self.travelhours = tour_obj['travel_hours']
        if 'single_fare' in tour_obj:
            self.singlefare = tour_obj['single_fare']
        if 'expenses' in tour_obj:
            self.expenses = tour_obj['expenses']
        if 'vendorname' in tour_obj:
            self.vendorname = tour_obj['vendorname']
        if 'vendortype' in tour_obj:
            self.vendortype = tour_obj['vendortype']
        if 'vendorcode' in tour_obj:
            self.vendorcode = tour_obj['vendorcode']
        if 'gstno' in tour_obj:
            self.gstno = tour_obj['gstno']
        if 'gstrate' in tour_obj:
            self.gstrate = tour_obj['gstrate']
        if 'eligibleamount' in tour_obj:
            self.eligibleamount = tour_obj['eligibleamount']
        if 'claimedamount' in tour_obj:
            self.claimedamount = tour_obj['claimedamount']
        if 'approvedamount' in tour_obj:
            self.approvedamount = tour_obj['approvedamount']
        if 'status' in tour_obj:
            self.status = tour_obj['status']
        if 'expenseid' in tour_obj:
            self.expenseid = tour_obj['expenseid']
        if 'requestercomment' in tour_obj:
            self.requestercomment = tour_obj['requestercomment']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_tourid(self, tourid):
        self.tourid = tourid

    def set_claimreqgid(self, claimreqgid):
        self.claimreqgid = claimreqgid

    def set_code(self, code):
        self.code = code

    def set_samedayreturn(self, samedayreturn):
        self.samedayreturn = samedayreturn

    def set_travelhours(self, travelhours):
        self.travelhours = travelhours

    def set_singlefare(self, singlefare):
        self.singlefare = singlefare

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

    def set_gstrate(self, gstrate):
        self.gstrate = gstrate

    def set_eligibleamount(self, eligibleamount):
        self.eligibleamount = eligibleamount

    def set_claimedamount(self, claimedamount):
        self.claimedamount = claimedamount

    def set_approvedamount(self, approvedamount):
        self.approvedamount = approvedamount

    def set_expenseid(self, expenseid):
        self.expenseid = expenseid

    def set_requestercomment(self, requestercomment):
        self.requestercomment = requestercomment

    def get_expenseid(self):
        return self.expenseid

    def get_requestercomment(self):
        return self.requestercomment

    def get_id(self):
        return self.id

    def get_tourid(self):
        return self.tourid

    def get_claimreqgid(self):
        return self.claimreqgid

    def get_code(self):
        return self.code

    def get_samedayreturn(self):
        return self.samedayreturn
    def get_travel_mode(self):
        return self.travel_mode

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

class Localconveyence_Request:
    id= None
    tour_id = None
    claimreqgid = None
    modeoftravel = None
    fromplace = None
    toplace = None
    fromdate = None
    todate = None
    remarks = None
    billno = None
    distance = None
    eligibleamount = None
    claimedamount = None
    approvedamount = None
    status = None
    expenseid = None
    requestercomment = None
    approvedamount=None
    eligibleamount=None

    def __init__(self, tour_obj):
        if 'id' in tour_obj:
            self.id = tour_obj['id']
        if 'tour_id' in tour_obj:
            self.tour_id = tour_obj['tour_id']
        if 'expensegid' in tour_obj:
            self.expensegid = tour_obj['expensegid']
        if 'claimreqgid' in tour_obj:
            self.claimreqgid = tour_obj['claimreqgid']
        if 'modeoftravel' in tour_obj:
            self.modeoftravel = tour_obj['modeoftravel']
        if 'distance' in tour_obj:
            self.distance = tour_obj['distance']
        if 'billno' in tour_obj:
            self.billno = tour_obj['billno']
        if 'remarks' in tour_obj:
            self.remarks = tour_obj['remarks']
        if 'fromplace' in tour_obj:
            self.fromplace = tour_obj['fromplace']
        if 'toplace' in tour_obj:
            self.toplace = tour_obj['toplace']
        if 'fromdate' in tour_obj:
            self.fromdate = tour_obj['fromdate']
        if 'todate' in tour_obj:
            self.todate = tour_obj['todate']
        if 'eligibleamount' in tour_obj:
            self.eligibleamount = tour_obj['eligibleamount']
        if 'claimedamount' in tour_obj:
            self.claimedamount = tour_obj['claimedamount']
        if 'approvedamount' in tour_obj:
            self.approvedamount = tour_obj['approvedamount']
        if 'status' in tour_obj:
            self.status = tour_obj['status']
        if 'expense_id' in tour_obj:
            self.expenseid = tour_obj['expense_id']
        if 'requestercomment' in tour_obj:
            self.requestercomment = tour_obj['requestercomment']

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

    def set_billno(self, billno):
        self.billno = billno

    def set_fromplace(self, fromplace):
        self.fromplace = fromplace

    def set_toplace(self, toplace):
        self.toplace = toplace

    def set_fromdate(self, fromdate):
        self.fromdate = fromdate

    def set_todate(self, todate):
        self.todate = todate

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_distance(self, distance):
        self.distance = distance

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

    def get_billno(self):
        return self.billno

    def get_fromplace(self):
        return self.fromplace

    def get_toplace(self):
        return self.toplace

    def get_fromdate(self):
        return self.fromdate

    def get_todate(self):
        return self.todate

    def get_remarks(self):
        return self.remarks

    def get_distance(self):
        return self.distance

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

class Lodging_Request:
    id = None
    tour_id = None
    claimreqgid = None
    Lodge_Homestay = None
    metro_nonmetro = None
    fromdate = None
    todate = None
    remarks =None
    city = None
    noofdays = None
    billno = None
    eligibleamount = None
    approvedamount = None
    Billamountexculdingtax = None
    taxonly = None
    claimedamount = None
    vendorname = None
    status = None
    expensegid = None
    requestercomment = None

    def __init__(self, tour_obj):
        if 'id' in tour_obj:
            self.id = tour_obj['id']
        if 'tour_id' in tour_obj:
            self.tour_id = tour_obj['tour_id']
        if 'claimreqgid' in tour_obj:
            self.claimreqgid = tour_obj['claimreqgid']
        if 'expensegid' in tour_obj:
            self.expensegid = tour_obj['expensegid']
        if 'Lodge_Homestay' in tour_obj:
            self.Lodge_Homestay = tour_obj['Lodge_Homestay']
        if 'metro_nonmetro' in tour_obj:
            self.metro_nonmetro = tour_obj['metro_nonmetro']
        if 'fromdate' in tour_obj:
            self.fromdate = tour_obj['fromdate']
        if 'todate' in tour_obj:
            self.todate = tour_obj['todate']
        if 'remarks' in tour_obj:
            self.remarks = tour_obj['remarks']
        if 'vendorname' in tour_obj:
            self.vendorname = tour_obj['vendorname']
        if 'city' in tour_obj:
            self.city = tour_obj['city']
        if 'billno' in tour_obj:
            self.billno = tour_obj['billno']
        if 'noofdays' in tour_obj:
            self.noofdays = tour_obj['noofdays']
        if 'eligibleamount' in tour_obj:
            self.eligibleamount = tour_obj['eligibleamount']
        if 'Billamountexculdingtax' in tour_obj:
            self.Billamountexculdingtax = tour_obj['Billamountexculdingtax']
        if 'approvedamount' in tour_obj:
            self.approvedamount = tour_obj['approvedamount']
        if 'taxonly' in tour_obj:
            self.taxonly = tour_obj['taxonly']
        if 'claimedamount' in tour_obj:
            self.claimedamount = tour_obj['claimedamount']
        if 'approvedamount' in tour_obj:
            self.approvedamount = tour_obj['approvedamount']
        if 'eligibleamount' in tour_obj:
            self.eligibleamount = tour_obj['eligibleamount']
        if 'status' in tour_obj:
            self.status = tour_obj['status']
        if 'expensegid' in tour_obj:
            self.expenseid = tour_obj['expensegid']
        if 'requestercomment' in tour_obj:
            self.requestercomment = tour_obj['requestercomment']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_tourid(self, tourid):
        self.tourid = tourid

    def set_claimreqgid(self, claimreqgid):
        self.claimreqgid = claimreqgid

    def set_Lodge_Homestay(self, Lodge_Homestay):
        self.Lodge_Homestay = Lodge_Homestay

    def set_metro_nonmetro(self, metro_nonmetro):
        self.metro_nonmetro = metro_nonmetro

    def set_billno(self, billno):
        self.billno = billno

    def set_fromdate(self, fromdate):
        self.fromdate = fromdate

    def set_todate(self, todate):
        self.todate = todate

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_city(self, city):
        self.city = city

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

    def get_metro_nonmetro(self):
        return self.metro_nonmetro

    def get_billno(self):
        return self.billno

    def get_fromdate(self):
        return self.fromdate

    def get_todate(self):
        return self.todate

    def get_vendorname(self):
        return self.vendorname

    def get_billno(self):
        return self.billno

    def get_city(self):
        return self.city

    def get_remarks(self):
        return self.remarks

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

class Misc_Request:
    id= None
    tourid = None
    claimreqgid = None
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
    status = Status.REQUESTED
    expenseid = None
    requestercomment = None
    center = None

    def __init__(self, tour_obj):
        if 'id' in tour_obj:
            self.id = tour_obj['id']
        if 'tourgid' in tour_obj:
            self.tourid = tour_obj['tourgid']
        if 'claimreqgid' in tour_obj:
            self.claimreqgid = tour_obj['claimreqgid']
        if 'description' in tour_obj:
            self.description = tour_obj['description']
        if 'expreason' in tour_obj:
            self.expreason = tour_obj['expreason']
        if 'vendorname' in tour_obj:
            self.vendorname = tour_obj['vendorname']
        if 'vendortype' in tour_obj:
            self.vendortype = tour_obj['vendortype']
        if 'vendorcode' in tour_obj:
            self.vendorcode = tour_obj['vendorcode']
        if 'bankgstno' in tour_obj:
            self.bankgstno = tour_obj['bankgstno']
        if 'vendorgstno' in tour_obj:
            self.vendorgstno = tour_obj['vendorgstno']
        if 'igst' in tour_obj:
            self.igst = tour_obj['igst']
        if 'cgst' in tour_obj:
            self.cgst = tour_obj['cgst']
        if 'sgst' in tour_obj:
            self.sgst = tour_obj['sgst']
        if 'eligibleamount' in tour_obj:
            self.eligibleamount = tour_obj['eligibleamount']
        if 'claimedamount' in tour_obj:
            self.claimedamount = tour_obj['claimedamount']
        if 'approvedamount' in tour_obj:
            self.approvedamount = tour_obj['approvedamount']
        if 'status' in tour_obj:
            self.status = tour_obj['status']
        if 'expense_id' in tour_obj:
            self.expenseid = tour_obj['expense_id']
        if 'requestercomment' in tour_obj:
            self.requestercomment = tour_obj['requestercomment']
        if 'center' in tour_obj:
            self.center = tour_obj['center']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_tourid(self, tourid):
        self.tourid = tourid

    def set_claimreqgid(self, claimreqgid):
        self.claimreqgid = claimreqgid

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

    def set_expenseid(self, expenseid):
        self.expenseid = expenseid

    def set_requestercomment(self, requestercomment):
        self.requestercomment = requestercomment

    def get_expenseid(self):
        return self.expenseid

    def get_requestercomment(self):
        return self.requestercomment

    def get_id(self):
        return self.id

    def get_tourid(self):
        return self.tourid

    def get_claimreqgid(self):
        return self.claimreqgid

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

    def get_center(self):
        return self.center

    def get_claimedamount(self):
        return self.claimedamount

    def get_approvedamount(self):
        return self.approvedamount

    def get_status(self):
        return self.status

class PackingMoving_Request:
    id= None
    tourid = None
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
    status = Status.REQUESTED
    expense_id = None
    requestercomment = None
    claimreqgid=None

    def __init__(self, tour_obj):
        if 'id' in tour_obj:
            self.id = tour_obj['id']
        if 'tourgid' in tour_obj:
            self.tourid = tour_obj['tourgid']
        if 'claimreqgid' in tour_obj:
            self.claimreqgid = tour_obj['claimreqgid']
        if 'twowheelertrans' in tour_obj:
            self.twowheelertrans = tour_obj['twowheelertrans']
        if 'hhgoodstrans' in tour_obj:
            self.hhgoodstrans = tour_obj['hhgoodstrans']
        if 'transtwowheelerby' in tour_obj:
            self.transtwowheelerby = tour_obj['transtwowheelerby']
        if 'ibaappvendor' in tour_obj:
            self.ibaappvendor = tour_obj['ibaappvendor']
        if 'totaldisttrans' in tour_obj:
            self.totaldisttrans = tour_obj['totaldisttrans']
        if 'distinhilly' in tour_obj:
            self.distinhilly = tour_obj['distinhilly']
        if 'tonnagehhgood' in tour_obj:
            self.tonnagehhgood = tour_obj['tonnagehhgood']
        if 'maxeligton' in tour_obj:
            self.maxeligton = tour_obj['maxeligton']
        if 'billedamthhgoodstrans' in tour_obj:
            self.billedamthhgoodstrans = tour_obj['billedamthhgoodstrans']
        if 'eligtransamt' in tour_obj:
            self.eligtransamt = tour_obj['eligtransamt']
        if 'transchargesvehicle' in tour_obj:
            self.transchargesvehicle = tour_obj['transchargesvehicle']
        if 'vehicletransbydriver' in tour_obj:
            self.vehicletransbydriver = tour_obj['vehicletransbydriver']
        if 'traveltime' in tour_obj:
            self.traveltimeinhours = tour_obj['traveltime']
        if 'daysdrivereng' in tour_obj:
            self.daysdrivereng = tour_obj['daysdrivereng']
        if 'driverbatta' in tour_obj:
            self.driverbatta = tour_obj['driverbatta']
        if 'octroivehicle' in tour_obj:
            self.octroivehicle = tour_obj['octroivehicle']
        if 'breakagecharges' in tour_obj:
            self.breakagecharges = tour_obj['breakagecharges']
        if 'receipt_loss' in tour_obj:
            self.receiptlosses = tour_obj['receipt_loss']
        if 'eligbreakagecharge' in tour_obj:
            self.eligbreakagecharge = tour_obj['eligbreakagecharge']
        if 'hsncode' in tour_obj:
            self.hsncode = tour_obj['hsncode']
        if 'vendorname' in tour_obj:
            self.vendorname = tour_obj['vendorname']
        if 'vendortype' in tour_obj:
            self.vendortype = tour_obj['vendortype']
        if 'vendorcode' in tour_obj:
            self.vendorcode = tour_obj['vendorcode']
        if 'bankgstno' in tour_obj:
            self.bankgstno = tour_obj['bankgstno']
        if 'vendorgstno' in tour_obj:
            self.vendorgstno = tour_obj['vendorgstno']
        if 'igst' in tour_obj:
            self.igst = tour_obj['igst']
        if 'cgst' in tour_obj:
            self.cgst = tour_obj['cgst']
        if 'sgst' in tour_obj:
            self.sgst = tour_obj['sgst']
        if 'eligibleamount' in tour_obj:
            self.eligibleamount = tour_obj['eligibleamount']
        if 'claimedamount' in tour_obj:
            self.claimedamount = tour_obj['claimedamount']
        if 'approvedamount' in tour_obj:
            self.approvedamount = tour_obj['approvedamount']
        if 'status' in tour_obj:
            self.status = tour_obj['status']
        if 'expense_id' in tour_obj:
            self.expenseid = tour_obj['expense_id']
        if 'requestercomment' in tour_obj:
            self.requestercomment = tour_obj['requestercomment']


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_tourid(self, tourid):
        self.tourid = tourid

    def set_claimreqgid(self, claimreqgid):
        self.claimreqgid = claimreqgid

    def set_twowheelertrans(self, twowheelertrans):
        self.twowheelertrans = twowheelertrans

    def set_hhgoodstrans(self, hhgoodstrans):
        self.hhgoodstrans = hhgoodstrans

    def set_transtwowheelerby(self, transtwowheelerby):
        self.transtwowheelerby = transtwowheelerby

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

    def set_traveltimeinhours(self, traveltimeinhours):
        self.traveltimeinhours = traveltimeinhours

    def set_daysdrivereng(self, daysdrivereng):
        self.daysdrivereng = daysdrivereng

    def set_driverbatta(self, driverbatta):
        self.driverbatta = driverbatta

    def set_octroivehicle(self, octroivehicle):
        self.octroivehicle = octroivehicle

    def set_breakagecharges(self, breakagecharges):
        self.breakagecharges = breakagecharges

    def set_receiptlosses(self, receiptlosses):
        self.receiptlosses = receiptlosses

    def set_eligbreakagecharge(self, eligbreakagecharge):
        self.eligbreakagecharge = eligbreakagecharge

    def set_hsncode(self, hsncode):
        self.hsncode = hsncode

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

    def set_expenseid(self, expenseid):
        self.expenseid = expenseid

    def set_requestercomment(self, requestercomment):
        self.requestercomment = requestercomment

    def get_expenseid(self):
        return self.expenseid

    def get_requestercomment(self):
        return self.requestercomment

    def get_id(self):
        return self.id

    def get_tourid(self):
        return self.tourid

    def get_claimreqgid(self):
        return self.claimreqgid

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
        return self.driverbatta

    def get_octroivehicle(self):
        return self.octroivehicle

    def get_breakagecharges(self):
        return self.breakagecharges

    def get_receiptlosses(self):
        return self.receiptlosses

    def get_eligbreakagecharge(self):
        return self.eligbreakagecharge

    def get_hsncode(self):
        return self.hsncode

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

class Travel_Request:
    id = None
    tour_id = None
    claimreqgid = None
    traveltype = None
    fromdate = None
    fromplace = None
    todate = None
    billno = None
    remarks =None
    toplace = None
    vendorname = None
    totaltkttamt = None
    approvedamount = None
    tktby = None
    actualmode = None
    travelclass = None
    eligiblemodeoftravel = None
    highermodereason = None
    prior_permission = 0
    status = None
    expensegid = None
    requestercomment = None

    def __init__(self, tour_obj):
        if 'id' in tour_obj:
            self.id = tour_obj['id']
        if 'tour_id' in tour_obj:
            self.tour_id = tour_obj['tour_id']
        if 'claimreqgid' in tour_obj:
            self.claimreqgid = tour_obj['claimreqgid']
        if 'traveltype' in tour_obj:
            self.traveltype = tour_obj['traveltype']
        if 'fromdate' in tour_obj:
            self.fromdate = tour_obj['fromdate']
        if 'fromplace' in tour_obj:
            self.fromplace = tour_obj['fromplace']
        if 'toplace' in tour_obj:
            self.toplace = tour_obj['toplace']
        if 'billno' in tour_obj:
            self.billno = tour_obj['billno']
        if 'todate' in tour_obj:
            self.todate = tour_obj['todate']
        if 'remarks' in tour_obj:
            self.remarks = tour_obj['remarks']
        if 'vendorname' in tour_obj:
            self.vendorname = tour_obj['vendorname']
        if 'totaltkttamt' in tour_obj:
            self.totaltkttamt = tour_obj['totaltkttamt']
        if 'approvedamount' in tour_obj:
            self.approvedamount = tour_obj['approvedamount']
        if 'tktby' in tour_obj:
            self.tktby = tour_obj['tktby']
        if 'actualmode' in tour_obj:
            self.actualmode = tour_obj['actualmode']
        if 'travelclass' in tour_obj:
            self.travelclass = tour_obj['travelclass']
        if 'eligiblemodeoftravel' in tour_obj:
            self.eligiblemodeoftravel = tour_obj['eligiblemodeoftravel']
        if 'highermodereason' in tour_obj:
            self.highermodereason = tour_obj['highermodereason']
        if 'prior_permission' in tour_obj:
            self.prior_permission = tour_obj['prior_permission']
        if 'status' in tour_obj:
            self.status = tour_obj['status']
        if 'expensegid' in tour_obj:
            self.expensegid = tour_obj['expensegid']
        if 'requestercomment' in tour_obj:
            self.requestercomment = tour_obj['requestercomment']

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
        self.fromdate = fromdate

    def set_billno(self, billno):
        self.billno = billno

    def set_fromplace(self, fromplace):
        self.fromplace = fromplace

    def set_todate(self, todate):
        self.todate = todate

    def set_toplace(self, toplace):
        self.toplace = toplace

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_vendorname(self, vendorname):
        self.vendorname = vendorname

    def set_totaltkttamt(self, totaltkttamt):
        self.totaltkttamt = totaltkttamt

    def set_approvedamount(self, approvedamount):
        self.approvedamount = approvedamount

    def set_tktby(self, tktby):
        self.tktby = tktby

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

    def get_vendorname(self):
        return self.vendorname

    def get_billno(self):
        return self.billno

    def get_fromdate(self):
        return self.fromdate

    def get_fromplace(self):
        return self.fromplace

    def get_todate(self):
        return self.todate

    def get_toplace(self):
        return self.toplace

    def get_remarks(self):
        return self.remarks

    def get_totaltkttamt(self):
        return self.totaltkttamt

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


class Travel_Dep_Request:
    id = None
    tourid = None
    claimreqgid = None
    travelid = None
    empid = None
    dependentid = None
    dependentname = None
    deprelation = None
    isdepelig = None

    def __init__(self, tour_obj):
        if 'id' in tour_obj:
            self.id = tour_obj['id']
        if 'tourid' in tour_obj:
            self.tourid = tour_obj['tourid']
        if 'claimreqgid' in tour_obj:
            self.claimreqgid = tour_obj['claimreqgid']
        if 'travelid' in tour_obj:
            self.travelid = tour_obj['travelid']
        if 'empid' in tour_obj:
            self.empid = tour_obj['empid']
        if 'dependentid' in tour_obj:
            self.dependentid = tour_obj['dependentid']
        if 'dependentname' in tour_obj:
            self.dependentname = tour_obj['dependentname']
        if 'deprelation' in tour_obj:
            self.deprelation = tour_obj['deprelation']
        if 'isdepelig' in tour_obj:
            self.isdepelig = tour_obj['isdepelig']

class associate_Request:
    tour = None
    claimreqgid = None
    description = None
    expense = None
    fromdate = None
    todate = None
    billno = None
    remarks = None
    claimedamount = None
    approvedamount = None
    expensegid = None
    status = None
    created_by = None
    created_date = None
    updated_by = None
    updated_date = None
    entity_id = None

    def __init__(self, tour_obj):
        if 'id' in tour_obj:
            self.id = tour_obj['id']
        if 'tour_id' in tour_obj:
            self.tour_id = tour_obj['tour_id']
        if 'claimreqgid' in tour_obj:
            self.claimreqgid = tour_obj['claimreqgid']
        if 'expensegid' in tour_obj:
            self.expensegid = tour_obj['expensegid']
        if 'description' in tour_obj:
            self.description = tour_obj['description']
        if 'expense' in tour_obj:
            self.expense = tour_obj['expense']
        if 'fromdate' in tour_obj:
            self.fromdate = tour_obj['fromdate']
        if 'todate' in tour_obj:
            self.todate = tour_obj['todate']
        if 'remarks' in tour_obj:
            self.remarks = tour_obj['remarks']
        if 'billno' in tour_obj:
            self.billno = tour_obj['billno']
        if 'claimedamount' in tour_obj:
            self.claimedamount = tour_obj['claimedamount']
        if 'approvedamount' in tour_obj:
            self.approvedamount = tour_obj['approvedamount']
        if 'requestercomment' in tour_obj:
            self.requestercomment = tour_obj['requestercomment']
        if 'status' in tour_obj:
            self.status = tour_obj['status']
        if 'created_by' in tour_obj:
            self.created_by = tour_obj['created_by']
        if 'created_date' in tour_obj:
            self.created_date = tour_obj['created_date']
        if 'updated_by' in tour_obj:
            self.updated_by = tour_obj['updated_by']
        if 'updated_date' in tour_obj:
            self.updated_date = tour_obj['updated_date']
        if 'entity_id' in tour_obj:
            self.entity_id = tour_obj['entity_id']

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
        self.fromdate = fromdate

    def set_todate(self, todate):
        self.todate = todate

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

    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_created_date(self, created_date):
        self.created_date = created_date

    def set_updated_by(self, updated_by):
        self.updated_by = updated_by

    def set_updated_date(self, updated_date):
        self.updated_date = updated_date

    def set_entity_id(self, entity_id):
        self.entity_id = entity_id

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

    def get_fromdate(self):
        return self.fromdate

    def get_todate(self):
        return self.todate

    def get_remarks(self):
        return self.remarks

    def get_billno(self):
        return self.billno

    def get_claimedamount(self):
        return self.claimedamount

    def get_approvedamount(self):
        return self.approvedamount

    def get_status(self):
        return self.status

    def get_created_by(self):
        return self.created_by

    def get_created_date(self):
        return self.created_date

    def get_updated_by(self):
        return self.updated_by

    def get_updated_date(self):
        return self.updated_date

    def get_entity_id(self):
        return self.entity_id




