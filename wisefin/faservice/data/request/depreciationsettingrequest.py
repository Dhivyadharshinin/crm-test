import json

class DepreciationSettingRequest:

    id =  doctype = depgl = depreservegl = None

    def __init__(self, depsetting_data):
        if 'id' in depsetting_data:
            self.id = depsetting_data['id']
        if 'doctype' in depsetting_data:
            self.doctype = depsetting_data['doctype']
        if 'depgl' in depsetting_data:
            self.depgl = depsetting_data['depgl']
        if 'depreservegl' in depsetting_data:
            self.depreservegl = depsetting_data['depreservegl']


    def get_id(self):
        return self.id
    def get_doctype(self):
        return self.doctype
    def get_depgl(self):
        return self.depgl
    def get_depreservegl(self):
        return self.depreservegl
