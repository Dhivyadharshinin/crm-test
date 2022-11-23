import json


class InwardMiniDetailsResponse:
        id = None
        doctype = None
        count = None
        attachment = None



        def get(self):
            return json.dumps(self, default=lambda o: o.__dict__,
                              sort_keys=True, indent=4)

        def set_id(self, id):
            self.id = id

        def set_doctype(self, doctype):
            self.doctype = doctype

        def set_count(self, count):
            self.count = count

        def set_attachment(self, attachment):
            self.attachment = attachment

