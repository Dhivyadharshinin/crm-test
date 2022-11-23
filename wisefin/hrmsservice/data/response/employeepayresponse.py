import json

class EmployeePayResponse:
    id = None
    employee_id = None
    basic_pay = None
    effective_from = None
    effective_to = None
    status = None
    created_by = None
    created_date = None
    updated_by = None
    updated_date = None


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                      sort_keys=True, indent=4)
    def set_id(self,id):
        self.id=id

    def set_employee_id(self, employee_id):
        self.employee_id = employee_id

    def set_basic_pay(self, basic_pay):
        self.basic_pay = basic_pay

    def set_effective_from(self, effective_from):
        self.effective_from = str(effective_from)

    def set_effective_to(self, effective_to):
        self.effective_to = str(effective_to)

    def set_status(self, status):
        self.status = status

    def set_created_by(self, created_by):
        self.created_by =created_by

    def set_created_date(self, created_date):
        self.created_date = str(created_date)

    def set_updated_by(self, updated_by):
        self.updated_by = updated_by

    def set_updated_date(self, updated_date):
        self.updated_date = str(updated_date)



class EmployeeAdvanceRequestResponse:
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

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_employee_id(self, employee_id):
            self.employee_id = employee_id

    def set_requested_advance_amount(self, requested_advance_amount):
        self.requested_advance_amount = requested_advance_amount

    def set_approved_advance_amount(self, approved_advance_amount):
        self.approved_advance_amount = approved_advance_amount

    def set_reason(self, reason):
        self.reason = reason

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


class EmployeeAdvanceApprovalResponse:
    id = None
    employee_request_id= None
    employee_id = None
    remarks = None
    status = None
    created_by = None
    created_date = None
    updated_by = None
    updated_date = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id

    def set_employee_request_id(self,employee_request_id):
        self.employee_request_id = employee_request_id

    def set_employee_id(self,employee_id):
        self.employee_id = employee_id

    def set_remarks(self,remarks):
        self.remarks = remarks

    def set_status(self,status):
        self.status = status

    def set_created_by(self,created_by):
        self.created_by = created_by

    def set_created_date(self,created_date):
        self.created_date = created_date

    def set_updated_by(self,updated_by):
        self.updated_by = updated_by

    def set_updated_date(self,updated_date):
        self.updated_date = updated_date











