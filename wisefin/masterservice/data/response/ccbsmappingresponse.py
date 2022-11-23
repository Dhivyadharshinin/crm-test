import json

class CcbsmappingResponse:
    id = None
    code = None
    no = None
    name = None
    remarks = None
    description = None
    costcentre_id = None
    businesssegment_id = None
    glno = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def set_no(self, no):
        self.no = no

    def set_name(self, name):
        self.name = name

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_description(self, description):
        self.description = description

    def set_costcentre(self, costcentre_id):
        self.costcentre_id= costcentre_id

    def set_businesssegment(self, businesssegment_id):
        self.businesssegment_id = businesssegment_id

    def set_glno(self, glno):
        self.glno = glno

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
        return self.costcentre_id

    def get_businesssegment(self):
        return self.businesssegment_id

    def get_glno(self):
        return self.glno