import json

class CourierRequest:
    id = None
    code = None
    name = None
    type = None
    contactperson = None
    contact_id = None
    address_id = None
    all_branch = True

    def __init__(self, courier_data):
        if 'id' in courier_data:
            self.id = courier_data['id']
        if 'code' in courier_data:
            self.code = courier_data['code']
        if 'name' in courier_data:
            self.name = courier_data['name']
        if 'type' in courier_data:
            self.type = courier_data['type']
        if 'contactperson' in courier_data:
            self.contactperson = courier_data['contactperson']
        if 'address_id' in courier_data:
            self.address_id = courier_data['address_id']
        if 'contact_id' in courier_data:
            self.contact_id = courier_data['contact_id']
        if 'all_branch' in courier_data:
            self.all_branch = courier_data['all_branch']

    # code, name, type, contactperson, address_id, contact_id
    def get_id(self):
        return self.id
    def get_code(self):
        return self.code
    def get_name(self):
        return self.name
    def get_type(self):
        return self.type
    def get_contactperson(self):
        return self.contactperson
    def get_contact_id(self):
        return self.contact_id
    def get_address_id(self):
        return self.address_id
    def get_all_branch(self):
        return self.all_branch
