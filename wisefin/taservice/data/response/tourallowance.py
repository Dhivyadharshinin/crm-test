import json
class Allowanceresponse:
    salarygrade = None
    city = None
    citytype = None
    amount = None
    applicableto = None
    status = None
    entity = 1
    id = None
    sys_hours=None
    name =None
    data =[]

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_name(self,name):
        self.name=name

    def set_salarygrade(self, salarygrade):
        self.salarygrade = salarygrade

    def set_city(self, city):
        self.city = city

    def set_citytype(self, citytype):
        self.citytype = citytype

    def set_amount(self, amount):
        self.elgibleamount = amount

    def set_applicableto(self, applicableto):
        self.applicableto = applicableto

    def set_status(self, status):
        self.status = status

    def set_entity(self, entity):
        self.entity = entity

    def set_expense_id(self, expense_id):
        self.expense_id = expense_id

    def set_expense_name(self,expense_name):
        self.expense_name=expense_name

    def set_data(self, data):
        self.data = data

    def set_eligible_amount(self,eligible_amount):
        self.eligible_amount=eligible_amount
    def set_sys_hours(self,sys_hours):
        self.sys_hours=sys_hours
    def set_effectivefrom(self, effectivefrom):
        if effectivefrom is None or effectivefrom==0:
            self.effectivefrom = effectivefrom
        else:
            self.effectivefrom = effectivefrom.strftime("%d-%b-%Y")
            self.effectivefrom_ms =round(effectivefrom.timestamp() * 1000)
    def set_effectiveto(self, effectiveto):
        if effectiveto is None or effectiveto==0:
            self.effectiveto = effectiveto
        else:
            self.effectiveto = effectiveto.strftime("%d-%b-%Y")
            self.effectiveto_ms =round(effectiveto.timestamp() * 1000)
    def set_approveddate(self, approveddate):
        if approveddate is None:
            self.approveddate = approveddate
        else:
            self.approveddate = approveddate.strftime("%d-%b-%Y")
            self.approveddate_ms =round(approveddate.timestamp() * 1000)

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

class GradeEligibiltyresponse:
    grage = None
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
    data =[]

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def set_id(self, id):
        self.id = id

    def set_grade(self, grade):
        self.grade = grade
    def set_employee_grade(self, employee_grade):
        self.employee_grade = employee_grade

    def set_gradelevel(self, gradelevel):
        self.gradelevel = gradelevel

    def set_travelclass(self, travelclass):
        self.travelclass = travelclass

    def set_travelmode(self, travelmode):
        self.travelmode = travelmode

    def set_freight1000(self, freight1000):
        self.freight1000 = freight1000

    def set_freight1001(self, freight1001):
        self.freight1001 = freight1001

    def set_twowheller(self, twowheller):
        self.twowheller = twowheller

    def set_hillyregion(self, hillyregion):
        self.hillyregion = hillyregion

    def set_tonnagefamily(self, tonnagefamily):
        self.tonnagefamily = tonnagefamily

    def set_maxtonnage(self, maxtonnage):
        self.maxtonnage = maxtonnage

    def set_employee_id(self, employee_id):
        self.employee_id = employee_id

    def set_request_no(self, request_no):
        self.request_no = request_no

    def set_employee_name(self, employee_name):
        self.employee_name = employee_name

    def set_employee_code(self, employee_code):
        self.employee_code = employee_code

    def set_data(self,data):
        self.data = data