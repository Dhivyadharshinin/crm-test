import json


class ProductcategoryResponse:
        id = None
        code = None
        name = None
        remarks = None
        is_sys = None


        def get(self):
            return json.dumps(self, default=lambda o: o.__dict__,
                              sort_keys=True, indent=4)

        def set_id(self, id):
            self.id = id

        def set_code(self, code):
            self.code = code

        def set_name(self, name):
            self.name = name

        def set_remarks(self, remarks):
            self.remarks = remarks

        def set_is_sys(self, is_sys):
            self.is_sys = is_sys


