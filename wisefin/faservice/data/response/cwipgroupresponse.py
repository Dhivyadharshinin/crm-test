import json


class CwipGroupResponse:

    id = code = name = gl = doctype = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_code(self, code):
        self.code = code
    def set_name(self, name):
        self.name =name
    def set_gl(self, gl):
        self.gl = gl
    def set_doctype(self, doctype):
        self.doctype = doctype


