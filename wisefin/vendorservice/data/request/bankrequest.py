import json

class BankRequest:

    id = None
    code = None
    name = None

    def __init__(self, bank_data):
        if 'id' in bank_data:
            self.id = bank_data['id']
        if 'code' in bank_data:
            self.code = bank_data['code']
        if 'name' in bank_data:
            self.name = bank_data['name']


    def get_id(self):
        return self.id
    def get_bankcode(self):
        return self.code
    def get_bankname(self):
        return self.name

