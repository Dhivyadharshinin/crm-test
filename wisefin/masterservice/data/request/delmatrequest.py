import json


class DelmatRequest:
    id = None
    commodity = None
    employee = None
    type = None
    limit = None
    delmat_status = None
    status = None
    remarks = None
    created_by = None
    commodity_code = None
    employee_code = None
    two_level_approval=None
    two_level_employee_id=None
    def __init__(self, delmat_obj):
        if 'id' in delmat_obj:
            self.id = delmat_obj['id']
        if 'created_by' in delmat_obj:
            self.created_by = delmat_obj['created_by']
        if 'commodity_id' in delmat_obj:
            self.commodity = delmat_obj['commodity_id']
        if 'employee_id' in delmat_obj:
            self.employee = delmat_obj['employee_id']
        if 'type' in delmat_obj:
            self.type = delmat_obj['type']
        if 'limit' in delmat_obj:
            self.limit = delmat_obj['limit']
        if 'delmat_status' in delmat_obj:
            self.delmat_status = delmat_obj['delmat_status']
        if 'status' in delmat_obj:
            self.status = delmat_obj['status']
        if 'remarks' in delmat_obj:
            self.remarks = delmat_obj['remarks']
        if 'commodity_code' in delmat_obj:
            self.commodity_code = delmat_obj['commodity_code']
        if 'employee_code' in delmat_obj:
            self.employee_code = delmat_obj['employee_code']
        if 'two_level_approval' in delmat_obj:
            self.two_level_approval=delmat_obj['two_level_approval']
        if 'two_level_employee_id' in delmat_obj:
            self.two_level_employee_id=delmat_obj['two_level_employee_id']
    def get_id(self):
        return self.id
    def get_created_by(self):
        return self.created_by

    def get_commodity(self):
        return self.commodity
    def get_employee(self):
        return self.employee
    def get_type(self):
        return self.type
    def get_limit(self):
        return self.limit
    def get_delmat_status(self):
        return self.delmat_status
    def get_status(self):
        return self.status
    def get_remarks(self):
        return self.remarks
    def get_commodity_code(self):
        return self.commodity_code
    def get_employee_code(self):
        return self.employee_code
    def get_two_level_approval(self):
        return self.two_level_approval
    def get_two_level_employee_id(self):
        return self.two_level_employee_id