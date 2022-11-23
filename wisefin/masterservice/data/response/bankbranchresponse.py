import json


class BankBranchResponse:
        id = None
        code = None
        name = None
        ifsccode = None
        microcode = None
        bank_id = None
        address_id = None

        def get(self):
            return json.dumps(self, default=lambda o: o.__dict__,
                              sort_keys=True, indent=4)

        def set_id(self, id):
            self.id = id
        def set_bank_id(self, bank_id):
            self.bank_id = bank_id
        def set_address_id(self, address_id):
            self.address_id = address_id
        def set_code(self, code):
            self.code = code
        def set_ifsccode(self, ifsccode):
            self.ifsccode = ifsccode
        def set_microcode(self, microcode):
            self.microcode = microcode
        def set_name(self, name):
            self.name = name