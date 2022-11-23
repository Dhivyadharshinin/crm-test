class Breakage_amount_req:
    expense_id= None
    receipt_loss = None
    grade = None


    def __init__(self,obj):
        if 'expense_id' in obj:
            self.expense_id=obj['expense_id']
        if 'receipt_loss' in obj:
            self.receipt_loss=obj['receipt_loss']
        if 'grade' in obj:
            self.grade=obj['grade']


    def get_expense_id(self):
        return self.expense_id
    def get_receipt_loss(self):
        return self.receipt_loss
    def get_grade(self):
        return self.grade
