import json

class BankBranchRequest:
    id = None
    code = None
    name = None
    ifsccode = None
    microcode = None
    bank_id = None
    address_id = None

    def __init__(self, bankbranch_data):
        if 'id' in bankbranch_data:
            self.id = bankbranch_data['id']
        if 'bank_id' in bankbranch_data:
            self.bank_id = bankbranch_data['bank_id']
        if 'address_id' in bankbranch_data:
            self.address_id = bankbranch_data['address_id']
        if 'code' in bankbranch_data:
            self.code = bankbranch_data['code']
        if 'ifsccode' in bankbranch_data:
            self.ifsccode = bankbranch_data['ifsccode']
        if 'microcode' in bankbranch_data:
            self.microcode = bankbranch_data['microcode']
        if 'name' in bankbranch_data:
            self.name = bankbranch_data['name']


    def get_id(self):
        return self.id
    def get_bankid(self):
        return self.bank_id
    def get_addrid(self):
        return self.address_id
    def get_code(self):
        return self.code
    def get_ifsccode(self):
        return self.ifsccode
    def get_microcode(self):
        return self.microcode
    def get_name(self):
        return self.name
