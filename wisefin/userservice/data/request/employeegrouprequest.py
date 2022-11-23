from django.utils.crypto import constant_time_compare, salted_hmac
from django.core import signing
class EmpGroupRequest:
    id = None
    code = None
    name = None
    type=None
    module_id =None

    def __init__(self, data_obj):
        if 'id' in data_obj:
            self.id = data_obj['id']
        if 'code' in data_obj:
            self.code = data_obj['code']
        if 'name' in data_obj:
            self.name = data_obj['name']
        if 'type' in data_obj:
            self.type = data_obj['type']
        if  'module_id' in data_obj:
            self.module_id = data_obj['module_id']

    def get_id(self):
        return self.id

    def get_code(self):
        return self.code

    def get_name(self):
        return self.name

    def get_type(self):
        return self.type

    def get_module_id(self):
        return self.module_id

class GroupPermissionResquest:
    id = None
    role_id = None
    group_id = None
    add = None
    remove = None

    def __init__(self, role_obj):
        if 'id' in role_obj:
            self.id = role_obj['id']
        if 'role_id' in role_obj:
            self.role_id = role_obj['role_id']
        if 'group_id' in role_obj:
            self.group_id = role_obj['group_id']
        if 'add' in role_obj:
            self.add = role_obj['add']
        if 'remove' in role_obj:
            self.remove = role_obj['remove']

    def get_id(self):
        return self.id

    def get_role_id(self):
        return self.role_id

    def get_group_id(self):
        return self.group_id

    def get_add(self):
        return self.add

    def get_remove(self):
        return self.remove