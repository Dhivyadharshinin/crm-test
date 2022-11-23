import json

from userservice.service.moduleservice import ModuleService


class QuestiontypeResponse:
    id, name, remarks, display_name, module_id,header_id,data = (None,)*7

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


    def set_id(self, id):
        self.id = id

    def set_name(self, name):
        self.name = name

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_display_name(self, display_name):
        self.display_name = display_name

    def set_module_id(self, module_id, arr):
        self.module = None
        for i in arr:
            if i.id == module_id:
                self.module = i
                break
        # module_serv = ModuleService(scope)
        # module_id = module_serv.get_module_id(module_id)
        # self.module = module_id

    def set_header_id(self, header_id):
        self.header_id = header_id

    def set_data(self, data):
        self.data = data

    def set_module(self,module_id):
        self.module_id = module_id
