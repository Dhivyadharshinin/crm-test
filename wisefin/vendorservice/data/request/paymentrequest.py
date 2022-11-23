import json


class PaymentRequest:
    id = None
    supplierbranch_id = None
    supplier = None
    paymode_id = None
    bank_id = None
    branch_id = None
    account_type = None
    account_no = None
    beneficiary = None
    remarks = None
    is_active = False
    portal_flag = 0


    def __init__(self, payment_obj):
        if 'id' in payment_obj:
            self.id = payment_obj['id']
        if 'supplier' in payment_obj:
            self.supplier = payment_obj['supplier']
        if 'paymode_id' in payment_obj:
            self.paymode_id = payment_obj['paymode_id']
        if 'bank_id' in payment_obj:
            self.bank_id = payment_obj['bank_id']
        if 'branch_id' in payment_obj:
            self.branch_id = payment_obj['branch_id']
        if 'account_type' in payment_obj:
            self.account_type = payment_obj['account_type']
        if 'account_no' in payment_obj:
            self.account_no = payment_obj['account_no']
        if 'supplierbranch_id' in payment_obj:
            self.supplierbranch_id = payment_obj['supplierbranch_id']
        if 'remarks' in payment_obj:
            self.remarks = payment_obj['remarks']
        if 'beneficiary' in payment_obj:
            self.beneficiary = payment_obj['beneficiary']
        if 'is_active' in payment_obj:
            if payment_obj['is_active'] == 1:
                self.is_active = True
        if 'portal_flag' in payment_obj:
            self.portal_flag = payment_obj['portal_flag']

    def get_id(self):
        return self.id

    def get_supplier(self):
        return self.supplier

    def get_paymode_id(self):
        return self.paymode_id

    def get_bank_id(self):
        return self.bank_id

    def get_branch_id(self):
        return self.branch_id

    def get_account_type(self):
        return self.account_type

    def get_account_no(self):
        return self.account_no

    def get_beneficiary(self):
        return self.beneficiary

    def get_remarks(self):
        return self.remarks

    def get_is_active(self):
        return self.is_active

    def get_supplierbranch_id(self):
        return self.supplierbranch_id

    def set_id(self, id):
        self.id = id
    def set_is_active(self, is_active):
        self.is_active = is_active

    def set_supplier(self, supplier):
        self.supplier = supplier

    def set_paymode(self, paymode):
        self.paymode_id = paymode

    def set_bank_id(self, bank_id):
        self.bank_id = bank_id

    def set_branch_id(self, branch_id):
        self.branch_id = branch_id

    def set_account_type(self, account_type):
        self.account_type = account_type

    def set_account_no(self, account_no):
        self.account_no = account_no

    def set_beneficiary(self, beneficiary):
        self.beneficiary = beneficiary

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_supplierbranch_id(self, supplierbranch_id):
        self.supplierbranch_id = supplierbranch_id

    def get_portal_flag(self):
        return self.portal_flag