import json

class CcbsMappingRequest:
    id = None
    code = None
    no = None
    name =None
    remarks = None
    description = None
    costcentre = None
    businesssegment = None
    glno = None

    def __init__(self, ccbsmapping_obj):
        if 'id' in ccbsmapping_obj:
            self.id = ccbsmapping_obj['id']
        if 'code' in ccbsmapping_obj:
            self.code = ccbsmapping_obj['code']
        if 'no' in ccbsmapping_obj:
            self.no = ccbsmapping_obj['no']
        if 'name' in ccbsmapping_obj:
            self.name = ccbsmapping_obj['name']
        if 'remarks' in ccbsmapping_obj:
            self.remarks = ccbsmapping_obj['remarks']
        if 'description' in ccbsmapping_obj:
            self.description = ccbsmapping_obj['description']
        if 'costcentre' in ccbsmapping_obj:
            self.costcentre = ccbsmapping_obj['costcentre']
        if 'businesssegment' in ccbsmapping_obj:
            self.businesssegment = ccbsmapping_obj['businesssegment']
        if 'glno' in ccbsmapping_obj:
            self.glno = ccbsmapping_obj['glno']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_id(self):
        return self.id
    def get_code(self):
        return self.code
    def get_remarks(self):
        return self.remarks
    def get_description(self):
        return self.description
    def get_no(self):
        return self.no
    def get_name(self):
        return self.name
    def get_costcentre(self):
        return self.costcentre
    def get_businesssegment(self):
        return self.businesssegment
    def get_glno(self):
        return self.glno