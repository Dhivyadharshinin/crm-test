import json



class BankDetailsResponse:

    id = None
    bankbranch_id = None
    bankbranch = None
    account_no = None
    accountholder = None

    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_bankbranch_id(self, bankbranch_id):
        self.bankbranch_id = bankbranch_id
    def set_account_no(self, account_no):
        self.account_no = account_no

    def set_accountholder(self, accountholder):
        self.accountholder = accountholder

    def set_bankbranch(self, bankbranch):
        self.bankbranch = bankbranch
