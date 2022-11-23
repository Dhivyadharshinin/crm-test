import json


class RoleResponse:
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

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_code(self):
        return self.code


class RoleEmployeeResponse:
    id = None
    role_id = None
    employee_id = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_role_id(self, role_id):
        self.role_id = role_id

    def set_employee_id(self, employee_id):
        self.employee_id = employee_id

    def get_id(self):
        return self.id

    def get_role_id(self):
        return self.role_id

    def get_employee_id(self):
        return self.employee_id


class RoleModuleResponse:
    id = None
    role = None
    module = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_role_id(self, role_id):
        self.role = role_id

    def set_module_id(self, module_id):
        self.module = module_id

    def get_id(self):
        return self.id

    def get_role_id(self):
        return self.role

    def get_module_id(self):
        return self.module
