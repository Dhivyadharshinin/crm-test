import json

class BankRequest:

    id = None
    code = None
    name = None
    status = None

    def __init__(self, bank_data):
        if 'id' in bank_data:
            self.id = bank_data['id']
        if 'code' in bank_data:
            self.code = bank_data['code']
        if 'name' in bank_data:
            self.name = bank_data['name']

        if 'status' in bank_data:
            self.status = bank_data['status']


    def get_id(self):
        return self.id
    def get_bankcode(self):
        return self.code
    def get_bankname(self):
        return self.name

    def get_status(self):
        return self.status

