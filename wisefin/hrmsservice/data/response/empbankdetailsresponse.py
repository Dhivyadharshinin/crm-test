import json

class EmpBankDetailResponse:
    id, account_name, bank_id, bank_branch, account_no,ifsc = (None,)*6

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_account_name(self, account_name):
        self.account_name = account_name

    def set_bank_id(self, bank_id):
        self.bank_id = bank_id

    def set_bank_branch(self, bank_branch):
        self.bank_branch = bank_branch

    def set_account_no(self, account_no):
        self.account_no = account_no

    def set_ifsc(self, ifsc):
        self.ifsc = ifsc


