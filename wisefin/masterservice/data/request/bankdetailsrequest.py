import json

class BankDetailsRequest:

    id = None
    bankbranch_id = None
    account_no = None
    accountholder = None

    def __init__(self, bank_data):
        if 'id' in bank_data:
            self.id = bank_data['id']
        if 'bankbranch_id' in bank_data:
            self.bankbranch_id = bank_data['bankbranch_id']
        if 'account_no' in bank_data:
            self.account_no = bank_data['account_no']
        if 'accountholder' in bank_data:
            self.accountholder = bank_data['accountholder']


    def get_id(self):
        return self.id
    def get_bankbranch_id(self):
        return self.bankbranch_id
    def get_account_no(self):
        return self.account_no
    def get_accountholder(self):
        return self.accountholder

