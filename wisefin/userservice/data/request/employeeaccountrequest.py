import json
class EmployeeAccountDetailsRequest:
    id=None
    employee = None
    paymode = None
    bank =None
    bankbranch =None
    account_number = None
    beneficiary_name = None
    status = None

    def __init__(self, emp_obj):
        if 'id' in emp_obj:
            self.id = emp_obj['id']
        if 'employee' in emp_obj:
            self.employee = emp_obj['employee']
        if 'paymode' in emp_obj:
            self.paymode = emp_obj['paymode']
        if 'bank' in emp_obj:
            self.bank = emp_obj['bank']
        if 'bankbranch' in emp_obj:
            self.bankbranch = emp_obj['bankbranch']
        if 'account_number' in emp_obj:
            self.account_number = emp_obj['account_number']
        if 'beneficiary_name' in emp_obj:
            self.beneficiary_name=emp_obj['beneficiary_name']
        if 'status' in emp_obj:
            self.status=emp_obj['status']
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_id(self):
        return self.id
    def get_employee(self):
        return self.employee
    def get_paymode(self):
        return self.paymode
    def get_bank(self):
        return self.bank
    def get_bankbranch(self):
        return self.bankbranch
    def get_account_number(self):
        return self.account_number

    def get_beneficiary_name(self):
        return self.beneficiary_name

    def get_status(self):
        return self.status


