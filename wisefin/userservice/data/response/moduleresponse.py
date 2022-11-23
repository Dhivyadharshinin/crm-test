import json


class ModuleListResponse:
    id = None
    name = None
    logo = None
    url = None
    role = None


class ModuleResponse:
    id = None
    name = None
    logo = None
    url = None
    refid =None
    role=None
    submodule=[]

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_name(self, name):
        self.name = name

    def set_logo(self, logo):
        self.logo = logo

    def set_url(self, url):
        self.url = url

    def set_refid(self,refid):
        self.refid = refid

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_logo(self):
        return self.logo

    def get_url(self):
        return self.url

    def get_refid(self):
        return self.refid


# class ModuleMappingResponse:
#
#     def set_module_id(self, module_id):
#         self.module_id = module_id
#
#     def set_order(self, order):
#         self.order = order
#
#
#     def get_module_id(self):
#         return self.module_id
#
#     def get_order(self):
#         return self.order
#
#     def get_user(self):
#         return self.user


class ModuleMappingResponse:
    id = None
    name = None
    logo = None
    url = None
    order = None
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def set_id(self, id):
        self.id = id
    def set_name(self, name):
        self.name = name
    def set_logo(self, logo):
        self.logo = logo
    def set_url(self, url):
        self.url = url
    def set_order(self, order):
        self.order = order
    def get_id(self):
        return self.id
    def get_name(self):
        return self.name
    def get_logo(self):
        return self.logo
    def get_url(self):
        return self.url
    def get_order(self):
        return self.order


