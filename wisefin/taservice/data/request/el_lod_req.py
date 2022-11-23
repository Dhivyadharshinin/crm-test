class El_lod_req:
    expense_id= None
    salarygrade = None
    city = None
    checkindate = None
    checkoutdate = None

    def __init__(self,obj):
        if 'expense_id' in obj:
            self.expense_id=obj['expense_id']
        if 'salarygrade' in obj:
            self.salarygrade=obj['salarygrade']
        if 'city' in obj:
            self.city=obj['city']
        if 'checkindate' in obj:
            self.checkindate=obj['checkindate']
        if 'checkoutdate' in obj:
            self.checkoutdate=obj['checkoutdate']

    def get_expense_id(self):
        return self.expense_id
    def get_salarygrade(self):
        return self.salarygrade
    def get_city(self):
        return self.city
    def get_checkindate(self):
        return self.checkindate
    def get_checkoutdate(self):
        return self.checkoutdate

