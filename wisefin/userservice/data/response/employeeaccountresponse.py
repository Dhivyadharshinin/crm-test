import json
from masterservice.data.response.bankresponse import BankResponse
from masterservice.data.response.bankbranchresponse import BankBranchResponse
from userservice.data.response.employeeresponse import EmployeeResponse
from masterservice.data.response.paymoderesponse import PaymodeResponse
class EmployeeAccountDetailsResponse:
    id = None
    employee = None
    paymode = None
    bank = None
    bankbranch = None
    account_number = None
    beneficiary_name = None
    status = None


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_employee(self, employee):
        self.employee = employee

    def set_paymode(self,paymode):
        self.paymode=paymode

    def set_bank(self, bank):
        self.bank = bank

    def set_bankbranch(self, bankbranch):
        self.bankbranch = bankbranch

    def set_account_number(self, account_number):
        self.account_number = account_number

    def set_beneficiary_name(self, beneficiary_name):
        self.beneficiary_name = beneficiary_name

    def set_status(self, status):
        self.status = status


class EmployeeAccountDetailsResponseSummary:
    id = None
    employee = None
    paymode = None
    bank = None
    bankbranch = None
    account_number = None
    beneficiary_name = None
    status = None
    employee_id=None
    employee_code=None
    employee_full_name=None
    set_bankbranch_name=None
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_employee(self, employee):
        self.employee=employee


    def set_paymode(self,paymode):

        self.paymode=paymode

    def set_bank(self, bank):
        self.bank = bank


    def set_bankbranch(self, bankbranch):
        self.bankbranch = bankbranch

    def set_account_number(self, account_number):
        self.account_number = account_number

    def set_beneficiary_name(self, beneficiary_name):
        self.beneficiary_name = beneficiary_name

    def set_status(self, status):
        self.status = status
    def set_employee_id(self,employee_id):
        self.employee_id=employee_id

    def set_employee_code(self,employee_code):
        self.employee_code=employee_code

    def set_employee_full_name(self,employee_full_name):
        self.employee_full_name=employee_full_name
    def set_paymode_id(self,paymode_id):
        self.paymode_id=paymode_id
    def set_paymode_name(self,paymode_name):
        self.paymode_name=paymode_name
    def set_bank_id(self,bank_id):
        self.bank_id=bank_id
    def set_bank_name(self,bank_name):
        self.bank_name=bank_name
    def set_bankbranch_id(self,bankbranch_id):
        self.bankbranch_id=bankbranch_id
    def set_bankbranch_name(self,bankbranch_name):
        self.bankbranch_name=bankbranch_name