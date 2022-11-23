import json
class DocumentGroupResponse:
    id = None
    partnertype = None
    isparent = None
    name = None
    parent_id = None
    docname = None
    period = None
    mand = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def set_id(self, id):
        self.id = id
    def set_partnertype(self, partnertype):
        self.partnertype = partnertype
    def set_isparent(self, isparent):
        self.isparent = isparent
    def set_name(self, name):
        self.name = name
    def set_parent_id(self, parent_id):
        self.parent_id = parent_id
    def set_docname(self, docname):
        self.docname = docname
    def set_period(self, period):
        self.period = period

    def set_mand(self, mand):
        self.mand = mand

    def get_id(self):
        return self.id
    def get_partnertype(self):
        return self.partnertype

    def get_name(self):
        return self.name
    def get_parent_id(self):
        return self.parent_id
    def get_docname(self):
        return self.docname
    def get_isparent(self):
        return self.isparent

    def get_period(self):
        return self.period
    def get_mand(self):
        return self.mand