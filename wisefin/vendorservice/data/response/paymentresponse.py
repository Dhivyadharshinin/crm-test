import json
class PaymentResponse:
    id = None
    supplier = None
    paymode_id = None
    bank_id = None
    branch_id = None
    account_type = None
    account_no = None
    beneficiary = None
    remarks = None
    supplierbranch_id=None
    status = None
    created_by = None
    created_date = None
    updated_by = None
    updated_date = None
    modify_ref_id = None
    modify_status = None
    is_active= False
    is_delete=None
    portal_flag = 0

    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_is_active(self, is_active):
        self.is_active = is_active

    def set_is_delete(self, is_delete):
        self.is_delete = is_delete

    def set_supplier(self, supplier):
        self.supplier = supplier

    def set_paymode_id(self, paymode_id):
        self.paymode_id = paymode_id

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

    def set_status(self, status):
        self.status = status

    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_created_date(self, created_date):
        created_date=str(created_date)
        self.created_date = created_date

    def set_modify_ref_id(self, modify_ref_id):
        self.modify_ref_id = modify_ref_id

    def set_modify_status(self, modify_status):
        self.modify_status = modify_status

    def set_updated_by(self, updated_by):
        self.updated_by = updated_by

    def set_updated_date(self, updated_date):
        updated_date=str(updated_date)
        self.updated_date = updated_date

    def get_id(self):
        return self.id
    def get_is_active(self):
        return self.is_active

    def get_supplier(self):
        return self.supplier

    def get_paymode(self):
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

    def get_supplierbranch_id(self):
        return self.supplierbranch_id

    def get_portal_flag(self):
        return self.portal_flag

    def set_portal_flag(self, portal_flag):
        self.portal_flag = portal_flag