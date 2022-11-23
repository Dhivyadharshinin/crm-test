import json


class DepartmentResponse:
    id = None
    name = None
    code = None
    description = None
    short_notation = None
    status = None
    created_date = None
    created_by = None
    updated_date = None
    updated_by = None
    branch = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_name(self, name):
        self.name = name

    def set_code(self, code):
        self.code = code

    def set_short_notation(self, short_notation):
        self.short_notation = short_notation

    def set_description(self, description):
        self.description = description

    def set_status(self, status):
        self.status = status

    def set_created_date(self, created_date):
        self.created_date = created_date

    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_updated_date(self, updated_date):
        self.updated_date = updated_date

    def set_updated_by(self, updated_by):
        self.updated_by = updated_by

    def set_branch(self,branch):
        self.branch=branch

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_code(self):
        return self.code

    def get_description(self):
        return self.description

    def get_status(self):
        return self.status

    def get_short_notation(self):
        return self.short_notation

    def get_branch(self):
        return self.branch

    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_created_date(self, created_date):
        created_date=str(created_date)
        self.created_date = created_date

    def set_updated_by(self, updated_by):
        self.updated_by = updated_by

    def set_updated_date(self, updated_date):
        updated_date=str(updated_date)
        self.updated_date = updated_date



        


class EmployeeDepartmentResponse:
    id = None
    name = None
    code = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_name(self, name):
        self.name = name

    def set_code(self, code):
        self.code = code

class DepartmentuploadResponse:
    id = None
    name = None
    remarks = None
    file = None
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_name(self, name):
        self.name = name

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_file(self,file):
        self.file = file