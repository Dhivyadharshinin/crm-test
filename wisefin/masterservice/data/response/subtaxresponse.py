import json


class SubTaxResponse:
    id = None
    tax_id = None
    code = None
    name = None
    remarks = None
    glno = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def set_name(self, name):
        self.name = name

    def set_tax_id(self, tax_id):
        self.tax_id = tax_id

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_glno(self, glno):
        self.glno = glno

