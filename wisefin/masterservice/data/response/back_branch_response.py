import json
from masterservice.data.response.addressresponse import AddressResponse
from masterservice.data.response.bankresponse import BankResponse


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
        def set_bankid(self, bank_id):
            self.bank_id = bank_id
        def set_addrid(self, address_id):
            self.address_id = address_id
        def set_code(self, code):
            self.code = code
        def set_ifsccode(self, ifsccode):
            self.ifsccode = ifsccode
        def set_microcode(self, microcode):
            self.microcode = microcode
        def set_name(self, name):
            self.name = name
        def set_bank_id(self, bank_id):
            self.bank_id = bank_id
        def set_address_id(self, address_id):
            self.address_id = address_id

        def set_bank(self,bank):
            bank_data = BankResponse()
            bank_data.set_id(bank.id)
            bank_data.set_code(bank.code)
            bank_data.set_name(bank.name)
            self.bank = bank_data

        def set_address(self, address):
            add_data = AddressResponse()
            add_data.set_id(address.id)
            add_data.set_line1(address.line1)
            add_data.set_line2(address.line2)
            add_data.set_line3(address.line3)
            add_data.set_pincode_id(address.pincode_id)
            add_data.set_city_id(address.city_id)
            add_data.set_district_id(address.district_id)
            add_data.set_state_id(address.state_id)
            self.address = add_data
