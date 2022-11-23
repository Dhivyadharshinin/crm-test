import json


class CourierResponse:
        id = None
        code = None
        name = None
        type = None
        contactperson = None
        contact_id = None
        address_id = None


        def get(self):
            return json.dumps(self, default=lambda o: o.__dict__,
                              sort_keys=True, indent=4)

        def set_id(self, id):
            self.id = id
        def set_code(self, code):
            self.code = code
        def set_name(self, name):
            self.name = name
        def set_type(self, type):
            self.type = type
        def set_contactperson(self, contactperson):
            self.contactperson = contactperson
        def set_contact_id(self, contact_id):
            self.contact_id = contact_id
        def set_address_id(self, address_id):
            self.address_id = address_id
        def set_all_branch(self, all_branch):
            self.all_branch = all_branch
