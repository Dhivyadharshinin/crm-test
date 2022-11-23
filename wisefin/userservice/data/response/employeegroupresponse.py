import json
class EmployeeGroupResponse:
    id = None
    code = None
    name = None
    type =None
    module=None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def set_name(self, name):
        self.name = name

    def set_type(self,type):
        self.type = type

    def set_module(self,module):
        m={"name":module.name,"id":module.id}
        self.module = m


class GroupMappingResponse:
    id = None
    employee = None
    group = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_employee(self, employee):
        self.employee = employee

    def set_group(self, group):
        if group !=None:
            group={"id":group.id,"code":group.code,"name":group.name}
        self.group = group
