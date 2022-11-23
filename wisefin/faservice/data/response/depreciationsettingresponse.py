import json


class DepreciationSettingResponse:
    id =  doctype = depgl = depreservegl = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_doctype(self, doctype):
        self.doctype = doctype
    def set_depgl(self, depgl):
        self.depgl = depgl
    def set_depreservegl(self, depreservegl):
        self.depreservegl = depreservegl

