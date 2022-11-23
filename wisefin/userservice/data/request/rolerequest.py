import json


class RoleResquest:
    id = None
    name = None
    code = None

    def __init__(self, role_obj):
        if 'id' in role_obj:
            self.id = role_obj['id']
        if 'name' in role_obj:
            self.name = role_obj['name']
        if 'code' in role_obj:
            self.code = role_obj['code']

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_code(self):
        return self.code


class RoleEmployeeResquest:
    id = None
    role_id = None
    employee_id = None

    def __init__(self, role_obj):
        if 'id' in role_obj:
            self.id = role_obj['id']
        if 'role_id' in role_obj:
            self.role_id = role_obj['role_id']
        if 'employee_id' in role_obj:
            self.employee_id = role_obj['employee_id']

    def get_id(self):
        return self.id

    def get_role_id(self):
        return self.role_id

    def get_employee_id(self):
        return self.employee_id


class RoleModuleResquest:
    id = None
    role_id = None
    module_id = None
    add = None
    remove = None

    def __init__(self, role_obj):
        if 'id' in role_obj:
            self.id = role_obj['id']
        if 'role_id' in role_obj:
            self.role_id = role_obj['role_id']
        if 'module_id' in role_obj:
            self.module_id = role_obj['module_id']
        if 'add' in role_obj:
            self.add = role_obj['add']
        if 'remove' in role_obj:
            self.remove = role_obj['remove']

    def get_id(self):
        return self.id

    def get_role_id(self):
        return self.role_id

    def get_module_id(self):
        return self.module_id

    def get_add(self):
        return self.add

    def get_remove(self):
        return self.remove
