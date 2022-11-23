import json

class SecurityguardRequest:
    id = None
    empcat = None
    empcatdesc = None

    def __init__(self, exuom_obj):
        if 'id' in exuom_obj:
            self.id=exuom_obj['id']
        if 'empcat' in exuom_obj:
            self.empcat=exuom_obj['empcat']
        if 'empcatdesc' in exuom_obj:
            self.empcatdesc=exuom_obj['empcatdesc']

    def get_id(self):
        return self.id

    def get_empcat(self):
        return self.empcat

    def get_empcatdesc(self):
        return self.empcatdesc
class EmployeetypecatRequest:
    id = None
    emptype = None
    emptypedesc = None
    empcat_id=None

    def __init__(self, exuom_obj):
        if 'id' in exuom_obj:
            self.id=exuom_obj['id']
        if 'emptype' in exuom_obj:
            self.emptype=exuom_obj['emptype']
        if 'emptypedesc' in exuom_obj:
            self.emptypedesc=exuom_obj['emptypedesc']
        if 'empcat_id' in exuom_obj:
            self.empcat_id=exuom_obj['empcat_id']

    def get_id(self):
        return self.id

    def get_emptype(self):
        return self.emptype

    def get_emptypedesc(self):
        return self.emptypedesc
    def get_empcat_id(self):
        return self.empcat_id