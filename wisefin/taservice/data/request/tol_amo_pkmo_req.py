class Tol_amo_pkmo_req:
    totaldisttrans = None
    tonnagehhgood = None
    distinhilly = None
    twowheelertrans = None
    grade = None
    expense_id = None
    salarygrade = None
    city = None
    checkindate = None
    checkoutdate = None
    traveltime = None
    receipt_loss = None
    tourgid = None
    applicable_to = None
    vehicletransbydriver=0


    def __init__(self, obj):
        if 'totaldisttrans' in obj:
            self.totaldisttrans = obj['totaldisttrans']
        if 'tonnagehhgood' in obj:
            self.tonnagehhgood = obj['tonnagehhgood']
        if 'distinhilly' in obj:
            self.distinhilly = obj['distinhilly']
        if 'twowheelertrans' in obj:
            self.twowheelertrans = obj['twowheelertrans']
        if 'grade' in obj:
            self.grade = obj['grade']
        if 'expense_id' in obj:
            self.expense_id=obj['expense_id']
        if 'salarygrade' in obj:
            self.salarygrade=obj['salarygrade']
        if 'city' in obj:
            self.city=obj['city']
        if 'checkindate' in obj:
            self.checkindate=obj['checkindate']
        if 'checkoutdate' in obj:
            self.checkoutdate=obj['checkoutdate']
        if 'traveltime' in obj:
            self.traveltime=obj['traveltime']
        if 'receipt_loss' in obj:
            self.receipt_loss=obj['receipt_loss']
        if 'applicable_to' in obj:
            self.applicable_to=obj['applicable_to']
        if 'tourgid' in obj:
            self.tourgid=obj['tourgid']
        if 'vehicletransbydriver' in obj:
            self.vehicletransbydriver=obj['vehicletransbydriver']

    def get_totaldisttrans(self):
        return self.totaldisttrans
    def get_tonnagehhgood(self):
        return self.tonnagehhgood
    def get_distinhilly(self):
        return self.distinhilly
    def get_twowheelertrans(self):
        return self.twowheelertrans
    def get_grade(self):
        return self.grade
    def get_expense_id(self):
        return self.expense_id
    def get_salarygrade(self):
        return self.salarygrade
    def get_city(self):
        return self.city
    def get_checkindate(self):
        return self.checkindate
    def get_checkoutdate(self):
        return self.checkoutdate
    def get_traveltime(self):
        return self.traveltime
    def get_receipt_loss(self):
        return self.receipt_loss


class Local_dept_res:
    no_of_days = None
    startdate = None
    enddate = None
    twowheelertrans = None
    grade = None
    expense_id = None
    salarygrade = None
    city = None
    leave = 0
    entity = 1
    tourgid = None


    def __init__(self, obj):
        if 'no_of_days' in obj:
            self.no_of_days = obj['no_of_days']
        if 'startdate' in obj:
            self.startdate = obj['startdate']
        if 'enddate' in obj:
            self.enddate = obj['enddate']
        if 'twowheelertrans' in obj:
            self.twowheelertrans = obj['twowheelertrans']
        if 'grade' in obj:
            self.grade = obj['grade']
        if 'expense_id' in obj:
            self.expense_id=obj['expense_id']
        if 'salarygrade' in obj:
            self.salarygrade=obj['salarygrade']
        if 'city' in obj:
            self.city=obj['city']
        if 'leave' in obj:
            self.leave=obj['leave']
        if 'entity' in obj:
            self.entity=obj['entity']
        if 'tourgid' in obj:
            self.tourgid=obj['tourgid']