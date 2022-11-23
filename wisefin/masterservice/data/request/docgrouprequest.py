import json

class DocumentGroupRequest:
    id = None
    partnertype = None
    name = None
    isparent = None
    parent_id = None
    docname = None
    period = None
    mand =  None

    def __init__(self, documentgroup_data):
        if 'id' in documentgroup_data:
            self.id = documentgroup_data['id']
        if 'docname' in documentgroup_data:
            self.docname = documentgroup_data['docname']
        if 'period' in documentgroup_data:
            self.period = documentgroup_data['period']
        if 'partnertype' in documentgroup_data:
            self.partnertype = documentgroup_data['partnertype']
        if 'isparent' in documentgroup_data:
            self.isparent = documentgroup_data['isparent']
        if 'parent_id' in documentgroup_data:
            self.parent_id = documentgroup_data['parent_id']
        if 'name' in documentgroup_data:
            self.name = documentgroup_data['name']
        if 'mand' in documentgroup_data:
            self.mand = documentgroup_data['mand']


    def get_id(self):
        return self.id
    def get_docname(self):
        return self.docname
    def get_period(self):
        return self.period
    def get_partnertype(self):
        return self.partnertype
    def get_isparent(self):
        return self.isparent
    def get_parent_id(self):
        return self.parent_id
    def get_name(self):
        return self.name
    def get_mand(self):
        return self.mand