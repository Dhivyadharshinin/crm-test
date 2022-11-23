class Designation_get_req:
    expense_id= None
    grade = None
    traveltime = None

    def __init__(self, obj):
        if 'expense_id' in obj:
            self.expense_id=obj['expense_id']
        if 'grade' in obj:
            self.grade=obj['grade']
        if 'traveltime' in obj:
            self.traveltime=obj['traveltime']

    def get_expense_id(self):
        return self.expense_id
    def get_grade(self):
        return self.grade
    def get_traveltime(self):
        return self.traveltime

