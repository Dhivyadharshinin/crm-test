import json
from taservice.util.ta_util import Status

class Allowancerequest:
    salarygrade = None
    city = None
    amount = None
    applicableto = None
    status = Status.REQUESTED
    entity = 1
    id = None
    expense_id = None
    effectiveto = None
    effectivefrom = None
    center = None
    tourgid = None
    claimedamount = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)
    def __init__(self, get_obj):

        if 'id' in get_obj:
            self.id = get_obj['id']
        if 'salarygrade' in get_obj:
            self.salarygrade = get_obj['salarygrade']
        if 'city' in get_obj:
            self.city = get_obj['city']
        if 'amount' in get_obj:
            self.amount = get_obj['amount']
        if 'applicableto' in get_obj:
            self.applicableto = get_obj['applicableto']
        if 'status' in get_obj:
            self.status = get_obj['status']
        if 'entity' in get_obj:
            self.entity = get_obj['entity']
        if 'expense_id' in get_obj:
            self.expense_id = get_obj['expense_id']
        if 'travel_mode' in get_obj:
            self.travel_mode = get_obj['travel_mode']
        if 'travel_hours' in get_obj:
            self.travel_hours = get_obj['travel_hours']
        if 'same_day_return' in get_obj:
            self.same_day_return = get_obj['same_day_return']
        if 'single_fare' in get_obj:
            self.single_fare = get_obj['single_fare']
        if 'effectivefrom' in get_obj:
            self.effectivefrom = get_obj['effectivefrom']
        if 'effectiveto' in get_obj:
            self.effectiveto = get_obj['effectiveto']
        if 'center' in get_obj:
            self.center = get_obj['center']
        if 'tourgid' in get_obj:
            self.tourgid = get_obj['tourgid']
        if 'claimedamount' in get_obj:
            self.claimedamount = get_obj['claimedamount']


    def get_id(self):
        return self.id
    def get_salarygrade(self):
        return self.salarygrade
    def get_city(self):
        return self.city
    def get_amount(self):
        return self.amount
    def get_applicableto(self):
        return self.applicableto
    def get_status(self):
        return self.status
    def get_entity(self):
        return self.entity
    def get_expense_id(self):
        return self.expense_id

class GradeEligibiltyrequest:
    grade = None
    gradelevel = None
    travelclass = None
    travelmode = None
    freight1000 = None
    freight1001 = None
    twowheller = None
    hillyregion = None
    tonnagefamily = None
    maxtonnage = None
    id = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def __init__(self, get_obj):

        if 'id' in get_obj:
            self.id = get_obj['id']
        if 'grade' in get_obj:
            self.grade = get_obj['grade']
        if 'gradelevel' in get_obj:
            self.gradelevel = get_obj['gradelevel']
        if 'travelclass' in get_obj:
            self.travelclass = get_obj['travelclass']
        if 'travelmode' in get_obj:
            self.travelmode = get_obj['travelmode']
        if 'freight1000' in get_obj:
            self.freight1000 = get_obj['freight1000']
        if 'freight1001' in get_obj:
            self.freight1001 = get_obj['freight1001']
        if 'twowheller' in get_obj:
            self.twowheller = get_obj['twowheller']
        if 'hillyregion' in get_obj:
            self.hillyregion = get_obj['hillyregion']
        if 'tonnagefamily' in get_obj:
            self.tonnagefamily = get_obj['tonnagefamily']
        if 'maxtonnage' in get_obj:
            self.maxtonnage = get_obj['maxtonnage']

    def get_id(self):
        return self.id

    def get_grade(self):
        return self.grade

    def get_gradelevel(self):
        return self.gradelevel

    def get_travelclass(self):
        return self.travelclass

    def get_travelmode(self):
        return self.travelmode

    def get_freight1000(self):
        return self.freight1000

    def get_freight1001(self):
        return self.freight1001

    def get_twowheller(self):
        return self.twowheller

    def get_hillyregion(self):
        return self.hillyregion

    def get_tonnagefamily(self):
        return self.tonnagefamily

    def get_maxtonnage(self):
        return self.maxtonnage
