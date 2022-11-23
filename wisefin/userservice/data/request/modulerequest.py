import json


class ModuleResquest:
    id = None
    name = None
    logo = None
    url = None
    refid = None

    def __init__(self, module_obj):
        if 'id' in module_obj:
            self.id = module_obj['id']
        if 'name' in module_obj:
            self.name = module_obj['name']
        if 'logo' in module_obj:
            self.logo = module_obj['logo']
        if 'url' in module_obj:
            self.url = module_obj['url']
        if 'refid' in module_obj:
            self.refid = module_obj['refid']


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
