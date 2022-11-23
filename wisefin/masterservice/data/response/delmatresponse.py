import json
class DelmatResponse:
    id = None
    commodity_id = None
    employee_id = None
    commodity = None
    employee = None
    type = None
    limit = None
    delmat_status = None
    status = None
    remarks = None
    created_by = None
    employee_name=None
    two_level_approval = None
    two_level_employee_id = None
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_commodity(self, commodity_id):
        self.commodity_id = commodity_id

    def set_employee(self, employee_id):
        self.employee_id = employee_id

    def set_commodity_id(self, commodity_id):
        self.commodity_id=commodity_id

    def set_employee_id(self, employee_id):
        self.employee_id=employee_id
    def set_employee_name(self, employee_id):
        self.employee_name = employee_id
    def set_employee_ap(self, employee_id):
        self.employee = employee_id
    def set_type(self, type):
        self.type = type

    def set_limit(self, limit):
        self.limit = limit

    def set_delmat_status(self, delmat_status):
        self.delmat_status = delmat_status

    def set_status(self, status):
        self.status = status

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_type_id(self, type_id):
        self.type_id = type_id
    def set_two_level_approval(self,two_level_approval):
        self.two_level_approval=two_level_approval
    def set_two_level_employee_id(self,two_level_employee_id):
        self.two_level_employee_id=two_level_employee_id
