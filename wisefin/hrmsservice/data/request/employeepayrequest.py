
class EmployeePayRequest:
    id=None
    employee_id=None
    basic_pay=None
    effective_from=None
    effective_to=None
    status=None
    created_by=None
    created_date=None
    updated_by=None
    updated_date=None

    def __init__(self,emp_obj):
        if 'id' in emp_obj:
            self.id=emp_obj['id']
        if 'employee_id' in emp_obj:
            self.employee_id = emp_obj['employee_id']
        if 'basic_pay' in emp_obj:
            self.basic_pay=emp_obj['basic_pay']
        if 'effective_from' in emp_obj:
            self.effective_from = emp_obj['effective_from']
        if 'effective_to' in emp_obj:
            self.effective_to = emp_obj['effective_to']
        if 'status' in emp_obj:
            self.status = emp_obj['status']
        if 'created_by' in emp_obj:
            self.created_by = emp_obj['created_by']
        if 'created_date' in emp_obj:
            self.created_date = emp_obj['created_date']
        if 'updated_by' in emp_obj:
            self.updated_by = emp_obj['updated_by']
        if 'updated_date' in emp_obj:
            self.updated_date = emp_obj['updated_date']

    def get_id(self):
        return self.id
    def get_employee_id(self):
        return self.employee_id
    def get_basic_pay(self):
        return self.basic_pay
    def get_effective_from(self):
        return self.effective_from
    def get_effective_to(self):
        return self.effective_to
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

class EmployeeAdvanceRequestRequest:
    id=None
    employee_id=None
    requested_advance_amount=None
    approved_advance_amount=None
    reason=None
    status=None
    created_by=None
    created_date=None
    updated_by=None
    updated_date=None

    def __init__(self,emp_obj):
        if 'id' in emp_obj:
            self.id=emp_obj['id']
        if 'employee_id' in emp_obj:
            self.employee_id = emp_obj['employee_id']
        if 'requested_advance_amount' in emp_obj:
            self.requested_advance_amount=emp_obj['requested_advance_amount']
        if 'approved_advance_amount' in emp_obj:
            self.approved_advance_amount = emp_obj['approved_advance_amount']
        if 'reason' in emp_obj:
            self.reason = emp_obj['reason']
        if 'status' in emp_obj:
            self.status = emp_obj['status']
        if 'created_by' in emp_obj:
            self.created_by = emp_obj['created_by']
        if 'created_date' in emp_obj:
            self.created_date = emp_obj['created_date']
        if 'updated_by' in emp_obj:
            self.updated_by = emp_obj['updated_by']
        if 'updated_date' in emp_obj:
            self.updated_date = emp_obj['updated_date']

    def get_id(self):
        return self.id

    def get_employee_id(self):
        return self.employee_id

    def get_requested_advance_amount(self):
        return self.requested_advance_amount

    def get_approved_advance_amount(self):
        return self.approved_advance_amount

    def get_reason(self):
        return self.reason

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




class EmployeeAdvanceApprovalRequest:
    id=None
    employee_request_id=None
    employee_id=None
    remarks=None
    status=None
    created_by=None
    created_date=None
    updated_by=None
    updated_date=None

    def __init__(self, emp_obj):
        if 'id' in emp_obj:
            self.id = emp_obj['id']
        if 'employee_request_id' in emp_obj:
            self.employee_request_id = emp_obj['employee_request_id']
        if 'employee_id' in emp_obj:
            self.employee_id = emp_obj['employee_id']
        if 'remarks' in emp_obj:
            self.remarks = emp_obj['remarks']
        if 'status' in emp_obj:
            self.status = emp_obj['status']
        if 'created_by' in emp_obj:
            self.created_by = emp_obj['created_by']
        if 'created_date' in emp_obj:
            self.created_date = emp_obj['created_date']
        if 'updated_by' in emp_obj:
            self.updated_by = emp_obj['updated_by']
        if 'updated_date' in emp_obj:
            self.updated_date = emp_obj['updated_date']


    def get_id(self):
        return self.id

    def get_employee_request_id(self):
        return self.employee_request_id

    def get_employee_id(self):
        return self.employee_id

    def get_remarks(self):
        return self.remarks

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





